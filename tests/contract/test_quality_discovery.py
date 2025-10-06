"""Contract tests for quality discovery API.

These tests define the contract for src/pantheon/quality/discovery.py
Tests MUST FAIL until implementation is complete (TDD approach).
"""

import json
from pathlib import Path

import pytest

from pantheon.quality.discovery import (
    detect_project_type,
    discover_quality_commands,
    parse_plan_quality_commands,
)


class TestDiscoverQualityCommands:
    """Contract tests for discover_quality_commands function."""

    def test_discover_with_plan_md_explicit_commands(self, tmp_path: Path) -> None:
        """Contract: explicit plan.md commands take precedence over auto-discovery."""
        # Setup: Create project with plan.md containing explicit commands
        plan_path = tmp_path / "plan.md"
        plan_content = """
# Implementation Plan

## Quality Standards
- Test command: custom-test-command
- Lint command: custom-lint-command
- Type command: custom-type-command
- Coverage command: custom-coverage-command
- Build command: custom-build-command
"""
        plan_path.write_text(plan_content)

        # Execute
        result = discover_quality_commands(tmp_path, plan_path)

        # Verify: Explicit commands from plan.md are used
        assert result["test"] == "custom-test-command"
        assert result["lint"] == "custom-lint-command"
        assert result["type_check"] == "custom-type-command"
        assert result["coverage"] == "custom-coverage-command"
        assert result["build"] == "custom-build-command"

    def test_discover_node_project_auto_discovery(self, tmp_path: Path) -> None:
        """Contract: Node.js project auto-discovery from package.json."""
        # Setup: Create Node.js project with package.json
        package_json = tmp_path / "package.json"
        package_json.write_text(
            json.dumps(
                {
                    "name": "test-project",
                    "scripts": {
                        "test": "jest",
                        "lint": "eslint .",
                        "build": "tsc",
                    },
                }
            )
        )

        # Execute
        result = discover_quality_commands(tmp_path)

        # Verify: Commands discovered from package.json scripts
        assert result["test"] == "npm test"
        assert result["lint"] == "npm run lint"
        assert result["build"] == "npm run build"
        assert isinstance(result["type_check"], str)  # May be empty
        assert isinstance(result["coverage"], str)  # May be empty

    def test_discover_python_project_auto_discovery(self, tmp_path: Path) -> None:
        """Contract: Python project auto-discovery from pyproject.toml."""
        # Setup: Create Python project with pyproject.toml
        pyproject_toml = tmp_path / "pyproject.toml"
        pyproject_content = """
[project]
name = "test-project"

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.ruff]
line-length = 100

[tool.mypy]
strict = true
"""
        pyproject_toml.write_text(pyproject_content)

        # Execute
        result = discover_quality_commands(tmp_path)

        # Verify: Commands discovered from pyproject.toml
        assert "pytest" in result["test"]
        assert "ruff" in result["lint"]
        assert "mypy" in result["type_check"]
        assert isinstance(result["coverage"], str)
        assert isinstance(result["build"], str)

    def test_discover_go_project_auto_discovery(self, tmp_path: Path) -> None:
        """Contract: Go project returns standard Go commands."""
        # Setup: Create Go project with go.mod
        go_mod = tmp_path / "go.mod"
        go_mod.write_text("module example.com/test\n\ngo 1.21\n")

        # Execute
        result = discover_quality_commands(tmp_path)

        # Verify: Standard Go commands returned
        assert "go test" in result["test"]
        assert result["build"] == "go build"
        assert isinstance(result["lint"], str)
        assert isinstance(result["type_check"], str)
        assert isinstance(result["coverage"], str)

    def test_discover_unknown_project_returns_empty_commands(
        self, tmp_path: Path
    ) -> None:
        """Contract: unknown project type returns empty commands."""
        # Setup: Empty directory (no recognizable project files)
        # Execute
        result = discover_quality_commands(tmp_path)

        # Verify: All command values are strings (empty for unknown)
        assert isinstance(result["test"], str)
        assert isinstance(result["lint"], str)
        assert isinstance(result["type_check"], str)
        assert isinstance(result["coverage"], str)
        assert isinstance(result["build"], str)
        # All required keys present
        assert len(result) == 5

    def test_discover_invalid_project_root_raises_error(self) -> None:
        """Contract: invalid project_root raises ValueError."""
        # Setup: Non-existent directory
        invalid_path = Path("/nonexistent/invalid/path")

        # Execute & Verify: Raises ValueError
        with pytest.raises(ValueError, match="project_root"):
            discover_quality_commands(invalid_path)


class TestDetectProjectType:
    """Contract tests for detect_project_type function."""

    def test_detect_node_project(self, tmp_path: Path) -> None:
        """Contract: detects Node.js from package.json."""
        # Setup
        (tmp_path / "package.json").write_text("{}")

        # Execute
        result = detect_project_type(tmp_path)

        # Verify
        assert result == "node"

    def test_detect_python_project_from_pyproject(self, tmp_path: Path) -> None:
        """Contract: detects Python from pyproject.toml."""
        # Setup
        (tmp_path / "pyproject.toml").write_text("[project]\n")

        # Execute
        result = detect_project_type(tmp_path)

        # Verify
        assert result == "python"

    def test_detect_python_project_from_setup_py(self, tmp_path: Path) -> None:
        """Contract: detects Python from setup.py."""
        # Setup
        (tmp_path / "setup.py").write_text("# setup\n")

        # Execute
        result = detect_project_type(tmp_path)

        # Verify
        assert result == "python"

    def test_detect_go_project(self, tmp_path: Path) -> None:
        """Contract: detects Go from go.mod."""
        # Setup
        (tmp_path / "go.mod").write_text("module test\n")

        # Execute
        result = detect_project_type(tmp_path)

        # Verify
        assert result == "go"

    def test_detect_ruby_project(self, tmp_path: Path) -> None:
        """Contract: detects Ruby from Gemfile."""
        # Setup
        (tmp_path / "Gemfile").write_text("source 'https://rubygems.org'\n")

        # Execute
        result = detect_project_type(tmp_path)

        # Verify
        assert result == "ruby"

    def test_detect_other_for_empty_directory(self, tmp_path: Path) -> None:
        """Contract: returns 'other' for unrecognized project."""
        # Setup: Empty directory
        # Execute
        result = detect_project_type(tmp_path)

        # Verify
        assert result == "other"


class TestParsePlanQualityCommands:
    """Contract tests for parse_plan_quality_commands function."""

    def test_parse_plan_with_all_commands(self, tmp_path: Path) -> None:
        """Contract: extracts all commands from plan.md Quality Standards section."""
        # Setup
        plan_path = tmp_path / "plan.md"
        plan_content = """
# Plan

## Quality Standards
- Test command: pytest tests/
- Lint command: ruff check src/
- Type command: mypy src/
- Coverage command: pytest --cov=src
- Build command: python -m build
"""
        plan_path.write_text(plan_content)

        # Execute
        result = parse_plan_quality_commands(plan_path)

        # Verify
        assert result["test"] == "pytest tests/"
        assert result["lint"] == "ruff check src/"
        assert result["type_check"] == "mypy src/"
        assert result["coverage"] == "pytest --cov=src"
        assert result["build"] == "python -m build"

    def test_parse_plan_with_partial_commands(self, tmp_path: Path) -> None:
        """Contract: returns only commands present in plan."""
        # Setup
        plan_path = tmp_path / "plan.md"
        plan_content = """
# Plan

## Quality Standards
- Test command: jest
- Lint command: eslint .
"""
        plan_path.write_text(plan_content)

        # Execute
        result = parse_plan_quality_commands(plan_path)

        # Verify: Only specified commands returned
        assert result["test"] == "jest"
        assert result["lint"] == "eslint ."
        assert "type_check" not in result
        assert "coverage" not in result
        assert "build" not in result

    def test_parse_plan_missing_quality_standards_section(
        self, tmp_path: Path
    ) -> None:
        """Contract: returns empty dict if Quality Standards section missing."""
        # Setup
        plan_path = tmp_path / "plan.md"
        plan_content = """
# Plan

## Some Other Section
Content here
"""
        plan_path.write_text(plan_content)

        # Execute
        result = parse_plan_quality_commands(plan_path)

        # Verify
        assert result == {}

    def test_parse_plan_file_not_found_raises_error(self, tmp_path: Path) -> None:
        """Contract: raises FileNotFoundError if plan.md doesn't exist."""
        # Setup
        plan_path = tmp_path / "nonexistent.md"

        # Execute & Verify
        with pytest.raises(FileNotFoundError):
            parse_plan_quality_commands(plan_path)
