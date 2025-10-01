"""Spec Kit integration utilities."""

from datetime import datetime
from pathlib import Path
from typing import Optional
import shutil


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

    commands_dir = project_root / ".claude" / "commands"
    files_to_backup = ["implement.md", "plan.md", "tasks.md"]

    for filename in files_to_backup:
        source = commands_dir / filename
        if source.exists():
            dest = backup_dir / filename
            shutil.copy2(source, dest)

    return backup_dir


def validate_integration(project_root: Optional[Path] = None) -> dict:
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

    commands_dir = project_root / ".claude" / "commands"
    results = {
        "valid": True,
        "errors": [],
        "files_checked": []
    }

    # Check that command files exist and contain integration sections
    expected_sections = {
        "implement.md": "## Agent Integration",
        "plan.md": "## Quality Standards (Required for DEV Integration)",
        "tasks.md": "## Task Format (Required for DEV Integration)"
    }

    for filename, section_marker in expected_sections.items():
        filepath = commands_dir / filename
        results["files_checked"].append(filename)

        if not filepath.exists():
            results["valid"] = False
            results["errors"].append(f"{filename} not found")
            continue

        try:
            content = filepath.read_text()
            if section_marker not in content:
                results["valid"] = False
                results["errors"].append(f"{filename} missing integration section: {section_marker}")
        except Exception as e:
            results["valid"] = False
            results["errors"].append(f"Error reading {filename}: {str(e)}")

    return results


# Integration directives to be inserted into Spec Kit commands
IMPLEMENT_DIRECTIVE = """## Agent Integration

**DEV Agent**: All task execution is delegated to the DEV sub-agent.

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

4. At phase boundaries: create sequential commits for completed tasks

See `.claude/agents/dev.md` for DEV's methodology and workflow.

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

    filepath = project_root / ".claude" / "commands" / "implement.md"

    if not filepath.exists():
        return False

    content = filepath.read_text()

    # Check if already integrated
    if "## Agent Integration" in content:
        return True  # Already integrated

    # Insert after the first heading
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('# '):
            # Insert directive after title
            lines.insert(i + 1, '\n' + IMPLEMENT_DIRECTIVE)
            break

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

    filepath = project_root / ".claude" / "commands" / "plan.md"

    if not filepath.exists():
        return False

    content = filepath.read_text()

    # Check if already integrated
    if "## Quality Standards (Required for DEV Integration)" in content:
        return True  # Already integrated

    # Insert after the first heading
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('# '):
            lines.insert(i + 1, '\n' + PLAN_DIRECTIVE)
            break

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

    filepath = project_root / ".claude" / "commands" / "tasks.md"

    if not filepath.exists():
        return False

    content = filepath.read_text()

    # Check if already integrated
    if "## Task Format (Required for DEV Integration)" in content:
        return True  # Already integrated

    # Insert after the first heading
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('# '):
            lines.insert(i + 1, '\n' + TASKS_DIRECTIVE)
            break

    filepath.write_text('\n'.join(lines))
    return True


def integrate_spec_kit(project_root: Optional[Path] = None) -> dict:
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

    result = {
        "success": False,
        "backup_dir": None,
        "files_modified": [],
        "errors": [],
        "validation": {}
    }

    # Step 1: Verify prerequisites
    if not verify_agents_installed(project_root):
        result["errors"].append("DEV agent not installed. Run 'pantheon init' first.")
        return result

    if not verify_spec_kit(project_root):
        result["errors"].append("Spec Kit not detected. Ensure .specify/ and .claude/commands/ exist.")
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
        if integrate_implement_command(project_root):
            result["files_modified"].append("implement.md")

        if integrate_plan_command(project_root):
            result["files_modified"].append("plan.md")

        if integrate_tasks_command(project_root):
            result["files_modified"].append("tasks.md")

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
