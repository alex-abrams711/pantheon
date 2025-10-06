"""End-to-end integration tests for quality discovery workflow.

Tests the complete quality discovery and config generation flow across
different project types and scenarios from quickstart.md.
"""

import json
import tempfile
from pathlib import Path

from pantheon.quality.config import generate_quality_config, load_quality_config
from pantheon.quality.discovery import discover_quality_commands


class TestQualityDiscoveryE2E:
    """End-to-end tests for quality discovery workflow."""

    def test_python_project_with_explicit_plan(self) -> None:
        """Test discovery with Python project and explicit plan.md commands."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)

            # Create Python project structure
            (project_root / "pyproject.toml").write_text(
                "[tool.poetry]\nname = 'test'\n"
            )

            # Create specs directory with plan.md
            specs_dir = project_root / "specs" / "feature"
            specs_dir.mkdir(parents=True)
            plan_path = specs_dir / "plan.md"
            plan_path.write_text(
                """
## Quality Standards

- Test command: pytest tests/ -v
- Lint command: ruff check src/ tests/
- Type command: mypy src/ --strict
- Coverage: 85%
"""
            )

            # Generate quality config
            config_path = generate_quality_config(
                project_root, plan_path, coverage_threshold=85
            )

            # Verify config created
            assert config_path.exists()
            assert config_path == project_root / ".pantheon" / "quality-config.json"

            # Load and validate config
            config = load_quality_config(project_root)

            assert config["version"] == "1.0"
            assert config["project_type"] == "python"
            assert config["discovery_source"] == "plan.md"
            assert config["commands"]["test"] == "pytest tests/ -v"
            assert config["commands"]["lint"] == "ruff check src/ tests/"
            assert config["commands"]["type_check"] == "mypy src/ --strict"
            assert config["thresholds"]["coverage_branches"] == 85

    def test_nodejs_project_auto_discovery(self) -> None:
        """Test auto-discovery with Node.js project (no plan.md)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)

            # Create Node.js project structure
            package_json = {
                "name": "test-project",
                "scripts": {
                    "test": "jest",
                    "lint": "eslint .",
                    "type-check": "tsc --noEmit",
                    "build": "webpack",
                },
            }
            (project_root / "package.json").write_text(json.dumps(package_json))

            # Generate quality config (no plan.md)
            config_path = generate_quality_config(project_root)

            # Verify config created
            assert config_path.exists()

            # Load and validate config
            config = load_quality_config(project_root)

            assert config["version"] == "1.0"
            assert config["project_type"] == "node"
            assert config["discovery_source"] == "auto"
            assert config["commands"]["test"] == "npm test"
            assert config["commands"]["lint"] == "npm run lint"
            assert config["commands"]["type_check"] == "npm run type-check"
            assert config["commands"]["build"] == "npm run build"

    def test_go_project_auto_discovery(self) -> None:
        """Test auto-discovery with Go project (no plan.md)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)

            # Create Go project structure
            (project_root / "go.mod").write_text("module test\n\ngo 1.21\n")
            (project_root / "main.go").write_text('package main\n\nfunc main() {}\n')

            # Generate quality config
            config_path = generate_quality_config(project_root)

            # Verify config created
            assert config_path.exists()

            # Load and validate config
            config = load_quality_config(project_root)

            assert config["version"] == "1.0"
            assert config["project_type"] == "go"
            assert config["discovery_source"] == "auto"
            assert config["commands"]["test"] == "go test ./..."
            assert config["commands"]["lint"] == "golangci-lint run"
            assert config["commands"]["build"] == "go build"

    def test_unknown_project_type_empty_commands(self) -> None:
        """Test that unknown project types get empty commands."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)

            # Empty directory (no recognizable project files)
            # Just create a random file
            (project_root / "README.md").write_text("# Test Project\n")

            # Generate quality config
            config_path = generate_quality_config(project_root)

            # Verify config created
            assert config_path.exists()

            # Load and validate config
            config = load_quality_config(project_root)

            assert config["version"] == "1.0"
            assert config["project_type"] == "other"
            assert config["discovery_source"] == "auto"
            # Commands should be empty strings
            assert config["commands"]["test"] == ""
            assert config["commands"]["lint"] == ""
            assert config["commands"]["type_check"] == ""

    def test_discovery_preserves_existing_config(self) -> None:
        """Test that regenerating config preserves manual customizations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)

            # Create Python project
            (project_root / "pyproject.toml").write_text(
                "[tool.poetry]\nname = 'test'\n"
            )

            # Generate initial config
            first_config_path = generate_quality_config(project_root)
            assert first_config_path.exists()

            # Load initial config
            initial_config = load_quality_config(project_root)
            initial_test_cmd = initial_config["commands"]["test"]

            # Generate config again (should use existing)
            second_config_path = generate_quality_config(project_root)

            # Load second config
            second_config = load_quality_config(project_root)

            # Should have same test command
            assert second_config["commands"]["test"] == initial_test_cmd
            assert first_config_path == second_config_path

    def test_complete_workflow_multiple_project_types(self) -> None:
        """Test complete workflow across Python, Node, and Go projects."""
        project_types = [
            ("python", "pyproject.toml", "[tool.poetry]\nname = 'test'\n"),
            (
                "node",
                "package.json",
                json.dumps({"name": "test", "scripts": {"test": "jest"}}),
            ),
            ("go", "go.mod", "module test\n\ngo 1.21\n"),
        ]

        for expected_type, filename, content in project_types:
            with tempfile.TemporaryDirectory() as tmpdir:
                project_root = Path(tmpdir)

                # Create project file
                (project_root / filename).write_text(content)

                # Discover commands
                commands = discover_quality_commands(project_root)
                assert isinstance(commands, dict)

                # Generate config
                config_path = generate_quality_config(project_root)
                assert config_path.exists()

                # Load and verify
                config = load_quality_config(project_root)
                assert config["project_type"] == expected_type
                assert config["version"] == "1.0"
                assert "commands" in config
                assert "thresholds" in config


class TestQualityConfigJSONStructure:
    """Test that generated configs match expected JSON structure."""

    def test_config_has_all_required_fields(self) -> None:
        """Test that config JSON has all required fields."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            (project_root / "pyproject.toml").write_text(
                "[tool.poetry]\nname = 'test'\n"
            )

            generate_quality_config(project_root)
            config = load_quality_config(project_root)

            # Check required top-level fields
            required_fields = [
                "version",
                "project_type",
                "commands",
                "thresholds",
                "discovery_source",
            ]
            for field in required_fields:
                assert field in config, f"Missing required field: {field}"

            # Check commands structure
            command_keys = ["test", "lint", "type_check", "build", "coverage"]
            for key in command_keys:
                assert key in config["commands"], f"Missing command: {key}"

            # Check thresholds structure
            threshold_keys = ["coverage_branches", "coverage_statements"]
            for key in threshold_keys:
                assert key in config["thresholds"], f"Missing threshold: {key}"

    def test_config_json_is_valid_and_parseable(self) -> None:
        """Test that config JSON is valid and can be parsed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            (project_root / "pyproject.toml").write_text(
                "[tool.poetry]\nname = 'test'\n"
            )

            config_path = generate_quality_config(project_root)

            # Read raw JSON and parse
            raw_json = config_path.read_text()
            parsed = json.loads(raw_json)

            # Should be a dictionary
            assert isinstance(parsed, dict)

            # Should have expected structure
            assert "version" in parsed
            assert "commands" in parsed
            assert isinstance(parsed["commands"], dict)
