"""
Docker Setup Manager
Comprehensive Docker environment setup and management for the MCP Python SDK.
Modern implementation using the validation framework.
"""

import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any

from ..typings import ValidationDetails, ValidationStatus
from ..validation.base import BaseValidator, ValidationContext, ValidationResult
from ..validation.registry import get_global_registry
from .container_config import DockerContainerManager
from .docker_validator import validate_docker_environment
from .image_manager import DockerImageManager
from .volume_config import DockerVolumeManager


class DockerSetupManager:
    """
    Comprehensive Docker setup and management for the MCP Python SDK.

    Coordinates Docker container, volume, and image management for both
    development and production environments following SOLID principles.
    """

    def __init__(self, workspace_root: Path, verbose: bool = False) -> None:
        """
        Initialize Docker setup manager.

        Args:
            workspace_root: Root directory of the workspace
            verbose: Enable verbose logging
        """
        self.workspace_root = Path(workspace_root).resolve()
        self.verbose = verbose
        self.registry = get_global_registry()

        # Initialize component managers
        self.container_manager = DockerContainerManager(self.workspace_root)
        self.volume_manager = DockerVolumeManager(self.workspace_root)
        self.image_manager = DockerImageManager()

    def setup_docker_environment(self, config: dict[str, Any] | None = None) -> bool:
        """
        Set up complete Docker development environment.

        Args:
            config: Optional configuration overrides

        Returns:
            True if setup completed successfully
        """
        try:
            success = True
            config = config or {}

            if self.verbose:
                print("🐳 Setting up Docker environment...")

            # Validate Docker installation
            docker_valid, docker_info = validate_docker_environment()
            if not docker_valid:
                if self.verbose:
                    print(f"✗ Docker validation failed: {docker_info}")
                return False

            # Configure volumes
            volumes_success = self.volume_manager.create_volume_directories()
            if not volumes_success:
                if self.verbose:
                    print("✗ Failed to configure Docker volumes")
                success = False

            # Pull required images
            images_success, _ = self.image_manager.pull_required_images()
            if not images_success:
                if self.verbose:
                    print("✗ Failed to pull required Docker images")
                success = False

            # Configure containers
            containers_success = self.container_manager.create_container_config()
            if not containers_success:
                if self.verbose:
                    print("✗ Failed to configure Docker containers")
                success = False

            return success

        except Exception as e:
            if self.verbose:
                print(f"✗ Docker setup failed: {e}")
            return False

    def validate_docker_environment(self) -> ValidationDetails:
        """
        Validate Docker environment using modern validation framework.

        Returns:
            ValidationDetails: Comprehensive validation results
        """
        context = ValidationContext(
            workspace_root=str(self.workspace_root),
            environment={},
            config={"component": "docker", "verbose": self.verbose},
        )

        # Create Docker validator if available
        try:
            validator = self.registry.create_validator("docker_environment", context)
            result = validator.validate()
              return ValidationDetails(
                is_valid=result.is_valid,
                status=ValidationStatus.VALID if result.is_valid else ValidationStatus.ERROR,
                message=result.message or "Docker validation completed",
                component_name="Docker",
                errors=result.data.get("errors", []) if result.data else [],
            )
        except Exception:
            # Fallback to legacy validation
            return self._legacy_docker_validation()

    def _legacy_docker_validation(self) -> ValidationDetails:
        """Legacy Docker validation for backward compatibility."""
        # Use existing docker validator
        docker_valid, docker_info = validate_docker_environment()

        # Extract message from docker info dict
        message = str(docker_info.get("message", "Docker validation completed"))
        errors = []
        if not docker_valid and "errors" in docker_info:
            errors = [str(docker_info["errors"])]

        return ValidationDetails(
            is_valid=docker_valid,
            status=ValidationStatus.VALID if docker_valid else ValidationStatus.ERROR,
            message=message,
            component_name="Docker",
            errors=errors,
        )

    def get_docker_status(self) -> dict[str, Any]:
        """
        Get comprehensive Docker environment status.

        Returns:
            Dictionary with detailed Docker status information
        """
        try:
            docker_valid, docker_info = validate_docker_environment()
            volume_status = self.volume_manager.get_volume_status()

            return {
                "docker_valid": docker_valid,
                "docker_info": docker_info,
                "volume_status": volume_status,
                "workspace_root": str(self.workspace_root),
            }

        except Exception as e:
            return {"error": str(e), "status": "error"}


# Utility functions for backward compatibility
def validate_docker_environment_compat() -> tuple[bool, str]:
    """Validate Docker environment - compatibility function."""
    valid, info = validate_docker_environment()
    if isinstance(info, dict):
        # Extract a meaningful message from the info dict
        if valid:
            return True, "Docker environment is properly configured"
        else:
            # Try to get specific error messages
            daemon_msg = str(info.get("daemon_message", "Docker daemon issue"))
            version_msg = str(info.get("version_message", "Docker version issue"))
            compose_msg = str(info.get("compose_message", "Docker Compose issue"))

            if not info.get("daemon_running", False):
                return False, daemon_msg
            elif not info.get("version_valid", False):
                return False, version_msg
            elif not info.get("compose_available", False):
                return False, compose_msg
            else:
                return False, "Docker environment validation failed"
    return valid, str(info)


def configure_volumes() -> bool:
    """Configure Docker volumes."""
    try:
        from ..environment.path_utils import get_project_root

        project_root = get_project_root()
        volume_manager = DockerVolumeManager(project_root)
        return volume_manager.create_volume_directories()
    except Exception:
        return False


def configure_containers() -> bool:
    """Configure Docker containers."""
    try:
        from ..environment.path_utils import get_project_root

        project_root = get_project_root()
        container_manager = DockerContainerManager(project_root)
        return container_manager.create_container_config()
    except Exception:
        return False


def check_required_images() -> bool:
    """Check if required Docker images are available."""
    try:
        from .image_manager import check_required_images as _check_images

        images_status = _check_images()
        return all(images_status.values())
    except Exception:
        return False


def pull_required_images() -> bool:
    """Pull required Docker images."""
    try:
        from .image_manager import pull_required_images as _pull_images

        success, _ = _pull_images()
        return success
    except Exception:
        return False


__all__ = [
    "DockerSetupManager",
    "validate_docker_environment",
    "configure_volumes",
    "configure_containers",
    "check_required_images",
    "pull_required_images",
]
