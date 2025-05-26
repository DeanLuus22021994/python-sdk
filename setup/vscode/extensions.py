"""
VS Code extensions configuration manager.

Handles creation and management of VS Code extensions.json with recommended
extensions for Python development with the MCP SDK.
"""

import json
from pathlib import Path
from typing import Any

from ..types import ValidationDetails, ValidationStatus


class VSCodeExtensionsManager:
    """Manages VS Code extensions.json configuration."""

    def __init__(self, project_root: Path) -> None:
        """Initialize the extensions manager.

        Args:
            project_root: Path to the project root directory
        """
        self.project_root = project_root
        self.vscode_dir = project_root / ".vscode"
        self.extensions_path = self.vscode_dir / "extensions.json"

    def get_recommended_extensions(self) -> list[str]:
        """Get list of recommended VS Code extensions for Python development.

        Returns:
            List of extension identifiers
        """
        return [
            # Core Python development
            "ms-python.python",
            "ms-python.vscode-pylance",
            "ms-python.debugpy",
            # Code formatting and linting
            "ms-python.black-formatter",
            "ms-python.isort",
            "charliermarsh.ruff",
            "ms-python.mypy-type-checker",
            # Development tools
            "github.copilot",
            "github.copilot-chat",
            "ms-vscode.errorlens",
            # File format support
            "ms-vscode.vscode-json",
            "tamasfe.even-better-toml",
            "redhat.vscode-yaml",
            "yzhang.markdown-all-in-one",
            # Additional utilities
            "ms-vscode.test-adapter-converter",
            "streetsidesoftware.code-spell-checker",
            # Docker and containers
            "ms-azuretools.vscode-docker",
            "ms-vscode-remote.remote-containers",
            # Git integration
            "mhutchie.git-graph",
            "eamodio.gitlens",
        ]

    def get_python_extensions(self) -> list[str]:
        """Get Python-specific extensions for this workspace.

        Returns:
            List of Python-related extension identifiers
        """
        return [
            "ms-python.python",
            "ms-python.vscode-pylance",
            "ms-python.debugpy",
            "ms-python.black-formatter",
            "ms-python.isort",
            "charliermarsh.ruff",
            "ms-python.mypy-type-checker",
        ]

    def get_unwanted_extensions(self) -> list[str]:
        """Get list of extensions that conflict with our setup.

        Returns:
            List of unwanted extension identifiers
        """
        return [
            # Replaced by Ruff
            "ms-python.pylint",
            "ms-python.flake8",
            "ms-python.autopep8",
            # Replaced by Black formatter
            "ms-python.yapf",
            # Conflicting formatters
            "esbenp.prettier-vscode",  # Can conflict with Python formatters
        ]

    def get_extensions_config(self) -> dict[str, Any]:
        """Get complete extensions configuration.

        Returns:
            Dictionary containing extensions configuration
        """
        return {
            "recommendations": self.get_recommended_extensions(),
            "unwantedRecommendations": self.get_unwanted_extensions(),
        }

    def create_extensions_file(self) -> bool:
        """Create VS Code extensions.json file.

        Returns:
            True if file was created successfully, False otherwise
        """
        try:
            # Ensure .vscode directory exists
            self.vscode_dir.mkdir(exist_ok=True)

            # Get extensions configuration
            config = self.get_extensions_config()

            # Write extensions file with proper formatting
            with open(self.extensions_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)

            return True
        except Exception:
            return False

    def should_create_extensions(self) -> bool:
        """Check if extensions.json should be created or updated.

        Returns:
            True if extensions file should be created/updated
        """
        if not self.extensions_path.exists():
            return True

        try:
            with open(self.extensions_path, encoding="utf-8") as f:
                existing_config = json.load(f)

            # Check if recommendations have changed
            current_recommendations = set(existing_config.get("recommendations", []))
            new_recommendations = set(self.get_recommended_extensions())

            # Update if recommendations differ significantly
            return len(new_recommendations - current_recommendations) > 0

        except (json.JSONDecodeError, Exception):
            return True  # File exists but is invalid

    def get_current_extensions(self) -> dict[str, Any]:
        """Get current VS Code extensions configuration.

        Returns:
            Dictionary with current extensions config or empty dict
        """
        if not self.extensions_path.exists():
            return {}

        try:
            with open(self.extensions_path, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, Exception):
            return {}

    def add_extension(self, extension_id: str) -> bool:
        """Add an extension to the recommendations.

        Args:
            extension_id: VS Code extension identifier

        Returns:
            True if extension was added successfully
        """
        try:
            current = self.get_current_extensions()
            recommendations = current.get("recommendations", [])

            if extension_id not in recommendations:
                recommendations.append(extension_id)
                current["recommendations"] = recommendations

                # Ensure .vscode directory exists
                self.vscode_dir.mkdir(exist_ok=True)

                # Write updated configuration
                with open(self.extensions_path, "w", encoding="utf-8") as f:
                    json.dump(current, f, indent=2)

            return True
        except Exception:
            return False

    def remove_extension(self, extension_id: str) -> bool:
        """Remove an extension from recommendations.

        Args:
            extension_id: VS Code extension identifier to remove

        Returns:
            True if extension was removed successfully
        """
        try:
            current = self.get_current_extensions()
            recommendations = current.get("recommendations", [])

            if extension_id in recommendations:
                recommendations.remove(extension_id)
                current["recommendations"] = recommendations

                # Write updated configuration
                with open(self.extensions_path, "w", encoding="utf-8") as f:
                    json.dump(current, f, indent=2)

            return True
        except Exception:
            return False

    def validate_extensions(
        self, config: dict[str, Any] | None = None
    ) -> ValidationDetails:
        """Validate VS Code extensions configuration.

        Args:
            config: Extensions config to validate, uses current if None

        Returns:
            ValidationDetails with validation results
        """
        if config is None:
            config = self.get_current_extensions()

        warnings = []
        errors = []
        recommendations = []

        # Validate structure
        if not isinstance(config, dict):
            errors.append("Extensions configuration must be a dictionary")
            return ValidationDetails(
                is_valid=False,
                status=ValidationStatus.ERROR,
                message="Invalid extensions configuration structure",
                warnings=warnings,
                errors=errors,
                recommendations=recommendations,
                metadata={"file_exists": self.extensions_path.exists()},
            )

        # Check for required fields
        if "recommendations" not in config:
            warnings.append("No extension recommendations found")
        else:
            # Validate recommendations format
            recs = config["recommendations"]
            if not isinstance(recs, list):
                errors.append("Recommendations must be a list")
            else:
                # Check for invalid extension IDs using list comprehension
                invalid_extensions = [
                    ext for ext in recs if not isinstance(ext, str) or "." not in ext
                ]
                warnings.extend(
                    [
                        f"Potentially invalid extension ID: {ext}"
                        for ext in invalid_extensions
                    ]
                )

        # Check for conflicting extensions
        unwanted = set(self.get_unwanted_extensions())
        current_recs = set(config.get("recommendations", []))
        conflicts = unwanted.intersection(current_recs)

        if conflicts:
            for conflict in conflicts:
                warnings.append(f"Conflicting extension found: {conflict}")
                recommendations.append(
                    f"Remove {conflict} as it conflicts with our setup"
                )

        # Check for missing core extensions
        core_extensions = [
            "ms-python.python",
            "ms-python.vscode-pylance",
            "charliermarsh.ruff",
        ]

        missing_core = [ext for ext in core_extensions if ext not in current_recs]

        if missing_core:
            warnings.append(f"Missing core extensions: {', '.join(missing_core)}")
            recommendations.append(
                "Add missing core extensions for optimal Python development"
            )

        # Validate JSON structure
        try:
            json.dumps(config)
        except (TypeError, ValueError) as e:
            errors.append(f"Invalid JSON structure: {e}")

        # Determine overall status
        if errors:
            status = ValidationStatus.ERROR
            is_valid = False
            message = f"Extensions validation failed with {len(errors)} errors"
        elif warnings:
            status = ValidationStatus.WARNING
            is_valid = True
            message = f"Extensions validation passed with {len(warnings)} warnings"
        else:
            status = ValidationStatus.VALID
            is_valid = True
            message = "Extensions validation passed successfully"

        return ValidationDetails(
            is_valid=is_valid,
            status=status,
            message=message,
            warnings=warnings,
            errors=errors,
            recommendations=recommendations,
            metadata={
                "recommendations_count": len(config.get("recommendations", [])),
                "unwanted_count": len(config.get("unwantedRecommendations", [])),
                "file_exists": self.extensions_path.exists(),
                "conflicts_found": len(conflicts),
                "missing_core": len(missing_core),
            },
        )

    def update_extensions(self, updates: dict[str, Any], merge: bool = True) -> bool:
        """Update VS Code extensions configuration.

        Args:
            updates: Extensions updates to apply
            merge: Whether to merge with existing config or replace

        Returns:
            True if update was successful
        """
        try:
            if merge:
                current = self.get_current_extensions()

                # Merge recommendations lists
                if "recommendations" in updates:
                    current_recs = set(current.get("recommendations", []))
                    new_recs = updates["recommendations"]
                    merged_recs = list(current_recs.union(new_recs))
                    current["recommendations"] = merged_recs

                # Merge unwanted recommendations
                if "unwantedRecommendations" in updates:
                    current_unwanted = set(current.get("unwantedRecommendations", []))
                    new_unwanted = updates["unwantedRecommendations"]
                    merged_unwanted = list(current_unwanted.union(new_unwanted))
                    current["unwantedRecommendations"] = merged_unwanted

                config_to_write = current
            else:
                config_to_write = updates

            # Ensure .vscode directory exists
            self.vscode_dir.mkdir(exist_ok=True)

            # Write updated configuration
            with open(self.extensions_path, "w", encoding="utf-8") as f:
                json.dump(config_to_write, f, indent=2)

            return True
        except Exception:
            return False
