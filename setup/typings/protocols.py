"""
Protocol definitions for type checking and interface compliance.

This module defines protocols that establish contracts for various
setup system components, enabling better type checking and ensuring
consistent interfaces across implementations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    # Import actual types for type checking
    try:
        from .core import SetupResult
        from .environment import (
            EnvironmentInfo,
            ProjectStructureInfo,
            PythonVersion,
            ValidationDetails,
        )
    except ImportError:
        # Fallback type aliases if imports fail
        SetupResult = Any
        ValidationDetails = Any
        EnvironmentInfo = Any
        PythonVersion = Any
        ProjectStructureInfo = Any
else:
    # Runtime type aliases to prevent name errors
    SetupResult = Any
    ValidationDetails = Any
    EnvironmentInfo = Any
    PythonVersion = Any
    ProjectStructureInfo = Any

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
    """

    def validate(self) -> ValidationDetails:
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
            SetupResult tuple containing success status and operation details.
        """
        ...

    def cleanup(self) -> bool:
        """
        Clean up resources and temporary files.

        Returns:
            True if cleanup was successful, False otherwise.
        """
        ...

    def get_status(self) -> dict[str, Any]:
        """
        Get current setup status and configuration.

        Returns:
            Dictionary containing current setup state and configuration.
        """
        ...


class ConfigManager(Protocol):
    """
    Protocol for configuration management.

    Defines the interface for components that handle configuration
    loading, validation, and persistence.
    """

    def load_config(self, path: str) -> dict[str, Any]:
        """
        Load configuration from file.

        Args:
            path: Path to configuration file.

        Returns:
            Dictionary containing configuration data.
        """
        ...

    def save_config(self, config: dict[str, Any], path: str) -> bool:
        """
        Save configuration to file.

        Args:
            config: Configuration data to save.
            path: Path where to save configuration.

        Returns:
            True if save was successful, False otherwise.
        """
        ...

    def validate_config(self, config: dict[str, Any]) -> ValidationDetails:
        """
        Validate configuration data.

        Args:
            config: Configuration data to validate.

        Returns:
            ValidationDetails containing validation results.
        """
        ...


class EnvironmentProvider(Protocol):
    """
    Protocol for environment information providers.

    Defines the interface for components that gather and provide
    environment information for setup operations.
    """

    def get_environment_info(self) -> EnvironmentInfo:
        """
        Gather comprehensive environment information.

        Returns:
            EnvironmentInfo containing system and environment details.
        """
        ...

    def validate_environment(self) -> ValidationDetails:
        """
        Validate current environment for setup requirements.

        Returns:
            ValidationDetails containing environment validation results.
        """
        ...

    def get_python_info(self) -> PythonVersion:
        """
        Get Python version information.

        Returns:
            PythonVersion containing Python version details.
        """
        ...


class ProjectStructureValidator(Protocol):
    """
    Protocol for project structure validation.

    Defines the interface for components that validate and analyze
    project directory structure and file organization.
    """

    def validate_structure(self, root_path: str) -> ValidationDetails:
        """
        Validate project directory structure.

        Args:
            root_path: Root directory of the project to validate.

        Returns:
            ValidationDetails containing structure validation results.
        """
        ...

    def get_structure_info(self, root_path: str) -> ProjectStructureInfo:
        """
        Analyze and return project structure information.

        Args:
            root_path: Root directory of the project to analyze.

        Returns:
            ProjectStructureInfo containing detailed structure analysis.
        """
        ...

    def suggest_improvements(self, root_path: str) -> list[str]:
        """
        Suggest improvements for project structure.

        Args:
            root_path: Root directory of the project to analyze.

        Returns:
            List of improvement suggestions.
        """
        ...
