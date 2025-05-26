"""
VS Code settings configuration manager.

Handles creation and management of VS Code settings.json with modern Python
development configurations optimized for the MCP Python SDK.
"""

import json
from pathlib import Path
from typing import Any

from ..types import ValidationDetails, ValidationStatus


class VSCodeSettingsManager:
    """Manages VS Code settings.json configuration."""

    def __init__(self, project_root: Path) -> None:
        """Initialize the settings manager.

        Args:
            project_root: Path to the project root directory
        """
        self.project_root = project_root
        self.vscode_dir = project_root / ".vscode"
        self.settings_path = self.vscode_dir / "settings.json"

    def get_modern_settings(self) -> dict[str, Any]:
        """Get modern VS Code settings for Python development.

        Returns:
            Dictionary containing modern VS Code settings
        """
        return {
            # Python interpreter and environment
            "python.defaultInterpreterPath": "./venv/Scripts/python.exe",
            "python.terminal.activateEnvironment": True,
            # Analysis and IntelliSense
            "python.analysis.autoImportCompletions": True,
            "python.analysis.diagnosticMode": "workspace",
            "python.analysis.inlayHints.variableTypes": True,
            "python.analysis.inlayHints.functionReturnTypes": True,
            "python.analysis.inlayHints.callArgumentNames": "partial",
            "python.analysis.inlayHints.pytestParameters": True,
            "python.analysis.completeFunctionParens": True,
            "python.analysis.indexing": True,
            "python.analysis.userFileIndexingLimit": 5000,
            "python.analysis.autoFormatStrings": True,
            "python.analysis.fixAll": ["source.convertImportFormat"],
            "python.analysis.typeCheckingMode": "basic",
            # Testing configuration
            "python.testing.pytestEnabled": True,
            "python.testing.unittestEnabled": False,
            "python.testing.pytestArgs": ["--color=yes"],
            "python.testing.autoTestDiscoverOnSaveEnabled": True,
            "python.testing.cwd": "${workspaceFolder}",
            "python.testing.debugPort": 3000,
            # Linting and formatting
            "python.linting.enabled": False,  # Using Ruff instead
            "ruff.enable": True,
            # Editor settings
            "editor.formatOnSave": True,
            "editor.codeActionsOnSave": {
                "source.organizeImports": "explicit",
                "source.fixAll.ruff": "explicit",
            },
            "editor.inlayHints.enabled": "on",
            # File management
            "files.exclude": {
                "**/__pycache__": True,
                "**/*.pyc": True,
                ".mypy_cache": True,
                ".pytest_cache": True,
                "*.egg-info": True,
                ".coverage": True,
                "**/htmlcov": True,
            },
            "files.watcherExclude": {
                "**/htmlcov/**": True,
                "**/__pycache__/**": True,
                ".mypy_cache/**": True,
                ".pytest_cache/**": True,
            },
            "files.insertFinalNewline": True,
            "files.trimFinalNewlines": True,
            "files.trimTrailingWhitespace": True,
            "files.associations": {
                "uv.lock": "yaml",
                "*.toml": "toml",
            },
            # Search settings
            "search.exclude": {
                "**/__pycache__": True,
                "**/*.pyc": True,
                ".mypy_cache": True,
                ".pytest_cache": True,
                "*.egg-info": True,
                "**/htmlcov": True,
            },
            # Language-specific settings
            "[python]": {
                "editor.inlayHints.enabled": "on",
                "editor.defaultFormatter": "ms-python.black-formatter",
            },
            "[json]": {
                "editor.defaultFormatter": "vscode.json-language-features",
            },
            "[jsonc]": {
                "editor.defaultFormatter": "vscode.json-language-features",
            },
            "[toml]": {
                "editor.defaultFormatter": "tamasfe.even-better-toml",
            },
            "[yaml]": {
                "editor.defaultFormatter": "redhat.vscode-yaml",
            },
            "[markdown]": {
                "editor.defaultFormatter": "yzhang.markdown-all-in-one",
            },
            # JSON schema settings
            "json.schemas": [],
            # Emmet settings
            "emmet.includeLanguages": {"jinja-html": "html", "jinja2": "html"},
        }

    def create_settings_file(self) -> bool:
        """Create VS Code settings.json file.

        Returns:
            True if file was created successfully, False otherwise
        """
        try:
            # Ensure .vscode directory exists
            self.vscode_dir.mkdir(exist_ok=True)

            # Get modern settings
            settings = self.get_modern_settings()

            # Write settings file
            with open(self.settings_path, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2)

            return True
        except Exception:
            return False

    def should_create_settings(self) -> bool:
        """Check if settings.json should be created or updated.

        Returns:
            True if settings file should be created/updated
        """
        if not self.settings_path.exists():
            return True

        try:
            with open(self.settings_path, encoding="utf-8") as f:
                json.load(f)
            return False  # File exists and is valid JSON
        except (json.JSONDecodeError, Exception):
            return True  # File exists but is invalid

    def get_current_settings(self) -> dict[str, Any]:
        """Get current VS Code settings from existing file.

        Returns:
            Dictionary with current settings or empty dict if file doesn't exist
        """
        if not self.settings_path.exists():
            return {}

        try:
            with open(self.settings_path, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, Exception):
            return {}

    def merge_settings(self, new_settings: dict[str, Any]) -> dict[str, Any]:
        """Merge new settings with existing ones.

        Args:
            new_settings: New settings to merge

        Returns:
            Merged settings dictionary
        """
        current = self.get_current_settings()

        # Deep merge dictionaries
        def deep_merge(dict1: dict[str, Any], dict2: dict[str, Any]) -> dict[str, Any]:
            result = dict1.copy()
            for key, value in dict2.items():
                if (
                    key in result
                    and isinstance(result[key], dict)
                    and isinstance(value, dict)
                ):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result

        return deep_merge(current, new_settings)

    def validate_settings(
        self, settings: dict[str, Any] | None = None
    ) -> ValidationDetails:
        """Validate VS Code settings configuration.

        Args:
            settings: Settings to validate, uses current if None

        Returns:
            ValidationDetails with validation results
        """
        if settings is None:
            settings = self.get_current_settings()

        warnings = []
        errors = []
        recommendations = []

        # Check for required settings
        required_python_settings = [
            "python.defaultInterpreterPath",
            "python.testing.pytestEnabled",
        ]

        for setting in required_python_settings:
            if setting not in settings:
                warnings.append(f"Missing recommended setting: {setting}")

        # Check for deprecated settings
        deprecated_settings = [
            "python.linting.pylintEnabled",
            "python.linting.flake8Enabled",
            "python.formatting.provider",
        ]

        for setting in deprecated_settings:
            if setting in settings:
                warnings.append(f"Deprecated setting found: {setting}")
                recommendations.append(
                    f"Consider removing {setting} and using modern alternatives"
                )

        # Validate JSON structure
        try:
            json.dumps(settings)
        except (TypeError, ValueError) as e:
            errors.append(f"Invalid JSON structure: {e}")

        # Determine overall status
        if errors:
            status = ValidationStatus.ERROR
            is_valid = False
            message = f"Settings validation failed with {len(errors)} errors"
        elif warnings:
            status = ValidationStatus.WARNING
            is_valid = True
            message = f"Settings validation passed with {len(warnings)} warnings"
        else:
            status = ValidationStatus.VALID
            is_valid = True
            message = "Settings validation passed successfully"

        return ValidationDetails(
            is_valid=is_valid,
            status=status,
            message=message,
            warnings=warnings,
            errors=errors,
            recommendations=recommendations,
            metadata={
                "settings_count": len(settings),
                "file_exists": self.settings_path.exists(),
                "file_size": (
                    self.settings_path.stat().st_size
                    if self.settings_path.exists()
                    else 0
                ),
            },
        )

    def update_settings(self, updates: dict[str, Any], merge: bool = True) -> bool:
        """Update VS Code settings.

        Args:
            updates: Settings updates to apply
            merge: Whether to merge with existing settings or replace

        Returns:
            True if update was successful
        """
        try:
            if merge:
                settings = self.merge_settings(updates)
            else:
                settings = updates

            # Ensure .vscode directory exists
            self.vscode_dir.mkdir(exist_ok=True)

            # Write updated settings
            with open(self.settings_path, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2)

            return True
        except Exception:
            return False
