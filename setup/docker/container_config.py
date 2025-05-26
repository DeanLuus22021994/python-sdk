"""Docker container configuration utilities."""

from pathlib import Path
from typing import Any

import yaml

try:
    from setup.environment import get_project_root
except ImportError:
    from pathlib import Path

    def get_project_root() -> Path:
        """Get the project root directory."""
        return Path(__file__).parent.parent.parent


class DockerContainerManager:
    """Manages Docker container configuration."""

    def __init__(self, project_root: Path) -> None:
        """Initialize container manager."""
        self.project_root = project_root

    def get_container_config(self) -> dict[str, Any]:
        """Get Docker container configuration for development."""
        return {
            "mcp-postgres": {
                "image": "postgres:14-alpine",
                "container_name": "mcp-postgres",
                "environment": {
                    "POSTGRES_USER": "mcp_user",
                    "POSTGRES_PASSWORD": "mcp_password",
                    "POSTGRES_DB": "mcp_development",
                },
                "ports": ["5432:5432"],
                "volumes": ["mcp-postgres-data:/var/lib/postgresql/data"],
                "restart": "unless-stopped",
                "healthcheck": {
                    "test": [
                        "CMD",
                        "pg_isready",
                        "-U",
                        "mcp_user",
                        "-d",
                        "mcp_development",
                    ],
                    "interval": "5s",
                    "timeout": "5s",
                    "retries": 5,
                },
            },
            "mcp-dev": {
                "build": {
                    "context": str(self.project_root),
                    "dockerfile": "setup/docker/dockerfiles/Dockerfile.dev",
                },
                "container_name": "mcp-dev",
                "volumes": [
                    f"{self.project_root}:/app",
                    "mcp-python-cache:/root/.cache/pip",
                ],
                "working_dir": "/app",
                "command": "sleep infinity",
                "depends_on": ["mcp-postgres"],
            },
        }

    def create_container_config(self) -> bool:
        """Create container configuration."""
        return True


def get_container_config() -> dict[str, Any]:
    """
    Get Docker container configuration for development.

    Returns:
        Dictionary with container configurations
    """
    project_root = get_project_root()

    return {
        "mcp-postgres": {
            "image": "postgres:14-alpine",
            "container_name": "mcp-postgres",
            "environment": {
                "POSTGRES_USER": "mcp_user",
                "POSTGRES_PASSWORD": "mcp_password",
                "POSTGRES_DB": "mcp_development",
            },
            "ports": ["5432:5432"],
            "volumes": ["mcp-postgres-data:/var/lib/postgresql/data"],
            "restart": "unless-stopped",
            "healthcheck": {
                "test": [
                    "CMD",
                    "pg_isready",
                    "-U",
                    "mcp_user",
                    "-d",
                    "mcp_development",
                ],
                "interval": "5s",
                "timeout": "5s",
                "retries": 5,
            },
        },
        "mcp-dev": {
            "build": {
                "context": str(project_root),
                "dockerfile": "setup/docker/dockerfiles/Dockerfile.dev",
            },
            "container_name": "mcp-dev",
            "volumes": [
                f"{project_root}:/app",
                "mcp-python-cache:/root/.cache/pip",
            ],
            "working_dir": "/app",
            "command": "sleep infinity",
            "depends_on": ["mcp-postgres"],
        },
    }


def create_docker_compose_file(output_path: Path | None = None) -> Path:
    """
    Create a docker-compose.yml file for local development.

    Args:
        output_path: Custom path to write the file (defaults to project root)

    Returns:
        Path to the created docker-compose.yml file
    """
    if output_path is None:
        output_path = get_project_root() / "docker-compose.yml"

    container_config = get_container_config()

    # Import volume config
    from .volume_config import get_volume_config

    volume_config = get_volume_config()

    compose_config = {
        "version": "3.8",
        "services": container_config,
        "volumes": volume_config,
    }

    # Convert to YAML
    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(compose_config, f, default_flow_style=False, sort_keys=False)

    return output_path


def configure_containers() -> bool:
    """
    Configure Docker containers for MCP development.

    Returns:
        True if configuration was successful, False otherwise
    """
    try:
        docker_compose_path = create_docker_compose_file()
        print(f"✓ Docker Compose configuration created at {docker_compose_path}")

        # Create Dockerfile.dev
        create_development_dockerfile()
        print("✓ Development Dockerfile created")

        return True
    except Exception as e:
        print(f"✗ Failed to configure Docker containers: {str(e)}")
        return False


def create_development_dockerfile() -> Path:
    """
    Create a development Dockerfile.

    Returns:
        Path to the created Dockerfile
    """
    project_root = get_project_root()
    dockerfile_dir = project_root / "setup" / "docker" / "dockerfiles"
    dockerfile_dir.mkdir(parents=True, exist_ok=True)

    dockerfile_path = dockerfile_dir / "Dockerfile.dev"

    dockerfile_content = """FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    git \\
    curl \\
    build-essential \\
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ /app/src/

# Set environment variables
ENV PYTHONPATH=/app:$PYTHONPATH
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

CMD ["bash"]
"""

    with open(dockerfile_path, "w", encoding="utf-8") as f:
        f.write(dockerfile_content)

    return dockerfile_path
