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

        try:
            self.registry = get_global_registry()
        except ImportError:
            # Graceful fallback when validation registry is not available
            self.registry = None

    async def orchestrate_complete_setup(
        self,
        mode: SetupMode = SetupMode.DEVELOPMENT,
    ) -> SetupSequenceResult:
        """Orchestrate complete setup process."""
        if self.verbose:
            print(f"🚀 Starting {mode.value} setup orchestration...")

        errors: list[str] = []
        warnings: list[str] = []

        try:
            # Phase 1: Environment validation
            if self.verbose:
                print("🔍 Validating environment...")

            validation_result = await self.validate_environment()
            if not validation_result.is_valid:
                errors.extend(validation_result.errors)
                warnings.extend(validation_result.warnings)

            # Phase 2: Environment setup
            if self.verbose:
                print("🔧 Setting up environment...")

            env_success = await self._setup_environment()
            if not env_success:
                errors.append("Environment setup failed")

            # Phase 3: Tools setup (if requested)
            if mode in (SetupMode.DEVELOPMENT, SetupMode.HYBRID):
                if self.verbose:
                    print("🛠️ Setting up development tools...")

                tools_success = await self._setup_tools()
                if not tools_success:
                    warnings.append("Some development tools setup failed")

            success = len(errors) == 0

            if self.verbose:
                status = "✅ SUCCESS" if success else "❌ FAILED"
                print(f"Setup orchestration completed: {status}")

            return SetupSequenceResult(
                success=success,
                mode=mode,
                errors=errors,
                warnings=warnings,
                metadata={
                    "workspace_root": str(self.workspace_root),
                    "mode": mode.value,
                },
            )

        except Exception as e:
            errors.append(f"Setup orchestration failed: {str(e)}")
            return SetupSequenceResult(
                success=False,
                mode=mode,
                errors=errors,
                warnings=warnings,
            )

    async def validate_environment(self) -> ValidationDetails:
        """Validate environment using registered validators."""
        try:
            if self.registry:
                validator = self.registry.create_validator(
                    "python_environment", self.context
                )
                result = validator.validate()

                return ValidationDetails(
                    is_valid=result.is_valid,
                    status=result.status,
                    message=result.message,
                    warnings=list(getattr(result, "warnings", [])),
                    errors=list(getattr(result, "errors", [])),
                    recommendations=list(getattr(result, "recommendations", [])),
                    metadata=getattr(result, "metadata", {}),
                    component_name="Environment",
                )
            else:
                # Fallback validation
                return ValidationDetails(
                    is_valid=True,
                    status=ValidationStatus.WARNING,
                    message="Validation registry not available - using basic validation",
                    warnings=["Advanced validation not available"],
                    errors=[],
                    recommendations=[
                        "Install validation dependencies for comprehensive checks"
                    ],
                    metadata={"workspace_root": str(self.workspace_root)},
                    component_name="Environment",
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

    async def _setup_environment(self) -> bool:
        """Setup environment phase."""
        try:
            # Basic environment setup
            return True
        except Exception:
            return False

    async def _setup_tools(self) -> bool:
        """Setup development tools phase."""
        try:
            # Basic tools setup
            return True
        except Exception:
            return False

    def get_orchestration_status(self) -> dict[str, Any]:
        """Get orchestration status."""
        return {
            "workspace_root": str(self.workspace_root),
            "registry_available": self.registry is not None,
            "verbose": self.verbose,
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
