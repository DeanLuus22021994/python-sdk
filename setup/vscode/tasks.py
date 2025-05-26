# filepath: c:\Projects\python-sdk\setup\vscode\tasks.py
"""
VS Code tasks configuration manager.

Handles creation and management of VS Code tasks.json with build, test, and
development tasks optimized for Python projects using modern tools.
"""

import json
from pathlib import Path
from typing import Any

from ..types import ValidationDetails, ValidationStatus


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
                "problemMatcher": [
                    "$pytest",
                ],
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
                "problemMatcher": [
                    "$pytest",
                ],
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
                "problemMatcher": [
                    "$mypy",
                ],
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
                    "import shutil; import os; [shutil.rmtree(p, ignore_errors=True) for p in ['build', 'dist', 'htmlcov', '.pytest_cache', '.mypy_cache'] if os.path.exists(p)]",
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
                "problemMatcher": [],
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
                    "import subprocess; import sys; "
                    + "commands = ["
                    + "['uv', 'run', 'black', '--check', 'src/', 'tests/', 'setup/'], "
                    + "['uv', 'run', 'isort', '--check-only', 'src/', 'tests/', 'setup/'], "
                    + "['uv', 'run', 'ruff', 'check', 'src/', 'tests/', 'setup/'], "
                    + "['uv', 'run', 'mypy', 'src/'], "
                    + "['uv', 'run', 'pytest', 'tests/', '--cov=src/mcp']"
                    + "]; "
                    + "[subprocess.run(cmd, check=True) for cmd in commands]",
                ],
                "group": "test",
                "presentation": {
                    "echo": True,
                    "reveal": "always",
                    "panel": "shared",
                },
                "problemMatcher": [
                    "$pytest",
                    "$mypy",
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
        return {
            "version": "2.0.0",
            "tasks": self.get_task_definitions(),
        }

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

            # Check if we have basic development tasks
            tasks = existing_config.get("tasks", [])
            task_labels = [task.get("label", "") for task in tasks]

            essential_tasks = [
                "Run Tests",
                "Format Code",
                "Lint Code",
            ]

            has_essential = all(
                any(essential in label for label in task_labels)
                for essential in essential_tasks
            )

            # Update if missing essential tasks
            return not has_essential

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
                return json.load(f)
        except (json.JSONDecodeError, Exception):
            return {}

    def add_task(self, task: dict[str, Any]) -> bool:
        """Add a task to the configuration.

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
                current["version"] = "2.0.0"

            tasks = current["tasks"]

            # Check if task with same label already exists
            task_label = task.get("label", "")
            existing_labels = [t.get("label", "") for t in tasks]

            if task_label not in existing_labels:
                tasks.append(task)

                # Ensure .vscode directory exists
                self.vscode_dir.mkdir(exist_ok=True)

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

        warnings = []
        errors = []
        recommendations = []

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
            warnings.append(f"Tasks config version should be '2.0.0', found: {version}")

        # Check tasks
        tasks = config.get("tasks", [])
        if not tasks:
            warnings.append("No tasks found")
        elif not isinstance(tasks, list):
            errors.append("Tasks must be a list")
        else:
            # Validate individual tasks
            for i, task in enumerate(tasks):
                if not isinstance(task, dict):
                    errors.append(f"Task {i} must be a dictionary")
                    continue

                # Check required fields
                required_fields = ["label", "type"]
                for field in required_fields:
                    if field not in task:
                        errors.append(
                            f"Task '{task.get('label', i)}' missing required field: {field}"
                        )

                # Check task type
                task_type = task.get("type")
                if task_type not in ["shell", "process"]:
                    warnings.append(
                        f"Task '{task.get('label')}' has unusual type: {task_type}"
                    )

                # Check for command if shell type
                if task_type == "shell" and "command" not in task:
                    errors.append(f"Shell task '{task.get('label')}' missing command")

                # Check for problem matchers on build/test tasks
                group = task.get("group", "")
                if isinstance(group, dict):
                    group = group.get("kind", "")

                if group in ["build", "test"] and not task.get("problemMatcher"):
                    recommendations.append(
                        f"Consider adding problem matchers to '{task.get('label')}'"
                    )

        # Check for essential tasks
        task_labels = [task.get("label", "") for task in tasks]
        essential_tasks = [
            "Run Tests",
            "Format Code",
            "Lint Code",
        ]

        missing_essential = []
        for essential in essential_tasks:
            if not any(essential in label for label in task_labels):
                missing_essential.append(essential)

        if missing_essential:
            warnings.append(f"Missing essential tasks: {', '.join(missing_essential)}")
            recommendations.append("Add missing essential development tasks")

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

        return ValidationDetails(
            is_valid=is_valid,
            status=status,
            message=message,
            warnings=warnings,
            errors=errors,
            recommendations=recommendations,
            metadata={
                "tasks_count": len(tasks),
                "file_exists": self.tasks_path.exists(),
                "version": version,
                "missing_essential": len(missing_essential),
            },
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

                # Merge tasks lists
                if "tasks" in updates:
                    current_tasks = current.get("tasks", [])
                    new_tasks = updates["tasks"]

                    # Merge by label, preferring new tasks
                    merged_tasks = []
                    existing_labels = set()

                    # Add new tasks first
                    for new_task in new_tasks:
                        label = new_task.get("label", "")
                        merged_tasks.append(new_task)
                        existing_labels.add(label)

                    # Add existing tasks that don't conflict
                    for existing_task in current_tasks:
                        label = existing_task.get("label", "")
                        if label not in existing_labels:
                            merged_tasks.append(existing_task)

                    current["tasks"] = merged_tasks

                # Update version if provided
                if "version" in updates:
                    current["version"] = updates["version"]

                config = current
            else:
                config = updates

            # Ensure .vscode directory exists
            self.vscode_dir.mkdir(exist_ok=True)

            # Write updated configuration
            with open(self.tasks_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)

            return True
        except Exception:
            return False
