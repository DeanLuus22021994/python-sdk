"""
Setup Module 1.2: Package Manager
Installs and verifies required packages
"""

import platform
import subprocess
import sys

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

PLATFORM_PACKAGES = {"uvloop": ["linux", "darwin"]}


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
    try:
        __import__(package.replace("-", "_"))
        return True, f"✓ {package} imports successfully"
    except ImportError as e:
        return False, f"✗ {package} import failed: {str(e)}"


def setup_packages() -> bool:
    """Install and verify all required packages."""
    print("📦 Setting up packages...")
    success = True
    current_platform = platform.system().lower()

    # Install main packages
    for package in REQUIRED_PACKAGES:
        installed, msg = install_package(package)
        print(f"  {msg}")
        if not installed:
            success = False

    # Platform-specific packages
    for package, supported_platforms in PLATFORM_PACKAGES.items():
        if current_platform in supported_platforms:
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

    for package, supported_platforms in PLATFORM_PACKAGES.items():
        if current_platform in supported_platforms:
            verified, msg = verify_import(package)
            print(f"  {msg}")
            if not verified:
                success = False

    return success