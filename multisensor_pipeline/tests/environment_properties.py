import os
import sys


def is_running_in_ci() -> bool:
    """Return whether this is running in continuous integration (CI)."""
    this_is_running_in_ci: bool = bool(os.getenv('CI', default=str(False)))

    return this_is_running_in_ci


def is_running_on_linux():
    """Return whether this is running on Linux (Ubuntu, etc.)."""
    this_is_running_under_linux: bool = sys.platform.startswith('linux')

    return this_is_running_under_linux


def is_running_on_macos() -> bool:
    """Return whether this is running on macOS (Darwin)."""
    this_is_running_under_macos: bool = sys.platform.startswith('darwin')

    return this_is_running_under_macos


def is_running_on_windows():
    """Return weather this is running under Windows."""
    this_is_running_on_windows: bool = \
        sys.platform.startswith('win32') or sys.platform.startswith('cygwin')

    return this_is_running_on_windows
