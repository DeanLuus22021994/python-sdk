"""Package management module for Python SDK setup."""

import platform
import subprocess
import sys

try:
    from setup.packages import (
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
        """Get platform-specific package requirements."""
        current_platform = platform.system().lower()
        return {"uvloop": current_platform in ["linux", "darwin"]}

    def normalize_package_name(package: str) -> str:
        """Normalize package name for import."""
        return package.replace("-", "_")


def install_package(package: str) -> tuple[bool, str]:
    """Install a single package using pip."""
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", package],
            capture_output=True,
            text=True,
            check=True,
        )
        return True, f"✓ Installed {package}"
    except subprocess.CalledProcessError as e:
        return False, f"✗ Failed to install {package}: {e.stderr.strip()}"


def verify_import(package: str) -> tuple[bool, str]:
    """Verify a package can be imported."""
    module_name = normalize_package_name(package)
    try:
        __import__(module_name)
        return True, f"✓ {package} imports successfully"
    except ImportError as e:
        return False, f"✗ {package} import failed: {str(e)}"


def setup_packages() -> bool:
    """Install and verify all required packages."""
    print("📦 Setting up packages...")
    success = True
    current_platform = platform.system().lower()
    platform_packages = get_platform_package_status()

    # Install main packages
    for package in REQUIRED_PACKAGES:
        installed, msg = install_package(package)
        print(f"  {msg}")
        if not installed:
            success = False

    # Install platform-specific packages
    for package, should_install in platform_packages.items():
        if should_install:
            installed, msg = install_package(package)
            print(f"  {msg}")
            if not installed:
                success = False
        else:
            print(f"  ⚠ {package} skipped (not for {current_platform})")

    if not success:
        return False

    # Verify imports
    print("\n🔍 Verifying imports...")
    for package in REQUIRED_PACKAGES:
        verified, msg = verify_import(package)
        print(f"  {msg}")
        if not verified:
            success = False

    # Verify platform-specific packages
    for package, should_install in platform_packages.items():
        if should_install:
            verified, msg = verify_import(package)
            print(f"  {msg}")
            if not verified:
                success = False

    return success


def check_package_availability(package: str) -> bool:
    """Check if a package is available without installing."""
    try:
        __import__(normalize_package_name(package))
        return True
    except ImportError:
        return False


def get_installed_packages() -> list[str]:
    """Get list of currently installed packages."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--format=freeze"],
            capture_output=True,
            text=True,
            check=True,
        )
        return [
            line.split("==")[0]
            for line in result.stdout.strip().split("\n")
            if "==" in line
        ]
    except subprocess.CalledProcessError:
        return []
