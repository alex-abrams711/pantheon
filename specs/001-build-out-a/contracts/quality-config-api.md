# Contract: Quality Config API

**Module**: `src/pantheon/quality/config.py`
**Purpose**: Generate and manage .pantheon/quality-config.json

---

## Function: `generate_quality_config`

**Signature**:
```python
def generate_quality_config(
    project_root: Path,
    plan_path: Optional[Path] = None,
    coverage_threshold: int = 80
) -> Path:
    """
    Generate quality config file for a project.

    Args:
        project_root: Absolute path to project root
        plan_path: Optional path to plan.md
        coverage_threshold: Coverage percentage threshold (0-100)

    Returns:
        Path to created config file (.pantheon/quality-config.json)

    Raises:
        ValueError: If project_root invalid or threshold out of range
    """
```

**Contract**:
- Input: `project_root` must be valid directory
- Input: `coverage_threshold` must be 0-100
- Output: Path object pointing to .pantheon/quality-config.json
- Behavior: Create .pantheon/ directory if not exists
- Behavior: Call discovery.discover_quality_commands() to get commands
- Behavior: Call discovery.detect_project_type() to get type
- Behavior: Write JSON file with schema from data-model.md
- Behavior: Set discovery_source based on whether plan.md used
- Error: Raise ValueError for invalid inputs

**Test Requirements**:
- Test creates .pantheon/ directory if missing
- Test generates valid JSON matching schema
- Test includes all discovered commands
- Test sets correct coverage threshold
- Test sets discovery_source correctly
- Test raises ValueError for invalid threshold

---

## Function: `load_quality_config`

**Signature**:
```python
def load_quality_config(project_root: Path) -> dict:
    """
    Load quality config from project.

    Args:
        project_root: Absolute path to project root

    Returns:
        Dictionary with config data

    Raises:
        FileNotFoundError: If config doesn't exist
        ValueError: If config JSON is invalid
    """
```

**Contract**:
- Input: `project_root` must be valid directory
- Output: Dictionary matching quality-config.json schema
- Behavior: Read .pantheon/quality-config.json
- Behavior: Parse JSON and validate structure
- Error: FileNotFoundError if config missing
- Error: ValueError if JSON invalid or schema mismatch

**Test Requirements**:
- Test loads valid config successfully
- Test returns correct dictionary structure
- Test raises FileNotFoundError for missing config
- Test raises ValueError for invalid JSON
- Test raises ValueError for missing required fields

---

## Function: `validate_quality_config`

**Signature**:
```python
def validate_quality_config(config: dict) -> bool:
    """
    Validate quality config structure.

    Args:
        config: Dictionary to validate

    Returns:
        True if valid, False otherwise
    """
```

**Contract**:
- Input: Any dictionary
- Output: Boolean (True = valid, False = invalid)
- Behavior: Check required keys present (version, commands, thresholds)
- Behavior: Check commands is dict with string values
- Behavior: Check thresholds values are 0-100
- No exceptions raised (returns False for invalid)

**Test Requirements**:
- Test returns True for valid config
- Test returns False for missing version
- Test returns False for missing commands
- Test returns False for invalid threshold values
- Test returns False for non-dict commands

---

## Contract Test Structure

```python
# tests/contract/test_quality_config.py

def test_generate_quality_config_creates_directory():
    """Contract: creates .pantheon/ if not exists"""
    # Temp project without .pantheon/
    config_path = generate_quality_config(project_root)
    assert (project_root / ".pantheon").exists()
    assert config_path.exists()

def test_generate_quality_config_valid_json():
    """Contract: generates valid JSON matching schema"""
    config_path = generate_quality_config(project_root)
    with open(config_path) as f:
        config = json.load(f)

    # Validate schema
    assert "version" in config
    assert "project_type" in config
    assert "commands" in config
    assert "thresholds" in config
    assert "discovery_source" in config

def test_generate_quality_config_invalid_threshold():
    """Contract: raises ValueError for threshold > 100"""
    with pytest.raises(ValueError):
        generate_quality_config(project_root, coverage_threshold=150)

def test_load_quality_config_success():
    """Contract: loads existing config"""
    # Create config first
    generate_quality_config(project_root)
    config = load_quality_config(project_root)
    assert isinstance(config, dict)
    assert "commands" in config

def test_load_quality_config_missing():
    """Contract: raises FileNotFoundError if missing"""
    with pytest.raises(FileNotFoundError):
        load_quality_config(project_root)

def test_validate_quality_config_valid():
    """Contract: returns True for valid config"""
    config = {
        "version": "1.0",
        "project_type": "python",
        "commands": {"test": "pytest"},
        "thresholds": {"coverage_branches": 80}
    }
    assert validate_quality_config(config) is True

def test_validate_quality_config_invalid():
    """Contract: returns False for missing keys"""
    config = {"version": "1.0"}  # Missing required keys
    assert validate_quality_config(config) is False
```

---

## Integration Points

**Used By**:
- `/constitution` command - generates config during setup
- All hooks (SubagentStop, PreCommit, Phase Gate) - read config
- DEV and QA agents - read config for quality commands

**Uses**:
- `pantheon.quality.discovery` - for command discovery

**File Format** (.pantheon/quality-config.json):
```json
{
  "version": "1.0",
  "project_type": "python",
  "commands": {
    "test": "pytest tests/",
    "lint": "ruff check src/",
    "type_check": "mypy src/",
    "coverage": "pytest --cov=src --cov-report=term-missing",
    "build": "python -m build"
  },
  "thresholds": {
    "coverage_branches": 80,
    "coverage_statements": 80
  },
  "discovery_source": "plan.md"
}
```
