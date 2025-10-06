"""Quality command discovery module.

Discovers project-specific quality commands (test, lint, type-check, coverage, build)
from project structure or plan.md.
"""

import json
import re
from pathlib import Path
from typing import Optional


def discover_quality_commands(
    project_root: Path,
    plan_path: Optional[Path] = None,
) -> dict[str, str]:
    """
    Discover quality commands for a project.

    Strategy:
    1. If plan_path provided, check for explicit commands in plan.md first
    2. Auto-discover commands based on project type
    3. Return dict with all 5 command keys (use "" for not found)

    Args:
        project_root: Absolute path to project root
        plan_path: Optional path to plan.md (if using Spec Kit)

    Returns:
        Dictionary with keys: test, lint, type_check, coverage, build
        Values are command strings or empty strings if not found

    Raises:
        ValueError: If project_root doesn't exist
    """
    # Validate project_root
    if not project_root.exists() or not project_root.is_dir():
        raise ValueError(
            f"project_root does not exist or is not a directory: "
            f"{project_root}"
        )

    # Initialize result with all required keys
    commands: dict[str, str] = {
        "test": "",
        "lint": "",
        "type_check": "",
        "coverage": "",
        "build": "",
    }

    # Step 1: Try to get explicit commands from plan.md
    if plan_path and plan_path.exists():
        plan_commands = parse_plan_quality_commands(plan_path)
        commands.update(plan_commands)

    # Step 2: Auto-discover missing commands based on project type
    project_type = detect_project_type(project_root)
    auto_commands = _auto_discover_commands(project_root, project_type)

    # Only fill in commands that weren't in plan.md (empty strings)
    for key, value in auto_commands.items():
        if not commands[key]:  # Empty string = not found in plan
            commands[key] = value

    return commands


def detect_project_type(project_root: Path) -> str:
    """
    Detect project type from file structure.

    Args:
        project_root: Absolute path to project root

    Returns:
        One of: "node", "python", "go", "ruby", "other"
    """
    # Check for Node.js
    if (project_root / "package.json").exists():
        return "node"

    # Check for Python (pyproject.toml or setup.py)
    if (
        (project_root / "pyproject.toml").exists()
        or (project_root / "setup.py").exists()
    ):
        return "python"

    # Check for Go
    if (project_root / "go.mod").exists():
        return "go"

    # Check for Ruby
    if (project_root / "Gemfile").exists():
        return "ruby"

    # Unknown type
    return "other"


def parse_plan_quality_commands(plan_path: Path) -> dict[str, str]:
    """
    Extract quality commands from plan.md.

    Looks for "## Quality Standards" section and parses lines like:
    - Test command: pytest tests/
    - Lint command: ruff check src/

    Args:
        plan_path: Path to plan.md file

    Returns:
        Dictionary with command keys and values from plan
        Only includes commands explicitly defined in plan

    Raises:
        FileNotFoundError: If plan.md doesn't exist
    """
    if not plan_path.exists():
        raise FileNotFoundError(f"plan.md not found: {plan_path}")

    content = plan_path.read_text()

    # Find Quality Standards section
    # Look for "## Quality Standards" heading
    quality_section_match = re.search(
        r"##\s+Quality Standards.*?(?=\n##|\Z)",
        content,
        re.DOTALL | re.IGNORECASE,
    )

    if not quality_section_match:
        return {}

    quality_section = quality_section_match.group(0)

    # Parse command lines
    commands: dict[str, str] = {}

    # Patterns for different command types
    patterns = {
        "test": r"-\s+Test command:\s*(.+?)(?:\n|$)",
        "lint": r"-\s+Lint command:\s*(.+?)(?:\n|$)",
        "type_check": r"-\s+Type command:\s*(.+?)(?:\n|$)",
        "coverage": r"-\s+Coverage command:\s*(.+?)(?:\n|$)",
        "build": r"-\s+Build command:\s*(.+?)(?:\n|$)",
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, quality_section, re.IGNORECASE)
        if match:
            commands[key] = match.group(1).strip()

    return commands


def _auto_discover_commands(project_root: Path, project_type: str) -> dict[str, str]:
    """
    Auto-discover commands based on project type.

    Args:
        project_root: Project root path
        project_type: Detected project type

    Returns:
        Dictionary with discovered commands
    """
    commands: dict[str, str] = {
        "test": "",
        "lint": "",
        "type_check": "",
        "coverage": "",
        "build": "",
    }

    if project_type == "node":
        commands.update(_discover_node_commands(project_root))
    elif project_type == "python":
        commands.update(_discover_python_commands(project_root))
    elif project_type == "go":
        commands.update(_discover_go_commands())
    elif project_type == "ruby":
        commands.update(_discover_ruby_commands())
    # "other" type returns empty commands

    return commands


def _discover_node_commands(project_root: Path) -> dict[str, str]:
    """Discover commands for Node.js projects."""
    commands: dict[str, str] = {
        "test": "",
        "lint": "",
        "type_check": "",
        "coverage": "",
        "build": "",
    }

    # Parse package.json for scripts
    package_json_path = project_root / "package.json"
    if package_json_path.exists():
        try:
            with open(package_json_path) as f:
                package_data = json.load(f)

            scripts = package_data.get("scripts", {})

            # Map npm scripts to our command keys
            if "test" in scripts:
                commands["test"] = "npm test"
            if "lint" in scripts:
                commands["lint"] = "npm run lint"
            if "type-check" in scripts or "typecheck" in scripts:
                if "type-check" in scripts:
                    commands["type_check"] = "npm run type-check"
                else:
                    commands["type_check"] = "npm run typecheck"
            if "coverage" in scripts:
                commands["coverage"] = "npm run coverage"
            if "build" in scripts:
                commands["build"] = "npm run build"

        except (json.JSONDecodeError, OSError):
            pass

    return commands


def _discover_python_commands(project_root: Path) -> dict[str, str]:
    """Discover commands for Python projects."""
    commands: dict[str, str] = {
        "test": "",
        "lint": "",
        "type_check": "",
        "coverage": "",
        "build": "",
    }

    # Check for pyproject.toml
    pyproject_path = project_root / "pyproject.toml"
    if pyproject_path.exists():
        content = pyproject_path.read_text()

        # Detect pytest
        if "[tool.pytest" in content or "pytest" in content:
            commands["test"] = "pytest tests/"
            commands["coverage"] = "pytest tests/ --cov"

        # Detect ruff
        if "[tool.ruff" in content or "ruff" in content:
            commands["lint"] = "ruff check src/ tests/"

        # Detect mypy
        if "[tool.mypy" in content or "mypy" in content:
            commands["type_check"] = "mypy src/"

        # Build command
        commands["build"] = "python -m build"

    return commands


def _discover_go_commands() -> dict[str, str]:
    """Discover commands for Go projects."""
    return {
        "test": "go test ./...",
        "lint": "golangci-lint run",
        "type_check": "",  # Go is statically typed, covered by build
        "coverage": "go test -cover ./...",
        "build": "go build",
    }


def _discover_ruby_commands() -> dict[str, str]:
    """Discover commands for Ruby projects."""
    return {
        "test": "bundle exec rspec",
        "lint": "bundle exec rubocop",
        "type_check": "",  # Ruby is dynamically typed
        "coverage": "bundle exec rspec --format documentation",
        "build": "bundle install",
    }
