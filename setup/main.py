"""
Main Setup Orchestration
Coordinates the entire setup process
"""

import sys
from pathlib import Path

# Add the project root to the path so imports work correctly
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from setup import sequence
except ImportError:
    # Fallback to direct import if package import fails
    from . import sequence


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


def main() -> int:
    """Main setup orchestrator."""
    print_header()
    try:
        success = sequence.run_setup_sequence()
        print_footer(success)
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        return 130
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
