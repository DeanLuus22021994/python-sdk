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
                result, timestamp = _validation_cache[cache_key]
                if current_time - timestamp < ttl_seconds:
                    return result

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

        # Execute and cache result
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
        start_time = time.time()
        try:
            result = func(*args, **kwargs)

            # If result has metadata, add timing info
            if hasattr(result, "metadata") and isinstance(result.metadata, dict):
                result.metadata["execution_time"] = time.time() - start_time

            return result
        finally:
            execution_time = time.time() - start_time
            # Store timing in function attribute for debugging
            if not hasattr(wrapper, "_timing_history"):
                wrapper._timing_history = []  # type: ignore
            wrapper._timing_history.append(execution_time)  # type: ignore

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

                    # If result is a ValidationResult, check if we should retry
                    if hasattr(result, "is_valid") and hasattr(result, "errors"):
                        if result.is_valid or not _should_retry_validation(result):
                            return result

                        # Should retry, but this was the last attempt
                        if attempt == max_retries:
                            return result
                    else:
                        return result

                except Exception as e:
                    last_exception = e
                    if attempt == max_retries:
                        raise

                # Wait before retry
                if attempt < max_retries:
                    time.sleep(current_delay)
                    if exponential_backoff:
                        current_delay *= 2

            # Should not reach here, but just in case
            if last_exception:
                raise last_exception
            return func(*args, **kwargs)

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
            # Skip 'self' parameter for methods
            key_parts.append(arg.__class__.__name__)
        else:
            key_parts.append(repr(arg))

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
