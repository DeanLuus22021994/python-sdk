"""
Core type aliases and fundamental types for the MCP Python SDK setup system.

This module provides the foundational type definitions used throughout the setup system.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypeAlias, Union

if TYPE_CHECKING:
    from .enums import LogLevel
    from .environment import EnvironmentInfo, ProjectStructureInfo, PythonVersion

__all__ = [
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
]

# Core type aliases using modern Python 3.10+ syntax
PathLike: TypeAlias = str | Path
"""Type alias for path-like objects - strings or Path objects."""

JsonValue: TypeAlias = str | int | float | bool | None | dict[str, Any] | list[Any]
"""Type alias for JSON-serializable values."""

ValidationResult: TypeAlias = tuple[bool, str]
"""Type alias for simple validation results - (is_valid, message)."""

SetupResult: TypeAlias = tuple[bool, dict[str, Any]]
"""Type alias for setup operation results - (success, details)."""

# Complex operation result types
EnvironmentValidationResult: TypeAlias = tuple[bool, "EnvironmentInfo", list[str]]
"""Type alias for environment validation results - (valid, info, errors)."""

ProjectValidationResult: TypeAlias = tuple[bool, "ProjectStructureInfo", list[str]]
"""Type alias for project validation results - (valid, info, errors)."""

# Callback types for setup operations
SetupProgressCallback: TypeAlias = Callable[[str, float], None]
"""Type alias for progress callback functions - (message, progress_percent)."""

LoggingCallback: TypeAlias = Callable[["LogLevel", str], None]
"""Type alias for logging callback functions - (level, message)."""

# Complex configuration dictionary types
VSCodeSettingsDict: TypeAlias = dict[str, str | int | bool | dict[str, Any] | list[Any]]
"""Type alias for VS Code settings dictionaries."""

PackageManagerDict: TypeAlias = dict[str, bool | str | None]
"""Type alias for package manager information dictionaries."""

EnvironmentDict: TypeAlias = dict[
    str, Union[str, int, bool, "PythonVersion", dict[str, Any]]
]
"""Type alias for environment information dictionaries."""
