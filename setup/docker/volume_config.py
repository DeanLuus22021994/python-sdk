"""Docker volume configuration utilities."""

import subprocess
from pathlib import Path
from typing import Any

try:
    from setup.environment import get_project_root
except ImportError:
    from pathlib import Path

    def get_project_root() -> Path:
        """Get the project root directory."""
        return Path(__file__).parent.parent.parent


def get_volume_config() -> dict[str, dict[str, str]]:
    """
    Get Docker volume configuration.

    Returns:
        Dictionary with volume configurations
    """
    return {
        "mcp-postgres-data": {"driver": "local"},
        "mcp-python-cache": {"driver": "local"},
    }


def check_volume_exists(volume_name: str) -> bool:
    """
    Check if a Docker volume exists.

    Args:
        volume_name: Name of the volume to check

    Returns:
        True if volume exists, False otherwise
    """
    try:
        result = subprocess.run(
            ["docker", "volume", "inspect", volume_name],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0
    except Exception:
        return False


def create_volume(volume_name: str) -> tuple[bool, str | None]:
    """
    Create a Docker volume.

    Args:
        volume_name: Name of the volume to create

    Returns:
        Tuple of (success, error_message)
    """
    try:
        if check_volume_exists(volume_name):
            return True, None

        # Execute docker volume create but don't store unused result
        subprocess.run(
            ["docker", "volume", "create", volume_name],
            capture_output=True,
            text=True,
            check=True,
        )
        return True, None
    except Exception as e:
        return False, str(e)


def configure_volumes() -> tuple[bool, list[str]]:
    """
    Configure Docker volumes for MCP development.

    Returns:
        Tuple of (success, error_messages)
    """
    volume_config = get_volume_config()
    errors = []

    for volume_name in volume_config:
        success, error = create_volume(volume_name)
        if not success:
            errors.append(f"Failed to create volume {volume_name}: {error}")

    return len(errors) == 0, errors


def get_volume_info(volume_name: str) -> dict[str, Any]:
    """
    Get detailed information about a Docker volume.

    Args:
        volume_name: Name of the volume

    Returns:
        Dictionary with volume information
    """
    try:
        if not check_volume_exists(volume_name):
            return {"name": volume_name, "exists": False}

        result = subprocess.run(
            ["docker", "volume", "inspect", volume_name],
            capture_output=True,
            text=True,
            check=True,
        )

        import json

        volume_info = json.loads(result.stdout)[0]

        return {
            "name": volume_name,
            "exists": True,
            "driver": volume_info.get("Driver", "unknown"),
            "mountpoint": volume_info.get("Mountpoint", "unknown"),
            "created": volume_info.get("CreatedAt", "unknown"),
        }
    except Exception:
        return {
            "name": volume_name,
            "exists": False,
            "error": "Failed to inspect volume",
        }
