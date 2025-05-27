"""
MCP Python SDK Setup Package

Modern, modular setup system for the MCP Python SDK with support for:
- Host-based development environment
- Docker containerization
- Performance optimization
- Clean architecture following SOLID principles
"""

from typing import Any, Final, Type

__version__: Final[str] = "2.0.0"
__author__: Final[str] = "MCP Python SDK Team"

# Core setup modules
from .environment import EnvironmentManager

# Import orchestrator with proper error handling
try:
    from .orchestrator import ModernSetupOrchestrator
except ImportError:
    # Fallback if orchestrator module is not available
    ModernSetupOrchestrator = None  # type: ignore[misc,assignment]

# Host setup capabilities
try:
    from .host.package_manager import setup_packages

    # Proper type annotation for HostSetupManager
    HostSetupManager: type[Any] | None = (
        None  # Placeholder until host module is implemented
    )
except ImportError:
    setup_packages = None  # type: ignore[misc,assignment]
    HostSetupManager: type[Any] | None = None  # type: ignore[misc,assignment]

# Docker setup capabilities
try:
    from .docker import DockerSetupManager
except ImportError:
    DockerSetupManager = None  # type: ignore[misc,assignment]

# Type exports for better IDE support
from .typings import (
    ContainerConfig,
    DockerInfo,
    EnvironmentInfo,
    LogLevel,
    PackageManagerInfo,
    PerformanceSettings,
    ProjectStructureInfo,
    PythonVersion,
    SetupMode,
    ValidationDetails,
    ValidationStatus,
    VSCodeConfig,
)

__all__ = [
    "__version__",
    "__author__",
    # Core managers
    "EnvironmentManager",
    "ModernSetupOrchestrator",
    "HostSetupManager",
    "DockerSetupManager",
    # Utilities
    "setup_packages",
    # Type exports
    "ContainerConfig",
    "DockerInfo",
    "EnvironmentInfo",
    "LogLevel",
    "PackageManagerInfo",
    "PerformanceSettings",
    "ProjectStructureInfo",
    "PythonVersion",
    "SetupMode",
    "ValidationDetails",
    "ValidationStatus",
    "VSCodeConfig",
]
