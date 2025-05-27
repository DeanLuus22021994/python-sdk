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
    """

    def validate(self) -> Any:
        """
        Perform validation and return detailed results.

        Returns:
            Validation results containing status, errors, warnings,
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

    def setup(self) -> Any:
        """
        Execute setup operations.

        Returns:
            Setup results with success status and details.
        """
        ...

    def cleanup(self) -> bool:
        """
        Clean up setup artifacts and temporary files.

        Returns:
            True if cleanup was successful.
        """
        ...

    def get_status(self) -> dict[str, Any]:
        """
        Get current setup status and information.

        Returns:
            Dictionary containing status information.
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
            path: Configuration file path

        Returns:
            Configuration dictionary
        """
        ...

    def save_config(self, config: dict[str, Any], path: str) -> bool:
        """
        Save configuration to file.

        Args:
            config: Configuration to save
            path: Target file path

        Returns:
            True if save was successful
        """
        ...

    def validate_config(self, config: dict[str, Any]) -> Any:
        """
        Validate configuration structure and values.

        Args:
            config: Configuration to validate

        Returns:
            Validation results
        """
        ...


class EnvironmentProvider(Protocol):
    """
    Protocol for environment information providers.

    Defines the interface for components that gather and provide
    environment information for setup operations.
    """

    def get_environment_info(self) -> Any:
        """
        Get comprehensive environment information.

        Returns:
            Environment information structure
        """
        ...

    def validate_environment(self) -> Any:
        """
        Validate current environment for setup requirements.

        Returns:
            Environment validation results
        """
        ...

    def get_python_info(self) -> Any:
        """
        Get Python-specific environment information.

        Returns:
            Python environment details
        """
        ...


class ProjectStructureValidator(Protocol):
    """
    Protocol for project structure validation.

    Defines the interface for components that validate and analyze
    project directory structure and file organization.
    """

    def validate_structure(self, root_path: str) -> Any:
        """
        Validate project structure at given path.

        Args:
            root_path: Root path to validate

        Returns:
            Structure validation results
        """
        ...

    def get_structure_info(self, root_path: str) -> Any:
        """
        Get detailed information about project structure.

        Args:
            root_path: Root path to analyze

        Returns:
            Project structure information
        """
        ...

    def suggest_improvements(self, root_path: str) -> list[str]:
        """
        Suggest improvements for project structure.

        Args:
            root_path: Root path to analyze

        Returns:
            List of improvement suggestions
        """
        ...
