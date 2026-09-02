import json
from datetime import datetime, timezone

from tomorrowkit.data_types import (
    DecisionKind,
    MatterDocument,
    MatterIntake,
    MatterStage,
    PosturePlan,
    ProvisionalPosture,
    Seed,
    SeedId,
    SeedOrigin,
    SeedRoute,
    SeedStatus,
)
from tomorrowkit.factories import create_matter_from_intake


def test_new_matter_starts_with_no_seeds_no_posture_and_no_chat_agent() -> None:
    matter = create_matter_from_intake(
        MatterIntake(title="Test invention", stage=MatterStage.EARLY_IDEA)
    )

    assert matter.seeds == ()
    assert matter.posture == PosturePlan()
    assert matter.posture.posture is None
    assert matter.posture.approved_by_inventor is False
    assert matter.chat_agent_id == ""


def test_seed_and_posture_round_trip_through_json() -> None:
    matter = create_matter_from_intake(
        MatterIntake(title="Test invention", stage=MatterStage.EARLY_IDEA)
    )
    now = datetime(2026, 9, 2, 12, 0, tzinfo=timezone.utc)
    seed = Seed(
        seed_id=SeedId.generate(),
        label="Pressure-energised lip",
        mechanism="Line pressure pushes the lip outward, so grip rises with pressure.",
        origin=SeedOrigin.INVENTOR,
        status=SeedStatus.ACCEPTED,
        route=SeedRoute.STANDALONE,
        closest_art_note="US 6,123,456 uses a threaded collar, not a pressure-responsive one.",
        created_at=now,
        updated_at=now,
    )
    posture = PosturePlan(
        posture=ProvisionalPosture.LEAN_CORE_STUB,
        rationale="Core is settled; keep the bleed groove out of the first filing.",
        approved_by_inventor=True,
    )
    payload = json.loads(matter.model_dump_json())
    payload["seeds"] = [json.loads(seed.model_dump_json())]
    payload["posture"] = json.loads(posture.model_dump_json())

    loaded = MatterDocument.model_validate(payload)

    assert loaded.seeds == (seed,)
    assert loaded.posture == posture
    assert DecisionKind.SINGLE_SEED_WAIVER.value == "SINGLE_SEED_WAIVER"
    assert DecisionKind.WORKFLOW_RETURN.value == "WORKFLOW_RETURN"


def test_matter_saved_before_seeds_existed_still_loads() -> None:
    matter = create_matter_from_intake(
        MatterIntake(title="Older matter", stage=MatterStage.EARLY_IDEA)
    )
    payload = json.loads(matter.model_dump_json())
    for absent in ("seeds", "posture", "chat_agent_id"):
        payload.pop(absent, None)

    loaded = MatterDocument.model_validate(payload)

    assert loaded.seeds == ()
    assert loaded.posture.posture is None
    assert loaded.chat_agent_id == ""
