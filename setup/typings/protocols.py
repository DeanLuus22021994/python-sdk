"""
Protocol definitions for type checking and interface compliance.

This module defines protocols that establish contracts for various
setup system components, enabling better type checking and ensuring
consistent interfaces across implementations.
"""

from __future__ import annotations

from typing import Any, Protocol

__all__ = [
    "Validator",
    "SetupManager",
    "ConfigManager",
    "EnvironmentProvider",
    "ProjectStructureValidator",
]


class Validator(Protocol):
    """
    Protocol for validation classes.

    Defines the interface that all validation components must implement
    to ensure consistent validation behavior across the setup system.
    """    def validate(self) -> "ValidationDetails":
        """
        Perform validation and return detailed results.

        Returns:
            ValidationDetails containing validation status, errors, warnings,
            and recommendations for improvement.
        """
        ...

    def is_valid(self) -> bool:
        """
        Quick validation check without detailed results.

        Returns:
            True if validation passes, False otherwise.
        """
        ...


class SetupManager(Protocol):
    """
    Protocol for setup manager classes.

    Defines the interface for components that manage setup operations,
    ensuring consistent setup behavior across different implementation modes.
    """

    def setup(self) -> SetupResult:
        """
        Perform setup and return results.

        Returns:
            Tuple of (success: bool, details: dict) indicating setup outcome
            and providing detailed information about the setup process.
        """
        ...

    def validate(self) -> ValidationDetails:
        """
        Validate current state before or after setup.

        Returns:
            ValidationDetails containing current validation status.
        """
        ...

    def cleanup(self) -> bool:
        """
        Clean up resources and temporary files.

        Returns:
            True if cleanup was successful, False otherwise.
        """
        ...


class ConfigManager(Protocol):
    """
    Protocol for configuration managers.

    Defines the interface for components that handle configuration
    loading, saving, and validation across the setup system.
    """

    def load_config(self) -> dict[str, Any]:
        """
        Load configuration from file or defaults.

        Returns:
            Dictionary containing configuration settings.
        """
        ...

    def save_config(self, config: dict[str, Any]) -> bool:
        """
        Save configuration to file.

        Args:
            config: Configuration dictionary to save.

        Returns:
            True if configuration was saved successfully, False otherwise.
        """
        ...

    def validate_config(self, config: dict[str, Any]) -> ValidationDetails:
        """
        Validate configuration structure and values.

        Args:
            config: Configuration dictionary to validate.

        Returns:
            ValidationDetails containing validation results.
        """
        ...

    def get_default_config(self) -> dict[str, Any]:
        """
        Get default configuration values.

        Returns:
            Dictionary containing default configuration settings.
        """
        ...


class EnvironmentProvider(Protocol):
    """
    Protocol for environment information providers.

    Defines the interface for components that gather and provide
    information about the development environment.
    """

    def get_python_info(self) -> dict[str, Any]:
        """
        Get Python environment information.

        Returns:
            Dictionary containing Python version, executable path,
            virtual environment status, and other relevant information.
        """
        ...

    def get_system_info(self) -> dict[str, Any]:
        """
        Get system information.

        Returns:
            Dictionary containing operating system, architecture,
            and platform-specific information.
        """
        ...

    def get_package_manager_info(self) -> dict[str, Any]:
        """
        Get package manager availability and versions.

        Returns:
            Dictionary containing information about available package
            managers (pip, conda, uv, poetry) and their versions.
        """
        ...

    def refresh_environment(self) -> None:
        """
        Refresh cached environment information.

        Forces re-detection of environment characteristics,
        useful when the environment has been modified.
        """
        ...


class ProjectStructureValidator(Protocol):
    """
    Protocol for project structure validation.

    Defines the interface for components that validate and analyze
    project directory structure and file organization.
    """

    def validate_structure(self) -> ValidationDetails:
        """
        Validate project directory structure.

        Returns:
            ValidationDetails containing structure validation results.
        """
        ...

    def check_required_files(self) -> dict[str, bool]:
        """
        Check presence of required project files.

        Returns:
            Dictionary mapping file paths to their existence status.
        """
        ...

    def check_optional_files(self) -> dict[str, bool]:
        """
        Check presence of optional project files.

        Returns:
            Dictionary mapping optional file paths to their existence status.
        """
        ...

    def get_project_metrics(self) -> dict[str, int | float]:
        """
        Get project size and complexity metrics.

        Returns:
            Dictionary containing metrics like file count, directory count,
            total size, and code complexity indicators.
        """
        ...

    def suggest_improvements(self) -> list[str]:
        """
        Suggest project structure improvements.

        Returns:
            List of recommendations for improving project organization.
        """
        ...
