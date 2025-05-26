"""
Setup Module 1.1: Environment Validator
Validates Python version and basic project structure
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from setup.environment import (
        validate_python_version,
        check_required_paths,
        get_project_root,
    )
except ImportError:
    # Fallback functions if import fails
    def validate_python_version():
        min_version = (3, 10)
        current = sys.version_info[:2]
        if current >= min_version:
            msg = f"✓ Python {current[0]}.{current[1]} (meets {min_version[0]}.{min_version[1]})"
            return True, msg
        msg = f"✗ Python {current[0]}.{current[1]} (requires {min_version[0]}.{min_version[1]}+)"
        return False, msg

    def check_required_paths():
        project_root = Path(__file__).parent.parent.parent
        required_paths = ["src/mcp", "pyproject.toml", ".vscode"]
        missing = []
        for path in required_paths:
            if not (project_root / path).exists():
                missing.append(path)
        return len(missing) == 0, missing

    def get_project_root():
        return Path(__file__).parent.parent.parent


def validate_environment() -> bool:
    """Main environment validation entry point."""
    print("🔍 Validating Environment...")

    # Validate Python version
    python_valid, python_msg = validate_python_version()
    print(f"  {python_msg}")

    # Validate project structure
    structure_valid, missing_paths = check_required_paths()
    if structure_valid:
        print("  ✓ Project structure validated")
    else:
        print(f"  ✗ Missing required paths: {', '.join(missing_paths)}")

    return python_valid and structure_valid
