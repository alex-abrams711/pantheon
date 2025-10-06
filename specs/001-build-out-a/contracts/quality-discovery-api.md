# Contract: Quality Discovery API

**Module**: `src/pantheon/quality/discovery.py`
**Purpose**: Discover project quality commands from structure and plan.md

---

## Function: `discover_quality_commands`

**Signature**:
```python
def discover_quality_commands(
    project_root: Path,
    plan_path: Optional[Path] = None
) -> dict[str, str]:
    """
    Discover quality commands for a project.

    Args:
        project_root: Absolute path to project root
        plan_path: Optional path to plan.md (if using Spec Kit)

    Returns:
        Dictionary with keys: test, lint, type_check, coverage, build
        Values are command strings or empty strings if not found

    Raises:
        ValueError: If project_root doesn't exist
    """
```

**Contract**:
- Input: `project_root` must be valid directory path
- Input: `plan_path` can be None (auto-discovery only)
- Output: Dictionary with 5 string keys, all present (use "" for not found)
- Behavior: Check plan.md first (if provided), then auto-discover
- Behavior: For Node.js, parse package.json scripts
- Behavior: For Python, check pyproject.toml or detect pytest/ruff/mypy
- Behavior: For Go, use standard commands (go test, etc.)
- Error: Raise ValueError if project_root invalid

**Test Requirements**:
- Test with plan.md containing explicit commands → uses those commands
- Test with Node.js project (package.json) → discovers npm scripts
- Test with Python project (pyproject.toml) → discovers pytest/ruff/mypy
- Test with Go project (go.mod) → returns standard Go commands
- Test with unknown project type → returns empty commands
- Test with invalid project_root → raises ValueError

---

## Function: `detect_project_type`

**Signature**:
```python
def detect_project_type(project_root: Path) -> str:
    """
    Detect project type from file structure.

    Args:
        project_root: Absolute path to project root

    Returns:
        One of: "node", "python", "go", "ruby", "other"
    """
```

**Contract**:
- Input: `project_root` must be valid directory
- Output: String from allowed set (node, python, go, ruby, other)
- Behavior: Check for package.json → "node"
- Behavior: Check for pyproject.toml or setup.py → "python"
- Behavior: Check for go.mod → "go"
- Behavior: Check for Gemfile → "ruby"
- Behavior: Otherwise → "other"

**Test Requirements**:
- Test with Node project → returns "node"
- Test with Python project → returns "python"
- Test with Go project → returns "go"
- Test with Ruby project → returns "ruby"
- Test with empty directory → returns "other"

---

## Function: `parse_plan_quality_commands`

**Signature**:
```python
def parse_plan_quality_commands(plan_path: Path) -> dict[str, str]:
    """
    Extract quality commands from plan.md.

    Args:
        plan_path: Path to plan.md file

    Returns:
        Dictionary with command keys and values from plan
        Only includes commands explicitly defined in plan

    Raises:
        FileNotFoundError: If plan.md doesn't exist
    """
```

**Contract**:
- Input: `plan_path` must point to existing file
- Output: Dictionary with subset of command keys (only those in plan)
- Behavior: Look for "## Quality Standards" section
- Behavior: Parse lines like "- Test command: pytest tests/"
- Behavior: Return only commands found (not full set)
- Error: Raise FileNotFoundError if plan missing

**Test Requirements**:
- Test with plan containing all commands → returns all
- Test with plan containing some commands → returns only those
- Test with plan missing Quality Standards section → returns empty dict
- Test with non-existent plan → raises FileNotFoundError

---

## Contract Test Structure

```python
# tests/contract/test_quality_discovery.py

def test_discover_quality_commands_with_plan():
    """Contract: explicit plan.md commands take precedence"""
    # Create temp project with plan.md
    # plan.md contains: test: custom-test
    result = discover_quality_commands(project_root, plan_path)
    assert result["test"] == "custom-test"

def test_discover_quality_commands_node_project():
    """Contract: Node.js project auto-discovery"""
    # Create temp project with package.json
    # package.json has scripts: {"test": "jest"}
    result = discover_quality_commands(project_root)
    assert result["test"] == "npm test"

def test_discover_quality_commands_python_project():
    """Contract: Python project auto-discovery"""
    # Create temp project with pyproject.toml
    # pyproject.toml has pytest config
    result = discover_quality_commands(project_root)
    assert "pytest" in result["test"]

def test_discover_quality_commands_invalid_root():
    """Contract: invalid project_root raises ValueError"""
    with pytest.raises(ValueError):
        discover_quality_commands(Path("/nonexistent"))

def test_detect_project_type_node():
    """Contract: detects Node.js from package.json"""
    # Create temp project with package.json
    assert detect_project_type(project_root) == "node"

def test_parse_plan_quality_commands_success():
    """Contract: extracts commands from plan.md"""
    # Create plan.md with Quality Standards section
    result = parse_plan_quality_commands(plan_path)
    assert "test" in result
```

---

## Integration Points

**Used By**:
- `pantheon.quality.config.generate_quality_config()` - calls to get commands
- `/constitution` command - invokes during project setup

**Dependencies**:
- Python stdlib: pathlib, json
- No external dependencies for discovery logic
