"""
Environment Management Module
Comprehensive environment setup and validation for the MCP Python SDK.
"""

from pathlib import Path
from typing import Any

from .environment.constants import (
    PERFORMANCE_SETTINGS,
    REQUIRED_PROJECT_PATHS,
)
from .environment.path_utils import get_project_root
from .environment.python_validator import (
    get_environment_info,
    validate_python_environment,
    validate_python_version,
)
from .types import SetupMode, ValidationDetails, ValidationStatus
from .vscode.integration import VSCodeIntegrationManager


class EnvironmentManager:
    """
    Comprehensive environment management for MCP Python SDK setup.

    Coordinates Python environment validation, project structure verification,
    and VS Code workspace configuration.
    """

    def __init__(
        self, workspace_root: Path | None = None, verbose: bool = False
    ) -> None:
        """
        Initialize environment manager.

        Args:
            workspace_root: Root directory of the workspace (auto-detected if None)
            verbose: Enable verbose logging
        """
        self.workspace_root = Path(workspace_root or get_project_root()).resolve()
        self.verbose = verbose
        self.vscode_manager = VSCodeIntegrationManager(self.workspace_root)

    def setup_environment(self, mode: SetupMode = SetupMode.HOST) -> bool:
        """
        Set up complete development environment.

        Args:
            mode: Setup mode (host, docker, or hybrid)

        Returns:
            True if setup completed successfully
        """
        try:
            success = True

            if self.verbose:
                print(f"Setting up environment in {mode.value} mode")

            # Validate Python environment
            python_validation = validate_python_environment()
            if not python_validation.get("valid", False):
                print("❌ Python environment validation failed")
                success = False

            return success

        except Exception as e:
            if self.verbose:
                print(f"Environment setup failed: {e}")
            return False

    def validate_environment(self) -> ValidationDetails:
        """
        Validate complete development environment.

        Returns:
            ValidationDetails with comprehensive validation results
        """
        try:
            warnings: list[str] = []
            errors: list[str] = []
            recommendations: list[str] = []

            # Validate Python
            python_valid, python_msg = validate_python_version()
            if not python_valid:
                errors.append(python_msg)

            # Validate project structure
            paths_valid, missing_paths = check_required_paths()
            if not paths_valid:
                errors.extend(
                    [f"Missing required path: {path}" for path in missing_paths]
                )

            # Determine overall status
            if errors:
                status = ValidationStatus.ERROR
                is_valid = False
            elif warnings:
                status = ValidationStatus.WARNING
                is_valid = True
            else:
                status = ValidationStatus.VALID
                is_valid = True

            return ValidationDetails(
                is_valid=is_valid,
                status=status,
                message="Environment validation complete",
                warnings=warnings,
                errors=errors,
                recommendations=recommendations,
                metadata={"workspace_root": str(self.workspace_root)},
            )

        except Exception as e:
            return ValidationDetails(
                is_valid=False,
                status=ValidationStatus.ERROR,
                message=f"Validation failed: {e}",
                errors=[str(e)],
            )


def check_required_paths() -> tuple[bool, list[str]]:
    """
    Check if all required project paths exist.

    Returns:
        Tuple of (all_required_exist, missing_paths)
    """
    try:
        project_root = get_project_root()
        missing_paths: list[str] = []

        # Check required paths
        for path_str in REQUIRED_PROJECT_PATHS:
            path = project_root / path_str
            if not path.exists():
                missing_paths.append(path_str)

        # All required paths must exist
        all_required_exist = len(missing_paths) == 0

        return all_required_exist, missing_paths

    except Exception:
        return False, ["Unable to check project structure"]


def get_current_environment_status() -> dict[str, Any]:
    """
    Get comprehensive current environment status.

    Returns:
        Dictionary with detailed environment information
    """
    try:
        # Get Python environment info
        python_info = get_environment_info()

        # Get project structure info
        paths_valid, missing_paths = check_required_paths()

        # Get VS Code status
        workspace_root = get_project_root()
        vscode_manager = VSCodeIntegrationManager(workspace_root)
        vscode_status = vscode_manager.get_workspace_status()

        return {
            "workspace_root": str(workspace_root),
            "python_environment": python_info,
            "project_structure": {
                "valid": paths_valid,
                "missing_paths": missing_paths,
            },
            "vscode_workspace": vscode_status,
            "performance_settings": PERFORMANCE_SETTINGS.__dict__,
        }

    except Exception as e:
        return {"error": str(e), "status": "error"}


# Export utility functions for backward compatibility
def create_vscode_directory() -> Path:
    """Create VS Code directory and return its path."""
    from .vscode.settings import VSCodeSettingsManager

    project_root = get_project_root()
    settings_manager = VSCodeSettingsManager(project_root)
    settings_manager.vscode_dir.mkdir(exist_ok=True)
    return settings_manager.vscode_dir


def get_modern_vscode_settings() -> dict[str, Any]:
    """Get modern VS Code settings configuration."""
    from .vscode.settings import VSCodeSettingsManager

    project_root = get_project_root()
    settings_manager = VSCodeSettingsManager(project_root)
    return settings_manager.get_modern_settings()


def should_create_settings_json() -> bool:
    """Check if settings.json should be created."""
    from .vscode.settings import VSCodeSettingsManager

    project_root = get_project_root()
    settings_manager = VSCodeSettingsManager(project_root)
    return settings_manager.should_create_settings()


def get_modern_launch_config() -> dict[str, Any]:
    """Get modern launch configuration."""
    from .vscode.launch import VSCodeLaunchManager

    project_root = get_project_root()
    launch_manager = VSCodeLaunchManager(project_root)
    return launch_manager.get_launch_config()


def get_modern_tasks_config() -> dict[str, Any]:
    """Get modern tasks configuration."""
    from .vscode.tasks import VSCodeTasksManager

    project_root = get_project_root()
    tasks_manager = VSCodeTasksManager(project_root)
    return tasks_manager.get_tasks_config()


def create_vscode_extensions_config() -> dict[str, Any]:
    """Create VS Code extensions configuration."""
    from .vscode.extensions import VSCodeExtensionsManager

    project_root = get_project_root()
    extensions_manager = VSCodeExtensionsManager(project_root)
    return extensions_manager.get_extensions_config()


__all__ = [
    "EnvironmentManager",
    "check_required_paths",
    "get_current_environment_status",
    "validate_python_version",
    "validate_python_environment",
    "get_environment_info",
    "create_vscode_directory",
    "get_modern_vscode_settings",
    "should_create_settings_json",
    "get_modern_launch_config",
    "get_modern_tasks_config",
    "create_vscode_extensions_config",
]
