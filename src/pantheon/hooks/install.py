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
    package_hooks_dir = Path(__file__).parent

    # Hook script mappings: (source_file, hook_name)
    hook_mappings = [
        ("phase-gate.sh", "QualityGate"),
        ("orchestrator-code-gate.sh", "OrchestratorCodeGate"),
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

    # Hook checks: (script_filename, hook_name, settings_key, expected_matcher)
    hook_checks = [
        ("phase-gate.sh", "QualityGate-SubagentStop", "SubagentStop", ""),
        ("phase-gate.sh", "QualityGate-PreCommit", "PreToolUse", "Bash(git commit*)"),
        ("phase-gate.sh", "QualityGate-Task", "PreToolUse", "Task"),
        (
            "orchestrator-code-gate.sh",
            "OrchestratorCodeGate",
            "PreToolUse",
            "Write(*) | Edit(*)",
        ),
    ]

    for script_filename, hook_name, settings_key, expected_matcher in hook_checks:
        script_path = hooks_dir / script_filename

        # Check if script exists
        if not script_path.exists():
            results[hook_name] = f"Missing: {script_filename} not found"
            continue

        # Check if executable
        if not os.access(script_path, os.X_OK):
            results[hook_name] = f"Missing executable permission on {script_filename}"
            continue

        # Check if settings.json has correct configuration (all use array format)
        if settings_key not in settings_hooks:
            results[hook_name] = "Not configured in .claude/settings.json"
            continue

        hook_array = settings_hooks[settings_key]
        if not isinstance(hook_array, list):
            results[hook_name] = f"{settings_key} not configured as array"
            continue

        # Check if hook with expected matcher exists
        matching_hook = None
        for hook in hook_array:
            matcher = hook.get("matcher") if isinstance(hook, dict) else None
            if matcher == expected_matcher:
                matching_hook = hook
                break

        if not matching_hook:
            if expected_matcher:
                matcher_desc = f"matcher '{expected_matcher}'"
            else:
                matcher_desc = "empty matcher"
            results[hook_name] = f"Hook with {matcher_desc} not found in {settings_key}"
            continue

        # Verify the hook command points to correct script
        hook_commands = matching_hook.get("hooks", [])
        has_correct_path = any(
            script_filename in cmd.get("command", "") for cmd in hook_commands
        )
        if not has_correct_path:
            results[hook_name] = f"Incorrect path in {settings_key} hook"
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

    # Initialize hooks dict if not present
    if "hooks" not in settings:
        settings["hooks"] = {}

    # Initialize PreToolUse array if not present
    if "PreToolUse" not in settings["hooks"]:
        settings["hooks"]["PreToolUse"] = []

    # Configure SubagentStop → phase-gate.sh
    if "SubagentStop" not in settings["hooks"]:
        settings["hooks"]["SubagentStop"] = []

    subagent_stop_exists = any(
        hook.get("matcher") == ""
        for hook in settings["hooks"]["SubagentStop"]
        if isinstance(hook, dict)
    )

    if not subagent_stop_exists:
        settings["hooks"]["SubagentStop"].append(
            {
                "matcher": "",
                "hooks": [
                    {
                        "type": "command",
                        "command": str(rel_hooks_dir / "phase-gate.sh"),
                    }
                ],
            }
        )

    # Configure PreToolUse(Task) → phase-gate.sh (for phase transitions)
    task_hook_exists = any(
        hook.get("matcher") == "Task"
        for hook in settings["hooks"]["PreToolUse"]
        if isinstance(hook, dict)
    )

    if not task_hook_exists:
        settings["hooks"]["PreToolUse"].append(
            {
                "matcher": "Task",
                "hooks": [
                    {
                        "type": "command",
                        "command": str(rel_hooks_dir / "phase-gate.sh"),
                    }
                ],
            }
        )

    # Configure PreToolUse(Bash(git commit*)) → phase-gate.sh
    git_commit_hook_exists = any(
        hook.get("matcher") == "Bash(git commit*)"
        for hook in settings["hooks"]["PreToolUse"]
        if isinstance(hook, dict)
    )

    if not git_commit_hook_exists:
        settings["hooks"]["PreToolUse"].append(
            {
                "matcher": "Bash(git commit*)",
                "hooks": [
                    {
                        "type": "command",
                        "command": str(rel_hooks_dir / "phase-gate.sh"),
                    }
                ],
            }
        )

    # Configure PreToolUse(Write(*) | Edit(*)) → orchestrator-code-gate.sh
    write_edit_hook_exists = any(
        hook.get("matcher") in ["Write(*) | Edit(*)", "Write(*)", "Edit(*)"]
        for hook in settings["hooks"]["PreToolUse"]
        if isinstance(hook, dict)
    )

    if not write_edit_hook_exists:
        settings["hooks"]["PreToolUse"].append(
            {
                "matcher": "Write(*) | Edit(*)",
                "hooks": [
                    {
                        "type": "command",
                        "command": str(rel_hooks_dir / "orchestrator-code-gate.sh"),
                    }
                ],
            }
        )

    # Write updated settings
    with open(settings_path, "w") as f:
        json.dump(settings, f, indent=2)
