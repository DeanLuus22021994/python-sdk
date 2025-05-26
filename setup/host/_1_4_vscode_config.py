"""
Setup Module 1.4: VS Code Configuration
Ensures VS Code is properly configured for development
"""

import json
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from setup.environment import (
        get_project_root,
        create_vscode_directory,
        should_create_settings_json,
        VSCODE_SETTINGS,
    )
except ImportError:
    # Fallback functions if import fails
    def get_project_root():
        return Path(__file__).parent.parent.parent

    def create_vscode_directory():
        project_root = get_project_root()
        vscode_path = project_root / ".vscode"
        vscode_path.mkdir(exist_ok=True)
        return vscode_path

    def should_create_settings_json():
        project_root = get_project_root()
        settings_path = project_root / ".vscode" / "settings.json"
        return not settings_path.exists()

    VSCODE_SETTINGS = {"python.defaultInterpreterPath": "python"}


def validate_vscode_config() -> tuple[bool, str]:
    """Validate VS Code configuration exists and is correct."""
    project_root = get_project_root()
    vscode_path = project_root / ".vscode"
    settings_path = vscode_path / "settings.json"

    if not vscode_path.exists():
        return False, "✗ .vscode directory not found"
    if not settings_path.exists():
        return False, "✗ VS Code settings.json not found"

    try:
        with open(settings_path, encoding="utf-8") as f:
            settings = json.load(f)
        if "python.defaultInterpreterPath" in settings:
            return True, "✓ VS Code configuration validated"
        else:
            return True, "✓ Basic .vscode setup detected"
    except json.JSONDecodeError:
        return False, "✗ Invalid JSON in settings.json"
    except Exception as e:
        return False, f"✗ Error reading VS Code config: {str(e)}"


def setup_vscode_config() -> bool:
    """Setup VS Code configuration for Python development."""
    print("⚙️  Setting up VS Code configuration...")
    validated, message = validate_vscode_config()
    print(f"  {message}")

    if not validated:
        vscode_path = create_vscode_directory()
        settings_path = vscode_path / "settings.json"

        if should_create_settings_json():
            with open(settings_path, "w", encoding="utf-8") as f:
                json.dump(VSCODE_SETTINGS, f, indent=2)
            print("  ✓ Created VS Code settings")

    return True
