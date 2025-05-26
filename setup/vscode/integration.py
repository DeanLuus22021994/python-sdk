"""
VS Code integration module for MCP Python SDK setup.

Provides a unified interface to manage all VS Code configurations using the
modular managers. This module coordinates between all VS Code configuration
components and integrates with the existing setup system.
"""

from pathlib import Path
from typing import Any

from ..types import ValidationDetails, ValidationStatus, VSCodeConfig
from .extensions import VSCodeExtensionsManager
from .launch import VSCodeLaunchManager
from .settings import VSCodeSettingsManager
from .tasks import VSCodeTasksManager


class VSCodeIntegrationManager:
    """Unified VS Code configuration manager."""

    def __init__(self, project_root: Path) -> None:
        """Initialize the integration manager.

        Args:
            project_root: Path to the project root directory
        """
        self.project_root = project_root
        self.vscode_dir = project_root / ".vscode"

        # Initialize component managers
        self.settings_manager = VSCodeSettingsManager(project_root)
        self.extensions_manager = VSCodeExtensionsManager(project_root)
        self.launch_manager = VSCodeLaunchManager(project_root)
        self.tasks_manager = VSCodeTasksManager(project_root)

    def should_configure_vscode(self) -> bool:
        """Check if VS Code configuration should be created or updated.

        Returns:
            True if any VS Code configuration needs updates
        """
        return (
            self.settings_manager.should_create_settings()
            or self.extensions_manager.should_create_extensions()
            or self.launch_manager.should_create_launch()
            or self.tasks_manager.should_create_tasks()
        )

    def create_all_configurations(self) -> bool:
        """Create all VS Code configuration files.

        Returns:
            True if all configurations were created successfully
        """
        try:
            # Ensure .vscode directory exists
            self.vscode_dir.mkdir(exist_ok=True)

            results = []

            # Create settings if needed
            if self.settings_manager.should_create_settings():
                results.append(self.settings_manager.create_settings_file())

            # Create extensions if needed
            if self.extensions_manager.should_create_extensions():
                results.append(self.extensions_manager.create_extensions_file())

            # Create launch configurations if needed
            if self.launch_manager.should_create_launch():
                results.append(self.launch_manager.create_launch_file())

            # Create tasks if needed
            if self.tasks_manager.should_create_tasks():
                results.append(self.tasks_manager.create_tasks_file())

            return all(results) if results else True

        except Exception:
            return False

    def get_vscode_config(self) -> VSCodeConfig:
        """Get complete VS Code configuration.

        Returns:
            VSCodeConfig object with all current configurations
        """
        return VSCodeConfig(
            settings=self.settings_manager.get_current_settings(),
            extensions=self.extensions_manager.get_current_extensions().get(
                "recommendations", []
            ),
            launch_config=self.launch_manager.get_current_launch(),
            tasks_config=self.tasks_manager.get_current_tasks(),
            workspace_config={},  # Not implemented yet
        )

    def validate_all_configurations(self) -> ValidationDetails:
        """Validate all VS Code configurations.

        Returns:
            ValidationDetails with overall validation results
        """
        # Validate each component
        settings_validation = self.settings_manager.validate_settings()
        extensions_validation = self.extensions_manager.validate_extensions()
        launch_validation = self.launch_manager.validate_launch()
        tasks_validation = self.tasks_manager.validate_tasks()

        # Aggregate results
        all_validations = [
            settings_validation,
            extensions_validation,
            launch_validation,
            tasks_validation,
        ]

        all_warnings = []
        all_errors = []
        all_recommendations = []

        for validation in all_validations:
            all_warnings.extend(validation.warnings)
            all_errors.extend(validation.errors)
            all_recommendations.extend(validation.recommendations)

        # Determine overall status
        if all_errors:
            status = ValidationStatus.ERROR
            is_valid = False
            message = (
                f"VS Code validation failed with {len(all_errors)} errors "
                f"across all configurations"
            )
        elif all_warnings:
            status = ValidationStatus.WARNING
            is_valid = True
            message = (
                f"VS Code validation passed with {len(all_warnings)} "
                f"warnings across all configurations"
            )
        else:
            status = ValidationStatus.VALID
            is_valid = True
            message = "All VS Code configurations validated successfully"

        # Aggregate metadata
        vscode_files = [
            self.settings_manager.settings_path,
            self.extensions_manager.extensions_path,
            self.launch_manager.launch_path,
            self.tasks_manager.tasks_path,
        ]

        metadata = {
            "settings_valid": settings_validation.is_valid,
            "extensions_valid": extensions_validation.is_valid,
            "launch_valid": launch_validation.is_valid,
            "tasks_valid": tasks_validation.is_valid,
            "vscode_dir_exists": self.vscode_dir.exists(),
            "total_files": sum(1 for path in vscode_files if path.exists()),
        }

        return ValidationDetails(
            is_valid=is_valid,
            status=status,
            message=message,
            warnings=all_warnings,
            errors=all_errors,
            recommendations=all_recommendations,
            metadata=metadata,
        )

    def update_all_configurations(self, force: bool = False) -> bool:
        """Update all VS Code configurations with modern settings.

        Args:
            force: Whether to force update even if files exist

        Returns:
            True if all updates were successful
        """
        try:
            results = []

            # Update settings
            if force or self.settings_manager.should_create_settings():
                modern_settings = self.settings_manager.get_modern_settings()
                results.append(
                    self.settings_manager.update_settings(
                        modern_settings, merge=not force
                    )
                )

            # Update extensions
            if force or self.extensions_manager.should_create_extensions():
                extensions_config = self.extensions_manager.get_extensions_config()
                results.append(
                    self.extensions_manager.update_extensions(
                        extensions_config, merge=not force
                    )
                )

            # Update launch configurations
            if force or self.launch_manager.should_create_launch():
                launch_config = self.launch_manager.get_launch_config()
                results.append(
                    self.launch_manager.update_launch(launch_config, merge=not force)
                )

            # Update tasks
            if force or self.tasks_manager.should_create_tasks():
                tasks_config = self.tasks_manager.get_tasks_config()
                results.append(
                    self.tasks_manager.update_tasks(tasks_config, merge=not force)
                )

            return all(results) if results else True

        except Exception:
            return False

    def clean_deprecated_configurations(self) -> bool:
        """Remove deprecated VS Code configurations.

        Returns:
            True if cleanup was successful
        """
        try:
            # Remove deprecated settings
            current_settings = self.settings_manager.get_current_settings()
            deprecated_settings = [
                "python.linting.pylintEnabled",
                "python.linting.flake8Enabled",
                "python.formatting.provider",
                "python.linting.enabled",  # Replaced by Ruff
            ]

            settings_changed = False
            for deprecated in deprecated_settings:
                if deprecated in current_settings:
                    del current_settings[deprecated]
                    settings_changed = True

            if settings_changed:
                self.settings_manager.update_settings(current_settings, merge=False)

            # Remove conflicting extensions
            current_extensions = self.extensions_manager.get_current_extensions()
            recommendations = current_extensions.get("recommendations", [])
            unwanted = self.extensions_manager.get_unwanted_extensions()

            cleaned_recommendations = [
                ext for ext in recommendations if ext not in unwanted
            ]

            if len(cleaned_recommendations) != len(recommendations):
                current_extensions["recommendations"] = cleaned_recommendations
                self.extensions_manager.update_extensions(
                    current_extensions, merge=False
                )

            return True

        except Exception:
            return False

    def get_configuration_summary(self) -> dict[str, Any]:
        """Get a summary of current VS Code configuration status.

        Returns:
            Dictionary with configuration summary
        """
        validation = self.validate_all_configurations()

        return {
            "status": validation.status.value,
            "is_valid": validation.is_valid,
            "message": validation.message,
            "files": {
                "settings.json": {
                    "exists": self.settings_manager.settings_path.exists(),
                    "valid": validation.metadata.get("settings_valid", False),
                },
                "extensions.json": {
                    "exists": self.extensions_manager.extensions_path.exists(),
                    "valid": validation.metadata.get("extensions_valid", False),
                },
                "launch.json": {
                    "exists": self.launch_manager.launch_path.exists(),
                    "valid": validation.metadata.get("launch_valid", False),
                },
                "tasks.json": {
                    "exists": self.tasks_manager.tasks_path.exists(),
                    "valid": validation.metadata.get("tasks_valid", False),
                },
            },
            "recommendations_count": len(validation.recommendations),
            "warnings_count": len(validation.warnings),
            "errors_count": len(validation.errors),
        }
