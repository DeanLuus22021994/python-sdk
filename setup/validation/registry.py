"""
Validation Registry
Central registry for validator discovery and management.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

from .base import BaseValidator, ValidationContext

__all__ = [
    "ValidationRegistry",
    "register_validator",
    "get_global_registry",
]

V = TypeVar("V", bound=BaseValidator[Any])

# Global registry for validator classes
_validator_registry: dict[str, type[BaseValidator[Any]]] = {}


class ValidationRegistry:
    """Central registry for validation components."""

    def __init__(self) -> None:
        self._validators: dict[str, type[BaseValidator[Any]]] = {}
        self._factories: dict[
            str, Callable[[ValidationContext], BaseValidator[Any]]
        ] = {}

    def register_validator(
        self,
        name: str,
        validator_class: type[BaseValidator[Any]],
        factory: Callable[[ValidationContext], BaseValidator[Any]] | None = None,
    ) -> None:
        """Register a validator class."""
        self._validators[name] = validator_class
        if factory:
            self._factories[name] = factory
        else:
            self._factories[name] = lambda ctx: validator_class(ctx)

    def create_validator(
        self, name: str, context: ValidationContext
    ) -> BaseValidator[Any]:
        """Create a validator instance."""
        if name not in self._factories:
            raise ValueError(f"Unknown validator: {name}")
        return self._factories[name](context)

    def get_validator(
        self, name: str, context: ValidationContext
    ) -> BaseValidator[Any] | None:
        """Get a validator instance, returning None if not found."""
        try:
            return self.create_validator(name, context)
        except ValueError:
            return None

    def list_validators(self) -> list[str]:
        """List registered validator names."""
        return list(self._validators.keys())


# Global registry instance
_global_registry = ValidationRegistry()


def register_validator(name: str) -> Callable[[type[V]], type[V]]:
    """Decorator to register a validator class."""

    def decorator(validator_class: type[V]) -> type[V]:
        _global_registry.register_validator(name, validator_class)
        return validator_class

    return decorator


def get_global_registry() -> ValidationRegistry:
    """Get the global validation registry."""
    return _global_registry
