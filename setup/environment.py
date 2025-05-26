# filepath: c:\Projects\python-sdk\setup\environment\__init__.py
"""
Environment Management Module
Comprehensive environment setup and validation for the MCP Python SDK.
"""

from pathlib import Path
from typing import Any, Dict, Tuple

from .constants import (
    MIN_PYTHON_VERSION,
    OPTIONAL_PROJECT_PATHS,
    PERFORMANCE_SETTINGS,
    RECOMMENDED_PYTHON_VERSION,
    REQUIRED_PROJECT_PATHS,
)
from .path_utils import get_project_root
from .python_validator import (
    get_environment_info,
    validate_python_environment,
    validate_python_version,
)
from ..types import LogLevel, SetupMode, ValidationDetails, ValidationStatus
from ..vscode.integration import VSCodeIntegrationManager


class EnvironmentManager:
    """
    Comprehensive environment management for MCP Python SDK setup.

    Coordinates Python environment validation, project structure verification,
    and VS Code workspace configuration.
    """

    def __init__(self, workspace_root: Path | None = None, verbose: bool = False) -> None:
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
                print(f"Setting up environment in {mode.value} mode...")

            # Validate Python environment
            python_validation = validate_python_environment()
            if not python_validation.get("valid", False):
                if self.verbose:
                    print("❌ Python environment validation failed")
                success = False

            # Validate project structure
            paths_valid, _ = check_required_paths()
            if not paths_valid:
                if self.verbose:
                    print("❌ Project structure validation failed")
                success = False

            # Setup VS Code workspace
            if mode in (SetupMode.HOST, SetupMode.HYBRID):
                vscode_success = self.vscode_manager.create_all_configurations()
                if not vscode_success:
                    if self.verbose:
                        print("❌ VS Code configuration failed")
                    success = False

            return success

        except Exception as e:
            if self.verbose:
                print(f"❌ Environment setup failed: {e}")
            return False

    def validate_environment(self) -> ValidationDetails:
        """
        Validate complete development environment.

        Returns:
            ValidationDetails with comprehensive validation results
        """
        try:
            warnings = []
            errors = []
            recommendations = []

            # Validate Python environment
            python_validation = validate_python_environment()
            if not python_validation.get("valid", False):
                errors.extend(python_validation.get("errors", []))
                warnings.extend(python_validation.get("warnings", []))
                recommendations.extend(python_validation.get("recommendations", []))

            # Validate project structure
            paths_valid, path_results = check_required_paths()
            if not paths_valid:
                errors.append("Required project paths are missing")

            # Validate VS Code setup
            vscode_validation = self.vscode_manager.validate_all_configurations()
            warnings.extend(vscode_validation.warnings)
            errors.extend(vscode_validation.errors)
            recommendations.extend(vscode_validation.recommendations)

            # Determine overall status
            if errors:
                status = ValidationStatus.ERROR
                is_valid = False
                message = f"Environment validation failed with {len(errors)} errors"
            elif warnings:
                status = ValidationStatus.WARNING
                is_valid = True
                message = f"Environment validation passed with {len(warnings)} warnings"
            else:
                status = ValidationStatus.VALID
                is_valid = True
                message = "Environment validation passed successfully"

            return ValidationDetails(
                is_valid=is_valid,
                status=status,
                message=message,
                warnings=warnings,
                errors=errors,
                recommendations=recommendations,
                metadata={
                    "python_environment": python_validation,
                    "project_structure": path_results,
                    "vscode_setup": vscode_validation.metadata,
                }
            )

        except Exception as e:
            return ValidationDetails(
                is_valid=False,
                status=ValidationStatus.ERROR,
                message=f"Validation failed: {e}",
                warnings=[],
                errors=[str(e)],
                recommendations=["Check environment configuration and try again"],
                metadata={}
            )


def check_required_paths() -> Tuple[bool, Dict[str, Any]]:
    """
    Check if all required project paths exist.

    Returns:
        Tuple of (all_required_exist, path_details)
    """
    try:
        project_root = get_project_root()
        results = {
            "required": [],
            "optional": [],
            "missing_required": [],
            "missing_optional": [],
        }

        # Check required paths
        for path_str in REQUIRED_PROJECT_PATHS:
            path = project_root / path_str
            path_info = {
                "path": path_str,
                "absolute_path": str(path),
                "exists": path.exists(),
                "type": "directory" if path.is_dir() else "file" if path.is_file() else "missing",
            }
            results["required"].append(path_info)
            if not path.exists():
                results["missing_required"].append(path_str)

        # Check optional paths
        for path_str in OPTIONAL_PROJECT_PATHS:
            path = project_root / path_str
            path_info = {
                "path": path_str,
                "absolute_path": str(path),
                "exists": path.exists(),
                "type": "directory" if path.is_dir() else "file" if path.is_file() else "missing",
            }
            results["optional"].append(path_info)
            if not path.exists():
                results["missing_optional"].append(path_str)

        # All required paths must exist
        all_required_exist = len(results["missing_required"]) == 0

        return all_required_exist, results

    except Exception:
        return False, {"error": "Failed to check project paths"}


def get_current_environment_status() -> Dict[str, Any]:
    """
    Get comprehensive current environment status.

    Returns:
        Dictionary with detailed environment information
    """
    try:
        # Get Python environment info
        python_info = get_environment_info()

        # Get project structure info
        paths_valid, path_info = check_required_paths()

        # Get VS Code status
        workspace_root = get_project_root()
        vscode_manager = VSCodeIntegrationManager(workspace_root)
        vscode_status = vscode_manager.get_workspace_status()

        return {
            "workspace_root": str(workspace_root),
            "python_environment": python_info,
            "project_structure": {
                "valid": paths_valid,
                "details": path_info,
            },
            "vscode_workspace": vscode_status,
            "performance_settings": PERFORMANCE_SETTINGS.__dict__,
        }

    except Exception as e:
        return {
            "error": str(e),
            "status": "error"
        }


# Export utility functions for backward compatibility
def create_vscode_directory() -> Path:
    """Create VS Code directory and return its path."""
    from ..vscode.settings import create_vscode_directory
    return create_vscode_directory()


def get_modern_vscode_settings() -> Dict[str, Any]:
    """Get modern VS Code settings configuration."""
    from ..vscode.settings import get_modern_vscode_settings
    return get_modern_vscode_settings()


def should_create_settings_json() -> bool:
    """Check if settings.json should be created."""
    from ..vscode.settings import should_create_settings_json
    return should_create_settings_json()


def get_modern_launch_config() -> Dict[str, Any]:
    """Get modern launch configuration."""
    from ..vscode.launch import get_modern_launch_config
    return get_modern_launch_config()


def get_modern_tasks_config() -> Dict[str, Any]:
    """Get modern tasks configuration."""
    from ..vscode.tasks import get_modern_tasks_config
    return get_modern_tasks_config()


def create_vscode_extensions_config() -> Dict[str, Any]:
    """Create VS Code extensions configuration."""
    from ..vscode.extensions import create_vscode_extensions_config
    return create_vscode_extensions_config()


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
