"""Integration tests for 'pantheon init' command."""

from pathlib import Path

from click.testing import CliRunner

from pantheon.cli import main


def test_init_copies_both_agents(tmp_path: Path) -> None:
    """Test that 'pantheon init' copies both dev.md and qa.md agents."""
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path) as td:
        project_dir = Path(td)

        # Run init command
        result = runner.invoke(main, ["init"])

        # Should succeed
        assert result.exit_code == 0

        # Should create .claude/agents/ directory
        agents_dir = project_dir / ".claude" / "agents"
        assert agents_dir.exists()
        assert agents_dir.is_dir()

        # Should copy both dev.md and qa.md
        dev_agent = agents_dir / "dev.md"
        qa_agent = agents_dir / "qa.md"

        assert dev_agent.exists(), "dev.md should be copied"
        assert qa_agent.exists(), "qa.md should be copied"

        # Both should be readable files with content
        assert dev_agent.stat().st_size > 0, "dev.md should have content"
        assert qa_agent.stat().st_size > 0, "qa.md should have content"

        # Output should mention both agents
        assert "DEV agent" in result.output
        assert "QA agent" in result.output


def test_init_skips_existing_agents(tmp_path: Path) -> None:
    """Test that 'pantheon init' skips agents that already exist."""
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path) as td:
        project_dir = Path(td)

        # Create .claude/agents/ directory with existing dev.md
        agents_dir = project_dir / ".claude" / "agents"
        agents_dir.mkdir(parents=True)

        existing_dev = agents_dir / "dev.md"
        existing_dev.write_text("# Existing DEV agent\n")

        # Run init command
        result = runner.invoke(main, ["init"])

        # Should succeed
        assert result.exit_code == 0

        # dev.md should be unchanged (not overwritten)
        assert existing_dev.read_text() == "# Existing DEV agent\n"

        # qa.md should still be copied
        qa_agent = agents_dir / "qa.md"
        assert qa_agent.exists()
        assert qa_agent.stat().st_size > 0

        # Output should mention skipping dev.md
        assert "already exists (skipping)" in result.output
        assert "dev.md" in result.output


def test_init_creates_claude_directory(tmp_path: Path) -> None:
    """Test that 'pantheon init' creates .claude/ directory if missing."""
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path) as td:
        project_dir = Path(td)

        # Run init without .claude/ directory
        result = runner.invoke(main, ["init"])

        # Should succeed
        assert result.exit_code == 0

        # Should create .claude/ directory
        claude_dir = project_dir / ".claude"
        assert claude_dir.exists()
        assert claude_dir.is_dir()

        # Output should mention creating it
        assert "Created .claude" in result.output


def test_init_with_auto_integrate_skips_prompt(tmp_path: Path) -> None:
    """Test that 'pantheon init --auto-integrate' skips Spec Kit prompt."""
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path) as td:
        project_dir = Path(td)

        # Create .specify/ and .claude/commands/ to simulate Spec Kit
        (project_dir / ".specify").mkdir()
        commands_dir = project_dir / ".claude" / "commands"
        commands_dir.mkdir(parents=True)

        # Create minimal Spec Kit command files
        (commands_dir / "implement.md").write_text("# /implement\n")
        (commands_dir / "plan.md").write_text("# /plan\n")
        (commands_dir / "tasks.md").write_text("# /tasks\n")

        # Run init with --auto-integrate
        result = runner.invoke(main, ["init", "--auto-integrate"])

        # Should succeed
        assert result.exit_code == 0

        # Should detect Spec Kit
        assert "Spec Kit detected" in result.output

        # Should not prompt user (auto-integrate)
        assert "Would you like to integrate" not in result.output


def test_init_agent_files_have_yaml_frontmatter(tmp_path: Path) -> None:
    """Test that copied agent files contain valid YAML frontmatter."""
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path) as td:
        project_dir = Path(td)

        # Run init command
        result = runner.invoke(main, ["init"])
        assert result.exit_code == 0

        agents_dir = project_dir / ".claude" / "agents"

        # Read agent files
        dev_content = (agents_dir / "dev.md").read_text()
        qa_content = (agents_dir / "qa.md").read_text()

        # Both should start with YAML frontmatter
        assert dev_content.startswith("---\n"), "dev.md should have YAML frontmatter"
        assert qa_content.startswith("---\n"), "qa.md should have YAML frontmatter"

        # Should contain required frontmatter fields
        assert "name:" in dev_content
        assert "description:" in dev_content
        assert "tools:" in dev_content

        assert "name:" in qa_content
        assert "description:" in qa_content
        assert "tools:" in qa_content
