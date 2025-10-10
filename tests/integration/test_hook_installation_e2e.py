"""End-to-end integration tests for hook installation workflow.

Tests the complete hook installation, validation, and rollback flow
as described in quickstart.md Step 2.
"""

import json
import os
import tempfile
from pathlib import Path

from pantheon.hooks import (
    install_hooks,
    validate_hook_installation,
)


class TestHookInstallationE2E:
    """End-to-end tests for hook installation workflow."""

    def test_full_install_workflow(self) -> None:
        """Test complete hook installation workflow from quickstart.md."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)

            # Create .claude/ directory (prerequisite)
            claude_dir = project_root / ".claude"
            claude_dir.mkdir()

            # Install hooks
            result = install_hooks(project_root)

            # Verify both hooks installed successfully
            assert result["QualityGate"] is True
            assert result["OrchestratorCodeGate"] is True

            # Verify .pantheon/hooks/ directory created with 2 scripts
            hooks_dir = project_root / ".pantheon" / "hooks"
            assert hooks_dir.exists()
            assert hooks_dir.is_dir()

            expected_scripts = [
                "phase-gate.sh",
                "orchestrator-code-gate.sh",
            ]
            for script in expected_scripts:
                script_path = hooks_dir / script
                assert script_path.exists(), f"Missing script: {script}"
                assert script_path.is_file()

            # Verify all scripts are executable
            for script in expected_scripts:
                script_path = hooks_dir / script
                assert os.access(
                    script_path, os.X_OK
                ), f"Script not executable: {script}"

            # Verify .claude/settings.json updated with hook configuration
            settings_path = claude_dir / "settings.json"
            assert settings_path.exists()

            with open(settings_path) as f:
                settings = json.load(f)

            assert "hooks" in settings
            assert "SubagentStop" in settings["hooks"]
            assert "PreToolUse" in settings["hooks"]

            # Verify hook paths are correct
            subagent_hooks = settings["hooks"]["SubagentStop"]
            pretool_hooks = settings["hooks"]["PreToolUse"]
            assert any("phase-gate.sh" in str(h) for h in subagent_hooks)
            assert any("phase-gate.sh" in str(h) for h in pretool_hooks)
            assert any("orchestrator-code-gate.sh" in str(h) for h in pretool_hooks)

    def test_hook_validation_success(self) -> None:
        """Test hook validation after successful installation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            claude_dir = project_root / ".claude"
            claude_dir.mkdir()

            # Install hooks
            install_hooks(project_root)

            # Validate installation
            validation = validate_hook_installation(project_root)

            # All hooks should validate as OK (phase-gate used in multiple places)
            assert validation["QualityGate-SubagentStop"] == "OK"
            assert validation["QualityGate-PreCommit"] == "OK"
            assert validation["QualityGate-Task"] == "OK"
            assert validation["OrchestratorCodeGate"] == "OK"

    def test_install_with_existing_settings_json(self) -> None:
        """Test that installation preserves existing settings.json content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            claude_dir = project_root / ".claude"
            claude_dir.mkdir()

            # Create settings.json with existing content
            settings_path = claude_dir / "settings.json"
            existing_settings = {
                "theme": "dark",
                "editor": {"fontSize": 14, "lineNumbers": True},
                "custom": "value",
            }
            settings_path.write_text(json.dumps(existing_settings, indent=2))

            # Install hooks
            install_hooks(project_root)

            # Verify existing settings preserved
            with open(settings_path) as f:
                updated_settings = json.load(f)

            assert updated_settings["theme"] == "dark"
            assert updated_settings["editor"]["fontSize"] == 14
            assert updated_settings["custom"] == "value"

            # Verify hooks added
            assert "hooks" in updated_settings
            assert "SubagentStop" in updated_settings["hooks"]
            assert "PreToolUse" in updated_settings["hooks"]

    def test_install_creates_settings_json_if_missing(self) -> None:
        """Test that installation creates settings.json if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            claude_dir = project_root / ".claude"
            claude_dir.mkdir()

            # No settings.json exists
            settings_path = claude_dir / "settings.json"
            assert not settings_path.exists()

            # Install hooks
            install_hooks(project_root)

            # Verify settings.json created
            assert settings_path.exists()

            with open(settings_path) as f:
                settings = json.load(f)

            # Should only have hooks configuration
            assert "hooks" in settings
            assert len(settings) == 1


class TestHookExecutabilityValidation:
    """Test that hooks are properly executable."""

    def test_all_hooks_have_execute_permission(self) -> None:
        """Test that all installed hooks have execute permission."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            claude_dir = project_root / ".claude"
            claude_dir.mkdir()

            install_hooks(project_root)

            hooks_dir = project_root / ".pantheon" / "hooks"
            for script_file in hooks_dir.glob("*.sh"):
                # Check executable permission
                assert os.access(
                    script_file, os.X_OK
                ), f"{script_file.name} is not executable"

                # Verify it's a shell script (starts with shebang)
                first_line = script_file.read_text().split("\n")[0]
                assert first_line.startswith(
                    "#!"
                ), f"{script_file.name} missing shebang"


class TestHookValidationEdgeCases:
    """Test edge cases in hook validation."""

    def test_validation_detects_missing_script(self) -> None:
        """Test that validation detects when a script is missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            claude_dir = project_root / ".claude"
            claude_dir.mkdir()

            install_hooks(project_root)

            # Delete one script
            hooks_dir = project_root / ".pantheon" / "hooks"
            (hooks_dir / "phase-gate.sh").unlink()

            # Validate
            validation = validate_hook_installation(project_root)

            # QualityGate hooks should report missing (affects all three usages)
            assert "Missing" in validation["QualityGate-SubagentStop"]
            assert "Missing" in validation["QualityGate-PreCommit"]
            assert "Missing" in validation["QualityGate-Task"]

            # OrchestratorCodeGate should still be OK
            assert validation["OrchestratorCodeGate"] == "OK"

    def test_validation_detects_non_executable_script(self) -> None:
        """Test that validation detects when a script is not executable."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            claude_dir = project_root / ".claude"
            claude_dir.mkdir()

            install_hooks(project_root)

            # Remove execute permission from one script
            hooks_dir = project_root / ".pantheon" / "hooks"
            script_path = hooks_dir / "orchestrator-code-gate.sh"
            os.chmod(script_path, 0o644)  # Read/write only, no execute

            # Validate
            validation = validate_hook_installation(project_root)

            # OrchestratorCodeGate should report permission issue
            assert "executable permission" in validation["OrchestratorCodeGate"]

            # QualityGate hooks should still be OK
            assert validation["QualityGate-SubagentStop"] == "OK"
            assert validation["QualityGate-PreCommit"] == "OK"
            assert validation["QualityGate-Task"] == "OK"
