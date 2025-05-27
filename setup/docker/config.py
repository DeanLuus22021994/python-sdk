"""
Docker Configuration Management
Modernized Docker configuration using the validation framework.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from ..environment.utils import get_project_root
from ..typings import ValidationStatus
from ..typings.environment import ValidationDetails


class DockerConfigManager:
    """Manages Docker configuration and validation using modern patterns."""

    def __init__(self, workspace_root: Path | None = None) -> None:
        """Initialize Docker configuration manager."""
        self.workspace_root = Path(workspace_root) if workspace_root else get_project_root()

    def validate_configuration(self) -> ValidationDetails:
        """Validate Docker container configuration."""
        errors: list[str] = []
        warnings: list[str] = []
        recommendations: list[str] = []

        # Check if Docker is available
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                errors.append("Docker is not available or not working")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            errors.append("Docker is not installed")

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
        message = "Docker configuration is valid" if is_valid else f"Validation failed: {len(errors)} errors"

        return ValidationDetails(
            is_valid=is_valid,
            status=ValidationStatus.VALID if is_valid else ValidationStatus.ERROR,
            message=message,
            errors=errors,
            warnings=warnings,
            recommendations=recommendations,
            component_name="Docker Container",
            metadata={
                "workspace_root": str(self.workspace_root),
            },
        )


__all__ = ["DockerConfigManager"]
