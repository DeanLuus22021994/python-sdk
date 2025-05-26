"""
Environment Configuration
Centralized environment variable definitions and validation for the MCP Python SDK setup
"""

import sys
from pathlib import Path

# Python version requirements
MIN_PYTHON_VERSION = (3, 10)
RECOMMENDED_PYTHON_VERSION = (3, 11)

# Project structure requirements
REQUIRED_PROJECT_PATHS = ["src/mcp", "pyproject.toml", ".vscode"]

# Optional project paths
OPTIONAL_PROJECT_PATHS = ["tests", "docs", "examples"]

# VS Code configuration
VSCODE_SETTINGS = {
    "python.defaultInterpreterPath": "python",
    "python.analysis.typeCheckingMode": "basic",
    "python.testing.pytestEnabled": True,
    "python.testing.unittestEnabled": False,
    "python.formatting.provider": "black",
    "editor.formatOnSave": True,
    "editor.codeActionsOnSave": {"source.organizeImports": True},
}


def get_project_root() -> Path:
    """
    Get the project root directory.

    Returns:
        Path to the project root directory
    """
    # Start from the current file and go up to find the project root
    current_file = Path(__file__)
    project_root = current_file.parent.parent

    # Verify this is actually the project root by checking for key files
    if (project_root / "pyproject.toml").exists():
        return project_root

    # If not found, try going up one more level
    project_root = project_root.parent
    if (project_root / "pyproject.toml").exists():
        return project_root

    # Fallback to current working directory
    return Path.cwd()


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


def check_required_paths() -> tuple[bool, list[str]]:
    """
    Check if all required project paths exist.

    Returns:
        Tuple of (all_exist, missing_paths)
    """
    project_root = get_project_root()
    missing_paths = [
        path for path in REQUIRED_PROJECT_PATHS if not (project_root / path).exists()
    ]

    return len(missing_paths) == 0, missing_paths


def get_optional_paths_status() -> dict[str, bool]:
    """
    Get the status of optional project paths.

    Returns:
        Dictionary mapping path to existence status
    """
    project_root = get_project_root()
    return {path: (project_root / path).exists() for path in OPTIONAL_PROJECT_PATHS}


def create_vscode_directory() -> Path:
    """
    Create the .vscode directory if it doesn't exist.

    Returns:
        Path to the .vscode directory
    """
    project_root = get_project_root()
    vscode_path = project_root / ".vscode"
    vscode_path.mkdir(exist_ok=True)
    return vscode_path


def should_create_settings_json() -> bool:
    """
    Check if VS Code settings.json should be created.

    Returns:
        True if settings.json doesn't exist or is invalid
    """
    import json

    project_root = get_project_root()
    settings_path = project_root / ".vscode" / "settings.json"

    if not settings_path.exists():
        return True

    try:
        with open(settings_path, encoding="utf-8") as f:
            json.load(f)
        return False  # Valid JSON exists
    except (json.JSONDecodeError, Exception):
        return True  # Invalid or unreadable JSON
