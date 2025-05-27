"""Package management module for Python SDK setup."""

import subprocess
import sys
from typing import Any

try:
    from ..packages import (
        REQUIRED_PACKAGES,
        get_platform_package_status,
        normalize_package_name,
    )
except ImportError:
    # Fallback definitions if import fails
    REQUIRED_PACKAGES = [
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

    def get_platform_package_status() -> dict[str, bool]:
        """Fallback platform package status."""
        return {}

    def normalize_package_name(package: str) -> str:
        """Fallback package name normalization."""
        return package.lower().replace("_", "-")


def install_package(package: str) -> tuple[bool, str]:
    """
    Install a Python package using the best available package manager.

    Args:
        package: Package name to install

    Returns:
        Tuple of (success, message)
    """
    try:
        # Try uv first (modern fast package manager)
        try:
            result = subprocess.run(
                [sys.executable, "-m", "uv", "add", package],
                capture_output=True,
                text=True,
                timeout=300,
            )
            if result.returncode == 0:
                return True, f"✓ Package {package} installed successfully with uv"
        except FileNotFoundError:
            pass

        # Fallback to pip
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package],
            capture_output=True,
            text=True,
            timeout=300,
        )

        if result.returncode == 0:
            return True, f"✓ Package {package} installed successfully with pip"
        else:
            return False, f"✗ Failed to install {package}: {result.stderr}"

    except subprocess.TimeoutExpired:
        return False, f"✗ Installation of {package} timed out"
    except Exception as e:
        return False, f"✗ Error installing {package}: {e}"


def verify_import(package: str) -> tuple[bool, str]:
    """
    Verify that a package can be imported.

    Args:
        package: Package name to verify

    Returns:
        Tuple of (can_import, message)
    """
    normalized_name = normalize_package_name(package)

    # Map of package names to import names
    import_map = {
        "asyncpg": "asyncpg",
        "httpx-sse": "httpx_sse",
        "sse-starlette": "sse_starlette",
        "pydantic-ai": "pydantic_ai",
        "pgvector": "pgvector",
        "orjson": "orjson",
        "lz4": "lz4",
        "ujson": "ujson",
        "xxhash": "xxhash",
        "zstandard": "zstandard",
        "docker": "docker",
        "pyyaml": "yaml",
    }

    import_name = import_map.get(normalized_name, normalized_name)

    try:
        __import__(import_name)
        return True, f"✓ Package {package} imports successfully"
    except ImportError as e:
        return False, f"✗ Cannot import {package}: {e}"
    except Exception as e:
        return False, f"✗ Error importing {package}: {e}"


def setup_packages() -> bool:
    """
    Set up all required packages for the MCP Python SDK.

    Returns:
        True if all packages were set up successfully
    """
    print("📦 Setting up required packages...")

    # Check platform-specific packages
    platform_status = get_platform_package_status()

    # Combine required packages with platform-specific ones
    all_packages = REQUIRED_PACKAGES.copy()
    all_packages.extend(
        [pkg for pkg, available in platform_status.items() if available]
    )

    success_count = 0
    total_packages = len(all_packages)

    for package in all_packages:
        print(f"  Installing {package}...")

        # First check if already available
        can_import, import_msg = verify_import(package)
        if can_import:
            print(f"    {import_msg}")
            success_count += 1
            continue

        # Try to install
        installed, install_msg = install_package(package)
        print(f"    {install_msg}")

        if installed:
            # Verify after installation
            can_import_after, verify_msg = verify_import(package)
            if can_import_after:
                success_count += 1
                print(f"    {verify_msg}")
            else:
                print(f"    ⚠️ Package installed but verification failed: {verify_msg}")

    print(
        f"\n📦 Package setup complete: {success_count}/{total_packages} packages ready"
    )
    return success_count == total_packages


def check_package_availability(package: str) -> bool:
    """
    Check if a package is available for import.

    Args:
        package: Package name to check

    Returns:
        True if package is available
    """
    can_import, _ = verify_import(package)
    return can_import


def get_installed_packages() -> list[str]:
    """
    Get list of installed packages.

    Returns:
        List of installed package names
    """
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--format=freeze"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            packages = []
            for line in result.stdout.strip().split("\n"):
                if "==" in line:
                    package_name = line.split("==")[0]
                    packages.append(package_name)
            return packages
        return []

    except (subprocess.TimeoutExpired, Exception):
        return []


def get_package_manager_info() -> dict[str, Any]:
    """
    Get information about available package managers.

    Returns:
        Dictionary with package manager information
    """
    managers = {}

    # Check pip
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            managers["pip"] = {
                "available": True,
                "version": result.stdout.strip(),
                "executable": f"{sys.executable} -m pip",
            }
    except (subprocess.TimeoutExpired, FileNotFoundError):
        managers["pip"] = {"available": False}

    # Check uv
    try:
        result = subprocess.run(
            ["uv", "--version"], capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            managers["uv"] = {
                "available": True,
                "version": result.stdout.strip().split()[-1],
                "executable": "uv",
            }
    except (subprocess.TimeoutExpired, FileNotFoundError):
        managers["uv"] = {"available": False}

    # Check poetry
    try:
        result = subprocess.run(
            ["poetry", "--version"], capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            managers["poetry"] = {
                "available": True,
                "version": result.stdout.strip(),
                "executable": "poetry",
            }
    except (subprocess.TimeoutExpired, FileNotFoundError):
        managers["poetry"] = {"available": False}

    return managers


def get_preferred_package_manager() -> str:
    """
    Get the preferred package manager for the current environment.

    Returns:
        Name of the preferred package manager
    """
    managers = get_package_manager_info()

    # Prefer uv > poetry > pip
    if managers.get("uv", {}).get("available", False):
        return "uv"
    elif managers.get("poetry", {}).get("available", False):
        return "poetry"
    elif managers.get("pip", {}).get("available", False):
        return "pip"
    else:
        return "pip"  # Fallback
