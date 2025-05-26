"""VS Code configuration module for Python SDK setup."""

import json
from pathlib import Path

try:
    from setup.environment import get_project_root, get_vscode_settings
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
            vscode_settings = get_vscode_settings()
            with open(settings_path, "w", encoding="utf-8") as f:
                json.dump(vscode_settings, f, indent=2)
            print("  ✓ Created VS Code settings")

    return True


def get_current_vscode_settings() -> dict[str, str]:
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

        with open(settings_path, "w", encoding="utf-8") as f:
            json.dump(current_settings, f, indent=2)
        return True
    except Exception:
        return False
