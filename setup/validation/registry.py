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
    "get_registered_validators",
    "create_validator_factory",
]

V = TypeVar("V", bound=BaseValidator[Any])

# Global registry for validator classes
_validator_registry: dict[str, type[BaseValidator[Any]]] = {}

# Global registry for validator factories
_validator_factories: dict[str, Callable[[ValidationContext], BaseValidator[Any]]] = {}


class ValidationRegistry:
    """
    Central registry for validation components.

    Implements the Registry pattern for validator discovery and instantiation.
    Follows SOLID principles:
    - Single Responsibility: Manages validator registration and lookup
    - Open/Closed: Extensible for new validators without modification
    - Dependency Inversion: Uses factory pattern for validator creation
    """

    def __init__(self) -> None:
        """Initialize validation registry."""
        self._local_registry: dict[str, type[BaseValidator[Any]]] = {}
        self._local_factories: dict[
            str, Callable[[ValidationContext], BaseValidator[Any]]
        ] = {}

    def register_validator(
        self,
        name: str,
        validator_class: type[BaseValidator[Any]],
        factory: Callable[[ValidationContext], BaseValidator[Any]] | None = None,
    ) -> None:
        """
        Register a validator class or factory.

        Args:
            name: Unique name for the validator
            validator_class: The validator class to register
            factory: Optional factory function for custom instantiation
        """
        if name in self._local_registry:
            raise ValueError(f"Validator '{name}' is already registered")

        self._local_registry[name] = validator_class

        if factory:
            self._local_factories[name] = factory
        else:
            # Create default factory
            def default_factory(context: ValidationContext) -> BaseValidator[Any]:
                return validator_class(context)

            self._local_factories[name] = default_factory

    def unregister_validator(self, name: str) -> bool:
        """
        Unregister a validator.

        Args:
            name: Name of the validator to unregister

        Returns:
            True if validator was found and removed
        """
        removed = False
        if name in self._local_registry:
            del self._local_registry[name]
            removed = True

        if name in self._local_factories:
            del self._local_factories[name]
            removed = True

        return removed

    def get_validator_class(self, name: str) -> type[BaseValidator[Any]] | None:
        """
        Get a registered validator class by name.

        Args:
            name: Name of the validator

        Returns:
            Validator class or None if not found
        """
        return self._local_registry.get(name)

    def create_validator(
        self, name: str, context: ValidationContext
    ) -> BaseValidator[Any]:
        """
        Create a validator instance using registered factory.

        Args:
            name: Name of the validator to create
            context: Validation context for the validator

        Returns:
            Configured validator instance

        Raises:
            ValueError: If validator is not registered
        """
        if name not in self._local_factories:
            raise ValueError(f"Validator '{name}' is not registered")

        return self._local_factories[name](context)

    def list_validators(self) -> list[str]:
        """
        Get list of all registered validator names.

        Returns:
            List of validator names
        """
        return list(self._local_registry.keys())

    def is_registered(self, name: str) -> bool:
        """
        Check if a validator is registered.

        Args:
            name: Name to check

        Returns:
            True if validator is registered
        """
        return name in self._local_registry

    def clear(self) -> None:
        """Clear all registered validators."""
        self._local_registry.clear()
        self._local_factories.clear()

    def register_from_global(self) -> None:
        """Register all validators from global registry."""
        for name, validator_class in _validator_registry.items():
            if name not in self._local_registry:
                factory = _validator_factories.get(name)
                self.register_validator(name, validator_class, factory)

    def export_to_global(self) -> None:
        """Export local registry to global registry."""
        _validator_registry.update(self._local_registry)
        _validator_factories.update(self._local_factories)


# Global registry instance
_global_registry = ValidationRegistry()


def register_validator(
    name: str,
    validator_class: type[BaseValidator[Any]] | None = None,
    factory: Callable[[ValidationContext], BaseValidator[Any]] | None = None,
) -> Callable[[type[V]], type[V]]:
    """
    Decorator and function to register validators globally.

    Can be used as a decorator or called directly.

    Args:
        name: Unique name for the validator
        validator_class: The validator class (for direct calls)
        factory: Optional factory function

    Returns:
        Decorator function or the validator class
    """

    def decorator(cls: type[V]) -> type[V]:
        """Decorator implementation."""
        _global_registry.register_validator(name, cls, factory)
        return cls

    if validator_class is not None:
        # Direct function call
        _global_registry.register_validator(name, validator_class, factory)
        return lambda x: x  # Return identity function
    else:
        # Decorator usage
        return decorator


def get_registered_validators() -> list[str]:
    """
    Get list of all globally registered validators.

    Returns:
        List of validator names
    """
    return _global_registry.list_validators()


def create_validator_factory(
    validator_class: type[BaseValidator[Any]],
    **default_kwargs: Any,
) -> Callable[[ValidationContext], BaseValidator[Any]]:
    """
    Create a factory function for a validator with default arguments.

    Args:
        validator_class: The validator class
        **default_kwargs: Default keyword arguments for the validator

    Returns:
        Factory function that creates validator instances
    """

    def factory(context: ValidationContext) -> BaseValidator[Any]:
        """Factory function implementation."""
        # Merge context config with default kwargs
        config = {**default_kwargs, **context.config}

        # Create new context with merged config
        factory_context = ValidationContext(
            workspace_root=context.workspace_root,
            environment=context.environment,
            config=config,
            cache_enabled=context.cache_enabled,
            verbose=context.verbose,
        )

        return validator_class(factory_context)

    return factory


def get_global_registry() -> ValidationRegistry:
    """
    Get the global validation registry.

    Returns:
        Global registry instance
    """
    return _global_registry


def create_local_registry() -> ValidationRegistry:
    """
    Create a new local validation registry.

    Returns:
        New registry instance
    """
    registry = ValidationRegistry()
    registry.register_from_global()  # Start with global validators
    return registry


# Auto-discovery support
def discover_validators(module_name: str) -> int:
    """
    Discover and register validators from a module.

    Args:
        module_name: Name of the module to scan

    Returns:
        Number of validators discovered and registered
    """
    import importlib
    import inspect

    try:
        module = importlib.import_module(module_name)
        discovered_count = 0

        for name, obj in inspect.getmembers(module):
            if (
                inspect.isclass(obj)
                and issubclass(obj, BaseValidator)
                and obj is not BaseValidator
                and hasattr(obj, "get_validator_name")
            ):
                # Generate validator name from class name
                validator_name = obj.__name__.lower().replace("validator", "")

                if not _global_registry.is_registered(validator_name):
                    _global_registry.register_validator(validator_name, obj)
                    discovered_count += 1

        return discovered_count

    except ImportError as e:
        raise ValueError(f"Could not import module '{module_name}': {e}")


# Convenience function for bulk registration
def register_validators(
    validators: dict[
        str,
        type[BaseValidator[Any]]
        | tuple[
            type[BaseValidator[Any]], Callable[[ValidationContext], BaseValidator[Any]]
        ],
    ],
) -> None:
    """
    Register multiple validators at once.

    Args:
        validators: Dictionary mapping names to validator classes or (class, factory) tuples
    """
    for name, validator_spec in validators.items():
        if isinstance(validator_spec, tuple):
            validator_class, factory = validator_spec
            _global_registry.register_validator(name, validator_class, factory)
        else:
            _global_registry.register_validator(name, validator_spec)
