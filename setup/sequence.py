"""
Setup Sequence Management
Orchestrates the setup process for the MCP Python SDK
"""

import importlib.util
import sys
from pathlib import Path
from typing import Any

from .environment import (
    check_required_paths,
    validate_python_version,
)
from .packages import get_packages_for_platform, normalize_package_name


class SetupOrchestrator:
    """
    Main orchestrator for the MCP Python SDK setup process.

    Follows the Single Responsibility Principle by coordinating
    different setup components without implementing their logic.
    """

    def __init__(self, verbose: bool = False) -> None:
        self.verbose = verbose
        self._setup_results: dict[str, Any] = {}

    def run_complete_setup(self) -> bool:
        """
        Execute the complete setup sequence.

        Returns:
            True if all setup steps completed successfully
        """
        return run_setup_sequence()

    def get_setup_results(self) -> dict[str, Any]:
        """Get detailed results from the setup process."""
        return self._setup_results.copy()


def run_setup_sequence() -> bool:
    """
    Run the complete setup sequence for the MCP Python SDK.

    Returns:
        True if all setup steps completed successfully
    """
    print("🚀 Starting MCP Python SDK Setup")
    print("=" * 50)

    success = True

    # Step 1: Validate Python version
    print("\nStep 1: Validating Python environment")
    is_valid, message = validate_python_version()
    if is_valid:
        print(f"✓ {message}")
    else:
        print(f"✗ {message}")
        success = False

    # Step 2: Check required project structure
    print("\nStep 2: Validating project structure")
    paths_valid, missing_paths = check_required_paths()
    if paths_valid:
        print("✓ All required paths exist")
    else:
        print("✗ Missing required project paths")
        for path in missing_paths:
            print(f"  ✗ {path}")
        success = False

    # Step 3: Configure VS Code workspace
    print("\nStep 3: Configuring VS Code workspace")
    try:
        from .environment import get_project_root
        from .vscode.integration import VSCodeIntegrationManager

        project_root = get_project_root()
        vscode_manager = VSCodeIntegrationManager(project_root)

        vscode_success = vscode_manager.create_workspace_configuration()
        if vscode_success:
            print("✓ VS Code workspace configured successfully")
        else:
            print("✗ Failed to configure VS Code workspace")
            success = False

    except Exception as e:
        print(f"✗ Failed to configure VS Code: {str(e)}")
        success = False

    # Step 4: Verify required packages
    print("\nStep 4: Checking required packages")
    packages = get_packages_for_platform(include_dev=True)

    for package in packages:
        try:
            # Simple check using importlib to see if package can be imported
            module_name = normalize_package_name(package)
            __import__(module_name)
            print(f"✓ {package} is installed")
        except ImportError:
            print(f"✗ {package} is not installed or cannot be imported")
            print(f"  Install with: pip install {package}")
            success = False

    # Step 5: Configure Docker environment (if available)
    docker_spec = importlib.util.find_spec("setup.docker")
    if docker_spec is not None:
        try:
            from .docker import (
                configure_containers,
                configure_volumes,
                validate_docker_environment_compat,
            )

            print("\nStep 5: Configuring Docker environment")
            docker_valid, docker_msg = validate_docker_environment_compat()
            if docker_valid:
                print(f"✓ {docker_msg}")

                # Configure Docker components
                volumes_success = configure_volumes()
                containers_success = configure_containers()

                if volumes_success and containers_success:
                    print("✓ Docker environment configured")
                else:
                    print("⚠ Docker configuration incomplete")
            else:
                print(f"⚠ {docker_msg}")

        except ImportError:
            print("\nℹ Docker setup not available (optional)")
    else:
        print("\nℹ Docker setup module not found (optional)")

    # Summary
    print("\n" + "=" * 50)
    if success:
        print("🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Install dependencies: uv sync")
        print("2. Run tests: uv run pytest")
        print("3. Start development server: uv run python -m mcp.server")

        # Write completion marker
        try:
            project_root = Path.cwd()
            marker_file = project_root / ".setup_complete"
            marker_file.write_text("Setup completed successfully")
        except Exception:
            pass  # Non-critical

    else:
        print("❌ Setup completed with errors")
        print("Please review the errors above and run setup again.")

    return success


if __name__ == "__main__":
    success = run_setup_sequence()
    sys.exit(0 if success else 1)
