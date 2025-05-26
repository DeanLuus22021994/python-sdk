# filepath: c:\Projects\python-sdk\setup\sequence.py
"""
Setup Sequence Management
Orchestrates the setup process for the MCP Python SDK
"""

import json
import sys
from typing import Any

from .environment import (
    check_required_paths,
    validate_python_version,
)
from .packages import get_packages_for_platform, normalize_package_name
from .vscode.extensions import create_vscode_extensions_config
from .vscode.launch import get_modern_launch_config

# Import VSCode functions directly from their modules
from .vscode.settings import (
    create_vscode_directory,
    get_modern_vscode_settings,
    should_create_settings_json,
)
from .vscode.tasks import get_modern_tasks_config


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
    paths_valid, path_results = check_required_paths()
    if paths_valid:
        print("✓ All required paths exist")
        for path_type, paths in path_results.items():
            for path_info in paths:
                if path_info.get("exists", False):
                    print(f"  ✓ {path_info['path']}")
                else:
                    print(f"  ⚠ {path_info['path']} (optional)")
    else:
        print("✗ Missing required project paths")
        success = False

    # Step 3: Configure VS Code workspace
    print("\nStep 3: Configuring VS Code workspace")
    try:
        # Ensure .vscode directory exists
        vscode_dir = create_vscode_directory()
        print(f"✓ VS Code directory: {vscode_dir}")

        # Configure settings.json
        settings_path = vscode_dir / "settings.json"
        if not settings_path.exists() or should_create_settings_json():
            settings_config = get_modern_vscode_settings()
            with open(settings_path, "w", encoding="utf-8") as f:
                json.dump(settings_config, f, indent=2)
            print("  - settings.json (Editor configuration)")

        # Configure launch.json
        launch_path = vscode_dir / "launch.json"
        if not launch_path.exists():
            launch_config = get_modern_launch_config()
            with open(launch_path, "w", encoding="utf-8") as f:
                json.dump(launch_config, f, indent=2)
            print("  - launch.json (Debug configurations)")

        tasks_path = vscode_dir / "tasks.json"
        if not tasks_path.exists():
            tasks_config = get_modern_tasks_config()
            with open(tasks_path, "w", encoding="utf-8") as f:
                json.dump(tasks_config, f, indent=2)
            print("  - tasks.json (Build and test tasks)")

        extensions_path = vscode_dir / "extensions.json"
        if not extensions_path.exists():
            extensions_config = create_vscode_extensions_config()
            with open(extensions_path, "w", encoding="utf-8") as f:
                json.dump(extensions_config, f, indent=2)
            print("  - extensions.json (Recommended extensions)")

    except Exception as e:
        print(f"✗ Failed to configure VS Code: {str(e)}")
        success = False

    # Step 4: Verify required packages
    print("\nChecking required packages:")
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
    try:
        # Import Docker functions
        from .docker import (
            check_required_images,
            configure_containers,
            configure_volumes,
            pull_required_images,
            validate_docker_environment,
        )

        print("\nStep 5: Configuring Docker environment")
        docker_valid, docker_msg = validate_docker_environment()
        if docker_valid:
            print(f"✓ {docker_msg}")

            # Configure Docker volumes
            volume_success = configure_volumes()
            if volume_success:
                print("✓ Docker volumes configured")
            else:
                print("⚠ Docker volume configuration failed")

            # Configure containers
            container_success = configure_containers()
            if container_success:
                print("✓ Docker containers configured")
            else:
                print("⚠ Docker container configuration failed")

            # Check required images
            images_present = check_required_images()
            if not images_present:
                print("ℹ Pulling required Docker images...")
                pull_success = pull_required_images()
                if pull_success:
                    print("✓ Required Docker images downloaded")
                else:
                    print("⚠ Failed to download some Docker images")

        else:
            print(f"ℹ Docker not available: {docker_msg}")

    except ImportError:
        print("\nℹ Docker setup not available (optional)")

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
            with open("SETUP_COMPLETE.md", "w", encoding="utf-8") as f:
                f.write("# Setup Complete\n\n")
                f.write("The MCP Python SDK setup has been completed successfully.\n")
                f.write("All required configurations have been created.\n")
        except Exception:
            pass  # Non-critical

    else:
        print("❌ Setup completed with errors")
        print("Please review the errors above and run setup again.")

    return success


if __name__ == "__main__":
    success = run_setup_sequence()
    sys.exit(0 if success else 1)
