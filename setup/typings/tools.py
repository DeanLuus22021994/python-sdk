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
                    "label": "Install Dependencies",
                    "type": "shell",
                    "command": "uv sync",
                    "group": "build",
                    "presentation": {
                        "echo": True,
                        "reveal": "always",
                        "focus": False,
                        "panel": "shared",
                    },
                },
                {
                    "label": "Run Tests",
                    "type": "shell",
                    "command": "uv run pytest tests/ -v",
                    "group": {"kind": "test", "isDefault": True},
                    "presentation": {
                        "echo": True,
                        "reveal": "always",
                        "focus": False,
                        "panel": "shared",
                    },
                },
                {
                    "label": "Format Code",
                    "type": "shell",
                    "command": "uv run black src/ tests/ setup/",
                    "group": "build",
                },
                {
                    "label": "Type Check",
                    "type": "shell",
                    "command": "uv run mypy src/",
                    "group": "build",
                },
            ],
        }

    def add_extension(
        self, extension_id: str, publisher: str, name: str, description: str
    ) -> None:
        """Add an extension to the recommended list."""
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

        # Update existing or add new
        for i, ext in enumerate(self.recommended_extensions):
            if ext["id"] == extension_id:
                self.recommended_extensions[i] = extension_info
                return

        self.recommended_extensions.append(extension_info)

    def get_workspace_settings_path(self) -> Path | None:
        """Get path to workspace settings file."""
        if self.workspace_path:
            return self.workspace_path / ".vscode" / "settings.json"
        return None

    def export_configuration(self) -> dict[str, dict[str, Any]]:
        """Export complete VS Code configuration for serialization."""
        return {
            "settings": self.settings,
            "extensions": {
                "recommendations": [ext["id"] for ext in self.recommended_extensions]
            },
            "launch": self.launch_config,
            "tasks": self.tasks_config,
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
    total_containers: int = 0
    total_images: int = 0

    def __post_init__(self) -> None:
        """Validate Docker information after initialization."""
        if self.docker_available and not self.docker_version:
            raise ValueError("docker_version required when docker_available is True")

    @property
    def is_usable(self) -> bool:
        """Check if Docker is available and usable for development."""
        return self.docker_available and self.docker_version is not None

    @property
    def supports_modern_features(self) -> bool:
        """Check if Docker version supports modern features."""
        if not self.docker_version:
            return False

        # Docker 20.10+ supports modern features
        major, minor, _ = self.docker_version
        return (major, minor) >= (20, 10)

    @property
    def version_string(self) -> str:
        """Get Docker version as a string."""
        if self.docker_version:
            return f"{self.docker_version[0]}.{self.docker_version[1]}.{self.docker_version[2]}"
        return "unknown"

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

        compose_info = (
            f", Compose {self.compose_version}" if self.compose_available else ""
        )
        return (
            f"Docker {self.version_string}{compose_info} - "
            f"{len(self.images_available)} images, "
            f"{len(self.containers_running)} running containers"
        )

    def get_status_dict(self) -> dict[str, Any]:
        """Get Docker status as a dictionary."""
        return {
            "available": self.docker_available,
            "version": self.version_string,
            "compose_available": self.compose_available,
            "compose_version": self.compose_version,
            "images_count": len(self.images_available),
            "containers_running": len(self.containers_running),
            "buildkit_available": self.buildkit_available,
            "supports_modern_features": self.supports_modern_features,
        }
