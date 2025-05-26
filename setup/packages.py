"""
Package Configuration
Centralized package definitions and management for the MCP Python SDK setup
"""

import importlib.util
import platform
from collections import defaultdict
from functools import lru_cache

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
    "docker",  # Docker SDK for Python
    "pyyaml",  # YAML handling
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

# Performance optimization packages
PERF_PACKAGES: list[str] = [
    "cython",
    "pyarrow",
]


@lru_cache(maxsize=128)
def get_packages_for_platform(
    include_dev: bool = False, include_performance: bool = False
) -> list[str]:
    """
    Get all packages that should be installed for the current platform.

    Args:
        include_dev: Whether to include development packages
        include_performance: Whether to include performance optimization packages

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

    # Add performance packages if requested
    if include_performance:
        packages.extend(PERF_PACKAGES)

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
    # Special mappings for packages with different import names
    special_mappings = {
        "pyyaml": "yaml",
        "httpx-sse": "httpx_sse",
        "sse-starlette": "sse_starlette",
        "pydantic-ai": "pydantic_ai",
        "pytest-asyncio": "pytest_asyncio",
    }

    if package in special_mappings:
        return special_mappings[package]

    return package.replace("-", "_")


def check_package_installed(package: str) -> bool:
    """
    Check if a package is installed.

    Args:
        package: The package name

    Returns:
        True if the package is installed, False otherwise
    """
    module_name = normalize_package_name(package)
    return importlib.util.find_spec(module_name) is not None


def get_package_dependencies(packages: list[str]) -> dict[str, set[str]]:
    """
    Get dependencies for the given packages.

    Args:
        packages: List of package names

    Returns:
        Dictionary mapping package names to sets of dependency package names
    """
    try:
        import pkg_resources

        dependencies = defaultdict(set)
        for package in packages:
            try:
                dist = pkg_resources.get_distribution(package)
                for req in dist.requires():
                    dependencies[package].add(req.project_name)
            except pkg_resources.DistributionNotFound:
                pass
        return dependencies
    except ImportError:
        # pkg_resources not available, return empty dependencies
        return {package: set() for package in packages}


def get_missing_packages(packages: list[str]) -> tuple[list[str], list[str]]:
    """
    Check which packages are missing and which are installed.

    Args:
        packages: List of package names to check

    Returns:
        Tuple of (missing_packages, installed_packages)
    """
    missing = []
    installed = []

    for package in packages:
        if check_package_installed(package):
            installed.append(package)
        else:
            missing.append(package)

    return missing, installed
