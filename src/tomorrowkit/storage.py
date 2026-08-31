from abc import ABC, abstractmethod
from _thread import RLock as RLockType
from datetime import datetime
from pathlib import Path
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
            final_path = self._matter_path(matter.matter_id)
            temporary_path = final_path.with_suffix(".json.tmp")
            try:
                temporary_path.write_text(matter.model_dump_json(indent=2))
                temporary_path.replace(final_path)
            except OSError as e:
                raise MatterStorageError(
                    f"Cannot write matter file: {final_path}"
                ) from e

    def save_matter_if_current(
        self, matter: MatterDocument, expected_updated_at: datetime
    ) -> None:
        with self._lock:
            current = self.load_matter(matter.matter_id)
            if current.updated_at != expected_updated_at:
                raise StaleMatterError(str(matter.matter_id))
            self.save_matter(matter)

    def load_matter(self, matter_id: MatterId) -> MatterDocument:
        with self._lock:
            matter_path = self._matter_path(matter_id)
            if not matter_path.exists():
                raise MatterNotFoundError(matter_id)
            try:
                raw_json = matter_path.read_text()
            except OSError as e:
                raise MatterStorageError(
                    f"Cannot read matter file: {matter_path}"
                ) from e
            try:
                return MatterDocument.model_validate_json(raw_json)
            except ValidationError as e:
                raise MatterStorageError(
                    f"Matter file is not a valid matter document: {matter_path}"
                ) from e

    def list_matters(self) -> list[MatterDocument]:
        with self._lock:
            if not self.matters_directory.exists():
                return []
            # Skip (but loudly log) any corrupt file so one bad record cannot hide the rest.
            matters: list[MatterDocument] = []
            for matter_path in sorted(self.matters_directory.glob("mat-*.json")):
                try:
                    matters.append(
                        MatterDocument.model_validate_json(matter_path.read_text())
                    )
                except ValidationError:
                    logger.warning(
                        "Skipped matter file that is not a valid matter document: {}",
                        matter_path,
                    )
            return sorted(matters, key=lambda matter: matter.created_at, reverse=True)

    def delete_matter(self, matter_id: MatterId) -> None:
        with self._lock:
            matter_path = self._matter_path(matter_id)
            if not matter_path.exists():
                raise MatterNotFoundError(matter_id)
            matter_path.unlink()

    def _matter_path(self, matter_id: MatterId) -> Path:
        return self.matters_directory / f"{matter_id}.json"
