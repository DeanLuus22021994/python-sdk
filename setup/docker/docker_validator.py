"""Docker environment validation utilities."""

import platform
import subprocess

try:
    from setup.environment import get_project_root
except ImportError:
    from pathlib import Path

    def get_project_root() -> Path:
        """Get the project root directory."""
        return Path(__file__).parent.parent.parent


def check_docker_daemon() -> tuple[bool, str]:
    """
    Check if Docker daemon is running.

    Returns:
        Tuple of (is_running, message)
    """
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return True, "✓ Docker daemon is running"
        return False, "✗ Docker daemon is not running"
    except FileNotFoundError:
        return False, "✗ Docker is not installed or not in PATH"
    except Exception as e:
        return False, f"✗ Error checking Docker daemon: {str(e)}"


def check_docker_version() -> tuple[bool, str]:
    """
    Check if Docker version meets requirements.

    Returns:
        Tuple of (meets_requirements, message)
    """
    min_version = (20, 10, 0)
    try:
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            check=True,
        )
        # Parse version from "Docker version 20.10.14, build a224086"
        version_str = result.stdout.split()[2].rstrip(",")
        version_parts = version_str.split(".")

        # Extract major and minor versions
        major = int(version_parts[0])
        minor = int(version_parts[1])
        patch = int(version_parts[2].split("-")[0]) if len(version_parts) > 2 else 0

        current_version = (major, minor, patch)

        if current_version >= min_version:
            return True, f"✓ Docker version {version_str} meets requirements"
        else:
            return False, (
                f"✗ Docker version {version_str} does not meet minimum "
                f"requirements {min_version[0]}.{min_version[1]}.{min_version[2]}"
            )
    except FileNotFoundError:
        return False, "✗ Docker is not installed or not in PATH"
    except Exception as e:
        return False, f"✗ Error checking Docker version: {str(e)}"


def check_docker_compose() -> tuple[bool, str]:
    """
    Check if Docker Compose is available.

    Returns:
        Tuple of (is_available, message)
    """
    try:
        # First try docker compose (V2)
        result = subprocess.run(
            ["docker", "compose", "version"],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            return True, "✓ Docker Compose V2 is available"

        # If V2 fails, try docker-compose (V1)
        result = subprocess.run(
            ["docker-compose", "--version"],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            return True, "✓ Docker Compose V1 is available"

        return False, "✗ Docker Compose is not available"
    except FileNotFoundError:
        return False, "✗ Docker Compose is not installed or not in PATH"
    except Exception as e:
        return False, f"✗ Error checking Docker Compose: {str(e)}"


def validate_docker_environment() -> tuple[bool, dict[str, bool | str]]:
    """
    Validate the Docker environment for MCP SDK development.

    Returns:
        Tuple containing:
        - bool: True if environment is valid
        - Dict: Environment details and validation results
    """
    # Run all checks
    daemon_running, daemon_msg = check_docker_daemon()
    version_valid, version_msg = check_docker_version()
    compose_available, compose_msg = check_docker_compose()

    # Determine if Docker environment is ready for development
    is_valid = daemon_running and version_valid and compose_available

    # Explicitly specify the dictionary types to match the return type annotation
    env_info: dict[str, bool | str] = {
        "daemon_running": daemon_running,
        "version_valid": version_valid,
        "compose_available": compose_available,
        "platform": platform.system(),
        "daemon_message": daemon_msg,
        "version_message": version_msg,
        "compose_message": compose_msg,
    }

    return is_valid, env_info


def get_docker_runtime_info() -> dict[str, str | list[str]]:
    """
    Get detailed information about the Docker runtime.

    Returns:
        Dict with Docker version, configuration, and capabilities
    """
    # Explicitly annotate the info dictionary with correct types
    info: dict[str, str | list[str]] = {
        "version": "unknown",
        "api_version": "unknown",
        "os": "unknown",
        "arch": "unknown",
        "cpu": "unknown",
        "memory": "unknown",
        "storage_driver": "unknown",
        "root_dir": "unknown",
        "plugins": [],  # Always initialize as a list
    }

    try:
        # Get Docker info
        result = subprocess.run(
            ["docker", "info", "--format", "{{json .}}"],
            capture_output=True,
            text=True,
            check=True,
        )

        import json

        docker_info = json.loads(result.stdout)

        # Extract relevant information
        info["version"] = docker_info.get("ServerVersion", "unknown")
        info["api_version"] = docker_info.get("ApiVersion", "unknown")
        info["os"] = docker_info.get("OperatingSystem", "unknown")
        info["arch"] = docker_info.get("Architecture", "unknown")
        info["cpu"] = f"{docker_info.get('NCPU', 'unknown')} cores"

        mem_bytes = docker_info.get("MemTotal", 0)
        info["memory"] = f"{mem_bytes // (1024*1024*1024)} GB"

        info["storage_driver"] = docker_info.get("Driver", "unknown")
        info["root_dir"] = docker_info.get("DockerRootDir", "unknown")

        # Extract plugins
        plugins_list: list[str] = []  # Create a temporary list for plugins
        if "Plugins" in docker_info:
            for plugin_type, plugins in docker_info["Plugins"].items():
                for plugin in plugins:
                    plugins_list.append(f"{plugin_type}: {plugin}")
        info["plugins"] = plugins_list  # Assign the complete list to info["plugins"]

    except Exception:
        # If we can't get detailed info, fall back to basic version
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                check=True,
            )
            info["version"] = result.stdout.strip()
        except Exception:
            pass

    return info
