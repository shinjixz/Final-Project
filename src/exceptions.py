"""Custom exceptions shared by every layer.

The CLI catches ``AppError`` (the base class) so any expected failure is
shown to the user as a friendly message instead of crashing the program.
"""


class AppError(Exception):
    """Base class for all expected application errors."""


class InvalidInputError(AppError):
    """User input failed validation (empty text, bad number, unknown field)."""


class RecordNotFoundError(AppError):
    """A history record with the requested id does not exist."""

    def __init__(self, record_id: int):
        super().__init__(f"ไม่พบรายการ id={record_id} ในประวัติ")
        self.record_id = record_id


class StorageError(AppError):
    """Reading from or writing to the database/file system failed."""


class AnalysisError(AppError):
    """The emotion model could not analyse the given text."""
