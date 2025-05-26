"""
Constants and Configuration Values
Centralized constants for the MCP Python SDK setup with type safety and immutability.
"""

from dataclasses import dataclass
from typing import Final, NamedTuple


class PythonVersion(NamedTuple):
    """Type-safe Python version representation."""

    major: int
    minor: int

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}"

    def __lt__(self, other: "PythonVersion") -> bool:
        return (self.major, self.minor) < (other.major, other.minor)

    def __le__(self, other: "PythonVersion") -> bool:
        return (self.major, self.minor) <= (other.major, other.minor)

    def __gt__(self, other: "PythonVersion") -> bool:
        return (self.major, self.minor) > (other.major, other.minor)

    def __ge__(self, other: "PythonVersion") -> bool:
        return (self.major, self.minor) >= (other.major, other.minor)


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


# Python version requirements with type safety
MIN_PYTHON_VERSION: Final[PythonVersion] = PythonVersion(3, 10)
RECOMMENDED_PYTHON_VERSION: Final[PythonVersion] = PythonVersion(3, 11)
MAX_TESTED_PYTHON_VERSION: Final[PythonVersion] = PythonVersion(3, 13)

# Project structure requirements - immutable collections
REQUIRED_PROJECT_PATHS: Final[tuple[str, ...]] = (
    "src/mcp",
    "pyproject.toml",
    ".vscode",
    "setup",
)

# Optional project paths for enhanced development
OPTIONAL_PROJECT_PATHS: Final[tuple[str, ...]] = (
    "docs",
    "tests",
    "examples",
    "README.md",
    "LICENSE",
    "docker-compose.yml",
    ".devcontainer",
    ".github",
)

# VS Code recommended extensions for enhanced development
RECOMMENDED_EXTENSIONS: Final[tuple[str, ...]] = (
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-python.black-formatter",
    "ms-python.mypy-type-checker",
    "charliermarsh.ruff",
    "ms-python.debugpy",
    "github.copilot",
    "github.copilot-chat",
    "ms-vscode.errorlens",
    "ms-vscode.vscode-json",
    "tamasfe.even-better-toml",
    "redhat.vscode-yaml",
    "yzhang.markdown-all-in-one",
    "ms-azuretools.vscode-docker",
)

# Default performance settings instance
PERFORMANCE_SETTINGS: Final[PerformanceSettings] = PerformanceSettings()

# VS Code performance settings
VS_CODE_PERFORMANCE_SETTINGS: Final[dict[str, str | int | bool | dict[str, bool]]] = {
    "python.analysis.userFileIndexingLimit": 5000,
    "python.analysis.packageIndexDepths": [{"name": "mcp", "depth": 5}],
    "files.watcherExclude": {
        "**/__pycache__/**": True,
        "**/.git/objects/**": True,
        "**/.git/subtree-cache/**": True,
        "**/node_modules/**": True,
        "**/.pytest_cache/**": True,
        "**/.mypy_cache/**": True,
        "**/.ruff_cache/**": True,
        "**/.venv/**": True,
        "**/venv/**": True,
        "**/build/**": True,
        "**/dist/**": True,
        "**/.coverage/**": True,
        "**/.tox/**": True,
        "**/htmlcov/**": True,
    },
    "search.exclude": {
        "**/.venv": True,
        "**/venv": True,
        "**/__pycache__": True,
        "**/*.pyc": True,
        "**/.pytest_cache": True,
        "**/.mypy_cache": True,
        "**/.ruff_cache": True,
        "**/build": True,
        "**/dist": True,
        "**/*.egg-info": True,
        "**/.coverage": True,
        "**/.tox": True,
        "**/htmlcov": True,
        "**/uv.lock": True,
    },
}

# Default container configuration instance
DEFAULT_CONTAINER_CONFIG: Final[ContainerConfig] = ContainerConfig()

# Docker requirements
DOCKER_MIN_VERSION: Final[tuple[int, int, int]] = (20, 10, 0)
REQUIRED_DOCKER_IMAGES: Final[tuple[str, ...]] = (
    "postgres:14-alpine",
    "python:3.11-slim",
)
