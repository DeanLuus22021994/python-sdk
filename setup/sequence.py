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
        self.workspace_root = Path(workspace_root)
        self.mode = mode
        self.verbose = verbose
        self.context = ValidationContext(
            workspace_root=str(self.workspace_root),
            environment=dict(os.environ),
            config={"mode": mode.value, "verbose": verbose},
            cache_enabled=True,
            verbose=verbose,
        )
        self.reporter = ConsoleReporter()
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
        Run the complete setup sequence with reporting.

        Returns:
            True if setup is successful
        """
        print("🚀 Starting MCP Python SDK Setup")
        print("=" * 50)  # Run validation
        report = self.run_setup_validation()

        # Generate and display report
        report_text = self.reporter.format_report(report)
        print(report_text)

        # Check if setup is successful
        success = report.valid_count > 0 and report.error_count == 0

        if success:
            print("\n✅ Setup validation completed successfully!")
            if report.warning_count > 0:
                print(f"⚠️  Note: {report.warning_count} warning(s) found")
        else:
            print(f"\n❌ Setup validation failed with {report.error_count} error(s)")

        return success

    def get_validation_summary(self) -> dict[str, Any]:
        """Get summary of validation results."""
        report = self.run_setup_validation()
        return {
            "total_validations": report.total_validations,
            "valid_count": report.valid_count,
            "invalid_count": report.invalid_count,
            "error_count": report.error_count,
            "warning_count": report.warning_count,
            "overall_success": report.valid_count > 0 and report.error_count == 0,
        }


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
    orchestrator = ModernSetupOrchestrator(
        workspace_root=workspace_root,
        mode=SetupMode.HOST,
        verbose=False,
    )

    return orchestrator.run_complete_setup()


if __name__ == "__main__":
    success = run_setup_sequence()
    exit(0 if success else 1)
