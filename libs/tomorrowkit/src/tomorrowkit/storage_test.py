from pathlib import Path

import pytest

from tomorrowkit.data_types import MatterId
from tomorrowkit.errors import MatterNotFoundError
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
