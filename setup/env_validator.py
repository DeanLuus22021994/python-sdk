"""
Setup Module 01: Core Environment Validation
Validates Python version and environment compatibility
"""

import sys
from pathlib import Path


def validate_python_version() -> tuple[bool, str]:
    """Validate Python version meets minimum requirements."""
    min_version = (3, 10)
    current = sys.version_info[:2]

    if current >= min_version:
        version_msg = f"✓ Python {current[0]}.{current[1]}"
        min_msg = f"(meets minimum {min_version[0]}.{min_version[1]})"
        return True, f"{version_msg} {min_msg}"

    current_msg = f"✗ Python {current[0]}.{current[1]}"
    required_msg = f"(requires {min_version[0]}.{min_version[1]}+)"
    return False, f"{current_msg} {required_msg}"


def validate_project_structure() -> tuple[bool, str]:
    """Validate required project structure exists."""
    project_root = Path(__file__).parent.parent
    required_paths = ["src/mcp", "pyproject.toml", ".vscode"]

    for path in required_paths:
        if not (project_root / path).exists():
            return False, f"✗ Missing required path: {path}"

    return True, "✓ Project structure validated"


def validate_environment() -> bool:
    """Main environment validation."""
    print("🔍 Validating Environment...")

    checks = [validate_python_version(), validate_project_structure()]

    success = True
    for check_passed, message in checks:
        print(f"  {message}")
        if not check_passed:
            success = False

    return success
