"""Runtime utilities for Pydgey execution environments.

This package provides tools for:
- Command execution with logging
- Environment detection and setup (Pixi, Colab)
- Colab-specific utilities
"""

from .commands import run_command
from .environment import (
    PixiEnvironment,
    check_colab,
    check_environment,
    check_tool,
    find_lockfile,
    is_pixi_installed,
    setup_environment,
    wrap_command_for_pixi,
)
from .colab import keep_alive_thread, mount_google_drive

__all__ = [
    "run_command",
    "PixiEnvironment",
    "check_colab",
    "check_environment",
    "check_tool",
    "find_lockfile",
    "is_pixi_installed",
    "setup_environment",
    "wrap_command_for_pixi",
    "keep_alive_thread",
    "mount_google_drive",
]
