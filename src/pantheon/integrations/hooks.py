"""Hook installation and management module.

Installs and configures Claude Code quality gate hooks in user projects.
"""

import json
import os
import shutil
from pathlib import Path
from typing import Any


def install_hooks(project_root: Path) -> dict[str, bool]:
    """
    Install quality gate hooks in project.

    Copies hook scripts from package to project's .pantheon/hooks/ directory,
    makes them executable, and updates .claude/settings.json.

    Args:
        project_root: Absolute path to project root

    Returns:
        Dictionary with hook names as keys, success status as values
        Example: {"SubagentStop": True, "PreCommit": True, "PhaseGate": True}

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

    # Create .pantheon/hooks/ directory
    hooks_dir = project_root / ".pantheon" / "hooks"
    try:
        hooks_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError as e:
        raise PermissionError(
            f"Cannot create {hooks_dir}: insufficient permissions"
        ) from e

    # Get hook scripts from package
    package_hooks_dir = Path(__file__).parent.parent / "hooks"

    # Hook script mappings: (source_file, hook_name)
    hook_mappings = [
        ("subagent-validation.sh", "SubagentStop"),
        ("pre-commit-gate.sh", "PreCommit"),
        ("phase-gate.sh", "PhaseGate"),  # UserPromptSubmit
    ]

    results: dict[str, bool] = {}

    # Copy and setup each hook
    for script_filename, hook_name in hook_mappings:
        source_path = package_hooks_dir / script_filename
        dest_path = hooks_dir / script_filename

        try:
            # Copy script from package to project
            if source_path.exists():
                shutil.copy2(source_path, dest_path)
            else:
                # Hook script doesn't exist in package (not yet created)
                # Create a placeholder for now
                dest_path.write_text(
                    "#!/bin/bash\n"
                    "# Placeholder - hook script not yet implemented\n"
                    "exit 0\n"
                )

            # Make executable
            os.chmod(dest_path, 0o755)

            results[hook_name] = True

        except (OSError, PermissionError):
            results[hook_name] = False

    # Update .claude/settings.json
    _update_settings_json(project_root, hooks_dir)

    return results


def uninstall_hooks(project_root: Path) -> bool:
    """
    Remove quality gate hooks from project.

    Removes hook entries from .claude/settings.json and deletes
    .pantheon/hooks/ directory. Preserves .pantheon/quality-config.json.

    Args:
        project_root: Absolute path to project root

    Returns:
        True if all hooks removed successfully

    Raises:
        FileNotFoundError: If .claude/ directory doesn't exist
    """
    # Validate .claude/ directory exists
    claude_dir = project_root / ".claude"
    if not claude_dir.exists():
        raise FileNotFoundError(
            f".claude/ directory not found in {project_root}"
        )

    # Remove hook entries from settings.json
    _remove_hooks_from_settings(project_root)

    # Delete .pantheon/hooks/ directory
    hooks_dir = project_root / ".pantheon" / "hooks"
    if hooks_dir.exists():
        try:
            shutil.rmtree(hooks_dir)
        except OSError:
            return False

    return True


def validate_hook_installation(project_root: Path) -> dict[str, str]:
    """
    Validate that hooks are installed correctly.

    Checks that hook scripts exist, are executable, and settings.json
    has correct paths.

    Args:
        project_root: Absolute path to project root

    Returns:
        Dictionary with hook names as keys, status messages as values
        Example: {"SubagentStop": "OK", "PreCommit": "Missing executable permission"}
    """
    results: dict[str, str] = {}

    hooks_dir = project_root / ".pantheon" / "hooks"
    settings_path = project_root / ".claude" / "settings.json"

    # Load settings.json if exists
    settings_hooks: dict[str, Any] = {}
    if settings_path.exists():
        try:
            with open(settings_path) as f:
                settings = json.load(f)
            settings_hooks = settings.get("hooks", {})
        except (json.JSONDecodeError, OSError):
            pass

    # Hook mappings: (script_filename, hook_name, settings_key)
    hook_checks = [
        ("subagent-validation.sh", "SubagentStop", "SubagentStop"),
        ("pre-commit-gate.sh", "PreCommit", "PreCommit"),
        ("phase-gate.sh", "PhaseGate", "UserPromptSubmit"),
    ]

    for script_filename, hook_name, settings_key in hook_checks:
        script_path = hooks_dir / script_filename

        # Check if script exists
        if not script_path.exists():
            results[hook_name] = f"Missing: {script_filename} not found"
            continue

        # Check if executable
        if not os.access(script_path, os.X_OK):
            results[hook_name] = f"Missing executable permission on {script_filename}"
            continue

        # Check if settings.json has correct path
        if settings_key not in settings_hooks:
            results[hook_name] = "Not configured in .claude/settings.json"
            continue

        settings_path_str = settings_hooks[settings_key]
        if script_filename not in settings_path_str:
            results[hook_name] = f"Incorrect path in settings.json: {settings_path_str}"
            continue

        # All checks passed
        results[hook_name] = "OK"

    return results


def _update_settings_json(project_root: Path, hooks_dir: Path) -> None:
    """Update .claude/settings.json with hook paths."""
    settings_path = project_root / ".claude" / "settings.json"

    # Load existing settings or create new
    if settings_path.exists():
        with open(settings_path) as f:
            settings = json.load(f)
    else:
        settings = {}

    # Add hooks configuration
    # Paths are relative to project root
    rel_hooks_dir = hooks_dir.relative_to(project_root)
    settings["hooks"] = {
        "SubagentStop": str(rel_hooks_dir / "subagent-validation.sh"),
        "PreCommit": str(rel_hooks_dir / "pre-commit-gate.sh"),
        "UserPromptSubmit": str(rel_hooks_dir / "phase-gate.sh"),
    }

    # Write updated settings
    with open(settings_path, "w") as f:
        json.dump(settings, f, indent=2)


def _remove_hooks_from_settings(project_root: Path) -> None:
    """Remove hook entries from .claude/settings.json."""
    settings_path = project_root / ".claude" / "settings.json"

    if not settings_path.exists():
        return

    # Load settings
    with open(settings_path) as f:
        settings = json.load(f)

    # Remove hooks key
    if "hooks" in settings:
        del settings["hooks"]

    # Write updated settings
    with open(settings_path, "w") as f:
        json.dump(settings, f, indent=2)
