import io
import json
import zipfile
from pathlib import Path

from flask.testing import FlaskClient

from tomorrowkit.data_types import MatterId
from tomorrowkit.runner import build_app
from tomorrowkit.storage import FileMatterStore
from tomorrowkit.testing import build_sample_matter


def _build_client(tmp_path: Path) -> tuple[FlaskClient, FileMatterStore]:
    store = FileMatterStore(matters_directory=tmp_path / "matters")
    app = build_app(store)
    app.config["TESTING"] = True
    return app.test_client(), store


def test_health_endpoint(tmp_path: Path) -> None:
    client, _ = _build_client(tmp_path)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_home_page_lists_existing_matters_and_starts_in_chat(tmp_path: Path) -> None:
    client, store = _build_client(tmp_path)
    store.save_matter(build_sample_matter())

    response = client.get("/")

    assert response.status_code == 200
    assert b"Self-sealing irrigation coupler" in response.data
    assert b'id="start-in-chat"' in response.data
    # The conversation is the only intake path: no quiz, no form, no onboarding script.
    assert b'id="orientation-quiz"' not in response.data
    assert b"<form" not in response.data
    assert b"onboarding.js" not in response.data


def test_home_page_without_matters_points_to_the_conversation(tmp_path: Path) -> None:
    client, _ = _build_client(tmp_path)

    response = client.get("/")

    assert response.status_code == 200
    assert b'id="start-in-chat"' in response.data
    assert b'class="resume-strip"' not in response.data
    assert b'id="orientation-quiz"' not in response.data


def test_orientation_endpoint_is_gone(tmp_path: Path) -> None:
    client, store = _build_client(tmp_path)

    response = client.post(
        "/api/orientation",
        json={
            "idea_state": "WRITTEN_OR_BUILT",
            "disclosure_state": "CONFIDENTIAL_ONLY",
            "objectives": ["PROTECT_PRODUCT"],
            "materials_state": "NOTES_OR_SKETCHES",
            "collaboration_style": "GUIDED_CHOICES",
        },
    )

    assert response.status_code == 404
    assert store.list_matters() == []


def test_create_matter_from_intake_payload(tmp_path: Path) -> None:
    client, store = _build_client(tmp_path)

    response = client.post(
        "/api/matters",
        json={
            "title": "Test invention",
            "problem_summary": "A problem.",
            "stage": "DRAFT_READY",
            "goal": "File soon",
            "theme": "",
            "known_dates": [{"label": "Demo", "date_text": "2026-01-01", "note": ""}],
        },
    )

    assert response.status_code == 201
    created = response.get_json()
    stored = store.load_matter(MatterId(created["matter_id"]))
    assert stored.title == "Test invention"
    assert stored.stage.value == "DRAFT_READY"
    assert stored.workflow_phase.value == "WELCOME"
    # A new matter starts with the guided harvest checkpoints ready to run.
    assert [c["checkpoint_id"] for c in created["harvest"]] == [
        "source_lock",
        "objective_lock",
        "core_mechanism",
        "seed_expansion",
        "seed_assay",
        "terrain_selection",
        "provisional_posture",
        "disclosure_build",
        "attack_repair",
    ]






def test_create_matter_rejects_missing_title(tmp_path: Path) -> None:
    client, _ = _build_client(tmp_path)

    response = client.post("/api/matters", json={"stage": "EARLY_IDEA"})

    assert response.status_code == 400


def test_get_and_update_matter_round_trip(tmp_path: Path) -> None:
    client, store = _build_client(tmp_path)
    matter = build_sample_matter()
    store.save_matter(matter)

    fetched = client.get(f"/api/matters/{matter.matter_id}").get_json()
    fetched["brief"]["problem"] = "An updated problem statement."
    fetched["matter_id"] = "mat-" + "f" * 32
    fetched["created_at"] = "1999-01-01T00:00:00Z"
    updated_response = client.put(f"/api/matters/{matter.matter_id}", json=fetched)

    assert updated_response.status_code == 200
    updated = updated_response.get_json()
    # The server owns identity and creation time; the client cannot rewrite them.
    assert updated["matter_id"] == matter.matter_id
    assert updated["created_at"] == json.loads(matter.model_dump_json())["created_at"]
    assert updated["brief"]["problem"] == "An updated problem statement."
    assert (
        store.load_matter(matter.matter_id).brief.problem
        == "An updated problem statement."
    )


def test_update_matter_rejects_invalid_document(tmp_path: Path) -> None:
    client, store = _build_client(tmp_path)
    matter = build_sample_matter()
    store.save_matter(matter)

    response = client.put(
        f"/api/matters/{matter.matter_id}", json={"title": "x", "stage": "NOT_A_STAGE"}
    )

    assert response.status_code == 400


def test_stale_update_is_rejected_without_losing_newer_changes(
    tmp_path: Path,
) -> None:
    client, store = _build_client(tmp_path)
    matter = build_sample_matter()
    store.save_matter(matter)

    first_snapshot = client.get(f"/api/matters/{matter.matter_id}").get_json()
    stale_snapshot = client.get(f"/api/matters/{matter.matter_id}").get_json()
    first_snapshot["brief"]["problem"] = "The first accepted revision."
    stale_snapshot["title"] = "A stale title"

    assert (
        client.put(f"/api/matters/{matter.matter_id}", json=first_snapshot).status_code
        == 200
    )
    stale_response = client.put(f"/api/matters/{matter.matter_id}", json=stale_snapshot)

    assert stale_response.status_code == 409
    current = store.load_matter(matter.matter_id)
    assert current.brief.problem == "The first accepted revision."
    assert current.title == matter.title


def test_matter_page_renders_for_existing_matter(tmp_path: Path) -> None:
    client, store = _build_client(tmp_path)
    matter = build_sample_matter()
    store.save_matter(matter)

    response = client.get(f"/matter/{matter.matter_id}")

    assert response.status_code == 200
    assert matter.matter_id.encode() in response.data
    assert b"Continue with Tomorrowkit" in response.data
    assert b'id="pane-continue"' in response.data
    assert b'id="harvest-list"' not in response.data


def test_unknown_and_malformed_matter_ids_return_404(tmp_path: Path) -> None:
    client, _ = _build_client(tmp_path)

    assert client.get(f"/matter/{MatterId.generate()}").status_code == 404
    assert client.get("/matter/not-a-real-id").status_code == 404
    assert client.get("/api/matters/not-a-real-id").status_code == 404


def test_export_zip_download(tmp_path: Path) -> None:
    client, store = _build_client(tmp_path)
    matter = build_sample_matter()
    store.save_matter(matter)

    response = client.get(f"/matter/{matter.matter_id}/export.zip")

    assert response.status_code == 200
    assert response.mimetype == "application/zip"
    archive = zipfile.ZipFile(io.BytesIO(response.data))
    assert "matter.json" in archive.namelist()


def test_export_supports_unicode_titles(tmp_path: Path) -> None:
    client, _ = _build_client(tmp_path)
    created = client.post(
        "/api/matters", json={"title": "発明", "stage": "EARLY_IDEA"}
    ).get_json()

    response = client.get(f"/matter/{created['matter_id']}/export.zip")

    assert response.status_code == 200
    assert response.mimetype == "application/zip"
    disposition = response.headers["Content-Disposition"]
    assert "filename=" in disposition
    assert "filename*=UTF-8''" in disposition


def test_raw_record_view_returns_pretty_json(tmp_path: Path) -> None:
    client, store = _build_client(tmp_path)
    matter = build_sample_matter()
    store.save_matter(matter)

    response = client.get(f"/matter/{matter.matter_id}/raw")

    assert response.status_code == 200
    assert response.mimetype == "application/json"
    assert json.loads(response.data)["matter_id"] == matter.matter_id


def test_delete_matter(tmp_path: Path) -> None:
    client, store = _build_client(tmp_path)
    matter = build_sample_matter()
    store.save_matter(matter)

    response = client.delete(f"/api/matters/{matter.matter_id}")

    assert response.status_code == 200
    assert store.list_matters() == []
    assert client.delete(f"/api/matters/{matter.matter_id}").status_code == 404


def test_deleted_matter_cannot_be_resurrected_by_stale_update(tmp_path: Path) -> None:
    client, store = _build_client(tmp_path)
    matter = build_sample_matter()
    store.save_matter(matter)
    stale_snapshot = client.get(f"/api/matters/{matter.matter_id}").get_json()

    assert client.delete(f"/api/matters/{matter.matter_id}").status_code == 200
    response = client.put(f"/api/matters/{matter.matter_id}", json=stale_snapshot)

    assert response.status_code == 404
    assert store.list_matters() == []


def test_static_assets_and_favicon_are_served_safely(tmp_path: Path) -> None:
    client, _ = _build_client(tmp_path)

    static_response = client.get("/static/favicon.svg")
    script_response = client.get("/static/matter.js")
    favicon_response = client.get("/favicon.ico")

    assert static_response.status_code == 200
    assert static_response.mimetype == "image/svg+xml"
    assert script_response.status_code == 200
    assert script_response.mimetype in {"text/javascript", "application/javascript"}
    assert favicon_response.status_code == 200
    assert favicon_response.mimetype == "image/svg+xml"
    assert client.get("/static/../templates/home.html").status_code == 404


def test_hostile_titles_are_escaped_in_rendered_pages(tmp_path: Path) -> None:
    client, _ = _build_client(tmp_path)
    hostile_title = "<script>alert(1)</script><img src=x onerror=alert(2)>"

    created = client.post(
        "/api/matters",
        json={"title": hostile_title, "stage": "EARLY_IDEA"},
    ).get_json()
    home_page = client.get("/")
    matter_page = client.get(f"/matter/{created['matter_id']}")

    assert b"<script>alert(1)</script>" not in home_page.data
    assert b"<img src=x onerror" not in home_page.data
    assert b"&lt;script&gt;alert(1)&lt;/script&gt;" in home_page.data
    assert b"<script>alert(1)</script>" not in matter_page.data
