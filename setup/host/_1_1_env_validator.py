"""
Setup Module 1.1: Environment Validator
Validates Python version and basic project structure
"""

import sys
from pathlib import Path


def validate_python_version() -> tuple[bool, str]:
    """Validate Python version meets minimum requirements."""
    min_version = (3, 10)
    current = sys.version_info[:2]
    if current >= min_version:
        msg = f"✓ Python {current[0]}.{current[1]} (meets {min_version[0]}.{min_version[1]})"
        return True, msg
    msg = f"✗ Python {current[0]}.{current[1]} (requires {min_version[0]}.{min_version[1]}+)"
    return False, msg


def validate_project_structure() -> tuple[bool, str]:
    """Validate required project structure exists."""
    project_root = Path(__file__).parent.parent.parent
    required_paths = ["src/mcp", "pyproject.toml", ".vscode"]
    for path in required_paths:
        if not (project_root / path).exists():
            return False, f"✗ Missing required path: {path}"
    return True, "✓ Project structure validated"


def validate_environment() -> bool:
    """Main environment validation entry point."""
    print("🔍 Validating Environment...")
    checks = [validate_python_version(), validate_project_structure()]
    success = True
    for passed, message in checks:
        print(f"  {message}")
        if not passed:
            success = False
    return success
