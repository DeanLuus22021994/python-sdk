"""
Docker Configuration Package
Provides Docker environment validation and configuration for MCP Python SDK
"""

from setup.docker.container_config import configure_containers, get_container_config
from setup.docker.docker_validator import (
    check_docker_compose,
    check_docker_daemon,
    check_docker_version,
    validate_docker_environment,
)
from setup.docker.image_manager import (
    build_development_image,
    check_required_images,
    pull_required_images,
)
from setup.docker.volume_config import configure_volumes, get_volume_config

__version__ = "1.0.0"
__all__ = [
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
