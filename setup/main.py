"""
Main setup entry point for the MCP Python SDK.
Provides CLI interface for setup operations.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from .orchestrator import ModernSetupOrchestrator
from .typings import SetupMode


async def main() -> int:
    """Main setup function."""
    parser = argparse.ArgumentParser(
        description="MCP Python SDK Setup System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--mode",
        type=str,
        choices=[mode.value for mode in SetupMode],
        default=SetupMode.DEVELOPMENT.value,
        help="Setup mode to use",
    )

    parser.add_argument(
        "--workspace",
        type=Path,
        help="Workspace root directory",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output",
    )

    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate environment, don't perform setup",
    )

    args = parser.parse_args()

    try:
        mode = SetupMode(args.mode)
        orchestrator = ModernSetupOrchestrator(
            workspace_root=args.workspace,
            verbose=args.verbose,
        )

        if args.validate_only:
            print("🔍 Validating environment...")
            validation_result = await orchestrator.validate_environment()

            if validation_result.is_valid:
                print("✅ Environment validation passed")
                return 0
            else:
                print("❌ Environment validation failed")
                for error in validation_result.errors:
                    print(f"  • {error}")
                return 1
        else:
            print(f"🚀 Starting {mode.value} setup...")
            result = await orchestrator.orchestrate_complete_setup(mode)

            if result.success:
                print("✅ Setup completed successfully")
                return 0
            else:
                print("❌ Setup failed")
                for error in result.errors:
                    print(f"  • {error}")
                return 1

    except KeyboardInterrupt:
        print("\n⚠️ Setup interrupted by user")
        return 130
    except Exception as e:
        print(f"❌ Setup failed with error: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
