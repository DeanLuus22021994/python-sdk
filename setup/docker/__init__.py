"""
Docker Setup Module
Modern Docker configuration and management for the MCP Python SDK setup.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any

from ..typings import ValidationStatus
from ..typings.environment import ValidationDetails
from ..validation.base import ValidationContext
from ..validation.registry import get_global_registry


class DockerSetupManager:
    """
    Modern Docker setup manager using the validation framework.

    Coordinates Docker environment setup, validation, and configuration
    following SOLID principles and modern Python patterns.
    """

    def __init__(self, workspace_root: Path | str, verbose: bool = False) -> None:
        """Initialize Docker setup manager."""
        self.workspace_root = (
            Path(workspace_root) if isinstance(workspace_root, str) else workspace_root
        )
        self.verbose = verbose

        # Create validation context
        self.context = ValidationContext(
            workspace_root=str(self.workspace_root),
            environment=dict(os.environ),
            config={"component": "docker", "verbose": verbose},
        )

    def setup_docker_environment(self) -> bool:
        """Set up complete Docker environment."""
        try:
            # Use the modern validation framework
            registry = get_global_registry()

            try:
                validator = registry.create_validator(
                    "docker_environment", self.context
                )
                validation_result = validator.validate()

                if not validation_result.is_valid:
                    if self.verbose:
                        print(
                            f"❌ Docker validation failed: {validation_result.message}"
                        )
                    return False

                if self.verbose:
                    print("✅ Docker environment validation passed")

            except ValueError:
                # Fallback if docker validator not available
                if self.verbose:
                    print("⚠️ Docker validator not available, skipping validation")

            return True

        except Exception as e:
            if self.verbose:
                print(f"❌ Docker setup failed: {e}")
            return False

    def validate_complete_setup(self) -> ValidationDetails:
        """Validate complete Docker setup."""
        registry = get_global_registry()

        try:
            validator = registry.create_validator("docker_environment", self.context)
            result = validator.validate()

            return ValidationDetails(
                is_valid=result.is_valid,
                status=result.status,
                message=result.message,
                warnings=list(result.warnings),
                errors=list(result.errors),
                recommendations=list(result.recommendations),
                metadata=result.metadata,
                component_name="Docker",
            )

        except ValueError:
            # Fallback validation
            return ValidationDetails(
                is_valid=True,
                status=ValidationStatus.WARNING,
                message="Docker validator not available",
                warnings=["Docker validator not registered"],
                errors=[],
                recommendations=["Ensure docker validator is properly registered"],
                metadata={"workspace_root": str(self.workspace_root)},
                component_name="Docker",
            )

    def cleanup_environment(self) -> bool:
        """Clean up Docker environment."""
        try:
            # Clean up Docker containers and volumes if needed
            containers = subprocess.run(
                ["docker", "ps", "-a", "-q", "--filter", "label=mcp-python-sdk"],
                capture_output=True,
                text=True,
            )

            if containers.returncode == 0 and containers.stdout.strip():
                subprocess.run(
                    ["docker", "rm", "-f"] + containers.stdout.strip().split(),
                    capture_output=True,
                )

            return True

        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    def get_setup_status(self) -> dict[str, Any]:
        """Get current Docker setup status."""
        validation = self.validate_complete_setup()

        return {
            "docker_available": validation.is_valid,
            "status": validation.status.value,
            "message": validation.message,
            "workspace_root": str(self.workspace_root),
            "errors": validation.errors,
            "warnings": validation.warnings,
        }


def validate_docker_environment(
    workspace_root: Path | str | None = None,
) -> ValidationDetails:
    """Validate the Docker environment."""
    root = Path(workspace_root) if workspace_root else Path.cwd()
    manager = DockerSetupManager(root)
    return manager.validate_complete_setup()


__all__ = [
    "DockerSetupManager",
    "validate_docker_environment",
]
