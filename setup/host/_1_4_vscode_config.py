"""VS Code configuration module for Python SDK setup."""

import json
from pathlib import Path

try:
    from setup.environment import (
        get_project_root,
        get_vscode_settings,
    )
except ImportError:
    # Fallback functions if import fails
    def get_project_root() -> Path:
        """Get project root directory."""
        return Path(__file__).parent.parent.parent

    def get_vscode_settings() -> dict[str, str | bool]:
        """Get default VS Code settings."""
        return {"python.defaultInterpreterPath": "python"}


def create_vscode_directory() -> Path:
    """Create .vscode directory if it doesn't exist."""
    project_root = get_project_root()
    vscode_path = project_root / ".vscode"
    vscode_path.mkdir(exist_ok=True)
    return vscode_path


def should_create_settings_json() -> bool:
    """Check if settings.json should be created."""
    project_root = get_project_root()
    settings_path = project_root / ".vscode" / "settings.json"
    return not settings_path.exists()


def should_create_launch_json() -> bool:
    """Check if launch.json should be created."""
    project_root = get_project_root()
    launch_path = project_root / ".vscode" / "launch.json"
    return not launch_path.exists()


def create_settings_json() -> bool:
    """Create VS Code settings.json file."""
    try:
        vscode_path = create_vscode_directory()
        settings_path = vscode_path / "settings.json"

        settings = get_vscode_settings()

        with open(settings_path, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)

        return True
    except Exception:
        return False


def create_launch_json() -> bool:
    """Create VS Code launch.json file."""
    try:
        vscode_path = create_vscode_directory()
        launch_path = vscode_path / "launch.json"

        launch_config = {
            "version": "0.2.0",
            "configurations": [
                {
                    "name": "Python: Current File",
                    "type": "python",
                    "request": "launch",
                    "program": "${file}",
                    "console": "integratedTerminal",
                    "justMyCode": True,
                }
            ],
        }

        with open(launch_path, "w", encoding="utf-8") as f:
            json.dump(launch_config, f, indent=2)

        return True
    except Exception:
        return False


def get_current_vscode_settings() -> dict[str, str | bool]:
    """Get current VS Code settings from settings.json."""
    try:
        project_root = get_project_root()
        settings_path = project_root / ".vscode" / "settings.json"
        if settings_path.exists():
            with open(settings_path, encoding="utf-8") as f:
                return json.load(f)
        return {}
    except Exception:
        return {}


def update_vscode_settings(new_settings: dict[str, str]) -> bool:
    """Update VS Code settings with new values."""
    try:
        vscode_path = create_vscode_directory()
        settings_path = vscode_path / "settings.json"

        current_settings = get_current_vscode_settings()
        current_settings.update(new_settings)

        with open(settings_path, "w", encoding="utf-8") as f:
            json.dump(current_settings, f, indent=2)

        return True
    except Exception:
        return False


def setup_vscode_config() -> tuple[bool, str]:
    """Set up VS Code configuration files."""
    try:
        success = True
        messages = []

        # Create .vscode directory
        vscode_path = create_vscode_directory()
        if vscode_settings := get_vscode_settings():
            update_vscode_settings(vscode_settings)
            messages.append("✓ VS Code settings configured")
        else:
            messages.append("✓ VS Code directory created")
            success = False

        return success, "; ".join(messages)
    except Exception as e:
        return False, f"Error setting up VS Code config: {e}"
