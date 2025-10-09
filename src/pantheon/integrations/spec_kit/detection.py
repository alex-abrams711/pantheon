"""Spec Kit format detection and verification utilities."""

from pathlib import Path
from typing import Optional

from .types import CommandFormat


def detect_command_format(
    project_root: Optional[Path] = None,
) -> Optional[CommandFormat]:
    """Detect which Spec Kit command format is being used.

    Args:
        project_root: Root directory of the project. Defaults to current directory.

    Returns:
        "new" for v0.0.57+ format (speckit.*.md),
        "old" for pre-v0.0.57 format (*.md),
        None if neither format detected.
    """
    if project_root is None:
        project_root = Path.cwd()

    commands_dir = project_root / ".claude" / "commands"

    if not commands_dir.exists():
        return None

    # Check for new format (v0.0.57+)
    new_format_files = [
        "speckit.implement.md",
        "speckit.plan.md",
        "speckit.tasks.md",
    ]
    if all((commands_dir / f).exists() for f in new_format_files):
        return "new"

    # Check for old format (pre-v0.0.57)
    old_format_files = ["implement.md", "plan.md", "tasks.md"]
    if any((commands_dir / f).exists() for f in old_format_files):
        return "old"

    return None


def get_command_files(
    project_root: Optional[Path] = None,
) -> dict[str, Path]:
    """Get command file paths based on detected Spec Kit format.

    Args:
        project_root: Root directory of the project. Defaults to current directory.

    Returns:
        Dictionary mapping command names to file paths:
        {
            "implement": Path,
            "plan": Path,
            "tasks": Path
        }
        Returns empty dict if format cannot be detected.
    """
    if project_root is None:
        project_root = Path.cwd()

    commands_dir = project_root / ".claude" / "commands"
    format_type = detect_command_format(project_root)

    if format_type == "new":
        return {
            "implement": commands_dir / "speckit.implement.md",
            "plan": commands_dir / "speckit.plan.md",
            "tasks": commands_dir / "speckit.tasks.md",
        }
    elif format_type == "old":
        return {
            "implement": commands_dir / "implement.md",
            "plan": commands_dir / "plan.md",
            "tasks": commands_dir / "tasks.md",
        }
    else:
        return {}


def verify_agents_installed(project_root: Optional[Path] = None) -> bool:
    """Verify that DEV agent is installed in the project.

    Args:
        project_root: Root directory of the project. Defaults to current directory.

    Returns:
        True if DEV agent exists in .claude/agents/, False otherwise.
    """
    if project_root is None:
        project_root = Path.cwd()

    dev_agent = project_root / ".claude" / "agents" / "dev.md"
    return dev_agent.exists()


def verify_spec_kit(project_root: Optional[Path] = None) -> bool:
    """Verify that Spec Kit is installed in the project.

    Args:
        project_root: Root directory of the project. Defaults to current directory.

    Returns:
        True if both .specify/ and .claude/commands/ exist, False otherwise.
    """
    if project_root is None:
        project_root = Path.cwd()

    specify_dir = project_root / ".specify"
    commands_dir = project_root / ".claude" / "commands"

    return specify_dir.exists() and commands_dir.exists()
