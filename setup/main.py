"""
MCP Python SDK Setup - Main Entry Point
Orchestrates the complete setup process
"""

import sys
from pathlib import Path


def get_module_functions():
    """Import modules after adding path to avoid import issues."""
    # Add project root to path for imports
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

    # Import setup modules
    from setup.env_validator import validate_environment
    from setup.package_manager import setup_packages
    from setup.sdk_validator import validate_sdk
    from setup.vscode_config import setup_vscode_config

    return validate_environment, setup_packages, validate_sdk, setup_vscode_config


def print_header():
    """Print setup header."""
    print("\n" + "=" * 60)
    print("🐍 MCP Python SDK Setup")
    print("Preparing development environment...")
    print("=" * 60)


def print_footer(success: bool):
    """Print setup results."""
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

    # Get imported functions
    validate_environment, setup_packages, validate_sdk, setup_vscode_config = (
        get_module_functions()
    )

    try:
        # Step 1: Validate environment
        if not validate_environment():
            print_footer(False)
            return 1

        # Step 2: Setup VS Code configuration
        if not setup_vscode_config():
            print_footer(False)
            return 1

        # Step 3: Install and verify packages
        if not setup_packages():
            print_footer(False)
            return 1

        # Step 4: Validate SDK
        if not validate_sdk():
            print_footer(False)
            return 1

        print_footer(True)
        return 0

    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        return 130
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
