"""What the record still lacks before its phase marker can honestly move on.

Pure functions over a MatterDocument. Nothing here is shown to the inventor;
the agent reads the report to decide what to ask about next.
"""

from imbue.imbue_common.frozen_model import FrozenModel
from imbue.imbue_common.pure import pure
from pydantic import Field

from tomorrowkit.data_types import (
    DecisionKind,
    HarvestStatus,
    MatterDocument,
    SeedStatus,
    SourceType,
    WorkflowPhase,
)

PHASE_ORDER: tuple[WorkflowPhase, ...] = tuple(WorkflowPhase)
_CONFIRMED_SEED_STATUSES = frozenset({SeedStatus.ACCEPTED, SeedStatus.EDITED})


class GateCondition(FrozenModel):
    condition: str = Field(description="What the record must contain, in plain words")
    met: bool = Field(description="Whether the record contains it now")
    detail: str = Field(description="What is there, or what is missing")


class GateReport(FrozenModel):
    phase: WorkflowPhase
    next_phase: WorkflowPhase | None
    can_advance: bool
    gaps: tuple[GateCondition, ...]
    focus: str = Field(description="One sentence for the agent about what to ask next")


@pure
def phase_after(phase: WorkflowPhase) -> WorkflowPhase | None:
    index = PHASE_ORDER.index(phase)
    return PHASE_ORDER[index + 1] if index + 1 < len(PHASE_ORDER) else None


@pure
def _checkpoint_captured(matter: MatterDocument, checkpoint_id: str) -> GateCondition:
    status = next(
        (c.status for c in matter.harvest if c.checkpoint_id == checkpoint_id),
        HarvestStatus.NOT_STARTED,
    )
    return GateCondition(
        condition=f"The {checkpoint_id.replace('_', ' ')} checkpoint is captured",
        met=status is HarvestStatus.CAPTURED,
        detail=f"checkpoint status is {status.value}",
    )


@pure
def gate_conditions(matter: MatterDocument) -> tuple[GateCondition, ...]:
    phase = matter.workflow_phase
    confirmed = [s for s in matter.seeds if s.status in _CONFIRMED_SEED_STATUSES]
    if phase is WorkflowPhase.TRIAGE_QUIZ:
        o = matter.orientation
        answered = [
            o.idea_state is not None,
            o.disclosure_state is not None,
            bool(o.objectives),
            o.materials_state is not None,
            o.collaboration_style is not None,
        ]
        return (
            GateCondition(
                condition="All five orientation answers are recorded",
                met=all(answered),
                detail=f"{sum(answered)} of 5 answered",
            ),
        )
    if phase is WorkflowPhase.SOURCE_LOCK:
        inventor_sources = [
            r for r in matter.references if r.source_type is SourceType.INVENTOR_MATERIAL
        ]
        return (
            _checkpoint_captured(matter, "source_lock"),
            GateCondition(
                condition="At least one inventor-material reference is in the library",
                met=bool(inventor_sources),
                detail=f"{len(inventor_sources)} inventor-material references",
            ),
        )
    if phase is WorkflowPhase.OBJECTIVE_LOCK:
        return (
            _checkpoint_captured(matter, "objective_lock"),
            GateCondition(
                condition="The inventor's goal is recorded",
                met=bool(matter.goal.strip()),
                detail=matter.goal.strip() or "goal is empty",
            ),
        )
    if phase is WorkflowPhase.CORE_MECHANISM:
        return (
            _checkpoint_captured(matter, "core_mechanism"),
            GateCondition(
                condition="The brief describes the mechanism",
                met=bool(matter.brief.mechanism.strip()),
                detail="mechanism written" if matter.brief.mechanism.strip() else "brief.mechanism is empty",
            ),
        )
    if phase is WorkflowPhase.SEED_EXPANSION:
        waived = any(d.kind is DecisionKind.SINGLE_SEED_WAIVER for d in matter.decisions)
        return (
            GateCondition(
                condition="Two or more inventor-confirmed seeds, or one seed plus a single-seed waiver",
                met=len(confirmed) >= 2 or (len(confirmed) == 1 and waived),
                detail=f"{len(confirmed)} confirmed of {len(matter.seeds)} seeds"
                + (", waiver recorded" if waived else ""),
            ),
        )
    if phase is WorkflowPhase.SEED_ASSAY:
        unassayed = [s.label for s in confirmed if not s.closest_art_note.strip()]
        return (
            GateCondition(
                condition="Every confirmed seed has a closest-art note",
                met=bool(confirmed) and not unassayed,
                detail="all assayed" if confirmed and not unassayed else f"missing for: {', '.join(unassayed) or 'no confirmed seeds'}",
            ),
        )
    if phase is WorkflowPhase.TERRAIN_SELECTION:
        unrouted = [s.label for s in confirmed if s.route is None]
        terrain_decided = any(d.kind is DecisionKind.COMMERCIAL_TERRAIN for d in matter.decisions)
        return (
            GateCondition(
                condition="Every confirmed seed has a route",
                met=bool(confirmed) and not unrouted,
                detail="all routed" if confirmed and not unrouted else f"unrouted: {', '.join(unrouted) or 'no confirmed seeds'}",
            ),
            GateCondition(
                condition="A commercial-terrain decision is in the ledger",
                met=terrain_decided,
                detail="recorded" if terrain_decided else "no COMMERCIAL_TERRAIN decision",
            ),
        )
    if phase is WorkflowPhase.PROVISIONAL_POSTURE:
        p = matter.posture
        return (
            GateCondition(
                condition="A posture is chosen and approved by the inventor",
                met=p.posture is not None and p.approved_by_inventor,
                detail=(p.posture.value if p.posture else "no posture")
                + (", approved" if p.approved_by_inventor else ", not approved"),
            ),
        )
    if phase is WorkflowPhase.DISCLOSURE_BUILD:
        return (_checkpoint_captured(matter, "disclosure_build"),)
    if phase is WorkflowPhase.ATTACK_REPAIR:
        return (_checkpoint_captured(matter, "attack_repair"),)
    return ()


@pure
def evaluate_gate(matter: MatterDocument) -> GateReport:
    conditions = gate_conditions(matter)
    unmet = [c for c in conditions if not c.met]
    nxt = phase_after(matter.workflow_phase)
    if nxt is None:
        focus = "The record is at handoff; offer the export or a separately authorized next workflow."
    elif unmet:
        focus = f"Ask about this next, in plain words: {unmet[0].condition.lower()} ({unmet[0].detail})."
    else:
        focus = f"The record supports moving to {nxt.value}; advance when the inventor is ready."
    return GateReport(
        phase=matter.workflow_phase,
        next_phase=nxt,
        can_advance=nxt is not None and not unmet,
        gaps=conditions,
        focus=focus,
    )
