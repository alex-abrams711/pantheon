"""Main Spec Kit integration orchestration."""

from pathlib import Path
from typing import Optional

from .backup import create_backup
from .detection import (
    detect_command_format,
    get_command_files,
    verify_agents_installed,
    verify_spec_kit,
)
from .directives import (
    integrate_implement_command,
    integrate_plan_command,
    integrate_tasks_command,
)
from .types import IntegrationResult
from .validation import validate_integration


def integrate_spec_kit(project_root: Optional[Path] = None) -> IntegrationResult:
    """Main integration flow: Add DEV agent directives to Spec Kit commands.

    Args:
        project_root: Root directory of the project. Defaults to current directory.

    Returns:
        Dictionary with integration results:
        {
            "success": bool,
            "backup_dir": Path or None,
            "files_modified": list of filenames,
            "errors": list of error messages,
            "validation": dict from validate_integration()
        }
    """
    if project_root is None:
        project_root = Path.cwd()

    result: IntegrationResult = {
        "success": False,
        "backup_dir": None,
        "files_modified": [],
        "errors": [],
        "validation": {"valid": False, "errors": [], "files_checked": []},
    }

    # Step 1: Verify prerequisites
    if not verify_agents_installed(project_root):
        result["errors"].append("DEV agent not installed. Run 'pantheon init' first.")
        return result

    if not verify_spec_kit(project_root):
        result["errors"].append(
            "Spec Kit not detected. Ensure .specify/ and .claude/commands/ exist."
        )
        return result

    # Detect command format
    format_type = detect_command_format(project_root)
    if format_type is None:
        result["errors"].append(
            "Spec Kit command files not found. "
            "Expected either speckit.*.md (v0.0.57+) or *.md (pre-v0.0.57) format."
        )
        return result

    # Step 2: Create backup
    try:
        backup_dir = create_backup(project_root)
        result["backup_dir"] = backup_dir
    except Exception as e:
        result["errors"].append(f"Failed to create backup: {str(e)}")
        return result

    # Step 3: Integrate commands
    try:
        command_files = get_command_files(project_root)

        if integrate_implement_command(project_root):
            result["files_modified"].append(command_files["implement"].name)

        if integrate_plan_command(project_root):
            result["files_modified"].append(command_files["plan"].name)

        if integrate_tasks_command(project_root):
            result["files_modified"].append(command_files["tasks"].name)

    except Exception as e:
        result["errors"].append(f"Integration failed: {str(e)}")
        # TODO: Rollback on failure
        return result

    # Step 4: Validate integration
    validation = validate_integration(project_root)
    result["validation"] = validation

    if validation["valid"]:
        result["success"] = True
    else:
        result["errors"].extend(validation["errors"])

    return result
