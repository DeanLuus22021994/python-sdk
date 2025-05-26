#!/usr/bin/env python3
"""
MCP Python SDK Setup
Simple entry point for development environment setup

Usage:
    python setup_environment.py
"""
import sys
from pathlib import Path

# Add the setup module to path
setup_path = Path(__file__).parent / "setup"
sys.path.insert(0, str(setup_path.parent))

if __name__ == "__main__":
    from setup.main import main

    sys.exit(main())
