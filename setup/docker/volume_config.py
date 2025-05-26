"""Docker volume configuration and management utilities."""

from functools import lru_cache
from pathlib import Path
from typing import Any

# Import with proper fallback handling
try:
    from setup.environment import get_project_root
except ImportError:
    # Fallback implementation with proper typing
    @lru_cache(maxsize=1)
    def get_project_root() -> Path:
        """Get the project root directory."""
        return Path(__file__).parent.parent.parent


class DockerVolumeManager:
    """Manages Docker volume configuration and operations."""

    def __init__(self, project_root: Path) -> None:
        """
        Initialize volume manager.

        Args:
            project_root: Root directory of the project
        """
        self.project_root = Path(project_root).resolve()

    def get_volume_config(self) -> dict[str, Any]:
        """
        Get Docker volume configuration.

        Returns:
            Dictionary with volume configurations
        """
        return {
            "mcp-postgres-data": {
                "driver": "local",
                "driver_opts": {
                    "type": "none",
                    "o": "bind",
                    "device": str(self.project_root / "data" / "postgres"),
                },
            },
            "mcp-python-cache": {
                "driver": "local",
                "driver_opts": {
                    "type": "none",
                    "o": "bind",
                    "device": str(self.project_root / ".cache"),
                },
            },
            "mcp-redis-data": {
                "driver": "local",
                "driver_opts": {
                    "type": "none",
                    "o": "bind",
                    "device": str(self.project_root / "data" / "redis"),
                },
            },
        }

    def create_volume_directories(self) -> bool:
        """
        Create necessary volume directories and validate configuration.

        Returns:
            True if volumes are properly configured
        """
        try:
            # Create local data directories if needed
            data_dir = self.project_root / "data"
            data_dir.mkdir(exist_ok=True, parents=True)

            # Create specific service data directories
            postgres_dir = data_dir / "postgres"
            postgres_dir.mkdir(exist_ok=True, parents=True)

            redis_dir = data_dir / "redis"
            redis_dir.mkdir(exist_ok=True, parents=True)

            # Create cache directory
            cache_dir = self.project_root / ".cache"
            cache_dir.mkdir(exist_ok=True, parents=True)

            # Create cache subdirectories
            (cache_dir / "pip").mkdir(exist_ok=True, parents=True)
            (cache_dir / "pytest").mkdir(exist_ok=True, parents=True)
            (cache_dir / "mypy").mkdir(exist_ok=True, parents=True)

            # Set proper permissions for directories (Unix systems)
            try:
                import os
                import stat

                if os.name == "posix":
                    # Make data directories writable by the user and group
                    postgres_dir.chmod(
                        stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH | stat.S_IXOTH
                    )
                    redis_dir.chmod(
                        stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH | stat.S_IXOTH
                    )
                    cache_dir.chmod(
                        stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH | stat.S_IXOTH
                    )
            except Exception:
                # Permissions setting failed, but directories were created
                pass

            return True
        except Exception as e:
            print(f"Failed to create volume directories: {e}")
            return False

    def validate_volume_config(self) -> bool:
        """
        Validate Docker volume configuration.

        Returns:
            True if volume configuration is valid
        """
        try:
            volume_config = self.get_volume_config()

            # Check that all volumes have required properties
            for volume_name, config in volume_config.items():
                if not isinstance(config, dict):
                    return False
                if "driver" not in config:
                    return False

            return bool(volume_config and len(volume_config) > 0)
        except Exception:
            return False

    def get_volume_status(self) -> dict[str, Any]:
        """
        Get status of Docker volumes.

        Returns:
            Dictionary with volume status information
        """
        try:
            volumes = self.get_volume_config()

            # Check if volume directories exist
            volume_dirs_status = {}
            for volume_name, config in volumes.items():
                if "driver_opts" in config and "device" in config["driver_opts"]:
                    device_path = Path(config["driver_opts"]["device"])
                    volume_dirs_status[volume_name] = {
                        "exists": device_path.exists(),
                        "is_directory": device_path.is_dir(),
                        "path": str(device_path),
                    }
                else:
                    volume_dirs_status[volume_name] = {
                        "exists": False,
                        "path": "unknown",
                    }

            return {
                "volumes_configured": len(volumes),
                "volume_names": list(volumes.keys()),
                "project_root": str(self.project_root),
                "volume_directories": volume_dirs_status,
            }
        except Exception as e:
            return {"error": str(e), "status": "error"}

    def cleanup_volume_directories(self) -> bool:
        """
        Clean up volume directories (for development/testing).

        Returns:
            True if cleanup was successful
        """
        try:
            import shutil

            # Remove data directories
            data_dir = self.project_root / "data"
            if data_dir.exists():
                shutil.rmtree(data_dir)

            # Remove cache directory
            cache_dir = self.project_root / ".cache"
            if cache_dir.exists():
                shutil.rmtree(cache_dir)

            return True
        except Exception as e:
            print(f"Failed to cleanup volume directories: {e}")
            return False


def get_volume_config() -> dict[str, Any]:
    """
    Get Docker volume configuration.

    Returns:
        Dictionary with volume configurations for Docker Compose
    """
    try:
        project_root = get_project_root()
        volume_manager = DockerVolumeManager(project_root)
        return volume_manager.get_volume_config()
    except Exception:
        # Fallback configuration
        return {
            "mcp-postgres-data": {
                "driver": "local",
            },
            "mcp-python-cache": {
                "driver": "local",
            },
        }


def configure_volumes() -> bool:
    """
    Configure Docker volumes for MCP development.

    Returns:
        True if configuration was successful, False otherwise
    """
    try:
        project_root = get_project_root()
        volume_manager = DockerVolumeManager(project_root)
        return volume_manager.create_volume_directories()
    except Exception as e:
        print(f"✗ Failed to configure Docker volumes: {str(e)}")
        return False


def validate_volume_config() -> bool:
    """
    Validate Docker volume configuration.

    Returns:
        True if volume configuration is valid
    """
    try:
        project_root = get_project_root()
        volume_manager = DockerVolumeManager(project_root)
        return volume_manager.validate_volume_config()
    except Exception:
        return False


def cleanup_volumes() -> bool:
    """
    Clean up all Docker volumes (for development/testing).

    Returns:
        True if cleanup was successful
    """
    try:
        project_root = get_project_root()
        volume_manager = DockerVolumeManager(project_root)
        return volume_manager.cleanup_volume_directories()
    except Exception as e:
        print(f"✗ Failed to cleanup Docker volumes: {str(e)}")
        return False
