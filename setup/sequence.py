"""
Setup Module 05: Additional Setup Sequence
Provides future-proofing and extra steps for advanced setup if needed
"""

# Use relative import for intra-package references
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
