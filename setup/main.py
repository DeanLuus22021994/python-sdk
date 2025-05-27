"""
Main Setup Orchestration
Coordinates the entire setup process
"""

import argparse
import sys
import time
from pathlib import Path

# Add the project root to the path so imports work correctly
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from setup import sequence
    from setup.typings import LogLevel, SetupMode
except ImportError:
    # Fallback to direct import if package import fails
    from . import sequence
    from .typings import LogLevel, SetupMode


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="MCP Python SDK Setup")
    parser.add_argument(
        "--mode",
        choices=["host", "docker", "hybrid"],
        default="host",
        help="Setup mode (default: host)",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument(
        "--skip-vscode", action="store_true", help="Skip VS Code configuration"
    )
    parser.add_argument(
        "--skip-docker", action="store_true", help="Skip Docker configuration"
    )
    parser.add_argument(
        "--log-level",
        choices=["debug", "info", "warning", "error"],
        default="info",
        help="Set logging level (default: info)",
    )
    return parser.parse_args()


def print_header() -> None:
    """Print setup header information."""
    print("\n" + "=" * 60)
    print("🐍 MCP Python SDK Setup")
    print("Preparing development environment...")
    print("=" * 60)


def print_footer(success: bool) -> None:
    """Print setup completion footer."""
    print("\n" + "=" * 60)
    if success:
        print("✅ Setup completed successfully!")
        print("Your MCP Python SDK development environment is ready.")
        print("\nNext steps:")
        print("1. Open VS Code")
        print("2. Open this project folder")
        print("3. Start developing!")
    else:
        print("❌ Setup failed!")
        print("Please review the errors above and try again.")
    print("=" * 60 + "\n")


def log_message(level: LogLevel, message: str, verbose: bool = False) -> None:
    """
    Log a message with the appropriate level.

    Args:
        level: Log level
        message: Message to log
        verbose: Whether to show debug messages
    """
    if level == LogLevel.DEBUG and not verbose:
        return

    level_prefixes = {
        LogLevel.DEBUG: "🔍 DEBUG:",
        LogLevel.INFO: "ℹ️ INFO:",
        LogLevel.WARNING: "⚠️ WARNING:",
        LogLevel.ERROR: "❌ ERROR:",
    }

    prefix = level_prefixes.get(level, "")
    print(f"{prefix} {message}")


def main() -> int:
    """Main setup orchestrator."""
    start_time = time.time()
    args = parse_args()
    verbose = args.verbose

    print_header()
    try:
        # Set up setup mode
        mode = SetupMode(args.mode)
        log_message(LogLevel.INFO, f"Running in {mode.value} mode", verbose)

        success = sequence.run_setup_sequence()

        elapsed_time = time.time() - start_time
        log_message(
            LogLevel.INFO, f"Setup completed in {elapsed_time:.2f} seconds", verbose
        )

        print_footer(success)
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        return 130
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {str(e)}")
        if verbose:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
