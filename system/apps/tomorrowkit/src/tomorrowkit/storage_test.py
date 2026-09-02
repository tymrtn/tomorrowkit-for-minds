import fcntl
import json
import os
import select
from datetime import timedelta
from pathlib import Path

import pytest

from tomorrowkit import storage as storage_module
from tomorrowkit.data_types import MatterId, WorkflowPhase
from tomorrowkit.errors import MatterNotFoundError, StaleMatterError
from tomorrowkit.storage import FileMatterStore
from tomorrowkit.testing import build_matter_with_id, build_sample_matter


def test_save_and_load_round_trips_the_full_document(tmp_path: Path) -> None:
    store = FileMatterStore(matters_directory=tmp_path / "matters")
    matter = build_sample_matter()

    store.save_matter(matter)
    loaded = store.load_matter(matter.matter_id)

    assert loaded == matter


def test_load_missing_matter_raises_not_found(tmp_path: Path) -> None:
    store = FileMatterStore(matters_directory=tmp_path / "matters")

    with pytest.raises(MatterNotFoundError):
        store.load_matter(MatterId.generate())


def test_list_matters_returns_newest_first(tmp_path: Path) -> None:
    store = FileMatterStore(matters_directory=tmp_path / "matters")
    older = build_sample_matter()
    newer = build_sample_matter()

    store.save_matter(older)
    store.save_matter(newer)
    listed = store.list_matters()

    assert {m.matter_id for m in listed} == {older.matter_id, newer.matter_id}
    assert listed == sorted(listed, key=lambda m: m.created_at, reverse=True)


def test_list_matters_skips_corrupt_files(tmp_path: Path) -> None:
    matters_directory = tmp_path / "matters"
    store = FileMatterStore(matters_directory=matters_directory)
    matter = build_sample_matter()
    store.save_matter(matter)
    corrupt_id = MatterId.generate()
    (matters_directory / f"{corrupt_id}.json").write_text('{"not": "a matter"}')

    listed = store.list_matters()

    assert [m.matter_id for m in listed] == [matter.matter_id]


def test_delete_matter_removes_it(tmp_path: Path) -> None:
    store = FileMatterStore(matters_directory=tmp_path / "matters")
    matter = build_sample_matter()
    store.save_matter(matter)

    store.delete_matter(matter.matter_id)

    assert store.list_matters() == []
    with pytest.raises(MatterNotFoundError):
        store.delete_matter(matter.matter_id)


def test_matters_are_stored_one_json_file_per_matter(tmp_path: Path) -> None:
    matters_directory = tmp_path / "matters"
    store = FileMatterStore(matters_directory=matters_directory)
    matter_id = MatterId.generate()
    store.save_matter(build_matter_with_id(matter_id))

    assert (matters_directory / f"{matter_id}.json").exists()


def test_each_atomic_save_uses_a_unique_temporary_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    matters_directory = tmp_path / "matters"
    store = FileMatterStore(matters_directory=matters_directory)
    matter = build_sample_matter()
    temporary_paths: list[Path] = []
    real_replace = os.replace

    def record_replace(source: os.PathLike[str], destination: os.PathLike[str]) -> None:
        temporary_paths.append(Path(source))
        real_replace(source, destination)

    monkeypatch.setattr(storage_module.os, "replace", record_replace)

    store.save_matter(matter)
    store.save_matter(matter)

    assert len(temporary_paths) == 2
    assert temporary_paths[0] != temporary_paths[1]
    assert all(path.parent == matters_directory for path in temporary_paths)
    assert not list(matters_directory.glob("*.tmp"))


def test_revision_check_and_write_are_locked_across_processes(tmp_path: Path) -> None:
    matters_directory = tmp_path / "matters"
    store = FileMatterStore(matters_directory=matters_directory)
    original = build_sample_matter()
    store.save_matter(original)
    child_candidate = original.model_copy(
        update={"updated_at": original.updated_at + timedelta(seconds=1)}
    )
    winning_update = original.model_copy(
        update={"updated_at": original.updated_at + timedelta(seconds=2)}
    )
    ready_read, ready_write = os.pipe()
    result_read, result_write = os.pipe()
    lock_path = store._matter_lock_path(original.matter_id)

    with lock_path.open("a+b") as parent_lock:
        fcntl.flock(parent_lock.fileno(), fcntl.LOCK_EX)
        child_pid = os.fork()
        if child_pid == 0:
            os.close(ready_read)
            os.close(result_read)
            parent_lock.close()
            os.write(ready_write, b"1")
            os.close(ready_write)
            child_store = FileMatterStore(matters_directory=matters_directory)
            try:
                child_store.save_matter_if_current(child_candidate, original.updated_at)
            except StaleMatterError:
                result = b"S"
            except BaseException:
                result = b"E"
            else:
                result = b"W"
            os.write(result_write, result)
            os.close(result_write)
            os._exit(0)

        os.close(ready_write)
        os.close(result_write)
        assert os.read(ready_read, 1) == b"1"
        os.close(ready_read)
        readable, _, _ = select.select([result_read], [], [], 0.2)
        completed_before_unlock = bool(readable)
        premature_result = os.read(result_read, 1) if readable else b""
        store._write_matter_unlocked(winning_update)
        fcntl.flock(parent_lock.fileno(), fcntl.LOCK_UN)

    child_result = premature_result or os.read(result_read, 1)
    os.close(result_read)
    waited_pid, wait_status = os.waitpid(child_pid, 0)

    assert not completed_before_unlock
    assert child_result == b"S"
    assert waited_pid == child_pid
    assert os.WIFEXITED(wait_status)
    assert os.WEXITSTATUS(wait_status) == 0
    assert store.load_matter(original.matter_id) == winning_update


def test_load_migrates_legacy_harvest_without_losing_progress(
    tmp_path: Path,
) -> None:
    matters_directory = tmp_path / "matters"
    matters_directory.mkdir()
    matter = build_sample_matter()
    legacy_payload = matter.model_dump(mode="json")
    legacy_payload.pop("workflow_phase")
    legacy_payload.pop("orientation")
    legacy_payload["harvest"] = [
        {
            "checkpoint_id": "intake",
            "name": "Intake interview",
            "purpose": "Legacy intake",
            "agent_prompt": "Legacy intake prompt",
            "status": "CAPTURED",
            "notes": "The inventor explained the causal mechanism.",
        },
        {
            "checkpoint_id": "prospecting",
            "name": "Prior-art prospecting",
            "purpose": "Legacy prospecting",
            "agent_prompt": "Legacy prospecting prompt",
            "status": "IN_PROGRESS",
            "notes": "Three search leads still need review.",
        },
        {
            "checkpoint_id": "drafting",
            "name": "Disclosure drafting",
            "purpose": "Legacy drafting",
            "agent_prompt": "Legacy drafting prompt",
            "status": "NOT_STARTED",
            "notes": "",
        },
        {
            "checkpoint_id": "adversarial",
            "name": "Adversarial review",
            "purpose": "Legacy review",
            "agent_prompt": "Legacy review prompt",
            "status": "CAPTURED",
            "notes": "The unresolved enablement gap is recorded.",
        },
    ]
    matter_path = matters_directory / f"{matter.matter_id}.json"
    matter_path.write_text(json.dumps(legacy_payload))

    loaded = FileMatterStore(matters_directory=matters_directory).load_matter(
        matter.matter_id
    )
    checkpoints = {
        checkpoint.checkpoint_id: checkpoint for checkpoint in loaded.harvest
    }

    assert loaded.workflow_phase is WorkflowPhase.SOURCE_LOCK
    assert list(checkpoints) == [
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
    assert checkpoints["source_lock"].status.value == "NOT_STARTED"
    assert checkpoints["core_mechanism"].status.value == "CAPTURED"
    assert (
        checkpoints["core_mechanism"].notes
        == "The inventor explained the causal mechanism."
    )
    assert checkpoints["seed_assay"].status.value == "IN_PROGRESS"
    assert checkpoints["seed_assay"].notes == "Three search leads still need review."
    assert checkpoints["disclosure_build"].status.value == "NOT_STARTED"
    assert checkpoints["attack_repair"].status.value == "CAPTURED"
    assert (
        checkpoints["attack_repair"].notes
        == "The unresolved enablement gap is recorded."
    )
