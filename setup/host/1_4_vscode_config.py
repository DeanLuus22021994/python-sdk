"""
Setup Module 1.4: VS Code Configuration
Ensures VS Code is properly configured for development
"""

import json
from pathlib import Path


def validate_vscode_config() -> tuple[bool, str]:
    """Validate VS Code configuration exists and is correct."""
    project_root = Path(__file__).parent.parent.parent
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
        project_root = Path(__file__).parent.parent.parent
        vscode_path = project_root / ".vscode"
        vscode_path.mkdir(exist_ok=True)

        settings_path = vscode_path / "settings.json"
        if not settings_path.exists():
            minimal_settings = {"python.defaultInterpreterPath": "python"}
            with open(settings_path, "w", encoding="utf-8") as f:
                json.dump(minimal_settings, f, indent=2)
            print("  ✓ Created minimal VS Code settings")

    return True