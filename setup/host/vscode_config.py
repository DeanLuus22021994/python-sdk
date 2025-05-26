"""VS Code configuration for host setup."""

import json
from pathlib import Path
from typing import Any

try:
    from setup.environment import (
        create_modern_vscode_settings,
        create_vscode_directory,
        get_modern_vscode_settings,
    )
except ImportError:
    # Fallback implementations if imports fail
    def create_vscode_directory() -> Path:
        """Create .vscode directory if it doesn't exist."""
        project_root = Path.cwd()
        vscode_path = project_root / ".vscode"
        vscode_path.mkdir(exist_ok=True)
        return vscode_path

    def get_modern_vscode_settings() -> dict[str, Any]:
        """Get default VS Code settings."""
        return {"python.defaultInterpreterPath": "python"}

    def create_modern_vscode_settings() -> bool:
        """Create modern VS Code settings files."""
        try:
            vscode_dir = create_vscode_directory()
            settings_path = vscode_dir / "settings.json"
            if not settings_path.exists():
                settings = get_modern_vscode_settings()
                with open(settings_path, "w", encoding="utf-8") as f:
                    json.dump(settings, f, indent=2)
            return True
        except Exception:
            return False


def setup_vscode_config() -> bool:
    """Setup VS Code configuration for Python development."""
    print("⚙️  Setting up VS Code configuration...")
    try:
        if create_modern_vscode_settings():
            print("  ✓ Created VS Code settings")
            return True
        else:
            print("  ✗ Failed to create VS Code settings")
            return False
    except Exception as e:
        print(f"  ✗ Error setting up VS Code: {str(e)}")
        return False


def get_current_vscode_settings() -> dict[str, Any]:
    """Get current VS Code settings from settings.json."""
    try:
        vscode_dir = create_vscode_directory()
        settings_path = vscode_dir / "settings.json"
        if settings_path.exists():
            with open(settings_path, encoding="utf-8") as f:
                return json.load(f)
        return {}
    except Exception:
        return {}


def update_vscode_settings(new_settings: dict[str, Any]) -> bool:
    """Update VS Code settings with new values."""
    try:
        vscode_dir = create_vscode_directory()
        settings_path = vscode_dir / "settings.json"

        current_settings = get_current_vscode_settings()
        # Merge settings
        merged_settings = {**current_settings, **new_settings}

        with open(settings_path, "w", encoding="utf-8") as f:
            json.dump(merged_settings, f, indent=2)
        return True
    except Exception:
        return False
