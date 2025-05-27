"""
Main Setup Orchestration
Coordinates the entire setup process using the modern validation framework.
"""

import argparse
import sys
import time
from pathlib import Path

# Add the project root to the path so imports work correctly
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from setup.sequence import ModernSetupOrchestrator
    from setup.typings import LogLevel, SetupMode
except ImportError:
    # Fallback to direct import if package import fails
    from .sequence import ModernSetupOrchestrator
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
        print("🚀 Your development environment is ready.")
    else:
        print("❌ Setup failed!")
        print("🔧 Please check the errors above and try again.")
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
    """Main setup orchestrator using modern validation framework."""
    start_time = time.time()
    args = parse_args()
    verbose = args.verbose

    print_header()

    try:
        # Convert string mode to enum
        mode_map = {
            "host": SetupMode.HOST,
            "docker": SetupMode.DOCKER,
            "hybrid": SetupMode.HYBRID,
        }
        setup_mode = mode_map.get(args.mode, SetupMode.HOST)

        # Create modern orchestrator
        workspace_root = Path.cwd()
        orchestrator = ModernSetupOrchestrator(
            workspace_root=workspace_root,
            mode=setup_mode,
            verbose=verbose,
        )

        log_message(LogLevel.INFO, f"Starting setup in {args.mode} mode", verbose)
        log_message(LogLevel.INFO, f"Workspace: {workspace_root}", verbose)

        # Run complete setup
        success = orchestrator.run_complete_setup()

        # Print results
        elapsed_time = time.time() - start_time
        log_message(
            LogLevel.INFO, f"Setup completed in {elapsed_time:.2f} seconds", verbose
        )

        print_footer(success)
        return 0 if success else 1

    except KeyboardInterrupt:
        log_message(LogLevel.WARNING, "Setup interrupted by user")
        return 1
    except Exception as e:
        log_message(LogLevel.ERROR, f"Setup failed with error: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
