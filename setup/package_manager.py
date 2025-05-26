"""
Setup Module 02: Package Manager
Handles installation and verification of required packages
"""

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
    "uvloop",
]


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

    # Install packages
    for package in REQUIRED_PACKAGES:
        installed, message = install_package(package)
        print(f"  {message}")
        if not installed:
            success = False

    if not success:
        return False

    # Verify imports
    print("\n🔍 Verifying imports...")
    for package in REQUIRED_PACKAGES:
        verified, message = verify_import(package)
        print(f"  {message}")
        if not verified:
            success = False

    return success
