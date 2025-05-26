"""
Docker Configuration Package
Provides Docker environment validation and configuration for MCP Python SDK
"""

from .container_config import configure_containers, get_container_config
from .docker_validator import (
    check_docker_compose,
    check_docker_daemon,
    check_docker_version,
    validate_docker_environment,
)
from .image_manager import (
    build_development_image,
    check_required_images,
    pull_required_images,
)
from .volume_config import configure_volumes, get_volume_config


class DockerSetupManager:
    """
    Docker-based setup manager following Single Responsibility Principle.

    Coordinates Docker environment setup and containerization.
    """

    def __init__(self, verbose: bool = False) -> None:
        self.verbose = verbose
        self._setup_results: dict[str, bool] = {}

    def setup(self) -> tuple[bool, dict[str, bool]]:
        """
        Perform complete Docker-based setup.

        Returns:
            Tuple of (success, setup_results)
        """
        print("🐳 Starting Docker-based setup...")

        # Docker environment validation
        docker_valid, docker_info = validate_docker_environment()
        self._setup_results["docker_environment"] = docker_valid
        if self.verbose:
            print(f"Docker environment: {'✓' if docker_valid else '✗'}")

        if not docker_valid:
            print("❌ Docker environment not available. Skipping Docker setup.")
            return False, self._setup_results

        # Image management
        images_success, _ = pull_required_images()
        self._setup_results["images"] = images_success
        if self.verbose:
            print(f"Docker images: {'✓' if images_success else '✗'}")

        # Volume configuration
        volumes_success, _ = configure_volumes()
        self._setup_results["volumes"] = volumes_success
        if self.verbose:
            print(f"Docker volumes: {'✓' if volumes_success else '✗'}")

        # Container configuration
        containers_success = configure_containers()
        self._setup_results["containers"] = containers_success
        if self.verbose:
            print(f"Docker containers: {'✓' if containers_success else '✗'}")

        overall_success = all(self._setup_results.values())

        if overall_success:
            print("✅ Docker setup completed successfully!")
        else:
            print("❌ Docker setup completed with some issues.")

        return overall_success, self._setup_results

    def validate(self) -> bool:
        """
        Validate current Docker environment.

        Returns:
            True if Docker environment is valid for development
        """
        docker_valid, _ = validate_docker_environment()
        if not docker_valid:
            return False

        image_status = check_required_images()
        return all(image_status.values())

    def get_status(self) -> dict[str, bool | dict[str, bool]]:
        """
        Get current Docker environment status.

        Returns:
            Dictionary with Docker status information
        """
        docker_valid, docker_info = validate_docker_environment()
        image_status = check_required_images()

        return {
            "docker_valid": docker_valid,
            "docker_details": docker_info,
            "image_status": image_status,
            "setup_results": self._setup_results,
        }


__version__ = "1.0.0"
__all__ = [
    # Main manager
    "DockerSetupManager",
    # Docker environment validation
    "validate_docker_environment",
    "check_docker_daemon",
    "check_docker_version",
    "check_docker_compose",
    # Container configuration
    "configure_containers",
    "get_container_config",
    # Volume configuration
    "configure_volumes",
    "get_volume_config",
    # Image management
    "check_required_images",
    "pull_required_images",
    "build_development_image",
]
