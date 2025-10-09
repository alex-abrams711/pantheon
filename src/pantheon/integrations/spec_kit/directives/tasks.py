"""/tasks command integration directive and logic."""

from pathlib import Path
from typing import Optional

from ..detection import get_command_files

# Load directive content from file
_CONTENT_DIR = Path(__file__).parent / "content"
TASKS_DIRECTIVE = (_CONTENT_DIR / "tasks.md").read_text()


def integrate_tasks_command(project_root: Optional[Path] = None) -> bool:
    """Add task format directive to /tasks command.

    Args:
        project_root: Root directory of the project. Defaults to current directory.

    Returns:
        True if integration successful, False otherwise.
    """
    if project_root is None:
        project_root = Path.cwd()

    command_files = get_command_files(project_root)
    filepath = command_files.get("tasks")

    if not filepath or not filepath.exists():
        return False

    content = filepath.read_text()

    # Check if already integrated
    if "## Task Format (Required for DEV Integration)" in content:
        return True  # Already integrated

    # Insert after YAML frontmatter or at beginning if no frontmatter
    lines = content.split("\n")
    insert_index = 0
    in_frontmatter = False
    frontmatter_end_found = False

    for i, line in enumerate(lines):
        # Detect start of YAML frontmatter
        if i == 0 and line.strip() == "---":
            in_frontmatter = True
            continue

        # Detect end of YAML frontmatter
        if in_frontmatter and line.strip() == "---":
            insert_index = i + 1
            frontmatter_end_found = True
            break

    # If no frontmatter found, insert at beginning
    if not frontmatter_end_found:
        insert_index = 0

    # Insert directive at the determined position
    lines.insert(insert_index, "\n" + TASKS_DIRECTIVE)

    filepath.write_text("\n".join(lines))
    return True
