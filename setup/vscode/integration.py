"""
VS Code Integration Manager
Comprehensive VS Code workspace configuration and management.
"""

from pathlib import Path
from typing import Any

from ..typings import ValidationDetails, ValidationStatus
from .extensions import VSCodeExtensionsManager
from .launch import VSCodeLaunchManager
from .settings import VSCodeSettingsManager
from .tasks import VSCodeTasksManager


class VSCodeIntegrationManager:
    """
    Comprehensive VS Code workspace configuration manager.

    Coordinates all VS Code configuration components including extensions,
    settings, tasks, and launch configurations.
    """

    def __init__(self, workspace_root: Path) -> None:
        """
        Initialize VS Code integration manager.

        Args:
            workspace_root: Root directory of the workspace
        """
        self.workspace_root = Path(workspace_root).resolve()
        self.vscode_dir = self.workspace_root / ".vscode"

        # Initialize component managers
        self.extensions = VSCodeExtensionsManager(self.workspace_root)
        self.settings = VSCodeSettingsManager(self.workspace_root)
        self.tasks = VSCodeTasksManager(self.workspace_root)
        self.launch = VSCodeLaunchManager(self.workspace_root)

    def create_workspace_configuration(
        self,
        force_overwrite: bool = False,
        include_optional: bool = True,
        custom_config: dict[str, Any] | None = None,
    ) -> bool:
        """
        Create complete VS Code workspace configuration.

        Args:
            force_overwrite: Whether to overwrite existing files
            include_optional: Whether to include optional configurations
            custom_config: Custom configuration overrides

        Returns:
            True if configuration was created successfully
        """
        try:
            # Ensure .vscode directory exists
            self.vscode_dir.mkdir(exist_ok=True)

            success = True

            # Create or update all configuration files
            if not self.settings.create_settings_file() and not force_overwrite:
                success = False

            if not self.launch.create_launch_file() and not force_overwrite:
                success = False

            if not self.tasks.create_tasks_file() and not force_overwrite:
                success = False

            if not self.extensions.create_extensions_file() and not force_overwrite:
                success = False

            return success

        except Exception:
            return False

    def validate_workspace(self) -> ValidationDetails:
        """Validate complete VS Code workspace configuration.

        Returns:
            ValidationDetails with overall validation results
        """
        # Collect validation results from all components
        extensions_validation = self.extensions.validate_extensions()
        settings_validation = self.settings.validate_settings()
        tasks_validation = self.tasks.validate_tasks()
        launch_validation = self.launch.validate_launch()

        # Aggregate results
        all_warnings = []
        all_errors = []
        all_recommendations = []

        validations = [
            ("Extensions", extensions_validation),
            ("Settings", settings_validation),
            ("Tasks", tasks_validation),
            ("Launch", launch_validation),
        ]

        for component_name, validation in validations:
            all_warnings.extend(validation.warnings)
            all_errors.extend(validation.errors)
            all_recommendations.extend(validation.recommendations)

        # Determine overall status
        if all_errors:
            status = ValidationStatus.ERROR
            is_valid = False
            message = f"Validation failed with {len(all_errors)} errors"
        elif all_warnings:
            status = ValidationStatus.WARNING
            is_valid = True
            message = f"Validation passed with {len(all_warnings)} warnings"
        else:
            status = ValidationStatus.VALID
            is_valid = True
            message = "All configurations are valid"

        # Collect metadata from all components
        combined_metadata = {
            "components_validated": len(validations),
            "extensions": extensions_validation.metadata,
            "settings": settings_validation.metadata,
            "tasks": tasks_validation.metadata,
            "launch": launch_validation.metadata,
            "workspace_exists": self.vscode_dir.exists(),
        }

        return ValidationDetails(
            is_valid=is_valid,
            status=status,
            message=message,
            warnings=all_warnings,
            errors=all_errors,
            recommendations=all_recommendations,
            metadata=combined_metadata,
        )

    def get_workspace_status(self) -> dict[str, Any]:
        """Get current workspace configuration status.

        Returns:
            Dictionary with status information for all components
        """
        return {
            "workspace_root": str(self.workspace_root),
            "vscode_dir_exists": self.vscode_dir.exists(),
            "settings_exists": self.settings.settings_path.exists(),
            "launch_exists": self.launch.launch_path.exists(),
            "tasks_exists": self.tasks.tasks_path.exists(),
            "extensions_exists": self.extensions.extensions_path.exists(),
        }

    def update_workspace_config(
        self, config_updates: dict[str, Any], merge: bool = True
    ) -> bool:
        """Update workspace configuration with new values.

        Args:
            config_updates: Configuration updates to apply
            merge: Whether to merge with existing config

        Returns:
            True if update was successful
        """
        try:
            success = True

            if "settings" in config_updates:
                success &= self.settings.update_settings(
                    config_updates["settings"], merge
                )

            if "launch" in config_updates:
                success &= self.launch.update_launch(config_updates["launch"], merge)

            if "tasks" in config_updates:
                success &= self.tasks.update_tasks(config_updates["tasks"], merge)

            if "extensions" in config_updates:
                success &= self.extensions.update_extensions(
                    config_updates["extensions"], merge
                )

            return success

        except Exception:
            return False

    def export_workspace_config(self) -> dict[str, Any]:
        """Export current workspace configuration.

        Returns:
            Dictionary with all configuration data
        """
        return {
            "settings": self.settings.get_current_settings(),
            "launch": self.launch.get_current_launch(),
            "tasks": self.tasks.get_current_tasks(),
            "extensions": self.extensions.get_current_extensions(),
        }

    def reset_workspace(self, components: list[str] | None = None) -> bool:
        """Reset workspace configuration components.

        Args:
            components: List of components to reset, or None for all

        Returns:
            True if reset was successful
        """
        try:
            components = components or ["settings", "launch", "tasks", "extensions"]

            success = True

            if "settings" in components:
                success &= self.settings.create_settings_file()

            if "launch" in components:
                success &= self.launch.create_launch_file()

            if "tasks" in components:
                success &= self.tasks.create_tasks_file()

            if "extensions" in components:
                success &= self.extensions.create_extensions_file()

            return success

        except Exception:
            return False

    def cleanup_workspace(self, remove_vscode_dir: bool = False) -> bool:
        """Clean up workspace configuration.

        Args:
            remove_vscode_dir: Whether to remove the entire .vscode directory

        Returns:
            True if cleanup was successful
        """
        try:
            if remove_vscode_dir and self.vscode_dir.exists():
                import shutil

                shutil.rmtree(self.vscode_dir)
            else:
                # Remove individual files
                for path in [
                    self.settings.settings_path,
                    self.launch.launch_path,
                    self.tasks.tasks_path,
                    self.extensions.extensions_path,
                ]:
                    if path.exists():
                        path.unlink()

            return True

        except Exception:
            return False

    # Compatibility methods for the interface
    def get_python_extensions(self) -> list[str]:
        """Get Python-specific extensions."""
        return self.extensions.get_python_extensions()

    def get_python_tasks(self) -> dict[str, Any]:
        """Get Python-specific task definitions."""
        return {"tasks": self.tasks.get_task_definitions()}

    def get_python_launch_configs(self) -> dict[str, Any]:
        """Get Python debug configurations."""
        return {"configurations": self.launch.get_debug_configurations()}

    def create_all_configurations(self, **kwargs) -> bool:
        """Create all VS Code configurations."""
        return self.create_workspace_configuration(**kwargs)

    def validate_all_configurations(self) -> ValidationDetails:
        """Validate all VS Code configurations."""
        return self.validate_workspace()
