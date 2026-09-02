import fcntl
import os
from _thread import RLock as RLockType
from abc import ABC, abstractmethod
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from tempfile import NamedTemporaryFile
from threading import RLock

from imbue.imbue_common.mutable_model import MutableModel
from loguru import logger
from pydantic import Field, PrivateAttr, ValidationError

from tomorrowkit.data_types import MatterDocument, MatterId
from tomorrowkit.errors import MatterNotFoundError, MatterStorageError, StaleMatterError


class MatterStoreInterface(MutableModel, ABC):
    """Defines the contract for persisting and retrieving matter documents."""

    @abstractmethod
    def save_matter(self, matter: MatterDocument) -> None:
        """Persist a matter document, overwriting any existing version."""

    @abstractmethod
    def load_matter(self, matter_id: MatterId) -> MatterDocument:
        """Load a matter by ID. Raises MatterNotFoundError if absent."""

    @abstractmethod
    def save_matter_if_current(
        self, matter: MatterDocument, expected_updated_at: datetime
    ) -> None:
        """Save only if the stored matter still has the expected revision."""

    @abstractmethod
    def list_matters(self) -> list[MatterDocument]:
        """Load every stored matter, newest first."""

    @abstractmethod
    def delete_matter(self, matter_id: MatterId) -> None:
        """Remove a matter from storage. Raises MatterNotFoundError if absent."""


class FileMatterStore(MatterStoreInterface):
    """Stores each matter as one JSON file under a local directory."""

    _lock: RLockType = PrivateAttr(default_factory=RLock)

    matters_directory: Path = Field(
        frozen=True, description="Directory holding one JSON file per matter"
    )

    def save_matter(self, matter: MatterDocument) -> None:
        with self._lock:
            self.matters_directory.mkdir(parents=True, exist_ok=True)
            with self._matter_lock(matter.matter_id, exclusive=True):
                self._write_matter_unlocked(matter)

    def save_matter_if_current(
        self, matter: MatterDocument, expected_updated_at: datetime
    ) -> None:
        with self._lock:
            self.matters_directory.mkdir(parents=True, exist_ok=True)
            with self._matter_lock(matter.matter_id, exclusive=True):
                current = self._load_matter_unlocked(matter.matter_id)
                if current.updated_at != expected_updated_at:
                    raise StaleMatterError(str(matter.matter_id))
                self._write_matter_unlocked(matter)

    def load_matter(self, matter_id: MatterId) -> MatterDocument:
        with self._lock:
            self.matters_directory.mkdir(parents=True, exist_ok=True)
            with self._matter_lock(matter_id, exclusive=False):
                return self._load_matter_unlocked(matter_id)

    def list_matters(self) -> list[MatterDocument]:
        with self._lock:
            if not self.matters_directory.exists():
                return []
            # Skip (but loudly log) any corrupt file so one bad record cannot hide the rest.
            matters: list[MatterDocument] = []
            for matter_path in sorted(self.matters_directory.glob("mat-*.json")):
                try:
                    matter_id = MatterId(matter_path.stem)
                    with self._matter_lock(matter_id, exclusive=False):
                        matters.append(self._load_matter_unlocked(matter_id))
                except (MatterNotFoundError, MatterStorageError, ValueError):
                    logger.warning(
                        "Skipped matter file that is not a valid matter document: {}",
                        matter_path,
                    )
            return sorted(matters, key=lambda matter: matter.created_at, reverse=True)

    def delete_matter(self, matter_id: MatterId) -> None:
        with self._lock:
            self.matters_directory.mkdir(parents=True, exist_ok=True)
            with self._matter_lock(matter_id, exclusive=True):
                matter_path = self._matter_path(matter_id)
                if not matter_path.exists():
                    raise MatterNotFoundError(matter_id)
                try:
                    matter_path.unlink()
                except OSError as e:
                    raise MatterStorageError(
                        f"Cannot delete matter file: {matter_path}"
                    ) from e

    def _matter_path(self, matter_id: MatterId) -> Path:
        return self.matters_directory / f"{matter_id}.json"

    def _matter_lock_path(self, matter_id: MatterId) -> Path:
        return self.matters_directory / f".{matter_id}.lock"

    @contextmanager
    def _matter_lock(self, matter_id: MatterId, *, exclusive: bool) -> Iterator[None]:
        """Hold an advisory lock shared by every process touching this matter."""
        lock_path = self._matter_lock_path(matter_id)
        try:
            lock_file = lock_path.open("a+b")
        except OSError as e:
            raise MatterStorageError(f"Cannot open matter lock: {lock_path}") from e

        with lock_file:
            try:
                operation = fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH
                fcntl.flock(lock_file.fileno(), operation)
            except OSError as e:
                raise MatterStorageError(f"Cannot lock matter file: {lock_path}") from e
            try:
                yield
            finally:
                try:
                    fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
                except OSError:
                    logger.exception("Failed to unlock matter file: {}", lock_path)

    def _load_matter_unlocked(self, matter_id: MatterId) -> MatterDocument:
        matter_path = self._matter_path(matter_id)
        if not matter_path.exists():
            raise MatterNotFoundError(matter_id)
        try:
            raw_json = matter_path.read_text()
        except OSError as e:
            raise MatterStorageError(f"Cannot read matter file: {matter_path}") from e
        try:
            return MatterDocument.model_validate_json(raw_json)
        except ValidationError as e:
            raise MatterStorageError(
                f"Matter file is not a valid matter document: {matter_path}"
            ) from e

    def _write_matter_unlocked(self, matter: MatterDocument) -> None:
        """Atomically replace one matter using a process-unique sibling file."""
        final_path = self._matter_path(matter.matter_id)
        temporary_path: Path | None = None
        try:
            with NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.matters_directory,
                prefix=f".{final_path.name}.",
                suffix=".tmp",
                delete=False,
            ) as temporary_file:
                temporary_path = Path(temporary_file.name)
                temporary_file.write(matter.model_dump_json(indent=2))
                temporary_file.flush()
                os.fsync(temporary_file.fileno())
            os.replace(temporary_path, final_path)
        except OSError as e:
            if temporary_path is not None:
                try:
                    temporary_path.unlink(missing_ok=True)
                except OSError:
                    logger.exception(
                        "Failed to clean up temporary matter file: {}", temporary_path
                    )
            raise MatterStorageError(f"Cannot write matter file: {final_path}") from e
