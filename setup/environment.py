"""
Environment Configuration
Centralized environment variable definitions and validation for the MCP Python SDK setup
"""

import json
import sys
from pathlib import Path
from typing import Any

from .constants import (
    MIN_PYTHON_VERSION,
    OPTIONAL_PROJECT_PATHS,
    RECOMMENDED_PYTHON_VERSION,
    REQUIRED_PROJECT_PATHS,
    PythonVersion,
)

# Project structure requirements
VSCODE_SETTINGS: dict[str, Any] = {
    "python.defaultInterpreterPath": "python",
    "python.analysis.autoImportCompletions": True,
    "python.analysis.typeCheckingMode": "basic",
    "python.analysis.autoSearchPaths": True,
    "python.analysis.diagnosticMode": "workspace",
    "files.exclude": {
        "**/__pycache__": True,
        "**/*.pyc": True,
        ".pytest_cache": True,
        "*.egg-info": True,
        "**/.mypy_cache": True,
        "**/.ruff_cache": True,
    },
    "python.testing.pytestEnabled": True,
    "python.testing.unittestEnabled": False,
    "python.testing.pytestArgs": ["tests", "-v", "--tb=short"],
    "python.testing.autoTestDiscoverOnSaveEnabled": True,
    "[python]": {
        "editor.defaultFormatter": "ms-python.black-formatter",
        "editor.formatOnSave": True,
        "editor.codeActionsOnSave": {
            "source.organizeImports": "explicit",
            "source.fixAll.ruff": "explicit",
        },
        "editor.rulers": [88],
        "editor.tabSize": 4,
        "editor.insertSpaces": True,
    },
    "python.linting.enabled": True,
    "python.linting.ruffEnabled": True,
    "python.linting.mypyEnabled": True,
    "python.linting.pylintEnabled": False,
    "python.linting.flake8Enabled": False,
    "ruff.enable": True,
    "ruff.organizeImports": True,
    "ruff.fixAll": True,
    "isort.args": ["--profile", "black"],
    "mypy-type-checker.importStrategy": "fromEnvironment",
    "mypy-type-checker.args": ["--strict", "--ignore-missing-imports"],
}


def get_vscode_settings() -> dict[str, Any]:
    """Get the default VS Code settings."""
    return VSCODE_SETTINGS


def get_modern_vscode_settings() -> dict[str, Any]:
    """Get modern VS Code settings optimized for MCP Python SDK development."""
    return {
        **VSCODE_SETTINGS,
        "python.terminal.activateEnvironment": True,
        "python.terminal.activateEnvInCurrentTerminal": True,
        "editor.minimap.enabled": False,
        "editor.wordWrap": "on",
        "editor.lineNumbers": "on",
        "terminal.integrated.defaultProfile.windows": "PowerShell",
        "git.autofetch": True,
        "git.enableSmartCommit": True,
        "files.autoSave": "afterDelay",
        "files.autoSaveDelay": 1000,
    }


def get_modern_launch_config() -> dict[str, Any]:
    """Get modern launch configuration for debugging."""
    return {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "Python: Current File",
                "type": "python",
                "request": "launch",
                "program": "${file}",
                "console": "integratedTerminal",
                "justMyCode": True,
            },
            {
                "name": "Python: Run Tests",
                "type": "python",
                "request": "launch",
                "module": "pytest",
                "args": ["tests/", "-v"],
                "console": "integratedTerminal",
                "justMyCode": False,
            },
            {
                "name": "Python: Setup Script",
                "type": "python",
                "request": "launch",
                "program": "${workspaceFolder}/setup.py",
                "console": "integratedTerminal",
                "justMyCode": True,
            },
        ],
    }


def get_modern_tasks_config() -> dict[str, Any]:
    """Get modern tasks configuration for build and test automation."""
    return {
        "version": "2.0.0",
        "tasks": [
            {
                "label": "Install Dependencies",
                "type": "shell",
                "command": "uv",
                "args": ["sync"],
                "group": "build",
                "presentation": {"echo": True, "reveal": "always", "panel": "new"},
                "problemMatcher": [],
            },
            {
                "label": "Run Tests",
                "type": "shell",
                "command": "uv",
                "args": ["run", "pytest", "tests/", "-v"],
                "group": {"kind": "test", "isDefault": True},
                "presentation": {"echo": True, "reveal": "always", "panel": "new"},
                "problemMatcher": [],
            },
            {
                "label": "Format Code",
                "type": "shell",
                "command": "uv",
                "args": ["run", "black", "src/", "tests/", "setup/"],
                "group": "build",
                "presentation": {"echo": True, "reveal": "always", "panel": "new"},
                "problemMatcher": [],
            },
            {
                "label": "Lint Code",
                "type": "shell",
                "command": "uv",
                "args": ["run", "ruff", "check", "src/", "tests/", "setup/"],
                "group": "build",
                "presentation": {"echo": True, "reveal": "always", "panel": "new"},
                "problemMatcher": [],
            },
        ],
    }


def create_vscode_extensions_config() -> dict[str, Any]:
    """Get recommended VS Code extensions configuration."""
    return {
        "recommendations": [
            "ms-python.python",
            "ms-python.black-formatter",
            "ms-python.mypy-type-checker",
            "charliermarsh.ruff",
            "ms-vscode.vscode-json",
            "redhat.vscode-yaml",
            "ms-python.pytest",
            "ms-vscode.test-adapter-converter",
            "eamodio.gitlens",
            "ms-vscode.vscode-docker",
            "ms-vscode.powershell",
        ],
        "unwantedRecommendations": [
            "ms-python.pylint",
            "ms-python.flake8",
        ],
    }


def get_project_root() -> Path:
    """
    Get the project root directory.

    Returns:
        Path to the project root directory
    """
    # Start from the current file and go up to find the project root
    current_file = Path(__file__)
    project_root = current_file.parent.parent.parent

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
    current = PythonVersion(*get_python_version_info())

    if current >= MIN_PYTHON_VERSION:
        if current >= RECOMMENDED_PYTHON_VERSION:
            return True, f"Python {current} meets all requirements"
        else:
            return (
                True,
                f"Python {current} meets minimum requirements (recommended: {RECOMMENDED_PYTHON_VERSION})",
            )
    else:
        return False, f"Python {current} is too old (minimum: {MIN_PYTHON_VERSION})"


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
    project_root = get_project_root()
    settings_path = project_root / ".vscode" / "settings.json"

    if not settings_path.exists():
        return True

    try:
        with open(settings_path, encoding="utf-8") as f:
            json.load(f)
        return False  # File exists and is valid JSON
    except (json.JSONDecodeError, Exception):
        return True  # File exists but is invalid


def create_modern_vscode_settings() -> bool:
    """
    Create modern VS Code settings files.

    Returns:
        True if settings were created successfully, False otherwise
    """
    try:
        vscode_dir = create_vscode_directory()
        settings_path = vscode_dir / "settings.json"

        if should_create_settings_json():
            settings = get_modern_vscode_settings()
            with open(settings_path, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2)

        # Create other configuration files
        launch_path = vscode_dir / "launch.json"
        if not launch_path.exists():
            launch_config = get_modern_launch_config()
            with open(launch_path, "w", encoding="utf-8") as f:
                json.dump(launch_config, f, indent=2)

        tasks_path = vscode_dir / "tasks.json"
        if not tasks_path.exists():
            tasks_config = get_modern_tasks_config()
            with open(tasks_path, "w", encoding="utf-8") as f:
                json.dump(tasks_config, f, indent=2)

        extensions_path = vscode_dir / "extensions.json"
        if not extensions_path.exists():
            extensions_config = create_vscode_extensions_config()
            with open(extensions_path, "w", encoding="utf-8") as f:
                json.dump(extensions_config, f, indent=2)

        return True
    except Exception:
        return False
