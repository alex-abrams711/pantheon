"""Quality configuration module.

Generates and manages .pantheon/quality-config.json for projects.
"""

import json
from pathlib import Path
from typing import Any, Optional

from pantheon.quality.discovery import detect_project_type, discover_quality_commands


def generate_quality_config(
    project_root: Path,
    plan_path: Optional[Path] = None,
    coverage_threshold: int = 80,
) -> Path:
    """
    Generate quality config file for a project.

    Creates .pantheon/quality-config.json with discovered commands
    and quality thresholds.

    Args:
        project_root: Absolute path to project root
        plan_path: Optional path to plan.md
        coverage_threshold: Coverage percentage threshold (0-100)

    Returns:
        Path to created config file (.pantheon/quality-config.json)

    Raises:
        ValueError: If project_root invalid or threshold out of range
    """
    # Validate inputs
    if not project_root.exists() or not project_root.is_dir():
        raise ValueError(
            f"project_root does not exist or is not a directory: {project_root}"
        )

    if not (0 <= coverage_threshold <= 100):
        raise ValueError(
            f"coverage_threshold must be between 0 and 100, got: {coverage_threshold}"
        )

    # Create .pantheon directory if not exists
    pantheon_dir = project_root / ".pantheon"
    pantheon_dir.mkdir(exist_ok=True)

    # Discover quality commands
    commands = discover_quality_commands(project_root, plan_path)

    # Detect project type
    project_type = detect_project_type(project_root)

    # Determine discovery source
    discovery_source = "plan.md" if plan_path and plan_path.exists() else "auto"

    # Build config structure
    config = {
        "version": "1.0",
        "project_type": project_type,
        "commands": commands,
        "thresholds": {
            "coverage_branches": coverage_threshold,
            "coverage_statements": coverage_threshold,
        },
        "discovery_source": discovery_source,
    }

    # Write config file
    config_path = pantheon_dir / "quality-config.json"
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    return config_path


def load_quality_config(project_root: Path) -> dict[str, Any]:
    """
    Load quality config from project.

    Args:
        project_root: Absolute path to project root

    Returns:
        Dictionary with config data

    Raises:
        FileNotFoundError: If config doesn't exist
        ValueError: If config JSON is invalid or missing required fields
    """
    config_path = project_root / ".pantheon" / "quality-config.json"

    if not config_path.exists():
        raise FileNotFoundError(
            f"Quality config not found: {config_path}\n"
            "Run 'pantheon integrate' or generate config manually."
        )

    # Load JSON
    try:
        with open(config_path) as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in quality config: {e}") from e

    # Validate required fields
    required_fields = ["version", "project_type", "commands", "thresholds"]
    missing_fields = [field for field in required_fields if field not in config]

    if missing_fields:
        raise ValueError(
            f"Quality config missing required fields: {', '.join(missing_fields)}"
        )

    return dict(config)


def validate_quality_config(config: Any) -> bool:
    """
    Validate quality config structure.

    Checks for required keys, correct types, and valid threshold values.

    Args:
        config: Dictionary to validate

    Returns:
        True if valid, False otherwise
    """
    # Handle non-dict input
    if not isinstance(config, dict):
        return False

    # Check required keys
    required_keys = ["version", "commands", "thresholds"]
    if not all(key in config for key in required_keys):
        return False

    # Check commands is dict with string values
    commands = config.get("commands")
    if not isinstance(commands, dict):
        return False

    if not all(isinstance(v, str) for v in commands.values()):
        return False

    # Check thresholds
    thresholds = config.get("thresholds")
    if not isinstance(thresholds, dict):
        return False

    # Validate threshold values (must be 0-100)
    for key, value in thresholds.items():
        if not isinstance(value, (int, float)):
            return False
        if not (0 <= value <= 100):
            return False

    return True
