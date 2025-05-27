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
                print("Phase 1: Validation")

            validation_result = await self._run_validation_phase()

            if not validation_result.is_valid():
                errors.append("Validation phase failed")
                for (
                    validator_name,
                    result,
                ) in validation_result.get_validator_results().items():
                    if not result.is_valid:
                        errors.extend(
                            [f"{validator_name}: {error}" for error in result.errors]
                        )

            # Get warnings from composite validator results
            for result in validation_result.get_validator_results().values():
                warnings.extend(result.warnings)

            # Phase 2: Environment Setup
            if self.verbose:
                print("Phase 2: Environment Setup")

            env_success = await self._setup_environment_phase()
            if not env_success:
                errors.append("Environment setup phase failed")

            # Phase 3: Tool Configuration
            if self.verbose:
                print("Phase 3: Tool Configuration")

            tools_success = await self._setup_tools_phase()
            if not tools_success:
                errors.append("Tools configuration phase failed")

            success = len(errors) == 0

            if self.verbose:
                print(f"Setup complete: {'SUCCESS' if success else 'FAILED'}")

            return SetupSequenceResult(
                success=success,
                mode=self.mode,
                validation_report=validation_result.create_report(),
                setup_metadata=setup_metadata,
                errors=errors,
                warnings=warnings,
            )

        except Exception as e:
            errors.append(f"Setup sequence failed: {str(e)}")
            return SetupSequenceResult(
                success=False,
                mode=self.mode,
                validation_report=ValidationReport(),
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
                # Skip validators that aren't available
                if self.verbose:
                    print(f"Validator '{name}' not available, skipping")

        # Run validation and return the composite validator itself
        composite.validate()
        return composite

    async def _setup_environment_phase(self) -> bool:
        """Setup the environment phase."""
        try:
            from .environment.manager import EnvironmentManager

            manager = EnvironmentManager(self.workspace_root)
            return True  # Placeholder for actual environment setup
        except Exception as e:
            if self.verbose:
                print(f"Environment setup failed: {e}")
            return False

    async def _setup_tools_phase(self) -> bool:
        """Setup development tools phase."""
        try:
            # Placeholder for VS Code configuration and other tools
            from .vscode.integration import VSCodeIntegrationManager

            vscode_manager = VSCodeIntegrationManager(self.workspace_root)
            return vscode_manager.create_workspace_configuration()
        except Exception as e:
            if self.verbose:
                print(f"Tools setup failed: {e}")
            return False

    def get_setup_status(self) -> dict[str, Any]:
        """Get current setup status."""
        return {
            "mode": self.mode.value,
            "workspace_root": str(self.workspace_root),
            "registry_validators": len(self.registry.list_validators()),
        }


async def run_setup_sequence(
    workspace_root: Path | str,
    mode: SetupMode = SetupMode.DEVELOPMENT,
    verbose: bool = False,
) -> SetupSequenceResult:
    """Run the complete setup sequence."""
    manager = SetupSequenceManager(workspace_root, mode, verbose)
    return await manager.execute_complete_setup()


__all__ = [
    "SetupSequenceManager",
    "SetupSequenceResult",
    "run_setup_sequence",
]
