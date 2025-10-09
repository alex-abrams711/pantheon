"""Type definitions for Spec Kit integration."""

from pathlib import Path
from typing import Literal, Optional, TypedDict


class ValidationResult(TypedDict):
    """Type for validation result dictionary."""

    valid: bool
    errors: list[str]
    files_checked: list[str]


class IntegrationResult(TypedDict):
    """Type for integration result dictionary."""

    success: bool
    backup_dir: Optional[Path]
    files_modified: list[str]
    errors: list[str]
    validation: ValidationResult


class RestoreResult(TypedDict):
    """Type for restore result dictionary."""

    success: bool
    files_restored: list[str]
    errors: list[str]


class RollbackResult(TypedDict):
    """Type for rollback result dictionary."""

    success: bool
    backup_dir: Optional[Path]
    files_restored: list[str]
    errors: list[str]


CommandFormat = Literal["old", "new"]
