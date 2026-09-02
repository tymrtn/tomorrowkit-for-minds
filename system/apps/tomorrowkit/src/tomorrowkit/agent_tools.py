"""Deterministic bridge between a Minds agent and the Tomorrowkit record."""

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import click

from tomorrowkit.data_types import (
    DecisionId,
    ImportantDate,
    MapEdgeId,
    MapNodeId,
    MatterDocument,
    MatterId,
    MatterIntake,
    MatterStage,
    OrientationProfile,
    ReferenceId,
    SeedId,
    WorkflowPhase,
)
from tomorrowkit.factories import (
    create_matter_from_intake,
    create_matter_from_orientation,
)
from tomorrowkit.steering import PHASE_ORDER, evaluate_gate
from tomorrowkit.storage import FileMatterStore

_DEFAULT_DATA_DIR = Path("data/.apps/tomorrowkit")
_SETTABLE_FIELDS = {
    "title",
    "stage",
    "problem_summary",
    "goal",
    "what_is_known",
    "what_is_uncertain",
    "next_action",
    "orientation.idea_state",
    "orientation.disclosure_state",
    "orientation.objectives",
    "orientation.materials_state",
    "orientation.collaboration_style",
    "brief.problem",
    "brief.mechanism",
    "brief.intended_result",
    "brief.alternatives",
    "brief.open_questions",
    "posture.posture",
    "posture.rationale",
    "posture.first_date_material",
    "posture.withheld_material",
    "posture.constraints",
    "posture.next_trigger",
    "posture.conversion_deadline_text",
    "posture.approved_by_inventor",
    *(
        f"scorecard.{lens}.{field}"
        for lens in ("invention_value", "priority_asset")
        for field in (
            "level",
            "coverage_notes",
            "evidence_notes",
            "missing_prerequisites",
            "reasoning",
        )
    ),
}
# A priority-asset score is only meaningful once a provisional candidate or a
# filed provisional exists; before that the lens stays "not assessed".
_CANDIDATE_PHASES = {WorkflowPhase.ATTACK_REPAIR.value, WorkflowPhase.READY_HANDOFF.value}
_FILED_STAGES = {MatterStage.FILED_PROVISIONAL.value, MatterStage.EXISTING_APPLICATION.value}


class AgentToolInputError(ValueError):
    """The agent supplied an invalid or stale workspace operation."""


def _write_json(value: Any) -> None:
    serialized = value if isinstance(value, str) else json.dumps(value, indent=2)
    click.echo(serialized)


def _store() -> FileMatterStore:
    data_dir = Path(os.environ.get("TOMORROWKIT_DATA_DIR", _DEFAULT_DATA_DIR))
    return FileMatterStore(matters_directory=data_dir / "matters")


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text())
    if not isinstance(payload, dict):
        raise AgentToolInputError("Input must be a JSON object")
    return payload


def _apply_set(payload: dict[str, Any], path: str, value: Any) -> None:
    if path == "workflow_phase":
        raise AgentToolInputError(
            "workflow_phase moves with `tomorrowkit-workspace advance`, not `set`"
        )
    if path not in _SETTABLE_FIELDS:
        raise AgentToolInputError(f"Unsupported set path: {path}")
    if path.startswith("scorecard.priority_asset.") and not (
        payload["workflow_phase"] in _CANDIDATE_PHASES
        or payload["stage"] in _FILED_STAGES
    ):
        raise AgentToolInputError(
            "The priority-asset lens stays unassessed until a provisional candidate "
            "or filed provisional exists"
        )
    target = payload
    parts = path.split(".")
    for part in parts[:-1]:
        target = target[part]
    target[parts[-1]] = value


def _apply_checkpoint(payload: dict[str, Any], update: dict[str, Any]) -> None:
    checkpoint_id = update.get("checkpoint_id")
    for checkpoint in payload["harvest"]:
        if checkpoint["checkpoint_id"] == checkpoint_id:
            if "status" in update:
                checkpoint["status"] = update["status"]
            if "notes" in update:
                checkpoint["notes"] = update["notes"]
            return
    raise AgentToolInputError(f"Unknown checkpoint: {checkpoint_id}")


def _append_reference(payload: dict[str, Any], entry: dict[str, Any]) -> None:
    candidate = dict(entry)
    candidate["reference_id"] = str(ReferenceId.generate())
    candidate["added_at"] = datetime.now(timezone.utc).isoformat()
    candidate.setdefault("citation", "")
    candidate.setdefault("relevance_note", "")
    candidate.setdefault("tags", [])
    candidate.setdefault("source_date_text", "")
    candidate.setdefault("provenance_note", "Added by the configured Minds agent")
    candidate.setdefault("verification_state", "LEAD")
    payload["references"].append(candidate)


def _append_decision(payload: dict[str, Any], entry: dict[str, Any]) -> None:
    candidate = dict(entry)
    candidate["decision_id"] = str(DecisionId.generate())
    candidate["recorded_at"] = datetime.now(timezone.utc).isoformat()
    candidate.setdefault("rationale", "")
    payload["decisions"].append(candidate)


def _append_date(payload: dict[str, Any], entry: dict[str, Any]) -> None:
    """Append one validated date, without duplicating an identical retry."""
    candidate = ImportantDate.model_validate(entry).model_dump(mode="json")
    if candidate not in payload["known_dates"]:
        payload["known_dates"].append(candidate)


def _append_map_node(payload: dict[str, Any], entry: dict[str, Any]) -> None:
    """Append one node while keeping identity and basic placement server-owned."""
    candidate = dict(entry)
    candidate["node_id"] = str(MapNodeId.generate())
    candidate.setdefault("note", "")
    candidate.setdefault("linked_reference_id", "")

    node_index = len(payload["map_nodes"])
    candidate.setdefault("x", float(80 + (node_index % 3) * 280))
    candidate.setdefault("y", float(80 + (node_index // 3) * 160))

    linked_reference_id = candidate["linked_reference_id"]
    known_reference_ids = {
        reference["reference_id"] for reference in payload["references"]
    }
    if linked_reference_id and linked_reference_id not in known_reference_ids:
        raise AgentToolInputError(
            f"Map node links to unknown reference: {linked_reference_id}"
        )
    payload["map_nodes"].append(candidate)


def _append_map_edge(payload: dict[str, Any], entry: dict[str, Any]) -> None:
    known = {node["node_id"] for node in payload["map_nodes"]}
    for key in ("source_node_id", "target_node_id"):
        if entry.get(key) not in known:
            raise AgentToolInputError(f"Map edge refers to an unknown node: {entry.get(key)}")
    candidate = dict(entry)
    candidate["edge_id"] = str(MapEdgeId.generate())
    candidate.setdefault("label", "")
    payload["map_edges"].append(candidate)


def _append_seed(payload: dict[str, Any], entry: dict[str, Any]) -> None:
    candidate = dict(entry)
    now = datetime.now(timezone.utc).isoformat()
    candidate["seed_id"] = str(SeedId.generate())
    candidate["created_at"] = now
    candidate["updated_at"] = now
    candidate.setdefault("status", "PROPOSED")
    payload["seeds"].append(candidate)


_SEED_UPDATABLE = {
    "label",
    "mechanism",
    "status",
    "route",
    "closest_art_note",
    "design_around_note",
    "evidence_note",
}


def _update_seed(payload: dict[str, Any], update: dict[str, Any]) -> None:
    seed_id = update.get("seed_id")
    for seed in payload["seeds"]:
        if seed["seed_id"] == seed_id:
            for key, value in update.items():
                if key == "seed_id":
                    continue
                if key not in _SEED_UPDATABLE:
                    raise AgentToolInputError(f"Unsupported seed field: {key}")
                seed[key] = value
            seed["updated_at"] = datetime.now(timezone.utc).isoformat()
            return
    raise AgentToolInputError(f"Unknown seed: {seed_id}")


def _stamp_chat_agent(payload: dict[str, Any]) -> None:
    """Remember which chat agent owns the matter so the tab can message it."""
    if not payload.get("chat_agent_id"):
        payload["chat_agent_id"] = os.environ.get("MNGR_AGENT_ID", "")


def _list_matters() -> None:
    summaries = [
        {
            "matter_id": str(matter.matter_id),
            "title": matter.title,
            "stage": matter.stage.value,
            "updated_at": matter.updated_at.isoformat(),
        }
        for matter in _store().list_matters()
    ]
    _write_json(summaries)


def _show_matter(raw_matter_id: str) -> None:
    matter = _store().load_matter(MatterId(raw_matter_id))
    _write_json(matter.model_dump_json(indent=2))


def _with_chat_agent(matter: MatterDocument) -> MatterDocument:
    payload = matter.model_dump(mode="json")
    _stamp_chat_agent(payload)
    return MatterDocument.model_validate(payload)


def _create_matter(input_path: Path) -> None:
    intake = MatterIntake.model_validate(_load_json(input_path))
    matter = _with_chat_agent(create_matter_from_intake(intake))
    _store().save_matter(matter)
    _write_json(matter.model_dump_json(indent=2))


def _create_oriented_matter(input_path: Path) -> None:
    orientation = OrientationProfile.model_validate(_load_json(input_path))
    if (
        orientation.idea_state is None
        or orientation.disclosure_state is None
        or not orientation.objectives
        or orientation.materials_state is None
        or orientation.collaboration_style is None
    ):
        raise AgentToolInputError("Expected all five orientation answers")
    matter = _with_chat_agent(create_matter_from_orientation(orientation))
    _store().save_matter(matter)
    _write_json(matter.model_dump_json(indent=2))


def _parse_expected_updated_at(raw: Any) -> datetime:
    # `show` prints the record with pydantic's `Z` suffix while `isoformat()`
    # emits `+00:00`; accept either so the agent can copy the value verbatim.
    if not isinstance(raw, str):
        raise AgentToolInputError("Expected `expected_updated_at` from `show`")
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError as e:
        raise AgentToolInputError(f"Invalid expected_updated_at: {raw!r}") from e


def _apply_patch(raw_matter_id: str, patch_path: Path) -> None:
    store = _store()
    current = store.load_matter(MatterId(raw_matter_id))
    patch = _load_json(patch_path)
    expected = _parse_expected_updated_at(patch.get("expected_updated_at"))
    if expected != current.updated_at:
        raise AgentToolInputError(
            "Stale matter revision; run show again before applying changes"
        )

    payload = current.model_dump(mode="json")
    for path, value in patch.get("set", {}).items():
        _apply_set(payload, path, value)
    for update in patch.get("checkpoints", []):
        _apply_checkpoint(payload, update)
    for entry in patch.get("append_references", []):
        _append_reference(payload, entry)
    for entry in patch.get("append_decisions", []):
        _append_decision(payload, entry)
    for entry in patch.get("append_dates", []):
        _append_date(payload, entry)
    for entry in patch.get("append_map_nodes", []):
        _append_map_node(payload, entry)
    for entry in patch.get("append_map_edges", []):
        _append_map_edge(payload, entry)
    for entry in patch.get("append_seeds", []):
        _append_seed(payload, entry)
    for update in patch.get("update_seeds", []):
        _update_seed(payload, update)
    _stamp_chat_agent(payload)

    payload["updated_at"] = datetime.now(timezone.utc).isoformat()
    updated = MatterDocument.model_validate(payload)
    store.save_matter_if_current(updated, current.updated_at)
    _write_json(updated.model_dump_json(indent=2))


def _next_matter(raw_matter_id: str) -> None:
    matter = _store().load_matter(MatterId(raw_matter_id))
    report = evaluate_gate(matter)
    _write_json(
        {
            "phase": report.phase.value,
            "next_phase": report.next_phase.value if report.next_phase else None,
            "can_advance": report.can_advance,
            "gaps": [gap.model_dump(mode="json") for gap in report.gaps],
            "focus": report.focus,
        }
    )


def _advance_matter(raw_matter_id: str, raw_phase: str, reason: str) -> None:
    store = _store()
    current = store.load_matter(MatterId(raw_matter_id))
    try:
        target = WorkflowPhase(raw_phase)
    except ValueError as e:
        raise AgentToolInputError(f"Unknown workflow phase: {raw_phase}") from e
    here = PHASE_ORDER.index(current.workflow_phase)
    there = PHASE_ORDER.index(target)
    if there == here:
        raise AgentToolInputError(f"The matter is already at {target.value}")

    payload = current.model_dump(mode="json")
    if there > here:
        # Walk forward one phase at a time; every gate on the way must hold.
        probe = current
        for step in PHASE_ORDER[here:there]:
            probe = probe.model_copy(update={"workflow_phase": step})
            report = evaluate_gate(probe)
            if not report.can_advance:
                unmet = "; ".join(
                    f"{gap.condition} ({gap.detail})" for gap in report.gaps if not gap.met
                )
                raise AgentToolInputError(
                    f"Advance to {target.value} is not yet supported by the record: {unmet}"
                )
    else:
        if not reason.strip():
            raise AgentToolInputError(
                "Moving backward needs a --reason so the record shows why"
            )
        _append_decision(
            payload,
            {
                "kind": "WORKFLOW_RETURN",
                "title": f"Returned to {target.value} from {current.workflow_phase.value}",
                "rationale": reason.strip(),
            },
        )
    payload["workflow_phase"] = target.value
    payload["updated_at"] = datetime.now(timezone.utc).isoformat()
    updated = MatterDocument.model_validate(payload)
    store.save_matter_if_current(updated, current.updated_at)
    _write_json(updated.model_dump_json(indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list")
    show = subparsers.add_parser("show")
    show.add_argument("matter_id")
    create = subparsers.add_parser("create")
    create.add_argument("--input", type=Path, required=True)
    orient = subparsers.add_parser("orient")
    orient.add_argument("--input", type=Path, required=True)
    apply = subparsers.add_parser("apply")
    apply.add_argument("matter_id")
    apply.add_argument("--patch", type=Path, required=True)
    nxt = subparsers.add_parser("next", help="What the record still lacks, and what to ask")
    nxt.add_argument("matter_id")
    advance = subparsers.add_parser("advance", help="Move the phase marker when the record supports it")
    advance.add_argument("matter_id")
    advance.add_argument("phase")
    advance.add_argument("--reason", default="", help="Required when moving backward")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "list":
        _list_matters()
    elif args.command == "show":
        _show_matter(args.matter_id)
    elif args.command == "create":
        _create_matter(args.input)
    elif args.command == "orient":
        _create_oriented_matter(args.input)
    elif args.command == "apply":
        _apply_patch(args.matter_id, args.patch)
    elif args.command == "next":
        _next_matter(args.matter_id)
    elif args.command == "advance":
        _advance_matter(args.matter_id, args.phase, args.reason)


if __name__ == "__main__":
    main()
