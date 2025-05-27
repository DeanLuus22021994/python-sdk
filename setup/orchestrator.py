"""
Modern Setup Orchestrator
Provides unified orchestration for all setup operations following SOLID principles.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .typings import SetupMode, ValidationStatus
from .typings.environment import ValidationDetails
from .validation.base import ValidationContext
from .validation.registry import get_global_registry


class SetupSequenceResult:
    """Result container for setup operations."""

    def __init__(
        self,
        success: bool,
        mode: SetupMode,
        errors: list[str] | None = None,
        warnings: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.success = success
        self.mode = mode
        self.errors = errors or []
        self.warnings = warnings or []
        self.metadata = metadata or {}


class ModernSetupOrchestrator:
    """Modern setup orchestrator implementing comprehensive setup coordination."""

    def __init__(
        self,
        workspace_root: Path | str | None = None,
        verbose: bool = False,
    ) -> None:
        from .config.utils import get_project_root

        self.workspace_root = (
            Path(workspace_root) if workspace_root else get_project_root()
        )
        self.verbose = verbose
        self.registry = get_global_registry()

        # Create validation context
        self.context = ValidationContext(
            workspace_root=str(self.workspace_root),
            environment=dict(os.environ),
            config={"verbose": verbose},
        )

    def orchestrate_setup(self) -> bool:
        """Synchronous setup orchestration - wrapper for async method."""
        import asyncio
        try:
            result = asyncio.run(self.orchestrate_complete_setup())
            return result.success
        except Exception as e:
            if self.verbose:
                print(f"Setup orchestration error: {e}")
            return False

    async def orchestrate_complete_setup(
        self,
        mode: SetupMode = SetupMode.DEVELOPMENT,
    ) -> SetupSequenceResult:
        """Orchestrate complete setup process."""
        if self.verbose:
            print(f"🚀 Starting setup orchestration in {mode} mode...")

        errors: list[str] = []
        warnings: list[str] = []
        metadata: dict[str, Any] = {
            "mode": mode.value if hasattr(mode, "value") else str(mode),
            "workspace_root": str(self.workspace_root),
        }

        try:
            # Phase 1: Environment validation
            if self.verbose:
                print("📋 Phase 1: Environment validation...")

            validation = await self.validate_environment()
            if not validation.is_valid:
                errors.extend(validation.errors)
                return SetupSequenceResult(False, mode, errors, warnings, metadata)

            # Phase 2: Environment setup
            if self.verbose:
                print("🔧 Phase 2: Environment setup...")

            env_success = await self._setup_environment()
            if not env_success:
                errors.append("Environment setup failed")

            # Phase 3: Tools setup
            if self.verbose:
                print("🛠️  Phase 3: Tools setup...")

            tools_success = await self._setup_tools()
            if not tools_success:
                errors.append("Tools setup failed")

            success = env_success and tools_success
            if self.verbose:
                status = "✅ Success" if success else "❌ Failed"
                print(f"🏁 Setup orchestration completed: {status}")

            return SetupSequenceResult(success, mode, errors, warnings, metadata)

        except Exception as e:
            errors.append(f"Setup orchestration failed: {e}")
            return SetupSequenceResult(False, mode, errors, warnings, metadata)    async def validate_environment(self) -> ValidationDetails:
        """Validate complete environment."""
        try:
            # Use validation registry for validation
            from .validation.composite import CompositeValidator

            validator = CompositeValidator(self.context)

            # Add available validators from registry
            for validator_name in self.registry.list_validators():
                try:
                    validator_instance = self.registry.get_validator(validator_name, self.context)
                    if validator_instance:
                        validator.add_validator(validator_instance)
                except Exception as e:
                    if self.verbose:
                        print(f"Warning: Could not load validator {validator_name}: {e}")

            # Run composite validation
            result = validator.validate()

            return ValidationDetails(
                is_valid=result.is_valid,
                status=result.status,
                message=result.message,
                component_name="Environment",
                errors=result.errors,
                warnings=result.warnings,
                recommendations=result.recommendations,
            )

        except Exception as e:
            return ValidationDetails(
                is_valid=False,
                status=ValidationStatus.ERROR,
                message=f"Environment validation failed: {e}",
                component_name="Environment",
                errors=[str(e)],
            )

    async def _setup_environment(self) -> bool:
        """Setup environment components."""
        try:
            from .environment import EnvironmentManager

            manager = EnvironmentManager(self.workspace_root)
            return await manager.setup_environment()

        except Exception as e:
            if self.verbose:
                print(f"Environment setup error: {e}")
            return False

    async def _setup_tools(self) -> bool:
        """Setup development tools."""
        try:
            # Setup VS Code if available
            from .vscode.integration import VSCodeIntegrationManager

            vscode_manager = VSCodeIntegrationManager(self.workspace_root)
            vscode_success = vscode_manager.create_workspace_configuration()

            if self.verbose and vscode_success:
                print("✅ VS Code configuration created")

            return vscode_success

        except Exception as e:
            if self.verbose:
                print(f"Tools setup error: {e}")
            return False

    def get_orchestration_status(self) -> dict[str, Any]:
        """Get current orchestration status."""
        return {
            "workspace_root": str(self.workspace_root),
            "verbose": self.verbose,
            "registry_validators": self.registry.list_validators(),
        }


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
    "SetupSequenceResult",
    "orchestrate_setup",
    "validate_setup_environment",
]
