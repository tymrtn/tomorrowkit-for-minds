from datetime import datetime, timezone
from typing import Final

from imbue.imbue_common.pure import pure

from tomorrowkit.data_types import (
    DisclosureState,
    IdeaState,
    MaterialsState,
    MatterDocument,
    MatterId,
    MatterIntake,
    MatterStage,
    OrientationObjective,
    OrientationProfile,
    WorkflowPhase,
    build_default_harvest_checkpoints,
)

_OBJECTIVE_GOALS: Final[dict[OrientationObjective, str]] = {
    OrientationObjective.PROTECT_PRODUCT: "Protect a product or service",
    OrientationObjective.LICENSE_OR_PARTNER: "Prepare for licensing or partnership",
    OrientationObjective.ENCIRCLE_OR_BLOCK: "Build defensive patent terrain",
    OrientationObjective.FUNDRAISE_OR_ACQUIRE: "Support fundraising or acquisition",
    OrientationObjective.BANK_OPTIONALITY: "Preserve future options",
    OrientationObjective.PUBLISH_OR_PUBLIC_BENEFIT: "Prepare for publication or public benefit",
    OrientationObjective.UNDERSTAND_OPTIONS: "Understand the available patent options",
}


@pure
def derive_stage_from_orientation(orientation: OrientationProfile) -> MatterStage:
    """Map the quiz's state choices onto the legacy matter-stage vocabulary."""
    if orientation.idea_state is IdeaState.FILED:
        return MatterStage.FILED_PROVISIONAL
    if (
        orientation.idea_state
        in {
            IdeaState.WRITTEN_OR_BUILT,
            IdeaState.DRAFT_PROVISIONAL,
        }
        or orientation.materials_state is MaterialsState.DRAFT_OR_FILING
    ):
        return MatterStage.DRAFT_READY
    return MatterStage.EARLY_IDEA


@pure
def derive_goal_from_orientation(orientation: OrientationProfile) -> str:
    """Render the selected objectives as a concise matter goal."""
    if not orientation.objectives:
        return "Understand the invention and choose the right next step"
    return "; ".join(
        _OBJECTIVE_GOALS[objective] for objective in orientation.objectives
    )


@pure
def derive_next_action_from_orientation(orientation: OrientationProfile) -> str:
    """Choose the source-lock instruction most relevant to the quiz answers."""
    if (
        orientation.idea_state is IdeaState.FILED
        or orientation.materials_state is MaterialsState.DRAFT_OR_FILING
    ):
        return "Gather the draft or filing and lock the source record before developing it further."
    if orientation.disclosure_state in {
        DisclosureState.MAYBE_PUBLIC,
        DisclosureState.PUBLIC_OR_COMMERCIAL,
    }:
        return "Record the disclosure timeline and lock the source materials that existed before it."
    if orientation.materials_state in {
        MaterialsState.NOTES_OR_SKETCHES,
        MaterialsState.TECHNICAL_MATERIALS,
    }:
        return "Gather the existing invention materials and lock them as the starting source record."
    return "Capture what existed before this conversation and lock it as the starting source record."


def create_matter_from_intake(intake: MatterIntake) -> MatterDocument:
    now = datetime.now(timezone.utc)
    return MatterDocument(
        matter_id=MatterId.generate(),
        created_at=now,
        updated_at=now,
        title=intake.title,
        problem_summary=intake.problem_summary,
        stage=intake.stage,
        goal=intake.goal,
        theme=intake.theme,
        known_dates=intake.known_dates,
        harvest=build_default_harvest_checkpoints(),
    )


def create_matter_from_orientation(orientation: OrientationProfile) -> MatterDocument:
    """Create the conversational workspace produced by the orientation quiz."""
    now = datetime.now(timezone.utc)
    return MatterDocument(
        matter_id=MatterId.generate(),
        created_at=now,
        updated_at=now,
        title="Untitled invention",
        stage=derive_stage_from_orientation(orientation),
        goal=derive_goal_from_orientation(orientation),
        orientation=orientation,
        workflow_phase=WorkflowPhase.SOURCE_LOCK,
        next_action=derive_next_action_from_orientation(orientation),
        harvest=build_default_harvest_checkpoints(),
    )
