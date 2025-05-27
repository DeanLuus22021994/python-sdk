"""
VS Code tasks configuration manager.

Handles creation and management of VS Code tasks.json with build, test, and
development tasks optimized for Python projects using modern tools.
"""

import json
from pathlib import Path
from typing import Any

from ..typings import ValidationDetails, ValidationStatus


class VSCodeTasksManager:
    """Manages VS Code tasks.json configuration."""

    def __init__(self, project_root: Path) -> None:
        """Initialize the tasks manager.

        Args:
            project_root: Path to the project root directory
        """
        self.project_root = project_root
        self.vscode_dir = project_root / ".vscode"
        self.tasks_path = self.vscode_dir / "tasks.json"

    def get_task_definitions(self) -> list[dict[str, Any]]:
        """Get task definitions for Python development.

        Returns:
            List of task definition dictionaries
        """
        return [
            {
                "label": "Install Dependencies",
                "type": "shell",
                "command": "uv",
                "args": ["sync"],
                "group": "build",
                "presentation": {
                    "echo": True,
                    "reveal": "always",
                    "panel": "shared",
                    "clear": False,
                },
                "problemMatcher": [],
                "detail": "Install project dependencies using uv",
            },
            {
                "label": "Run Tests",
                "type": "shell",
                "command": "uv",
                "args": ["run", "pytest", "tests/", "-v"],
                "group": {
                    "kind": "test",
                    "isDefault": True,
                },
                "presentation": {
                    "echo": True,
                    "reveal": "always",
                    "panel": "shared",
                },
                "problemMatcher": ["$python"],
                "detail": "Run all tests with verbose output",
            },
            {
                "label": "Run Tests with Coverage",
                "type": "shell",
                "command": "uv",
                "args": [
                    "run",
                    "pytest",
                    "tests/",
                    "--cov=src/mcp",
                    "--cov-report=html",
                    "--cov-report=term",
                ],
                "group": "test",
                "presentation": {
                    "echo": True,
                    "reveal": "always",
                    "panel": "shared",
                },
                "problemMatcher": ["$python"],
                "detail": "Run tests with coverage report",
            },
            {
                "label": "Format Code",
                "type": "shell",
                "command": "uv",
                "args": ["run", "black", "src/", "tests/", "setup/"],
                "group": "build",
                "presentation": {
                    "echo": True,
                    "reveal": "silent",
                    "panel": "shared",
                },
                "problemMatcher": [],
                "detail": "Format code using Black",
            },
            {
                "label": "Sort Imports",
                "type": "shell",
                "command": "uv",
                "args": ["run", "isort", "src/", "tests/", "setup/"],
                "group": "build",
                "presentation": {
                    "echo": True,
                    "reveal": "silent",
                    "panel": "shared",
                },
                "problemMatcher": [],
                "detail": "Sort imports using isort",
            },
            {
                "label": "Lint Code",
                "type": "shell",
                "command": "uv",
                "args": ["run", "ruff", "check", "src/", "tests/", "setup/"],
                "group": "build",
                "presentation": {
                    "echo": True,
                    "reveal": "always",
                    "panel": "shared",
                },
                "problemMatcher": [
                    {
                        "owner": "ruff",
                        "fileLocation": ["relative", "${workspaceFolder}"],
                        "pattern": {
                            "regexp": "^(.+?):(\\d+):(\\d+): (\\w+) (.+) \\((.+)\\)$",
                            "file": 1,
                            "line": 2,
                            "column": 3,
                            "severity": 4,
                            "message": 5,
                            "code": 6,
                        },
                    }
                ],
                "detail": "Lint code using Ruff",
            },
            {
                "label": "Fix Lint Issues",
                "type": "shell",
                "command": "uv",
                "args": ["run", "ruff", "check", "--fix", "src/", "tests/", "setup/"],
                "group": "build",
                "presentation": {
                    "echo": True,
                    "reveal": "always",
                    "panel": "shared",
                },
                "problemMatcher": [
                    {
                        "owner": "ruff",
                        "fileLocation": ["relative", "${workspaceFolder}"],
                        "pattern": {
                            "regexp": "^(.+?):(\\d+):(\\d+): (\\w+) (.+) \\((.+)\\)$",
                            "file": 1,
                            "line": 2,
                            "column": 3,
                            "severity": 4,
                            "message": 5,
                            "code": 6,
                        },
                    }
                ],
                "detail": "Auto-fix lint issues using Ruff",
            },
            {
                "label": "Type Check",
                "type": "shell",
                "command": "uv",
                "args": ["run", "mypy", "src/"],
                "group": "build",
                "presentation": {
                    "echo": True,
                    "reveal": "always",
                    "panel": "shared",
                },
                "problemMatcher": ["$python"],
                "detail": "Run type checking with MyPy",
            },
            {
                "label": "Build Documentation",
                "type": "shell",
                "command": "uv",
                "args": ["run", "mkdocs", "build"],
                "group": "build",
                "presentation": {
                    "echo": True,
                    "reveal": "always",
                    "panel": "shared",
                },
                "problemMatcher": [],
                "detail": "Build documentation using MkDocs",
            },
            {
                "label": "Serve Documentation",
                "type": "shell",
                "command": "uv",
                "args": ["run", "mkdocs", "serve"],
                "group": "build",
                "presentation": {
                    "echo": True,
                    "reveal": "always",
                    "panel": "shared",
                },
                "isBackground": True,
                "problemMatcher": [],
                "detail": "Serve documentation locally with live reload",
            },
            {
                "label": "Clean Build Artifacts",
                "type": "shell",
                "command": "python",
                "args": [
                    "-c",
                    (
                        "import shutil; import os; "
                        "[shutil.rmtree(p, ignore_errors=True) for p in "
                        "['build', 'dist', 'htmlcov', '.pytest_cache', '.mypy_cache'] "
                        "if os.path.exists(p)]"
                    ),
                ],
                "group": "build",
                "presentation": {
                    "echo": True,
                    "reveal": "silent",
                    "panel": "shared",
                },
                "problemMatcher": [],
                "detail": "Clean build artifacts and cache directories",
            },
            {
                "label": "Run Setup Script",
                "type": "shell",
                "command": "uv",
                "args": ["run", "python", "setup.py"],
                "group": "build",
                "presentation": {
                    "echo": True,
                    "reveal": "always",
                    "panel": "shared",
                },
                "problemMatcher": ["$python"],
                "detail": "Run the setup script",
            },
            {
                "label": "Full CI Check",
                "type": "shell",
                "command": "uv",
                "args": [
                    "run",
                    "python",
                    "-c",
                    (
                        "import subprocess; import sys; "
                        "commands = ["
                        "['uv', 'run', 'black', '--check', 'src/', 'tests/', 'setup/'], "
                        "['uv', 'run', 'isort', '--check-only', 'src/', 'tests/', 'setup/'], "
                        "['uv', 'run', 'ruff', 'check', 'src/', 'tests/', 'setup/'], "
                        "['uv', 'run', 'mypy', 'src/'], "
                        "['uv', 'run', 'pytest', 'tests/', '--cov=src/mcp']"
                        "]; "
                        "[subprocess.run(cmd, check=True) for cmd in commands]"
                    ),
                ],
                "group": "test",
                "presentation": {
                    "echo": True,
                    "reveal": "always",
                    "panel": "shared",
                },
                "problemMatcher": [
                    "$python",
                    {
                        "owner": "ruff",
                        "fileLocation": ["relative", "${workspaceFolder}"],
                        "pattern": {
                            "regexp": "^(.+?):(\\d+):(\\d+): (\\w+) (.+) \\((.+)\\)$",
                            "file": 1,
                            "line": 2,
                            "column": 3,
                            "severity": 4,
                            "message": 5,
                            "code": 6,
                        },
                    },
                ],
                "detail": "Run complete CI pipeline checks",
            },
        ]

    def get_tasks_config(self) -> dict[str, Any]:
        """Get complete tasks configuration.

        Returns:
            Dictionary containing tasks configuration
        """
        config: dict[str, Any] = {
            "version": "2.0.0",
            "tasks": self.get_task_definitions(),
        }
        return config

    def create_tasks_file(self) -> bool:
        """Create VS Code tasks.json file.

        Returns:
            True if file was created successfully, False otherwise
        """
        try:
            # Ensure .vscode directory exists
            self.vscode_dir.mkdir(exist_ok=True)

            # Get tasks configuration
            config = self.get_tasks_config()

            # Write tasks file with proper formatting
            with open(self.tasks_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)

            return True
        except Exception:
            return False

    def should_create_tasks(self) -> bool:
        """Check if tasks.json should be created or updated.

        Returns:
            True if tasks file should be created/updated
        """
        if not self.tasks_path.exists():
            return True

        try:
            with open(self.tasks_path, encoding="utf-8") as f:
                existing_config = json.load(f)

            # Check if we have basic task definitions
            tasks = existing_config.get("tasks", [])
            has_test_task = any(
                "test" in task.get("label", "").lower() for task in tasks
            )
            has_build_task = any(
                task.get("group") == "build"
                or (
                    isinstance(task.get("group"), dict)
                    and task.get("group", {}).get("kind") == "build"
                )
                for task in tasks
            )

            # Update if missing essential task types
            return not (has_test_task and has_build_task)

        except (json.JSONDecodeError, Exception):
            return True  # File exists but is invalid

    def get_current_tasks(self) -> dict[str, Any]:
        """Get current VS Code tasks configuration.

        Returns:
            Dictionary with current tasks config or empty dict
        """
        if not self.tasks_path.exists():
            return {}

        try:
            with open(self.tasks_path, encoding="utf-8") as f:
                config: dict[str, Any] = json.load(f)
                return config
        except (json.JSONDecodeError, Exception):
            return {}

    def add_task(self, task: dict[str, Any]) -> bool:
        """Add a task definition.

        Args:
            task: Task definition to add

        Returns:
            True if task was added successfully
        """
        try:
            current = self.get_current_tasks()

            # Initialize tasks if not present
            if "tasks" not in current:
                current["tasks"] = []

            tasks = current["tasks"]

            # Check if task with same label already exists
            task_label = task.get("label", "")
            existing_labels = [t.get("label", "") for t in tasks]

            if task_label not in existing_labels:
                tasks.append(task)

                # Write updated configuration
                with open(self.tasks_path, "w", encoding="utf-8") as f:
                    json.dump(current, f, indent=2)

            return True
        except Exception:
            return False

    def remove_task(self, label: str) -> bool:
        """Remove a task by label.

        Args:
            label: Label of the task to remove

        Returns:
            True if task was removed successfully
        """
        try:
            current = self.get_current_tasks()
            tasks = current.get("tasks", [])

            # Filter out the task to remove
            updated_tasks = [task for task in tasks if task.get("label") != label]

            if len(updated_tasks) != len(tasks):
                current["tasks"] = updated_tasks

                # Write updated configuration
                with open(self.tasks_path, "w", encoding="utf-8") as f:
                    json.dump(current, f, indent=2)

            return True
        except Exception:
            return False

    def validate_tasks(self, config: dict[str, Any] | None = None) -> ValidationDetails:
        """Validate VS Code tasks configuration.

        Args:
            config: Tasks config to validate, uses current if None

        Returns:
            ValidationDetails with validation results
        """
        if config is None:
            config = self.get_current_tasks()

        warnings: list[str] = []
        errors: list[str] = []
        recommendations: list[str] = []

        # Validate structure
        if not isinstance(config, dict):
            errors.append("Tasks configuration must be a dictionary")
            return ValidationDetails(
                is_valid=False,
                status=ValidationStatus.ERROR,
                message="Invalid tasks configuration structure",
                warnings=warnings,
                errors=errors,
                recommendations=recommendations,
                metadata={"file_exists": self.tasks_path.exists()},
            )

        # Check version
        version = config.get("version")
        if version != "2.0.0":
            warnings.append(f"Unexpected version: {version}, expected 2.0.0")

        # Check tasks
        tasks = config.get("tasks", [])
        if not tasks:
            warnings.append("No tasks found")
            recommendations.append("Add basic Python development tasks")
        elif not isinstance(tasks, list):
            errors.append("Tasks must be a list")
        else:
            # Validate each task has required fields
            for i, task in enumerate(tasks):
                if not isinstance(task, dict):
                    errors.append(f"Task {i} is not a dictionary")
                    continue

                required_fields = ["label", "type"]
                missing = [field for field in required_fields if field not in task]
                if missing:
                    errors.append(
                        f"Task '{task.get('label', f'at index {i}')}' "
                        f"is missing required fields: {', '.join(missing)}"
                    )

        # Check for essential task types
        task_types: list[str] = []
        for task in tasks:
            group = task.get("group", "")
            if isinstance(group, dict):
                task_types.append(group.get("kind", ""))
            else:
                task_types.append(str(group))

        has_build = "build" in task_types
        has_test = "test" in task_types

        if not has_build:
            warnings.append("Missing build task type")
            recommendations.append("Add tasks with 'build' group")

        if not has_test:
            warnings.append("Missing test task type")
            recommendations.append("Add tasks with 'test' group")

        # Validate JSON structure
        try:
            json.dumps(config)
        except (TypeError, ValueError) as e:
            errors.append(f"Invalid JSON structure: {e}")

        # Determine overall status
        if errors:
            status = ValidationStatus.ERROR
            is_valid = False
            message = f"Tasks validation failed with {len(errors)} errors"
        elif warnings:
            status = ValidationStatus.WARNING
            is_valid = True
            message = f"Tasks validation passed with {len(warnings)} warnings"
        else:
            status = ValidationStatus.VALID
            is_valid = True
            message = "Tasks validation passed successfully"

        metadata: dict[str, str | int | bool | None] = {
            "tasks_count": len(tasks),
            "file_exists": self.tasks_path.exists(),
            "version": str(version) if version is not None else None,
            "has_build": has_build,
            "has_test": has_test,
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

    def update_tasks(self, updates: dict[str, Any], merge: bool = True) -> bool:
        """Update VS Code tasks configuration.

        Args:
            updates: Tasks updates to apply
            merge: Whether to merge with existing config or replace

        Returns:
            True if update was successful
        """
        try:
            if merge:
                current = self.get_current_tasks()

                # Merge tasks
                if "tasks" in updates:
                    current_tasks = {
                        task.get("label"): task
                        for task in current.get("tasks", [])
                        if "label" in task
                    }

                    # Add or update tasks
                    for task in updates["tasks"]:
                        label = task.get("label")
                        if label:
                            current_tasks[label] = task

                    current["tasks"] = list(current_tasks.values())

                # Set version if provided
                if "version" in updates:
                    current["version"] = updates["version"]

                config_to_write = current
            else:
                config_to_write = updates

            # Ensure .vscode directory exists
            self.vscode_dir.mkdir(exist_ok=True)

            # Write updated configuration
            with open(self.tasks_path, "w", encoding="utf-8") as f:
                json.dump(config_to_write, f, indent=2)

            return True
        except Exception:
            return False
