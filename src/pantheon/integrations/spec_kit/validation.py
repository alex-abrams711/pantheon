"""Integration validation utilities."""

from pathlib import Path
from typing import Optional

from .detection import get_command_files
from .types import ValidationResult


def validate_integration(project_root: Optional[Path] = None) -> ValidationResult:
    """Validate that integration was successful.

    Args:
        project_root: Root directory of the project. Defaults to current directory.

    Returns:
        Dictionary with validation results:
        {
            "valid": bool,
            "errors": list of error messages,
            "files_checked": list of filenames
        }
    """
    if project_root is None:
        project_root = Path.cwd()

    results: ValidationResult = {"valid": True, "errors": [], "files_checked": []}

    # Get command files based on detected format
    command_files = get_command_files(project_root)

    if not command_files:
        results["valid"] = False
        results["errors"].append("No Spec Kit command files detected")
        return results

    # Check that command files exist and contain integration sections
    expected_sections = {
        "implement": "## Sub-Agent Integration",
        "plan": "## Quality Standards (Required for DEV Integration)",
        "tasks": "## Task Format (Required for DEV Integration)",
    }

    for command_name, filepath in command_files.items():
        results["files_checked"].append(filepath.name)

        if not filepath.exists():
            results["valid"] = False
            results["errors"].append(f"{filepath.name} not found")
            continue

        section_marker = expected_sections.get(command_name)
        if not section_marker:
            continue

        try:
            content = filepath.read_text()
            if section_marker not in content:
                results["valid"] = False
                error_msg = (
                    f"{filepath.name} missing integration section: {section_marker}"
                )
                results["errors"].append(error_msg)
        except Exception as e:
            results["valid"] = False
            results["errors"].append(f"Error reading {filepath.name}: {str(e)}")

    return results
