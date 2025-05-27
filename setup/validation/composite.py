"""
Composite Validation Framework
Provides composite validation capabilities for complex validation scenarios.
"""

from __future__ import annotations

from typing import Any

from ..typings.enums import ValidationStatus
from .base import BaseValidator, ValidationContext, ValidationResult
from .reporters import ValidationReport

__all__ = [
    "CompositeValidator",
]


class CompositeValidator:
    """
    Composite validator that manages multiple validators.

    Implements the Composite pattern for complex validation scenarios.
    Follows SOLID principles:
    - Single Responsibility: Orchestrates validation execution
    - Open/Closed: Extensible with new validators
    - Dependency Inversion: Uses validator abstractions
    """

    def __init__(
        self,
        context: ValidationContext,
        validators: list[BaseValidator[Any]] | None = None,
        fail_fast: bool = False,
    ) -> None:
        """Initialize composite validator."""
        self.context = context
        self.validators = validators or []
        self.fail_fast = fail_fast
        self._results: dict[str, ValidationResult[Any]] = {}

    def add_validator(self, validator: BaseValidator[Any]) -> None:
        """Add a validator to the composite."""
        self.validators.append(validator)

    def remove_validator(self, validator_name: str) -> bool:
        """Remove a validator by name."""
        for i, validator in enumerate(self.validators):
            if validator.get_validator_name() == validator_name:
                del self.validators[i]
                # Also remove from results if exists
                if validator_name in self._results:
                    del self._results[validator_name]
                return True
        return False

    def validate(self) -> ValidationResult[dict[str, Any]]:
        """
        Execute all validators and return composite result.

        Returns:
            Composite validation result
        """
        self._results.clear()

        all_valid = True
        aggregated_errors: list[str] = []
        aggregated_warnings: list[str] = []
        aggregated_recommendations: list[str] = []
        aggregated_metadata: dict[str, Any] = {}

        for validator in self.validators:
            try:
                result = validator.validate()
                validator_name = validator.get_validator_name()
                self._results[validator_name] = result

                # Aggregate results
                if not result.is_valid:
                    all_valid = False

                aggregated_errors.extend(result.errors)
                aggregated_warnings.extend(result.warnings)
                aggregated_recommendations.extend(result.recommendations)

                # Add validator-specific metadata
                aggregated_metadata[validator_name] = result.metadata

                # Fail fast if requested and validation failed
                if self.fail_fast and not result.is_valid:
                    break

            except Exception as e:
                # Handle validator execution errors
                all_valid = False
                validator_name = validator.get_validator_name()
                error_msg = f"Validator '{validator_name}' failed: {str(e)}"
                aggregated_errors.append(error_msg)

                # Create error result for this validator
                self._results[validator_name] = ValidationResult(
                    is_valid=False,
                    status=ValidationStatus.ERROR,
                    message=error_msg,
                    errors=(error_msg,),
                )

                if self.fail_fast:
                    break

        # Create composite result
        if aggregated_errors:
            status = ValidationStatus.ERROR
            message = f"Composite validation failed: {len(aggregated_errors)} error(s)"
        elif aggregated_warnings:
            status = ValidationStatus.WARNING
            message = f"Composite validation passed with {len(aggregated_warnings)} warning(s)"
        else:
            status = ValidationStatus.VALID
            message = "All validations passed successfully"

        return ValidationResult(
            is_valid=all_valid,
            status=status,
            message=message,
            data=aggregated_metadata,
            errors=tuple(aggregated_errors),
            warnings=tuple(aggregated_warnings),
            recommendations=tuple(aggregated_recommendations),
            metadata={
                "validators_executed": len(self._results),
                "total_validators": len(self.validators),
                "fail_fast": self.fail_fast,
            },
        )

    def get_validator_results(self) -> dict[str, ValidationResult[Any]]:
        """Get individual validator results."""
        return self._results.copy()

    def get_failed_validators(self) -> list[str]:
        """Get names of validators that failed."""
        return [
            name for name, result in self._results.items()
            if not result.is_valid
        ]

    def get_successful_validators(self) -> list[str]:
        """Get names of validators that passed."""
        return [
            name for name, result in self._results.items()
            if result.is_valid
        ]

    def clear_results(self) -> None:
        """Clear validation results."""
        self._results.clear()

    def is_valid(self) -> bool:
        """Quick check if all validations passed."""
        return all(result.is_valid for result in self._results.values())

    def has_warnings(self) -> bool:
        """Check if any validations have warnings."""
        return any(len(result.warnings) > 0 for result in self._results.values())

    def get_summary(self) -> dict[str, Any]:
        """Get validation summary."""
        total = len(self.validators)
        executed = len(self._results)
        successful = len(self.get_successful_validators())
        failed = len(self.get_failed_validators())

        return {
            "total_validators": total,
            "executed_validators": executed,
            "successful_validators": successful,
            "failed_validators": failed,
            "overall_valid": self.is_valid(),
            "has_warnings": self.has_warnings(),
        }

    def create_report(self) -> ValidationReport:
        """Create a validation report from results."""
        return ValidationReport(
            results=tuple(self._results.values()),
            metadata=self.get_summary(),
        )
