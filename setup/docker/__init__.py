"""
Docker Setup Module
Modern Docker configuration and management for the MCP Python SDK setup.
"""

from pathlib import Path
from typing import Any

from ..typings import ContainerConfig, ValidationStatus
from ..typings.environment import ValidationDetails
from .config import DockerConfigManager, validate_docker_environment
from .images import DockerImageManager
from .volumes import DockerVolumeManager


class DockerSetupManager:
    """
    Modern Docker setup manager using the validation framework.

    Coordinates Docker environment setup, validation, and configuration
    following SOLID principles and modern Python patterns.
    """

    def __init__(self, workspace_root: Path | None = None) -> None:
        """Initialize Docker setup manager."""
        self.workspace_root = Path(workspace_root) if workspace_root else Path.cwd()
        self.config_manager = DockerConfigManager(self.workspace_root)
        self.image_manager = DockerImageManager(self.workspace_root)
        self.volume_manager = DockerVolumeManager(self.workspace_root)

    def validate_complete_setup(self) -> ValidationDetails:
        """Validate complete Docker setup."""
        # Use the modern validation framework
        return validate_docker_environment()

    def setup_environment(self) -> bool:
        """Set up complete Docker environment."""
        try:
            # Validate first
            validation = self.validate_complete_setup()
            if not validation.is_valid:
                return False

            # Create volumes
            if not self.volume_manager.create_volumes():
                return False

            # Generate configuration files
            self.config_manager.save_dockerfile()
            self.config_manager.save_compose_file()

            return True
        except Exception:
            return False

    def cleanup_environment(self) -> bool:
        """Clean up Docker environment."""
        try:
            return self.volume_manager.cleanup_volumes()
        except Exception:
            return False

    def get_setup_status(self) -> dict[str, Any]:
        """Get current Docker setup status."""
        validation = self.validate_complete_setup()
        images_status = self.image_manager.check_required_images()

        return {
            "docker_available": validation.is_valid,
            "images_status": images_status,
            "volumes_configured": True,  # Assume configured if Docker is available
            "workspace_root": str(self.workspace_root),
        }


def configure_volumes() -> bool:
    """Configure Docker volumes for the project."""
    manager = DockerVolumeManager()
    return manager.create_volumes()


def configure_containers() -> bool:
    """Configure Docker containers for the project."""
    manager = DockerConfigManager()
    try:
        manager.save_dockerfile()
        manager.save_compose_file()
        return True
    except Exception:
        return False


def check_required_images() -> dict[str, bool]:
    """Check if required Docker images are available."""
    manager = DockerImageManager()
    return manager.check_required_images()


def pull_required_images() -> dict[str, bool]:
    """Pull required Docker images."""
    manager = DockerImageManager()
    return manager.pull_required_images()


__all__ = [
    "DockerSetupManager",
    "validate_docker_environment",
    "configure_volumes",
    "configure_containers",
    "check_required_images",
    "pull_required_images",
]
