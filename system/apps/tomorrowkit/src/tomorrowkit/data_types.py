from datetime import datetime
from enum import auto
from typing import Any, Final

from imbue.imbue_common.enums import UpperCaseStrEnum
from imbue.imbue_common.frozen_model import FrozenModel
from imbue.imbue_common.ids import RandomId
from imbue.imbue_common.pure import pure
from pydantic import Field, model_validator


class MatterId(RandomId):
    """Unique identifier for an invention matter."""

    PREFIX = "mat"


class ReferenceId(RandomId):
    """Unique identifier for a reference library entry."""

    PREFIX = "ref"


class DecisionId(RandomId):
    """Unique identifier for a decision ledger entry."""

    PREFIX = "dec"


class MapNodeId(RandomId):
    """Unique identifier for an invention map node."""

    PREFIX = "node"


class MapEdgeId(RandomId):
    """Unique identifier for an invention map edge."""

    PREFIX = "edge"


class MatterStage(UpperCaseStrEnum):
    """Where the invention currently sits in its journey, in the user's terms."""

    EARLY_IDEA = auto()
    DRAFT_READY = auto()
    FILED_PROVISIONAL = auto()
    EXISTING_APPLICATION = auto()


class IdeaState(UpperCaseStrEnum):
    """How far the inventor's idea has progressed before this workspace."""

    IN_MY_HEAD = auto()
    WRITTEN_OR_BUILT = auto()
    DRAFT_PROVISIONAL = auto()
    FILED = auto()


class DisclosureState(UpperCaseStrEnum):
    """How broadly the invention may already have been disclosed."""

    PRIVATE = auto()
    CONFIDENTIAL_ONLY = auto()
    MAYBE_PUBLIC = auto()
    PUBLIC_OR_COMMERCIAL = auto()


class OrientationObjective(UpperCaseStrEnum):
    """A reason the inventor wants to develop this invention record."""

    PROTECT_PRODUCT = auto()
    LICENSE_OR_PARTNER = auto()
    ENCIRCLE_OR_BLOCK = auto()
    FUNDRAISE_OR_ACQUIRE = auto()
    BANK_OPTIONALITY = auto()
    PUBLISH_OR_PUBLIC_BENEFIT = auto()
    UNDERSTAND_OPTIONS = auto()


class MaterialsState(UpperCaseStrEnum):
    """The strongest source material the inventor already has."""

    CONVERSATION_ONLY = auto()
    NOTES_OR_SKETCHES = auto()
    TECHNICAL_MATERIALS = auto()
    DRAFT_OR_FILING = auto()


class CollaborationStyle(UpperCaseStrEnum):
    """How the inventor wants the Tomorrowkit agent to work with them."""

    INTERVIEW_ME = auto()
    GUIDED_CHOICES = auto()
    BACKGROUND_WITH_GATES = auto()
    HIGH_AUTONOMY = auto()


class WorkflowPhase(UpperCaseStrEnum):
    """The current phase of the conversational Tomorrowkit workflow."""

    WELCOME = auto()
    TRIAGE_QUIZ = auto()
    SOURCE_LOCK = auto()
    OBJECTIVE_LOCK = auto()
    CORE_MECHANISM = auto()
    SEED_EXPANSION = auto()
    SEED_ASSAY = auto()
    TERRAIN_SELECTION = auto()
    PROVISIONAL_POSTURE = auto()
    DISCLOSURE_BUILD = auto()
    ATTACK_REPAIR = auto()
    READY_HANDOFF = auto()


class SourceType(UpperCaseStrEnum):
    """The kind of source a reference library entry points at."""

    PATENT_PUBLICATION = auto()
    PAPER = auto()
    PRODUCT = auto()
    WEB_PAGE = auto()
    STANDARD = auto()
    INVENTOR_MATERIAL = auto()
    RESEARCH_LEAD = auto()


class ReferenceRelationship(UpperCaseStrEnum):
    """How a reference relates to the matter."""

    SUPPORTS = auto()
    CONTRADICTS = auto()
    DESIGN_AROUND = auto()
    SEARCH_LEAD = auto()
    NEEDS_VERIFICATION = auto()


class VerificationState(UpperCaseStrEnum):
    """How thoroughly a reference has been checked by a human."""

    LEAD = auto()
    REVIEWED = auto()
    VERIFIED = auto()


class DecisionKind(UpperCaseStrEnum):
    """The category of a decision recorded in the ledger."""

    COMMERCIAL_TERRAIN = auto()
    EMBODIMENT_CHOICE = auto()
    DEFERRAL = auto()
    SUGGESTION_DISPOSITION = auto()
    OTHER = auto()


class HarvestStatus(UpperCaseStrEnum):
    """Progress state of one harvesting checkpoint."""

    NOT_STARTED = auto()
    IN_PROGRESS = auto()
    CAPTURED = auto()


class MapNodeKind(UpperCaseStrEnum):
    """What an invention map node represents."""

    COMPONENT = auto()
    ACTOR = auto()
    INPUT = auto()
    OUTPUT = auto()
    STEP = auto()
    ALTERNATIVE = auto()
    QUESTION = auto()
    ASSUMPTION = auto()
    EVIDENCE = auto()


class LensLevel(UpperCaseStrEnum):
    """Self-assessed confidence level for one scorecard lens."""

    NOT_ASSESSED = auto()
    WEAK = auto()
    DEVELOPING = auto()
    SOLID = auto()


class ImportantDate(FrozenModel):
    """A date the inventor knows matters (e.g. a public demo or a filing)."""

    label: str = Field(description="What this date is, in the inventor's words")
    date_text: str = Field(
        description="The date as the inventor knows it (may be approximate)"
    )
    note: str = Field(default="", description="Optional extra context for this date")


class OrientationProfile(FrozenModel):
    """The inventor's answers to the short, choice-based orientation quiz."""

    idea_state: IdeaState | None = Field(
        default=None, description="How far the idea has progressed"
    )
    disclosure_state: DisclosureState | None = Field(
        default=None, description="Whether the invention may already be public"
    )
    objectives: tuple[OrientationObjective, ...] = Field(
        default=(),
        max_length=3,
        description="Up to three outcomes the inventor wants from Tomorrowkit",
    )
    materials_state: MaterialsState | None = Field(
        default=None, description="What source material already exists"
    )
    collaboration_style: CollaborationStyle | None = Field(
        default=None, description="How the inventor wants the agent to collaborate"
    )


class InventionBrief(FrozenModel):
    """The evolving human-reviewable account of the invention, kept in the inventor's own language."""

    problem: str = Field(
        default="", description="The problem being solved and who has it"
    )
    mechanism: str = Field(
        default="", description="How the invention works, in the inventor's words"
    )
    intended_result: str = Field(
        default="", description="What the invention achieves when it works"
    )
    alternatives: str = Field(
        default="", description="Other ways to build it and variations considered"
    )
    open_questions: str = Field(
        default="", description="What is still unknown or undecided"
    )


class HarvestCheckpoint(FrozenModel):
    """One checkpoint shared between the Minds agent and visual matter record."""

    checkpoint_id: str = Field(description="Stable slug identifying this checkpoint")
    name: str = Field(description="Short human-readable name of the checkpoint")
    purpose: str = Field(description="What this checkpoint is for, in plain language")
    agent_prompt: str = Field(
        description="Internal workflow guidance available to the configured Minds agent"
    )
    status: HarvestStatus = Field(
        default=HarvestStatus.NOT_STARTED, description="Progress on this checkpoint"
    )
    notes: str = Field(
        default="",
        description="What came out of this checkpoint, in the inventor's words",
    )


_WORKFLOW_CHECKPOINTS: Final[tuple[tuple[WorkflowPhase, str, str, str], ...]] = (
    (
        WorkflowPhase.SOURCE_LOCK,
        "Source lock",
        "Identify what existed before this conversation and preserve its provenance.",
        "Inventory existing notes, sketches, prototypes, drafts, filings, dates, and contributors. "
        "Keep inventor material separate from later model suggestions.",
    ),
    (
        WorkflowPhase.OBJECTIVE_LOCK,
        "Objective lock",
        "Turn the inventor's selected outcomes into a clear working objective.",
        "Confirm what success means, what terrain matters, and which outcomes are deliberately secondary.",
    ),
    (
        WorkflowPhase.CORE_MECHANISM,
        "Core mechanism",
        "Capture the causal mechanism that makes the invention work.",
        "Ask for the actors, inputs, steps, transformations, outputs, and failure conditions one question at a time.",
    ),
    (
        WorkflowPhase.SEED_EXPANSION,
        "Seed expansion",
        "Grow the core mechanism into alternatives, variants, and adjacent implementations.",
        "Explore substitutions, reordered steps, different boundaries, fallback implementations, and design-arounds.",
    ),
    (
        WorkflowPhase.SEED_ASSAY,
        "Seed assay",
        "Test each invention seed for support, distinctiveness, and practical importance.",
        "Separate inventor-supported facts from hypotheses and identify what needs evidence or further explanation.",
    ),
    (
        WorkflowPhase.TERRAIN_SELECTION,
        "Terrain selection",
        "Choose the technical and commercial terrain worth carrying forward.",
        "Present the strongest supported terrain and record the inventor's selections, deferrals, and rationale.",
    ),
    (
        WorkflowPhase.PROVISIONAL_POSTURE,
        "Provisional posture",
        "Set a disclosure posture appropriate to the matter's timing, evidence, and goals.",
        "Review disclosure dates, source coverage, ownership questions, and the limits of the current record without giving a legal verdict.",
    ),
    (
        WorkflowPhase.DISCLOSURE_BUILD,
        "Disclosure build",
        "Develop a technically enabling account of the selected terrain.",
        "Deepen mechanisms, embodiments, ranges, materials, sequences, edge cases, alternatives, and implementation detail.",
    ),
    (
        WorkflowPhase.ATTACK_REPAIR,
        "Attack and repair",
        "Pressure-test the record and repair the highest-priority gaps.",
        "Challenge missing support, weak assumptions, unclear terminology, omitted variants, contradictory evidence, and unresolved inventorship facts.",
    ),
)


@pure
def build_default_harvest_checkpoints() -> tuple[HarvestCheckpoint, ...]:
    return tuple(
        HarvestCheckpoint(
            checkpoint_id=phase.value.lower(),
            name=name,
            purpose=purpose,
            agent_prompt=agent_prompt,
        )
        for phase, name, purpose, agent_prompt in _WORKFLOW_CHECKPOINTS
    )


class MapNode(FrozenModel):
    """A node on the invention map canvas."""

    node_id: MapNodeId = Field(description="Unique identifier")
    kind: MapNodeKind = Field(description="What this node represents")
    label: str = Field(description="Short display label")
    note: str = Field(default="", description="Longer free-form note")
    x: float = Field(description="Canvas x position")
    y: float = Field(description="Canvas y position")
    linked_reference_id: str = Field(
        default="", description="Optional reference library entry this node points at"
    )


class MapEdge(FrozenModel):
    """A directed connection between two invention map nodes."""

    edge_id: MapEdgeId = Field(description="Unique identifier")
    source_node_id: MapNodeId = Field(description="Node the edge starts from")
    target_node_id: MapNodeId = Field(description="Node the edge points to")
    label: str = Field(
        default="", description="Optional label describing the relationship"
    )


class ReferenceEntry(FrozenModel):
    """One entry in the matter's reference library."""

    reference_id: ReferenceId = Field(description="Unique identifier")
    title: str = Field(description="Human-readable name of the source")
    citation: str = Field(
        default="", description="Citation text or a stable link to the source"
    )
    source_type: SourceType = Field(description="What kind of source this is")
    relevance_note: str = Field(
        default="", description="Short plain-language note on why this matters"
    )
    tags: tuple[str, ...] = Field(
        default=(), description="Free-form tags (concept, embodiment, market, ...)"
    )
    relationship: ReferenceRelationship = Field(
        description="How this source relates to the matter"
    )
    source_date_text: str = Field(
        default="", description="Date metadata for the source, when known"
    )
    provenance_note: str = Field(
        default="", description="Where this entry came from (who found it, how)"
    )
    verification_state: VerificationState = Field(
        default=VerificationState.LEAD,
        description="How thoroughly a human has checked this entry",
    )
    added_at: datetime = Field(description="When this entry was added to the library")


class DecisionEntry(FrozenModel):
    """One human decision recorded in the decision ledger."""

    decision_id: DecisionId = Field(description="Unique identifier")
    kind: DecisionKind = Field(description="The category of decision")
    title: str = Field(description="The decision itself, stated plainly")
    rationale: str = Field(default="", description="Why the inventor decided this")
    recorded_at: datetime = Field(description="When the decision was recorded")


class LensAssessment(FrozenModel):
    """A structured self-review for one scorecard lens."""

    level: LensLevel = Field(
        default=LensLevel.NOT_ASSESSED, description="Self-assessed confidence level"
    )
    coverage_notes: str = Field(
        default="", description="What the record currently covers for this lens"
    )
    evidence_notes: str = Field(
        default="", description="What evidence backs the current assessment"
    )
    missing_prerequisites: str = Field(
        default="", description="What is missing before this lens can improve"
    )
    reasoning: str = Field(
        default="", description="The reasoning behind the current level"
    )


class Scorecard(FrozenModel):
    """The two provisional-stage Tomorrowkit lenses. Never merged into a single score."""

    invention_value: LensAssessment = Field(
        default_factory=LensAssessment,
        description="IVS: whether the inventor-approved terrain appears worth pursuing",
    )
    priority_asset: LensAssessment = Field(
        default_factory=LensAssessment,
        description="PAS: whether the provisional record captures that terrain",
    )


class MatterDocument(FrozenModel):
    """The complete record of one invention matter. One invention, one workspace."""

    matter_id: MatterId = Field(description="Unique identifier")
    created_at: datetime = Field(description="When the matter was created")
    updated_at: datetime = Field(description="When the matter was last saved")
    title: str = Field(description="Working title of the invention")
    problem_summary: str = Field(
        default="", description="Short description of the problem and intended approach"
    )
    stage: MatterStage = Field(
        description="Where the invention currently sits in its journey"
    )
    goal: str = Field(default="", description="The inventor's immediate goal")
    theme: str = Field(default="", description="Optional visual theme or industry cue")
    known_dates: tuple[ImportantDate, ...] = Field(
        default=(), description="Important dates the inventor entered"
    )
    orientation: OrientationProfile = Field(
        default_factory=OrientationProfile,
        description="Choice-based orientation answers that shape the workflow",
    )
    workflow_phase: WorkflowPhase = Field(
        default=WorkflowPhase.WELCOME,
        description="Current phase of the conversational workflow",
    )
    what_is_known: str = Field(
        default="", description="Plain-language summary of what is established"
    )
    what_is_uncertain: str = Field(
        default="", description="Plain-language summary of what remains unknown"
    )
    next_action: str = Field(
        default="", description="The next recommended action, in plain language"
    )
    brief: InventionBrief = Field(
        default_factory=InventionBrief, description="The evolving invention brief"
    )
    harvest: tuple[HarvestCheckpoint, ...] = Field(
        default=(), description="Guided harvesting checkpoints"
    )
    map_nodes: tuple[MapNode, ...] = Field(
        default=(), description="Invention map nodes"
    )
    map_edges: tuple[MapEdge, ...] = Field(
        default=(), description="Invention map edges"
    )
    references: tuple[ReferenceEntry, ...] = Field(
        default=(), description="Reference library entries"
    )
    decisions: tuple[DecisionEntry, ...] = Field(
        default=(), description="Decision ledger entries"
    )
    scorecard: Scorecard = Field(
        default_factory=Scorecard, description="The two provisional-stage lenses"
    )

    @model_validator(mode="before")
    @classmethod
    def _normalize_legacy_harvest(cls, data: Any) -> Any:
        """Upgrade the original four checkpoints without discarding their work."""
        if not isinstance(data, dict):
            return data

        raw_harvest = data.get("harvest")
        if not isinstance(raw_harvest, (list, tuple)):
            return data

        legacy_targets = {
            "intake": WorkflowPhase.CORE_MECHANISM.value.lower(),
            "prospecting": WorkflowPhase.SEED_ASSAY.value.lower(),
            "drafting": WorkflowPhase.DISCLOSURE_BUILD.value.lower(),
            "adversarial": WorkflowPhase.ATTACK_REPAIR.value.lower(),
        }
        raw_checkpoints = [
            checkpoint for checkpoint in raw_harvest if isinstance(checkpoint, dict)
        ]
        if not any(
            checkpoint.get("checkpoint_id") in legacy_targets
            for checkpoint in raw_checkpoints
        ):
            return data

        normalized_harvest = [
            checkpoint.model_dump(mode="json")
            for checkpoint in build_default_harvest_checkpoints()
        ]
        normalized_by_id = {
            checkpoint["checkpoint_id"]: checkpoint for checkpoint in normalized_harvest
        }
        current_ids_present = {
            checkpoint.get("checkpoint_id")
            for checkpoint in raw_checkpoints
            if checkpoint.get("checkpoint_id") in normalized_by_id
        }

        for checkpoint in raw_checkpoints:
            raw_id = checkpoint.get("checkpoint_id")
            if not isinstance(raw_id, str):
                continue
            target_id = legacy_targets.get(raw_id, raw_id)
            target = normalized_by_id.get(target_id)
            if target is None:
                continue
            # Prefer an already-normalized checkpoint if a partially migrated record
            # contains both forms. Otherwise carry the legacy progress and notes over.
            if raw_id in legacy_targets and target_id in current_ids_present:
                continue
            if "status" in checkpoint:
                target["status"] = checkpoint["status"]
            if "notes" in checkpoint:
                target["notes"] = checkpoint["notes"]

        normalized = dict(data)
        normalized["harvest"] = normalized_harvest
        if "workflow_phase" not in normalized:
            normalized["workflow_phase"] = WorkflowPhase.SOURCE_LOCK.value
        return normalized


class MatterIntake(FrozenModel):
    """The minimal information collected when creating a new matter workspace."""

    title: str = Field(min_length=1, description="Working title of the invention")
    problem_summary: str = Field(
        default="", description="Short description of the problem and intended approach"
    )
    stage: MatterStage = Field(description="Where the invention currently sits")
    goal: str = Field(default="", description="The inventor's immediate goal")
    theme: str = Field(default="", description="Optional visual theme or industry cue")
    known_dates: tuple[ImportantDate, ...] = Field(
        default=(), description="Important dates the inventor knows"
    )
