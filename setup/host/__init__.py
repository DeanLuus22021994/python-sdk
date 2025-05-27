"""
Modern MCP Python SDK Setup System
Comprehensive setup and validation system following SOLID principles.
"""

from __future__ import annotations

from .docker import DockerSetupManager, validate_docker_environment

# Component managers
from .environment.manager import EnvironmentManager
from .host import HostSetupManager, validate_host_environment

# Core orchestration
from .orchestrator import (
    ModernSetupOrchestrator,
    orchestrate_setup,
    validate_setup_environment,
)

# Sequence management
from .sequence import SetupSequenceManager, SetupSequenceResult, run_setup_sequence

# Type definitions
from .typings import (
    EnvironmentInfo,
    LogLevel,
    PythonVersion,
    SetupMode,
    ValidationStatus,
)
from .typings.environment import ValidationDetails

# Validation framework
from .validation.base import BaseValidator, ValidationContext, ValidationResult
from .validation.composite import CompositeValidator
from .validation.registry import ValidationRegistry, get_global_registry
from .vscode.integration import VSCodeIntegrationManager

__version__ = "1.0.0"

__all__ = [
    # Core orchestration
    "ModernSetupOrchestrator",
    "orchestrate_setup",
    "validate_setup_environment",
    # Sequence management
    "SetupSequenceManager",
    "SetupSequenceResult",
    "run_setup_sequence",
    # Type definitions
    "LogLevel",
    "SetupMode",
    "ValidationStatus",
    "EnvironmentInfo",
    "PythonVersion",
    "ValidationDetails",
    # Validation framework
    "BaseValidator",
    "ValidationContext",
    "ValidationResult",
    "ValidationRegistry",
    "get_global_registry",
    "CompositeValidator",
    # Component managers
    "EnvironmentManager",
    "DockerSetupManager",
    "validate_docker_environment",
    "HostSetupManager",
    "validate_host_environment",
    "VSCodeIntegrationManager",
]
