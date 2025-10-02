"""Unit tests for Spec Kit integration utilities."""

import os
from pathlib import Path

from pantheon.integrations.spec_kit import (
    create_backup,
    find_latest_backup,
    restore_files,
    validate_integration,
    verify_agents_installed,
    verify_spec_kit,
)


class TestVerifyAgentsInstalled:
    """Tests for verify_agents_installed function."""

    def test_agents_installed(self, mock_claude_dir: Path):
        """Test when DEV agent is installed."""
        dev_file = mock_claude_dir / "agents" / "dev.md"
        dev_file.write_text("# DEV Agent")

        os.chdir(mock_claude_dir.parent)
        assert verify_agents_installed() is True

    def test_agents_not_installed_missing_directory(self, temp_dir: Path):
        """Test when .claude/agents directory doesn't exist."""
        os.chdir(temp_dir)
        assert verify_agents_installed() is False

    def test_agents_not_installed_missing_file(self, mock_claude_dir: Path):
        """Test when .claude/agents exists but dev.md doesn't."""
        os.chdir(mock_claude_dir.parent)
        assert verify_agents_installed() is False


class TestVerifySpecKit:
    """Tests for verify_spec_kit function."""

    def test_spec_kit_installed(self, mock_spec_kit_project: Path):
        """Test when Spec Kit is fully installed."""
        os.chdir(mock_spec_kit_project)
        assert verify_spec_kit() is True

    def test_spec_kit_missing_specify(self, mock_claude_dir: Path):
        """Test when .specify directory is missing."""
        os.chdir(mock_claude_dir.parent)
        assert verify_spec_kit() is False

    def test_spec_kit_missing_commands(self, mock_specify_dir: Path):
        """Test when .claude/commands directory is missing."""
        os.chdir(mock_specify_dir.parent)
        assert verify_spec_kit() is False


class TestCreateBackup:
    """Tests for create_backup function."""

    def test_backup_creation(self, mock_spec_kit_project: Path):
        """Test backup directory creation with files."""
        os.chdir(mock_spec_kit_project)

        backup_dir = create_backup()

        assert backup_dir.exists()
        assert backup_dir.name.startswith(".integration-backup-")
        assert (backup_dir / "implement.md").exists()
        assert (backup_dir / "plan.md").exists()
        assert (backup_dir / "tasks.md").exists()

    def test_backup_preserves_content(self, mock_spec_kit_project: Path):
        """Test that backup preserves file content."""
        os.chdir(mock_spec_kit_project)

        original_content = (
            Path(".claude/commands/implement.md").read_text()
        )

        backup_dir = create_backup()
        backup_content = (backup_dir / "implement.md").read_text()

        assert backup_content == original_content

    def test_backup_missing_commands_dir(self, temp_dir: Path):
        """Test backup when commands directory doesn't exist."""
        os.chdir(temp_dir)

        # Should succeed but create empty backup since files don't exist
        backup_dir = create_backup()
        assert backup_dir.exists()


class TestFindLatestBackup:
    """Tests for find_latest_backup function."""

    def test_find_single_backup(self, temp_dir: Path):
        """Test finding a single backup."""
        os.chdir(temp_dir)

        backup = temp_dir / ".integration-backup-20240101-120000"
        backup.mkdir()

        found = find_latest_backup()
        assert found.resolve() == backup.resolve()

    def test_find_latest_of_multiple(self, temp_dir: Path):
        """Test finding the latest of multiple backups."""
        os.chdir(temp_dir)

        old_backup = temp_dir / ".integration-backup-20240101-120000"
        old_backup.mkdir()

        new_backup = temp_dir / ".integration-backup-20241231-235959"
        new_backup.mkdir()

        found = find_latest_backup()
        assert found.resolve() == new_backup.resolve()

    def test_no_backup_found(self, temp_dir: Path):
        """Test when no backup exists."""
        os.chdir(temp_dir)

        found = find_latest_backup()
        assert found is None


class TestRestoreFiles:
    """Tests for restore_files function."""

    def test_restore_files(self, mock_spec_kit_project: Path):
        """Test restoring files from backup."""
        os.chdir(mock_spec_kit_project)

        # Create backup
        backup_dir = create_backup()

        # Modify original files
        commands_dir = Path(".claude/commands")
        (commands_dir / "implement.md").write_text("MODIFIED")

        # Restore
        restore_files(backup_dir)

        # Verify restoration
        restored_content = (commands_dir / "implement.md").read_text()
        assert "MODIFIED" not in restored_content
        assert "Execute the implementation plan by processing tasks" in restored_content

    def test_restore_missing_backup(self, temp_dir: Path):
        """Test restore with missing backup directory."""
        os.chdir(temp_dir)

        fake_backup = temp_dir / "nonexistent-backup"

        result = restore_files(fake_backup)
        assert result["success"] is False
        assert any("not found" in err for err in result["errors"])


class TestValidateIntegration:
    """Tests for validate_integration function."""

    def test_validate_successful_integration(
        self, mock_spec_kit_project: Path
    ):
        """Test validation of successfully integrated files."""
        os.chdir(mock_spec_kit_project)

        # Add correct integration markers
        commands_dir = Path(".claude/commands")

        impl_file = commands_dir / "implement.md"
        impl_file.write_text(
            impl_file.read_text() + "\n## Agent Integration\nContent\n"
        )

        plan_file = commands_dir / "plan.md"
        plan_content = (
            plan_file.read_text()
            + "\n## Quality Standards (Required for DEV Integration)\nContent\n"
        )
        plan_file.write_text(plan_content)

        tasks_file = commands_dir / "tasks.md"
        tasks_content = (
            tasks_file.read_text()
            + "\n## Task Format (Required for DEV Integration)\nContent\n"
        )
        tasks_file.write_text(tasks_content)

        result = validate_integration()
        assert result["valid"] is True

    def test_validate_missing_markers(self, mock_spec_kit_project: Path):
        """Test validation when integration markers are missing."""
        os.chdir(mock_spec_kit_project)

        # Don't add markers - original files
        result = validate_integration()
        assert result["valid"] is False

    def test_validate_missing_files(self, temp_dir: Path):
        """Test validation when command files don't exist."""
        os.chdir(temp_dir)

        result = validate_integration()
        assert result["valid"] is False
