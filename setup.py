#!/usr/bin/env python3
"""
MCP Python SDK Setup
Modern, idempotent development environment setup with containerization support.

Usage:
    python setup.py [--docker] [--verbose]

Features:
    - Host-based development setup
    - Docker containerization support
    - Idempotent operations
    - Performance optimizations
    - Clean architecture following SOLID principles
"""

import sys
from pathlib import Path
from typing import NoReturn

# Ensure project root is in path for proper imports
PROJECT_ROOT = Path(__file__).parent.resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def ensure_package_structure() -> None:
    """Ensure all package directories have proper __init__.py files."""
    package_dirs = [
        PROJECT_ROOT / "setup",
        PROJECT_ROOT / "setup" / "environment",
        PROJECT_ROOT / "setup" / "host",
        PROJECT_ROOT / "setup" / "docker",
    ]

    for package_dir in package_dirs:
        package_dir.mkdir(parents=True, exist_ok=True)
        init_file = package_dir / "__init__.py"
        if not init_file.exists():
            init_file.touch()


def main() -> NoReturn:
    """Entry point for setup process."""
    ensure_package_structure()

    try:
        from setup.main import main as setup_main

        sys.exit(setup_main())
    except ImportError as e:
        print(f"Setup import failed: {e}")
        print(
            "Ensure all dependencies are installed and the project structure is correct."
        )
        sys.exit(1)
    except Exception as e:
        print(f"Setup failed with unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
