# filepath: c:\Projects\python-sdk\setup\vscode\integration.py
"""
VS Code Integration Manager
Comprehensive VS Code workspace configuration and management.
"""

from pathlib import Path
from typing import Any

from ..types import ValidationDetails, ValidationStatus
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
        self.extensions = VSCodeExtensionsManager(self.vscode_dir)
        self.settings = VSCodeSettingsManager(self.vscode_dir)
        self.tasks = VSCodeTasksManager(self.vscode_dir)
        self.launch = VSCodeLaunchManager(self.vscode_dir)

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

            # Setup core configurations
            success_flags = []

            # Extensions recommendations
            if force_overwrite or self.extensions.should_create_extensions():
                success_flags.append(self.extensions.create_extensions_file())

            # Settings configuration
            if force_overwrite or self.settings.should_create_settings():
                if custom_config and "settings" in custom_config:
                    merged_settings = self.settings.merge_settings(
                        custom_config["settings"]
                    )
                    success_flags.append(
                        self.settings.update_settings(merged_settings, merge=False)
                    )
                else:
                    success_flags.append(self.settings.create_settings_file())

            # Task configurations
            if force_overwrite or self.tasks.should_create_tasks():
                success_flags.append(self.tasks.create_tasks_file())

            # Launch configurations (optional)
            if include_optional and (
                force_overwrite or self.launch.should_create_launch()
            ):
                success_flags.append(self.launch.create_launch_file())

            # Return True if all operations succeeded
            return all(success_flags) if success_flags else True

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
            # Prefix component name to messages for clarity
            all_warnings.extend(
                [f"{component_name}: {warning}" for warning in validation.warnings]
            )
            all_errors.extend(
                [f"{component_name}: {error}" for error in validation.errors]
            )
            all_recommendations.extend(
                [f"{component_name}: {rec}" for rec in validation.recommendations]
            )

        # Determine overall status
        if all_errors:
            status = ValidationStatus.ERROR
            is_valid = False
            message = f"Workspace validation failed with {len(all_errors)} errors"
        elif all_warnings:
            status = ValidationStatus.WARNING
            is_valid = True
            message = f"Workspace validation passed with {len(all_warnings)} warnings"
        else:
            status = ValidationStatus.VALID
            is_valid = True
            message = "Workspace validation passed successfully"

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
            "workspace_directory": str(self.vscode_dir),
            "workspace_exists": self.vscode_dir.exists(),
            "components": {
                "extensions": {
                    "file_exists": self.extensions.extensions_path.exists(),
                    "should_create": self.extensions.should_create_extensions(),
                    "validation": self.extensions.validate_extensions(),
                },
                "settings": {
                    "file_exists": self.settings.settings_path.exists(),
                    "should_create": self.settings.should_create_settings(),
                    "validation": self.settings.validate_settings(),
                },
                "tasks": {
                    "file_exists": self.tasks.tasks_path.exists(),
                    "should_create": self.tasks.should_create_tasks(),
                    "validation": self.tasks.validate_tasks(),
                },
                "launch": {
                    "file_exists": self.launch.launch_path.exists(),
                    "should_create": self.launch.should_create_launch(),
                    "validation": self.launch.validate_launch(),
                },
            },
        }

    def update_workspace_config(
        self, config_updates: dict[str, Any], merge: bool = True
    ) -> bool:
        """Update workspace configuration with new values.

        Args:
            config_updates: Configuration updates to apply
            merge: Whether to merge with existing configurations

        Returns:
            True if all updates were successful
        """
        try:
            success_flags = []

            # Update extensions if provided
            if "extensions" in config_updates:
                success_flags.append(
                    self.extensions.update_extensions(
                        config_updates["extensions"], merge=merge
                    )
                )

            # Update settings if provided
            if "settings" in config_updates:
                success_flags.append(
                    self.settings.update_settings(
                        config_updates["settings"], merge=merge
                    )
                )

            # Update tasks if provided
            if "tasks" in config_updates:
                success_flags.append(
                    self.tasks.update_tasks(config_updates["tasks"], merge=merge)
                )

            # Update launch if provided
            if "launch" in config_updates:
                success_flags.append(
                    self.launch.update_launch(config_updates["launch"], merge=merge)
                )

            return all(success_flags) if success_flags else True

        except Exception:
            return False

    def export_workspace_config(self) -> dict[str, Any]:
        """Export current workspace configuration.

        Returns:
            Dictionary containing all workspace configurations
        """
        return {
            "extensions": self.extensions.get_current_extensions(),
            "settings": self.settings.get_current_settings(),
            "tasks": self.tasks.get_current_tasks(),
            "launch": self.launch.get_current_launch(),
        }

    def reset_workspace(self, components: list[str] | None = None) -> bool:
        """Reset workspace configuration to defaults.

        Args:
            components: Specific components to reset, all if None

        Returns:
            True if reset was successful
        """
        try:
            target_components = components or [
                "extensions",
                "settings",
                "tasks",
                "launch",
            ]

            success_flags = []

            for component in target_components:
                if component == "extensions":
                    success_flags.append(self.extensions.create_extensions_file())
                elif component == "settings":
                    success_flags.append(self.settings.create_settings_file())
                elif component == "tasks":
                    success_flags.append(self.tasks.create_tasks_file())
                elif component == "launch":
                    success_flags.append(self.launch.create_launch_file())

            return all(success_flags)

        except Exception:
            return False

    def cleanup_workspace(self, remove_vscode_dir: bool = False) -> bool:
        """Clean up workspace configuration files.

        Args:
            remove_vscode_dir: Whether to remove entire .vscode directory

        Returns:
            True if cleanup was successful
        """
        try:
            if remove_vscode_dir and self.vscode_dir.exists():
                import shutil

                shutil.rmtree(self.vscode_dir)
                return True

            # Remove individual files
            files_to_remove = [
                self.extensions.extensions_path,
                self.settings.settings_path,
                self.tasks.tasks_path,
                self.launch.launch_path,
            ]

            for file_path in files_to_remove:
                if file_path.exists():
                    file_path.unlink()

            return True

        except Exception:
            return False

    # Add the missing methods that are being called
    def get_python_extensions(self) -> list[str]:
        """Get Python-related extensions for this workspace."""
        return self.extensions.get_python_extensions()

    def get_python_tasks(self) -> dict[str, Any]:
        """Get Python-related tasks for this workspace."""
        return self.tasks.get_python_tasks()

    def get_python_launch_configs(self) -> dict[str, Any]:
        """Get Python launch configurations for this workspace."""
        return self.launch.get_python_launch_configs()

    def create_all_configurations(self, **kwargs) -> bool:
        """Create all VS Code configurations."""
        return self.create_workspace_configuration(**kwargs)

    def validate_all_configurations(self) -> ValidationDetails:
        """Validate all VS Code configurations."""
        return self.validate_workspace()
