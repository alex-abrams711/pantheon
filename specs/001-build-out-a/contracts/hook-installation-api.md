# Contract: Hook Installation API

**Module**: `src/pantheon/integrations/hooks.py`
**Purpose**: Install and configure Claude Code quality gate hooks

---

## Function: `install_hooks`

**Signature**:
```python
def install_hooks(project_root: Path) -> dict[str, bool]:
    """
    Install quality gate hooks in project.

    Args:
        project_root: Absolute path to project root

    Returns:
        Dictionary with hook names as keys, success status as values
        Example: {"SubagentStop": True, "PreCommit": True, "PhaseGate": True}

    Raises:
        FileNotFoundError: If .claude/ directory doesn't exist
        PermissionError: If cannot write to project directory
    """
```

**Contract**:
- Input: `project_root` must be valid directory with .claude/
- Output: Dictionary with 3 keys (SubagentStop, PreCommit, PhaseGate), boolean values
- Behavior: Create .pantheon/hooks/ directory if not exists
- Behavior: Copy hook scripts from package to project
- Behavior: Make hook scripts executable (chmod +x)
- Behavior: Update .claude/settings.json with hook paths
- Behavior: Validate each hook installed correctly
- Behavior: Return success status for each hook
- Error: FileNotFoundError if .claude/ missing
- Error: PermissionError if cannot write files

**Test Requirements**:
- Test creates .pantheon/hooks/ directory
- Test copies all 3 hook scripts
- Test makes scripts executable
- Test updates settings.json correctly
- Test returns all True for successful installation
- Test raises FileNotFoundError if no .claude/
- Test raises PermissionError for read-only directory

---

## Function: `uninstall_hooks`

**Signature**:
```python
def uninstall_hooks(project_root: Path) -> bool:
    """
    Remove quality gate hooks from project.

    Args:
        project_root: Absolute path to project root

    Returns:
        True if all hooks removed successfully

    Raises:
        FileNotFoundError: If .claude/ directory doesn't exist
    """
```

**Contract**:
- Input: `project_root` must be valid directory with .claude/
- Output: Boolean (True = all removed, False = some failed)
- Behavior: Remove hook entries from .claude/settings.json
- Behavior: Delete .pantheon/hooks/ directory (including all scripts)
- Behavior: Keep .pantheon/quality-config.json (don't delete)
- Error: FileNotFoundError if .claude/ missing

**Test Requirements**:
- Test removes all hook entries from settings.json
- Test deletes .pantheon/hooks/ directory
- Test preserves .pantheon/quality-config.json
- Test returns True on success
- Test raises FileNotFoundError if no .claude/

---

## Function: `validate_hook_installation`

**Signature**:
```python
def validate_hook_installation(project_root: Path) -> dict[str, str]:
    """
    Validate that hooks are installed correctly.

    Args:
        project_root: Absolute path to project root

    Returns:
        Dictionary with hook names as keys, status messages as values
        Example: {"SubagentStop": "OK", "PreCommit": "Missing executable permission"}
    """
```

**Contract**:
- Input: `project_root` must be valid directory
- Output: Dictionary with hook names and status messages
- Behavior: Check hook scripts exist in .pantheon/hooks/
- Behavior: Check scripts are executable
- Behavior: Check .claude/settings.json has correct paths
- Behavior: Return "OK" for valid hooks, error message for invalid
- No exceptions raised (returns status for all hooks)

**Test Requirements**:
- Test returns "OK" for correctly installed hooks
- Test returns error message for missing script
- Test returns error message for non-executable script
- Test returns error message for incorrect settings.json path

---

## Contract Test Structure

```python
# tests/contract/test_hook_installation.py

def test_install_hooks_creates_directory():
    """Contract: creates .pantheon/hooks/ directory"""
    result = install_hooks(project_root)
    assert (project_root / ".pantheon" / "hooks").exists()
    assert all(result.values())  # All True

def test_install_hooks_copies_scripts():
    """Contract: copies all 3 hook scripts"""
    install_hooks(project_root)
    hooks_dir = project_root / ".pantheon" / "hooks"

    assert (hooks_dir / "subagent-validation.sh").exists()
    assert (hooks_dir / "pre-commit-gate.sh").exists()
    assert (hooks_dir / "phase-gate.sh").exists()

def test_install_hooks_makes_executable():
    """Contract: makes hook scripts executable"""
    install_hooks(project_root)
    hooks_dir = project_root / ".pantheon" / "hooks"

    for script in ["subagent-validation.sh", "pre-commit-gate.sh", "phase-gate.sh"]:
        script_path = hooks_dir / script
        assert os.access(script_path, os.X_OK)

def test_install_hooks_updates_settings():
    """Contract: updates .claude/settings.json"""
    install_hooks(project_root)
    settings_path = project_root / ".claude" / "settings.json"

    with open(settings_path) as f:
        settings = json.load(f)

    assert "hooks" in settings
    assert "SubagentStop" in settings["hooks"]
    assert "PreCommit" in settings["hooks"]
    assert "UserPromptSubmit" in settings["hooks"]

def test_install_hooks_no_claude_directory():
    """Contract: raises FileNotFoundError if no .claude/"""
    # Project without .claude/
    with pytest.raises(FileNotFoundError):
        install_hooks(project_root)

def test_uninstall_hooks_removes_entries():
    """Contract: removes hook entries from settings.json"""
    install_hooks(project_root)
    uninstall_hooks(project_root)

    settings_path = project_root / ".claude" / "settings.json"
    with open(settings_path) as f:
        settings = json.load(f)

    assert "hooks" not in settings or not settings["hooks"]

def test_uninstall_hooks_deletes_directory():
    """Contract: deletes .pantheon/hooks/ directory"""
    install_hooks(project_root)
    uninstall_hooks(project_root)

    assert not (project_root / ".pantheon" / "hooks").exists()

def test_uninstall_hooks_preserves_config():
    """Contract: preserves quality-config.json"""
    # Create quality config
    (project_root / ".pantheon").mkdir(exist_ok=True)
    config_path = project_root / ".pantheon" / "quality-config.json"
    config_path.write_text('{"version": "1.0"}')

    install_hooks(project_root)
    uninstall_hooks(project_root)

    assert config_path.exists()

def test_validate_hook_installation_success():
    """Contract: returns OK for valid installation"""
    install_hooks(project_root)
    result = validate_hook_installation(project_root)

    assert result["SubagentStop"] == "OK"
    assert result["PreCommit"] == "OK"
    assert result["PhaseGate"] == "OK"

def test_validate_hook_installation_missing_script():
    """Contract: detects missing hook script"""
    install_hooks(project_root)
    # Delete one script
    (project_root / ".pantheon" / "hooks" / "phase-gate.sh").unlink()

    result = validate_hook_installation(project_root)
    assert "Missing" in result["PhaseGate"] or "not found" in result["PhaseGate"]
```

---

## Integration Points

**Used By**:
- `pantheon integrate` command - calls install_hooks()
- `pantheon rollback` command - calls uninstall_hooks()
- CLI validation - calls validate_hook_installation()

**Hook Script Paths** (in package):
- `src/pantheon/hooks/subagent-validation.sh`
- `src/pantheon/hooks/pre-commit-gate.sh`
- `src/pantheon/hooks/phase-gate.sh`

**Hook Script Paths** (in user project):
- `.pantheon/hooks/subagent-validation.sh`
- `.pantheon/hooks/pre-commit-gate.sh`
- `.pantheon/hooks/phase-gate.sh`
