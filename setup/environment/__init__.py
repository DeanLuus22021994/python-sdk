"""
Environment Configuration Package
Modern environment configuration aligned with the new validation framework.
"""

from typing import Any

from ..typings import (
    EnvironmentInfo,
    LogLevel,
    PackageManagerInfo,
    ProjectStructureInfo,
    PythonVersion,
    SetupMode,
    ValidationStatus,
)
from ..validation import ValidationRegistry, register_validator
from .constants import (
    DEFAULT_PERFORMANCE_SETTINGS,
    MAX_TESTED_PYTHON_VERSION,
    MIN_PYTHON_VERSION,
    OPTIONAL_PROJECT_PATHS,
    RECOMMENDED_PYTHON_VERSION,
    REQUIRED_PROJECT_PATHS,
)
from .manager import EnvironmentManager


# Register validators with the global registry
def _register_environment_validators() -> None:
    """Register all environment validators."""
    # Import validators from the main validators module
    from .. import validators

    # The validators auto-register themselves via decorators
    _ = validators  # Force import to trigger registration


# Auto-register on import
_register_environment_validators()

__all__ = [
    # Core manager
    "EnvironmentManager",
    # Constants
    "MIN_PYTHON_VERSION",
    "RECOMMENDED_PYTHON_VERSION",
    "MAX_TESTED_PYTHON_VERSION",
    "REQUIRED_PROJECT_PATHS",
    "OPTIONAL_PROJECT_PATHS",
    "DEFAULT_PERFORMANCE_SETTINGS",
    # Type exports
    "EnvironmentInfo",
    "PackageManagerInfo",
    "ProjectStructureInfo",
    "PythonVersion",
    "ValidationStatus",
    "SetupMode",
    "LogLevel",
]
