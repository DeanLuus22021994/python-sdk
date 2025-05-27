"""
MCP Python SDK Setup - Package Entry Point

Modern, modular setup system entry point following standardization principles.
Enables running the setup system via: python -m setup
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

# Robust import handling for package execution
_setup_path = Path(__file__).parent
if str(_setup_path.parent) not in sys.path:
    sys.path.insert(0, str(_setup_path.parent))

if TYPE_CHECKING:
    from .orchestrator import ModernSetupOrchestrator
    from .typings.enums import SetupMode
else:
    ModernSetupOrchestrator = None
    SetupMode = None

    # Try multiple import strategies following DRY principle
    try:
        from setup.orchestrator import ModernSetupOrchestrator
        from setup.typings.enums import SetupMode
    except ImportError:
        try:
            from .orchestrator import ModernSetupOrchestrator
            from .typings.enums import SetupMode
        except ImportError:
            # Create fallback classes
            class MockSetupMode:
                DEVELOPMENT = "development"
                PRODUCTION = "production"
                DOCKER = "docker"
                HOST = "host"

            SetupMode = MockSetupMode


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="MCP Python SDK Setup System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m setup                           # Development mode setup
  python -m setup --mode production         # Production mode setup
  python -m setup --mode docker             # Docker mode setup
  python -m setup --validate-only           # Validation only
  python -m setup --verbose                 # Verbose output
        """,
    )

    # Handle both enum and fallback SetupMode
    if hasattr(SetupMode, "__members__"):
        choices = list(SetupMode.__members__.keys())
        default = SetupMode.DEVELOPMENT.value
    else:
        choices = ["development", "production", "docker", "host"]
        default = "development"

    parser.add_argument(
        "--mode",
        type=str,
        choices=choices,
        default=default,
        help="Setup mode to use (default: %(default)s)",
        metavar="MODE",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate environment, don't perform setup",
    )

    return parser


async def handle_validation_only(orchestrator: Any, verbose: bool) -> int:
    """Handle validation-only mode."""
    if verbose:
        print("🔍 Validating environment...")

    try:
        validation_result = await orchestrator.validate_environment()

        if validation_result.is_valid:
            print("✅ Environment validation passed")
            return 0
        else:
            print("❌ Environment validation failed")
            if validation_result.errors:
                for error in validation_result.errors:
                    print(f"  Error: {error}")
            return 1
    except Exception as e:
        print(f"❌ Validation failed with error: {e}")
        return 1


async def handle_setup_mode(orchestrator: Any, mode: Any, verbose: bool) -> int:
    """Handle setup mode execution."""
    if verbose:
        print(f"🚀 Starting setup in {mode} mode...")

    try:
        result = await orchestrator.orchestrate_complete_setup(mode)

        if result.success:
            print("✅ Setup completed successfully")
            return 0
        else:
            print("❌ Setup failed")
            if result.errors:
                for error in result.errors:
                    print(f"  Error: {error}")
            return 1
    except Exception as e:
        print(f"❌ Setup failed with error: {e}")
        return 1


async def main() -> int:
    """Main entry point for the setup system."""
    parser = create_argument_parser()
    args = parser.parse_args()

    if ModernSetupOrchestrator is None:
        print("❌ Setup orchestrator not available")
        return 1

    # Create orchestrator
    orchestrator = ModernSetupOrchestrator(verbose=args.verbose)

    # Handle different execution modes
    if args.validate_only:
        return await handle_validation_only(orchestrator, args.verbose)
    else:
        # Convert string mode to enum if available
        if hasattr(SetupMode, args.mode.upper()):
            mode = getattr(SetupMode, args.mode.upper())
        else:
            mode = args.mode

        return await handle_setup_mode(orchestrator, mode, args.verbose)


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
