"""
Python Environment Validation
Python version and environment validation utilities
"""

import sys
from pathlib import Path

from .constants import MIN_PYTHON_VERSION, RECOMMENDED_PYTHON_VERSION
from .path_utils import get_project_root


def get_python_version_info() -> tuple[int, int]:
    """
    Get the current Python version as a tuple.

    Returns:
        Tuple of (major, minor) version numbers
    """
    return sys.version_info[:2]


def validate_python_version() -> tuple[bool, str]:
    """
    Validate that the current Python version meets requirements.

    Returns:
        Tuple of (is_valid, message)
    """
    current = get_python_version_info()

    if current >= MIN_PYTHON_VERSION:
        if current >= RECOMMENDED_PYTHON_VERSION:
            status = "✓ Python {}.{} (recommended version)".format(*current)
        else:
            status = "✓ Python {}.{} (meets minimum {}.{})".format(
                *current, *MIN_PYTHON_VERSION
            )
        return True, status
    else:
        status = "✗ Python {}.{} (requires {}.{}+)".format(
            *current, *MIN_PYTHON_VERSION
        )
        return False, status


def get_environment_info() -> dict[str, str]:
    """
    Get relevant environment information.

    Returns:
        Dictionary of environment information
    """
    return {
        "python_version": "{}.{}".format(*get_python_version_info()),
        "python_executable": sys.executable,
        "platform": sys.platform,
        "project_root": str(get_project_root()),
        "working_directory": str(Path.cwd()),
    }


def check_virtual_environment() -> tuple[bool, str]:
    """
    Check if running in a virtual environment.

    Returns:
        Tuple of (is_venv, environment_type)
    """
    # Check for virtual environment indicators
    if hasattr(sys, "real_prefix"):
        return True, "virtualenv"

    if hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix:
        return True, "venv"

    # Check for conda environment
    if "CONDA_DEFAULT_ENV" in sys.prefix or "conda" in sys.executable.lower():
        return True, "conda"

    return False, "system"


def get_python_path_info() -> dict[str, str]:
    """
    Get Python path information for debugging.

    Returns:
        Dictionary with Python path details
    """
    venv_active, venv_type = check_virtual_environment()

    return {
        "executable": sys.executable,
        "prefix": sys.prefix,
        "base_prefix": getattr(sys, "base_prefix", sys.prefix),
        "real_prefix": getattr(sys, "real_prefix", None),
        "virtual_env": venv_active,
        "virtual_env_type": venv_type,
        "python_path": str(Path(sys.executable).parent),
    }


def validate_python_environment() -> tuple[bool, list[str]]:
    """
    Perform comprehensive Python environment validation.

    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []

    # Check Python version
    version_valid, version_msg = validate_python_version()
    if not version_valid:
        issues.append(version_msg)

    # Check if in virtual environment (recommended)
    venv_active, venv_type = check_virtual_environment()
    if not venv_active:
        issues.append(
            "⚠️  Not running in a virtual environment (recommended)"
        )  # Check if pip is available
    try:
        import importlib.util

        pip_spec = importlib.util.find_spec("pip")
        if pip_spec is None:
            issues.append("✗ pip is not available")
    except ImportError:
        issues.append("✗ pip is not available")

    return len(issues) == 0, issues
