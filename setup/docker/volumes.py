"""
Docker Volume Configuration
Manages Docker volume configuration and validation.
"""

from pathlib import Path
from typing import Any

from ..environment.utils import get_project_root


class DockerVolumeManager:
    """Manages Docker volume configuration."""

    def __init__(self, workspace_root: Path | None = None) -> None:
        """Initialize volume manager."""
        self.workspace_root = (
            Path(workspace_root) if workspace_root else get_project_root()
        )

    def get_volume_configuration(self) -> dict[str, Any]:
        """Get Docker volume configuration."""
        return {
            "volumes": {
                "mcp_venv": {"driver": "local"},
                "mcp_cache": {"driver": "local"},
            },
            "volume_mounts": [
                {
                    "source": str(self.workspace_root),
                    "target": "/app",
                    "type": "bind",
                },
                {
                    "source": "mcp_venv",
                    "target": "/app/.venv",
                    "type": "volume",
                },
                {
                    "source": "mcp_cache",
                    "target": "/root/.cache",
                    "type": "volume",
                },
            ],
        }

    def create_volumes(self) -> bool:
        """Create required Docker volumes."""
        import subprocess

        volumes = ["mcp_venv", "mcp_cache"]

        for volume in volumes:
            try:
                subprocess.run(
                    ["docker", "volume", "create", volume],
                    capture_output=True,
                    text=True,
                    check=True,
                )
            except (subprocess.CalledProcessError, FileNotFoundError):
                return False

        return True

    def cleanup_volumes(self) -> bool:
        """Clean up Docker volumes."""
        import subprocess

        volumes = ["mcp_venv", "mcp_cache"]

        for volume in volumes:
            try:
                subprocess.run(
                    ["docker", "volume", "rm", "-f", volume],
                    capture_output=True,
                    text=True,
                )
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue

        return True
