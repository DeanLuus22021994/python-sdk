"""
MCP Python SDK Setup Package

Modern, modular setup system for the MCP Python SDK with support for:
- Host-based development environment
- Docker containerization
- Performance optimization
- Clean architecture following SOLID principles
"""

from __future__ import annotations

import sys
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Final, Optional, Type

# Add parent directory to path for absolute imports if needed
_setup_path = Path(__file__).parent
if str(_setup_path.parent) not in sys.path:
    sys.path.insert(0, str(_setup_path.parent))

# Core setup modules - always import these first
try:
    from .environment import EnvironmentManager
except ImportError:
    EnvironmentManager = None

# Version and metadata
__version__: Final[str] = "2.0.0"
__author__: Final[str] = "MCP Python SDK Team"

# Type definitions for optional imports
_ModernSetupOrchestrator: type[Any] | None = None
_HostSetupManager: type[Any] | None = None
_DockerSetupManager: type[Any] | None = None
_setup_packages: Callable[[], bool] | None = None


def _load_orchestrator() -> type[Any] | None:
    """Load orchestrator with graceful fallback."""
    try:
        from .orchestrator import ModernSetupOrchestrator

        return ModernSetupOrchestrator
    except ImportError:
        return None


def _load_host_setup() -> tuple[type[Any] | None, Callable[[], bool] | None]:
    """Load host setup components with graceful fallback."""
    try:
        from .host import HostSetupManager
        from .host.package_manager import setup_packages

        return HostSetupManager, setup_packages
    except ImportError:
        return None, None


def _load_docker_setup() -> type[Any] | None:
    """Load Docker setup components with graceful fallback."""
    try:
        from .docker import DockerSetupManager

        return DockerSetupManager
    except ImportError:
        return None


def _load_typings() -> dict[str, type[Any] | None]:
    """Load typing definitions with graceful fallback."""
    typings: dict[str, type[Any] | None] = {}

    try:
        # Import all type definitions
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

        # Cast each imported type to Type[Any] to match the function's return type
        typings.update(
            {
                "ContainerConfig": ContainerConfig,
                "DockerInfo": DockerInfo,
                "EnvironmentInfo": EnvironmentInfo,
                "LogLevel": LogLevel,
                "PackageManagerInfo": PackageManagerInfo,
                "PerformanceSettings": PerformanceSettings,
                "ProjectStructureInfo": ProjectStructureInfo,
                "PythonVersion": PythonVersion,
                "SetupMode": SetupMode,
                "ValidationDetails": ValidationDetails,
                "ValidationStatus": ValidationStatus,
                "VSCodeConfig": VSCodeConfig,
            }
        )
    except ImportError:
        # Graceful fallback with None values
        for key in [
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
        ]:
            typings[key] = None

    return typings


# Load all optional components
_ModernSetupOrchestrator = _load_orchestrator()
_HostSetupManager, _setup_packages = _load_host_setup()
_DockerSetupManager = _load_docker_setup()
_typings = _load_typings()

# Create public interface - avoid redefinition by using different names
ModernSetupOrchestrator = _ModernSetupOrchestrator
HostSetupManager = _HostSetupManager
DockerSetupManager = _DockerSetupManager
setup_packages = _setup_packages

# Export typings
ContainerConfig = _typings["ContainerConfig"]
DockerInfo = _typings["DockerInfo"]
EnvironmentInfo = _typings["EnvironmentInfo"]
LogLevel = _typings["LogLevel"]
PackageManagerInfo = _typings["PackageManagerInfo"]
PerformanceSettings = _typings["PerformanceSettings"]
ProjectStructureInfo = _typings["ProjectStructureInfo"]
PythonVersion = _typings["PythonVersion"]
SetupMode = _typings["SetupMode"]
ValidationDetails = _typings["ValidationDetails"]
# TYPE_CHECKING imports for better IDE support
if TYPE_CHECKING:
    # Re-import for type checking to ensure proper type hints
    try:
        # Using conditional imports to handle potential missing modules
        try:
            from .orchestrator import ModernSetupOrchestrator as _TypedOrchestrator

            ModernSetupOrchestrator = _TypedOrchestrator
        except ImportError:
            pass

        try:
            from .typings import ContainerConfig as _TypedContainerConfig
            from .typings import DockerInfo as _TypedDockerInfo
            from .typings import EnvironmentInfo as _TypedEnvironmentInfo
            from .typings import LogLevel as _TypedLogLevel
            from .typings import PackageManagerInfo as _TypedPackageManagerInfo
            from .typings import PerformanceSettings as _TypedPerformanceSettings
            from .typings import ProjectStructureInfo as _TypedProjectStructureInfo
            from .typings import PythonVersion as _TypedPythonVersion
            from .typings import SetupMode as _TypedSetupMode
            from .typings import ValidationDetails as _TypedValidationDetails
            from .typings import ValidationStatus as _TypedValidationStatus
            from .typings import VSCodeConfig as _TypedVSCodeConfig

            ContainerConfig = _TypedContainerConfig
            DockerInfo = _TypedDockerInfo
            EnvironmentInfo = _TypedEnvironmentInfo
            LogLevel = _TypedLogLevel
            PackageManagerInfo = _TypedPackageManagerInfo
            PerformanceSettings = _TypedPerformanceSettings
            ProjectStructureInfo = _TypedProjectStructureInfo
            PythonVersion = _TypedPythonVersion
            SetupMode = _TypedSetupMode
            ValidationDetails = _TypedValidationDetails
            ValidationStatus = _TypedValidationStatus
            VSCodeConfig = _TypedVSCodeConfig
        except ImportError:
            pass
    except Exception:
        pass
