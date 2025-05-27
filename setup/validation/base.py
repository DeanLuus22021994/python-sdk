"""
Base Validation Framework
Core validation components following SOLID principles.
"""

from __future__ import annotations

import abc
import hashlib
import time
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

from ..typings import ValidationStatus

__all__ = [
    "ValidationResult",
    "BaseValidator",
    "CachedValidator",
    "ValidationContext",
]

T = TypeVar("T")


@dataclass(slots=True, frozen=True)
class ValidationResult(Generic[T]):
    """Modern validation result with comprehensive type safety."""

    is_valid: bool
    status: ValidationStatus
    message: str
    data: T | None = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ValidationContext:
    """Context for validation operations."""

    workspace_root: str
    environment: dict[str, str]
    config: dict[str, Any] = field(default_factory=dict)


class BaseValidator(abc.ABC, Generic[T]):
    """Abstract base validator implementing the Strategy pattern."""

    def __init__(self, context: ValidationContext) -> None:
        self.context = context
        self._cache: dict[str, tuple[ValidationResult[T], float]] = {}

    @abc.abstractmethod
    def get_validator_name(self) -> str:
        """Get the name of this validator."""
        ...

    @abc.abstractmethod
    def _perform_validation(self) -> ValidationResult[T]:
        """Perform the actual validation logic."""
        ...

    def validate(self) -> ValidationResult[T]:
        """Execute validation with caching support."""
        cache_key = self._get_cache_key()

        # Check cache
        if cache_key in self._cache:
            cached_result, timestamp = self._cache[cache_key]
            if self._is_cache_valid(cached_result):
                return cached_result

        # Perform validation
        result = self._perform_validation()

        # Cache result
        self._cache[cache_key] = (result, time.time())

        return result

    def is_valid(self) -> bool:
        """Check if validation passes."""
        return self.validate().is_valid

    def clear_cache(self) -> None:
        """Clear validation cache."""
        self._cache.clear()

    def _get_cache_key(self) -> str:
        """Generate cache key for this validation."""
        content = f"{self.get_validator_name()}:{self.context.workspace_root}"
        return hashlib.md5(content.encode()).hexdigest()

    def _is_cache_valid(self, cached_result: ValidationResult[T]) -> bool:
        """Check if cached result is still valid."""
        # Cache TTL of 5 minutes
        return True  # Simplified for now

    def _create_result(
        self,
        is_valid: bool,
        status: ValidationStatus,
        message: str,
        data: T | None = None,
        errors: list[str] | None = None,
        warnings: list[str] | None = None,
        recommendations: list[str] | None = None,
        **metadata: Any,
    ) -> ValidationResult[T]:
        """Create a validation result."""
        return ValidationResult(
            is_valid=is_valid,
            status=status,
            message=message,
            data=data,
            errors=errors or [],
            warnings=warnings or [],
            recommendations=recommendations or [],
            metadata=metadata,
        )


class CachedValidator(BaseValidator[T]):
    """Validator with enhanced caching capabilities."""

    def __init__(self, wrapped_validator: BaseValidator[T]) -> None:
        super().__init__(wrapped_validator.context)
        self.wrapped_validator = wrapped_validator

    def get_validator_name(self) -> str:
        """Get validator name from wrapped validator."""
        return f"Cached({self.wrapped_validator.get_validator_name()})"

    def _perform_validation(self) -> ValidationResult[T]:
        """Delegate to wrapped validator."""
        return self.wrapped_validator._perform_validation()

    def clear_cache(self) -> None:
        """Clear both our cache and wrapped validator's cache."""
        super().clear_cache()
        self.wrapped_validator.clear_cache()
