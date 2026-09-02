import io
import zipfile
from typing import Final

from imbue.imbue_common.pure import pure

from tomorrowkit.data_types import LensAssessment, MapNode, MatterDocument

_STAGE_LABELS: Final[dict[str, str]] = {
    "EARLY_IDEA": "Early idea",
    "DRAFT_READY": "Draft-ready",
    "FILED_PROVISIONAL": "Filed provisional",
    "EXISTING_APPLICATION": "Existing application",
}

_SOURCE_TYPE_LABELS: Final[dict[str, str]] = {
    "PATENT_PUBLICATION": "Patent publication",
    "PAPER": "Paper",
    "PRODUCT": "Product",
    "WEB_PAGE": "Web page",
    "STANDARD": "Standard",
    "INVENTOR_MATERIAL": "Inventor material",
    "RESEARCH_LEAD": "Research lead",
}

_RELATIONSHIP_LABELS: Final[dict[str, str]] = {
    "SUPPORTS": "Supports the matter",
    "CONTRADICTS": "Contradicts the matter",
    "DESIGN_AROUND": "Raises a design-around",
    "SEARCH_LEAD": "Creates a search lead",
    "NEEDS_VERIFICATION": "Needs verification",
}

_VERIFICATION_LABELS: Final[dict[str, str]] = {
    "LEAD": "Lead",
    "REVIEWED": "Reviewed",
    "VERIFIED": "Verified",
}

_DECISION_KIND_LABELS: Final[dict[str, str]] = {
    "COMMERCIAL_TERRAIN": "Commercial terrain",
    "EMBODIMENT_CHOICE": "Embodiment choice",
    "DEFERRAL": "Deferral",
    "SUGGESTION_DISPOSITION": "Suggestion disposition",
    "SINGLE_SEED_WAIVER": "Single-seed waiver",
    "WORKFLOW_RETURN": "Returned to an earlier phase",
    "OTHER": "Other",
}

_SEED_ORIGIN_LABELS: Final[dict[str, str]] = {
    "INVENTOR": "Inventor's own",
    "MODEL": "Model proposal",
}

_SEED_STATUS_LABELS: Final[dict[str, str]] = {
    "PROPOSED": "Proposed",
    "ACCEPTED": "Accepted",
    "EDITED": "Accepted with edits",
    "REJECTED": "Rejected",
    "DEFERRED": "Deferred",
}

_SEED_ROUTE_LABELS: Final[dict[str, str]] = {
    "STANDALONE": "Standalone filing",
    "COMBINE": "Combine with another seed",
    "LATER_FILING": "Later filing",
    "DEFER": "Defer",
    "NO_FILE": "No filing",
}

_POSTURE_LABELS: Final[dict[str, str]] = {
    "LEAN_CORE_STUB": "Lean-core priority stub",
    "DISCLOSURE_RESERVOIR": "Disclosure reservoir",
    "LAYERED_PROVISIONALS": "Layered provisionals",
}

_LENS_LEVEL_LABELS: Final[dict[str, str]] = {
    "NOT_ASSESSED": "Not assessed",
    "WEAK": "Weak",
    "DEVELOPING": "Developing",
    "SOLID": "Solid",
}

_NODE_KIND_LABELS: Final[dict[str, str]] = {
    "COMPONENT": "Component",
    "ACTOR": "Actor",
    "INPUT": "Input",
    "OUTPUT": "Output",
    "STEP": "Step",
    "ALTERNATIVE": "Alternative",
    "QUESTION": "Question",
    "ASSUMPTION": "Assumption",
    "EVIDENCE": "Evidence",
}

_HARVEST_STATUS_LABELS: Final[dict[str, str]] = {
    "NOT_STARTED": "Not started",
    "IN_PROGRESS": "In progress",
    "CAPTURED": "Captured",
}


@pure
def _text_or_placeholder(text: str) -> str:
    return text.strip() if text.strip() else "_Nothing recorded yet._"


@pure
def render_readme_markdown(matter: MatterDocument) -> str:
    lines = [
        f"# {matter.title} -- portable matter record",
        "",
        "This folder is the complete, portable export of one invention matter from the",
        "Tomorrowkit provisional workspace. It is yours to keep, adapt, and share",
        "selectively with counsel or collaborators.",
        "",
        "Contents:",
        "",
        "- `matter.json` -- the complete raw record (everything below derives from this file)",
        "- `invention-brief.md` -- the invention brief, in the inventor's own words",
        "- `invention-map.md` -- the invention map, written out as text",
        "- `reference-library.md` -- every reference entry with its metadata",
        "- `decision-ledger.md` -- the recorded human decisions and rationale",
        "- `seed-portfolio.md` -- the harvested seeds, their dispositions, and the provisional posture",
        "- `scorecard.md` -- the two provisional-stage lens self-reviews",
        "- `harvest-notes.md` -- notes from the guided invention harvest",
        "",
        "This export is an organized working record. It is not a filed document, a formal",
        "information-disclosure statement, or legal advice.",
        "",
        f"Stage at export: {_STAGE_LABELS[matter.stage.value]}",
        f"Created: {matter.created_at.date().isoformat()}",
        f"Last saved: {matter.updated_at.date().isoformat()}",
        "",
    ]
    return "\n".join(lines)


@pure
def render_brief_markdown(matter: MatterDocument) -> str:
    brief = matter.brief
    lines = [
        f"# Invention brief -- {matter.title}",
        "",
        f"**Working title:** {matter.title}",
        "",
        f"**Stage:** {_STAGE_LABELS[matter.stage.value]}",
        "",
        f"**Problem and intended approach:** {_text_or_placeholder(matter.problem_summary)}",
        "",
        f"**Immediate goal:** {_text_or_placeholder(matter.goal)}",
        "",
    ]
    if matter.known_dates:
        lines.extend(["## Important dates", ""])
        for known_date in matter.known_dates:
            note_suffix = f" -- {known_date.note}" if known_date.note.strip() else ""
            lines.append(
                f"- **{known_date.label}**: {known_date.date_text}{note_suffix}"
            )
        lines.append("")
    lines.extend(
        [
            "## Problem",
            "",
            _text_or_placeholder(brief.problem),
            "",
            "## Proposed mechanism",
            "",
            _text_or_placeholder(brief.mechanism),
            "",
            "## Intended result",
            "",
            _text_or_placeholder(brief.intended_result),
            "",
            "## Alternatives and variations",
            "",
            _text_or_placeholder(brief.alternatives),
            "",
            "## Open questions",
            "",
            _text_or_placeholder(brief.open_questions),
            "",
            "## Current status",
            "",
            f"**What is known:** {_text_or_placeholder(matter.what_is_known)}",
            "",
            f"**What remains uncertain:** {_text_or_placeholder(matter.what_is_uncertain)}",
            "",
            f"**Next recommended action:** {_text_or_placeholder(matter.next_action)}",
            "",
        ]
    )
    return "\n".join(lines)


@pure
def _node_display_label(node: MapNode) -> str:
    return f"{node.label} ({_NODE_KIND_LABELS[node.kind.value]})"


@pure
def render_map_markdown(matter: MatterDocument) -> str:
    lines = [
        f"# Invention map -- {matter.title}",
        "",
        "The invention map is a thinking canvas, not a formal patent drawing.",
        "Node positions live in `matter.json`; this file writes the structure out as text.",
        "",
    ]
    if not matter.map_nodes:
        lines.extend(["_The map is empty._", ""])
        return "\n".join(lines)
    node_by_id = {node.node_id: node for node in matter.map_nodes}
    lines.extend(["## Elements", ""])
    for node in matter.map_nodes:
        lines.append(f"- **{node.label}** -- {_NODE_KIND_LABELS[node.kind.value]}")
        if node.note.strip():
            lines.append(f"  - Note: {node.note.strip()}")
        if node.linked_reference_id:
            reference_titles = [
                reference.title
                for reference in matter.references
                if reference.reference_id == node.linked_reference_id
            ]
            if reference_titles:
                lines.append(f"  - Evidence: {reference_titles[0]}")
    lines.append("")
    if matter.map_edges:
        lines.extend(["## Connections", ""])
        for edge in matter.map_edges:
            source = node_by_id.get(edge.source_node_id)
            target = node_by_id.get(edge.target_node_id)
            if source is None or target is None:
                continue
            label_part = f" ({edge.label})" if edge.label.strip() else ""
            lines.append(
                f"- {_node_display_label(source)} -> {_node_display_label(target)}{label_part}"
            )
        lines.append("")
    return "\n".join(lines)


@pure
def render_reference_library_markdown(matter: MatterDocument) -> str:
    lines = [
        f"# Reference library -- {matter.title}",
        "",
        "An organized research and disclosure record. It is not a filed",
        "information-disclosure statement and does not satisfy any formal filing obligation.",
        "",
    ]
    if not matter.references:
        lines.extend(["_The library is empty._", ""])
        return "\n".join(lines)
    for reference in matter.references:
        lines.extend(
            [
                f"## {reference.title}",
                "",
                f"- Source type: {_SOURCE_TYPE_LABELS[reference.source_type.value]}",
                f"- Relationship: {_RELATIONSHIP_LABELS[reference.relationship.value]}",
                f"- Verification: {_VERIFICATION_LABELS[reference.verification_state.value]}",
            ]
        )
        if reference.citation.strip():
            lines.append(f"- Citation / link: {reference.citation.strip()}")
        if reference.source_date_text.strip():
            lines.append(f"- Source date: {reference.source_date_text.strip()}")
        if reference.tags:
            lines.append(f"- Tags: {', '.join(reference.tags)}")
        if reference.provenance_note.strip():
            lines.append(f"- Provenance: {reference.provenance_note.strip()}")
        lines.append(f"- Added: {reference.added_at.date().isoformat()}")
        if reference.relevance_note.strip():
            lines.extend(["", reference.relevance_note.strip()])
        lines.append("")
    return "\n".join(lines)


@pure
def render_decision_ledger_markdown(matter: MatterDocument) -> str:
    lines = [
        f"# Decision ledger -- {matter.title}",
        "",
        "The important human decisions behind this matter, with their rationale.",
        "",
    ]
    if not matter.decisions:
        lines.extend(["_No decisions recorded yet._", ""])
        return "\n".join(lines)
    for decision in sorted(
        matter.decisions, key=lambda entry: entry.recorded_at, reverse=True
    ):
        lines.extend(
            [
                f"## {decision.title}",
                "",
                f"- Kind: {_DECISION_KIND_LABELS[decision.kind.value]}",
                f"- Recorded: {decision.recorded_at.date().isoformat()}",
                "",
                _text_or_placeholder(decision.rationale),
                "",
            ]
        )
    return "\n".join(lines)


@pure
def _render_lens_markdown(
    lens_name: str, lens_question: str, assessment: LensAssessment
) -> list[str]:
    return [
        f"## {lens_name}",
        "",
        f"_{lens_question}_",
        "",
        f"- Self-assessed level: {_LENS_LEVEL_LABELS[assessment.level.value]}",
        "",
        f"**Coverage:** {_text_or_placeholder(assessment.coverage_notes)}",
        "",
        f"**Evidence:** {_text_or_placeholder(assessment.evidence_notes)}",
        "",
        f"**Missing prerequisites:** {_text_or_placeholder(assessment.missing_prerequisites)}",
        "",
        f"**Reasoning:** {_text_or_placeholder(assessment.reasoning)}",
        "",
    ]


@pure
def render_scorecard_markdown(matter: MatterDocument) -> str:
    lines = [
        f"# Scorecard -- {matter.title}",
        "",
        "Two separate lenses, never merged into a single score. These are structured",
        "self-reviews recorded by the inventor and their agent -- not independent",
        "council scoring and not a legal conclusion.",
        "",
    ]
    lines.extend(
        _render_lens_markdown(
            "IVS -- Invention Value Score",
            "Does the inventor-approved terrain appear worth pursuing?",
            matter.scorecard.invention_value,
        )
    )
    lines.extend(
        _render_lens_markdown(
            "PAS -- Priority Asset Score",
            "Does the provisional record capture that terrain?",
            matter.scorecard.priority_asset,
        )
    )
    return "\n".join(lines)


@pure
def render_seed_portfolio_markdown(matter: MatterDocument) -> str:
    lines = [
        f"# Seed portfolio -- {matter.title}",
        "",
        "Every distinct technical seed harvested from the conversation, with the",
        "inventor's disposition, its route, and the assay notes. Model proposals stay",
        "labelled as proposals until the inventor acts on them.",
        "",
    ]
    if not matter.seeds:
        lines.extend(["_No seeds harvested yet._", ""])
    for seed in matter.seeds:
        route = _SEED_ROUTE_LABELS[seed.route.value] if seed.route else "Not routed yet"
        lines.extend(
            [
                f"## {seed.label}",
                "",
                f"- Origin: {_SEED_ORIGIN_LABELS[seed.origin.value]}",
                f"- Status: {_SEED_STATUS_LABELS[seed.status.value]}",
                f"- Route: {route}",
                "",
                f"**Mechanism:** {_text_or_placeholder(seed.mechanism)}",
                "",
                f"**Closest art:** {_text_or_placeholder(seed.closest_art_note)}",
                "",
                f"**Design-arounds:** {_text_or_placeholder(seed.design_around_note)}",
                "",
                f"**Evidence:** {_text_or_placeholder(seed.evidence_note)}",
                "",
            ]
        )
    posture = matter.posture
    lines.extend(["## Provisional posture", ""])
    if posture.posture is None:
        lines.extend(["_No posture chosen yet._", ""])
        return "\n".join(lines)
    approval = "approved by the inventor" if posture.approved_by_inventor else "not yet approved by the inventor"
    lines.extend(
        [
            f"- Posture: {_POSTURE_LABELS[posture.posture.value]} ({approval})",
            "",
            f"**Why:** {_text_or_placeholder(posture.rationale)}",
            "",
            f"**Needs the first date:** {_text_or_placeholder(posture.first_date_material)}",
            "",
            f"**Withheld or staged:** {_text_or_placeholder(posture.withheld_material)}",
            "",
            f"**Constraints:** {_text_or_placeholder(posture.constraints)}",
            "",
            f"**Next trigger:** {_text_or_placeholder(posture.next_trigger)}",
            "",
            f"**Earliest conversion deadline:** {_text_or_placeholder(posture.conversion_deadline_text)}",
            "",
        ]
    )
    return "\n".join(lines)


@pure
def render_harvest_markdown(matter: MatterDocument) -> str:
    lines = [
        f"# Harvest notes -- {matter.title}",
        "",
        "Checkpoints from the guided invention harvest, run with the inventor's own agent.",
        "",
    ]
    if not matter.harvest:
        lines.extend(["_No harvest checkpoints._", ""])
        return "\n".join(lines)
    for checkpoint in matter.harvest:
        lines.extend(
            [
                f"## {checkpoint.name}",
                "",
                f"- Status: {_HARVEST_STATUS_LABELS[checkpoint.status.value]}",
                f"- Purpose: {checkpoint.purpose}",
                "",
                _text_or_placeholder(checkpoint.notes),
                "",
            ]
        )
    return "\n".join(lines)


@pure
def build_export_zip_bytes(matter: MatterDocument) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("README.md", render_readme_markdown(matter))
        archive.writestr("matter.json", matter.model_dump_json(indent=2))
        archive.writestr("invention-brief.md", render_brief_markdown(matter))
        archive.writestr("invention-map.md", render_map_markdown(matter))
        archive.writestr(
            "reference-library.md", render_reference_library_markdown(matter)
        )
        archive.writestr("decision-ledger.md", render_decision_ledger_markdown(matter))
        archive.writestr("seed-portfolio.md", render_seed_portfolio_markdown(matter))
        archive.writestr("scorecard.md", render_scorecard_markdown(matter))
        archive.writestr("harvest-notes.md", render_harvest_markdown(matter))
    return buffer.getvalue()
