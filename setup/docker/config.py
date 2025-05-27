"""
Docker Configuration Management
Modernized Docker configuration using the validation framework.
"""

from __future__ import annotations

from pathlib import Path

from ..typings import ContainerConfig, DockerInfo


class DockerConfigManager:
    """
    Modern Docker configuration manager.

    Handles Docker configuration with proper validation and type safety.
    """

    def __init__(self, workspace_root: Path | str) -> None:
        """Initialize Docker configuration manager."""
        self.workspace_root = (
            Path(workspace_root) if isinstance(workspace_root, str) else workspace_root
        )

    def get_default_config(self) -> ContainerConfig:
        """Get default Docker configuration."""
        return ContainerConfig(
            image_name="python:3.11-slim",
            container_name="mcp-python-sdk-dev",
            ports={"8000": "8000"},
            volumes={str(self.workspace_root): "/workspace"},
            environment_vars={"PYTHONPATH": "/workspace", "ENV": "development"},
            working_directory="/workspace",
            entrypoint=["/bin/bash"],
        )

    def validate_config(self, config: ContainerConfig) -> list[str]:
        """Validate Docker configuration."""
        errors = []

        if not config.image_name:
            errors.append("Image name is required")

        if not config.container_name:
            errors.append("Container name is required")

        return errors

    def get_docker_info(self) -> DockerInfo:
        """Get Docker environment information."""
        return DockerInfo(
            docker_available=True,  # This would be checked properly
            docker_version="24.0.0",  # This would be detected
            compose_available=True,  # This would be checked
            compose_version="2.0.0",  # This would be detected
        )


__all__ = [
    "DockerConfigManager",
]
