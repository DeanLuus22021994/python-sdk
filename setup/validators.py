"""
Setup System Validators
Concrete validators for the MCP Python SDK setup system.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

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
                f"Python {python_version} is supported but Python 3.11+ is recommended."
            )
            recommendations.append(
                "Consider upgrading to Python 3.11 or higher for better performance."
            )

        # Check if virtual environment is active
        in_venv = hasattr(sys, "real_prefix") or (
            hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
        )
        metadata["in_virtual_environment"] = in_venv

        if not in_venv:
            warnings.append("Not running in a virtual environment.")
            recommendations.append(
                "Consider using a virtual environment to isolate dependencies."
            )

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
            message = f"Python {python_version} environment is valid"

        return self._create_result(
            is_valid=is_valid,
            status=status,
            message=message,
            data=metadata,
            errors=errors,
            warnings=warnings,
            recommendations=recommendations,
            **metadata,
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
            if not path.exists():
                missing_optional.append(path_str)
                warnings.append(f"Optional path missing: {path_str}")

        # Add recommendations for missing optional paths
        if "docs" in missing_optional:
            recommendations.append(
                "Consider adding documentation in a 'docs' directory."
            )
        if "examples" in missing_optional:
            recommendations.append(
                "Consider adding examples to help users understand usage."
            )

        # Determine overall status
        if missing_required:
            status = ValidationStatus.ERROR
            is_valid = False
            message = f"Project structure validation failed: {len(missing_required)} required path(s) missing"
        elif missing_optional:
            status = ValidationStatus.WARNING
            is_valid = True
            message = f"Project structure valid with {len(missing_optional)} optional path(s) missing"
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
            workspace_root=str(workspace_root),
            required_paths_found=len(found_paths),
            total_required_paths=len(required_paths),
        )


@register_validator("dependencies")
class DependencyValidator(BaseValidator[dict[str, Any]]):
    """
    Validates project dependencies and package configuration.

    Follows SRP by focusing on dependency validation.
    """

    def get_validator_name(self) -> str:
        """Get validator name."""
        return "Dependencies"

    def _perform_validation(self) -> ValidationResult[dict[str, Any]]:
        """Validate dependencies."""
        errors: list[str] = []
        warnings: list[str] = []
        recommendations: list[str] = []

        workspace_root = Path(self.context.workspace_root)
        pyproject_path = workspace_root / "pyproject.toml"

        if not pyproject_path.exists():
            errors.append("pyproject.toml file not found")
            return self._create_result(
                is_valid=False,
                status=ValidationStatus.ERROR,
                message="Dependencies validation failed: pyproject.toml missing",
                errors=errors,
            )

        try:
            # Try to import and check if we can load the project config
            import tomllib

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

            # Try to check if dependencies are installable
            dependencies = project_data.get("dependencies", [])
            metadata = {
                "dependencies_count": len(dependencies),
                "has_dev_dependencies": "dev"
                in pyproject_data.get("project", {}).get("optional-dependencies", {}),
            }

        except ImportError:
            warnings.append(
                "tomllib not available (Python 3.11+), using basic validation"
            )
            metadata = {"validation_limited": True}
        except Exception as e:
            errors.append(f"Error reading pyproject.toml: {e}")
            metadata = {"read_error": str(e)}

        # Determine overall status
        if errors:
            status = ValidationStatus.ERROR
            is_valid = False
            message = f"Dependencies validation failed: {len(errors)} error(s)"
        elif warnings:
            status = ValidationStatus.WARNING
            is_valid = True
            message = f"Dependencies validation has {len(warnings)} warning(s)"
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
            **metadata,
        )
