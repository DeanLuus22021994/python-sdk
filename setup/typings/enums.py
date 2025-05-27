"""
Enumeration types for the MCP Python SDK setup system.

This module contains all enum definitions used for categorization, status tracking,
and configuration options throughout the setup system.
"""

from __future__ import annotations

from enum import Enum, auto

__all__ = [
    "SetupMode",
    "LogLevel",
    "ValidationStatus",
]


class SetupMode(Enum):
    """Setup execution modes for different deployment scenarios."""

    HOST = "host"
    """Direct host installation mode."""

    DOCKER = "docker"
    """Docker container-based setup mode."""

    HYBRID = "hybrid"
    """Hybrid mode supporting both host and container operations."""

    DEVELOPMENT = "development"
    """Development mode with enhanced debugging and tooling."""

    def __str__(self) -> str:
        return self.value


class LogLevel(Enum):
    """Logging levels for setup operations and debugging."""

    DEBUG = auto()
    """Detailed debugging information."""

    INFO = auto()
    """General informational messages."""

    WARNING = auto()
    """Warning messages for potential issues."""

    ERROR = auto()
    """Error messages for failures."""

    def __str__(self) -> str:
        return self.name.lower()

    @property
    def numeric_value(self) -> int:
        """Get numeric value for level comparison."""
        return {
            LogLevel.DEBUG: 10,
            LogLevel.INFO: 20,
            LogLevel.WARNING: 30,
            LogLevel.ERROR: 40,
        }[self]


class ValidationStatus(Enum):
    """Validation status enumeration for setup components."""

    VALID = auto()
    """Component is valid and ready for use."""

    WARNING = auto()
    """Component has warnings but can still function."""

    ERROR = auto()
    """Component has errors and cannot function properly."""

    UNKNOWN = auto()
    """Component status could not be determined."""

    def __str__(self) -> str:
        return self.name.lower()

    @property
    def is_healthy(self) -> bool:
        """Check if status indicates a healthy state."""
        return self in (ValidationStatus.VALID, ValidationStatus.WARNING)

    @property
    def requires_attention(self) -> bool:
        """Check if status requires user attention."""
        return self in (
            ValidationStatus.WARNING,
            ValidationStatus.ERROR,
            ValidationStatus.UNKNOWN,
        )
