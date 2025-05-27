#!/usr/bin/env python3
"""
MCP Python SDK Setup
Modern, idempotent development environment setup with containerization support.

Usage:
    python setup.py [--mode MODE] [--workspace PATH] [--verbose] [--validate-only]

Features:
    - Host-based development setup
    - Docker containerization support
    - Idempotent operations
    - Performance optimizations
    - Clean architecture following SOLID principles
"""

import asyncio
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
        PROJECT_ROOT / "setup" / "vscode",
        PROJECT_ROOT / "setup" / "validation",
        PROJECT_ROOT / "setup" / "typings",
    ]

    for package_dir in package_dirs:
        package_dir.mkdir(parents=True, exist_ok=True)
        init_file = package_dir / "__init__.py"
        if not init_file.exists():
            init_file.touch()


async def run_setup() -> int:
    """Run the async setup process."""
    try:
        # Try to use the main async function from __main__.py first
        try:
            from setup.__main__ import main as async_main

            return await async_main()
        except ImportError:
            # Fallback to the orchestrator directly
            from setup.orchestrator import ModernSetupOrchestrator

            print("🚀 Starting MCP Python SDK Setup...")
            orchestrator = ModernSetupOrchestrator(verbose=True)

            # Run setup orchestration
            result = orchestrator.orchestrate_setup()

            if result:
                print("✅ Setup completed successfully!")
                return 0
            else:
                print("❌ Setup failed. Check logs for details.")
                return 1

    except ImportError as e:
        print(f"Setup import failed: {e}")
        print(
            "Ensure all dependencies are installed and the project structure is correct."
        )
        return 1
    except Exception as e:
        print(f"Setup failed with unexpected error: {e}")
        return 1


def main() -> NoReturn:
    """Entry point for setup process."""
    ensure_package_structure()

    try:
        # Run the async setup process
        exit_code = asyncio.run(run_setup())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️ Setup interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"Setup failed with unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
