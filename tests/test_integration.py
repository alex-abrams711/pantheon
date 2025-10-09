"""Integration tests for the full workflow."""

import os
import shutil
from pathlib import Path

from pantheon.integrations.spec_kit import (
    create_backup,
    integrate_spec_kit,
    rollback_integration,
)


class TestFullIntegrationWorkflow:
    """Test complete integration workflow."""

    def test_full_integration_cycle(self, mock_spec_kit_project: Path):
        """Test init → integrate → verify → rollback cycle."""
        os.chdir(mock_spec_kit_project)

        # Setup: Copy dev agent
        src_agent = (
            Path(__file__).parent.parent / "src" / "pantheon" / "agents" / "dev.md"
        )
        dst_agent = Path(".claude/agents/dev.md")

        if src_agent.exists():
            shutil.copy(src_agent, dst_agent)
        else:
            # Fallback: create minimal agent
            agent_content = (
                "---\nname: DEV\ndescription: Test\n"
                "model: claude-sonnet-4-5\n---\n# DEV"
            )
            dst_agent.write_text(agent_content)

        # Step 1: Verify initial state
        commands_dir = Path(".claude/commands")
        original_implement = (commands_dir / "implement.md").read_text()

        # Step 2: Integrate
        integrate_spec_kit()

        # Step 3: Verify integration
        integrated_implement = (commands_dir / "implement.md").read_text()
        assert "Agent Integration" in integrated_implement
        assert integrated_implement != original_implement

        # Step 4: Rollback
        rollback_integration()

        # Step 5: Verify rollback
        restored_implement = (commands_dir / "implement.md").read_text()
        assert restored_implement == original_implement
        assert "Agent Integration" not in restored_implement

    def test_idempotent_integration(self, mock_spec_kit_project: Path):
        """Test that running integration twice doesn't duplicate content."""
        os.chdir(mock_spec_kit_project)

        # Setup dev agent
        dst_agent = Path(".claude/agents/dev.md")
        dst_agent.write_text(
            "---\nname: DEV\ndescription: Test\nmodel: claude-sonnet-4-5\n---\n# DEV"
        )

        # First integration
        integrate_spec_kit()
        first_result = Path(".claude/commands/implement.md").read_text()

        # Second integration (should detect existing markers)
        integrate_spec_kit()
        second_result = Path(".claude/commands/implement.md").read_text()

        # Should be identical (no duplicate sections)
        assert first_result == second_result

    def test_integration_with_customized_commands(self, mock_spec_kit_project: Path):
        """Test integration preserves custom content in commands."""
        os.chdir(mock_spec_kit_project)

        # Setup dev agent
        dst_agent = Path(".claude/agents/dev.md")
        dst_agent.write_text(
            "---\nname: DEV\ndescription: Test\nmodel: claude-sonnet-4-5\n---\n# DEV"
        )

        # Add custom content to implement.md
        commands_dir = Path(".claude/commands")
        implement_file = commands_dir / "implement.md"
        custom_content = "\n## My Custom Section\nCustom implementation notes.\n"

        original = implement_file.read_text()
        implement_file.write_text(original + custom_content)

        # Integrate
        integrate_spec_kit()

        # Verify custom content preserved
        integrated = implement_file.read_text()
        assert "My Custom Section" in integrated
        assert "Custom implementation notes" in integrated
        assert "Agent Integration" in integrated


class TestErrorHandling:
    """Test error handling in integration."""

    def test_integration_without_agents(self, mock_spec_kit_project: Path):
        """Test integration fails gracefully without DEV agent."""
        os.chdir(mock_spec_kit_project)

        # Remove dev agent if exists
        dev_agent = Path(".claude/agents/dev.md")
        if dev_agent.exists():
            dev_agent.unlink()

        result = integrate_spec_kit()
        assert result["success"] is False
        assert any("DEV agent" in err for err in result["errors"])

    def test_integration_without_spec_kit(self, temp_dir: Path):
        """Test integration fails gracefully without Spec Kit."""
        os.chdir(temp_dir)

        # Create only .claude/agents
        claude_dir = temp_dir / ".claude"
        claude_dir.mkdir()
        agents_dir = claude_dir / "agents"
        agents_dir.mkdir()

        dev_agent = agents_dir / "dev.md"
        dev_agent.write_text("---\nname: DEV\n---\n# DEV")

        result = integrate_spec_kit()
        assert result["success"] is False
        assert any("Spec Kit" in err for err in result["errors"])

    def test_rollback_without_backup(self, temp_dir: Path):
        """Test rollback fails gracefully without backup."""
        os.chdir(temp_dir)

        result = rollback_integration()
        assert result["success"] is False
        assert any("No backup" in err for err in result["errors"])


class TestBackupManagement:
    """Test backup creation and management."""

    def test_multiple_backups_tracked(self, mock_spec_kit_project: Path):
        """Test that multiple backups can coexist."""
        os.chdir(mock_spec_kit_project)

        # Create multiple backups (need small delay to ensure different timestamps)
        import time

        backup1 = create_backup()
        time.sleep(1)  # Ensure different timestamp
        backup2 = create_backup()

        assert backup1.exists()
        assert backup2.exists()
        assert backup1 != backup2

    def test_backup_includes_all_files(self, mock_spec_kit_project: Path):
        """Test backup includes all required command files."""
        os.chdir(mock_spec_kit_project)

        backup_dir = create_backup()

        required_files = ["implement.md", "plan.md", "tasks.md"]
        for file in required_files:
            assert (backup_dir / file).exists()
            assert (backup_dir / file).stat().st_size > 0


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_integration_without_frontmatter(
        self, mock_spec_kit_project_no_frontmatter: Path
    ):
        """Test integration works with files that have no YAML frontmatter."""
        os.chdir(mock_spec_kit_project_no_frontmatter)

        # Setup dev agent
        dst_agent = Path(".claude/agents/dev.md")
        dst_agent.write_text(
            "---\nname: DEV\ndescription: Test\nmodel: claude-sonnet-4-5\n---\n# DEV"
        )

        # Integrate
        result = integrate_spec_kit()

        # Should succeed
        assert result["success"] is True

        # Verify directives added at beginning of file
        implement_content = Path(".claude/commands/implement.md").read_text()
        assert "## Agent Integration" in implement_content

        # Verify original content preserved
        assert "Execute the implementation plan" in implement_content

    def test_integration_with_malformed_frontmatter(
        self, mock_claude_dir: Path, mock_specify_dir: Path
    ):
        """Test integration handles malformed YAML frontmatter gracefully."""
        project_root = mock_claude_dir.parent
        os.chdir(project_root)

        # Setup dev agent
        dst_agent = Path(".claude/agents/dev.md")
        dst_agent.write_text(
            "---\nname: DEV\ndescription: Test\nmodel: claude-sonnet-4-5\n---\n# DEV"
        )

        # Create command file with malformed frontmatter (missing closing ---)
        commands_dir = mock_claude_dir / "commands"
        (commands_dir / "implement.md").write_text(
            "---\n"
            "description: Execute the implementation plan\n"
            "This is malformed - no closing ---\n\n"
            "Execute the implementation plan.\n"
        )
        (commands_dir / "plan.md").write_text(
            "---\ndescription: Plan\n---\n\nCreate plan.\n"
        )
        (commands_dir / "tasks.md").write_text(
            "---\ndescription: Tasks\n---\n\nCreate tasks.\n"
        )

        # Integrate (should handle malformed frontmatter by inserting at beginning)
        result = integrate_spec_kit()

        # Should succeed (fallback to beginning of file)
        assert result["success"] is True

        # Verify directive added
        implement_content = Path(".claude/commands/implement.md").read_text()
        assert "## Agent Integration" in implement_content
