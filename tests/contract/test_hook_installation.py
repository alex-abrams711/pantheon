"""Contract tests for hook installation API.

These tests define the contract for src/pantheon/hooks/install.py
Tests MUST FAIL until implementation is complete (TDD approach).
"""

import json
import os
from pathlib import Path

import pytest

from pantheon.hooks import (
    install_hooks,
    validate_hook_installation,
)


class TestInstallHooks:
    """Contract tests for install_hooks function."""

    def test_install_creates_hooks_directory(self, tmp_path: Path) -> None:
        """Contract: creates .pantheon/hooks/ directory."""
        # Setup: Project with .claude/ but no .pantheon/hooks/
        (tmp_path / ".claude").mkdir()
        (tmp_path / ".claude" / "settings.json").write_text("{}")

        # Execute
        result = install_hooks(tmp_path)

        # Verify: Directory created
        assert (tmp_path / ".pantheon" / "hooks").exists()
        assert (tmp_path / ".pantheon" / "hooks").is_dir()
        # All hooks installed successfully
        assert all(result.values())

    def test_install_copies_both_hook_scripts(self, tmp_path: Path) -> None:
        """Contract: copies both hook scripts to project."""
        # Setup
        (tmp_path / ".claude").mkdir()
        (tmp_path / ".claude" / "settings.json").write_text("{}")

        # Execute
        install_hooks(tmp_path)

        # Verify: Both scripts exist
        hooks_dir = tmp_path / ".pantheon" / "hooks"
        assert (hooks_dir / "phase-gate.sh").exists()
        assert (hooks_dir / "orchestrator-code-gate.sh").exists()

    def test_install_makes_scripts_executable(self, tmp_path: Path) -> None:
        """Contract: makes hook scripts executable (chmod +x)."""
        # Setup
        (tmp_path / ".claude").mkdir()
        (tmp_path / ".claude" / "settings.json").write_text("{}")

        # Execute
        install_hooks(tmp_path)

        # Verify: Scripts are executable
        hooks_dir = tmp_path / ".pantheon" / "hooks"
        for script in [
            "phase-gate.sh",
            "orchestrator-code-gate.sh",
        ]:
            script_path = hooks_dir / script
            assert os.access(script_path, os.X_OK), f"{script} not executable"

    def test_install_updates_settings_json_with_hook_paths(
        self, tmp_path: Path
    ) -> None:
        """Contract: updates .claude/settings.json with hook paths."""
        # Setup
        (tmp_path / ".claude").mkdir()
        settings_path = tmp_path / ".claude" / "settings.json"
        settings_path.write_text(json.dumps({}))

        # Execute
        install_hooks(tmp_path)

        # Verify: settings.json updated correctly
        with open(settings_path) as f:
            settings = json.load(f)

        assert "hooks" in settings
        assert "SubagentStop" in settings["hooks"]
        assert "PreToolUse" in settings["hooks"]

        # Verify SubagentStop hook (phase-gate.sh)
        subagent_hooks = settings["hooks"]["SubagentStop"]
        assert isinstance(subagent_hooks, list)
        assert any("phase-gate.sh" in str(h) for h in subagent_hooks)

        # Verify PreToolUse hooks (git commit, Task, Write|Edit)
        pretool_hooks = settings["hooks"]["PreToolUse"]
        assert isinstance(pretool_hooks, list)
        # phase-gate.sh used for git commit and Task
        assert any("phase-gate.sh" in str(h) for h in pretool_hooks)
        # orchestrator-code-gate.sh used for Write|Edit
        assert any("orchestrator-code-gate.sh" in str(h) for h in pretool_hooks)

    def test_install_preserves_existing_settings_json_content(
        self, tmp_path: Path
    ) -> None:
        """Contract: preserves other settings in settings.json."""
        # Setup: settings.json with existing content
        (tmp_path / ".claude").mkdir()
        settings_path = tmp_path / ".claude" / "settings.json"
        existing_settings = {"some_setting": "value", "another": 123}
        settings_path.write_text(json.dumps(existing_settings))

        # Execute
        install_hooks(tmp_path)

        # Verify: Existing settings preserved
        with open(settings_path) as f:
            settings = json.load(f)

        assert settings["some_setting"] == "value"
        assert settings["another"] == 123
        assert "hooks" in settings  # New hooks added

    def test_install_returns_success_status_for_each_hook(self, tmp_path: Path) -> None:
        """Contract: returns dict with success status for each hook."""
        # Setup
        (tmp_path / ".claude").mkdir()
        (tmp_path / ".claude" / "settings.json").write_text("{}")

        # Execute
        result = install_hooks(tmp_path)

        # Verify: Returns dict with 2 keys, all True
        assert isinstance(result, dict)
        assert "QualityGate" in result
        assert "OrchestratorCodeGate" in result
        assert result["QualityGate"] is True
        assert result["OrchestratorCodeGate"] is True

    def test_install_raises_file_not_found_if_no_claude_directory(
        self, tmp_path: Path
    ) -> None:
        """Contract: raises FileNotFoundError if .claude/ doesn't exist."""
        # Setup: No .claude/ directory
        assert not (tmp_path / ".claude").exists()

        # Execute & Verify
        with pytest.raises(FileNotFoundError, match=".claude"):
            install_hooks(tmp_path)

    def test_install_raises_permission_error_for_readonly_directory(
        self, tmp_path: Path
    ) -> None:
        """Contract: raises PermissionError if cannot write to project."""
        # Setup: Read-only directory
        (tmp_path / ".claude").mkdir()
        (tmp_path / ".claude" / "settings.json").write_text("{}")
        os.chmod(tmp_path, 0o444)  # Read-only

        try:
            # Execute & Verify
            with pytest.raises(PermissionError):
                install_hooks(tmp_path)
        finally:
            # Cleanup: Restore permissions
            os.chmod(tmp_path, 0o755)


class TestValidateHookInstallation:
    """Contract tests for validate_hook_installation function."""

    def test_validate_returns_ok_for_correctly_installed_hooks(
        self, tmp_path: Path
    ) -> None:
        """Contract: returns 'OK' for valid hooks."""
        # Setup: Install hooks correctly
        (tmp_path / ".claude").mkdir()
        (tmp_path / ".claude" / "settings.json").write_text("{}")
        install_hooks(tmp_path)

        # Execute
        result = validate_hook_installation(tmp_path)

        # Verify: All hooks OK (phase-gate used in multiple places)
        assert result["QualityGate-SubagentStop"] == "OK"
        assert result["QualityGate-PreCommit"] == "OK"
        assert result["QualityGate-Task"] == "OK"
        assert result["OrchestratorCodeGate"] == "OK"

    def test_validate_returns_error_for_missing_script(self, tmp_path: Path) -> None:
        """Contract: detects missing hook script."""
        # Setup: Install hooks then delete one
        (tmp_path / ".claude").mkdir()
        (tmp_path / ".claude" / "settings.json").write_text("{}")
        install_hooks(tmp_path)
        (tmp_path / ".pantheon" / "hooks" / "phase-gate.sh").unlink()

        # Execute
        result = validate_hook_installation(tmp_path)

        # Verify: Error message for missing script (affects all phase-gate usages)
        assert "OK" not in result["QualityGate-SubagentStop"]
        assert (
            "Missing" in result["QualityGate-SubagentStop"]
            or "not found" in result["QualityGate-SubagentStop"]
        )

    def test_validate_returns_error_for_non_executable_script(
        self, tmp_path: Path
    ) -> None:
        """Contract: detects non-executable script."""
        # Setup: Install hooks then remove execute permission
        (tmp_path / ".claude").mkdir()
        (tmp_path / ".claude" / "settings.json").write_text("{}")
        install_hooks(tmp_path)
        script_path = tmp_path / ".pantheon" / "hooks" / "orchestrator-code-gate.sh"
        os.chmod(script_path, 0o644)  # Remove execute permission

        # Execute
        result = validate_hook_installation(tmp_path)

        # Verify: Error message for non-executable
        assert "OK" not in result["OrchestratorCodeGate"]
        assert "executable" in result["OrchestratorCodeGate"].lower()

    def test_validate_returns_error_for_incorrect_settings_json_path(
        self, tmp_path: Path
    ) -> None:
        """Contract: detects incorrect path in settings.json."""
        # Setup: Install hooks then modify settings.json
        (tmp_path / ".claude").mkdir()
        settings_path = tmp_path / ".claude" / "settings.json"
        settings_path.write_text("{}")
        install_hooks(tmp_path)

        # Modify settings.json with wrong path for git commit hook
        with open(settings_path) as f:
            settings = json.load(f)
        # Find and modify the git commit hook in PreToolUse array
        for hook in settings["hooks"]["PreToolUse"]:
            if hook.get("matcher") == "Bash(git commit*)":
                hook["hooks"][0]["command"] = "/wrong/path/to/script.sh"
                break
        with open(settings_path, "w") as f:
            json.dump(settings, f)

        # Execute
        result = validate_hook_installation(tmp_path)

        # Verify: Error for QualityGate-PreCommit
        assert "OK" not in result["QualityGate-PreCommit"]

    def test_validate_does_not_raise_exceptions(self, tmp_path: Path) -> None:
        """Contract: never raises exceptions, always returns status dict."""
        # Setup: Various invalid states
        # Case 1: No hooks installed
        result1 = validate_hook_installation(tmp_path)
        assert isinstance(result1, dict)

        # Case 2: Partial installation
        (tmp_path / ".pantheon" / "hooks").mkdir(parents=True)
        (tmp_path / ".pantheon" / "hooks" / "phase-gate.sh").write_text(
            "#!/bin/bash\n"
        )
        result2 = validate_hook_installation(tmp_path)
        assert isinstance(result2, dict)

        # No exceptions raised in any case
        assert True
