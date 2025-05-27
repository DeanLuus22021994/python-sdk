"""
Modern Setup Orchestrator
Provides unified orchestration for all setup operations following SOLID principles.
"""

from __future__ import annotations

import asyncio
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
            self.workspace_root,
            mode=mode,
            verbose=self.verbose,
        )

        result = await sequence_manager.execute_complete_setup()

        if self.verbose:
            self._print_orchestration_summary(result)

        return result

    async def validate_environment(self) -> ValidationDetails:
        """Validate environment using orchestrator."""
        try:
            # Use environment manager for validation
            from .environment.manager import EnvironmentManager

            env_manager = EnvironmentManager(self.workspace_root, self.registry)
            validation_result = await env_manager.validate_environment()

            # Convert to ValidationDetails format
            is_valid, env_info, errors = validation_result

            return ValidationDetails(
                is_valid=is_valid,
                status=ValidationStatus.VALID if is_valid else ValidationStatus.ERROR,
                message="Environment validation completed",
                errors=errors,
                warnings=[],
                recommendations=[],
                component_name="Environment",
                metadata={
                    "python_version": str(env_info.python_version),
                    "platform": env_info.platform_system,
                    "virtual_env_active": env_info.virtual_env_active,
                },
            )

        except Exception as e:
            return ValidationDetails(
                is_valid=False,
                status=ValidationStatus.ERROR,
                message=f"Environment validation failed: {str(e)}",
                errors=[str(e)],
                warnings=[],
                recommendations=["Check environment setup and try again"],
                component_name="Environment",
                metadata={"workspace_root": str(self.workspace_root)},
            )

    def get_orchestration_status(self) -> dict[str, Any]:
        """Get orchestration status."""
        return {
            "workspace_root": str(self.workspace_root),
            "registry_initialized": self.registry is not None,
            "available_validators": len(self.registry.list_validators()),
            "verbose": self.verbose,
        }

    def _print_orchestration_summary(self, result: SetupSequenceResult) -> None:
        """Print orchestration summary."""
        print("\n" + "="*60)
        print("🎯 SETUP ORCHESTRATION SUMMARY")
        print("="*60)

        status_icon = "✅" if result.success else "❌"
        print(f"{status_icon} Status: {'SUCCESS' if result.success else 'FAILED'}")
        print(f"🔧 Mode: {result.mode.value}")
        print(f"📁 Workspace: {result.setup_metadata.get('workspace_root', 'Unknown')}")

        if result.errors:
            print(f"\n❌ Errors ({len(result.errors)}):")
            for error in result.errors:
                print(f"  • {error}")

        if result.warnings:
            print(f"\n⚠️ Warnings ({len(result.warnings)}):")
            for warning in result.warnings:
                print(f"  • {warning}")

        print("\n" + "="*60)


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
