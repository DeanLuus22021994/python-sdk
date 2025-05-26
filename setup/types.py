"""
Type definitions for the MCP Python SDK setup system.
Centralized type definitions to ensure consistency across all setup modules.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any, NamedTuple, Protocol, TypeAlias, TypedDict

# Core type aliases for compatibility - using modern Python 3.10+ syntax
PathLike: TypeAlias = str | Path
JsonValue: TypeAlias = str | int | float | bool | None | dict[str, Any] | list[Any]
ValidationResult: TypeAlias = tuple[bool, str]
SetupResult: TypeAlias = tuple[bool, dict[str, Any]]


class PythonVersion(NamedTuple):
    """Python version representation without overriding incompatible methods."""

    major: int
    minor: int

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}"

    def compare_to(self, other: "PythonVersion") -> int:
        """Compare versions without overriding incompatible NamedTuple methods."""
        if (self.major, self.minor) < (other.major, other.minor):
            return -1
        elif (self.major, self.minor) > (other.major, other.minor):
            return 1
        else:
            return 0

    def is_compatible_with(self, other: "PythonVersion") -> bool:
        """Check if this version is compatible with the other version."""
        return self.major == other.major and self.minor >= other.minor


class SetupMode(Enum):
    """Setup execution modes."""

    HOST = "host"
    DOCKER = "docker"
    HYBRID = "hybrid"


class LogLevel(Enum):
    """Logging levels for setup operations."""

    DEBUG = auto()
    INFO = auto()
    WARNING = auto()
    ERROR = auto()

    def __str__(self) -> str:
        return self.name.lower()


class ValidationStatus(Enum):
    """Validation status enumeration."""

    VALID = auto()
    WARNING = auto()
    ERROR = auto()
    UNKNOWN = auto()

    def __str__(self) -> str:
        return self.name.lower()


@dataclass(frozen=True)
class PerformanceSettings:
    """Performance configuration for setup operations."""

    parallel_operations: bool = True
    max_workers: int = 4
    cache_enabled: bool = True
    cache_ttl_seconds: int = 3600
    enable_parallel_validation: bool = True
    timeout_seconds: float = 30.0
    cache_size: int = 128


@dataclass(frozen=True)
class ContainerConfig:
    """Container runtime configuration."""

    base_image: str = "python:3.11-slim"
    work_dir: str = "/app"
    expose_port: int = 8000
    health_check_interval: int = 30


@dataclass
class EnvironmentInfo:
    """Comprehensive environment information."""

    python_version: PythonVersion
    python_executable: str
    virtual_env_active: bool
    virtual_env_type: str | None = None
    virtual_env_path: str | None = None
    platform_system: str = ""
    platform_release: str = ""
    architecture: str = ""


@dataclass
class ValidationDetails:
    """Detailed validation results."""

    is_valid: bool
    status: ValidationStatus
    message: str
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ProjectStructureInfo:
    """Project structure validation information."""

    root_path: Path
    required_paths_valid: bool
    missing_required: list[str] = field(default_factory=list)
    optional_paths_status: dict[str, bool] = field(default_factory=dict)
    total_size_bytes: int = 0
    file_count: int = 0


@dataclass
class PackageManagerInfo:
    """Package manager availability and configuration."""

    pip_available: bool
    pip_version: str | None = None
    conda_available: bool = False
    conda_version: str | None = None
    uv_available: bool = False
    uv_version: str | None = None
    preferred_manager: str = "pip"


class VSCodeExtension(TypedDict):
    """VS Code extension information."""

    id: str
    publisher: str
    name: str
    description: str


@dataclass
class VSCodeConfig:
    """VS Code configuration settings."""

    settings: dict[str, Any] = field(default_factory=dict)
    extensions: list[str] = field(default_factory=list)
    recommended_extensions: list[VSCodeExtension] = field(default_factory=list)
    launch_config: dict[str, Any] = field(default_factory=dict)
    tasks_config: dict[str, Any] = field(default_factory=dict)
    workspace_config: dict[str, Any] = field(default_factory=dict)


@dataclass
class DockerInfo:
    """Docker environment information."""

    docker_available: bool
    docker_version: tuple[int, int, int] | None = None
    compose_available: bool = False
    compose_version: str | None = None
    images_available: list[str] = field(default_factory=list)
    containers_running: list[str] = field(default_factory=list)


@dataclass
class SetupContext:
    """Complete setup context information."""

    mode: SetupMode
    project_root: Path
    environment_info: EnvironmentInfo
    project_structure: ProjectStructureInfo
    package_manager: PackageManagerInfo
    vscode_config: VSCodeConfig | None = None
    docker_info: DockerInfo | None = None
    performance_settings: PerformanceSettings | None = None

    def __post_init__(self) -> None:
        if self.performance_settings is None:
            self.performance_settings = PerformanceSettings()


# Protocol definitions for type checking
class Validator(Protocol):
    """Protocol for validation classes."""

    def validate(self) -> ValidationDetails:
        """Perform validation and return detailed results."""
        ...


class SetupManager(Protocol):
    """Protocol for setup manager classes."""

    def setup(self) -> SetupResult:
        """Perform setup and return results."""
        ...

    def validate(self) -> ValidationDetails:
        """Validate current state."""
        ...


class ConfigManager(Protocol):
    """Protocol for configuration managers."""

    def load_config(self) -> dict[str, Any]:
        """Load configuration from file or defaults."""
        ...

    def save_config(self, config: dict[str, Any]) -> bool:
        """Save configuration to file."""
        ...

    def validate_config(self, config: dict[str, Any]) -> ValidationDetails:
        """Validate configuration structure and values."""
        ...


# Type aliases for complex return types
EnvironmentValidationResult: TypeAlias = tuple[bool, EnvironmentInfo, list[str]]
ProjectValidationResult: TypeAlias = tuple[bool, ProjectStructureInfo, list[str]]
SetupProgressCallback: TypeAlias = Callable[[str, float], None]
LoggingCallback: TypeAlias = Callable[[LogLevel, str], None]


# Exception types for setup operations
class SetupError(Exception):
    """Base exception for setup operations."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.details = details or {}


class ValidationError(SetupError):
    """Exception raised during validation failures."""

    pass


class ConfigurationError(SetupError):
    """Exception raised for configuration issues."""

    pass


class EnvironmentError(SetupError):
    """Exception raised for environment-related issues."""

    pass


class ContainerError(SetupError):
    """Exception raised for container-related issues."""

    pass


# Constants for type annotations - using modern Python 3.10+ syntax
VSCodeSettingsDict: TypeAlias = dict[str, str | int | bool | dict[str, Any] | list[Any]]
PackageManagerDict: TypeAlias = dict[str, bool | str | None]
EnvironmentDict: TypeAlias = dict[
    str, str | int | bool | PythonVersion | dict[str, Any]
]
