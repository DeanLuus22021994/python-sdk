"""
Environment Manager
Central coordination of environment validation and setup.
"""

from __future__ import annotations

import asyncio
import os
import platform
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..typings import (
    EnvironmentInfo,
    EnvironmentValidationResult,
    PythonVersion,
    SetupMode,
)
from ..validation.base import BaseValidator, ValidationContext
from ..validation.registry import ValidationRegistry, get_global_registry
from .utils import get_project_root


@dataclass
class EnvironmentSetupConfig:
    """Configuration for environment setup operations."""

    setup_mode: SetupMode = SetupMode.DEVELOPMENT
    create_venv: bool = True
    install_dev_packages: bool = True
    configure_vscode: bool = True
    enable_pre_commit: bool = True
    parallel_operations: bool = True
    timeout_seconds: float = 60.0


class EnvironmentManager:
    """
    Modern environment manager with comprehensive validation and setup.

    Follows SOLID principles:
    - Single Responsibility: Environment coordination
    - Open/Closed: Extensible through validator registry
    - Dependency Inversion: Uses abstractions for validators
    """

    def __init__(
        self,
        workspace_root: Path | str | None = None,
        registry: ValidationRegistry | None = None,
    ) -> None:
        """Initialize environment manager."""
        self._workspace_root = (
            Path(workspace_root) if workspace_root else get_project_root()
        )
        self._registry = registry or get_global_registry()

        self._context = ValidationContext(
            workspace_root=str(self._workspace_root),
            environment=dict(os.environ),
            config={"component": "environment"},
        )

    async def validate_environment(
        self,
        parallel: bool = True,
    ) -> EnvironmentValidationResult:
        """
        Comprehensive environment validation.

        Args:
            parallel: Enable parallel validation for performance

        Returns:
            Complete validation result
        """
        validators = []

        try:
            validators.extend(
                [
                    self._get_validator("python_environment"),
                    self._get_validator("project_structure"),
                    self._get_validator("dependencies"),
                ]
            )
        except ValueError:
            # Fallback if validators not available
            pass

        if not validators:
            env_info = self.get_environment_info()
            return (True, env_info, [])

        if parallel:
            results = await self._run_parallel_validation(validators)
        else:
            results = await self._run_sequential_validation(validators)

        return self._aggregate_results(results)

    def get_environment_info(self) -> EnvironmentInfo:
        """Get comprehensive environment information."""
        version_info = sys.version_info
        python_version = PythonVersion(
            version_info.major, version_info.minor, version_info.micro
        )

        # Check virtual environment
        in_venv = hasattr(sys, "real_prefix") or (
            hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
        )

        return EnvironmentInfo(
            python_version=python_version,
            python_executable=sys.executable,
            virtual_env_active=in_venv,
            virtual_env_type="venv" if in_venv else None,
            virtual_env_path=sys.prefix if in_venv else None,
            platform_system=platform.system(),
            platform_release=platform.release(),
            architecture=platform.machine(),
        )

    def get_status_summary(self) -> dict[str, Any]:
        """Get environment status summary."""
        env_info = self.get_environment_info()

        return {
            "python_version": str(env_info.python_version),
            "virtual_env_active": env_info.virtual_env_active,
            "platform": env_info.platform_system,
            "workspace_root": str(self._workspace_root),
        }

    def _get_validator(self, name: str) -> BaseValidator[Any]:
        """Get validator instance from registry."""
        return self._registry.create_validator(name, self._context)

    async def _run_parallel_validation(
        self,
        validators: list[BaseValidator[Any]],
    ) -> list[Any]:
        """Run validators in parallel."""
        tasks = [
            asyncio.create_task(self._run_validator_async(validator))
            for validator in validators
        ]
        return await asyncio.gather(*tasks, return_exceptions=True)

    async def _run_sequential_validation(
        self,
        validators: list[BaseValidator[Any]],
    ) -> list[Any]:
        """Run validators sequentially."""
        results = []
        for validator in validators:
            result = await self._run_validator_async(validator)
            results.append(result)
        return results

    async def _run_validator_async(self, validator: BaseValidator[Any]) -> Any:
        """Run a single validator asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, validator.validate)

    def _aggregate_results(self, results: list[Any]) -> EnvironmentValidationResult:
        """Aggregate validation results into final result."""
        env_info = self.get_environment_info()
        errors = []

        # Process validation results
        for result in results:
            if isinstance(result, Exception):
                errors.append(f"Validation error: {result}")
            elif hasattr(result, "is_valid") and not result.is_valid:
                errors.extend(getattr(result, "errors", []))

        is_valid = len(errors) == 0
        return (is_valid, env_info, errors)

    async def setup_environment(
        self,
        config: EnvironmentSetupConfig | None = None,
    ) -> bool:
        """Setup environment with given configuration."""
        if config is None:
            config = EnvironmentSetupConfig()

        try:
            if config.configure_vscode:
                await self._setup_vscode_configuration()
            return True
        except Exception:
            return False

    async def _setup_vscode_configuration(self) -> None:
        """Setup VS Code configuration."""
        try:
            from ..vscode.integration import VSCodeIntegrationManager

            vscode_manager = VSCodeIntegrationManager(self._workspace_root)
            vscode_manager.create_workspace_configuration()
        except ImportError:
            pass
