"""
Python Environment Validation
Modern Python version and environment validation utilities with performance optimization.
"""

import platform
import subprocess
import sys
from pathlib import Path
from typing import Any

from .constants import MIN_PYTHON_VERSION, RECOMMENDED_PYTHON_VERSION, PythonVersion
from .path_utils import get_project_root


def get_python_version_info() -> PythonVersion:
    """
    Get the current Python version as a structured type.

    Returns:
        PythonVersion: Named tuple with major and minor version numbers
    """
    return PythonVersion(sys.version_info.major, sys.version_info.minor)


def validate_python_version() -> tuple[bool, str]:
    """
    Validate that the current Python version meets requirements.

    Returns:
        Tuple of (is_valid, status_message)
    """
    current_version = get_python_version_info()

    if current_version < MIN_PYTHON_VERSION:
        return False, (
            f"Python {current_version} is too old. "
            f"Minimum required: {MIN_PYTHON_VERSION}, "
            f"Recommended: {RECOMMENDED_PYTHON_VERSION}"
        )

    if current_version < RECOMMENDED_PYTHON_VERSION:
        return True, (
            f"Python {current_version} meets minimum requirements "
            f"but {RECOMMENDED_PYTHON_VERSION} is recommended for optimal performance"
        )

    return True, f"Python {current_version} meets all requirements"


def get_environment_info() -> dict[str, Any]:
    """
    Get comprehensive Python environment information.

    Returns:
        Dictionary containing environment details
    """
    current_version = get_python_version_info()

    # Get Python executable information
    executable_info = {
        "executable": sys.executable,
        "executable_path": Path(sys.executable).resolve(),
        "version": str(current_version),
        "version_full": sys.version,
        "implementation": platform.python_implementation(),
        "compiler": platform.python_compiler(),
    }

    # Platform information
    platform_info = {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "architecture": platform.architecture()[0],
    }

    # Virtual environment detection
    venv_info = get_virtual_environment_info()

    # Package management information
    package_info = get_package_manager_info()

    return {
        "python": executable_info,
        "platform": platform_info,
        "virtual_environment": venv_info,
        "package_management": package_info,
        "validation": {
            "meets_minimum": current_version >= MIN_PYTHON_VERSION,
            "meets_recommended": current_version >= RECOMMENDED_PYTHON_VERSION,
            "is_supported": True,  # Could add upper bound checking here
        },
    }


def get_virtual_environment_info() -> dict[str, Any]:
    """
    Detect and provide information about virtual environment.

    Returns:
        Dictionary with virtual environment details
    """
    # Check for virtual environment indicators
    in_venv = hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )

    venv_info: dict[str, Any] = {
        "active": in_venv,
        "type": None,
        "path": None,
        "name": None,
    }

    if in_venv:
        # Determine virtual environment type and details
        venv_path = Path(sys.prefix)
        venv_info["path"] = str(venv_path)
        venv_info["name"] = venv_path.name

        # Detect environment type
        if (venv_path / "conda-meta").exists():
            venv_info["type"] = "conda"
        elif (venv_path / "pyvenv.cfg").exists():
            venv_info["type"] = "venv"
        elif "virtualenv" in str(venv_path):
            venv_info["type"] = "virtualenv"
        else:
            venv_info["type"] = "unknown"

    return venv_info


def get_package_manager_info() -> dict[str, Any]:
    """
    Get information about available package managers.

    Returns:
        Dictionary with package manager availability and versions
    """
    managers = {}

    # Check for pip
    try:
        import pip

        managers["pip"] = {
            "available": True,
            "version": pip.__version__,
            "executable": sys.executable + " -m pip",
        }
    except ImportError:
        managers["pip"] = {"available": False}

    # Check for conda
    try:
        result = subprocess.run(
            ["conda", "--version"], capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            managers["conda"] = {
                "available": True,
                "version": result.stdout.strip().split()[-1],
                "executable": "conda",
            }
    except (subprocess.TimeoutExpired, FileNotFoundError):
        managers["conda"] = {"available": False}

    # Check for uv (modern Python package manager)
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

    return managers


def check_python_compatibility() -> tuple[bool, list[str]]:
    """
    Check Python compatibility for specific features used in the project.

    Returns:
        Tuple of (is_compatible, compatibility_issues)
    """
    issues = []
    current_version = get_python_version_info()

    # Check for modern typing features (PEP 585)
    if current_version < PythonVersion(3, 9):
        issues.append("Modern typing features (dict, list) require Python 3.9+")

    # Check for structural pattern matching
    if current_version < PythonVersion(3, 10):
        issues.append("Structural pattern matching requires Python 3.10+")

    # Check for performance improvements
    if current_version < PythonVersion(3, 11):
        issues.append("Significant performance improvements available in Python 3.11+")

    return len(issues) == 0, issues


def is_development_environment() -> bool:
    """
    Determine if we're running in a development environment.

    Returns:
        True if this appears to be a development environment
    """
    try:
        project_root = get_project_root()

        # Check for development indicators
        dev_indicators = [
            ".git",
            "pyproject.toml",
            "setup.py",
            ".vscode",
            ".devcontainer",
        ]

        return any((project_root / indicator).exists() for indicator in dev_indicators)

    except Exception:
        return False


def check_virtual_environment() -> tuple[bool, str]:
    """
    Check if a virtual environment is active and properly configured.

    Returns:
        Tuple of (is_valid, status_message)
    """
    venv_info = get_virtual_environment_info()

    if not venv_info["active"]:
        return False, (
            "No virtual environment detected. "
            "Consider using 'python -m venv .venv' or conda."
        )

    venv_type = venv_info.get("type", "unknown")
    venv_path = venv_info.get("path", "unknown")

    return True, f"Virtual environment active: {venv_type} at {venv_path}"


def validate_python_environment() -> dict[str, Any]:
    """
    Comprehensive Python environment validation.

    Returns:
        Dictionary containing validation results and recommendations
    """
    results = {
        "valid": True,
        "warnings": [],
        "errors": [],
        "recommendations": [],
        "environment_info": {},
    }

    # Validate Python version
    version_valid, version_msg = validate_python_version()
    if not version_valid:
        results["valid"] = False
        results["errors"].append(version_msg)
    elif "recommended" in version_msg.lower():
        results["warnings"].append(version_msg)

    # Check virtual environment
    venv_valid, venv_msg = check_virtual_environment()
    if not venv_valid:
        results["warnings"].append(venv_msg)
        results["recommendations"].append(
            "Set up a virtual environment for better dependency isolation"
        )

    # Check compatibility
    compat_valid, compat_issues = check_python_compatibility()
    if not compat_valid:
        results["warnings"].extend(compat_issues)

    # Add environment information
    results["environment_info"] = get_environment_info()

    # Development environment check
    if is_development_environment():
        results["recommendations"].append(
            "Development environment detected - ensure all dev dependencies are installed"
        )

    return results
