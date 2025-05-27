"""
Environment Manager
Central coordination of environment validation and setup.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..typings import (
    EnvironmentInfo,
    EnvironmentValidationResult,
    LogLevel,
    SetupMode,
    ValidationStatus,
)
from ..validation import BaseValidator, ValidationContext, ValidationRegistry
from .constants import DEFAULT_PERFORMANCE_SETTINGS
from .path_validator import PathStructureValidator
from .python_validator import PythonEnvironmentValidator
from .structure_validator import ProjectStructureValidator
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
        self._workspace_root = Path(workspace_root) if workspace_root else get_project_root()
        self._registry = registry or ValidationRegistry()
        self._context = ValidationContext(
            workspace_root=str(self._workspace_root),
            config={"performance": DEFAULT_PERFORMANCE_SETTINGS.__dict__},
        )
        self._cache: dict[str, Any] = {}

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
        validators = [
            self._get_validator("python_environment"),
            self._get_validator("project_structure"),
            self._get_validator("path_structure"),
        ]

        if parallel:
            results = await self._run_parallel_validation(validators)
        else:
            results = await self._run_sequential_validation(validators)

        return self._aggregate_results(results)

    async def setup_environment(
        self,
        config: EnvironmentSetupConfig | None = None,
    ) -> bool:
        """
        Complete environment setup.

        Args:
            config: Setup configuration

        Returns:
            True if setup was successful
        """
        config = config or EnvironmentSetupConfig()

        try:
            # Validate current state
            validation = await self.validate_environment()
            if validation.status == ValidationStatus.ERROR:
                return False

            # Setup operations based on configuration
            if config.create_venv:
                await self._setup_virtual_environment()

            if config.configure_vscode:
                await self._setup_vscode_configuration()

            if config.enable_pre_commit:
                await self._setup_pre_commit()

            return True

        except Exception:
            return False

    def get_environment_info(self) -> EnvironmentInfo:
        """
        Get comprehensive environment information.

        Returns:
            Environment information structure
        """
        python_validator = self._get_validator("python_environment")
        structure_validator = self._get_validator("project_structure")

        # Collect information from validators
        python_info = python_validator.get_python_info()
        structure_info = structure_validator.get_structure_info()

        return EnvironmentInfo(
            python_version=python_info.version,
            platform_info=python_info.platform,
            virtual_environment=python_info.virtual_environment,
            package_managers=python_info.package_managers,
            project_structure=structure_info,
            workspace_root=str(self._workspace_root),
        )

    def get_status_summary(self) -> dict[str, Any]:
        """
        Get simplified status summary.

        Returns:
            Status dictionary with basic information
        """
        env_info = self.get_environment_info()

        return {
            "python_version": str(env_info.python_version),
            "platform": env_info.platform_info.system,
            "virtual_env_active": env_info.virtual_environment.active,
            "project_structure_valid": env_info.project_structure.is_valid,
            "workspace_root": env_info.workspace_root,
        }

    def _get_validator(self, name: str) -> BaseValidator[Any]:
        """Get validator instance from registry."""
        validator_class = self._registry.get_validator_class(name)
        if not validator_class:
            raise ValueError(f"Validator '{name}' not found in registry")

        return validator_class(self._context)

    async def _run_parallel_validation(
        self,
        validators: list[BaseValidator[Any]],
    ) -> list[Any]:
        """Run validators in parallel."""
        tasks = [validator.validate() for validator in validators]
        return await asyncio.gather(*tasks, return_exceptions=True)

    async def _run_sequential_validation(
        self,
        validators: list[BaseValidator[Any]],
    ) -> list[Any]:
        """Run validators sequentially."""
        results = []
        for validator in validators:
            result = await validator.validate()
            results.append(result)
        return results

    def _aggregate_results(self, results: list[Any]) -> EnvironmentValidationResult:
        """Aggregate validation results into final result."""
        all_valid = all(
            getattr(result, 'is_valid', False)
            for result in results
            if not isinstance(result, Exception)
        )

        errors = []
        warnings = []

        for result in results:
            if isinstance(result, Exception):
                errors.append(str(result))
            elif hasattr(result, 'errors'):
                errors.extend(result.errors)
            elif hasattr(result, 'warnings'):
                warnings.extend(result.warnings)

        status = ValidationStatus.VALID if all_valid else ValidationStatus.ERROR
        if warnings and all_valid:
            status = ValidationStatus.WARNING

        return EnvironmentValidationResult(
            is_valid=all_valid,
            status=status,
            message="Environment validation complete",
            errors=tuple(errors),
            warnings=tuple(warnings),
        )

    async def _setup_virtual_environment(self) -> None:
        """Setup virtual environment if needed."""
        # Implementation for virtual environment setup
        pass

    async def _setup_vscode_configuration(self) -> None:
        """Setup VS Code configuration."""
        # Implementation for VS Code setup
        pass

    async def _setup_pre_commit(self) -> None:
        """Setup pre-commit hooks."""
        # Implementation for pre-commit setup
        pass
