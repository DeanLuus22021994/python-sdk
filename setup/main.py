"""
Setup Module 2.1: Main Orchestration
Coordinates the entire setup process
"""

from .sequence import run_setup_sequence


def print_header() -> None:
    print("\n" + "=" * 60)
    print("🐍 MCP Python SDK Setup")
    print("Preparing development environment...")
    print("=" * 60)


def print_footer(success: bool) -> None:
    print("\n" + "=" * 60)
    if success:
        print("✅ Setup completed successfully!")
        print("Your MCP Python SDK development environment is ready.")
        print("\nNext steps:")
        print("1. Open VS Code Insiders")
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
        success = run_setup_sequence()
        print_footer(success)
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        return 130
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {str(e)}")
        return 1
