"""
Setup Sequence Management
Modern orchestration system using the validation framework.
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any

from . import validators  # Import to trigger validator registration
from .typings.enums import SetupMode
from .validation.base import ValidationContext
from .validation.composite import CompositeValidator
from .validation.registry import get_global_registry
from .validation.reporters import ConsoleReporter, ValidationReport


class ModernSetupOrchestrator:
    """
    Modern setup orchestrator using the validation framework.

    Follows SOLID principles:
    - Single Responsibility: Coordinates setup validation
    - Open/Closed: Extensible with new validators
    - Dependency Inversion: Uses validation abstractions
    """

    def __init__(
        self,
        workspace_root: str | Path,
        mode: SetupMode = SetupMode.HOST,
        verbose: bool = False,
    ) -> None:
        """Initialize orchestrator."""
        self.workspace_root = Path(workspace_root).resolve()
        self.mode = mode
        self.verbose = verbose

        # Create validation context
        self.context = ValidationContext(
            workspace_root=str(self.workspace_root),
            environment=dict(os.environ),
            config={
                "mode": mode.value,
                "verbose": verbose,
            },
        )

        # Setup validators
        self._setup_validators()

    def _setup_validators(self) -> None:
        """Set up validators for the setup sequence."""
        # Import validators to ensure registration
        _ = validators  # Force import evaluation

        registry = get_global_registry()

        # Create core validators
        self.validators = [
            registry.create_validator("python_environment", self.context),
            registry.create_validator("project_structure", self.context),
            registry.create_validator("dependencies", self.context),
        ]

        # Add mode-specific validators
        if self.mode == SetupMode.HOST:
            try:
                self.validators.append(
                    registry.create_validator("vscode_workspace", self.context)
                )
            except ValueError:
                pass  # VS Code validator not available

        elif self.mode == SetupMode.DOCKER:
            try:
                self.validators.append(
                    registry.create_validator("docker_environment", self.context)
                )
            except ValueError:
                pass  # Docker validator not available

        # Create composite validator
        self.composite_validator = CompositeValidator(
            context=self.context,
            validators=self.validators,
            fail_fast=False,  # Run all validations to get complete picture
        )

    def run_setup_validation(self) -> ValidationReport:
        """
        Run complete setup validation.

        Returns:
            Validation report with all results
        """
        if self.verbose:
            print(f"🔍 Running setup validation in {self.mode.value} mode")
            print(f"📁 Workspace: {self.workspace_root}")

        start_time = time.time()

        # Run validation
        self.composite_validator.validate()

        # Get individual results
        individual_results = self.composite_validator.get_validator_results()

        execution_time = time.time() - start_time

        # Create validation report
        report = ValidationReport(
            results=tuple(individual_results.values()),
            metadata={
                "execution_time": execution_time,
                "mode": self.mode.value,
                "workspace_root": str(self.workspace_root),
            },
        )

        return report

    def run_complete_setup(self) -> bool:
        """
        Run complete setup process including validation and configuration.

        Returns:
            True if setup completed successfully
        """
        try:
            # Run validation first
            report = self.run_setup_validation()

            # Print validation results
            reporter = ConsoleReporter(verbose=self.verbose, use_colors=True)
            reporter.write_report(report)

            # Check if validation passed
            validation_success = all(result.is_valid for result in report.results)

            if not validation_success:
                print("❌ Validation failed. Please fix errors before proceeding.")
                return False

            # Run setup steps based on mode
            setup_success = self._run_setup_steps()

            return setup_success

        except Exception as e:
            if self.verbose:
                import traceback
                traceback.print_exc()
            else:
                print(f"❌ Setup failed: {e}")
            return False

    def _run_setup_steps(self) -> bool:
        """Run mode-specific setup steps."""
        try:
            if self.mode == SetupMode.HOST:
                return self._setup_host_environment()
            elif self.mode == SetupMode.DOCKER:
                return self._setup_docker_environment()
            elif self.mode == SetupMode.HYBRID:
                return self._setup_host_environment() and self._setup_docker_environment()
            else:
                return True

        except Exception as e:
            if self.verbose:
                print(f"❌ Setup step failed: {e}")
            return False

    def _setup_host_environment(self) -> bool:
        """Setup host development environment."""
        try:
            # Setup VS Code configuration
            from .vscode.integration import VSCodeIntegrationManager

            vscode_manager = VSCodeIntegrationManager(self.workspace_root)
            vscode_success = vscode_manager.create_workspace_configuration()

            if vscode_success and self.verbose:
                print("✅ VS Code workspace configured")

            return vscode_success

        except Exception as e:
            if self.verbose:
                print(f"❌ Host setup failed: {e}")
            return False

    def _setup_docker_environment(self) -> bool:
        """Setup Docker development environment."""
        try:
            from .docker import DockerSetupManager

            docker_manager = DockerSetupManager(self.workspace_root, self.verbose)
            docker_success = docker_manager.setup_docker_environment()

            if docker_success and self.verbose:
                print("✅ Docker environment configured")

            return docker_success

        except Exception as e:
            if self.verbose:
                print(f"❌ Docker setup failed: {e}")
            return False

    def get_validation_summary(self) -> dict[str, Any]:
        """Get summary of validation results."""
        report = self.run_setup_validation()

        summary = {
            "total_validators": len(report.results),
            "passed": sum(1 for r in report.results if r.is_valid),
            "failed": sum(1 for r in report.results if not r.is_valid),
            "warnings": sum(len(r.warnings) for r in report.results),
            "errors": sum(len(r.errors) for r in report.results),
            "execution_time": report.metadata.get("execution_time", 0),
        }

        return summary


# Legacy compatibility functions
def validate_python_version() -> tuple[bool, str]:
    """
    Legacy function for Python version validation.

    Returns:
        Tuple of (is_valid, message)
    """
    workspace_root = Path.cwd()
    context = ValidationContext(
        workspace_root=str(workspace_root),
        environment=dict(os.environ),
    )

    registry = get_global_registry()
    validator = registry.create_validator("python_environment", context)
    result = validator.validate()

    return result.is_valid, result.message


def check_required_paths() -> tuple[bool, list[str]]:
    """
    Legacy function for path validation.

    Returns:
        Tuple of (is_valid, missing_paths)
    """
    workspace_root = Path.cwd()
    context = ValidationContext(
        workspace_root=str(workspace_root),
        environment=dict(os.environ),
    )

    registry = get_global_registry()
    validator = registry.create_validator("project_structure", context)
    result = validator.validate()

    missing_paths = []
    if result.data and "missing_required" in result.data:
        missing_paths = result.data["missing_required"]

    return result.is_valid, missing_paths


def run_setup_sequence() -> bool:
    """
    Run the complete setup sequence (legacy interface).

    Returns:
        True if all setup steps completed successfully
    """
    workspace_root = Path.cwd()
    orchestrator = ModernSetupOrchestrator(workspace_root=workspace_root)
    return orchestrator.run_complete_setup()


if __name__ == "__main__":
    success = run_setup_sequence()
    exit(0 if success else 1)
