#!/usr/bin/env python3
"""
MCP Python SDK Setup
Simple entry point for development environment setup

Usage:
    python setup_environment.py
"""
import os
import sys
from pathlib import Path

# Add the project root to the path so imports work correctly
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Create __init__.py if it doesn't exist to make setup a proper package
setup_init = project_root / "setup" / "__init__.py"
if not setup_init.exists():
    with open(setup_init, "w") as f:
        f.write('"""MCP Python SDK Setup Package"""')

# Create host/__init__.py if it doesn't exist
host_init = project_root / "setup" / "host" / "__init__.py"
if not os.path.exists(host_init.parent):
    os.makedirs(host_init.parent, exist_ok=True)
if not host_init.exists():
    with open(host_init, "w") as f:
        f.write('"""MCP Python SDK Setup Host Package"""\n\n')
        f.write("from ._1_1_env_validator import validate_environment\n")
        f.write("from ._1_2_package_manager import setup_packages\n")
        f.write("from ._1_3_sdk_validator import validate_sdk\n")
        f.write("from ._1_4_vscode_config import setup_vscode_config\n\n")
        f.write("__all__ = [\n")
        f.write('    "validate_environment",\n')
        f.write('    "setup_packages",\n')
        f.write('    "validate_sdk",\n')
        f.write('    "setup_vscode_config",\n')
        f.write("]\n")

if __name__ == "__main__":
    # Use a direct import instead of a package import
    import setup.main

    sys.exit(setup.main.main())
