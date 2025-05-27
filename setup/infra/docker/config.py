"""
Docker Configuration Management
Modernized Docker configuration using the validation framework.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from ...typings import ContainerConfig, DockerInfo


class DockerConfigManager:
    """
    Modern Docker configuration manager.

    Handles Docker configuration with proper validation and type safety.
    Follows SOLID principles with single responsibility for configuration.
    """

    def __init__(self, workspace_root: Path | str) -> None:
        """Initialize Docker configuration manager."""
        self.workspace_root = (
            Path(workspace_root) if isinstance(workspace_root, str) else workspace_root
        )

    def get_default_config(self) -> ContainerConfig:
        """Get default Docker configuration."""
        return ContainerConfig(
            base_image="python:3.11-slim",
            work_dir="/workspace",
            expose_port=8000,
            health_check_interval=30,
            memory_limit="512m",
            cpu_limit="0.5",
        )

    def validate_config(self, config: ContainerConfig) -> list[str]:
        """Validate Docker configuration."""
        errors = []

        if not config.base_image:
            errors.append("Base image is required")

        if config.base_image not in config.SUPPORTED_IMAGES:
            errors.append(f"Unsupported base image: {config.base_image}")

        return errors

    def get_docker_info(self) -> DockerInfo:
        """Get Docker environment information."""
        docker_available = self._check_docker_available()
        docker_version = self._get_docker_version() if docker_available else None
        compose_available = (
            self._check_compose_available() if docker_available else False
        )
        compose_version = self._get_compose_version() if compose_available else None

        return DockerInfo(
            docker_available=docker_available,
            docker_version=docker_version,
            compose_available=compose_available,
            compose_version=compose_version,
        )

    def _check_docker_available(self) -> bool:
        """Check if Docker is available."""
        try:
            result = subprocess.run(
                ["docker", "version"], capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except (
            subprocess.TimeoutExpired,
            FileNotFoundError,
            subprocess.SubprocessError,
        ):
            return False

    def _get_docker_version(self) -> tuple[int, int, int] | None:
        """Get Docker version as tuple."""
        try:
            result = subprocess.run(
                ["docker", "version", "--format", "{{.Server.Version}}"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                version_str = result.stdout.strip()
                # Parse version string like "24.0.6" into tuple
                parts = version_str.split(".")
                if len(parts) >= 2:
                    major = int(parts[0])
                    minor = int(parts[1])
                    patch = int(parts[2]) if len(parts) > 2 else 0
                    return (major, minor, patch)
        except (
            subprocess.TimeoutExpired,
            FileNotFoundError,
            subprocess.SubprocessError,
            ValueError,
        ):
            pass
        return None

    def _check_compose_available(self) -> bool:
        """Check if Docker Compose is available."""
        try:
            # Try docker compose (v2) first
            result = subprocess.run(
                ["docker", "compose", "version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return True

            # Fallback to docker-compose (v1)
            result = subprocess.run(
                ["docker-compose", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except (
            subprocess.TimeoutExpired,
            FileNotFoundError,
            subprocess.SubprocessError,
        ):
            return False

    def _get_compose_version(self) -> str | None:
        """Get Docker Compose version."""
        try:
            result = subprocess.run(
                ["docker", "compose", "version", "--short"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except (
            subprocess.TimeoutExpired,
            FileNotFoundError,
            subprocess.SubprocessError,
        ):
            pass
        return None


__all__ = [
    "DockerConfigManager",
]
