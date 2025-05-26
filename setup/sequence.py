"""
Setup Sequence Controller
Provides the main setup sequence orchestration and coordination
"""

import sys
from pathlib import Path

# Add the project root to the path so imports work correctly
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from setup.host import (
        setup_packages,
        setup_vscode_config,
        validate_environment,
        validate_sdk,
    )
except ImportError:
    # Fallback to relative import if absolute import fails
    from .host import (
        setup_packages,
        setup_vscode_config,
        validate_environment,
        validate_sdk,
    )


def run_setup_sequence() -> bool:
    """
    Runs the full setup sequence.
    Returns True if all steps succeed; otherwise False.
    """
    print("⏳ Starting setup sequence...")

    # Environment validation
    if not validate_environment():
        return False

    # VS Code setup
    if not setup_vscode_config():
        return False

    # Package installation
    if not setup_packages():
        return False

    # SDK validation
    if not validate_sdk():
        return False

    return True
