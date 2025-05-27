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
    """
    Modern validation result with comprehensive type safety.

    Follows the Single Responsibility Principle by focusing solely on
    result representation and provides immutable, structured validation outcomes.
    """

    is_valid: bool
    status: ValidationStatus
    message: str
    data: T | None = None
    errors: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)
    recommendations: tuple[str, ...] = field(default_factory=tuple)
    metadata: dict[str, Any] = field(default_factory=dict)
    validation_time: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        """Ensure result consistency."""
        # Validate status consistency
        if self.is_valid and self.status == ValidationStatus.ERROR:
            object.__setattr__(self, "is_valid", False)
        elif not self.is_valid and self.status == ValidationStatus.VALID:
            object.__setattr__(self, "status", ValidationStatus.ERROR)

    @property
    def has_issues(self) -> bool:
        """Check if validation has any issues."""
        return len(self.errors) > 0 or len(self.warnings) > 0

    @property
    def severity_score(self) -> int:
        """Calculate severity score for result comparison."""
        return len(self.errors) * 3 + len(self.warnings)


@dataclass(slots=True)
class ValidationContext:
    """
    Validation execution context for dependency injection and configuration.

    Supports the Dependency Inversion Principle by providing a context
    that validators can depend on for their requirements.
    """

    workspace_root: str
    environment: dict[str, str] = field(default_factory=dict)
    config: dict[str, Any] = field(default_factory=dict)
    cache_enabled: bool = True
    verbose: bool = False

    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get configuration value with fallback."""
        return self.config.get(key, default)

    def has_environment_var(self, var_name: str) -> bool:
        """Check if environment variable exists."""
        return var_name in self.environment


class BaseValidator(abc.ABC, Generic[T]):
    """
    Abstract base validator implementing the Strategy pattern.

    Follows SOLID principles:
    - Single Responsibility: Each validator handles one validation concern
    - Open/Closed: Extensible through inheritance, closed for modification
    - Liskov Substitution: All validators are interchangeable
    - Interface Segregation: Minimal, focused interface
    - Dependency Inversion: Depends on abstractions (ValidationContext)
    """

    def __init__(self, context: ValidationContext) -> None:
        """Initialize validator with context."""
        self.context = context
        self._cache: dict[str, ValidationResult[T]] = {}

    @abc.abstractmethod
    def get_validator_name(self) -> str:
        """Get human-readable validator name."""
        ...

    @abc.abstractmethod
    def _perform_validation(self) -> ValidationResult[T]:
        """Perform the actual validation logic."""
        ...

    def validate(self) -> ValidationResult[T]:
        """
        Execute validation with caching support.

        Returns:
            ValidationResult with comprehensive validation details
        """
        # Check cache if enabled
        if self.context.cache_enabled:
            cache_key = self._get_cache_key()
            if cache_key in self._cache:
                cached_result = self._cache[cache_key]
                if self._is_cache_valid(cached_result):
                    return cached_result

        # Perform validation
        result = self._perform_validation()

        # Cache result if enabled
        if self.context.cache_enabled:
            cache_key = self._get_cache_key()
            self._cache[cache_key] = result

        return result

    def is_valid(self) -> bool:
        """Quick validation check without detailed results."""
        result = self.validate()
        return result.is_valid

    def clear_cache(self) -> None:
        """Clear validation cache for re-execution."""
        self._cache.clear()

    def _get_cache_key(self) -> str:
        """Generate cache key for this validation context."""
        context_str = f"{self.context.workspace_root}:{str(self.context.config)}"
        return hashlib.sha256(context_str.encode()).hexdigest()[:16]

    def _is_cache_valid(self, cached_result: ValidationResult[T]) -> bool:
        """Check if cached result is still valid."""
        # Simple time-based cache invalidation (5 minutes)
        cache_age = time.time() - cached_result.validation_time
        return cache_age < 300

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
        """Helper method to create standardized validation results."""
        return ValidationResult(
            is_valid=is_valid,
            status=status,
            message=message,
            data=data,
            errors=tuple(errors or []),
            warnings=tuple(warnings or []),
            recommendations=tuple(recommendations or []),
            metadata=metadata,
            validation_time=time.time(),
        )


class CachedValidator(BaseValidator[T]):
    """
    Validator with enhanced caching capabilities.

    Implements the Decorator pattern for adding caching behavior
    to any validator implementation.
    """

    def __init__(self, wrapped_validator: BaseValidator[T]) -> None:
        """Initialize with wrapped validator."""
        super().__init__(wrapped_validator.context)
        self._wrapped = wrapped_validator

    def get_validator_name(self) -> str:
        """Get validator name from wrapped validator."""
        return f"Cached({self._wrapped.get_validator_name()})"

    def _perform_validation(self) -> ValidationResult[T]:
        """Delegate to wrapped validator."""
        return self._wrapped._perform_validation()

    def clear_cache(self) -> None:
        """Clear both local and wrapped validator caches."""
        super().clear_cache()
        self._wrapped.clear_cache()


# Forward declaration for registry to avoid circular imports
class ValidationRegistry:
    """Forward declaration - implementation in registry.py"""

    pass
