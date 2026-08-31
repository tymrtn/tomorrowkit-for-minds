import json
from pathlib import Path

import pytest

from tomorrowkit import agent_tools
from tomorrowkit.data_types import MatterIntake, MatterStage
from tomorrowkit.factories import create_matter_from_intake
from tomorrowkit.storage import FileMatterStore


def test_agent_patch_updates_brief_and_appends_reference(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("TOMORROWKIT_DATA_DIR", str(tmp_path))
    store = FileMatterStore(matters_directory=tmp_path / "matters")
    matter = create_matter_from_intake(
        MatterIntake(title="Test invention", stage=MatterStage.EARLY_IDEA)
    )
    store.save_matter(matter)
    patch_path = tmp_path / "patch.json"
    patch_path.write_text(
        json.dumps(
            {
                "expected_updated_at": matter.updated_at.isoformat(),
                "set": {"brief.problem": "A verified inventor statement."},
                "checkpoints": [
                    {"checkpoint_id": "intake", "status": "IN_PROGRESS"}
                ],
                "append_references": [
                    {
                        "title": "Example patent",
                        "source_type": "PATENT_PUBLICATION",
                        "relationship": "NEEDS_VERIFICATION",
                    }
                ],
            }
        )
    )

    agent_tools._apply_patch(str(matter.matter_id), patch_path)

    updated = store.load_matter(matter.matter_id)
    assert updated.brief.problem == "A verified inventor statement."
    assert updated.harvest[0].status.value == "IN_PROGRESS"
    assert updated.references[0].title == "Example patent"
    assert updated.references[0].verification_state.value == "LEAD"
    assert json.loads(capsys.readouterr().out)["matter_id"] == matter.matter_id


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
