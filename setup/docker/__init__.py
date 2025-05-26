"""
Docker Setup Manager
Comprehensive Docker environment setup and management for the MCP Python SDK.
"""

from pathlib import Path
from typing import Any

from ..types import ValidationDetails, ValidationStatus
from .container_config import DockerContainerManager
from .docker_validator import validate_docker_environment
from .image_manager import DockerImageManager
from .volume_config import DockerVolumeManager


class DockerSetupManager:
    """
    Comprehensive Docker setup and management for the MCP Python SDK.

    Coordinates Docker container, volume, and image management for both
    development and production environments.
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
                print("Setting up Docker environment...")

            # Validate Docker installation
            docker_valid, docker_info = validate_docker_environment()
            if not docker_valid:
                print(f"Docker validation failed: {docker_info}")
                return False

            # Configure volumes
            volumes_success = self.volume_manager.create_volume_directories()
            if not volumes_success:
                print("Failed to configure Docker volumes")
                success = False

            # Pull required images
            images_success, _ = self.image_manager.pull_required_images()
            if not images_success:
                print("Failed to pull required Docker images")
                success = False

            # Configure containers
            containers_success = self.container_manager.create_container_config()
            if not containers_success:
                print("Failed to configure Docker containers")
                success = False

            return success

        except Exception as e:
            if self.verbose:
                print(f"Docker setup failed: {e}")
            return False

    def validate_docker_setup(self) -> ValidationDetails:
        """
        Validate Docker environment setup.

        Returns:
            ValidationDetails with comprehensive validation results
        """
        try:
            warnings: list[str] = []
            errors: list[str] = []
            recommendations: list[str] = []

            # Validate Docker environment
            docker_valid, docker_info = validate_docker_environment()
            if not docker_valid:
                errors.append(f"Docker environment invalid: {docker_info}")

            # Validate volumes
            volumes_valid = self.volume_manager.validate_volume_config()
            if not volumes_valid:
                warnings.append("Docker volume configuration invalid")

            # Check required images
            images_available = self.image_manager.check_required_images()
            if not images_available:
                recommendations.append("Consider pulling required Docker images")

            # Determine overall status
            if errors:
                status = ValidationStatus.ERROR
                is_valid = False
                message = "Docker validation failed"
            elif warnings:
                status = ValidationStatus.WARNING
                is_valid = True
                message = "Docker validation passed with warnings"
            else:
                status = ValidationStatus.VALID
                is_valid = True
                message = "Docker environment is valid"

            return ValidationDetails(
                is_valid=is_valid,
                status=status,
                message=message,
                warnings=warnings,
                errors=errors,
                recommendations=recommendations,
                metadata={
                    "workspace_root": str(self.workspace_root),
                    "docker_info": docker_info,
                },
            )

        except Exception as e:
            return ValidationDetails(
                is_valid=False,
                status=ValidationStatus.ERROR,
                message=f"Docker validation failed: {e}",
                errors=[str(e)],
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
        return valid, str(info.get("daemon_message", "Docker check complete"))
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
