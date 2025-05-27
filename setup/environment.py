"""
Environment Management Module
Comprehensive environment setup and validation for the MCP Python SDK.
Modern implementation using the validation framework.
"""

from pathlib import Path
from typing import Any

from .environment.constants import REQUIRED_PROJECT_PATHS
from .environment.utils import get_project_root
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
        # Use modern validation framework
        from .environment.manager import EnvironmentManager as ModernManager

        manager = ModernManager()
        env_info = manager.get_environment_info()

        # Get validation results
        context = ValidationContext(
            workspace_root=str(get_project_root()),
            environment={},
        )

        registry = get_global_registry()
        python_validator = registry.create_validator("python_environment", context)
        python_result = python_validator.validate()

        paths_valid, missing_paths = check_required_paths()

        return {
            "python_version": str(env_info.python_version),
            "python_valid": python_result.is_valid,
            "python_message": python_result.message,
            "virtual_env": env_info.virtual_env_active,
            "platform": env_info.platform_system,
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


# Legacy compatibility imports - bridge to modern validation
def validate_python_version() -> tuple[bool, str]:
    """Legacy function for Python version validation."""
    try:
        context = ValidationContext(
            workspace_root=str(get_project_root()),
            environment={},
        )

        registry = get_global_registry()
        validator = registry.create_validator("python_environment", context)
        result = validator.validate()

        return result.is_valid, result.message
    except Exception as e:
        return False, f"Validation failed: {e}"


def get_environment_info() -> dict[str, Any]:
    """Legacy function for environment info."""
    try:
        from .environment.manager import EnvironmentManager as ModernManager

        manager = ModernManager()
        env_info = manager.get_environment_info()

        return {
            "python_version": env_info.python_version,
            "virtual_env_active": env_info.virtual_env_active,
            "platform_system": env_info.platform_system,
            "architecture": env_info.architecture,
        }
    except Exception:
        import platform
        import sys

        # Fallback to basic info
        return {
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "virtual_env_active": hasattr(sys, "real_prefix")
            or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix),
            "platform_system": platform.system(),
            "architecture": platform.machine(),
        }
