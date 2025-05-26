"""
Modular type definitions for the MCP Python SDK setup system.

This package provides a well-organized, modular type system to replace the
monolithic types.py file with better separation of concerns and improved
maintainability.

Modules:
    core: Core type aliases and fundamental types
    enums: Enumeration types for setup modes, log levels, etc.
    config: Configuration data classes
    environment: Environment and validation data classes
    tools: VS Code and Docker configuration classes
    protocols: Protocol definitions for type checking
"""

# Re-export all types from submodules for easy importing
from .config import ContainerConfig, PerformanceSettings
from .core import (
    EnvironmentDict,
    EnvironmentValidationResult,
    JsonValue,
    LoggingCallback,
    PackageManagerDict,
    PathLike,
    ProjectValidationResult,
    SetupProgressCallback,
    SetupResult,
    ValidationResult,
    VSCodeSettingsDict,
)
from .enums import LogLevel, SetupMode, ValidationStatus
from .environment import (
    EnvironmentInfo,
    ProjectStructureInfo,
    PythonVersion,
    ValidationDetails,
)
from .protocols import (
    ConfigManager,
    EnvironmentProvider,
    ProjectStructureValidator,
    SetupManager,
    Validator,
)
from .tools import DockerConfig, DockerInfo, VSCodeConfig, VSCodeExtension

__version__ = "1.0.0"
__all__ = [
    # From core
    "PathLike",
    "JsonValue",
    "ValidationResult",
    "SetupResult",
    "EnvironmentValidationResult",
    "ProjectValidationResult",
    "SetupProgressCallback",
    "LoggingCallback",
    "VSCodeSettingsDict",
    "PackageManagerDict",
    "EnvironmentDict",
    # From enums
    "SetupMode",
    "LogLevel",
    "ValidationStatus",
    # From config
    "PerformanceSettings",
    "ContainerConfig",
    # From environment
    "PythonVersion",
    "EnvironmentInfo",
    "ValidationDetails",
    "ProjectStructureInfo",
    # From tools
    "VSCodeConfig",
    "DockerConfig",
    # From protocols
    "Validator",
    "SetupManager",
    "ConfigManager",
    "EnvironmentProvider",
    "ProjectStructureValidator",
]
