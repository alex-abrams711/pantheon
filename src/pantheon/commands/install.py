"""Command installation module.

Installs Pantheon slash commands in user projects.
"""

import shutil
from pathlib import Path


def install_commands(project_root: Path) -> dict[str, bool]:
    """
    Install Pantheon slash commands in project.

    Copies command markdown files from package to project's
    .claude/commands/pantheon/ directory.

    Args:
        project_root: Absolute path to project root

    Returns:
        Dictionary with command names as keys, success status as values
        Example: {"contextualize": True}

    Raises:
        FileNotFoundError: If .claude/ directory doesn't exist
        PermissionError: If cannot write to project directory
    """
    # Validate .claude/ directory exists
    claude_dir = project_root / ".claude"
    if not claude_dir.exists():
        raise FileNotFoundError(
            f".claude/ directory not found in {project_root}\n"
            "This project is not initialized for Claude Code."
        )

    # Create .claude/commands/pantheon/ directory
    pantheon_commands_dir = claude_dir / "commands" / "pantheon"
    try:
        pantheon_commands_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError as e:
        raise PermissionError(
            f"Cannot create {pantheon_commands_dir}: insufficient permissions"
        ) from e

    # Get command files from package
    package_commands_dir = Path(__file__).parent
    commands_to_copy = ["contextualize.md"]

    results: dict[str, bool] = {}

    # Copy each command
    for command_file in commands_to_copy:
        command_name = command_file.replace(".md", "")
        source_path = package_commands_dir / command_file
        dest_path = pantheon_commands_dir / command_file

        try:
            # Skip if already exists
            if dest_path.exists():
                results[command_name] = True  # Consider existing as success
                continue

            # Copy command from package to project
            if source_path.exists():
                shutil.copy2(source_path, dest_path)
                results[command_name] = True
            else:
                # Command file doesn't exist in package
                results[command_name] = False

        except (OSError, PermissionError):
            results[command_name] = False

    return results


def validate_command_installation(project_root: Path) -> dict[str, str]:
    """
    Validate that commands are installed correctly.

    Checks that command files exist and have content.

    Args:
        project_root: Absolute path to project root

    Returns:
        Dictionary with command names as keys, status messages as values
        Example: {"contextualize": "OK"}
    """
    results: dict[str, str] = {}

    pantheon_commands_dir = project_root / ".claude" / "commands" / "pantheon"
    commands_to_check = ["contextualize.md"]

    for command_file in commands_to_check:
        command_name = command_file.replace(".md", "")
        command_path = pantheon_commands_dir / command_file

        # Check if file exists
        if not command_path.exists():
            results[command_name] = f"Missing: {command_file} not found"
            continue

        # Check if file has content
        if command_path.stat().st_size == 0:
            results[command_name] = f"Empty: {command_file} has no content"
            continue

        # All checks passed
        results[command_name] = "OK"

    return results
