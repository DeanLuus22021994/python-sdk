"""
Environment Configuration Package
Decomposed environment configuration for the MCP Python SDK setup
"""

# Use relative imports to avoid circular imports
from .constants import (
    MIN_PYTHON_VERSION,
    OPTIONAL_PROJECT_PATHS,
    RECOMMENDED_PYTHON_VERSION,
    REQUIRED_PROJECT_PATHS,
)
from .path_utils import (
    check_required_paths,
    ensure_directory_exists,
    get_optional_paths_status,
    get_project_root,
)
from .python_validator import (
    check_virtual_environment,
    get_environment_info,
    get_python_version_info,
    validate_python_environment,
    validate_python_version,
)
from .vscode_config import (
    create_modern_vscode_settings,
    create_vscode_directory,
    create_vscode_extensions_config,
    get_modern_launch_config,
    get_modern_tasks_config,
    get_modern_vscode_settings,
    get_vscode_settings,
    should_create_settings_json,
)

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
    # VS Code configuration
    "get_vscode_settings",
    "get_modern_vscode_settings",
    "create_vscode_directory",
    "should_create_settings_json",
    "create_modern_vscode_settings",
    "get_modern_launch_config",
    "get_modern_tasks_config",
    "create_vscode_extensions_config",
]
