"""
Setup Module 1.2: Package Manager
Installs and verifies required packages
"""

import platform
import subprocess
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

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

    def get_platform_package_status():
        current_platform = platform.system().lower()
        return {"uvloop": current_platform in ["linux", "darwin"]}

    def normalize_package_name(package):
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
    platform_status = get_platform_package_status()

    # Install main packages
    for package in REQUIRED_PACKAGES:
        installed, msg = install_package(package)
        print(f"  {msg}")
        if not installed:
            success = False

    # Install platform-specific packages
    for package, should_install in platform_status.items():
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

    for package, should_install in platform_status.items():
        if should_install:
            verified, msg = verify_import(package)
            print(f"  {msg}")
            if not verified:
                success = False

    return success
