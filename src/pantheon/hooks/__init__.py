"""Pantheon hooks package.

Contains quality gate hook scripts and installation utilities.
"""

from .install import install_hooks, validate_hook_installation

__all__ = [
    "install_hooks",
    "validate_hook_installation",
]
