"""
Setup System Validators
Concrete validators for the MCP Python SDK setup system.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

import tomllib

from .typings.enums import ValidationStatus
from .validation.base import BaseValidator, ValidationResult
from .validation.registry import register_validator


@register_validator("python_environment")
class PythonEnvironmentValidator(BaseValidator[dict[str, Any]]):
    """
    Validates Python environment requirements.

    Follows SRP by focusing solely on Python validation.
    """

    def get_validator_name(self) -> str:
        """Get validator name."""
        return "Python Environment"

    def _perform_validation(self) -> ValidationResult[dict[str, Any]]:
        """Validate Python environment."""
        errors: list[str] = []
        warnings: list[str] = []
        recommendations: list[str] = []
        metadata: dict[str, Any] = {}

        # Check Python version
        version_info = sys.version_info
        python_version = (
            f"{version_info.major}.{version_info.minor}.{version_info.micro}"
        )
        metadata["python_version"] = python_version
        metadata["python_executable"] = sys.executable

        # Minimum version check (3.10+)
        if version_info < (3, 10):
            errors.append(
                f"Python {python_version} is not supported. "
                "Please upgrade to Python 3.10 or higher."
            )
        elif version_info < (3, 11):
            warnings.append(
                f"Python {python_version} is supported but 3.11+ is recommended"
            )
            recommendations.append(
                "Consider upgrading to Python 3.11 for better performance"
            )

        # Check if virtual environment is active
        in_venv = hasattr(sys, "real_prefix") or (
            hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
        )
        metadata["in_virtual_environment"] = in_venv

        if not in_venv:
            warnings.append("Not running in virtual environment")
            recommendations.append("Use virtual environment for better isolation")

        # Determine overall status
        if errors:
            status = ValidationStatus.ERROR
            is_valid = False
            message = f"Python environment validation failed: {len(errors)} error(s)"
        elif warnings:
            status = ValidationStatus.WARNING
            is_valid = True
            message = f"Python environment has {len(warnings)} warning(s)"
        else:
            status = ValidationStatus.VALID
            is_valid = True
            message = "Python environment is valid"

        return self._create_result(
            is_valid=is_valid,
            status=status,
            message=message,
            data=metadata,
            errors=errors,
            warnings=warnings,
            recommendations=recommendations,
        )


@register_validator("project_structure")
class ProjectStructureValidator(BaseValidator[dict[str, Any]]):
    """
    Validates project directory structure.

    Follows SRP by focusing on project structure validation.
    """

    def get_validator_name(self) -> str:
        """Get validator name."""
        return "Project Structure"

    def _perform_validation(self) -> ValidationResult[dict[str, Any]]:
        """Validate project structure."""
        errors: list[str] = []
        warnings: list[str] = []
        recommendations: list[str] = []

        workspace_root = Path(self.context.workspace_root)
        required_paths = [
            "src",
            "src/mcp",
            "setup",
            "tests",
            "pyproject.toml",
        ]

        optional_paths = [
            "docs",
            "examples",
            ".github",
            "README.md",
            "LICENSE",
        ]

        found_paths: list[str] = []
        missing_required: list[str] = []
        missing_optional: list[str] = []

        # Check required paths
        for path_str in required_paths:
            path = workspace_root / path_str
            if path.exists():
                found_paths.append(path_str)
            else:
                missing_required.append(path_str)
                errors.append(f"Required path missing: {path_str}")

        # Check optional paths
        for path_str in optional_paths:
            path = workspace_root / path_str
            if path.exists():
                found_paths.append(path_str)
            else:
                missing_optional.append(path_str)

        # Add recommendations for missing optional paths
        if "docs" in missing_optional:
            recommendations.append("Consider adding documentation directory")
        if "examples" in missing_optional:
            recommendations.append("Consider adding examples for better usability")

        # Determine overall status
        if missing_required:
            status = ValidationStatus.ERROR
            is_valid = False
            message = f"Project structure invalid: {len(missing_required)} required paths missing"
        elif missing_optional:
            status = ValidationStatus.WARNING
            is_valid = True
            message = f"Project structure valid with {len(missing_optional)} optional improvements"
        else:
            status = ValidationStatus.VALID
            is_valid = True
            message = "Project structure is complete"

        return self._create_result(
            is_valid=is_valid,
            status=status,
            message=message,
            data={
                "found_paths": found_paths,
                "missing_required": missing_required,
                "missing_optional": missing_optional,
            },
            errors=errors,
            warnings=warnings,
            recommendations=recommendations,
        )


@register_validator("dependencies")
class DependencyValidator(BaseValidator[dict[str, Any]]):
    """
    Validates project dependencies and package configuration.

    Follows SRP by focusing on dependency validation.
    """

    def get_validator_name(self) -> str:
        """Get validator name."""
        return "Project Dependencies"

    def _perform_validation(self) -> ValidationResult[dict[str, Any]]:
        """Validate dependencies."""
        errors: list[str] = []
        warnings: list[str] = []
        recommendations: list[str] = []
        metadata: dict[str, Any] = {
            "dependencies_count": 0,
            "has_dev_dependencies": False,
        }

        workspace_root = Path(self.context.workspace_root)
        pyproject_path = workspace_root / "pyproject.toml"

        if not pyproject_path.exists():
            errors.append("pyproject.toml file not found")
            return self._create_result(
                is_valid=False,
                status=ValidationStatus.ERROR,
                message="Dependencies validation failed: pyproject.toml missing",
                data=metadata,
                errors=errors,
            )

        try:
            with open(pyproject_path, "rb") as f:
                pyproject_data = tomllib.load(f)

            # Check for required sections
            required_sections = ["project", "build-system"]
            missing_sections = []

            for section in required_sections:
                if section not in pyproject_data:
                    missing_sections.append(section)
                    errors.append(
                        f"Required section '[{section}]' missing from pyproject.toml"
                    )

            # Check project metadata
            project_data = pyproject_data.get("project", {})
            required_fields = ["name", "version", "dependencies"]
            missing_fields = []

            for field in required_fields:
                if field not in project_data:
                    missing_fields.append(field)
                    warnings.append(
                        f"Recommended field 'project.{field}' missing from pyproject.toml"
                    )

            if "python" not in project_data.get("requires-python", ""):
                recommendations.append(
                    "Consider specifying 'requires-python' in pyproject.toml"
                )

            # Count dependencies
            dependencies = project_data.get("dependencies", [])
            metadata["dependencies_count"] = len(dependencies)

            # Check for dev dependencies
            optional_deps = project_data.get("optional-dependencies", {})
            metadata["has_dev_dependencies"] = "dev" in optional_deps

            if not metadata["has_dev_dependencies"]:
                recommendations.append(
                    "Consider adding development dependencies in [project.optional-dependencies.dev]"
                )

        except Exception as e:
            errors.append(f"Failed to parse pyproject.toml: {e}")

        # Determine status
        if errors:
            status = ValidationStatus.ERROR
            is_valid = False
            message = f"Dependencies validation failed: {len(errors)} error(s)"
        elif warnings:
            status = ValidationStatus.WARNING
            is_valid = True
            message = f"Dependencies valid with {len(warnings)} warning(s)"
        else:
            status = ValidationStatus.VALID
            is_valid = True
            message = "Dependencies configuration is valid"

        return self._create_result(
            is_valid=is_valid,
            status=status,
            message=message,
            data=metadata,
            errors=errors,
            warnings=warnings,
            recommendations=recommendations,
        )


@register_validator("vscode_workspace")
class VSCodeWorkspaceValidator(BaseValidator[dict[str, Any]]):
    """
    Validates VS Code workspace configuration.

    Follows SRP by focusing on VS Code validation.
    """

    def get_validator_name(self) -> str:
        """Get validator name."""
        return "VS Code Workspace"

    def _perform_validation(self) -> ValidationResult[dict[str, Any]]:
        """Validate VS Code workspace configuration."""
        errors: list[str] = []
        warnings: list[str] = []
        recommendations: list[str] = []
        metadata: dict[str, Any] = {}

        workspace_root = Path(self.context.workspace_root)
        vscode_dir = workspace_root / ".vscode"

        if not vscode_dir.exists():
            warnings.append("VS Code configuration directory missing")
            recommendations.append("Create .vscode directory with recommended settings")

        config_files = ["settings.json", "tasks.json", "launch.json", "extensions.json"]
        found_configs = []
        missing_configs = []

        for config_file in config_files:
            config_path = vscode_dir / config_file
            if config_path.exists():
                found_configs.append(config_file)
            else:
                missing_configs.append(config_file)

        metadata.update(
            {
                "vscode_dir_exists": vscode_dir.exists(),
                "found_configs": found_configs,
                "missing_configs": missing_configs,
            }
        )

        if missing_configs:
            recommendations.extend(
                [f"Consider adding {config}" for config in missing_configs]
            )

        # Determine status
        if errors:
            status = ValidationStatus.ERROR
            is_valid = False
            message = f"VS Code validation failed: {len(errors)} error(s)"
        elif warnings:
            status = ValidationStatus.WARNING
            is_valid = True
            message = f"VS Code configuration has {len(warnings)} warning(s)"
        else:
            status = ValidationStatus.VALID
            is_valid = True
            message = "VS Code workspace configuration is valid"

        return self._create_result(
            is_valid=is_valid,
            status=status,
            message=message,
            data=metadata,
            errors=errors,
            warnings=warnings,
            recommendations=recommendations,
        )


@register_validator("docker_environment")
class DockerEnvironmentValidator(BaseValidator[dict[str, Any]]):
    """
    Validates Docker environment for containerized development.

    Follows SRP by focusing on Docker validation.
    """

    def get_validator_name(self) -> str:
        """Get validator name."""
        return "Docker Environment"

    def _perform_validation(self) -> ValidationResult[dict[str, Any]]:
        """Validate Docker environment."""
        errors: list[str] = []
        warnings: list[str] = []
        recommendations: list[str] = []
        metadata: dict[str, Any] = {}

        try:
            # Check Docker daemon
            result = subprocess.run(
                ["docker", "info"], capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                metadata["docker_running"] = True

                # Check Docker Compose
                compose_result = subprocess.run(
                    ["docker", "compose", "version"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )

                if compose_result.returncode == 0:
                    metadata["compose_available"] = True
                else:
                    warnings.append("Docker Compose not available")
                    recommendations.append(
                        "Install Docker Compose for container orchestration"
                    )

            else:
                errors.append("Docker daemon not running")
                recommendations.append("Start Docker daemon before proceeding")

        except subprocess.TimeoutExpired:
            errors.append("Docker command timed out")
        except FileNotFoundError:
            errors.append("Docker not installed")
            recommendations.append("Install Docker for containerized development")
        except Exception as e:
            errors.append(f"Docker validation error: {e}")

        # Determine status
        if errors:
            status = ValidationStatus.ERROR
            is_valid = False
            message = f"Docker validation failed: {len(errors)} error(s)"
        elif warnings:
            status = ValidationStatus.WARNING
            is_valid = True
            message = f"Docker environment has {len(warnings)} warning(s)"
        else:
            status = ValidationStatus.VALID
            is_valid = True
            message = "Docker environment is ready"

        return self._create_result(
            is_valid=is_valid,
            status=status,
            message=message,
            data=metadata,
            errors=errors,
            warnings=warnings,
            recommendations=recommendations,
        )
