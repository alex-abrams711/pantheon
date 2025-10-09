"""Backup, restore, and rollback utilities for Spec Kit integration."""

import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from .detection import get_command_files
from .types import RestoreResult, RollbackResult


def create_backup(project_root: Optional[Path] = None) -> Path:
    """Create timestamped backup of Spec Kit command files.

    Args:
        project_root: Root directory of the project. Defaults to current directory.

    Returns:
        Path to the backup directory.

    Raises:
        FileNotFoundError: If command files don't exist.
    """
    if project_root is None:
        project_root = Path.cwd()

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_dir = project_root / f".integration-backup-{timestamp}"
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Get command files based on detected format
    command_files = get_command_files(project_root)

    for command_name, source_path in command_files.items():
        if source_path.exists():
            # Preserve original filename in backup
            dest = backup_dir / source_path.name
            shutil.copy2(source_path, dest)

    return backup_dir


def find_latest_backup(project_root: Optional[Path] = None) -> Optional[Path]:
    """Find the most recent integration backup directory.

    Args:
        project_root: Root directory of the project. Defaults to current directory.

    Returns:
        Path to the most recent backup directory, or None if no backups found.
    """
    if project_root is None:
        project_root = Path.cwd()

    # Find all backup directories
    backup_dirs = list(project_root.glob(".integration-backup-*"))

    if not backup_dirs:
        return None

    # Sort by name (which includes timestamp) and return the latest
    backup_dirs.sort(reverse=True)
    return backup_dirs[0]


def restore_files(
    backup_dir: Path, project_root: Optional[Path] = None
) -> RestoreResult:
    """Restore command files from a backup directory.

    Args:
        backup_dir: Path to the backup directory containing files to restore.
        project_root: Root directory of the project. Defaults to current directory.

    Returns:
        Dictionary with restoration results:
        {
            "success": bool,
            "files_restored": list of filenames,
            "errors": list of error messages
        }
    """
    if project_root is None:
        project_root = Path.cwd()

    result: RestoreResult = {"success": False, "files_restored": [], "errors": []}

    if not backup_dir.exists():
        result["errors"].append(f"Backup directory not found: {backup_dir}")
        return result

    commands_dir = project_root / ".claude" / "commands"

    # Restore each file from backup
    for backup_file in backup_dir.glob("*.md"):
        try:
            dest_file = commands_dir / backup_file.name
            shutil.copy2(backup_file, dest_file)
            result["files_restored"].append(backup_file.name)
        except Exception as e:
            result["errors"].append(f"Failed to restore {backup_file.name}: {str(e)}")

    if result["files_restored"] and not result["errors"]:
        result["success"] = True

    return result


def rollback_integration(project_root: Optional[Path] = None) -> RollbackResult:
    """Rollback to the most recent backup.

    Args:
        project_root: Root directory of the project. Defaults to current directory.

    Returns:
        Dictionary with rollback results:
        {
            "success": bool,
            "backup_dir": Path or None,
            "files_restored": list of filenames,
            "errors": list of error messages
        }
    """
    if project_root is None:
        project_root = Path.cwd()

    result: RollbackResult = {
        "success": False,
        "backup_dir": None,
        "files_restored": [],
        "errors": [],
    }

    # Find latest backup
    backup_dir = find_latest_backup(project_root)

    if not backup_dir:
        result["errors"].append("No backup found. Nothing to rollback.")
        return result

    result["backup_dir"] = backup_dir

    # Restore files
    restore_result = restore_files(backup_dir, project_root)

    result["files_restored"] = restore_result["files_restored"]
    result["errors"].extend(restore_result["errors"])
    result["success"] = restore_result["success"]

    return result
