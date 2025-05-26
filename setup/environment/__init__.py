"""
Environment Configuration Package
Modern environment configuration for the MCP Python SDK setup with clean architecture.
"""

from typing import Any

# Import new modular VS Code system
from ..vscode.integration import VSCodeIntegrationManager
from .constants import (
    DEFAULT_CONTAINER_CONFIG,
    MAX_TESTED_PYTHON_VERSION,
    MIN_PYTHON_VERSION,
    OPTIONAL_PROJECT_PATHS,
    PERFORMANCE_SETTINGS,
    RECOMMENDED_EXTENSIONS,
    RECOMMENDED_PYTHON_VERSION,
    REQUIRED_PROJECT_PATHS,
    ContainerConfig,
    PerformanceSettings,
    PythonVersion,
)
from .path_utils import (
    check_required_paths,
    clear_path_cache,
    ensure_directory_exists,
    find_files_by_pattern,
    get_directory_size,
    get_optional_paths_status,
    get_project_root,
    get_relative_path,
    is_project_structure_valid,
)
from .python_validator import (
    check_virtual_environment,
    get_environment_info,
    get_python_version_info,
    validate_python_environment,
    validate_python_version,
)


class EnvironmentManager:
    """
    Centralized environment management following Single Responsibility Principle.
    Modern async-ready implementation with proper error handling.
    """

    def __init__(self) -> None:
        self._cache_initialized = False

    def validate_environment(self) -> tuple[bool, dict[str, str]]:
        """
        Comprehensive environment validation with modern error handling.

        Returns:
            Tuple of (is_valid, validation_details)
        """
        validation_results: dict[str, str] = {}

        # Python version validation
        python_valid, python_msg = validate_python_version()
        validation_results["python_message"] = python_msg

        # Project structure validation
        paths_valid, missing_paths = check_required_paths()
        validation_results["missing_paths"] = (
            ", ".join(missing_paths) if missing_paths else "none"
        )

        # VS Code configuration check with specific exception handling
        try:
            vscode_manager = VSCodeIntegrationManager(get_project_root())
            validation = vscode_manager.validate_workspace()
            validation_results["vscode_status"] = validation.status.value
        except ImportError:
            validation_results["vscode_status"] = "not_available"
        except Exception as e:
            validation_results["vscode_status"] = f"error: {type(e).__name__}"

        overall_valid = python_valid and paths_valid

        return overall_valid, validation_results

    def setup_environment(self) -> bool:
        """
        Complete environment setup with modern Path handling.

        Returns:
            True if setup was successful
        """
        try:
            # Ensure required directories exist
            project_root = get_project_root()

            for required_path in REQUIRED_PROJECT_PATHS:
                path = project_root / required_path
                if not path.exists() and not required_path.endswith((".toml", ".py")):
                    ensure_directory_exists(path)

            # Setup VS Code configuration
            try:
                vscode_manager = VSCodeIntegrationManager(project_root)
                vscode_manager.create_workspace_configuration()
            except ImportError:
                # VS Code integration not available, continue without it
                pass

            return True

        except Exception:
            return False

    def get_status(self) -> dict[str, Any]:
        """
        Get current environment status with proper type handling.

        Returns:
            Status dictionary with environment information
        """
        env_info = get_environment_info()
        optional_paths = get_optional_paths_status()

        # Modern approach: build status dict with proper typing
        status_dict: dict[str, Any] = {
            # Environment information (nested structures preserved)
            **env_info,
            # Project structure validation
            "project_structure_valid": is_project_structure_valid(),
            "optional_paths_available": sum(optional_paths.values()),
            # Cache and performance info
            "cache_initialized": self._cache_initialized,
        }

        return status_dict

    def get_summary(self) -> dict[str, str | int | bool]:
        """
        Get a simplified status summary for compatibility.

        Returns:
            Status dictionary with basic types only
        """
        full_status = self.get_status()

        # Extract and convert to basic types for backward compatibility
        summary: dict[str, str | int | bool] = {
            "python_version": str(
                full_status.get("python", {}).get("version", "unknown")
            ),
            "platform": str(full_status.get("platform", {}).get("system", "unknown")),
            "virtual_env_active": bool(
                full_status.get("virtual_environment", {}).get("active", False)
            ),
            "project_structure_valid": bool(
                full_status.get("project_structure_valid", False)
            ),
            # Use int() for explicit type compatibility with declared return type
            "optional_paths_available": int(
                full_status.get("optional_paths_available", 0)
            ),
            "cache_initialized": bool(full_status.get("cache_initialized", False)),
        }

        return summary


__all__ = [
    # Constants
    "MIN_PYTHON_VERSION",
    "RECOMMENDED_PYTHON_VERSION",
    "MAX_TESTED_PYTHON_VERSION",
    "REQUIRED_PROJECT_PATHS",
    "OPTIONAL_PROJECT_PATHS",
    "PERFORMANCE_SETTINGS",
    "RECOMMENDED_EXTENSIONS",
    "DEFAULT_CONTAINER_CONFIG",
    "PythonVersion",
    "PerformanceSettings",
    "ContainerConfig",
    # Path utilities
    "check_required_paths",
    "clear_path_cache",
    "ensure_directory_exists",
    "find_files_by_pattern",
    "get_directory_size",
    "get_optional_paths_status",
    "get_project_root",
    "get_relative_path",
    "is_project_structure_valid",
    # Python validation
    "get_environment_info",
    "get_python_version_info",
    "validate_python_version",
    "check_virtual_environment",
    "validate_python_environment",
    # VS Code configuration (new modular system)
    "VSCodeIntegrationManager",
    # Main interface
    "EnvironmentManager",
]
