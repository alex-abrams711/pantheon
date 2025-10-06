"""Contract tests for quality config API.

These tests define the contract for src/pantheon/quality/config.py
Tests MUST FAIL until implementation is complete (TDD approach).
"""

import json
from pathlib import Path

import pytest

from pantheon.quality.config import (
    generate_quality_config,
    load_quality_config,
    validate_quality_config,
)


class TestGenerateQualityConfig:
    """Contract tests for generate_quality_config function."""

    def test_generate_creates_pantheon_directory(self, tmp_path: Path) -> None:
        """Contract: creates .pantheon/ directory if it doesn't exist."""
        # Setup: Project without .pantheon/
        assert not (tmp_path / ".pantheon").exists()

        # Execute
        config_path = generate_quality_config(tmp_path)

        # Verify: Directory created
        assert (tmp_path / ".pantheon").exists()
        assert config_path.exists()
        assert config_path.name == "quality-config.json"

    def test_generate_creates_valid_json_matching_schema(self, tmp_path: Path) -> None:
        """Contract: generates valid JSON matching data model schema."""
        # Execute
        config_path = generate_quality_config(tmp_path)

        # Verify: Valid JSON with required fields
        with open(config_path) as f:
            config = json.load(f)

        # Schema validation
        assert "version" in config
        assert "project_type" in config
        assert "commands" in config
        assert "thresholds" in config
        assert "discovery_source" in config

        # Commands structure
        assert isinstance(config["commands"], dict)
        assert "test" in config["commands"]
        assert "lint" in config["commands"]
        assert "type_check" in config["commands"]
        assert "coverage" in config["commands"]
        assert "build" in config["commands"]

        # Thresholds structure
        assert isinstance(config["thresholds"], dict)
        assert "coverage_branches" in config["thresholds"]

    def test_generate_uses_discovered_commands(self, tmp_path: Path) -> None:
        """Contract: includes commands from discovery module."""
        # Setup: Python project
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'\n")

        # Execute
        config_path = generate_quality_config(tmp_path)

        # Verify: Commands discovered and included
        with open(config_path) as f:
            config = json.load(f)

        # Should detect Python project and include pytest/ruff/mypy
        assert config["project_type"] == "python"
        # Commands should be non-empty strings (discovered)
        assert isinstance(config["commands"]["test"], str)
        assert isinstance(config["commands"]["lint"], str)

    def test_generate_sets_coverage_threshold(self, tmp_path: Path) -> None:
        """Contract: sets coverage threshold from parameter."""
        # Execute with custom threshold
        config_path = generate_quality_config(tmp_path, coverage_threshold=90)

        # Verify
        with open(config_path) as f:
            config = json.load(f)

        assert config["thresholds"]["coverage_branches"] == 90

    def test_generate_sets_discovery_source_from_plan(self, tmp_path: Path) -> None:
        """Contract: sets discovery_source='plan.md' when plan provided."""
        # Setup
        plan_path = tmp_path / "plan.md"
        plan_path.write_text("# Plan\n## Quality Standards\n- Test command: pytest\n")

        # Execute
        config_path = generate_quality_config(tmp_path, plan_path)

        # Verify
        with open(config_path) as f:
            config = json.load(f)

        assert config["discovery_source"] == "plan.md"

    def test_generate_sets_discovery_source_auto(self, tmp_path: Path) -> None:
        """Contract: sets discovery_source='auto' when no plan provided."""
        # Execute without plan
        config_path = generate_quality_config(tmp_path)

        # Verify
        with open(config_path) as f:
            config = json.load(f)

        assert config["discovery_source"] == "auto"

    def test_generate_raises_error_for_invalid_threshold(self, tmp_path: Path) -> None:
        """Contract: raises ValueError for threshold > 100."""
        # Execute & Verify
        with pytest.raises(ValueError, match="threshold"):
            generate_quality_config(tmp_path, coverage_threshold=150)

    def test_generate_raises_error_for_negative_threshold(
        self, tmp_path: Path
    ) -> None:
        """Contract: raises ValueError for negative threshold."""
        # Execute & Verify
        with pytest.raises(ValueError, match="threshold"):
            generate_quality_config(tmp_path, coverage_threshold=-10)

    def test_generate_raises_error_for_invalid_project_root(self) -> None:
        """Contract: raises ValueError for invalid project_root."""
        # Setup
        invalid_path = Path("/nonexistent/invalid/path")

        # Execute & Verify
        with pytest.raises(ValueError, match="project_root"):
            generate_quality_config(invalid_path)


class TestLoadQualityConfig:
    """Contract tests for load_quality_config function."""

    def test_load_existing_config_success(self, tmp_path: Path) -> None:
        """Contract: loads existing config successfully."""
        # Setup: Generate config first
        generate_quality_config(tmp_path)

        # Execute
        config = load_quality_config(tmp_path)

        # Verify: Returns dict with correct structure
        assert isinstance(config, dict)
        assert "version" in config
        assert "commands" in config
        assert "thresholds" in config

    def test_load_returns_correct_dictionary_structure(self, tmp_path: Path) -> None:
        """Contract: returns dictionary matching schema."""
        # Setup
        generate_quality_config(tmp_path, coverage_threshold=85)

        # Execute
        config = load_quality_config(tmp_path)

        # Verify: All fields present and correct types
        assert config["version"] == "1.0"
        assert isinstance(config["project_type"], str)
        assert isinstance(config["commands"], dict)
        assert isinstance(config["thresholds"], dict)
        assert config["thresholds"]["coverage_branches"] == 85

    def test_load_missing_config_raises_file_not_found(self, tmp_path: Path) -> None:
        """Contract: raises FileNotFoundError if config doesn't exist."""
        # Setup: No config file
        assert not (tmp_path / ".pantheon" / "quality-config.json").exists()

        # Execute & Verify
        with pytest.raises(FileNotFoundError):
            load_quality_config(tmp_path)

    def test_load_invalid_json_raises_value_error(self, tmp_path: Path) -> None:
        """Contract: raises ValueError for invalid JSON."""
        # Setup: Create invalid JSON file
        (tmp_path / ".pantheon").mkdir()
        config_path = tmp_path / ".pantheon" / "quality-config.json"
        config_path.write_text("{ invalid json }")

        # Execute & Verify
        with pytest.raises(ValueError, match="JSON"):
            load_quality_config(tmp_path)

    def test_load_missing_required_fields_raises_value_error(
        self, tmp_path: Path
    ) -> None:
        """Contract: raises ValueError for missing required fields."""
        # Setup: Create config with missing fields
        (tmp_path / ".pantheon").mkdir()
        config_path = tmp_path / ".pantheon" / "quality-config.json"
        config_path.write_text(json.dumps({"version": "1.0"}))  # Missing other fields

        # Execute & Verify
        with pytest.raises(ValueError, match="required"):
            load_quality_config(tmp_path)


class TestValidateQualityConfig:
    """Contract tests for validate_quality_config function."""

    def test_validate_valid_config_returns_true(self) -> None:
        """Contract: returns True for valid config."""
        # Setup: Valid config
        config = {
            "version": "1.0",
            "project_type": "python",
            "commands": {
                "test": "pytest",
                "lint": "ruff check",
                "type_check": "mypy",
                "coverage": "pytest --cov",
                "build": "python -m build",
            },
            "thresholds": {"coverage_branches": 80, "coverage_statements": 80},
            "discovery_source": "auto",
        }

        # Execute
        result = validate_quality_config(config)

        # Verify
        assert result is True

    def test_validate_missing_version_returns_false(self) -> None:
        """Contract: returns False for missing version."""
        # Setup
        config = {
            "project_type": "python",
            "commands": {},
            "thresholds": {},
        }

        # Execute
        result = validate_quality_config(config)

        # Verify
        assert result is False

    def test_validate_missing_commands_returns_false(self) -> None:
        """Contract: returns False for missing commands."""
        # Setup
        config = {
            "version": "1.0",
            "project_type": "python",
            "thresholds": {},
        }

        # Execute
        result = validate_quality_config(config)

        # Verify
        assert result is False

    def test_validate_missing_thresholds_returns_false(self) -> None:
        """Contract: returns False for missing thresholds."""
        # Setup
        config = {
            "version": "1.0",
            "project_type": "python",
            "commands": {},
        }

        # Execute
        result = validate_quality_config(config)

        # Verify
        assert result is False

    def test_validate_invalid_threshold_value_returns_false(self) -> None:
        """Contract: returns False for threshold value > 100."""
        # Setup
        config = {
            "version": "1.0",
            "project_type": "python",
            "commands": {},
            "thresholds": {"coverage_branches": 150},  # Invalid
        }

        # Execute
        result = validate_quality_config(config)

        # Verify
        assert result is False

    def test_validate_negative_threshold_returns_false(self) -> None:
        """Contract: returns False for negative threshold."""
        # Setup
        config = {
            "version": "1.0",
            "project_type": "python",
            "commands": {},
            "thresholds": {"coverage_branches": -10},  # Invalid
        }

        # Execute
        result = validate_quality_config(config)

        # Verify
        assert result is False

    def test_validate_non_dict_commands_returns_false(self) -> None:
        """Contract: returns False for non-dict commands."""
        # Setup
        config = {
            "version": "1.0",
            "project_type": "python",
            "commands": "not a dict",  # Invalid type
            "thresholds": {},
        }

        # Execute
        result = validate_quality_config(config)

        # Verify
        assert result is False

    def test_validate_does_not_raise_exceptions(self) -> None:
        """Contract: never raises exceptions, always returns bool."""
        # Setup: Various invalid configs
        invalid_configs = [
            {},  # Empty
            {"version": "1.0"},  # Incomplete
            None,  # Wrong type
            {"commands": []},  # Wrong types
        ]

        # Execute & Verify: No exceptions raised
        for config in invalid_configs:
            result = validate_quality_config(config)  # type: ignore
            assert isinstance(result, bool)
            assert result is False
