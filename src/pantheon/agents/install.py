"""Agent installation module.

Installs DEV and QA agents in user projects.
"""

import shutil
from pathlib import Path


def install_agents(project_root: Path) -> dict[str, str]:
    """
    Install DEV and QA agents in project.

    Copies agent markdown files from package to project's .claude/agents/ directory.

    Args:
        project_root: Absolute path to project root

    Returns:
        Dictionary with agent names as keys, status as values
        Status values: "copied", "skipped" (already exists), "failed"
        Example: {"dev": "copied", "qa": "skipped"}

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

    # Create .claude/agents/ directory
    agents_dir = claude_dir / "agents"
    try:
        agents_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError as e:
        raise PermissionError(
            f"Cannot create {agents_dir}: insufficient permissions"
        ) from e

    # Get agent files from package
    package_agents_dir = Path(__file__).parent
    agents_to_copy = ["dev.md", "qa.md"]

    results: dict[str, str] = {}

    # Copy each agent
    for agent_file in agents_to_copy:
        agent_name = agent_file.replace(".md", "")
        source_path = package_agents_dir / agent_file
        dest_path = agents_dir / agent_file

        try:
            # Skip if already exists
            if dest_path.exists():
                results[agent_name] = "skipped"
                continue

            # Copy agent from package to project
            if source_path.exists():
                shutil.copy2(source_path, dest_path)
                results[agent_name] = "copied"
            else:
                # Agent file doesn't exist in package
                results[agent_name] = "failed"

        except (OSError, PermissionError):
            results[agent_name] = "failed"

    return results


def validate_agent_installation(project_root: Path) -> dict[str, str]:
    """
    Validate that agents are installed correctly.

    Checks that agent files exist and have content.

    Args:
        project_root: Absolute path to project root

    Returns:
        Dictionary with agent names as keys, status messages as values
        Example: {"dev": "OK", "qa": "Missing"}
    """
    results: dict[str, str] = {}

    agents_dir = project_root / ".claude" / "agents"
    agents_to_check = ["dev.md", "qa.md"]

    for agent_file in agents_to_check:
        agent_name = agent_file.replace(".md", "")
        agent_path = agents_dir / agent_file

        # Check if file exists
        if not agent_path.exists():
            results[agent_name] = f"Missing: {agent_file} not found"
            continue

        # Check if file has content
        if agent_path.stat().st_size == 0:
            results[agent_name] = f"Empty: {agent_file} has no content"
            continue

        # All checks passed
        results[agent_name] = "OK"

    return results
