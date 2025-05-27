"""
Data classes for environment and system information.
"""

from __future__ import annotations

import os
import platform
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import NamedTuple

from .enums import ValidationStatus

__all__ = [
    "PythonVersion",
    "EnvironmentInfo",
    "ValidationDetails",
    "ProjectStructureInfo",
    "PackageManagerInfo",
]


class PythonVersion(NamedTuple):
    """Python version representation with modern comparison methods."""

    major: int
    minor: int
    patch: int = 0

    def __str__(self) -> str:
        if self.patch:
            return f"{self.major}.{self.minor}.{self.patch}"
        return f"{self.major}.{self.minor}"

    def compare_to(self, other: PythonVersion) -> int:
        """Compare versions without overriding incompatible NamedTuple methods."""
        self_tuple = (self.major, self.minor, self.patch)
        other_tuple = (other.major, other.minor, other.patch)

        if self_tuple < other_tuple:
            return -1
        elif self_tuple > other_tuple:
            return 1
        else:
            return 0

    def is_compatible_with(self, other: PythonVersion) -> bool:
        """Check if this version is compatible with the other version."""
        return self.major == other.major and self.minor >= other.minor

    @property
    def is_supported(self) -> bool:
        """Check if this Python version is supported."""
        return self.major >= 3 and self.minor >= 10

    @property
    def version_tuple(self) -> tuple[int, int, int]:
        """Get version as tuple."""
        return (self.major, self.minor, self.patch)

    @classmethod
    def from_string(cls, version_str: str) -> PythonVersion:
        """Create PythonVersion from string representation."""
        parts = version_str.split(".")
        if len(parts) < 2:
            raise ValueError(f"Invalid version string: {version_str}")

        major = int(parts[0])
        minor = int(parts[1])
        patch = int(parts[2]) if len(parts) > 2 else 0

        return cls(major, minor, patch)


@dataclass(slots=True)
class EnvironmentInfo:
    """Comprehensive environment information for setup validation."""

    python_version: PythonVersion
    python_executable: str
    virtual_env_active: bool
    virtual_env_type: str | None = None
    virtual_env_path: str | None = None
    platform_system: str = ""
    platform_release: str = ""
    architecture: str = ""

    # Additional environment details
    python_path: list[str] = field(default_factory=list)
    environment_variables: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialize additional environment information."""
        if not self.platform_system:
            self.platform_system = platform.system()
        if not self.platform_release:
            self.platform_release = platform.release()
        if not self.architecture:
            self.architecture = platform.machine()
        if not self.python_path:
            self.python_path = sys.path.copy()
        if not self.environment_variables:
            self.environment_variables = dict(os.environ)

    @property
    def is_virtual_env(self) -> bool:
        """Check if running in virtual environment."""
        return self.virtual_env_active

    @property
    def environment_summary(self) -> str:
        """Get summary of environment."""
        return (
            f"Python {self.python_version} on {self.platform_system} "
            f"({self.architecture})"
        )


@dataclass(slots=True)
class ValidationDetails:
    """Detailed validation results with comprehensive information."""

    is_valid: bool
    status: ValidationStatus
    message: str
    component_name: str = ""
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    metadata: dict[str, str | int | bool | None] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate the validation details."""
        if self.is_valid and self.status == ValidationStatus.ERROR:
            # Fix inconsistent state
            self.is_valid = False

    @property
    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return len(self.errors) > 0

    @property
    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return len(self.warnings) > 0

    @property
    def error_count(self) -> int:
        """Get number of errors."""
        return len(self.errors)

    @property
    def warning_count(self) -> int:
        """Get number of warnings."""
        return len(self.warnings)


@dataclass(slots=True)
class ProjectStructureInfo:
    """Project structure validation information with detailed metrics."""

    root_path: Path
    required_paths_valid: bool
    missing_required: list[str] = field(default_factory=list)
    optional_paths_status: dict[str, bool] = field(default_factory=dict)
    total_size_bytes: int = 0
    file_count: int = 0

    # Additional structure metrics
    directory_count: int = 0
    python_file_count: int = 0
    test_file_count: int = 0

    def __post_init__(self) -> None:
        """Initialize structure info after creation."""
        if not self.root_path.exists():
            raise ValueError(f"Root path does not exist: {self.root_path}")

    @property
    def has_missing_required(self) -> bool:
        """Check if any required paths are missing."""
        return len(self.missing_required) > 0

    @property
    def optional_coverage_percent(self) -> float:
        """Get percentage of optional paths that exist."""
        if not self.optional_paths_status:
            return 100.0
        total = len(self.optional_paths_status)
        existing = sum(1 for exists in self.optional_paths_status.values() if exists)
        return (existing / total) * 100.0

    def get_structure_summary(self) -> str:
        """Get structure summary string."""
        return (
            f"Files: {self.file_count}, Directories: {self.directory_count}, "
            f"Python files: {self.python_file_count}"
        )


@dataclass(slots=True)
class PackageManagerInfo:
    """Package manager availability and configuration with version tracking."""

    pip_available: bool
    pip_version: str | None = None
    conda_available: bool = False
    conda_version: str | None = None
    uv_available: bool = False
    uv_version: str | None = None
    poetry_available: bool = False
    poetry_version: str | None = None
    preferred_manager: str = "pip"

    # Additional package manager details
    installation_path: dict[str, str] = field(default_factory=dict)
    capabilities: dict[str, list[str]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialize package manager info."""
        if not any([
            self.pip_available,
            self.conda_available,
            self.uv_available,
            self.poetry_available,
        ]):
            raise ValueError("At least one package manager must be available")

    def get_available_managers(self) -> list[str]:
        """Get list of available package managers."""
        managers = []
        if self.pip_available:
            managers.append("pip")
        if self.conda_available:
            managers.append("conda")
        if self.uv_available:
            managers.append("uv")
        if self.poetry_available:
            managers.append("poetry")
        return managers

    @property
    def has_modern_manager(self) -> bool:
        """Check if modern package managers (uv, poetry) are available."""
        return self.uv_available or self.poetry_available

    def get_best_manager(self) -> str:
        """Get the best available package manager."""
        if self.uv_available:
            return "uv"
        elif self.poetry_available:
            return "poetry"
        elif self.pip_available:
            return "pip"
        elif self.conda_available:
            return "conda"
        else:
            return self.preferred_manager
