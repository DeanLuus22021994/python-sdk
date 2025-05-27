"""
Modern Setup Orchestrator
Provides unified orchestration for all setup operations following SOLID principles.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .sequence import SetupSequenceManager, SetupSequenceResult
from .typings import SetupMode, ValidationStatus
from .typings.environment import ValidationDetails
from .validation.base import ValidationContext
from .validation.registry import get_global_registry


class ModernSetupOrchestrator:
    """
    Modern setup orchestrator implementing comprehensive setup coordination.

    Follows SOLID principles:
    - Single Responsibility: Orchestrates setup operations
    - Open/Closed: Extensible through validator registry
    - Liskov Substitution: Uses validation abstractions
    - Interface Segregation: Focused interface for setup operations
    - Dependency Inversion: Depends on abstractions
    """

    def __init__(
        self,
        workspace_root: Path | str | None = None,
        verbose: bool = False,
    ) -> None:
        """Initialize modern setup orchestrator."""
        self.workspace_root = Path(workspace_root) if workspace_root else Path.cwd()
        self.verbose = verbose

        self.context = ValidationContext(
            workspace_root=str(self.workspace_root),
            environment=dict(os.environ),
            config={"verbose": verbose},
        )

        self.registry = get_global_registry()

    async def orchestrate_complete_setup(
        self,
        mode: SetupMode = SetupMode.DEVELOPMENT,
    ) -> SetupSequenceResult:
        """Orchestrate complete setup process."""
        if self.verbose:
            print(f"🚀 Starting {mode.value} setup orchestration...")

        sequence_manager = SetupSequenceManager(
            workspace_root=self.workspace_root,
            mode=mode,
            verbose=self.verbose,
        )

        result = await sequence_manager.execute_complete_setup()

        if self.verbose:
            self._print_orchestration_summary(result)

        return result

    async def validate_environment(self) -> ValidationDetails:
        """Validate environment using registered validators."""
        try:
            validator = self.registry.create_validator(
                "python_environment", self.context
            )
            result = validator.validate()

            return ValidationDetails(
                is_valid=result.is_valid,
                status=result.status,
                message=result.message,
                warnings=list(result.warnings),
                errors=list(result.errors),
                recommendations=list(result.recommendations),
                metadata=result.metadata,
                component_name="Environment",
            )

        except ValueError:
            # Fallback validation
            return ValidationDetails(
                is_valid=True,
                status=ValidationStatus.WARNING,
                message="Python environment validator not available",
                warnings=["Python environment validator not registered"],
                errors=[],
                recommendations=["Register python environment validator"],
                metadata={"workspace_root": str(self.workspace_root)},
                component_name="Environment",
            )

    def get_orchestration_status(self) -> dict[str, Any]:
        """Get orchestration status."""
        return {
            "workspace_root": str(self.workspace_root),
            "registry_validators": len(self.registry.list_validators()),
            "verbose": self.verbose,
        }

    def _print_orchestration_summary(self, result: SetupSequenceResult) -> None:
        """Print orchestration summary."""
        if result.success:
            print("✅ Setup orchestration completed successfully")
        else:
            print("❌ Setup orchestration failed")
            for error in result.errors:
                print(f"  • {error}")


# Convenience functions for backward compatibility
async def orchestrate_setup(
    workspace_root: Path | str | None = None,
    mode: SetupMode = SetupMode.DEVELOPMENT,
    verbose: bool = False,
) -> SetupSequenceResult:
    """Orchestrate complete setup process."""
    orchestrator = ModernSetupOrchestrator(workspace_root, verbose)
    return await orchestrator.orchestrate_complete_setup(mode)


async def validate_setup_environment(
    workspace_root: Path | str | None = None,
    verbose: bool = False,
) -> ValidationDetails:
    """Validate setup environment."""
    orchestrator = ModernSetupOrchestrator(workspace_root, verbose)
    return await orchestrator.validate_environment()


__all__ = [
    "ModernSetupOrchestrator",
    "orchestrate_setup",
    "validate_setup_environment",
]
