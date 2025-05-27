"""
Docker Image Management
Handles Docker image building and management for the MCP Python SDK.
"""

from pathlib import Path

from ..environment.utils import get_project_root
from ..typings import ValidationDetails


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
        errors = []
        warnings = []

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
            status="valid" if is_valid else "error",
            message=(
                "Image configuration is valid"
                if is_valid
                else "Image validation failed"
            ),
            errors=errors,
            warnings=warnings,
            component_name="Docker Image",
        )
