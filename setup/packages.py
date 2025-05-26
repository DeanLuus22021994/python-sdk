"""
Package Configuration
Centralized package definitions and management for the MCP Python SDK setup
"""

import platform

# Core packages required for all platforms
REQUIRED_PACKAGES: list[str] = [
    "asyncpg",
    "httpx-sse",
    "sse-starlette",
    "pydantic-ai",
    "pgvector",
    "orjson",
    "lz4",
    "ujson",
    "xxhash",
    "zstandard",
    "docker",  # Added Docker SDK for Python
    "pyyaml",  # Added for YAML handling
]

# Platform-specific packages with their supported platforms
PLATFORM_PACKAGES: dict[str, list[str]] = {
    "uvloop": ["linux", "darwin"],  # Unix-like systems only
}

# Development packages (optional)
DEV_PACKAGES: list[str] = [
    "pytest",
    "pytest-asyncio",
    "black",
    "mypy",
    "ruff",
]


def get_packages_for_platform(include_dev: bool = False) -> list[str]:
    """
    Get all packages that should be installed for the current platform.

    Args:
        include_dev: Whether to include development packages

    Returns:
        List of package names to install
    """
    packages = REQUIRED_PACKAGES.copy()
    current_platform = platform.system().lower()

    # Add platform-specific packages
    for package, supported_platforms in PLATFORM_PACKAGES.items():
        if current_platform in supported_platforms:
            packages.append(package)

    # Add development packages if requested
    if include_dev:
        packages.extend(DEV_PACKAGES)

    return packages


def get_platform_package_status() -> dict[str, bool]:
    """
    Get the installation status of platform-specific packages.

    Returns:
        Dictionary mapping package names to whether they should be installed
    """
    current_platform = platform.system().lower()
    return {
        package: current_platform in supported_platforms
        for package, supported_platforms in PLATFORM_PACKAGES.items()
    }


def normalize_package_name(package: str) -> str:
    """
    Normalize package name for import (replace hyphens with underscores).

    Args:
        package: The package name as it appears in pip

    Returns:
        The package name as it should be imported
    """
    return package.replace("-", "_")
