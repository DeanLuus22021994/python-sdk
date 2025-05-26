"""
Environment Configuration Package
Modern environment configuration for the MCP Python SDK setup with clean architecture.
"""

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


# Environment Manager - Main interface for environment operations
class EnvironmentManager:
    """
    Centralized environment management following Single Responsibility Principle.
    """

    def __init__(self) -> None:
        self._cache_initialized = False

    def validate_environment(self) -> tuple[bool, dict[str, str]]:
        """
        Comprehensive environment validation.

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

        # VS Code configuration check
        try:
            vscode_manager = VSCodeIntegrationManager(get_project_root())
            validation = vscode_manager.validate_workspace()
            validation_results["vscode_status"] = validation.status.value
        except Exception:
            validation_results["vscode_status"] = "error"

        overall_valid = python_valid and paths_valid

        return overall_valid, validation_results

    def setup_environment(self) -> bool:
        """
        Complete environment setup.

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
            vscode_manager = VSCodeIntegrationManager(project_root)
            vscode_manager.create_workspace_configuration()

            return True

        except Exception:
            return False

    def get_status(self) -> dict[str, str | int | bool]:
        """
        Get current environment status.

        Returns:
            Status dictionary with environment information
        """
        env_info = get_environment_info()
        optional_paths = get_optional_paths_status()

        # Convert all values to appropriate types for the return type
        status_dict: dict[str, str | int | bool] = {}

        # Handle nested dict values by flattening or converting to strings
        for key, value in env_info.items():
            if isinstance(value, dict):
                # Convert nested dict to a string representation
                status_dict[key] = str(value)
            elif isinstance(value, str | int | bool):
                status_dict[key] = value
            else:
                # Convert other types to string
                status_dict[key] = str(value)

        # Add additional status information
        status_dict["project_structure_valid"] = is_project_structure_valid()
        status_dict["optional_paths_available"] = len(
            [p for p in optional_paths.values() if p]
        )

        return status_dict


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
