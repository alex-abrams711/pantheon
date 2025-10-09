"""Pytest configuration and shared fixtures."""

import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_claude_dir(temp_dir: Path) -> Path:
    """Create a mock .claude directory structure."""
    claude_dir = temp_dir / ".claude"
    claude_dir.mkdir()
    (claude_dir / "agents").mkdir()
    (claude_dir / "commands").mkdir()
    return claude_dir


@pytest.fixture
def mock_specify_dir(temp_dir: Path) -> Path:
    """Create a mock .specify directory for Spec Kit."""
    specify_dir = temp_dir / ".specify"
    specify_dir.mkdir()
    return specify_dir


@pytest.fixture
def mock_spec_kit_project(mock_claude_dir: Path, mock_specify_dir: Path) -> Path:
    """Create a complete mock Spec Kit project with YAML frontmatter."""
    # Create sample command files matching Spec Kit v0.0.55 format
    commands_dir = mock_claude_dir / "commands"

    (commands_dir / "implement.md").write_text(
        "---\n"
        "description: Execute the implementation plan by processing tasks\n"
        "---\n\n"
        "Execute the implementation plan by processing tasks.\n"
    )

    (commands_dir / "plan.md").write_text(
        "---\n"
        "description: Create a detailed implementation plan\n"
        "---\n\n"
        "Create a detailed implementation plan.\n"
    )

    (commands_dir / "tasks.md").write_text(
        "---\n"
        "description: Generate actionable tasks\n"
        "---\n\n"
        "Generate actionable tasks.\n"
    )

    return mock_claude_dir.parent


@pytest.fixture
def mock_spec_kit_project_no_frontmatter(
    mock_claude_dir: Path, mock_specify_dir: Path
) -> Path:
    """Create a mock Spec Kit project without YAML frontmatter (legacy format)."""
    # Create sample command files without frontmatter
    commands_dir = mock_claude_dir / "commands"

    (commands_dir / "implement.md").write_text(
        "# /implement - Execute Implementation Plan\n\n"
        "Execute the implementation plan by processing tasks.\n"
    )

    (commands_dir / "plan.md").write_text(
        "# /plan - Create Implementation Plan\n\n"
        "Create a detailed implementation plan.\n"
    )

    (commands_dir / "tasks.md").write_text(
        "# /tasks - Generate Task List\n\nGenerate actionable tasks.\n"
    )

    return mock_claude_dir.parent


@pytest.fixture
def mock_dev_agent(temp_dir: Path) -> Path:
    """Create a mock DEV agent file."""
    agents_dir = temp_dir / "agents"
    agents_dir.mkdir(exist_ok=True)

    dev_content = """---
name: DEV
description: Senior Software Engineer
model: claude-sonnet-4-5
tools:
  - Read
  - Write
  - Edit
  - Bash
---

## Core Principles
Test content for DEV agent.
"""

    dev_file = agents_dir / "dev.md"
    dev_file.write_text(dev_content)
    return dev_file
