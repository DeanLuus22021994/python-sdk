"""
Data classes for environment and system information.

This module contains data classes that represent various aspects of the
development environment, including Python version, environment details,
and system information.
"""

from __future__ import annotations

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
    """
    Python version representation with modern comparison methods.

    Uses NamedTuple for immutability and built-in comparison support
    without overriding incompatible methods.
    """

    major: int
    minor: int
    patch: int = 0

    def __str__(self) -> str:
        if self.patch:
            return f"{self.major}.{self.minor}.{self.patch}"
        return f"{self.major}.{self.minor}"

    def compare_to(self, other: PythonVersion) -> int:
        """
        Compare versions without overriding incompatible NamedTuple methods.

        Returns:
            -1 if self < other, 0 if equal, 1 if self > other
        """
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
        """Check if this Python version is supported by the SDK."""
        # Support Python 3.10+
        return (self.major, self.minor) >= (3, 10)

    @property
    def version_tuple(self) -> tuple[int, int, int]:
        """Get version as a tuple for easy comparison."""
        return (self.major, self.minor, self.patch)

    @classmethod
    def from_string(cls, version_str: str) -> PythonVersion:
        """Create PythonVersion from string like '3.11.0'."""
        parts = version_str.split(".")
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
        """Validate environment information after initialization."""
        if not self.python_executable:
            raise ValueError("python_executable cannot be empty")

        if self.virtual_env_active and not self.virtual_env_path:
            self.virtual_env_path = "unknown"

    @property
    def is_virtual_env(self) -> bool:
        """Check if running in a virtual environment."""
        return self.virtual_env_active

    @property
    def env_summary(self) -> str:
        """Get a brief summary of the environment."""
        venv_status = "virtual" if self.virtual_env_active else "system"
        return f"Python {self.python_version} ({venv_status}) on {self.platform_system}"


@dataclass(slots=True)
class ValidationDetails:
    """Detailed validation results with comprehensive error tracking."""

    is_valid: bool
    status: ValidationStatus
    message: str
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    metadata: dict[str, object] = field(default_factory=dict)

    # Additional validation context
    component_name: str = ""
    validation_time: float = 0.0

    def __post_init__(self) -> None:
        """Ensure validation details are consistent."""
        if self.is_valid and self.status == ValidationStatus.ERROR:
            self.is_valid = False

        if not self.is_valid and self.status == ValidationStatus.VALID:
            self.status = ValidationStatus.ERROR

    def add_warning(self, warning: str) -> None:
        """Add a warning message."""
        self.warnings.append(warning)
        if self.status == ValidationStatus.VALID:
            self.status = ValidationStatus.WARNING

    def add_error(self, error: str) -> None:
        """Add an error message."""
        self.errors.append(error)
        self.is_valid = False
        self.status = ValidationStatus.ERROR

    def add_recommendation(self, recommendation: str) -> None:
        """Add a recommendation for improvement."""
        self.recommendations.append(recommendation)

    @property
    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return len(self.warnings) > 0

    @property
    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return len(self.errors) > 0

    def get_summary(self) -> str:
        """Get a summary of validation results."""
        status_msg = f"Status: {self.status.name.lower()}"
        if self.has_errors:
            status_msg += f" ({len(self.errors)} errors)"
        if self.has_warnings:
            status_msg += f" ({len(self.warnings)} warnings)"
        return status_msg


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
        """Validate project structure information."""
        if not self.root_path.exists():
            raise ValueError(f"Project root path does not exist: {self.root_path}")

    @property
    def completeness_percentage(self) -> float:
        """Calculate project structure completeness percentage."""
        total_paths = len(self.missing_required) + len(self.optional_paths_status)
        if total_paths == 0:
            return 100.0

        existing_paths = len([p for p in self.optional_paths_status.values() if p])
        if self.required_paths_valid:
            existing_paths += len(self.missing_required)

        return (existing_paths / total_paths) * 100.0

    @property
    def size_mb(self) -> float:
        """Get total size in megabytes."""
        return self.total_size_bytes / (1024 * 1024)

    def get_structure_summary(self) -> str:
        """Get a summary of project structure."""
        return (
            f"Project at {self.root_path.name}: "
            f"{self.file_count} files, "
            f"{self.directory_count} directories, "
            f"{self.size_mb:.1f} MB"
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
        """Validate package manager information."""
        if not any(
            [
                self.pip_available,
                self.conda_available,
                self.uv_available,
                self.poetry_available,
            ]
        ):
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
    def best_manager(self) -> str:
        """Get the best available package manager."""
        # Prefer modern managers
        if self.uv_available:
            return "uv"
        elif self.poetry_available:
            return "poetry"
        elif self.pip_available:
            return "pip"
        elif self.conda_available:
            return "conda"
        else:
            return "none"

    def get_install_command(self, package: str) -> str:
        """Get installation command for a package."""
        manager = self.best_manager
        if manager == "uv":
            return f"uv add {package}"
        elif manager == "poetry":
            return f"poetry add {package}"
        elif manager == "pip":
            return f"pip install {package}"
        elif manager == "conda":
            return f"conda install {package}"
        else:
            return f"# No package manager available to install {package}"

    def get_manager_summary(self) -> str:
        """Get a summary of available package managers."""
        available = self.get_available_managers()
        return f"Available managers: {', '.join(available)} (preferred: {self.best_manager})"
