"""
VS Code launch configuration manager.

Handles creation and management of VS Code launch.json with debug configurations
optimized for Python development and MCP SDK testing.
"""

import json
from pathlib import Path
from typing import Any

from ..typings import ValidationDetails, ValidationStatus


class VSCodeLaunchManager:
    """Manages VS Code launch.json configuration."""

    def __init__(self, project_root: Path) -> None:
        """Initialize the launch manager.

        Args:
            project_root: Path to the project root directory
        """
        self.project_root = project_root
        self.vscode_dir = project_root / ".vscode"
        self.launch_path = self.vscode_dir / "launch.json"

    def get_debug_configurations(self) -> list[dict[str, Any]]:
        """Get debug configurations for Python development.

        Returns:
            List of debug configuration dictionaries
        """
        return [
            {
                "name": "Python: Current File",
                "type": "debugpy",
                "request": "launch",
                "program": "${file}",
                "console": "integratedTerminal",
                "cwd": "${workspaceFolder}",
                "env": {"PYTHONPATH": "${workspaceFolder}/src"},
                "justMyCode": True,
                "stopOnEntry": False,
                "showReturnValue": True,
            },
            {
                "name": "Python: Test Current File",
                "type": "debugpy",
                "request": "launch",
                "module": "pytest",
                "args": ["${file}", "--tb=short", "-v"],
                "console": "integratedTerminal",
                "cwd": "${workspaceFolder}",
                "env": {"PYTHONPATH": "${workspaceFolder}/src"},
                "justMyCode": True,
            },
            {
                "name": "Python: All Tests",
                "type": "debugpy",
                "request": "launch",
                "module": "pytest",
                "args": ["tests/", "--tb=short", "-v"],
                "console": "integratedTerminal",
                "cwd": "${workspaceFolder}",
                "env": {"PYTHONPATH": "${workspaceFolder}/src"},
                "justMyCode": True,
            },
            {
                "name": "Python: Test with Coverage",
                "type": "debugpy",
                "request": "launch",
                "module": "pytest",
                "args": ["tests/", "--cov=src/mcp", "--cov-report=term", "--tb=short"],
                "console": "integratedTerminal",
                "cwd": "${workspaceFolder}",
                "env": {"PYTHONPATH": "${workspaceFolder}/src"},
                "justMyCode": False,
            },
            {
                "name": "Python: MCP Server Example",
                "type": "debugpy",
                "request": "launch",
                "program": "${workspaceFolder}/examples/servers/simple-tool/server.py",
                "console": "integratedTerminal",
                "cwd": "${workspaceFolder}/examples/servers/simple-tool",
                "env": {"PYTHONPATH": "${workspaceFolder}/src"},
                "justMyCode": True,
            },
            {
                "name": "Python: MCP Client Example",
                "type": "debugpy",
                "request": "launch",
                "program": "${workspaceFolder}/examples/clients/simple-chatbot/client.py",
                "console": "integratedTerminal",
                "cwd": "${workspaceFolder}/examples/clients/simple-chatbot",
                "env": {"PYTHONPATH": "${workspaceFolder}/src"},
                "justMyCode": True,
            },
            {
                "name": "Python: Setup Script",
                "type": "debugpy",
                "request": "launch",
                "program": "${workspaceFolder}/setup.py",
                "console": "integratedTerminal",
                "cwd": "${workspaceFolder}",
                "env": {"PYTHONPATH": "${workspaceFolder}/src"},
                "justMyCode": True,
            },
            {
                "name": "Python: Attach to Process",
                "type": "debugpy",
                "request": "attach",
                "connect": {"host": "localhost", "port": 5678},
                "pathMappings": [
                    {"localRoot": "${workspaceFolder}", "remoteRoot": "/app"}
                ],
                "justMyCode": True,
            },
        ]

    def get_launch_config(self) -> dict[str, Any]:
        """Get complete launch configuration.

        Returns:
            Dictionary containing launch configuration
        """
        return {
            "version": "0.2.0",
            "configurations": self.get_debug_configurations(),
        }

    def create_launch_file(self) -> bool:
        """Create VS Code launch.json file.

        Returns:
            True if file was created successfully, False otherwise
        """
        try:
            # Ensure .vscode directory exists
            self.vscode_dir.mkdir(exist_ok=True)

            # Get launch configuration
            config = self.get_launch_config()

            # Write launch file with proper formatting
            with open(self.launch_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)

            return True
        except Exception:
            return False

    def should_create_launch(self) -> bool:
        """Check if launch.json should be created or updated.

        Returns:
            True if launch file should be created/updated
        """
        if not self.launch_path.exists():
            return True

        try:
            with open(self.launch_path, encoding="utf-8") as f:
                existing_config = json.load(f)

            # Check if we have basic Python configurations
            configs = existing_config.get("configurations", [])
            has_python_current = any(
                config.get("name") == "Python: Current File" for config in configs
            )
            has_test_config = any(
                "test" in config.get("name", "").lower() for config in configs
            )

            # Update if missing essential configurations
            return not (has_python_current and has_test_config)

        except (json.JSONDecodeError, Exception):
            return True  # File exists but is invalid

    def get_current_launch(self) -> dict[str, Any]:
        """Get current VS Code launch configuration.

        Returns:
            Dictionary with current launch config or empty dict
        """
        if not self.launch_path.exists():
            return {}

        try:
            with open(self.launch_path, encoding="utf-8") as f:
                current_config: dict[str, Any] = json.load(f)
                return current_config
        except (json.JSONDecodeError, Exception):
            return {}

    def add_configuration(self, config: dict[str, Any]) -> bool:
        """Add a debug configuration.

        Args:
            config: Debug configuration to add

        Returns:
            True if configuration was added successfully
        """
        try:
            current = self.get_current_launch()

            # Initialize configurations if not present
            if "configurations" not in current:
                current["configurations"] = []

            configurations = current["configurations"]

            # Check if configuration with same name already exists
            config_name = config.get("name", "")
            existing_names = [c.get("name", "") for c in configurations]

            if config_name not in existing_names:
                configurations.append(config)

                # Write updated configuration
                with open(self.launch_path, "w", encoding="utf-8") as f:
                    json.dump(current, f, indent=2)

            return True
        except Exception:
            return False

    def remove_configuration(self, name: str) -> bool:
        """Remove a debug configuration by name.

        Args:
            name: Name of the configuration to remove

        Returns:
            True if configuration was removed successfully
        """
        try:
            current = self.get_current_launch()
            configurations = current.get("configurations", [])

            # Filter out the configuration to remove
            updated_configs = [
                config for config in configurations if config.get("name") != name
            ]

            if len(updated_configs) != len(configurations):
                current["configurations"] = updated_configs

                # Write updated configuration
                with open(self.launch_path, "w", encoding="utf-8") as f:
                    json.dump(current, f, indent=2)

            return True
        except Exception:
            return False

    def validate_launch(
        self, config: dict[str, Any] | None = None
    ) -> ValidationDetails:
        """Validate VS Code launch configuration.

        Args:
            config: Launch config to validate, uses current if None

        Returns:
            ValidationDetails with validation results
        """
        if config is None:
            config = self.get_current_launch()

        warnings: list[str] = []
        errors: list[str] = []
        recommendations: list[str] = []

        # Validate structure
        if not isinstance(config, dict):
            errors.append("Launch configuration must be a dictionary")
            return ValidationDetails(
                is_valid=False,
                status=ValidationStatus.ERROR,
                message="Invalid launch configuration structure",
                warnings=warnings,
                errors=errors,
                recommendations=recommendations,
                metadata={"file_exists": self.launch_path.exists()},
            )

        # Check version
        version = config.get("version")
        if version != "0.2.0":
            warnings.append(f"Unexpected version: {version}, expected 0.2.0")

        # Check configurations
        configurations = config.get("configurations", [])
        if not configurations:
            warnings.append("No debug configurations found")
            recommendations.append("Add basic Python debug configurations")
        elif not isinstance(configurations, list):
            errors.append("Configurations must be a list")
        else:
            # Validate each configuration has required fields
            for i, cfg in enumerate(configurations):
                if not isinstance(cfg, dict):
                    errors.append(f"Configuration {i} is not a dictionary")
                    continue

                required_fields = ["name", "type", "request"]
                missing = [field for field in required_fields if field not in cfg]
                if missing:
                    errors.append(
                        f"Configuration '{cfg.get('name', f'at index {i}')}' "
                        f"is missing required fields: {', '.join(missing)}"
                    )

        # Check for essential configurations
        config_names = [cfg.get("name", "") for cfg in configurations]
        essential_configs = [
            "Python: Current File",
            "Python: All Tests",
        ]

        missing_essential = [
            conf for conf in essential_configs if conf not in config_names
        ]

        if missing_essential:
            warnings.append(
                f"Missing essential configurations: {', '.join(missing_essential)}"
            )
            recommendations.append("Add missing essential debug configurations")

        # Validate JSON structure
        try:
            json.dumps(config)
        except (TypeError, ValueError) as e:
            errors.append(f"Invalid JSON structure: {e}")

        # Determine overall status
        if errors:
            status = ValidationStatus.ERROR
            is_valid = False
            message = f"Launch validation failed with {len(errors)} errors"
        elif warnings:
            status = ValidationStatus.WARNING
            is_valid = True
            message = f"Launch validation passed with {len(warnings)} warnings"
        else:
            status = ValidationStatus.VALID
            is_valid = True
            message = "Launch validation passed successfully"

        metadata: dict[str, str | int | bool | None] = {
            "configurations_count": len(configurations),
            "file_exists": self.launch_path.exists(),
            "version": str(version) if version else None,
            "missing_essential": len(missing_essential),
        }

        return ValidationDetails(
            is_valid=is_valid,
            status=status,
            message=message,
            warnings=warnings,
            errors=errors,
            recommendations=recommendations,
            metadata=metadata,
        )

    def update_launch(self, updates: dict[str, Any], merge: bool = True) -> bool:
        """Update VS Code launch configuration.

        Args:
            updates: Launch updates to apply
            merge: Whether to merge with existing config or replace

        Returns:
            True if update was successful
        """
        try:
            if merge:
                current = self.get_current_launch()

                # Merge configurations
                if "configurations" in updates:
                    current_configs = {
                        cfg.get("name"): cfg
                        for cfg in current.get("configurations", [])
                        if "name" in cfg
                    }

                    # Add or update configurations
                    for cfg in updates["configurations"]:
                        name = cfg.get("name")
                        if name:
                            current_configs[name] = cfg

                    current["configurations"] = list(current_configs.values())

                # Set version if provided
                if "version" in updates:
                    current["version"] = updates["version"]

                config_to_write = current
            else:
                config_to_write = updates

            # Ensure .vscode directory exists
            self.vscode_dir.mkdir(exist_ok=True)

            # Write updated configuration
            with open(self.launch_path, "w", encoding="utf-8") as f:
                json.dump(config_to_write, f, indent=2)

            return True
        except Exception:
            return False
