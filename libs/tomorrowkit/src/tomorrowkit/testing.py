from datetime import datetime, timezone

from imbue.imbue_common.model_update import to_update

from tomorrowkit.data_types import (
    DecisionEntry,
    DecisionId,
    DecisionKind,
    ImportantDate,
    MapEdge,
    MapEdgeId,
    MapNode,
    MapNodeId,
    MapNodeKind,
    MatterDocument,
    MatterId,
    MatterIntake,
    MatterStage,
    ReferenceEntry,
    ReferenceId,
    ReferenceRelationship,
    SourceType,
    VerificationState,
)
from tomorrowkit.factories import create_matter_from_intake


def build_sample_intake() -> MatterIntake:
    return MatterIntake(
        title="Self-sealing irrigation coupler",
        problem_summary="Drip lines pop off under pressure surges.",
        stage=MatterStage.EARLY_IDEA,
        goal="File a provisional before the March demo",
        theme="agriculture hardware",
        known_dates=(
            ImportantDate(label="Farm demo", date_text="2026-03-14", note="public"),
        ),
    )


def build_sample_matter() -> MatterDocument:
    matter = create_matter_from_intake(build_sample_intake())
    node_a = MapNode(
        node_id=MapNodeId.generate(),
        kind=MapNodeKind.COMPONENT,
        label="Compression ring",
        note="Seats under surge pressure",
        x=100.0,
        y=80.0,
    )
    node_b = MapNode(
        node_id=MapNodeId.generate(),
        kind=MapNodeKind.QUESTION,
        label="Material fatigue?",
        x=400.0,
        y=200.0,
    )
    reference = ReferenceEntry(
        reference_id=ReferenceId.generate(),
        title="US 9,999,999 coupler patent",
        citation="https://patents.example/US9999999",
        source_type=SourceType.PATENT_PUBLICATION,
        relevance_note="Closest known coupler design.",
        tags=("coupler", "sealing"),
        relationship=ReferenceRelationship.NEEDS_VERIFICATION,
        source_date_text="2018",
        provenance_note="found during prospecting",
        verification_state=VerificationState.LEAD,
        added_at=datetime(2026, 8, 30, 12, 0, 0, tzinfo=timezone.utc),
    )
    decision = DecisionEntry(
        decision_id=DecisionId.generate(),
        kind=DecisionKind.EMBODIMENT_CHOICE,
        title="Lead with the compression-ring embodiment",
        rationale="Cheapest to manufacture.",
        recorded_at=datetime(2026, 8, 30, 13, 0, 0, tzinfo=timezone.utc),
    )
    edge = MapEdge(
        edge_id=MapEdgeId.generate(),
        source_node_id=node_a.node_id,
        target_node_id=node_b.node_id,
        label="raises",
    )
    return matter.model_copy_update(
        to_update(matter.field_ref().map_nodes, (node_a, node_b)),
        to_update(matter.field_ref().map_edges, (edge,)),
        to_update(matter.field_ref().references, (reference,)),
        to_update(matter.field_ref().decisions, (decision,)),
    )


def build_matter_with_id(matter_id: MatterId) -> MatterDocument:
    matter = build_sample_matter()
    return matter.model_copy_update(to_update(matter.field_ref().matter_id, matter_id))
