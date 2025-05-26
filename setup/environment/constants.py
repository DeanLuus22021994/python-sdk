"""
Constants and Configuration Values
Centralized constants for the MCP Python SDK setup with type safety and immutability.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Final, NamedTuple


class PythonVersion(NamedTuple):
    """Type-safe Python version representation."""
    major: int
    minor: int

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}"


class SetupMode(Enum):
    """Setup execution modes."""
    HOST = "host"
    DOCKER = "docker"
    HYBRID = "hybrid"


class LogLevel(Enum):
    """Logging levels for setup operations."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


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

# Performance optimization settings
@dataclass(frozen=True)
class PerformanceSettings:
    """Performance configuration for setup operations."""
    parallel_operations: bool = True
    max_workers: int = 4
    cache_enabled: bool = True
    cache_ttl_seconds: int = 3600
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
# Default performance settings instance
PERFORMANCE_SETTINGS: Final[PerformanceSettings] = PerformanceSettings()

# VS Code performance settings
VS_CODE_PERFORMANCE_SETTINGS: Final[dict] = {
    "python.analysis.userFileIndexingLimit": 5000,
    "python.analysis.packageIndexDepths": [{"name": "mcp", "depth": 5}],
    "files.watcherExclude": {
        "**/__pycache__/**": True,
        "**/.git/objects/**": True,
        "**/.git/subtree-cache/**": True,
        "**/node_modules/**": True,
        "**/.pytest_cache/**": True,
DEFAULT_CONTAINER_CONFIG: Final[ContainerConfig] = ContainerConfig()

# Docker requirements
DOCKER_MIN_VERSION: Final[tuple[int, int, int]] = (20, 10, 0)
REQUIRED_DOCKER_IMAGES: Final[tuple[str, ...]] = (
    "postgres:14-alpine",
    "python:3.11-slim",
)
    "ms-vscode.errorlens",
    "ms-vscode.vscode-json",
    "tamasfe.even-better-toml",
    "redhat.vscode-yaml",
    "yzhang.markdown-all-in-one",
    "ms-azuretools.vscode-docker",  # Added Docker extension
]

# Performance settings
PERFORMANCE_SETTINGS = {
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

# Docker requirements
DOCKER_MIN_VERSION = (20, 10, 0)
REQUIRED_DOCKER_IMAGES = [
    "postgres:14-alpine",
    "python:3.11-slim",
]
