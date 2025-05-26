# Continuing from the incomplete file
def create_modern_vscode_settings() -> bool:
    """
    Create modern VS Code settings files.

    Returns:
        True if settings were created successfully, False otherwise
    """
    try:
        vscode_dir = create_vscode_directory()
        settings_path = vscode_dir / "settings.json"

        if should_create_settings_json():
            settings = get_modern_vscode_settings()
            with open(settings_path, "w", encoding="utf-8") as f:
                import json
                json.dump(settings, f, indent=2)

        # Create other configuration files
        launch_path = vscode_dir / "launch.json"
        if not launch_path.exists():
            launch_config = get_modern_launch_config()
            with open(launch_path, "w", encoding="utf-8") as f:
                import json
                json.dump(launch_config, f, indent=2)

        tasks_path = vscode_dir / "tasks.json"
        if not tasks_path.exists():
            tasks_config = get_modern_tasks_config()
            with open(tasks_path, "w", encoding="utf-8") as f:
                import json
                json.dump(tasks_config, f, indent=2)

        extensions_path = vscode_dir / "extensions.json"
        if not extensions_path.exists():
            extensions_config = create_vscode_extensions_config()
            with open(extensions_path, "w", encoding="utf-8") as f:
                import json
                json.dump(extensions_config, f, indent=2)

        return True
    except Exception:
        return False


def get_modern_launch_config() -> dict[str, Any]:
    """
    Get modern VS Code launch configuration.

    Returns:
        Dictionary with launch configuration
    """
    return {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "Python: Current File",
                "type": "python",
                "request": "launch",
                "program": "${file}",
                "console": "integratedTerminal",
                "justMyCode": True,
            },
            {
                "name": "Python: Run Tests",
                "type": "python",
                "request": "launch",
                "module": "pytest",
                "args": ["tests/", "-v"],
                "console": "integratedTerminal",
                "justMyCode": False,
            },
            {
                "name": "Python: Setup Script",
                "type": "python",
                "request": "launch",
                "program": "${workspaceFolder}/setup.py",
                "console": "integratedTerminal",
                "justMyCode": True,
            },
        ],
    }


def get_modern_tasks_config() -> dict[str, Any]:
    """
    Get modern tasks configuration for build and test automation.

    Returns:
        Dictionary with tasks configuration
    """
    return {
        "version": "2.0.0",
        "tasks": [
            {
                "label": "Install Dependencies",
                "type": "shell",
                "command": "uv",
                "args": ["sync"],
                "group": "build",
                "presentation": {"echo": True, "reveal": "always", "panel": "new"},
                "problemMatcher": [],
            },
            {
                "label": "Run Tests",
                "type": "shell",
                "command": "uv",
                "args": ["run", "pytest", "tests/", "-v"],
                "group": {"kind": "test", "isDefault": True},
                "presentation": {"echo": True, "reveal": "always", "panel": "new"},
                "problemMatcher": [],
            },
            {
                "label": "Format Code",
                "type": "shell",
                "command": "uv",
                "args": ["run", "black", "src/", "tests/", "setup/"],
                "group": "build",
                "presentation": {"echo": True, "reveal": "always", "panel": "new"},
                "problemMatcher": [],
            },
            {
                "label": "Lint Code",
                "type": "shell",
                "command": "uv",
                "args": ["run", "ruff", "check", "src/", "tests/", "setup/"],
                "group": "build",
                "presentation": {"echo": True, "reveal": "always", "panel": "new"},
                "problemMatcher": [],
            },
        ],
    }


def create_vscode_extensions_config() -> dict[str, Any]:
    """
    Get recommended VS Code extensions configuration.

    Returns:
        Dictionary with extensions configuration
    """
    return {
        "recommendations": RECOMMENDED_EXTENSIONS,
        "unwantedRecommendations": [
            "ms-python.pylint",
            "ms-python.flake8",
        ],
    }


def should_create_settings_json() -> bool:
    """
    Check if VS Code settings.json should be created.

    Returns:
        True if settings.json doesn't exist or is invalid
    """
    project_root = get_project_root()
    settings_path = project_root / ".vscode" / "settings.json"

    if not settings_path.exists():
        return True

    try:
        import json
        with open(settings_path, encoding="utf-8") as f:
            json.load(f)
        return False  # File exists and is valid JSON
    except (json.JSONDecodeError, Exception):
        return True  # File exists but is invalid
