"""Environment validation module for Python SDK setup."""

import os
import platform
import sys
from pathlib import Path

try:
    from setup.environment import (
        check_required_paths,
        get_project_root,
        validate_python_version,
    )
except ImportError:

    def validate_python_version() -> tuple[bool, str]:
        """Check if current Python version is compatible."""
        current = sys.version_info[:2]
        min_version = (3, 8)
        if current >= min_version:
            msg = f"✓ Python {current[0]}.{current[1]} (meets minimum)"
            return True, msg
        msg = (
            f"✗ Python {current[0]}.{current[1]} "
            f"(requires {min_version[0]}.{min_version[1]}+)"
        )
        return False, msg

    def check_required_paths() -> tuple[bool, list[str]]:
        """Check if required project paths exist."""
        base_path = os.getcwd()
        required = ["src/mcp", "pyproject.toml", ".vscode"]
        missing = [
            path
            for path in required
            if not os.path.exists(os.path.join(base_path, path))
        ]
        return len(missing) == 0, missing

    def get_project_root() -> Path:
        """Get project root directory."""
        return Path.cwd()


def validate_environment() -> tuple[bool, dict[str, str | bool]]:
    """
    Validate the Python environment for MCP SDK compatibility.

    Returns:
        Tuple containing:
        - bool: True if environment is valid
        - Dict: Environment details and validation results
    """
    # Check Python version
    python_valid, _ = validate_python_version()

    # Check project structure
    structure_valid, missing_paths = check_required_paths()

    env_info: dict[str, str | bool] = {
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
        "platform": platform.system(),
        "architecture": platform.machine(),
        "python_compatible": python_valid,
        "project_structure_valid": structure_valid,
        "missing_paths": ", ".join(missing_paths) if missing_paths else "none",
        "virtual_env_active": (
            hasattr(sys, "real_prefix")
            or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix)
        ),
    }

    # Check environment requirements
    is_valid = python_valid and structure_valid

    return is_valid, env_info


def check_python_version() -> bool:
    """
    Check if Python version meets minimum requirements.

    Returns:
        bool: True if Python version is compatible
    """
    valid, _ = validate_python_version()
    return valid


def validate_project_directory() -> bool:
    """
    Validate the current project directory structure.

    Returns:
        bool: True if project structure is valid
    """
    valid, _ = check_required_paths()
    return valid


def get_environment_info() -> dict[str, str | bool]:
    """
    Get detailed environment information.

    Returns:
        Dict: Environment details including Python version, platform, etc.
    """
    _, env_info = validate_environment()
    return env_info
