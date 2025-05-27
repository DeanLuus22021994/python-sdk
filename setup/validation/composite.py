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

    Implements the Composite pattern to treat groups of validators
    as a single validator interface.
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
            validators: List of validators to compose
            fail_fast: Stop on first validation failure
        """
        super().__init__(context)
        self.validators = list(validators)
        self.fail_fast = fail_fast
        self._validator_results: dict[str, ValidationResult[Any]] = {}

    def get_validator_name(self) -> str:
        """Get composite validator name."""
        validator_names = [v.get_validator_name() for v in self.validators]
        return f"Composite({', '.join(validator_names)})"

    def _perform_validation(self) -> ValidationResult[dict[str, Any]]:
        """Perform validation on all composed validators."""
        if not self.validators:
            return self._create_result(
                is_valid=True,
                status=ValidationStatus.VALID,
                message="No validators to execute",
                data={},
            )

        # Run all validators
        all_errors = []
        all_warnings = []
        all_recommendations = []
        all_valid = True

        validator_data = {}

        for validator in self.validators:
            try:
                result = validator.validate()
                validator_name = validator.get_validator_name()

                # Store individual result
                self._validator_results[validator_name] = result

                # Collect data
                if result.data is not None:
                    validator_data[validator_name] = result.data

                # Collect issues
                if not result.is_valid:
                    all_valid = False
                    all_errors.extend(result.errors)

                    if self.fail_fast:
                        break

                all_warnings.extend(result.warnings)
                all_recommendations.extend(result.recommendations)

            except Exception as e:
                error_msg = f"Validator {validator.get_validator_name()} failed: {e}"
                all_errors.append(error_msg)
                all_valid = False

                if self.fail_fast:
                    break

        # Determine overall status
        if all_errors:
            status = ValidationStatus.ERROR
        elif all_warnings:
            status = ValidationStatus.WARNING
        else:
            status = ValidationStatus.VALID

        message = self._create_summary_message(
            all_valid, len(all_errors), len(all_warnings)
        )

        return self._create_result(
            is_valid=all_valid,
            status=status,
            message=message,
            data=validator_data,
            errors=all_errors,
            warnings=all_warnings,
            recommendations=all_recommendations,
            validators_executed=len(self.validators),
            successful_validators=sum(
                1 for r in self._validator_results.values() if r.is_valid
            ),
        )

    def get_validator_results(self) -> dict[str, ValidationResult[Any]]:
        """Get results from individual validators."""
        return self._validator_results.copy()

    def get_validator_result(self, validator_name: str) -> ValidationResult[Any] | None:
        """Get result from a specific validator."""
        return self._validator_results.get(validator_name)

    def _create_summary_message(
        self, all_valid: bool, error_count: int, warning_count: int
    ) -> str:
        """Create summary message for validation results."""
        if all_valid and error_count == 0:
            if warning_count > 0:
                return f"Validation passed with {warning_count} warnings"
            else:
                return "All validations passed successfully"
        else:
            return f"Validation failed with {error_count} errors and {warning_count} warnings"


class SequentialCompositeValidator(CompositeValidator):
    """
    Sequential composite validator that runs validators one after another.

    Useful when validators have dependencies or when resources are limited.
    """

    def get_validator_name(self) -> str:
        """Get sequential composite validator name."""
        return f"Sequential{super().get_validator_name()}"

    def _perform_validation(self) -> ValidationResult[dict[str, Any]]:
        """Run validators sequentially (default behavior)."""
        return super()._perform_validation()


class ParallelCompositeValidator(CompositeValidator):
    """
    Parallel composite validator that runs validators concurrently.

    Improves performance when validators are independent.
    """

    def __init__(
        self,
        context: ValidationContext,
        validators: Sequence[BaseValidator[Any]],
        max_concurrency: int = 4,
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
        """Run validators in parallel using asyncio."""
        try:
            # Try to use existing event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is running, we need to run in a new thread
                import concurrent.futures

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run, self._run_parallel_validation()
                    )
                    return future.result()
            else:
                return loop.run_until_complete(self._run_parallel_validation())
        except Exception:
            # Fallback to sequential validation
            return super()._perform_validation()

    async def _run_parallel_validation(self) -> ValidationResult[dict[str, Any]]:
        """Run validators in parallel asynchronously."""
        if not self.validators:
            return self._create_result(
                is_valid=True,
                status=ValidationStatus.VALID,
                message="No validators to execute",
                data={},
            )

        # Create semaphore to limit concurrency
        semaphore = asyncio.Semaphore(self.max_concurrency)

        async def run_validator(
            validator: BaseValidator[Any],
        ) -> tuple[str, ValidationResult[Any]]:
            """Run a single validator with semaphore."""
            async with semaphore:
                # Run validator in thread pool since validate() is synchronous
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, validator.validate)
                return validator.get_validator_name(), result

        # Create tasks for all validators
        tasks = [run_validator(validator) for validator in self.validators]

        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        all_errors = []
        all_warnings = []
        all_recommendations = []
        all_valid = True
        validator_data = {}

        for result in results:
            if isinstance(result, Exception):
                all_errors.append(f"Validator execution failed: {result}")
                all_valid = False
                continue

            validator_name, validation_result = result
            self._validator_results[validator_name] = validation_result

            # Collect data
            if validation_result.data is not None:
                validator_data[validator_name] = validation_result.data

            # Collect issues
            if not validation_result.is_valid:
                all_valid = False

            all_errors.extend(validation_result.errors)
            all_warnings.extend(validation_result.warnings)
            all_recommendations.extend(validation_result.recommendations)

        # Determine overall status
        if all_errors:
            status = ValidationStatus.ERROR
        elif all_warnings:
            status = ValidationStatus.WARNING
        else:
            status = ValidationStatus.VALID

        message = self._create_summary_message(
            all_valid, len(all_errors), len(all_warnings)
        )

        return self._create_result(
            is_valid=all_valid,
            status=status,
            message=message,
            data=validator_data,
            errors=all_errors,
            warnings=all_warnings,
            recommendations=all_recommendations,
            validators_executed=len(self.validators),
            successful_validators=sum(
                1 for r in self._validator_results.values() if r.is_valid
            ),
            execution_mode="parallel",
            max_concurrency=self.max_concurrency,
        )
