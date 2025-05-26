"""
VS Code integration manager.

Coordinates the creation and management of all VS Code configuration files
to provide a comprehensive Python development environment.
"""

from pathlib import Path
from typing import Any

from ..types import ValidationDetails, ValidationStatus
from .extensions import VSCodeExtensionsManager
from .launch import VSCodeLaunchManager
from .settings import VSCodeSettingsManager
from .tasks import VSCodeTasksManager


class VSCodeIntegrationManager:
    """Manages VS Code integration for Python projects."""

    def __init__(self, project_root: Path) -> None:
        """Initialize the integration manager.

        Args:
            project_root: Path to the project root directory
        """
        self.project_root = project_root
        self.vscode_dir = project_root / ".vscode"

        # Initialize component managers
        self.extensions = VSCodeExtensionsManager(project_root)
        self.settings = VSCodeSettingsManager(project_root)
        self.tasks = VSCodeTasksManager(project_root)
        self.launch = VSCodeLaunchManager(project_root)

    def setup_workspace(
        self,
        force_overwrite: bool = False,
        include_optional: bool = True,
        custom_config: dict[str, Any] | None = None,
    ) -> bool:
        """Set up complete VS Code workspace configuration.

        Args:
            force_overwrite: Whether to overwrite existing files
            include_optional: Whether to include optional configurations
            custom_config: Custom configuration overrides

        Returns:
            True if setup was successful
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

    def create_workspace_template(
        self, template_name: str = "python-mcp"
    ) -> dict[str, Any]:
        """Create a workspace configuration template.

        Args:
            template_name: Name of the template to create

        Returns:
            Template configuration dictionary
        """
        base_template = {
            "name": template_name,
            "description": "Modern Python development workspace for MCP SDK",
            "extensions": self.extensions.get_python_extensions(),
            "settings": self.settings.get_modern_settings(),
            "tasks": self.tasks.get_python_tasks(),
            "launch": self.launch.get_python_launch_configs(),
        }

        # Add template-specific customizations
        if template_name == "python-mcp":
            base_template["settings"].update(
                {
                    "python.analysis.extraPaths": ["src", "examples"],
                    "python.testing.pytestArgs": [
                        "tests/",
                        "-v",
                        "--tb=short",
                        "--cov=src",
                        "--cov-report=html",
                    ],
                }
            )

        return base_template
