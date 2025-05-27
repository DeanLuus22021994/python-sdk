"""
Package Configuration
Centralized package definitions and management for the MCP Python SDK setup
"""

import subprocess
import sys
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
    "docker",
    "pyyaml",
]

# Platform-specific packages with their supported platforms
PLATFORM_PACKAGES: dict[str, list[str]] = {
    "uvloop": ["linux", "darwin"],
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
def get_packages_for_platform(platform: str | None = None) -> list[str]:
    """
    Get packages appropriate for the current or specified platform.

    Args:
        platform: Platform name (linux, darwin, win32). If None, uses current platform.

    Returns:
        List of package names suitable for the platform
    """
    if platform is None:
        platform = sys.platform

    packages = REQUIRED_PACKAGES.copy()

    # Add platform-specific packages
    for package, supported_platforms in PLATFORM_PACKAGES.items():
        if platform in supported_platforms:
            packages.append(package)

    return packages


def get_platform_package_status() -> dict[str, bool]:
    """
    Get status of platform-specific packages.

    Returns:
        Dictionary mapping package names to availability status
    """
    status = {}
    current_platform = sys.platform

    for package, supported_platforms in PLATFORM_PACKAGES.items():
        status[package] = current_platform in supported_platforms

    return status


def normalize_package_name(package: str) -> str:
    """
    Normalize package name for import checking.

    Args:
        package: Package name to normalize

    Returns:
        Normalized package name
    """
    # Handle common package name to import name mappings
    name_mappings = {
        "httpx-sse": "httpx_sse",
        "pydantic-ai": "pydantic_ai",
        "sse-starlette": "sse_starlette",
    }

    return name_mappings.get(package, package.replace("-", "_"))


def check_package_installed(package: str) -> bool:
    """
    Check if a package is installed.

    Args:
        package: Package name to check

    Returns:
        True if package is installed, False otherwise
    """
    try:
        normalized_name = normalize_package_name(package)
        __import__(normalized_name)
        return True
    except ImportError:
        return False


def get_package_dependencies(packages: list[str]) -> dict[str, set[str]]:
    """
    Get dependencies for a list of packages.

    Args:
        packages: List of package names

    Returns:
        Dictionary mapping package names to their dependencies"""
    dependencies: dict[str, set[str]] = defaultdict(set)

    for package in packages:
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "show", package],
                capture_output=True,
                text=True,
                check=True,
            )
            for line in result.stdout.split("\n"):
                if line.startswith("Requires:"):
                    deps = line.split(":", 1)[1].strip()
                    if deps and deps != "":
                        dependencies[package] = {
                            dep.strip() for dep in deps.split(",") if dep.strip()
                        }
                    break

        except (subprocess.CalledProcessError, FileNotFoundError):
            # Package not installed or pip not available
            continue

    return dict(dependencies)
