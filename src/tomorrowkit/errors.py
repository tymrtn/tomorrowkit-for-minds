class TomorrowkitError(Exception):
    """Base exception for all tomorrowkit errors."""

    ...


class MatterNotFoundError(TomorrowkitError, KeyError):
    """Raised when a matter cannot be found in storage."""

    def __init__(self, matter_id: str) -> None:
        self.matter_id = matter_id
        super().__init__(f"Matter with ID '{matter_id}' not found")


class MatterStorageError(TomorrowkitError, OSError):
    """Raised when a matter cannot be read from or written to disk."""

    ...


class StaleMatterError(TomorrowkitError):
    """Raised when an update targets an older revision of a matter."""

    def __init__(self, matter_id: str) -> None:
        self.matter_id = matter_id
        super().__init__(f"Matter with ID '{matter_id}' changed since it was loaded")
