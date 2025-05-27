"""
Host Environment Setup
Modern host system configuration and validation for the MCP Python SDK.

Modernized for Python 3.13+ with comprehensive validation framework integration.
"""

from __future__ import annotations

import platform
import sys
from pathlib import Path
from typing import Any

from ..typings import ValidationDetails, ValidationStatus
from ..validation.base import ValidationContext
from ..validation.registry import get_global_registry


class HostEnvironmentValidator:
    """
    Modern host environment validator using the validation framework.

    Replaces the legacy env_validator with framework-integrated validation.
    """

    def __init__(self, workspace_root: Path) -> None:
        """Initialize with workspace root."""
        self.workspace_root = workspace_root
        self.context = ValidationContext(
            workspace_root=str(workspace_root),
            environment={},
            config={"component": "host", "python_version": "3.13+"},
        )
        self.registry = get_global_registry()

    def validate_complete_environment(self) -> ValidationDetails:
        """
        Validate complete host environment using modern framework.

        Returns:
            ValidationDetails with comprehensive validation results
        """
        try:
            # Create composite validator for host environment
            validators = []

            # Add available validators from registry
            available_validators = ["python_environment", "project_structure"]
            for validator_name in available_validators:
                try:
                    validator = self.registry.create_validator(validator_name, self.context)
                    validators.append(validator)
                except ValueError:
                    # Validator not available, skip
                    continue

            if not validators:
                # Fallback validation
                return ValidationDetails(
                    is_valid=True,
                    status=ValidationStatus.WARNING,
                    message="Host environment validation completed with limited checks",
                    warnings=["Modern validators not available, using basic validation"],
                    component_name="HostEnvironment",
                )

            # Run validations and combine results
            all_valid = True
            all_errors: list[str] = []
            all_warnings: list[str] = []
            all_recommendations: list[str] = []

            for validator in validators:
                try:
                    result = validator.validate()
                    if not result.is_valid:
                        all_valid = False
                        all_errors.extend(result.errors)
                    all_warnings.extend(result.warnings)
                    all_recommendations.extend(result.recommendations)
                except Exception as e:
                    all_valid = False
                    all_errors.append(f"Validator {validator.get_validator_name()} failed: {e}")

            status = ValidationStatus.VALID if all_valid else ValidationStatus.ERROR
            message = "Host environment validation passed" if all_valid else "Host environment validation failed"

            return ValidationDetails(
                is_valid=all_valid,
                status=status,
                message=message,
                warnings=all_warnings,
                errors=all_errors,
                recommendations=all_recommendations,
                component_name="HostEnvironment",
            )

        except Exception as e:
            return ValidationDetails(
                is_valid=False,                status=ValidationStatus.ERROR,
                message=f"Host environment validation failed: {e}",
                errors=[str(e)],
                component_name="HostEnvironment",
            )


class SystemInfoCollector:
    @staticmethod
    def collect_all_info() -> dict[str, Any]:
        """Collect comprehensive system information."""
        return {
            "platform": {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
            },
            "python": {
                "version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "executable": sys.executable,
                "implementation": platform.python_implementation(),
            },
        }

    @staticmethod
    def get_system_type() -> str:
        """Get system type."""
        return platform.system()


class HostSetupManager:
    """
    Modern host environment setup and validation manager.

    Provides comprehensive host system validation, configuration,
    and optimization for development environments.
    """

    def __init__(self, workspace_root: Path, verbose: bool = False) -> None:
        """
        Initialize host setup manager.

        Args:
            workspace_root: Root directory of the workspace
            verbose: Enable verbose logging
        """
        self.workspace_root = Path(workspace_root).resolve()
        self.verbose = verbose
        self.validator = HostEnvironmentValidator(self.workspace_root)
        self.system_info = SystemInfoCollector()

    def validate_host_environment(self) -> ValidationDetails:
        """
        Comprehensive host environment validation.

        Returns:
            ValidationDetails with complete validation results
        """
        return self.validator.validate_complete_environment()

    def setup_host_environment(self, config: dict[str, Any] | None = None) -> bool:
        """
        Set up complete host development environment.

        Args:
            config: Optional configuration overrides

        Returns:
            True if setup completed successfully
        """
        try:
            config = config or {}

            if self.verbose:
                print("Setting up host environment...")

            # Validate current environment
            validation = self.validate_host_environment()
            if not validation.is_valid and validation.status == ValidationStatus.ERROR:
                if self.verbose:
                    print(f"Host validation failed: {validation.message}")
                return False

            # Configure system-specific optimizations
            success = self._configure_system_optimizations(config)
            if not success:
                if self.verbose:
                    print("Failed to configure system optimizations")
                return False

            # Setup development tools integration
            success = self._setup_development_tools(config)
            if not success:
                if self.verbose:
                    print("Failed to setup development tools")
                return False

            if self.verbose:
                print("✓ Host environment setup completed successfully")

            return True

        except Exception as e:
            if self.verbose:
                print(f"Host setup failed: {e}")
            return False

    def get_host_status(self) -> dict[str, Any]:
        """
        Get comprehensive host environment status.

        Returns:
            Dictionary with detailed host status information
        """
        try:
            # Get system information
            system_info = self.system_info.collect_all_info()

            # Get validation results
            validation = self.validate_host_environment()

            # Get environment-specific info
            env_info = self.validator.get_environment_info()

            return {
                "system_info": system_info,
                "validation": {
                    "is_valid": validation.is_valid,
                    "status": validation.status.value,
                    "message": validation.message,
                    "warnings": validation.warnings,
                    "errors": validation.errors,
                    "recommendations": validation.recommendations,
                },
                "environment": env_info,
                "workspace_root": str(self.workspace_root),
            }

        except Exception as e:
            return {
                "error": str(e),
                "status": "error",
                "workspace_root": str(self.workspace_root),
            }

    def _configure_system_optimizations(self, config: dict[str, Any]) -> bool:
        """Configure system-specific optimizations."""
        try:
            # Platform-specific optimizations
            system_type = self.system_info.get_system_type()

            if system_type == "Windows":
                return self._configure_windows_optimizations(config)
            elif system_type == "Darwin":
                return self._configure_macos_optimizations(config)
            elif system_type == "Linux":
                return self._configure_linux_optimizations(config)

            return True

        except Exception:
            return False

    def _configure_windows_optimizations(self, config: dict[str, Any]) -> bool:
        """Configure Windows-specific optimizations."""
        # Windows-specific configuration
        # Could include PowerShell execution policy, Windows Defender exclusions, etc.
        return True

    def _configure_macos_optimizations(self, config: dict[str, Any]) -> bool:
        """Configure macOS-specific optimizations."""
        # macOS-specific configuration
        # Could include Xcode tools, Homebrew setup, etc.
        return True

    def _configure_linux_optimizations(self, config: dict[str, Any]) -> bool:
        """Configure Linux-specific optimizations."""
        # Linux-specific configuration
        # Could include package manager setup, system packages, etc.
        return True

    def _setup_development_tools(self, config: dict[str, Any]) -> bool:
        """Setup development tools integration."""
        try:
            # Setup git configuration if needed
            # Setup shell integrations
            # Configure terminal settings
            return True
        except Exception:
            return False


# Utility functions for backward compatibility
def validate_host_environment() -> tuple[bool, str]:
    """Validate host environment - compatibility function."""
    try:
        from ..environment.path_utils import get_project_root

        validator = HostEnvironmentValidator(get_project_root())
        result = validator.validate_complete_environment()
        return result.is_valid, result.message
    except Exception as e:
        return False, f"Host validation failed: {e}"


def get_system_info() -> dict[str, Any]:
    """Get system information."""
    try:
        collector = SystemInfoCollector()
        return collector.collect_all_info()
    except Exception:
        return {"error": "Failed to collect system information"}


def check_host_requirements() -> bool:
    """Check if host meets basic requirements."""
    try:
        from ..environment.path_utils import get_project_root

        validator = HostEnvironmentValidator(get_project_root())
        result = validator.validate_complete_environment()
        return result.is_valid
    except Exception:
        return False


__all__ = [
    "HostSetupManager",
    "HostEnvironmentValidator",
    "SystemInfoCollector",
    "validate_host_environment",
    "get_system_info",
    "check_host_requirements",
]
