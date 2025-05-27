"""
Composite Validation Framework
Implements the Composite pattern for combining multiple validators.
"""

from __future__ import annotations

import asyncio
from collections.abc import Sequence
from typing import Any

from ..typings.enums import ValidationStatus
from .base import BaseValidator, ValidationContext, ValidationResult

__all__ = [
    "CompositeValidator",
    "SequentialCompositeValidator",
    "ParallelCompositeValidator",
]


class CompositeValidator(BaseValidator[dict[str, Any]]):
    """
    Composite validator that combines multiple validators.

    Implements the Composite pattern, allowing validation of complex
    systems by combining simpler validators. Follows SOLID principles:
    - Single Responsibility: Coordinates multiple validators
    - Open/Closed: Can be extended with new validation strategies
    - Liskov Substitution: Can replace any BaseValidator
    """

    def __init__(
        self,
        context: ValidationContext,
        validators: Sequence[BaseValidator[Any]],
        fail_fast: bool = False,
    ) -> None:
        """
        Initialize composite validator.

        Args:
            context: Validation context
            validators: List of validators to execute
            fail_fast: Stop on first validation failure
        """
        super().__init__(context)
        self.validators = list(validators)
        self.fail_fast = fail_fast

    def get_validator_name(self) -> str:
        """Get composite validator name."""
        validator_names = [v.get_validator_name() for v in self.validators]
        return f"Composite[{', '.join(validator_names)}]"

    def _perform_validation(self) -> ValidationResult[dict[str, Any]]:
        """Execute all validators and combine results."""
        results: dict[str, ValidationResult[Any]] = {}
        all_errors: list[str] = []
        all_warnings: list[str] = []
        all_recommendations: list[str] = []
        combined_metadata: dict[str, Any] = {}

        overall_status = ValidationStatus.VALID
        any_valid = True

        for validator in self.validators:
            validator_name = validator.get_validator_name()

            try:
                result = validator.validate()
                results[validator_name] = result

                # Collect errors, warnings, and recommendations
                all_errors.extend(result.errors)
                all_warnings.extend(result.warnings)
                all_recommendations.extend(result.recommendations)

                # Merge metadata
                combined_metadata[validator_name] = result.metadata

                # Update overall status
                if not result.is_valid:
                    any_valid = False
                    if result.status == ValidationStatus.ERROR:
                        overall_status = ValidationStatus.ERROR
                    elif overall_status == ValidationStatus.VALID:
                        overall_status = ValidationStatus.WARNING

                # Stop on first failure if fail_fast is enabled
                if self.fail_fast and not result.is_valid:
                    break

            except Exception as e:
                error_msg = f"Validator {validator_name} failed: {e}"
                all_errors.append(error_msg)
                any_valid = False
                overall_status = ValidationStatus.ERROR

                # Create error result for this validator
                results[validator_name] = self._create_result(
                    is_valid=False,
                    status=ValidationStatus.ERROR,
                    message=error_msg,
                    errors=[error_msg],
                )

                if self.fail_fast:
                    break

        # Determine final validation status
        is_valid = any_valid and len(all_errors) == 0

        if len(all_errors) > 0:
            final_status = ValidationStatus.ERROR
        elif len(all_warnings) > 0:
            final_status = ValidationStatus.WARNING
        else:
            final_status = ValidationStatus.VALID

        # Create summary message
        total_validators = len(self.validators)
        valid_count = sum(1 for r in results.values() if r.is_valid)
        message = (
            f"Composite validation: {valid_count}/{total_validators} validators passed"
        )

        return self._create_result(
            is_valid=is_valid,
            status=final_status,
            message=message,
            data={"individual_results": results},
            errors=all_errors,
            warnings=all_warnings,
            recommendations=all_recommendations,
            **combined_metadata,
        )

    def add_validator(self, validator: BaseValidator[Any]) -> None:
        """Add a validator to the composite."""
        self.validators.append(validator)
        self.clear_cache()  # Invalidate cache when structure changes

    def remove_validator(self, validator_name: str) -> bool:
        """Remove a validator by name."""
        for i, validator in enumerate(self.validators):
            if validator.get_validator_name() == validator_name:
                self.validators.pop(i)
                self.clear_cache()
                return True
        return False

    def get_validator_results(self) -> dict[str, ValidationResult[Any]]:
        """Get individual validator results from last validation."""
        result = self.validate()
        if result.data and "individual_results" in result.data:
            return result.data["individual_results"]
        return {}


class SequentialCompositeValidator(CompositeValidator):
    """
    Sequential composite validator that runs validators in order.

    Provides explicit ordering guarantees for validators that have
    dependencies on each other.
    """

    def __init__(
        self,
        context: ValidationContext,
        validators: Sequence[BaseValidator[Any]],
        fail_fast: bool = True,  # Default to fail_fast for sequential
    ) -> None:
        """Initialize sequential composite validator."""
        super().__init__(context, validators, fail_fast)

    def get_validator_name(self) -> str:
        """Get sequential composite validator name."""
        return f"Sequential{super().get_validator_name()}"


class ParallelCompositeValidator(CompositeValidator):
    """
    Parallel composite validator that runs validators concurrently.

    Improves performance by running independent validators in parallel.
    Note: Only use when validators are truly independent.
    """

    def __init__(
        self,
        context: ValidationContext,
        validators: Sequence[BaseValidator[Any]],
        max_concurrency: int = 5,
    ) -> None:
        """
        Initialize parallel composite validator.

        Args:
            context: Validation context
            validators: List of validators to execute
            max_concurrency: Maximum number of concurrent validators
        """
        super().__init__(context, validators, fail_fast=False)
        self.max_concurrency = max_concurrency

    def get_validator_name(self) -> str:
        """Get parallel composite validator name."""
        return f"Parallel{super().get_validator_name()}"

    def _perform_validation(self) -> ValidationResult[dict[str, Any]]:
        """Execute validators in parallel using asyncio."""
        try:
            # Try to get the current event loop
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # No event loop running, use sequential validation as fallback
            return super()._perform_validation()

        # Run parallel validation if event loop is available
        return loop.run_until_complete(self._async_validation())

    async def _async_validation(self) -> ValidationResult[dict[str, Any]]:
        """Async validation implementation."""
        semaphore = asyncio.Semaphore(self.max_concurrency)

        async def validate_with_semaphore(
            validator: BaseValidator[Any],
        ) -> tuple[str, ValidationResult[Any]]:
            async with semaphore:
                # Run validation in thread pool since validators are sync
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, validator.validate)
                return validator.get_validator_name(), result

        # Create tasks for all validators
        tasks = [validate_with_semaphore(validator) for validator in self.validators]

        # Execute all tasks
        completed_validations = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results similar to sequential version
        results: dict[str, ValidationResult[Any]] = {}
        all_errors: list[str] = []
        all_warnings: list[str] = []
        all_recommendations: list[str] = []
        combined_metadata: dict[str, Any] = {}

        for validation_result in completed_validations:
            if isinstance(validation_result, Exception):
                error_msg = f"Parallel validation failed: {validation_result}"
                all_errors.append(error_msg)
                continue

            validator_name, result = validation_result
            results[validator_name] = result

            # Collect results same as sequential version
            all_errors.extend(result.errors)
            all_warnings.extend(result.warnings)
            all_recommendations.extend(result.recommendations)
            combined_metadata[validator_name] = result.metadata

        # Determine final status
        is_valid = len(all_errors) == 0 and all(r.is_valid for r in results.values())

        if len(all_errors) > 0:
            final_status = ValidationStatus.ERROR
        elif len(all_warnings) > 0:
            final_status = ValidationStatus.WARNING
        else:
            final_status = ValidationStatus.VALID

        total_validators = len(self.validators)
        valid_count = sum(1 for r in results.values() if r.is_valid)
        message = (
            f"Parallel validation: {valid_count}/{total_validators} validators passed"
        )

        return self._create_result(
            is_valid=is_valid,
            status=final_status,
            message=message,
            data={"individual_results": results},
            errors=all_errors,
            warnings=all_warnings,
            recommendations=all_recommendations,
            **combined_metadata,
        )
