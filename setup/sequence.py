"""
Setup Sequence Management
Orchestrates the complete setup process with proper error handling and rollback.
"""

from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .typings import SetupMode
from .validation.base import ValidationContext
from .validation.composite import CompositeValidator
from .validation.registry import get_global_registry
from .validation.reporters import ValidationReport


@dataclass
class SetupSequenceResult:
    """Result of a setup sequence execution."""

    success: bool
    mode: SetupMode
    validation_report: ValidationReport
    setup_metadata: dict[str, Any]
    errors: list[str]
    warnings: list[str]


class EnvironmentManagerStub:
    """Stub implementation for environment manager until the module is available."""

    def __init__(self, workspace_root: Path) -> None:
        """Initialize environment manager stub."""
        self.workspace_root = workspace_root

    async def setup_environment(self) -> bool:
        """Stub implementation for environment setup."""
        try:
            # Create basic workspace directories
            (self.workspace_root / "data").mkdir(exist_ok=True)
            (self.workspace_root / "logs").mkdir(exist_ok=True)
            (self.workspace_root / "cache").mkdir(exist_ok=True)
            return True
        except (OSError, PermissionError):
            return False


class SetupSequenceManager:
    """
    Manages the complete setup sequence with validation and rollback capabilities.

    Follows SOLID principles and provides comprehensive setup orchestration.
    """

    def __init__(
        self,
        workspace_root: Path | str,
        mode: SetupMode = SetupMode.DEVELOPMENT,
        verbose: bool = False,
    ) -> None:
        """Initialize setup sequence manager."""
        self.workspace_root = (
            Path(workspace_root) if isinstance(workspace_root, str) else workspace_root
        )
        self.mode = mode
        self.verbose = verbose

        # Create validation context
        self.context = ValidationContext(
            workspace_root=str(self.workspace_root),
            environment=dict(os.environ),
            config={"mode": mode.value, "verbose": verbose},
        )

        self.registry = get_global_registry()

    async def execute_complete_setup(self) -> SetupSequenceResult:
        """Execute the complete setup sequence."""
        setup_metadata: dict[str, Any] = {
            "mode": self.mode.value,
            "workspace_root": str(self.workspace_root),
            "timestamp": asyncio.get_event_loop().time(),
        }

        errors: list[str] = []
        warnings: list[str] = []

        try:
            # Phase 1: Validation
            if self.verbose:
                print("🔍 Running validation phase...")

            composite = await self._run_validation_phase()
            validation_report = composite.create_report()

            if not composite.is_valid():
                errors.extend(
                    [
                        f"Validation failed: {name}"
                        for name in composite.get_failed_validators()
                    ]
                )
                return SetupSequenceResult(
                    success=False,
                    mode=self.mode,
                    validation_report=validation_report,
                    setup_metadata=setup_metadata,
                    errors=errors,
                    warnings=warnings,
                )

            # Phase 2: Environment Setup
            if self.verbose:
                print("🔧 Setting up environment...")

            env_success = await self._setup_environment_phase()
            if not env_success:
                errors.append("Environment setup failed")

            # Phase 3: Tools Setup
            if self.verbose:
                print("🛠️ Setting up development tools...")

            tools_success = await self._setup_tools_phase()
            if not tools_success:
                warnings.append("Some development tools setup failed")

            overall_success = env_success and len(errors) == 0

            return SetupSequenceResult(
                success=overall_success,
                mode=self.mode,
                validation_report=validation_report,
                setup_metadata=setup_metadata,
                errors=errors,
                warnings=warnings,
            )

        except Exception as e:
            errors.append(f"Setup sequence failed: {str(e)}")
            return SetupSequenceResult(
                success=False,
                mode=self.mode,
                validation_report=ValidationReport(results=(), metadata={}),
                setup_metadata=setup_metadata,
                errors=errors,
                warnings=warnings,
            )

    async def _run_validation_phase(self) -> CompositeValidator:
        """Run the validation phase."""
        composite = CompositeValidator(self.context)

        # Add validators based on mode
        validator_names = ["python_environment", "project_structure", "dependencies"]

        if self.mode in (SetupMode.DOCKER, SetupMode.HYBRID):
            validator_names.append("docker_environment")

        for name in validator_names:
            try:
                validator = self.registry.create_validator(name, self.context)
                composite.add_validator(validator)
            except ValueError:
                if self.verbose:
                    print(f"⚠️ Validator '{name}' not available")

        # Run validation and return the composite validator itself
        composite.validate()
        return composite

    async def _setup_environment_phase(self) -> bool:
        """Setup the environment phase."""
        try:
            # Try to import the actual environment manager first
            try:
                from .environment.manager import EnvironmentManager

                env_manager = EnvironmentManager(self.workspace_root)
            except ImportError:
                # Fall back to stub implementation if module not available
                if self.verbose:
                    print("⚠️ Using stub environment manager")
                env_manager = EnvironmentManagerStub(self.workspace_root)

            # Use the manager for actual environment setup
            success = await env_manager.setup_environment()
            return success
        except Exception as e:
            if self.verbose:
                print(f"Environment setup failed: {e}")
            return False

    async def _setup_tools_phase(self) -> bool:
        """Setup development tools phase."""
        try:
            # Setup VS Code configuration
            from .vscode.integration import VSCodeIntegrationManager

            vscode_manager = VSCodeIntegrationManager(self.workspace_root)
            vscode_success = vscode_manager.create_workspace_configuration()

            # Setup Docker configuration if needed
            docker_success = True
            if self.mode in (SetupMode.DOCKER, SetupMode.HYBRID):
                docker_success = await self._setup_docker_tools()

            return vscode_success and docker_success
        except Exception as e:
            if self.verbose:
                print(f"Tools setup failed: {e}")
            return False

    async def _setup_docker_tools(self) -> bool:
        """Setup Docker-related tools."""
        try:
            from .infra.docker.volume_config import DockerVolumeManager

            volume_manager = DockerVolumeManager(self.workspace_root)
            return volume_manager.create_volume_directories()
        except Exception as e:
            if self.verbose:
                print(f"Docker tools setup failed: {e}")
            return False

    def get_setup_status(self) -> dict[str, Any]:
        """Get current setup status."""
        return {
            "mode": self.mode.value,
            "workspace_root": str(self.workspace_root),
            "registry_validators": len(self.registry.list_validators()),
        }

    async def rollback_setup(self) -> bool:
        """Rollback setup changes if needed."""
        try:
            # Clean up VS Code configuration
            from .vscode.integration import VSCodeIntegrationManager

            vscode_manager = VSCodeIntegrationManager(self.workspace_root)
            vscode_success = vscode_manager.cleanup_workspace()

            # Clean up Docker volumes if needed
            docker_success = True
            if self.mode in (SetupMode.DOCKER, SetupMode.HYBRID):
                try:
                    from .infra.docker.volume_config import DockerVolumeManager

                    volume_manager = DockerVolumeManager(self.workspace_root)
                    docker_success = volume_manager.cleanup_volumes()
                except Exception:
                    docker_success = False

            return vscode_success and docker_success
        except Exception as e:
            if self.verbose:
                print(f"Rollback failed: {e}")
            return False

    def validate_prerequisites(self) -> dict[str, bool]:
        """Validate setup prerequisites."""
        prerequisites = {
            "workspace_exists": self.workspace_root.exists(),
            "workspace_writable": (
                os.access(self.workspace_root, os.W_OK)
                if self.workspace_root.exists()
                else False
            ),
            "python_available": True,  # We're running Python
        }

        # Check Docker availability if needed
        if self.mode in (SetupMode.DOCKER, SetupMode.HYBRID):
            import shutil

            prerequisites["docker_available"] = shutil.which("docker") is not None

        return prerequisites


async def run_setup_sequence(
    workspace_root: Path | str,
    mode: SetupMode = SetupMode.DEVELOPMENT,
    verbose: bool = False,
) -> SetupSequenceResult:
    """Run the complete setup sequence."""
    sequence_manager = SetupSequenceManager(workspace_root, mode, verbose)
    return await sequence_manager.execute_complete_setup()


async def validate_setup_prerequisites(
    workspace_root: Path | str,
    mode: SetupMode = SetupMode.DEVELOPMENT,
) -> dict[str, bool]:
    """Validate setup prerequisites without running the full setup."""
    sequence_manager = SetupSequenceManager(workspace_root, mode, verbose=False)
    return sequence_manager.validate_prerequisites()


__all__ = [
    "SetupSequenceManager",
    "SetupSequenceResult",
    "EnvironmentManagerStub",
    "run_setup_sequence",
    "validate_setup_prerequisites",
]
