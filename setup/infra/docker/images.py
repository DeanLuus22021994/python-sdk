"""
Docker Image Management
Handles Docker image building and management for the MCP Python SDK.
"""

import subprocess
from pathlib import Path

from ...config.utils import get_project_root
from ...typings import ValidationStatus
from ...typings.environment import ValidationDetails


class DockerImageManager:
    """Manages Docker image building and configuration."""

    def __init__(self, workspace_root: Path | None = None) -> None:
        """Initialize image manager."""
        self.workspace_root = (
            Path(workspace_root) if workspace_root else get_project_root()
        )
        self.dockerfile_path = (
            self.workspace_root / "setup" / "docker" / "dockerfiles" / "Dockerfile.dev"
        )

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

        # Use correct parameter names for ValidationDetails
        return ValidationDetails(
            valid=is_valid,
            status=ValidationStatus.VALID if is_valid else ValidationStatus.ERROR,
            details=(
                "Image configuration is valid"
                if is_valid
                else "Image validation failed"
            ),
            error_messages=errors,
            warning_messages=warnings,
            metadata={
                "component": "Docker Image",
                "dockerfile_path": str(self.dockerfile_path),
            },
        )

    def build_image(self, tag: str = "mcp-python-sdk:latest") -> bool:
        """Build Docker image."""
        try:
            result = subprocess.run(
                [
                    "docker",
                    "build",
                    "-f",
                    str(self.dockerfile_path),
                    "-t",
                    tag,
                    str(self.workspace_root),
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.returncode == 0
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def pull_required_images(self) -> dict[str, bool]:
        """Pull required base images."""
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
                    check=True,
                )
                results[image] = result.returncode == 0
            except (subprocess.CalledProcessError, FileNotFoundError):
                results[image] = False

        return results

    def check_required_images(self) -> dict[str, bool]:
        """Check if required images are available."""
        required_images = [
            "python:3.11-slim",
            "python:3.12-slim",
        ]

        results = {}
        for image in required_images:
            try:
                result = subprocess.run(
                    ["docker", "images", "-q", image],
                    capture_output=True,
                    text=True,
                )
                results[image] = bool(result.stdout.strip())
            except (subprocess.CalledProcessError, FileNotFoundError):
                results[image] = False

        return results

    def get_image_info(self, image_name: str) -> dict[str, str | None]:
        """Get information about a specific image."""
        try:
            result = subprocess.run(
                ["docker", "inspect", image_name, "--format", "{{json .}}"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                import json

                image_data = json.loads(result.stdout.strip())
                return {
                    "id": image_data.get("Id", ""),
                    "created": image_data.get("Created", ""),
                    "size": str(image_data.get("Size", 0)),
                }
        except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError):
            pass
        return {"id": None, "created": None, "size": None}

    def cleanup_images(self, force: bool = False) -> bool:
        """Clean up unused Docker images."""
        try:
            cmd = ["docker", "image", "prune"]
            if force:
                cmd.append("--force")
            else:
                cmd.append("--all")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
            )
            return result.returncode == 0
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def get_build_context_size(self) -> int:
        """Get the size of the Docker build context."""
        try:
            import os

            total_size = 0
            for dirpath, dirnames, filenames in os.walk(self.workspace_root):
                # Skip .git and other unnecessary directories
                dirnames[:] = [
                    d
                    for d in dirnames
                    if not d.startswith(".")
                    and d not in ["__pycache__", "node_modules"]
                ]
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                    except (OSError, FileNotFoundError):
                        continue
            return total_size
        except Exception:
            return 0


__all__ = [
    "DockerImageManager",
]
