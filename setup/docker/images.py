"""
Docker Image Management
Handles Docker image building and management for the MCP Python SDK.
"""

from pathlib import Path

from ..environment.utils import get_project_root
from ..typings import ValidationStatus
from ..typings.environment import ValidationDetails


class DockerImageManager:
    """Manages Docker image building and configuration."""

    def __init__(self, workspace_root: Path | None = None) -> None:
        """Initialize image manager."""
        self.workspace_root = (
            Path(workspace_root) if workspace_root else get_project_root()
        )
        self.dockerfile_path = self.workspace_root / "Dockerfile"

    def validate_image_config(self) -> ValidationDetails:
        """Validate Docker image configuration."""
        errors: list[str] = []
        warnings: list[str] = []

        if not self.dockerfile_path.exists():
            errors.append("Dockerfile not found")

        # Check for required base files
        required_files = ["pyproject.toml", "src"]
        for file_name in required_files:
            file_path = self.workspace_root / file_name
            if not file_path.exists():
                warnings.append(f"Required file/directory missing: {file_name}")

        is_valid = len(errors) == 0
        return ValidationDetails(
            is_valid=is_valid,
            status=ValidationStatus.VALID if is_valid else ValidationStatus.ERROR,
            message=(
                "Image configuration is valid"
                if is_valid
                else "Image validation failed"
            ),
            errors=errors,
            warnings=warnings,
            component_name="Docker Image",
        )

    def build_image(self, tag: str = "mcp-python-sdk:latest") -> bool:
        """Build Docker image."""
        import subprocess

        try:
            result = subprocess.run(
                ["docker", "build", "-t", tag, str(self.workspace_root)],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.returncode == 0
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def pull_required_images(self) -> dict[str, bool]:
        """Pull required base images."""
        import subprocess

        required_images = [
            "python:3.11-slim",
            "python:3.12-slim",
        ]

        results = {}
        for image in required_images:
            try:
                result = subprocess.run(
                    ["docker", "pull", image],
                    capture_output=True,
                    text=True,
                    timeout=300,
                )
                results[image] = result.returncode == 0
            except (subprocess.TimeoutExpired, FileNotFoundError):
                results[image] = False

        return results

    def check_required_images(self) -> dict[str, bool]:
        """Check if required images are available."""
        import subprocess

        required_images = [
            "python:3.11-slim",
            "python:3.12-slim",
        ]

        results = {}
        for image in required_images:
            try:
                result = subprocess.run(
                    ["docker", "image", "inspect", image],
                    capture_output=True,
                    text=True,
                )
                results[image] = result.returncode == 0
            except FileNotFoundError:
                results[image] = False

        return results
