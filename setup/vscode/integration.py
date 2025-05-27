"""
VS Code Integration Manager
Comprehensive VS Code workspace configuration and management.
"""

from pathlib import Path
from typing import Any

from ..typings import ValidationDetails, ValidationStatus
from ..validation.base import ValidationContext
from ..validation.registry import get_global_registry
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
            force_overwrite: Overwrite existing configurations
            include_optional: Include optional configurations
            custom_config: Custom configuration overrides

        Returns:
            True if configuration was created successfully
        """
        try:
            # Ensure .vscode directory exists
            self.vscode_dir.mkdir(exist_ok=True)

            success = True

            # Create core configurations
            success &= self.settings.create_settings_file() or not force_overwrite
            success &= self.tasks.create_tasks_file() or not force_overwrite
            success &= self.launch.create_launch_file() or not force_overwrite

            if include_optional:
                success &= (
                    self.extensions.create_extensions_file() or not force_overwrite
                )

            return success

        except Exception:
            return False

    def _safe_get_int(
        self, metadata: dict[str, str | int | bool | None], key: str, default: int = 0
    ) -> int:
        """Safely extract integer from metadata.

        Args:
            metadata: Metadata dictionary
            key: Key to extract
            default: Default value if key is missing or not convertible

        Returns:
            Integer value
        """
        value = metadata.get(key, default)
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                return default
        if isinstance(value, bool):
            return int(value)
        return default

    def _safe_convert_metadata(
        self, metadata: dict[str, str | int | bool | None]
    ) -> dict[str, str | int | bool | None]:
        """Safely convert metadata values for ValidationDetails.

        Args:
            metadata: Input metadata dictionary

        Returns:
            Safely converted metadata dictionary
        """
        converted_metadata: dict[str, str | int | bool | None] = {}
        for k, v in metadata.items():
            if isinstance(v, int | float | bool | str):
                if isinstance(v, float):
                    converted_metadata[k] = int(v) if v.is_integer() else str(v)
                else:
                    converted_metadata[k] = v
            elif v is None:
                converted_metadata[k] = None
            else:
                converted_metadata[k] = bool(v)
        return converted_metadata

    def validate_workspace(self) -> ValidationDetails:
        """Validate complete VS Code workspace configuration.

        Returns:
            ValidationDetails with overall validation results
        """
        # Use the validation framework
        context = ValidationContext(
            workspace_root=str(self.workspace_root),
            environment={},
            config={"component": "vscode"},
        )

        registry = get_global_registry()

        try:
            validator = registry.create_validator("vscode_workspace", context)
            result = validator.validate()

            # Safely convert metadata
            safe_metadata = self._safe_convert_metadata(result.metadata)

            return ValidationDetails(
                is_valid=result.is_valid,
                status=result.status,
                message=result.message,
                warnings=list(result.warnings),
                errors=list(result.errors),
                recommendations=list(result.recommendations),
                metadata=safe_metadata,
                component_name="VSCode",
            )

        except ValueError:
            # Fallback to component-level validation
            return self._validate_workspace_components()

    def _validate_workspace_components(self) -> ValidationDetails:
        """Fallback validation using component managers."""
        # Collect validation results from all components
        extensions_validation = self.extensions.validate_extensions()
        settings_validation = self.settings.validate_settings()
        tasks_validation = self.tasks.validate_tasks()
        launch_validation = self.launch.validate_launch()

        # Aggregate results
        all_warnings: list[str] = []
        all_errors: list[str] = []
        all_recommendations: list[str] = []

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

        # Collect metadata from all components with safe type conversion
        combined_metadata: dict[str, str | int | bool | None] = {
            "components_validated": len(validations),
            "extensions": self._safe_get_int(
                extensions_validation.metadata, "recommendations_count", 0
            ),
            "settings": self._safe_get_int(
                settings_validation.metadata, "settings_count", 0
            ),
            "tasks": self._safe_get_int(tasks_validation.metadata, "tasks_count", 0),
            "launch": self._safe_get_int(
                launch_validation.metadata, "configurations_count", 0
            ),
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
        """Get comprehensive workspace status."""
        validation = self.validate_workspace()

        return {
            "valid": validation.is_valid,
            "status": validation.status.name,
            "message": validation.message,
            "errors": validation.errors,
            "warnings": validation.warnings,
            "vscode_dir_exists": self.vscode_dir.exists(),
        }

    def update_workspace_config(
        self, config_updates: dict[str, Any], merge: bool = True
    ) -> bool:
        """Update workspace configuration with new values."""
        try:
            success = True

            if "settings" in config_updates:
                success &= self.settings.update_settings(
                    config_updates["settings"], merge
                )

            if "tasks" in config_updates:
                success &= self.tasks.update_tasks(config_updates["tasks"], merge)

            if "launch" in config_updates:
                success &= self.launch.update_launch(config_updates["launch"], merge)

            if "extensions" in config_updates:
                success &= self.extensions.update_extensions(
                    config_updates["extensions"], merge
                )

            return success

        except Exception:
            return False

    def export_workspace_config(self) -> dict[str, Any]:
        """Export complete workspace configuration."""
        return {
            "settings": self.settings.get_current_settings(),
            "tasks": self.tasks.get_current_tasks(),
            "launch": self.launch.get_current_launch(),
            "extensions": self.extensions.get_current_extensions(),
        }

    def reset_workspace(self, components: list[str] | None = None) -> bool:
        """Reset workspace configuration to defaults."""
        components = components or ["settings", "tasks", "launch", "extensions"]

        try:
            success = True

            if "settings" in components:
                success &= self.settings.create_settings_file()

            if "tasks" in components:
                success &= self.tasks.create_tasks_file()

            if "launch" in components:
                success &= self.launch.create_launch_file()

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
        """Get Python launch configurations."""
        return {"configurations": self.launch.get_debug_configurations()}

    def create_all_configurations(self, **kwargs: Any) -> bool:
        """Create all VS Code configurations."""
        return self.create_workspace_configuration(**kwargs)

    def validate_all_configurations(self) -> ValidationDetails:
        """Validate all VS Code configurations."""
        return self.validate_workspace()
