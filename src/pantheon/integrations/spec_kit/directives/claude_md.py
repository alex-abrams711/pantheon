"""CLAUDE.md orchestration section integration."""

from pathlib import Path
from typing import Optional

# Load directive content from file
_CONTENT_DIR = Path(__file__).parent / "content"
ORCHESTRATION_SECTION = (_CONTENT_DIR / "claude_md.md").read_text()


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
