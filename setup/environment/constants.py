"""
Environment Constants and Configuration
Type-safe constants following modern Python practices.
"""

from typing import Final

from ..typings import PerformanceSettings, PythonVersion

# Python version requirements
MIN_PYTHON_VERSION: Final[PythonVersion] = PythonVersion(3, 10, 0)
RECOMMENDED_PYTHON_VERSION: Final[PythonVersion] = PythonVersion(3, 11, 0)
MAX_TESTED_PYTHON_VERSION: Final[PythonVersion] = PythonVersion(3, 13, 0)

# Project structure requirements
REQUIRED_PROJECT_PATHS: Final[tuple[str, ...]] = (
    "src/mcp",
    "pyproject.toml",
    "setup",
)

OPTIONAL_PROJECT_PATHS: Final[tuple[str, ...]] = (
    "docs",
    "tests",
    ".vscode",
    ".devcontainer",
    "docker-compose.yml",
    "Dockerfile",
    ".github",
    "CONTRIBUTING.md",
    "README.md",
)

# Core package requirements
CORE_PACKAGES: Final[tuple[str, ...]] = (
    "pydantic>=2.0.0",
    "anyio>=4.0.0",
    "httpx>=0.24.0",
    "jsonschema>=4.17.0",
)

# Development packages
DEV_PACKAGES: Final[tuple[str, ...]] = (
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "pytest-asyncio>=0.21.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
    "mypy>=1.5.0",
    "pre-commit>=3.0.0",
)

# Performance settings
DEFAULT_PERFORMANCE_SETTINGS: Final[PerformanceSettings] = PerformanceSettings(
    parallel_operations=True,
    max_workers=4,
    cache_enabled=True,
    cache_ttl_seconds=3600,
    enable_parallel_validation=True,
    timeout_seconds=30.0,
    cache_size=128,
)

# Environment validation timeouts
VALIDATION_TIMEOUTS: Final[dict[str, float]] = {
    "python_check": 5.0,
    "path_validation": 2.0,
    "package_manager": 10.0,
    "virtual_env": 3.0,
}

# Cache configuration
CACHE_CONFIG: Final[dict[str, int]] = {
    "max_size": 128,
    "ttl_seconds": 300,
    "cleanup_interval": 3600,
}
