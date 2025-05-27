"""
Data classes for VS Code and Docker configuration.

This module contains data classes for managing VS Code workspace configuration
and Docker environment setup.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, TypedDict

__all__ = [
    "VSCodeExtension",
    "VSCodeConfig",
    "DockerInfo",
    "DockerConfig",
]


class VSCodeExtension(TypedDict):
    """VS Code extension information with complete metadata."""

    id: str
    publisher: str
    name: str
    description: str
    version: str | None
    enabled: bool


@dataclass(slots=True)
class VSCodeConfig:
    """
    VS Code configuration settings with comprehensive workspace support.

    Manages all aspects of VS Code workspace configuration including
    settings, extensions, launch configurations, and tasks.
    """

    settings: dict[str, Any] = field(default_factory=dict)
    extensions: list[str] = field(default_factory=list)
    recommended_extensions: list[VSCodeExtension] = field(default_factory=list)
    launch_config: dict[str, Any] = field(default_factory=dict)
    tasks_config: dict[str, Any] = field(default_factory=dict)
    workspace_config: dict[str, Any] = field(default_factory=dict)

    # Additional VS Code configuration
    snippets: dict[str, dict[str, Any]] = field(default_factory=dict)
    keybindings: list[dict[str, str]] = field(default_factory=list)
    workspace_path: Path | None = None

    def __post_init__(self) -> None:
        """Initialize default configurations if not provided."""
        if not self.settings:
            self.settings = self._get_default_settings()
        if not self.launch_config:
            self.launch_config = self._get_default_launch_config()
        if not self.tasks_config:
            self.tasks_config = self._get_default_tasks_config()

    def _get_default_settings(self) -> dict[str, Any]:
        """Get default VS Code settings."""
        return {
            "python.defaultInterpreterPath": "./venv/bin/python",
            "python.formatting.provider": "black",
            "python.linting.enabled": True,
            "python.linting.pylintEnabled": False,
            "python.linting.ruffEnabled": True,
            "editor.formatOnSave": True,
            "editor.codeActionsOnSave": {"source.organizeImports": True},
        }

    def _get_default_launch_config(self) -> dict[str, Any]:
        """Get default launch configuration."""
        return {"version": "0.2.0", "configurations": []}

    def _get_default_tasks_config(self) -> dict[str, Any]:
        """Get default tasks configuration."""
        return {"version": "2.0.0", "tasks": []}

    def add_extension(
        self, extension_id: str, publisher: str, name: str, description: str
    ) -> None:
        """Add an extension to the configuration."""
        if extension_id not in self.extensions:
            self.extensions.append(extension_id)

        extension_info: VSCodeExtension = {
            "id": extension_id,
            "publisher": publisher,
            "name": name,
            "description": description,
            "version": None,
            "enabled": True,
        }
        self.recommended_extensions.append(extension_info)

    def get_workspace_settings_path(self) -> Path | None:
        """Get path to workspace settings file."""
        if self.workspace_path:
            return self.workspace_path / ".vscode" / "settings.json"
        return None

    def export_configuration(self) -> dict[str, dict[str, Any]]:
        """Export complete configuration for persistence."""
        return {
            "settings": self.settings,
            "extensions": {"recommendations": self.extensions},
            "launch": self.launch_config,
            "tasks": self.tasks_config,
            "workspace": self.workspace_config,
        }


@dataclass(slots=True)
class DockerInfo:
    """
    Docker environment information with comprehensive container management.

    Tracks Docker availability, version information, and running containers
    for development environment setup.
    """

    docker_available: bool
    docker_version: tuple[int, int, int] | None = None
    compose_available: bool = False
    compose_version: str | None = None
    images_available: list[str] = field(default_factory=list)
    containers_running: list[str] = field(default_factory=list)

    # Additional Docker information
    buildkit_available: bool = False
    swarm_mode: bool = False
    registry_auth: dict[str, str] = field(default_factory=dict)
    storage_driver: str = ""

    @property
    def is_ready(self) -> bool:
        """Check if Docker environment is ready for use."""
        return self.docker_available and self.docker_version is not None

    @property
    def version_string(self) -> str:
        """Get Docker version as string."""
        if self.docker_version:
            return f"{self.docker_version[0]}.{self.docker_version[1]}.{self.docker_version[2]}"
        return "unknown"


@dataclass(slots=True)
class DockerConfig:
    """
    Docker configuration for development environment setup.

    Manages Docker container configuration, image settings, and
    development environment specifications.
    """

    base_image: str = "python:3.11-slim"
    work_dir: str = "/app"
    expose_ports: list[int] = field(default_factory=lambda: [8000])
    volumes: dict[str, str] = field(default_factory=dict)
    environment_vars: dict[str, str] = field(default_factory=dict)

    # Resource limits
    memory_limit: str = "1g"
    cpu_limit: str = "1.0"

    # Health check configuration
    health_check_cmd: str = ""
    health_check_interval: int = 30
    health_check_timeout: int = 10
    health_check_retries: int = 3

    def __post_init__(self) -> None:
        """Initialize default configurations."""
        if not self.volumes:
            self.volumes = {".": "/app", "~/.cache": "/root/.cache"}

        if not self.environment_vars:
            self.environment_vars = {
                "PYTHONPATH": "/app",
                "PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONUNBUFFERED": "1",
            }

    @property
    def container_name(self) -> str:
        """Generate container name from configuration."""
        return f"mcp-dev-{self.base_image.replace(':', '-').replace('/', '-')}"

    def get_dockerfile_content(self) -> str:
        """Generate Dockerfile content from configuration."""
        lines = [
            f"FROM {self.base_image}",
            f"WORKDIR {self.work_dir}",
            "",
            "# Install system dependencies",
            "RUN apt-get update && apt-get install -y \\",
            "    git \\",
            "    curl \\",
            "    build-essential \\",
            "    && rm -rf /var/lib/apt/lists/*",
            "",
            "# Copy requirements and install Python dependencies",
            "COPY requirements.txt .",
            "RUN pip install --no-cache-dir -r requirements.txt",
            "",
            "# Copy source code",
            "COPY . .",
            "",
            "# Set environment variables",
        ]

        for key, value in self.environment_vars.items():
            lines.append(f"ENV {key}={value}")

        if self.health_check_cmd:
            lines.extend(
                [
                    "",
                    f"HEALTHCHECK --interval={self.health_check_interval}s \\",
                    f"  --timeout={self.health_check_timeout}s \\",
                    f"  --retries={self.health_check_retries} \\",
                    f"  CMD {self.health_check_cmd}",
                ]
            )

        lines.extend(["", 'CMD ["bash"]'])
        return "\n".join(lines)

    def get_docker_compose_service(self) -> dict[str, Any]:
        """Get Docker Compose service configuration."""
        config = {
            "build": ".",
            "working_dir": self.work_dir,
            "volumes": [
                f"{host}:{container}" for host, container in self.volumes.items()
            ],
            "environment": self.environment_vars,
            "deploy": {
                "resources": {
                    "limits": {"memory": self.memory_limit, "cpus": self.cpu_limit}
                }
            },
        }

        if self.expose_ports:
            config["ports"] = [f"{port}:{port}" for port in self.expose_ports]

        if self.health_check_cmd:
            config["healthcheck"] = {
                "test": self.health_check_cmd,
                "interval": f"{self.health_check_interval}s",
                "timeout": f"{self.health_check_timeout}s",
                "retries": self.health_check_retries,
            }

        return config
