"""
Environment Management Module
Comprehensive environment setup and validation for the MCP Python SDK.
Modern implementation using the validation framework.
"""

from pathlib import Path
from typing import Any

from .environment.constants import REQUIRED_PROJECT_PATHS
from .environment.path_utils import get_project_root
from .environment.python_validator import (
    get_environment_info,
    validate_python_version,
)
from .typings import SetupMode, ValidationDetails, ValidationStatus
from .validation.base import ValidationContext
from .validation.registry import get_global_registry
from .vscode.integration import VSCodeIntegrationManager


class EnvironmentManager:
    """
    Comprehensive environment management for the MCP Python SDK setup.

    Coordinates environment validation, configuration, and optimization
    for development environments following SOLID principles.
    """

    def __init__(self, workspace_root: Path, mode: SetupMode = SetupMode.HOST) -> None:
        self.workspace_root = Path(workspace_root).resolve()
        self.mode = mode
        self.vscode_manager = VSCodeIntegrationManager(self.workspace_root)
        self.registry = get_global_registry()

    def validate_complete_environment(self) -> ValidationDetails:
        """Validate the complete development environment using modern framework."""
        context = ValidationContext(
            workspace_root=str(self.workspace_root),
            environment={},
            config={"mode": self.mode.value},
        )

        # Create composite validator for complete environment
        validators = [
            self.registry.create_validator("python_environment", context),
            self.registry.create_validator("project_structure", context),
            self.registry.create_validator("dependencies", context),
        ]

        # Run all validations
        all_valid = True
        messages = []
        errors = []

        for validator in validators:
            result = validator.validate()
            if not result.is_valid:
                all_valid = False
                if result.message:
                    errors.append(result.message)
            else:
                if result.message:
                    messages.append(result.message)
        status = ValidationStatus.VALID if all_valid else ValidationStatus.ERROR
        message = "; ".join(messages) if all_valid else "; ".join(errors)
        return ValidationDetails(
            is_valid=all_valid,
            status=status,
            message=message,
            component_name="Environment",
            errors=errors if errors else [],
        )
        

    def setup_environment(self) -> bool:
        """Set up the complete development environment."""
        try:
            # Validate environment first
            validation = self.validate_complete_environment()
            if not validation.is_valid:
                return False

            # Set up VS Code configuration
            vscode_success = self.vscode_manager.create_workspace_configuration()

            return vscode_success
        except Exception:
            return False


def check_required_paths() -> tuple[bool, list[str]]:
    """
    Check if all required project paths exist.

    Returns:
        Tuple of (all_exist, missing_paths)
    """
    project_root = get_project_root()
    missing_paths = []

    for path_str in REQUIRED_PROJECT_PATHS:
        path = project_root / path_str
        if not path.exists():
            missing_paths.append(path_str)

    return len(missing_paths) == 0, missing_paths


def get_current_environment_status() -> dict[str, Any]:
    """Get current environment status and information."""
    try:
        env_info = get_environment_info()
        python_valid, python_msg = validate_python_version()
        paths_valid, missing_paths = check_required_paths()

        return {
            "python_version": str(env_info.get("python_version", "unknown")),
            "python_valid": python_valid,
            "python_message": python_msg,
            "virtual_env": env_info.get("virtual_env_active", False),
            "platform": env_info.get("platform_system", "unknown"),
            "paths_valid": paths_valid,
            "missing_paths": missing_paths,
        }
    except Exception as e:
        return {
            "error": str(e),
            "python_valid": False,
            "paths_valid": False,
        }


# Export utility functions for backward compatibility
def create_vscode_directory() -> Path:
    """Create VS Code directory in project root."""
    project_root = get_project_root()
    vscode_dir = project_root / ".vscode"
    vscode_dir.mkdir(exist_ok=True)
    return vscode_dir


def get_modern_vscode_settings() -> dict[str, Any]:
    """Get modern VS Code settings for Python development."""
    return {
        "python.analysis.typeCheckingMode": "basic",
        "python.linting.enabled": True,
        "python.linting.pylintEnabled": False,
        "python.linting.flake8Enabled": True,
        "python.formatting.provider": "black",
        "python.testing.pytestEnabled": True,
        "python.testing.unittestEnabled": False,
        "files.exclude": {
            "**/__pycache__": True,
            "**/.pytest_cache": True,
            "**/.mypy_cache": True,
            "**/dist": True,
            "**/build": True,
        },
        "editor.formatOnSave": True,
        "editor.codeActionsOnSave": {"source.organizeImports": True},
    }


def should_create_settings_json() -> bool:
    """Check if VS Code settings.json should be created."""
    project_root = get_project_root()
    settings_path = project_root / ".vscode" / "settings.json"
    return not settings_path.exists()


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
                "cwd": "${workspaceFolder}",
            },
            {
                "name": "Python: MCP Server",
                "type": "python",
                "request": "launch",
                "program": "${workspaceFolder}/src/mcp/server/__main__.py",
                "console": "integratedTerminal",
                "cwd": "${workspaceFolder}",
                "env": {"PYTHONPATH": "${workspaceFolder}/src"},
            },
        ],
    }


def get_modern_tasks_config() -> dict[str, Any]:
    """Get modern tasks configuration."""
    return {
        "version": "2.0.0",
        "tasks": [
            {
                "label": "Python: Run Tests",
                "type": "shell",
                "command": "python",
                "args": ["-m", "pytest"],
                "group": "test",
                "presentation": {"echo": True, "reveal": "always"},
            }
        ],
    }


def create_vscode_extensions_config() -> dict[str, Any]:
    """Create VS Code extensions configuration."""
    return {
        "recommendations": [
            "ms-python.python",
            "ms-python.vscode-pylance",
            "ms-python.debugpy",
            "ms-python.black-formatter",
            "charliermarsh.ruff",
        ]
    }
