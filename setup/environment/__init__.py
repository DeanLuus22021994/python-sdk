"""
Environment Configuration Package
Modern environment configuration aligned with the new validation framework.
"""

from typing import Any

from ..typings import (
    EnvironmentInfo,
    EnvironmentValidationResult,
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
from .path_validator import PathStructureValidator
from .python_validator import PythonEnvironmentValidator
from .structure_validator import ProjectStructureValidator


# Register validators with the global registry
def _register_environment_validators() -> None:
    """Register all environment validators."""
    registry = ValidationRegistry()

    registry.register_validator(
        "python_environment",
        PythonEnvironmentValidator,
    )

    registry.register_validator(
        "project_structure",
        ProjectStructureValidator,
    )

    registry.register_validator(
        "path_structure",
        PathStructureValidator,
    )


# Auto-register on import
_register_environment_validators()

__all__ = [
    # Core manager
    "EnvironmentManager",
    # Validators
    "PythonEnvironmentValidator",
    "ProjectStructureValidator",
    "PathStructureValidator",
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
    "EnvironmentValidationResult",
    "ValidationStatus",
    "SetupMode",
    "LogLevel",
]
