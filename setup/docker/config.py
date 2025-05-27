"""
Docker Configuration Management
Modernized Docker configuration using the validation framework.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from ..environment.utils import get_project_root
from ..typings import ContainerConfig, ValidationStatus
from ..typings.environment import ValidationDetails


class DockerConfigManager:
    """Manages Docker configuration and validation using modern patterns."""

    def __init__(self, workspace_root: Path | None = None) -> None:
        """Initialize Docker configuration manager."""
        self.workspace_root = (
            Path(workspace_root) if workspace_root else get_project_root()
        )
        self.config = ContainerConfig()

    def generate_compose_config(self) -> dict[str, Any]:
        """Generate Docker Compose configuration."""
        return {
            "version": "3.8",
            "services": {
                "mcp-python-sdk": {
                    **self.config.get_docker_compose_config(),
                    "volumes": [
                        f"{self.workspace_root}:/app",
                        "/app/.venv",  # Anonymous volume for virtual environment
                    ],
                    "environment": [
                        "PYTHONPATH=/app/src",
                        "PYTHONDONTWRITEBYTECODE=1",
                        "PYTHONUNBUFFERED=1",
                    ],
                }
            },
        }

    def save_compose_file(self) -> Path:
        """Save Docker Compose configuration to file."""
        config = self.generate_compose_config()
        compose_path = self.workspace_root / "docker-compose.yml"

        with open(compose_path, "w", encoding="utf-8") as f:
            import yaml

            yaml.dump(config, f, default_flow_style=False)

        return compose_path

    def generate_dockerfile_content(self) -> str:
        """Generate Dockerfile content based on configuration."""
        return f"""# Multi-stage Dockerfile for MCP Python SDK
FROM {self.config.base_image} as base

# Set working directory
WORKDIR {self.config.work_dir}

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    git \\
    curl \\
    build-essential \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY pyproject.toml ./
COPY README.md ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \\
    && pip install --no-cache-dir -e .[dev]

# Copy source code
COPY src/ ./src/
COPY tests/ ./tests/

# Create development stage
FROM base as development

# Install development tools
RUN pip install --no-cache-dir \\
    pytest \\
    pytest-cov \\
    black \\
    isort \\
    mypy \\
    flake8

# Set development environment
ENV PYTHONPATH={self.config.work_dir}/src
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE {self.config.expose_port}

# Health check
HEALTHCHECK --interval={self.config.health_check_interval}s \\
    --timeout=10s \\
    --start-period=5s \\
    --retries=3 \\
    CMD python -c "import sys; sys.exit(0)"

# Default command
CMD ["python", "-m", "mcp.server"]
"""

    def save_dockerfile(self) -> Path:
        """Save Dockerfile to workspace."""
        dockerfile_content = self.generate_dockerfile_content()
        dockerfile_path = self.workspace_root / "Dockerfile"

        with open(dockerfile_path, "w", encoding="utf-8") as f:
            f.write(dockerfile_content)

        return dockerfile_path

    def validate_configuration(self) -> ValidationDetails:
        """Validate Docker container configuration."""
        errors: list[str] = []
        warnings: list[str] = []
        recommendations: list[str] = []

        # Check if Docker is available
        try:
            result = subprocess.run(
                ["docker", "--version"], capture_output=True, text=True, timeout=5
            )
            if result.returncode != 0:
                errors.append("Docker is not available or not working")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            errors.append("Docker is not installed")

        # Validate configuration
        if not self.config.base_image:
            errors.append("Base image is required")

        if not self.config.work_dir.startswith("/"):
            errors.append("Work directory must be an absolute path")

        # Check workspace
        if not self.workspace_root.exists():
            errors.append(f"Workspace root does not exist: {self.workspace_root}")

        # Check for required files
        required_files = ["pyproject.toml"]
        for file_name in required_files:
            file_path = self.workspace_root / file_name
            if not file_path.exists():
                warnings.append(f"Required file missing: {file_name}")

        is_valid = len(errors) == 0
        message = (
            "Docker configuration is valid"
            if is_valid
            else f"Validation failed: {len(errors)} errors"
        )

        return ValidationDetails(
            is_valid=is_valid,
            status=ValidationStatus.VALID if is_valid else ValidationStatus.ERROR,
            message=message,
            errors=errors,
            warnings=warnings,
            recommendations=recommendations,
            component_name="Docker Container",
            metadata={
                "base_image": self.config.base_image,
                "work_dir": self.config.work_dir,
                "workspace_root": str(self.workspace_root),
            },
        )

    def get_container_info(self) -> dict[str, Any]:
        """Get Docker container information."""
        return {
            "docker_available": True,
            "compose_available": True,
            "workspace_root": str(self.workspace_root),
        }

    def create_container_config(self) -> dict[str, Any]:
        """Create complete Docker configuration."""
        return {
            "base_image": self.config.base_image,
            "working_directory": self.config.work_dir,
            "exposed_ports": [self.config.expose_port],
            "environment_variables": {
                "PYTHONPATH": f"{self.config.work_dir}/src",
                "PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONUNBUFFERED": "1",
            },
            "build_context": str(self.workspace_root),
            "dockerfile_path": "Dockerfile",
        }
