"""
Docker Environment Validator
Validates Docker setup and configuration for the MCP Python SDK.
"""

from pathlib import Path

from ..environment.utils import get_project_root
from ..typings import ValidationDetails


class DockerValidator:
    """Validates Docker environment and configuration."""

    def __init__(self, workspace_root: Path | None = None) -> None:
        """Initialize Docker validator."""
        self.workspace_root = (
            Path(workspace_root) if workspace_root else get_project_root()
        )

    def validate_docker_setup(self) -> ValidationDetails:
        """Validate complete Docker setup."""
        errors = []
        warnings = []
        recommendations = []

        # Check Docker installation
        try:
            import subprocess

            result = subprocess.run(
                ["docker", "--version"], capture_output=True, text=True, timeout=5
            )
            if result.returncode != 0:
                errors.append("Docker is not working properly")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            errors.append("Docker is not installed")
            recommendations.append("Install Docker Desktop or Docker Engine")

        # Check Docker Compose
        try:
            import subprocess

            result = subprocess.run(
                ["docker", "compose", "version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode != 0:
                warnings.append("Docker Compose not available")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            warnings.append("Docker Compose not installed")

        is_valid = len(errors) == 0
        return ValidationDetails(
            is_valid=is_valid,
            status="valid" if is_valid else "error",
            message="Docker setup is valid" if is_valid else "Docker validation failed",
            errors=errors,
            warnings=warnings,
            recommendations=recommendations,
            component_name="Docker Environment",
        )
