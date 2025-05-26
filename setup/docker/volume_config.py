# filepath: c:\Projects\python-sdk\setup\docker\volume_config.py
"""
Docker Volume Configuration Manager
Handles Docker volume setup and management for the MCP Python SDK.
"""

import json
from pathlib import Path
from typing import Any, Dict, List
from functools import cached_property


class DockerVolumeManager:
    """
    Manages Docker volume configuration for the MCP Python SDK.

    Provides functionality to create, configure, and manage Docker volumes
    for development and production environments.
    """

    def __init__(self, project_root: Path) -> None:
        """
        Initialize Docker volume manager.

        Args:
            project_root: Root directory of the project
        """
        self.project_root = Path(project_root).resolve()

    @cached_property
    def get_project_root(self) -> Path:
        """Get the project root directory."""
        return self.project_root

    def create_volume_config(self) -> Dict[str, Any]:
        """
        Create comprehensive Docker volume configuration.

        Returns:
            Dictionary containing volume configuration
        """
        return {
            "version": "3.8",
            "volumes": {
                "mcp_data": {
                    "driver": "local",
                    "driver_opts": {
                        "type": "none",
                        "o": "bind",
                        "device": str(self.project_root / "data"),
                    },
                },
                "mcp_cache": {
                    "driver": "local",
                    "driver_opts": {
                        "type": "tmpfs",
                        "o": "size=1g,uid=1000,gid=1000",
                    },
                },
                "postgres_data": {
                    "driver": "local",
                },
                "redis_data": {
                    "driver": "local",
                },
            },
            "networks": {
                "mcp_network": {
                    "driver": "bridge",
                    "ipam": {
                        "config": [
                            {
                                "subnet": "172.20.0.0/16",
                                "ip_range": "172.20.240.0/20",
                            }
                        ]
                    },
                }
            },
        }

    def validate_volume_config(self) -> bool:
        """
        Validate Docker volume configuration.

        Returns:
            True if configuration is valid
        """
        try:
            config = self.create_volume_config()

            # Basic validation checks
            required_keys = ["version", "volumes", "networks"]
            if not all(key in config for key in required_keys):
                return False

            # Validate volumes structure
            volumes = config.get("volumes", {})
            if not isinstance(volumes, dict):
                return False

            # Validate each volume
            for volume_name, volume_config in volumes.items():
                if not isinstance(volume_config, dict):
                    return False
                if "driver" not in volume_config:
                    return False

            return True

        except Exception:
            return False

    def get_volume_status(self) -> Dict[str, Any]:
        """
        Get current volume configuration status.

        Returns:
            Dictionary with volume status information
        """
        try:
            config = self.create_volume_config()
            is_valid = self.validate_volume_config()

            return {
                "project_root": str(self.project_root),
                "configuration_valid": is_valid,
                "volumes_defined": len(config.get("volumes", {})),
                "networks_defined": len(config.get("networks", {})),
                "config": config,
            }

        except Exception as e:
            return {
                "error": str(e),
                "status": "error"
            }

    def write_volume_config(self, output_path: Path | None = None) -> bool:
        """
        Write Docker volume configuration to file.

        Args:
            output_path: Path to write configuration file

        Returns:
            True if file was written successfully
        """
        try:
            if output_path is None:
                output_path = self.project_root / "docker-volumes.yml"

            config = self.create_volume_config()

            # Convert to YAML format for docker-compose
            import yaml

            with open(output_path, "w", encoding="utf-8") as f:
                yaml.dump(config, f, default_flow_style=False, indent=2)

            return True

        except Exception:
            return False

    def create_volume_directories(self) -> bool:
        """
        Create necessary directories for volume mounts.

        Returns:
            True if directories were created successfully
        """
        try:
            directories = [
                self.project_root / "data",
                self.project_root / "data" / "postgres",
                self.project_root / "data" / "redis",
                self.project_root / "logs",
                self.project_root / "cache",
            ]

            for directory in directories:
                directory.mkdir(parents=True, exist_ok=True)

            return True

        except Exception:
            return False


def configure_volumes() -> bool:
    """
    Configure Docker volumes for the MCP Python SDK.

    Returns:
        True if volumes were configured successfully
    """
    try:
        from ..environment.path_utils import get_project_root

        project_root = get_project_root()
        volume_manager = DockerVolumeManager(project_root)

        # Create necessary directories
        dirs_created = volume_manager.create_volume_directories()
        if not dirs_created:
            return False

        # Write volume configuration
        config_written = volume_manager.write_volume_config()
        return config_written

    except Exception:
        return False


def validate_volume_setup() -> bool:
    """
    Validate Docker volume setup.

    Returns:
        True if volume setup is valid
    """
    try:
        from ..environment.path_utils import get_project_root

        project_root = get_project_root()
        volume_manager = DockerVolumeManager(project_root)

        return volume_manager.validate_volume_config()

    except Exception:
        return False


__all__ = [
    "DockerVolumeManager",
    "configure_volumes",
    "validate_volume_setup",
]
