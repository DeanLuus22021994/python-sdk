"""
MCP Python SDK Setup Package

Modern, modular setup system for the MCP Python SDK with support for:
- Host-based development environment
- Docker containerization
- Performance optimization
- Clean architecture following SOLID principles
"""

from typing import Final

__version__: Final[str] = "2.0.0"
__author__: Final[str] = "MCP Python SDK Team"

# Core setup modules
from .environment import EnvironmentManager
from .sequence import ModernSetupOrchestrator

# Host setup capabilities
try:
    from .host import HostSetupManager
except ImportError:
    HostSetupManager = None  # type: ignore[misc,assignment]

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
