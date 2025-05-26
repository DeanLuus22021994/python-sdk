"""Docker volume configuration and management utilities."""

from pathlib import Path
from typing import Any

try:
    from setup.environment import get_project_root
except ImportError:
    from pathlib import Path

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
            },
            "mcp-python-cache": {
                "driver": "local",
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
            data_dir.mkdir(exist_ok=True)

            # Create cache directory
            cache_dir = self.project_root / ".cache"
            cache_dir.mkdir(exist_ok=True)

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
            return {
                "volumes_configured": len(volumes),
                "volume_names": list(volumes.keys()),
                "project_root": str(self.project_root),
            }
        except Exception as e:
            return {"error": str(e), "status": "error"}


def get_volume_config() -> dict[str, Any]:
    """
    Get Docker volume configuration.

    Returns:
        Dictionary with volume configurations for Docker Compose
    """
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
        volume_config = get_volume_config()
        return bool(volume_config and len(volume_config) > 0)
    except Exception:
        return False
