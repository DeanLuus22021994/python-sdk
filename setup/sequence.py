"""
Setup Sequence Management
Orchestrates the setup process for the MCP Python SDK
"""

import sys
from pathlib import Path


def run_setup_sequence() -> bool:
    """
    Run the complete setup sequence for the MCP Python SDK.

    This function orchestrates the entire setup process:
    1. Validate the Python environment
    2. Check required project structure
    3. Configure VS Code settings
    4. Ensure dependencies are installed

    Returns:
        bool: True if setup completed successfully, False otherwise
    """
    # Add current directory to path to ensure imports work
    sys.path.insert(0, str(Path(__file__).parent.parent))

    # Now import from setup packages
    from setup.environment import (
        check_required_paths,
        create_vscode_directory,
        get_modern_vscode_settings,
        should_create_settings_json,
        validate_python_version,
    )
    from setup.packages import get_packages_for_platform

    success = True

    # Step 1: Validate Python version
    python_valid, python_message = validate_python_version()
    print(f"Checking Python version: {python_message}")
    if not python_valid:
        return False

    # Step 2: Check project structure
    paths_valid, missing_paths = check_required_paths()
    if paths_valid:
        print("✓ Project structure is valid")
    else:
        print("✗ Missing required project paths:")
        for path in missing_paths:
            print(f"  - {path}")
        success = False

    # Step 3: Configure VS Code settings
    try:
        print("Creating modern VS Code configuration...")
        vscode_dir = create_vscode_directory()
        settings_path = vscode_dir / "settings.json"

        if should_create_settings_json():
            settings = get_modern_vscode_settings()
            with open(settings_path, "w", encoding="utf-8") as f:
                import json

                json.dump(settings, f, indent=2)
            print("✓ VS Code configuration created successfully")
            print("  - settings.json (Python development settings)")
        else:
            print("✓ VS Code settings.json already exists")

        # Create other VS Code configuration files
        launch_path = vscode_dir / "launch.json"
        if not launch_path.exists():
            from setup.environment import get_modern_launch_config

            launch_config = get_modern_launch_config()
            with open(launch_path, "w", encoding="utf-8") as f:
                import json

                json.dump(launch_config, f, indent=2)
            print("  - launch.json (Debug configurations)")

        tasks_path = vscode_dir / "tasks.json"
        if not tasks_path.exists():
            from setup.environment import get_modern_tasks_config

            tasks_config = get_modern_tasks_config()
            with open(tasks_path, "w", encoding="utf-8") as f:
                import json

                json.dump(tasks_config, f, indent=2)
            print("  - tasks.json (Build and test tasks)")

        extensions_path = vscode_dir / "extensions.json"
        if not extensions_path.exists():
            from setup.environment import create_vscode_extensions_config

            extensions_config = create_vscode_extensions_config()
            with open(extensions_path, "w", encoding="utf-8") as f:
                import json

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
            module_name = package.replace(
                "-", "_"
            )  # Convert package name to module name
            __import__(module_name)
            print(f"✓ {package} is installed")
        except ImportError:
            print(f"✗ {package} is not installed or cannot be imported")
            print(f"  Install with: pip install {package}")
            success = False

    return success
