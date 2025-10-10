"""Pantheon commands package.

Contains slash command specifications and installation utilities.
"""

from .install import install_commands, validate_command_installation

__all__ = [
    "install_commands",
    "validate_command_installation",
]
