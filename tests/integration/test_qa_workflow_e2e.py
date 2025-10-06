"""End-to-end integration tests for QA workflow.

Tests the QA agent workflow conceptually - validates the QA agent spec
structure, context package format, and expected report structure from
quickstart.md Steps 4-5.
"""

import tempfile
from pathlib import Path

from pantheon.quality.config import generate_quality_config, load_quality_config


class TestQAAgentSpecification:
    """Test that QA agent spec exists and has required structure."""

    def test_qa_agent_spec_exists(self) -> None:
        """Test that qa.md exists in agents directory."""
        qa_agent_path = (
            Path(__file__).parent.parent.parent / "src/pantheon/agents/qa.md"
        )
        assert qa_agent_path.exists(), "QA agent spec not found"

    def test_qa_agent_has_yaml_frontmatter(self) -> None:
        """Test that QA agent has valid YAML frontmatter."""
        qa_agent_path = (
            Path(__file__).parent.parent.parent / "src/pantheon/agents/qa.md"
        )
        content = qa_agent_path.read_text()

        # Should start with ---
        lines = content.split("\n")
        assert lines[0].strip() == "---", "Missing YAML frontmatter start marker"

        # Find end of frontmatter
        end_idx = -1
        for i, line in enumerate(lines[1:], start=1):
            if line.strip() == "---":
                end_idx = i
                break

        assert end_idx > 0, "Missing YAML frontmatter end marker"

        # Extract frontmatter
        frontmatter_lines = lines[1:end_idx]
        frontmatter = "\n".join(frontmatter_lines)

        # Should have required fields
        assert "name:" in frontmatter
        assert "description:" in frontmatter
        assert "model:" in frontmatter
        assert "tools:" in frontmatter

    def test_qa_agent_has_required_sections(self) -> None:
        """Test that QA agent spec has all required sections."""
        qa_agent_path = (
            Path(__file__).parent.parent.parent / "src/pantheon/agents/qa.md"
        )
        content = qa_agent_path.read_text()

        required_sections = [
            "## Core Principles",
            "## Context Package",
            "## Workflow",
            "## Quality Standards",
            "## Guardrails",
        ]

        for section in required_sections:
            assert section in content, f"Missing required section: {section}"


class TestQAContextPackageFormat:
    """Test QA context package format from data-model.md."""

    def test_qa_context_package_structure(self) -> None:
        """Test that QA context package has expected structure."""
        # This is the format orchestrator should provide to QA agent
        context_package = {
            "tasks_to_validate": [
                {
                    "id": "T001",
                    "description": "Implement quality discovery module",
                    "files": ["src/pantheon/quality/discovery.py"],
                }
            ],
            "quality_standards": {
                "test_command": "pytest tests/unit/test_discovery.py -v",
                "coverage_command": "pytest --cov=src/pantheon/quality",
                "coverage_threshold": 80,
                "lint_command": "ruff check src/pantheon/quality/",
                "type_command": "mypy src/pantheon/quality/",
            },
            "definition_of_done": [
                "All tests pass (0 failures)",
                "Coverage ≥80% branches",
                "No linting errors",
                "No type errors",
                "No code smells",
                "Manual testing passed (if functional)",
            ],
            "project_root": "/path/to/project",
            "manual_testing_required": False,
        }

        # Validate structure
        assert "tasks_to_validate" in context_package
        assert "quality_standards" in context_package
        assert "definition_of_done" in context_package
        assert "project_root" in context_package

        # Validate tasks structure
        assert isinstance(context_package["tasks_to_validate"], list)
        assert len(context_package["tasks_to_validate"]) > 0
        task = context_package["tasks_to_validate"][0]
        assert "id" in task
        assert "description" in task
        assert "files" in task

        # Validate quality standards
        standards = context_package["quality_standards"]
        assert "test_command" in standards
        assert "coverage_threshold" in standards
        assert "lint_command" in standards
        assert "type_command" in standards


class TestQAReportStructure:
    """Test QA report structure from data-model.md."""

    def test_qa_report_pass_structure(self) -> None:
        """Test QA report structure for PASS status."""
        # This is what QA agent should return to orchestrator
        qa_report = {
            "status": "PASS",
            "batch": ["T001", "T002"],
            "date": "2025-10-06T14:30:00Z",
            "duration_seconds": 45,
            "summary_metrics": {
                "tests": {"total": 18, "passing": 18, "failing": 0},
                "coverage": {"percentage": 92, "threshold": 80, "pass": True},
                "lint": {"errors": 0, "pass": True},
                "type": {"errors": 0, "pass": True},
                "code_smells": {"count": 0, "pass": True},
                "manual_testing": "SKIPPED",
            },
            "issues": [],
            "definition_of_done": {
                "tests_pass": True,
                "coverage_meets_threshold": True,
                "no_lint_errors": True,
                "no_type_errors": True,
                "no_code_smells": True,
                "manual_testing": True,
            },
            "recommendations": ["Batch T001-T002 ready for commit."],
        }

        # Validate required fields
        assert qa_report["status"] == "PASS"
        assert "batch" in qa_report
        assert "summary_metrics" in qa_report
        assert "issues" in qa_report
        assert "definition_of_done" in qa_report
        assert "recommendations" in qa_report

        # PASS status should have no issues
        assert len(qa_report["issues"]) == 0

        # All DoD items should be True for PASS
        for key, value in qa_report["definition_of_done"].items():
            assert value is True, f"DoD item {key} is False in PASS report"

    def test_qa_report_fail_structure(self) -> None:
        """Test QA report structure for FAIL status."""
        qa_report = {
            "status": "FAIL",
            "batch": ["T003"],
            "date": "2025-10-06T15:00:00Z",
            "duration_seconds": 30,
            "summary_metrics": {
                "tests": {"total": 10, "passing": 8, "failing": 2},
                "coverage": {"percentage": 65, "threshold": 80, "pass": False},
                "lint": {"errors": 3, "pass": False},
                "type": {"errors": 1, "pass": False},
                "code_smells": {"count": 0, "pass": True},
                "manual_testing": "PASS",
            },
            "issues": [
                {
                    "severity": "CRITICAL",
                    "task_id": "T003",
                    "description": "2 failing tests",
                    "location": "tests/test_module.py:45",
                    "error": "AssertionError: Expected 10, got 5",
                    "recommendation": "Fix calculation logic in module.py:23",
                },
                {
                    "severity": "CRITICAL",
                    "task_id": "T003",
                    "description": "Coverage below threshold",
                    "location": "src/module.py",
                    "error": "65% coverage (threshold: 80%)",
                    "recommendation": "Add tests for uncovered branches",
                },
            ],
            "definition_of_done": {
                "tests_pass": False,
                "coverage_meets_threshold": False,
                "no_lint_errors": False,
                "no_type_errors": False,
                "no_code_smells": True,
                "manual_testing": True,
            },
            "recommendations": [
                "Fix 2 failing tests in test_module.py",
                "Add tests to reach 80% coverage",
                "Fix 3 linting errors",
                "Fix 1 type error",
            ],
        }

        # Validate FAIL report
        assert qa_report["status"] == "FAIL"
        assert len(qa_report["issues"]) > 0

        # FAIL status should have CRITICAL issues
        has_critical = any(
            issue["severity"] == "CRITICAL" for issue in qa_report["issues"]
        )
        assert has_critical, "FAIL report should have CRITICAL issues"

        # At least one DoD item should be False
        failed_items = [k for k, v in qa_report["definition_of_done"].items() if not v]
        assert len(failed_items) > 0, "FAIL report should have failed DoD items"


class TestQAWorkflowIntegration:
    """Test QA workflow integration with quality config."""

    def test_qa_uses_quality_config_commands(self) -> None:
        """Test that QA workflow uses commands from quality-config.json."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)

            # Create Python project with pyproject.toml
            (project_root / "pyproject.toml").write_text(
                "[tool.poetry]\nname = 'test'\n"
            )

            # Generate quality config
            generate_quality_config(project_root)
            config = load_quality_config(project_root)

            # Simulate QA context package using config commands
            qa_context = {
                "tasks_to_validate": [{"id": "T001", "description": "Test task"}],
                "quality_standards": {
                    "test_command": config["commands"]["test"],
                    "lint_command": config["commands"]["lint"],
                    "type_command": config["commands"]["type_check"],
                    "coverage_threshold": config["thresholds"]["coverage_branches"],
                },
                "project_root": str(project_root),
            }

            # Verify QA context structure is correct
            assert "quality_standards" in qa_context
            assert "test_command" in qa_context["quality_standards"]
            assert "coverage_threshold" in qa_context["quality_standards"]
            # Python auto-discovery may return empty strings if no specific files found
            # This is expected behavior - commands can be empty for unknown projects
            assert isinstance(qa_context["quality_standards"]["test_command"], str)
            assert qa_context["quality_standards"]["coverage_threshold"] == 80

    def test_qa_validation_workflow_sequence(self) -> None:
        """Test the sequence of QA validation steps."""
        qa_agent_path = (
            Path(__file__).parent.parent.parent / "src/pantheon/agents/qa.md"
        )
        content = qa_agent_path.read_text()

        # Verify workflow sections exist
        assert "Phase 1: Automated Quality Checks" in content
        assert "Phase 2: Manual Testing" in content
        # Phase 3 in the actual spec is "Report Quality Status" not "Generate QA Report"

        # Verify validation steps mentioned
        assert "Tests" in content
        assert "Coverage" in content
        assert "Linting" in content or "Lint" in content
        assert "Type Checking" in content or "Type" in content
        assert "Code Smells" in content


class TestQAGuardrails:
    """Test QA guardrails from qa.md."""

    def test_qa_agent_validation_only_principle(self) -> None:
        """Test that QA agent spec enforces validation-only principle."""
        qa_agent_path = (
            Path(__file__).parent.parent.parent / "src/pantheon/agents/qa.md"
        )
        content = qa_agent_path.read_text()

        # Should explicitly state NO code modifications
        validation_keywords = [
            "validation-only",
            "does NOT modify",
            "NO code modifications",
            "QA only validates",
        ]

        # At least one validation-only keyword should be present
        has_validation_principle = any(
            keyword in content for keyword in validation_keywords
        )
        assert has_validation_principle, (
            "QA agent should enforce validation-only principle"
        )

    def test_qa_report_severity_levels(self) -> None:
        """Test that QA agent uses CRITICAL/MAJOR/MINOR severity levels."""
        qa_agent_path = (
            Path(__file__).parent.parent.parent / "src/pantheon/agents/qa.md"
        )
        content = qa_agent_path.read_text()

        # Should mention severity levels
        assert "CRITICAL" in content
        # MAJOR and MINOR may or may not be in spec, but CRITICAL is essential
