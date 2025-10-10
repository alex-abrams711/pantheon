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


def test_init_copies_contextualize_command(tmp_path: Path) -> None:
    """Test that 'pantheon init' copies /pantheon:contextualize command."""
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path) as td:
        project_dir = Path(td)

        # Run init command
        result = runner.invoke(main, ["init"])

        # Should succeed
        assert result.exit_code == 0

        # Should create .claude/commands/pantheon/ directory
        pantheon_commands_dir = project_dir / ".claude" / "commands" / "pantheon"
        assert pantheon_commands_dir.exists()
        assert pantheon_commands_dir.is_dir()

        # Should copy contextualize.md
        contextualize_cmd = pantheon_commands_dir / "contextualize.md"
        assert contextualize_cmd.exists(), "contextualize.md should be copied"
        assert (
            contextualize_cmd.stat().st_size > 0
        ), "contextualize.md should have content"

        # Should contain quality report generation logic
        content = contextualize_cmd.read_text()
        assert "quality-report.sh" in content
        assert "quality-config.json" in content

        # Output should mention copying the command
        assert "/pantheon:contextualize" in result.output


def test_init_installs_hooks(tmp_path: Path) -> None:
    """Test that 'pantheon init' installs quality gate hooks."""
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path) as td:
        project_dir = Path(td)

        # Run init command
        result = runner.invoke(main, ["init"])

        # Should succeed
        assert result.exit_code == 0

        # Should create .pantheon/hooks/ directory
        hooks_dir = project_dir / ".pantheon" / "hooks"
        assert hooks_dir.exists(), ".pantheon/hooks/ directory should be created"
        assert hooks_dir.is_dir()

        # Should copy hook scripts
        quality_gate_hook = hooks_dir / "phase-gate.sh"
        orchestrator_gate_hook = hooks_dir / "orchestrator-code-gate.sh"

        assert quality_gate_hook.exists(), "phase-gate.sh should be copied"
        assert (
            orchestrator_gate_hook.exists()
        ), "orchestrator-code-gate.sh should be copied"

        # Hook scripts should be executable
        import stat

        quality_gate_stat = quality_gate_hook.stat()
        orchestrator_gate_stat = orchestrator_gate_hook.stat()

        assert (
            quality_gate_stat.st_mode & stat.S_IXUSR
        ), "phase-gate.sh should be executable"
        assert (
            orchestrator_gate_stat.st_mode & stat.S_IXUSR
        ), "orchestrator-code-gate.sh should be executable"

        # Should update .claude/settings.json with hook configuration
        settings_path = project_dir / ".claude" / "settings.json"
        assert settings_path.exists(), ".claude/settings.json should be created"

        import json

        with open(settings_path) as f:
            settings = json.load(f)

        # Check hooks are configured
        assert "hooks" in settings, "settings.json should have 'hooks' key"
        hooks_config = settings["hooks"]

        # SubagentStop hook for quality gate
        assert "SubagentStop" in hooks_config, "SubagentStop hook should be configured"
        assert isinstance(hooks_config["SubagentStop"], list)

        # PreToolUse hooks for quality gate and orchestrator code gate
        assert "PreToolUse" in hooks_config, "PreToolUse hook should be configured"
        assert isinstance(hooks_config["PreToolUse"], list)

        # Verify hook commands reference correct scripts
        pre_tool_use_matchers = [
            hook.get("matcher") for hook in hooks_config["PreToolUse"]
        ]
        assert "Bash(git commit*)" in pre_tool_use_matchers
        assert "Task" in pre_tool_use_matchers
        assert "Write(*) | Edit(*)" in pre_tool_use_matchers

        # Output should mention hook installation
        assert "Installing quality gate hooks" in result.output
        assert (
            "Quality hooks installed successfully" in result.output
            or "⚠️" in result.output
        )
