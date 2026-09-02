import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from tomorrowkit import agent_tools
from tomorrowkit.data_types import MapNodeId, MatterIntake, MatterStage
from tomorrowkit.factories import create_matter_from_intake
from tomorrowkit.storage import FileMatterStore


def test_agent_patch_updates_workflow_profile_and_structured_artifacts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("TOMORROWKIT_DATA_DIR", str(tmp_path))
    store = FileMatterStore(matters_directory=tmp_path / "matters")
    matter = create_matter_from_intake(
        MatterIntake(title="Test invention", stage=MatterStage.EARLY_IDEA)
    )
    store.save_matter(matter)
    caller_supplied_node_id = str(MapNodeId.generate())
    patch_path = tmp_path / "patch.json"
    patch_path.write_text(
        json.dumps(
            {
                "expected_updated_at": matter.updated_at.isoformat(),
                "set": {
                    "title": "Pressure-responsive coupler",
                    "stage": "DRAFT_READY",
                    "workflow_phase": "CORE_MECHANISM",
                    "orientation.idea_state": "WRITTEN_OR_BUILT",
                    "orientation.disclosure_state": "CONFIDENTIAL_ONLY",
                    "orientation.objectives": [
                        "PROTECT_PRODUCT",
                        "LICENSE_OR_PARTNER",
                    ],
                    "orientation.materials_state": "NOTES_OR_SKETCHES",
                    "orientation.collaboration_style": "INTERVIEW_ME",
                    "brief.problem": "A verified inventor statement.",
                },
                "checkpoints": [
                    {"checkpoint_id": "source_lock", "status": "IN_PROGRESS"}
                ],
                "append_references": [
                    {
                        "title": "Example patent",
                        "source_type": "PATENT_PUBLICATION",
                        "relationship": "NEEDS_VERIFICATION",
                    }
                ],
                "append_map_nodes": [
                    {
                        "node_id": caller_supplied_node_id,
                        "kind": "COMPONENT",
                        "label": "Pressure-responsive valve",
                    }
                ],
                "append_dates": [
                    {
                        "label": "Confidential prototype review",
                        "date_text": "2026-08-14",
                        "note": "Review participants were under NDA.",
                    }
                ],
            }
        )
    )

    agent_tools._apply_patch(str(matter.matter_id), patch_path)

    updated = store.load_matter(matter.matter_id)
    assert updated.title == "Pressure-responsive coupler"
    assert updated.stage.value == "DRAFT_READY"
    assert updated.workflow_phase.value == "CORE_MECHANISM"
    assert updated.orientation.idea_state is not None
    assert updated.orientation.idea_state.value == "WRITTEN_OR_BUILT"
    assert [objective.value for objective in updated.orientation.objectives] == [
        "PROTECT_PRODUCT",
        "LICENSE_OR_PARTNER",
    ]
    assert updated.brief.problem == "A verified inventor statement."
    assert updated.harvest[0].status.value == "IN_PROGRESS"
    assert updated.references[0].title == "Example patent"
    assert updated.references[0].verification_state.value == "LEAD"
    assert updated.map_nodes[0].node_id != caller_supplied_node_id
    assert updated.map_nodes[0].label == "Pressure-responsive valve"
    assert updated.map_nodes[0].x == 80.0
    assert updated.map_nodes[0].y == 80.0
    assert updated.known_dates[0].label == "Confidential prototype review"
    assert json.loads(capsys.readouterr().out)["matter_id"] == matter.matter_id


def test_agent_can_create_the_same_oriented_matter_as_the_web_quiz(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("TOMORROWKIT_DATA_DIR", str(tmp_path))
    orientation_path = tmp_path / "orientation.json"
    orientation_path.write_text(
        json.dumps(
            {
                "idea_state": "WRITTEN_OR_BUILT",
                "disclosure_state": "PRIVATE",
                "objectives": ["PROTECT_PRODUCT", "BANK_OPTIONALITY"],
                "materials_state": "NOTES_OR_SKETCHES",
                "collaboration_style": "GUIDED_CHOICES",
            }
        )
    )

    agent_tools._create_oriented_matter(orientation_path)

    created = json.loads(capsys.readouterr().out)
    assert created["title"] == "Untitled invention"
    assert created["workflow_phase"] == "SOURCE_LOCK"
    assert created["orientation"]["objectives"] == [
        "PROTECT_PRODUCT",
        "BANK_OPTIONALITY",
    ]
    store = FileMatterStore(matters_directory=tmp_path / "matters")
    assert len(store.list_matters()) == 1


def test_agent_patch_rejects_stale_revision(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TOMORROWKIT_DATA_DIR", str(tmp_path))
    store = FileMatterStore(matters_directory=tmp_path / "matters")
    matter = create_matter_from_intake(
        MatterIntake(title="Test invention", stage=MatterStage.EARLY_IDEA)
    )
    store.save_matter(matter)
    patch_path = tmp_path / "patch.json"
    patch_path.write_text(json.dumps({"expected_updated_at": "2000-01-01T00:00:00Z"}))

    with pytest.raises(ValueError, match="Stale matter revision"):
        agent_tools._apply_patch(str(matter.matter_id), patch_path)


def test_agent_patch_retains_schema_validation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TOMORROWKIT_DATA_DIR", str(tmp_path))
    store = FileMatterStore(matters_directory=tmp_path / "matters")
    matter = create_matter_from_intake(
        MatterIntake(title="Test invention", stage=MatterStage.EARLY_IDEA)
    )
    store.save_matter(matter)
    patch_path = tmp_path / "invalid-patch.json"
    patch_path.write_text(
        json.dumps(
            {
                "expected_updated_at": matter.updated_at.isoformat(),
                "set": {
                    "orientation.objectives": [
                        "PROTECT_PRODUCT",
                        "LICENSE_OR_PARTNER",
                        "BANK_OPTIONALITY",
                        "UNDERSTAND_OPTIONS",
                    ]
                },
            }
        )
    )

    with pytest.raises(ValidationError):
        agent_tools._apply_patch(str(matter.matter_id), patch_path)

    assert store.load_matter(matter.matter_id) == matter


def test_agent_patch_rejects_map_node_link_to_unknown_reference(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TOMORROWKIT_DATA_DIR", str(tmp_path))
    store = FileMatterStore(matters_directory=tmp_path / "matters")
    matter = create_matter_from_intake(
        MatterIntake(title="Test invention", stage=MatterStage.EARLY_IDEA)
    )
    store.save_matter(matter)
    patch_path = tmp_path / "bad-link-patch.json"
    patch_path.write_text(
        json.dumps(
            {
                "expected_updated_at": matter.updated_at.isoformat(),
                "append_map_nodes": [
                    {
                        "kind": "EVIDENCE",
                        "label": "Unsupported link",
                        "linked_reference_id": "ref-00000000000000000000000000000000",
                    }
                ],
            }
        )
    )

    with pytest.raises(ValueError, match="links to unknown reference"):
        agent_tools._apply_patch(str(matter.matter_id), patch_path)

    assert store.load_matter(matter.matter_id) == matter


def test_agent_can_patch_source_lock_on_a_legacy_matter(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("TOMORROWKIT_DATA_DIR", str(tmp_path))
    matters_directory = tmp_path / "matters"
    matters_directory.mkdir()
    store = FileMatterStore(matters_directory=matters_directory)
    matter = create_matter_from_intake(
        MatterIntake(title="Legacy invention", stage=MatterStage.EARLY_IDEA)
    )
    legacy_payload = matter.model_dump(mode="json")
    legacy_payload.pop("workflow_phase")
    legacy_payload.pop("orientation")
    legacy_payload["harvest"] = [
        {
            "checkpoint_id": checkpoint_id,
            "name": checkpoint_id.title(),
            "purpose": "Legacy checkpoint",
            "agent_prompt": "Legacy prompt",
            "status": "NOT_STARTED",
            "notes": "",
        }
        for checkpoint_id in ("prospecting", "drafting", "adversarial")
    ]
    # Preserve intake as the first legacy checkpoint; the comprehension supplies
    # the remaining three original checkpoints.
    legacy_payload["harvest"].insert(
        0,
        {
            "checkpoint_id": "intake",
            "name": "Intake interview",
            "purpose": "Legacy intake",
            "agent_prompt": "Legacy prompt",
            "status": "CAPTURED",
            "notes": "Existing interview notes",
        },
    )
    (matters_directory / f"{matter.matter_id}.json").write_text(
        json.dumps(legacy_payload)
    )
    patch_path = tmp_path / "source-lock-patch.json"
    patch_path.write_text(
        json.dumps(
            {
                "expected_updated_at": matter.updated_at.isoformat(),
                "checkpoints": [
                    {
                        "checkpoint_id": "source_lock",
                        "status": "CAPTURED",
                        "notes": "Original source materials are now inventor-verified.",
                    }
                ],
            }
        )
    )

    agent_tools._apply_patch(str(matter.matter_id), patch_path)

    updated = store.load_matter(matter.matter_id)
    checkpoints = {
        checkpoint.checkpoint_id: checkpoint for checkpoint in updated.harvest
    }
    assert checkpoints["source_lock"].status.value == "CAPTURED"
    assert (
        checkpoints["source_lock"].notes
        == "Original source materials are now inventor-verified."
    )
    assert checkpoints["core_mechanism"].notes == "Existing interview notes"
    assert json.loads(capsys.readouterr().out)["matter_id"] == matter.matter_id


def test_agent_patch_accepts_the_revision_exactly_as_show_prints_it(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # The skill tells the agent to copy `updated_at` verbatim from `show` into
    # `expected_updated_at`; that round trip must never be rejected as stale.
    monkeypatch.setenv("TOMORROWKIT_DATA_DIR", str(tmp_path))
    store = FileMatterStore(matters_directory=tmp_path / "matters")
    matter = create_matter_from_intake(
        MatterIntake(title="Test invention", stage=MatterStage.EARLY_IDEA)
    )
    store.save_matter(matter)

    agent_tools._show_matter(str(matter.matter_id))
    shown_updated_at = json.loads(capsys.readouterr().out)["updated_at"]
    patch_path = tmp_path / "patch.json"
    patch_path.write_text(
        json.dumps(
            {
                "expected_updated_at": shown_updated_at,
                "set": {"title": "Renamed after show"},
            }
        )
    )

    agent_tools._apply_patch(str(matter.matter_id), patch_path)

    assert store.load_matter(matter.matter_id).title == "Renamed after show"
