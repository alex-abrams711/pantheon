"""Spec Kit integration utilities.

Supports both Spec Kit command formats:
- Pre-v0.0.57: implement.md, plan.md, tasks.md
- v0.0.57+: speckit.implement.md, speckit.plan.md, speckit.tasks.md
"""

import shutil
from datetime import datetime
from pathlib import Path
from typing import Literal, Optional, TypedDict


class ValidationResult(TypedDict):
    """Type for validation result dictionary."""

    valid: bool
    errors: list[str]
    files_checked: list[str]


class IntegrationResult(TypedDict):
    """Type for integration result dictionary."""

    success: bool
    backup_dir: Optional[Path]
    files_modified: list[str]
    errors: list[str]
    validation: ValidationResult


class RestoreResult(TypedDict):
    """Type for restore result dictionary."""

    success: bool
    files_restored: list[str]
    errors: list[str]


class RollbackResult(TypedDict):
    """Type for rollback result dictionary."""

    success: bool
    backup_dir: Optional[Path]
    files_restored: list[str]
    errors: list[str]


CommandFormat = Literal["old", "new"]


def _detect_command_format(
    project_root: Optional[Path] = None,
) -> Optional[CommandFormat]:
    """Detect which Spec Kit command format is being used.

    Args:
        project_root: Root directory of the project. Defaults to current directory.

    Returns:
        "new" for v0.0.57+ format (speckit.*.md),
        "old" for pre-v0.0.57 format (*.md),
        None if neither format detected.
    """
    if project_root is None:
        project_root = Path.cwd()

    commands_dir = project_root / ".claude" / "commands"

    if not commands_dir.exists():
        return None

    # Check for new format (v0.0.57+)
    new_format_files = [
        "speckit.implement.md",
        "speckit.plan.md",
        "speckit.tasks.md",
    ]
    if all((commands_dir / f).exists() for f in new_format_files):
        return "new"

    # Check for old format (pre-v0.0.57)
    old_format_files = ["implement.md", "plan.md", "tasks.md"]
    if any((commands_dir / f).exists() for f in old_format_files):
        return "old"

    return None


def _get_command_files(
    project_root: Optional[Path] = None,
) -> dict[str, Path]:
    """Get command file paths based on detected Spec Kit format.

    Args:
        project_root: Root directory of the project. Defaults to current directory.

    Returns:
        Dictionary mapping command names to file paths:
        {
            "implement": Path,
            "plan": Path,
            "tasks": Path
        }
        Returns empty dict if format cannot be detected.
    """
    if project_root is None:
        project_root = Path.cwd()

    commands_dir = project_root / ".claude" / "commands"
    format_type = _detect_command_format(project_root)

    if format_type == "new":
        return {
            "implement": commands_dir / "speckit.implement.md",
            "plan": commands_dir / "speckit.plan.md",
            "tasks": commands_dir / "speckit.tasks.md",
        }
    elif format_type == "old":
        return {
            "implement": commands_dir / "implement.md",
            "plan": commands_dir / "plan.md",
            "tasks": commands_dir / "tasks.md",
        }
    else:
        return {}


def verify_agents_installed(project_root: Optional[Path] = None) -> bool:
    """Verify that DEV agent is installed in the project.

    Args:
        project_root: Root directory of the project. Defaults to current directory.

    Returns:
        True if DEV agent exists in .claude/agents/, False otherwise.
    """
    if project_root is None:
        project_root = Path.cwd()

    dev_agent = project_root / ".claude" / "agents" / "dev.md"
    return dev_agent.exists()


def verify_spec_kit(project_root: Optional[Path] = None) -> bool:
    """Verify that Spec Kit is installed in the project.

    Args:
        project_root: Root directory of the project. Defaults to current directory.

    Returns:
        True if both .specify/ and .claude/commands/ exist, False otherwise.
    """
    if project_root is None:
        project_root = Path.cwd()

    specify_dir = project_root / ".specify"
    commands_dir = project_root / ".claude" / "commands"

    return specify_dir.exists() and commands_dir.exists()


def create_backup(project_root: Optional[Path] = None) -> Path:
    """Create timestamped backup of Spec Kit command files.

    Args:
        project_root: Root directory of the project. Defaults to current directory.

    Returns:
        Path to the backup directory.

    Raises:
        FileNotFoundError: If command files don't exist.
    """
    if project_root is None:
        project_root = Path.cwd()

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_dir = project_root / f".integration-backup-{timestamp}"
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Get command files based on detected format
    command_files = _get_command_files(project_root)

    for command_name, source_path in command_files.items():
        if source_path.exists():
            # Preserve original filename in backup
            dest = backup_dir / source_path.name
            shutil.copy2(source_path, dest)

    return backup_dir


def validate_integration(project_root: Optional[Path] = None) -> ValidationResult:
    """Validate that integration was successful.

    Args:
        project_root: Root directory of the project. Defaults to current directory.

    Returns:
        Dictionary with validation results:
        {
            "valid": bool,
            "errors": list of error messages,
            "files_checked": list of filenames
        }
    """
    if project_root is None:
        project_root = Path.cwd()

    results: ValidationResult = {
        "valid": True,
        "errors": [],
        "files_checked": []
    }

    # Get command files based on detected format
    command_files = _get_command_files(project_root)

    if not command_files:
        results["valid"] = False
        results["errors"].append("No Spec Kit command files detected")
        return results

    # Check that command files exist and contain integration sections
    expected_sections = {
        "implement": "## Agent Integration",
        "plan": "## Quality Standards (Required for DEV Integration)",
        "tasks": "## Task Format (Required for DEV Integration)"
    }

    for command_name, filepath in command_files.items():
        results["files_checked"].append(filepath.name)

        if not filepath.exists():
            results["valid"] = False
            results["errors"].append(f"{filepath.name} not found")
            continue

        section_marker = expected_sections.get(command_name)
        if not section_marker:
            continue

        try:
            content = filepath.read_text()
            if section_marker not in content:
                results["valid"] = False
                error_msg = (
                    f"{filepath.name} missing integration section: {section_marker}"
                )
                results["errors"].append(error_msg)
        except Exception as e:
            results["valid"] = False
            results["errors"].append(f"Error reading {filepath.name}: {str(e)}")

    return results


# Integration directives to be inserted into Spec Kit commands
IMPLEMENT_DIRECTIVE = """## Agent Integration

**Multi-Agent Workflow**: Task execution uses DEV and QA agents with quality gates.

### DEV Agent Delegation

When executing tasks:
1. For each task in tasks.md, prepare a context package containing:
   - Task ID, description, and file paths
   - Relevant spec requirements (FR-XXX references)
   - Quality standards from plan.md (lint/type/test commands)
   - Subtasks as acceptance criteria
   - Tech stack constraints

2. Invoke DEV sub-agent using Task tool:
   ```
   Use Task tool:
     subagent_type: "dev"
     description: "Implement [Task ID]"
     prompt: [context package from above]
   ```

3. Process DEV results:
   - If success: mark task complete, log decisions, continue
   - If failure: halt, report status, wait for user

### Parallel Execution

For tasks marked [P] in tasks.md (parallel-safe):
- Invoke up to 3 DEV agents simultaneously in a SINGLE message
- Use multiple Task tool calls in one message
- Wait for all agents to complete before proceeding
- Example:
  ```
  Use the DEV agent to implement T001: [description]
  Use the DEV agent to implement T002: [description]
  Use the DEV agent to implement T003: [description]
  ```

### QA Validation

After completing a batch of related tasks:
1. Prepare QA context package containing:
   - List of completed task IDs
   - Quality standards from plan.md
   - Definition of Done checklist
   - Manual testing requirements (if functional changes)

2. Invoke QA sub-agent using Task tool:
   ```
   Use Task tool:
     subagent_type: "qa"
     description: "Validate batch: [Task IDs]"
     prompt: [QA context package from above]
   ```

3. Process QA report:
   - If PASS: create commits for validated tasks
   - If FAIL: reinvoke DEV agents to fix issues, then re-validate

### Commit Strategy

- Commits created ONLY after QA PASS
- Orchestrator creates commits (DEV/QA agents do NOT commit)
- Atomic commits per task or logical batch
- Include task IDs and quality metrics in commit message

See `.claude/agents/dev.md` and `.claude/agents/qa.md` for agent workflows.

---
"""

PLAN_DIRECTIVE = """## Quality Standards (Required for DEV Integration)

Include in plan.md output:
- Lint command (e.g., `npm run lint`)
- Type check command (e.g., `tsc --noEmit`)
- Test command (e.g., `npm test`)
- Coverage requirement (e.g., 80%)

If commands cannot be auto-discovered, mark as "CLARIFICATION REQUIRED".

---
"""

TASKS_DIRECTIVE = """## Task Format (Required for DEV Integration)

Each task should include subtasks as acceptance criteria:

**T001** [Task Description] (`path/to/file.ext`)
- [ ] Subtask 1: [Specific acceptance criterion]
- [ ] Subtask 2: [Specific acceptance criterion]
- Dependencies: [Task IDs or "None"]
- Implements: [FR-XXX references]

---
"""


def integrate_implement_command(project_root: Optional[Path] = None) -> bool:
    """Add DEV integration directive to /implement command.

    Args:
        project_root: Root directory of the project. Defaults to current directory.

    Returns:
        True if integration successful, False otherwise.
    """
    if project_root is None:
        project_root = Path.cwd()

    command_files = _get_command_files(project_root)
    filepath = command_files.get("implement")

    if not filepath or not filepath.exists():
        return False

    content = filepath.read_text()

    # Check if already integrated
    if "## Agent Integration" in content:
        return True  # Already integrated

    # Insert after YAML frontmatter or at beginning if no frontmatter
    lines = content.split('\n')
    insert_index = 0
    in_frontmatter = False
    frontmatter_end_found = False

    for i, line in enumerate(lines):
        # Detect start of YAML frontmatter
        if i == 0 and line.strip() == '---':
            in_frontmatter = True
            continue

        # Detect end of YAML frontmatter
        if in_frontmatter and line.strip() == '---':
            insert_index = i + 1
            frontmatter_end_found = True
            break

    # If no frontmatter found, insert at beginning
    if not frontmatter_end_found:
        insert_index = 0

    # Insert directive at the determined position
    lines.insert(insert_index, '\n' + IMPLEMENT_DIRECTIVE)

    filepath.write_text('\n'.join(lines))
    return True


def integrate_plan_command(project_root: Optional[Path] = None) -> bool:
    """Add quality standards directive to /plan command.

    Args:
        project_root: Root directory of the project. Defaults to current directory.

    Returns:
        True if integration successful, False otherwise.
    """
    if project_root is None:
        project_root = Path.cwd()

    command_files = _get_command_files(project_root)
    filepath = command_files.get("plan")

    if not filepath or not filepath.exists():
        return False

    content = filepath.read_text()

    # Check if already integrated
    if "## Quality Standards (Required for DEV Integration)" in content:
        return True  # Already integrated

    # Insert after YAML frontmatter or at beginning if no frontmatter
    lines = content.split('\n')
    insert_index = 0
    in_frontmatter = False
    frontmatter_end_found = False

    for i, line in enumerate(lines):
        # Detect start of YAML frontmatter
        if i == 0 and line.strip() == '---':
            in_frontmatter = True
            continue

        # Detect end of YAML frontmatter
        if in_frontmatter and line.strip() == '---':
            insert_index = i + 1
            frontmatter_end_found = True
            break

    # If no frontmatter found, insert at beginning
    if not frontmatter_end_found:
        insert_index = 0

    # Insert directive at the determined position
    lines.insert(insert_index, '\n' + PLAN_DIRECTIVE)

    filepath.write_text('\n'.join(lines))
    return True


def integrate_tasks_command(project_root: Optional[Path] = None) -> bool:
    """Add task format directive to /tasks command.

    Args:
        project_root: Root directory of the project. Defaults to current directory.

    Returns:
        True if integration successful, False otherwise.
    """
    if project_root is None:
        project_root = Path.cwd()

    command_files = _get_command_files(project_root)
    filepath = command_files.get("tasks")

    if not filepath or not filepath.exists():
        return False

    content = filepath.read_text()

    # Check if already integrated
    if "## Task Format (Required for DEV Integration)" in content:
        return True  # Already integrated

    # Insert after YAML frontmatter or at beginning if no frontmatter
    lines = content.split('\n')
    insert_index = 0
    in_frontmatter = False
    frontmatter_end_found = False

    for i, line in enumerate(lines):
        # Detect start of YAML frontmatter
        if i == 0 and line.strip() == '---':
            in_frontmatter = True
            continue

        # Detect end of YAML frontmatter
        if in_frontmatter and line.strip() == '---':
            insert_index = i + 1
            frontmatter_end_found = True
            break

    # If no frontmatter found, insert at beginning
    if not frontmatter_end_found:
        insert_index = 0

    # Insert directive at the determined position
    lines.insert(insert_index, '\n' + TASKS_DIRECTIVE)

    filepath.write_text('\n'.join(lines))
    return True


def integrate_spec_kit(project_root: Optional[Path] = None) -> IntegrationResult:
    """Main integration flow: Add DEV agent directives to Spec Kit commands.

    Args:
        project_root: Root directory of the project. Defaults to current directory.

    Returns:
        Dictionary with integration results:
        {
            "success": bool,
            "backup_dir": Path or None,
            "files_modified": list of filenames,
            "errors": list of error messages,
            "validation": dict from validate_integration()
        }
    """
    if project_root is None:
        project_root = Path.cwd()

    result: IntegrationResult = {
        "success": False,
        "backup_dir": None,
        "files_modified": [],
        "errors": [],
        "validation": {"valid": False, "errors": [], "files_checked": []}
    }

    # Step 1: Verify prerequisites
    if not verify_agents_installed(project_root):
        result["errors"].append("DEV agent not installed. Run 'pantheon init' first.")
        return result

    if not verify_spec_kit(project_root):
        result["errors"].append(
            "Spec Kit not detected. Ensure .specify/ and .claude/commands/ exist."
        )
        return result

    # Detect command format
    format_type = _detect_command_format(project_root)
    if format_type is None:
        result["errors"].append(
            "Spec Kit command files not found. "
            "Expected either speckit.*.md (v0.0.57+) or *.md (pre-v0.0.57) format."
        )
        return result

    # Step 2: Create backup
    try:
        backup_dir = create_backup(project_root)
        result["backup_dir"] = backup_dir
    except Exception as e:
        result["errors"].append(f"Failed to create backup: {str(e)}")
        return result

    # Step 3: Integrate commands
    try:
        command_files = _get_command_files(project_root)

        if integrate_implement_command(project_root):
            result["files_modified"].append(command_files["implement"].name)

        if integrate_plan_command(project_root):
            result["files_modified"].append(command_files["plan"].name)

        if integrate_tasks_command(project_root):
            result["files_modified"].append(command_files["tasks"].name)

    except Exception as e:
        result["errors"].append(f"Integration failed: {str(e)}")
        # TODO: Rollback on failure
        return result

    # Step 4: Validate integration
    validation = validate_integration(project_root)
    result["validation"] = validation

    if validation["valid"]:
        result["success"] = True
    else:
        result["errors"].extend(validation["errors"])

    return result


def find_latest_backup(project_root: Optional[Path] = None) -> Optional[Path]:
    """Find the most recent integration backup directory.

    Args:
        project_root: Root directory of the project. Defaults to current directory.

    Returns:
        Path to the most recent backup directory, or None if no backups found.
    """
    if project_root is None:
        project_root = Path.cwd()

    # Find all backup directories
    backup_dirs = list(project_root.glob(".integration-backup-*"))

    if not backup_dirs:
        return None

    # Sort by name (which includes timestamp) and return the latest
    backup_dirs.sort(reverse=True)
    return backup_dirs[0]


def restore_files(
    backup_dir: Path, project_root: Optional[Path] = None
) -> RestoreResult:
    """Restore command files from a backup directory.

    Args:
        backup_dir: Path to the backup directory containing files to restore.
        project_root: Root directory of the project. Defaults to current directory.

    Returns:
        Dictionary with restoration results:
        {
            "success": bool,
            "files_restored": list of filenames,
            "errors": list of error messages
        }
    """
    if project_root is None:
        project_root = Path.cwd()

    result: RestoreResult = {
        "success": False,
        "files_restored": [],
        "errors": []
    }

    if not backup_dir.exists():
        result["errors"].append(f"Backup directory not found: {backup_dir}")
        return result

    commands_dir = project_root / ".claude" / "commands"

    # Restore each file from backup
    for backup_file in backup_dir.glob("*.md"):
        try:
            dest_file = commands_dir / backup_file.name
            shutil.copy2(backup_file, dest_file)
            result["files_restored"].append(backup_file.name)
        except Exception as e:
            result["errors"].append(f"Failed to restore {backup_file.name}: {str(e)}")

    if result["files_restored"] and not result["errors"]:
        result["success"] = True

    return result


def rollback_integration(project_root: Optional[Path] = None) -> RollbackResult:
    """Rollback to the most recent backup.

    Args:
        project_root: Root directory of the project. Defaults to current directory.

    Returns:
        Dictionary with rollback results:
        {
            "success": bool,
            "backup_dir": Path or None,
            "files_restored": list of filenames,
            "errors": list of error messages
        }
    """
    if project_root is None:
        project_root = Path.cwd()

    result: RollbackResult = {
        "success": False,
        "backup_dir": None,
        "files_restored": [],
        "errors": []
    }

    # Find latest backup
    backup_dir = find_latest_backup(project_root)

    if not backup_dir:
        result["errors"].append("No backup found. Nothing to rollback.")
        return result

    result["backup_dir"] = backup_dir

    # Restore files
    restore_result = restore_files(backup_dir, project_root)

    result["files_restored"] = restore_result["files_restored"]
    result["errors"].extend(restore_result["errors"])
    result["success"] = restore_result["success"]

    return result


# Multi-Agent Workflow Orchestration content to be added to CLAUDE.md
ORCHESTRATION_SECTION = """
## Multi-Agent Workflow Orchestration

### Overview

Pantheon uses a multi-agent architecture with DEV and QA agents for
quality-first development. As the orchestrator, you coordinate task execution,
quality validation, and commits.

### Parallel Execution Strategy

**When to use parallel execution**:
- Tasks marked `[P]` in tasks.md (parallel-safe)
- Tasks affecting different files with no shared state
- Maximum 3 DEV agents running simultaneously

**How to invoke parallel DEV agents**:
```
# SINGLE message with multiple Task tool calls:
Use the DEV agent to implement T001: [task description]
Use the DEV agent to implement T002: [task description]
Use the DEV agent to implement T003: [task description]
```

**Important**: ALL parallel invocations MUST be in a SINGLE message.
Do NOT send separate messages.

### DEV Agent Context Package

When invoking DEV agent, provide complete context:

```markdown
# Task Context: [Task ID]

## Task Details
**ID**: [Task ID]
**Description**: [Task description]
**Files**: [Comma-separated file paths]

## Acceptance Criteria
- [ ] [Specific acceptance criterion 1]
- [ ] [Specific acceptance criterion 2]
[... from tasks.md subtasks]

## Quality Standards
**Test Command**: [from plan.md]
**Lint Command**: [from plan.md]
**Type Command**: [from plan.md]
**Coverage Threshold**: [from plan.md]

## Related Requirements
[FR-XXX references from tasks.md]

## Tech Stack
**Language**: [from plan.md]
**Patterns**: [Architecture patterns to follow]
**Testing**: [Testing approach]

## Constitution
[Relevant principles from constitution]
```

### QA Validation Workflow

**When to invoke QA agent**:
- After completing a batch of related tasks
- Before creating commits
- At phase boundaries

**QA Agent Context Package**:

```markdown
# QA Validation Context

## Tasks to Validate
- **[Task ID]**: [Description]
  - Files: [file paths]
[... for each task in batch]

## Quality Standards
**Test Command**: [from plan.md]
**Coverage Command**: [test command with --cov flags]
**Coverage Threshold**: [from plan.md]
**Lint Command**: [from plan.md]
**Type Command**: [from plan.md]

## Definition of Done
- [ ] All tests pass (0 failures)
- [ ] Coverage ≥[threshold]% branches
- [ ] No linting errors
- [ ] No type errors
- [ ] No code smells (console.log, TODO, unused imports)
- [ ] Manual testing passed (if functional changes)

## Project Root
[Absolute path to project root]

## Manual Testing Required
[YES/NO] - [Description if YES]
```

**Processing QA Report**:
- If `Status: PASS`: Create commits for validated tasks
- If `Status: FAIL`: Reinvoke DEV agents to fix issues, then re-validate
- Maximum 2-3 rework cycles before escalating to user

### Phase Gate Checkpoints

**At phase boundaries**:
1. Generate Phase Completion Report showing:
   - Completed tasks
   - Quality metrics (tests, coverage, lint, type)
   - Git commits created
   - Statistics (agents invoked, rework cycles)

2. Present to user for approval:
   ```markdown
   # Phase [N] Complete: [Phase Name]

   [Summary of completed work]

   Type 'yes' to proceed to Phase [N+1], 'review' to pause, or 'no' to halt.
   ```

3. Wait for user approval before proceeding

### Commit Strategy

**CRITICAL**: Commits are created ONLY by orchestrator, NEVER by agents.

**When to commit**:
- ONLY after QA PASS status
- At phase boundaries (after user approval)
- Atomic commits per task or logical batch

**Commit message format**:
```
[type]: [Task IDs] [Brief description]

[Detailed changes]

Quality metrics:
- Tests: [passing]/[total] passing
- Coverage: [percentage]% branches
- Lint: 0 errors
- Type: 0 errors
```

**Example**:
```
feat: T001-T003 Add quality discovery and config modules

- Implement project-agnostic quality command discovery
- Generate quality config JSON with auto-detected commands
- Support Python, Node.js, Go project types

Quality metrics:
- Tests: 18/18 passing
- Coverage: 92% branches
- Lint: 0 errors
- Type: 0 errors
```
"""


def integrate_claude_md(project_root: Optional[Path] = None) -> bool:
    """Add multi-agent orchestration section to CLAUDE.md.

    Args:
        project_root: Root directory of the project. Defaults to current directory.

    Returns:
        True if integration successful, False otherwise.
    """
    if project_root is None:
        project_root = Path.cwd()

    claude_md_path = project_root / "CLAUDE.md"

    # Check if orchestration section already exists
    if claude_md_path.exists():
        content = claude_md_path.read_text()
        if "## Multi-Agent Workflow Orchestration" in content:
            return True  # Already integrated
    else:
        # Create CLAUDE.md if doesn't exist
        content = "# Claude Instructions\n\n"

    # Append orchestration section
    updated_content = content.rstrip() + "\n" + ORCHESTRATION_SECTION

    # Write updated content
    claude_md_path.write_text(updated_content)

    return True
