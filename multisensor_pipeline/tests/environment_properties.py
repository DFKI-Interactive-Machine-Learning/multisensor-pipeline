import os


def is_running_in_ci() -> bool:
    """Return whether this is running in continuous integration (CI)."""
    this_is_running_in_ci: bool = bool(os.getenv('CI', default=str(False)))

    return this_is_running_in_ci
