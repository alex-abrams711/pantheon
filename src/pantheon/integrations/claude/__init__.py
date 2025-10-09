"""Claude Code integration package.

Provides utilities for integrating Pantheon with Claude Code:
- Hook installation and management
- Claude Code settings configuration
"""

from .hooks import install_hooks, uninstall_hooks, validate_hook_installation

__all__ = [
    "install_hooks",
    "uninstall_hooks",
    "validate_hook_installation",
]
