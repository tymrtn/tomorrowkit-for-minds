import pytest
from pydantic import ValidationError

from tomorrowkit.data_types import OrientationProfile
from tomorrowkit.factories import create_matter_from_orientation


def test_orientation_derives_stage_goal_and_first_action() -> None:
    matter = create_matter_from_orientation(
        OrientationProfile.model_validate(
            {
                "idea_state": "WRITTEN_OR_BUILT",
                "disclosure_state": "CONFIDENTIAL_ONLY",
                "objectives": ["PROTECT_PRODUCT", "LICENSE_OR_PARTNER"],
                "materials_state": "NOTES_OR_SKETCHES",
                "collaboration_style": "GUIDED_CHOICES",
            }
        )
    )

    assert matter.title == "Untitled invention"
    assert matter.stage.value == "DRAFT_READY"
    assert matter.goal == (
        "Protect a product or service; Prepare for licensing or partnership"
    )
    assert matter.next_action == (
        "Gather the existing invention materials and lock them as the starting source record."
    )
    assert matter.workflow_phase.value == "SOURCE_LOCK"
    assert [checkpoint.checkpoint_id for checkpoint in matter.harvest] == [
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


def test_filed_provisional_orientation_derives_filed_stage() -> None:
    matter = create_matter_from_orientation(
        OrientationProfile.model_validate(
            {
                "idea_state": "FILED",
                "disclosure_state": "PUBLIC_OR_COMMERCIAL",
                "objectives": [
                    "BANK_OPTIONALITY"
                ],
                "materials_state": "DRAFT_OR_FILING",
                "collaboration_style": "BACKGROUND_WITH_GATES"
            }
        )
    )

    assert matter.stage.value == "FILED_PROVISIONAL"
    assert matter.goal == "Preserve future options"


def test_orientation_rejects_more_than_three_objectives() -> None:
    with pytest.raises(ValidationError):
        OrientationProfile.model_validate(
            {
                "idea_state": "IN_MY_HEAD",
                "disclosure_state": "PRIVATE",
                "objectives": [
                    "PROTECT_PRODUCT",
                    "LICENSE_OR_PARTNER",
                    "PRESERVE_OPTIONS",
                    "BLOCK_COMPETITORS",
                ],
                "materials_state": "CONVERSATION_ONLY",
                "collaboration_style": "INTERVIEW_ME",
            }
        )
