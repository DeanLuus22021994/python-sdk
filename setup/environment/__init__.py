"""
Environment Configuration Package
Modern environment configuration for the MCP Python SDK setup with clean architecture.
"""

# Core environment components
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
    LogLevel,
    PerformanceSettings,
    PythonVersion,
    SetupMode,
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

    def validate_environment(self) -> tuple[bool, dict[str, bool | str]]:
        """
        Comprehensive environment validation.

        Returns:
            Tuple of (is_valid, validation_details)
        """
        validation_results = {}

        # Python version validation
        python_valid, python_msg = validate_python_version()
        validation_results["python_version"] = python_valid
        validation_results["python_message"] = python_msg

        # Project structure validation
        paths_valid, missing_paths = check_required_paths()
        validation_results["project_structure"] = paths_valid
        validation_results["missing_paths"] = (
            missing_paths  # VS Code configuration check
        )
        try:
            vscode_manager = VSCodeIntegrationManager(get_project_root())
            validation = vscode_manager.validate_all_configurations()
            validation_results["vscode_config"] = validation.is_valid
            validation_results["vscode_status"] = validation.status.value
        except Exception:
            validation_results["vscode_config"] = False
            validation_results["vscode_status"] = "error"

        overall_valid = (
            python_valid and paths_valid and validation_results["vscode_config"]
        )

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
                    ensure_directory_exists(path)  # Setup VS Code configuration
            vscode_manager = VSCodeIntegrationManager(project_root)
            vscode_manager.create_all_configurations()

            return True

        except Exception:
            return False

    def get_status(self) -> dict[str, bool | str | int]:
        """
        Get current environment status.

        Returns:
            Status dictionary with environment information
        """
        return {
            **get_environment_info(),
            "project_structure_valid": is_project_structure_valid(),
            "optional_paths": get_optional_paths_status(),
        }


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
    "SetupMode",
    "LogLevel",
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
    # Main interface
    "EnvironmentManager",
]

__version__ = "1.0.0"
__all__ = [
    # Constants
    "MIN_PYTHON_VERSION",
    "RECOMMENDED_PYTHON_VERSION",
    "REQUIRED_PROJECT_PATHS",
    "OPTIONAL_PROJECT_PATHS",
    # Path utilities
    "get_project_root",
    "check_required_paths",
    "get_optional_paths_status",
    "ensure_directory_exists",
    # Python validation
    "get_python_version_info",
    "validate_python_version",
    "get_environment_info",
    "check_virtual_environment",
    "validate_python_environment",
    # VS Code configuration (new modular system)
    "VSCodeIntegrationManager",
]
