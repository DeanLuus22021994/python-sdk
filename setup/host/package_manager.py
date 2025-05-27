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
    ]

    def get_platform_package_status() -> dict[str, bool]:
        """Get platform-specific package availability status."""
        return {pkg: True for pkg in REQUIRED_PACKAGES}

    def normalize_package_name(package: str) -> str:
        """Normalize package name for consistent handling."""
        return package.lower().replace("_", "-")


def install_package(package: str) -> tuple[bool, str]:
    """
    Install a package using the best available package manager.

    Args:
        package: Package name to install

    Returns:
        Tuple of (success, message)
    """
    try:
        # Try uv first (fastest)
        try:
            result = subprocess.run(
                [sys.executable, "-m", "uv", "add", package],
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode == 0:
                return True, f"Successfully installed {package} with uv"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        # Fall back to pip
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package],
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode == 0:
            return True, f"Successfully installed {package} with pip"
        else:
            return False, f"Failed to install {package}: {result.stderr}"

    except subprocess.TimeoutExpired:
        return False, f"Installation of {package} timed out"
    except Exception as e:
        return False, f"Installation failed: {e}"


def verify_import(package: str) -> tuple[bool, str]:
    """
    Verify that a package can be imported.

    Args:
        package: Package name to verify

    Returns:
        Tuple of (success, message)
    """
    try:
        # Map package names to import names
        import_mapping = {
            "pydantic-ai": "pydantic_ai",
            "httpx-sse": "httpx_sse",
            "sse-starlette": "sse_starlette",
        }

        import_name = import_mapping.get(package, package)

        # Try to import the package
        __import__(import_name)
        return True, f"Package {package} imports successfully"

    except ImportError as e:
        return False, f"Cannot import {package}: {e}"
    except Exception as e:
        return False, f"Import verification failed: {e}"


def setup_packages() -> bool:
    """
    Set up all required packages for the MCP Python SDK.

    Returns:
        True if all packages were installed successfully
    """
    success_count = 0
    total_packages = len(REQUIRED_PACKAGES)

    print(f"Installing {total_packages} required packages...")

    for package in REQUIRED_PACKAGES:
        print(f"  Installing {package}...")

        # Check if already installed and working
        can_import, _ = verify_import(package)
        if can_import:
            print(f"    ✓ {package} already available")
            success_count += 1
            continue

        # Install the package
        installed, message = install_package(package)
        if installed:
            # Verify the installation
            can_import, import_message = verify_import(package)
            if can_import:
                print(f"    ✓ {package} installed and verified")
                success_count += 1
            else:
                print(f"    ⚠ {package} installed but cannot import: {import_message}")
        else:
            print(f"    ✗ Failed to install {package}: {message}")

    success_rate = (success_count / total_packages) * 100
    print(
        f"\nPackage setup completed: {success_count}/{total_packages} ({success_rate:.1f}%)"
    )

    return success_count == total_packages


def check_package_availability(package: str) -> bool:
    """
    Check if a package is available for installation.

    Args:
        package: Package name to check

    Returns:
        True if package is available
    """
    try:
        # Try to get package info from PyPI
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", package],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            return True

        # If not installed, try to search
        result = subprocess.run(
            [sys.executable, "-m", "pip", "search", package],
            capture_output=True,
            text=True,
            timeout=30,
        )

        return result.returncode == 0

    except Exception:
        return False


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

    except Exception:
        pass

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
            }
    except Exception:
        managers["pip"] = {"available": False}

    # Check uv
    try:
        result = subprocess.run(
            [sys.executable, "-m", "uv", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            managers["uv"] = {
                "available": True,
                "version": result.stdout.strip(),
            }
    except Exception:
        managers["uv"] = {"available": False}

    # Check poetry
    try:
        result = subprocess.run(
            ["poetry", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            managers["poetry"] = {
                "available": True,
                "version": result.stdout.strip(),
            }
    except Exception:
        managers["poetry"] = {"available": False}

    return managers


def get_preferred_package_manager() -> str:
    """
    Get the preferred package manager for the current environment.

    Returns:
        Name of preferred package manager
    """
    managers = get_package_manager_info()

    # Prefer uv > poetry > pip
    if managers.get("uv", {}).get("available"):
        return "uv"
    elif managers.get("poetry", {}).get("available"):
        return "poetry"
    elif managers.get("pip", {}).get("available"):
        return "pip"
    else:
        return "pip"  # Default fallback
