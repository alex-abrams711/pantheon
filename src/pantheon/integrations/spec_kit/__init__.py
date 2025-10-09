"""Spec Kit integration utilities.

Supports both Spec Kit command formats:
- Pre-v0.0.57: implement.md, plan.md, tasks.md
- v0.0.57+: speckit.implement.md, speckit.plan.md, speckit.tasks.md
"""

from .backup import (
    create_backup,
    find_latest_backup,
    restore_files,
    rollback_integration,
)
from .detection import verify_agents_installed, verify_spec_kit
from .directives import integrate_claude_md
from .integration import integrate_spec_kit
from .types import IntegrationResult, RestoreResult, RollbackResult, ValidationResult
from .validation import validate_integration

__all__ = [
    # Main functions
    "integrate_spec_kit",
    "rollback_integration",
    "integrate_claude_md",
    # Validation
    "validate_integration",
    # Verification
    "verify_spec_kit",
    "verify_agents_installed",
    # Utilities
    "create_backup",
    "find_latest_backup",
    "restore_files",
    # Types
    "IntegrationResult",
    "RollbackResult",
    "ValidationResult",
    "RestoreResult",
]
