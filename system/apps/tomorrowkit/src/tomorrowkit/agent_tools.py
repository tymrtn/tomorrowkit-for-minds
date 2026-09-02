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
    MapNodeId,
    MatterDocument,
    MatterId,
    MatterIntake,
    OrientationProfile,
    ReferenceId,
)
from tomorrowkit.factories import (
    create_matter_from_intake,
    create_matter_from_orientation,
)
from tomorrowkit.storage import FileMatterStore

_DEFAULT_DATA_DIR = Path("data/.apps/tomorrowkit")
_SETTABLE_FIELDS = {
    "title",
    "stage",
    "problem_summary",
    "goal",
    "workflow_phase",
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
}


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
    if path not in _SETTABLE_FIELDS:
        raise AgentToolInputError(f"Unsupported set path: {path}")
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


def _create_matter(input_path: Path) -> None:
    intake = MatterIntake.model_validate(_load_json(input_path))
    matter = create_matter_from_intake(intake)
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
    matter = create_matter_from_orientation(orientation)
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


if __name__ == "__main__":
    main()
