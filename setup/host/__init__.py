"""
Host Environment Setup Module
Manages host-based setup and validation for the MCP Python SDK.
"""

from __future__ import annotations

import os
import platform
import sys
from pathlib import Path
from typing import Any

from ..typings import EnvironmentInfo, PythonVersion, ValidationStatus
from ..typings.environment import ValidationDetails
from ..validation.base import BaseValidator, ValidationContext, ValidationResult
from ..validation.registry import get_global_registry, register_validator


@register_validator("host_environment")
class HostEnvironmentValidator(BaseValidator[dict[str, Any]]):
    """
    Validates host environment for direct installation.

    Follows SRP by focusing on host-specific validation requirements.
    """

    def get_validator_name(self) -> str:
        """Get validator name."""
        return "Host Environment"

    def _perform_validation(self) -> ValidationResult[dict[str, Any]]:
        """Validate host environment."""
        errors: list[str] = []
        warnings: list[str] = []
        recommendations: list[str] = []
        metadata: dict[str, Any] = {}

        # Get environment info
        env_info = self._get_environment_info()
        metadata.update(
            {
                "python_version": str(env_info.python_version),
                "platform": env_info.platform_system,
                "architecture": env_info.architecture,
                "virtual_env_active": env_info.virtual_env_active,
            }
        )

        # Check Python version
        if env_info.python_version < PythonVersion(3, 10, 0):
            errors.append(
                f"Python {env_info.python_version} is not supported. Minimum version is 3.10"
            )
        elif env_info.python_version < PythonVersion(3, 11, 0):
            warnings.append(
                f"Python {env_info.python_version} works but 3.11+ is recommended"
            )

        # Check virtual environment
        if not env_info.virtual_env_active:
            warnings.append("Not running in a virtual environment")
            recommendations.append(
                "Consider using a virtual environment for dependency isolation"
            )

        # Platform-specific checks
        if env_info.platform_system == "Windows":
            self._check_windows_environment(metadata, warnings, recommendations)
        elif env_info.platform_system == "Linux":
            self._check_linux_environment(metadata, warnings, recommendations)
        elif env_info.platform_system == "Darwin":
            self._check_macos_environment(metadata, warnings, recommendations)

        # Determine status
        if errors:
            status = ValidationStatus.ERROR
            is_valid = False
            message = f"Host environment validation failed: {len(errors)} error(s)"
        elif warnings:
            status = ValidationStatus.WARNING
            is_valid = True
            message = f"Host environment has {len(warnings)} warning(s)"
        else:
            status = ValidationStatus.VALID
            is_valid = True
            message = "Host environment is ready"

        return self._create_result(
            is_valid=is_valid,
            status=status,
            message=message,
            data=metadata,
            errors=errors,
            warnings=warnings,
            recommendations=recommendations,
        )

    def _get_environment_info(self) -> EnvironmentInfo:
        """Get comprehensive environment information."""
        version_info = sys.version_info
        python_version = PythonVersion(
            version_info.major, version_info.minor, version_info.micro
        )

        # Check virtual environment
        in_venv = hasattr(sys, "real_prefix") or (
            hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
        )

        return EnvironmentInfo(
            python_version=python_version,
            python_executable=sys.executable,
            virtual_env_active=in_venv,
            virtual_env_type="venv" if in_venv else None,
            virtual_env_path=sys.prefix if in_venv else None,
            platform_system=platform.system(),
            platform_release=platform.release(),
            architecture=platform.machine(),
        )

    def _check_windows_environment(
        self, metadata: dict[str, Any], warnings: list[str], recommendations: list[str]
    ) -> None:
        """Windows-specific environment checks."""
        # Check for Windows-specific tools
        try:
            import subprocess

            result = subprocess.run(["where", "git"], capture_output=True, text=True)
            metadata["git_available"] = result.returncode == 0
            if result.returncode != 0:
                warnings.append("Git not found in PATH")
                recommendations.append("Install Git for Windows")
        except Exception:
            warnings.append("Could not check Git availability")

    def _check_linux_environment(
        self, metadata: dict[str, Any], warnings: list[str], recommendations: list[str]
    ) -> None:
        """Linux-specific environment checks."""
        # Check for build tools
        try:
            import subprocess

            result = subprocess.run(["which", "gcc"], capture_output=True, text=True)
            metadata["gcc_available"] = result.returncode == 0
            if result.returncode != 0:
                warnings.append("GCC compiler not found")
                recommendations.append("Install build-essential or equivalent package")
        except Exception:
            warnings.append("Could not check build tools")

    def _check_macos_environment(
        self, metadata: dict[str, Any], warnings: list[str], recommendations: list[str]
    ) -> None:
        """macOS-specific environment checks."""
        # Check for Xcode command line tools
        try:
            import subprocess

            result = subprocess.run(
                ["xcode-select", "-p"], capture_output=True, text=True
            )
            metadata["xcode_tools_available"] = result.returncode == 0
            if result.returncode != 0:
                warnings.append("Xcode command line tools not installed")
                recommendations.append(
                    "Install Xcode command line tools: xcode-select --install"
                )
        except Exception:
            warnings.append("Could not check Xcode tools")


class HostSetupManager:
    """Manages host environment setup and validation."""

    def __init__(self, workspace_root: Path | str) -> None:
        """Initialize host setup manager."""
        self.workspace_root = (
            Path(workspace_root) if isinstance(workspace_root, str) else workspace_root
        )

        self.context = ValidationContext(
            workspace_root=str(self.workspace_root),
            environment=dict(os.environ),
            config={"component": "host"},
        )

    def validate_host_environment(self) -> ValidationDetails:
        """Validate host environment."""
        registry = get_global_registry()

        try:
            validator = registry.create_validator("host_environment", self.context)
            result = validator.validate()

            return ValidationDetails(
                is_valid=result.is_valid,
                status=result.status,
                message=result.message,
                warnings=list(result.warnings),
                errors=list(result.errors),
                recommendations=list(result.recommendations),
                metadata=result.metadata,
                component_name="Host Environment",
            )

        except ValueError:
            # Fallback validation
            return ValidationDetails(
                is_valid=True,
                status=ValidationStatus.WARNING,
                message="Host validator not available",
                warnings=["Host validator not registered"],
                errors=[],
                recommendations=["Ensure host validator is properly registered"],
                metadata={"workspace_root": str(self.workspace_root)},
                component_name="Host Environment",
            )


def validate_host_environment(
    workspace_root: Path | str | None = None,
) -> ValidationDetails:
    """Validate the host environment."""
    root = Path(workspace_root) if workspace_root else Path.cwd()
    manager = HostSetupManager(root)
    return manager.validate_host_environment()


__all__ = [
    "HostEnvironmentValidator",
    "HostSetupManager",
    "validate_host_environment",
]
