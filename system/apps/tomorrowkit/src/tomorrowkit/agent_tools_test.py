import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from tomorrowkit import agent_tools
from tomorrowkit.data_types import MapNodeId, MatterIntake, MatterStage, WorkflowPhase
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


def _seed_matter(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("TOMORROWKIT_DATA_DIR", str(tmp_path))
    store = FileMatterStore(matters_directory=tmp_path / "matters")
    matter = create_matter_from_intake(
        MatterIntake(title="Test invention", stage=MatterStage.EARLY_IDEA)
    )
    store.save_matter(matter)
    return store, matter


def _apply(tmp_path: Path, matter_id, patch: dict) -> None:
    store = FileMatterStore(matters_directory=tmp_path / "matters")
    current = store.load_matter(matter_id)
    patch = {"expected_updated_at": current.updated_at.isoformat(), **patch}
    patch_path = tmp_path / "patch.json"
    patch_path.write_text(json.dumps(patch))
    agent_tools._apply_patch(str(matter_id), patch_path)


def test_agent_appends_and_updates_seeds(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store, matter = _seed_matter(tmp_path, monkeypatch)

    _apply(
        tmp_path,
        matter.matter_id,
        {
            "append_seeds": [
                {"label": "Pressure-energised lip", "mechanism": "Lip grips harder as pressure rises.", "origin": "INVENTOR"},
                {"label": "Bleed groove", "mechanism": "Vents the first surge.", "origin": "MODEL"},
            ]
        },
    )
    seeds = store.load_matter(matter.matter_id).seeds
    assert [seed.label for seed in seeds] == ["Pressure-energised lip", "Bleed groove"]
    assert {seed.status.value for seed in seeds} == {"PROPOSED"}
    assert seeds[0].seed_id != seeds[1].seed_id

    _apply(
        tmp_path,
        matter.matter_id,
        {
            "update_seeds": [
                {"seed_id": str(seeds[1].seed_id), "status": "ACCEPTED", "route": "LATER_FILING", "closest_art_note": "No relief-groove art found yet; search incomplete."}
            ]
        },
    )
    updated = store.load_matter(matter.matter_id).seeds[1]
    assert updated.status.value == "ACCEPTED"
    assert updated.route is not None and updated.route.value == "LATER_FILING"
    assert "search incomplete" in updated.closest_art_note
    assert updated.updated_at > updated.created_at

    with pytest.raises(ValueError, match="Unknown seed"):
        _apply(tmp_path, matter.matter_id, {"update_seeds": [{"seed_id": "seed-nope", "status": "REJECTED"}]})


def test_agent_appends_map_edges_between_known_nodes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store, matter = _seed_matter(tmp_path, monkeypatch)
    _apply(
        tmp_path,
        matter.matter_id,
        {"append_map_nodes": [{"kind": "INPUT", "label": "Line pressure"}, {"kind": "OUTPUT", "label": "Grip force"}]},
    )
    nodes = store.load_matter(matter.matter_id).map_nodes

    _apply(
        tmp_path,
        matter.matter_id,
        {"append_map_edges": [{"source_node_id": str(nodes[0].node_id), "target_node_id": str(nodes[1].node_id), "label": "raises"}]},
    )
    edges = store.load_matter(matter.matter_id).map_edges
    assert len(edges) == 1 and edges[0].label == "raises"

    with pytest.raises(ValueError, match="unknown node"):
        _apply(tmp_path, matter.matter_id, {"append_map_edges": [{"source_node_id": "node-nope", "target_node_id": str(nodes[1].node_id)}]})


def test_agent_sets_posture_but_cannot_set_workflow_phase_directly(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store, matter = _seed_matter(tmp_path, monkeypatch)

    _apply(
        tmp_path,
        matter.matter_id,
        {"set": {"posture.posture": "LEAN_CORE_STUB", "posture.rationale": "Core is settled.", "posture.approved_by_inventor": True}},
    )
    posture = store.load_matter(matter.matter_id).posture
    assert posture.posture is not None and posture.posture.value == "LEAN_CORE_STUB"
    assert posture.approved_by_inventor is True

    with pytest.raises(ValueError, match="advance"):
        _apply(tmp_path, matter.matter_id, {"set": {"workflow_phase": "READY_HANDOFF"}})


def test_agent_scores_value_any_time_but_priority_only_with_a_candidate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store, matter = _seed_matter(tmp_path, monkeypatch)

    _apply(tmp_path, matter.matter_id, {"set": {"scorecard.invention_value.level": "DEVELOPING", "scorecard.invention_value.evidence_notes": "Bench test, three cycles."}})
    assert store.load_matter(matter.matter_id).scorecard.invention_value.level.value == "DEVELOPING"

    with pytest.raises(ValueError, match="provisional candidate"):
        _apply(tmp_path, matter.matter_id, {"set": {"scorecard.priority_asset.level": "WEAK"}})

    _apply(tmp_path, matter.matter_id, {"set": {"stage": "FILED_PROVISIONAL"}})
    _apply(tmp_path, matter.matter_id, {"set": {"scorecard.priority_asset.level": "WEAK"}})
    assert store.load_matter(matter.matter_id).scorecard.priority_asset.level.value == "WEAK"


def test_bridge_stamps_the_chat_agent_that_owns_the_matter(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("TOMORROWKIT_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("MNGR_AGENT_ID", "agent-abc123")
    intake_path = tmp_path / "intake.json"
    intake_path.write_text(json.dumps({"title": "Untitled invention", "stage": "EARLY_IDEA"}))

    agent_tools._create_matter(intake_path)

    created = json.loads(capsys.readouterr().out)
    assert created["chat_agent_id"] == "agent-abc123"


def test_next_reports_the_seed_gate_and_advance_honours_it(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    store, matter = _seed_matter(tmp_path, monkeypatch)
    store.save_matter(matter.model_copy(update={"workflow_phase": WorkflowPhase.SEED_EXPANSION}))
    _apply(tmp_path, matter.matter_id, {"append_seeds": [{"label": "Lip", "mechanism": "Grips harder under pressure.", "origin": "INVENTOR", "status": "ACCEPTED"}]})

    capsys.readouterr()
    agent_tools._next_matter(str(matter.matter_id))
    report = json.loads(capsys.readouterr().out)
    assert report["phase"] == "SEED_EXPANSION"
    assert report["next_phase"] == "SEED_ASSAY"
    assert report["can_advance"] is False
    assert any(not gap["met"] and "seed" in gap["condition"].lower() for gap in report["gaps"])
    assert report["focus"]

    with pytest.raises(ValueError, match="not yet supported"):
        agent_tools._advance_matter(str(matter.matter_id), "SEED_ASSAY", reason="")
    assert store.load_matter(matter.matter_id).workflow_phase is WorkflowPhase.SEED_EXPANSION

    _apply(tmp_path, matter.matter_id, {"append_seeds": [{"label": "Bleed groove", "mechanism": "Vents the first surge.", "origin": "MODEL", "status": "EDITED"}]})
    capsys.readouterr()
    agent_tools._next_matter(str(matter.matter_id))
    assert json.loads(capsys.readouterr().out)["can_advance"] is True

    agent_tools._advance_matter(str(matter.matter_id), "SEED_ASSAY", reason="")
    capsys.readouterr()
    assert store.load_matter(matter.matter_id).workflow_phase is WorkflowPhase.SEED_ASSAY


def test_advance_backward_needs_a_reason_and_records_it(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    store, matter = _seed_matter(tmp_path, monkeypatch)
    store.save_matter(matter.model_copy(update={"workflow_phase": WorkflowPhase.SEED_ASSAY}))

    with pytest.raises(ValueError, match="reason"):
        agent_tools._advance_matter(str(matter.matter_id), "CORE_MECHANISM", reason="")

    agent_tools._advance_matter(str(matter.matter_id), "CORE_MECHANISM", reason="Inventor revealed a second operating cycle.")
    capsys.readouterr()
    reloaded = store.load_matter(matter.matter_id)
    assert reloaded.workflow_phase is WorkflowPhase.CORE_MECHANISM
    assert reloaded.decisions[-1].kind.value == "WORKFLOW_RETURN"
    assert "second operating cycle" in reloaded.decisions[-1].rationale
