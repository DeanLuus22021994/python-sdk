"""
Validation Decorators
Function and class decorators for validation enhancement.
"""

from __future__ import annotations

import functools
import hashlib
import time
from collections.abc import Callable
from typing import Any, TypeVar, cast

from .base import BaseValidator, ValidationResult

__all__ = [
    "cache_validation",
    "idempotent_validation",
    "timed_validation",
    "retry_validation",
]

F = TypeVar("F", bound=Callable[..., Any])
V = TypeVar("V", bound=BaseValidator[Any])

# Global cache for validation results
_validation_cache: dict[str, tuple[ValidationResult[Any], float]] = {}


def cache_validation(
    ttl_seconds: int = 300,
    cache_key_func: Callable[..., str] | None = None,
) -> Callable[[F], F]:
    """
    Decorator to cache validation results.

    Implements caching pattern for expensive validation operations.
    Follows the Single Responsibility Principle by providing only caching behavior.

    Args:
        ttl_seconds: Time-to-live for cache entries in seconds
        cache_key_func: Optional function to generate cache keys

    Returns:
        Decorated function with caching behavior
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Generate cache key
            if cache_key_func:
                cache_key = cache_key_func(*args, **kwargs)
            else:
                cache_key = _generate_default_cache_key(func.__name__, args, kwargs)

            # Check cache
            current_time = time.time()
            if cache_key in _validation_cache:
                cached_result, cache_time = _validation_cache[cache_key]
                if current_time - cache_time < ttl_seconds:
                    return cached_result

            # Execute function and cache result
            result = func(*args, **kwargs)
            _validation_cache[cache_key] = (result, current_time)

            return result

        # Add cache management methods
        wrapper.clear_cache = lambda: _validation_cache.clear()  # type: ignore
        wrapper.cache_info = lambda: {  # type: ignore
            "cache_size": len(_validation_cache),
            "ttl_seconds": ttl_seconds,
        }

        return cast(F, wrapper)

    return decorator


def idempotent_validation(func: F) -> F:
    """
    Decorator to ensure validation functions are idempotent.

    Implements idempotency pattern to ensure consistent results
    regardless of how many times the validation is executed.

    Args:
        func: Function to make idempotent

    Returns:
        Decorated function with idempotency guarantees
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Generate a deterministic key based on function and arguments
        cache_key = _generate_idempotent_key(func.__name__, args, kwargs)

        # Use a simple cache with no TTL for idempotency
        if not hasattr(wrapper, "_idempotent_cache"):
            wrapper._idempotent_cache = {}  # type: ignore

        if cache_key in wrapper._idempotent_cache:  # type: ignore
            return wrapper._idempotent_cache[cache_key]  # type: ignore

        # Execute function and store result
        result = func(*args, **kwargs)
        wrapper._idempotent_cache[cache_key] = result  # type: ignore

        return result

    # Add method to clear idempotent cache
    wrapper.clear_idempotent_cache = lambda: setattr(  # type: ignore
        wrapper, "_idempotent_cache", {}
    )

    return cast(F, wrapper)


def timed_validation(func: F) -> F:
    """
    Decorator to add timing information to validation functions.

    Provides performance monitoring capabilities for validation operations.

    Args:
        func: Function to add timing to

    Returns:
        Decorated function with timing information
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.perf_counter()

        try:
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            execution_time = end_time - start_time

            # If result is a ValidationResult, add timing metadata
            if isinstance(result, ValidationResult):
                # Create new result with timing metadata
                new_metadata = result.metadata.copy()
                new_metadata.update(
                    {
                        "execution_time_seconds": execution_time,
                        "start_time": start_time,
                        "end_time": end_time,
                    }
                )

                # Create new ValidationResult with updated metadata
                return ValidationResult(
                    is_valid=result.is_valid,
                    status=result.status,
                    message=result.message,
                    data=result.data,
                    errors=result.errors,
                    warnings=result.warnings,
                    recommendations=result.recommendations,
                    metadata=new_metadata,
                    validation_time=result.validation_time,
                )

            return result

        except Exception as e:
            end_time = time.perf_counter()
            execution_time = end_time - start_time

            # Add timing info to exception
            if hasattr(e, "execution_time"):
                e.execution_time = execution_time  # type: ignore

            raise

    return cast(F, wrapper)


def retry_validation(
    max_retries: int = 3,
    delay_seconds: float = 1.0,
    exponential_backoff: bool = True,
) -> Callable[[F], F]:
    """
    Decorator to add retry logic to validation functions.

    Implements retry pattern for validations that might fail due to
    temporary conditions (e.g., network issues, resource locks).

    Args:
        max_retries: Maximum number of retry attempts
        delay_seconds: Initial delay between retries
        exponential_backoff: Whether to use exponential backoff

    Returns:
        Decorated function with retry behavior
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None
            current_delay = delay_seconds

            for attempt in range(max_retries + 1):
                try:
                    result = func(*args, **kwargs)

                    # If this is a ValidationResult and it's not valid,
                    # decide whether to retry based on error type
                    if isinstance(result, ValidationResult) and not result.is_valid:
                        # Only retry if errors suggest a temporary issue
                        if attempt < max_retries and _should_retry_validation(result):
                            if attempt > 0:  # Don't delay on first attempt
                                time.sleep(current_delay)
                                if exponential_backoff:
                                    current_delay *= 2
                            continue

                    return result

                except Exception as e:
                    last_exception = e

                    if attempt < max_retries:
                        if attempt > 0:  # Don't delay on first attempt
                            time.sleep(current_delay)
                            if exponential_backoff:
                                current_delay *= 2
                        continue
                    else:
                        # Max retries exceeded, raise the last exception
                        raise

            # This should not be reached, but handle it gracefully
            if last_exception:
                raise last_exception
            else:
                raise RuntimeError("Validation retry failed for unknown reason")

        # Add retry configuration info
        wrapper.retry_config = {  # type: ignore
            "max_retries": max_retries,
            "delay_seconds": delay_seconds,
            "exponential_backoff": exponential_backoff,
        }

        return cast(F, wrapper)

    return decorator


def _generate_default_cache_key(
    func_name: str, args: tuple[Any, ...], kwargs: dict[str, Any]
) -> str:
    """Generate a default cache key from function name and arguments."""
    # Create a deterministic string representation
    key_parts = [func_name]

    # Add args (skip 'self' for methods)
    for i, arg in enumerate(args):
        if i == 0 and hasattr(arg, "__class__"):
            # Likely 'self', use class name instead of instance
            key_parts.append(f"arg{i}:{arg.__class__.__name__}")
        else:
            key_parts.append(f"arg{i}:{repr(arg)}")

    # Add sorted kwargs
    for key, value in sorted(kwargs.items()):
        key_parts.append(f"{key}:{repr(value)}")

    # Hash the combined key to avoid very long cache keys
    key_string = "|".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()


def _generate_idempotent_key(
    func_name: str, args: tuple[Any, ...], kwargs: dict[str, Any]
) -> str:
    """Generate an idempotent key that's deterministic across runs."""
    return _generate_default_cache_key(func_name, args, kwargs)


def _should_retry_validation(result: ValidationResult[Any]) -> bool:
    """Determine if a validation failure should trigger a retry."""
    # Look for error messages that suggest temporary issues
    temporary_error_indicators = [
        "timeout",
        "connection",
        "network",
        "temporary",
        "busy",
        "locked",
        "unavailable",
    ]

    for error in result.errors:
        error_lower = error.lower()
        if any(indicator in error_lower for indicator in temporary_error_indicators):
            return True

    return False
