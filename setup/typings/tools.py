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


@dataclass
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
        """Initialize default VS Code configuration if empty."""
        if not self.settings:
            self.settings = self._get_default_settings()

        if not self.launch_config:
            self.launch_config = self._get_default_launch_config()

        if not self.tasks_config:
            self.tasks_config = self._get_default_tasks_config()

    def _get_default_settings(self) -> dict[str, Any]:
        """Get default VS Code settings for Python development."""
        return {
            "python.analysis.typeCheckingMode": "basic",
            "python.linting.enabled": True,
            "python.linting.pylintEnabled": False,
            "python.linting.flake8Enabled": True,
            "python.formatting.provider": "black",
            "python.testing.pytestEnabled": True,
            "python.testing.unittestEnabled": False,
            "files.exclude": {
                "**/__pycache__": True,
                "**/.pytest_cache": True,
                "**/.mypy_cache": True,
                "**/dist": True,
                "**/build": True,
            },
            "editor.formatOnSave": True,
            "editor.codeActionsOnSave": {"source.organizeImports": True},
        }

    def _get_default_launch_config(self) -> dict[str, Any]:
        """Get default launch configuration for debugging."""
        return {
            "version": "0.2.0",
            "configurations": [
                {
                    "name": "Python: Current File",
                    "type": "python",
                    "request": "launch",
                    "program": "${file}",
                    "console": "integratedTerminal",
                    "cwd": "${workspaceFolder}",
                },
                {
                    "name": "Python: MCP Server",
                    "type": "python",
                    "request": "launch",
                    "program": "${workspaceFolder}/src/mcp/server/__main__.py",
                    "console": "integratedTerminal",
                    "cwd": "${workspaceFolder}",
                    "env": {"PYTHONPATH": "${workspaceFolder}/src"},
                },
            ],
        }

    def _get_default_tasks_config(self) -> dict[str, Any]:
        """Get default tasks configuration."""
        return {
            "version": "2.0.0",
            "tasks": [
                {
                    "label": "Python: Run Tests",
                    "type": "shell",
                    "command": "python",
                    "args": ["-m", "pytest"],
                    "group": "test",
                    "presentation": {"echo": True, "reveal": "always"},
                }
            ],
        }

    def add_extension(
        self, extension_id: str, publisher: str, name: str, description: str
    ) -> None:
        """Add an extension to the configuration."""
        if extension_id not in self.extensions:
            self.extensions.append(extension_id)

        extension: VSCodeExtension = {
            "id": extension_id,
            "publisher": publisher,
            "name": name,
            "description": description,
            "version": None,
            "enabled": True,
        }

        # Update existing extension or add new one
        for i, ext in enumerate(self.recommended_extensions):
            if ext["id"] == extension_id:
                self.recommended_extensions[i] = extension
                return

        self.recommended_extensions.append(extension)

    def get_workspace_settings_path(self) -> Path | None:
        """Get path to workspace settings file."""
        if self.workspace_path:
            return self.workspace_path / ".vscode" / "settings.json"
        return None

    def export_configuration(self) -> dict[str, dict[str, Any]]:
        """Export complete configuration for serialization."""
        return {
            "settings": self.settings,
            "launch": self.launch_config,
            "tasks": self.tasks_config,
            "extensions": {
                "recommendations": self.extensions,
                "details": [dict(ext) for ext in self.recommended_extensions],
            },
            "workspace": self.workspace_config,
        }


@dataclass
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
    total_containers: int = 0
    total_images: int = 0

    def __post_init__(self) -> None:
        """Validate Docker information after initialization."""
        if self.docker_available and not self.docker_version:
            # Set a default version if Docker is available but version is unknown
            self.docker_version = (0, 0, 0)

    def version_string(self) -> str:
        """Get Docker version as a string."""
        if self.docker_version:
            return ".".join(map(str, self.docker_version))
        return "unknown"

    @property
    def is_compose_v2(self) -> bool:
        """Check if using Docker Compose V2."""
        return self.compose_available and (
            self.compose_version is None or "v2" in self.compose_version.lower()
        )

    @property
    def has_modern_features(self) -> bool:
        """Check if Docker has modern features (BuildKit, etc.)."""
        return (
            self.buildkit_available
            and self.docker_version is not None
            and self.docker_version >= (20, 10, 0)
        )

    def has_image(self, image_name: str) -> bool:
        """Check if a specific image is available."""
        return image_name in self.images_available

    def has_running_container(self, container_name: str) -> bool:
        """Check if a specific container is running."""
        return container_name in self.containers_running

    def get_environment_summary(self) -> str:
        """Get a summary of the Docker environment."""
        if not self.docker_available:
            return "Docker not available"

        summary = f"Docker {self.version_string}"
        if self.compose_available:
            summary += " with Compose"
        if self.buildkit_available:
            summary += " (BuildKit enabled)"

        return summary

    def get_status_dict(self) -> dict[str, Any]:
        """Get status as a dictionary for serialization."""
        return {
            "available": self.docker_available,
            "version": self.version_string,
            "compose": self.compose_available,
            "buildkit": self.buildkit_available,
            "containers": self.total_containers,
            "images": self.total_images,
            "storage_driver": self.storage_driver,
        }


@dataclass
class DockerConfig:
    """
    Docker configuration for development environment setup.

    Manages Docker and Docker Compose configuration settings for consistent
    development environment provisioning.
    """

    # Basic Docker configuration
    base_image: str = "python:3.11-slim"
    working_directory: str = "/app"
    exposed_ports: list[int] = field(default_factory=lambda: [8000])
    environment_variables: dict[str, str] = field(default_factory=dict)

    # Build configuration
    build_context: str = "."
    dockerfile_path: str = "Dockerfile"
    build_args: dict[str, str] = field(default_factory=dict)
    target_stage: str | None = None

    # Runtime configuration
    volumes: list[str] = field(default_factory=list)
    networks: list[str] = field(default_factory=list)
    depends_on: list[str] = field(default_factory=list)
    restart_policy: str = "unless-stopped"

    # Development specific
    development_overrides: dict[str, Any] = field(default_factory=dict)
    use_buildkit: bool = True
    enable_health_check: bool = True

    def __post_init__(self) -> None:
        """Initialize default configuration values."""
        if not self.environment_variables:
            self.environment_variables = {
                "PYTHONPATH": "/app",
                "PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONUNBUFFERED": "1",
            }

    def get_compose_config(self) -> dict[str, Any]:
        """Generate Docker Compose service configuration."""
        config: dict[str, Any] = {
            "build": {
                "context": self.build_context,
                "dockerfile": self.dockerfile_path,
            },
            "working_dir": self.working_directory,
            "environment": self.environment_variables,
            "restart": self.restart_policy,
        }

        if self.exposed_ports:
            config["ports"] = [f"{port}:{port}" for port in self.exposed_ports]

        if self.volumes:
            config["volumes"] = self.volumes

        if self.networks:
            config["networks"] = self.networks

        if self.depends_on:
            config["depends_on"] = self.depends_on

        if self.build_args:
            config["build"]["args"] = self.build_args

        if self.target_stage:
            config["build"]["target"] = self.target_stage

        if self.enable_health_check:
            config["healthcheck"] = {
                "test": [
                    "CMD",
                    "python",
                    "-c",
                    "import requests; requests.get('http://localhost:8000/health')",
                ],
                "interval": "30s",
                "timeout": "10s",
                "retries": 3,
            }

        return config

    def get_dockerfile_content(self) -> str:
        """Generate Dockerfile content based on configuration."""
        lines = [
            f"FROM {self.base_image}",
            f"WORKDIR {self.working_directory}",
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
            "COPY src/ /app/src/",
            "",
            "# Set environment variables",
        ]

        for key, value in self.environment_variables.items():
            lines.append(f"ENV {key}={value}")

        if self.exposed_ports:
            lines.append("")
            lines.extend([f"EXPOSE {port}" for port in self.exposed_ports])

        lines.extend(
            [
                "",
                'CMD ["python", "-m", "mcp.server"]',
            ]
        )

        return "\n".join(lines)

    def get_compose_override_for_development(self) -> dict[str, Any]:
        """Get development-specific Docker Compose overrides."""
        override = {
            "command": "sleep infinity",  # Keep container running for development
            "volumes": [
                "${PWD}:/app",  # Mount source code for live editing
                "python-cache:/root/.cache/pip",  # Cache pip packages
            ],
            "environment": {
                **self.environment_variables,
                "PYTHONDEBUG": "1",
                "DEVELOPMENT": "true",
            },
        }

        if self.development_overrides:
            override.update(self.development_overrides)

        return override
