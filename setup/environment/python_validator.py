"""
Python Environment Validator
Modern Python environment validation following the new validation framework.
"""

from __future__ import annotations

import platform
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from ..typings import (
    PackageManagerInfo,
    PythonVersion,
    ValidationStatus,
)
from ..validation import BaseValidator, ValidationContext, ValidationResult
from .constants import MIN_PYTHON_VERSION, RECOMMENDED_PYTHON_VERSION
from .utils import run_with_timeout


@dataclass(frozen=True)
class PythonInfo:
    """Comprehensive Python environment information."""

    version: PythonVersion
    executable: str
    platform: PlatformInfo
    virtual_environment: VirtualEnvironmentInfo
    package_managers: list[PackageManagerInfo]


@dataclass(frozen=True)
class PlatformInfo:
    """Platform information."""

    system: str
    release: str
    version: str
    machine: str
    architecture: str


@dataclass(frozen=True)
class VirtualEnvironmentInfo:
    """Virtual environment information."""

    active: bool
    type: str | None = None
    path: str | None = None
    name: str | None = None


class PythonEnvironmentValidator(BaseValidator[PythonInfo]):
    """
    Validates Python environment configuration.

    Implements comprehensive Python environment validation including:
    - Version compatibility
    - Virtual environment detection
    - Package manager availability
    - Platform compatibility
    """

    def __init__(self, context: ValidationContext) -> None:
        """Initialize Python environment validator."""
        super().__init__(context)
        self._timeout = context.get_config_value("python_timeout", 10.0)

    async def validate(self) -> ValidationResult[PythonInfo]:
        """
        Validate Python environment comprehensively.

        Returns:
            Validation result with Python environment information
        """
        try:
            python_info = await self._gather_python_info()

            errors = []
            warnings = []
            recommendations = []

            # Validate Python version
            version_valid, version_messages = self._validate_python_version(
                python_info.version
            )
            if not version_valid:
                errors.extend(version_messages)
            else:
                warnings.extend(
                    msg for msg in version_messages if "recommended" in msg.lower()
                )

            # Check virtual environment
            if not python_info.virtual_environment.active:
                warnings.append("No virtual environment detected")
                recommendations.append(
                    "Consider using 'python -m venv .venv' for dependency isolation"
                )

            # Validate package managers
            if not python_info.package_managers:
                errors.append("No package managers available")
            elif not any(pm.name == "pip" for pm in python_info.package_managers):
                warnings.append("pip not available")

            is_valid = len(errors) == 0
            status = self._determine_status(is_valid, warnings)

            return ValidationResult(
                is_valid=is_valid,
                status=status,
                message=self._create_summary_message(python_info, is_valid),
                data=python_info,
                errors=tuple(errors),
                warnings=tuple(warnings),
                recommendations=tuple(recommendations),
                metadata={
                    "python_version": str(python_info.version),
                    "platform": python_info.platform.system,
                    "virtual_env": python_info.virtual_environment.active,
                },
            )

        except Exception as e:
            return ValidationResult(
                is_valid=False,
                status=ValidationStatus.ERROR,
                message=f"Python validation failed: {e}",
                errors=(str(e),),
            )

    def get_python_info(self) -> PythonInfo:
        """Get Python environment information synchronously."""
        import asyncio

        try:
            # Try to get existing event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is running, we need to run in a new thread
                import concurrent.futures

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._gather_python_info())
                    return future.result(timeout=self._timeout)
            else:
                return loop.run_until_complete(self._gather_python_info())
        except Exception:
            # Fallback to synchronous gathering
            return self._gather_python_info_sync()

    async def _gather_python_info(self) -> PythonInfo:
        """Gather comprehensive Python environment information."""
        version = self._get_python_version()
        executable = sys.executable
        platform_info = self._get_platform_info()
        venv_info = self._get_virtual_environment_info()
        package_managers = await self._get_package_managers()

        return PythonInfo(
            version=version,
            executable=executable,
            platform=platform_info,
            virtual_environment=venv_info,
            package_managers=package_managers,
        )

    def _gather_python_info_sync(self) -> PythonInfo:
        """Synchronous fallback for gathering Python information."""
        version = self._get_python_version()
        executable = sys.executable
        platform_info = self._get_platform_info()
        venv_info = self._get_virtual_environment_info()
        package_managers = self._get_package_managers_sync()

        return PythonInfo(
            version=version,
            executable=executable,
            platform=platform_info,
            virtual_environment=venv_info,
            package_managers=package_managers,
        )

    def _get_python_version(self) -> PythonVersion:
        """Get current Python version."""
        return PythonVersion(
            sys.version_info.major,
            sys.version_info.minor,
            sys.version_info.micro,
        )

    def _get_platform_info(self) -> PlatformInfo:
        """Get platform information."""
        return PlatformInfo(
            system=platform.system(),
            release=platform.release(),
            version=platform.version(),
            machine=platform.machine(),
            architecture=platform.architecture()[0],
        )

    def _get_virtual_environment_info(self) -> VirtualEnvironmentInfo:
        """Detect virtual environment information."""
        in_venv = hasattr(sys, "real_prefix") or (
            hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
        )

        if not in_venv:
            return VirtualEnvironmentInfo(active=False)

        venv_path = Path(sys.prefix)
        venv_type = "unknown"

        if (venv_path / "conda-meta").exists():
            venv_type = "conda"
        elif (venv_path / "pyvenv.cfg").exists():
            venv_type = "venv"
        elif "virtualenv" in str(venv_path):
            venv_type = "virtualenv"

        return VirtualEnvironmentInfo(
            active=True,
            type=venv_type,
            path=str(venv_path),
            name=venv_path.name,
        )

    async def _get_package_managers(self) -> list[PackageManagerInfo]:
        """Get available package managers asynchronously."""
        managers = []

        # Check pip
        try:
            import pip

            managers.append(
                PackageManagerInfo(
                    name="pip",
                    version=pip.__version__,
                    available=True,
                    executable=f"{sys.executable} -m pip",
                )
            )
        except ImportError:
            managers.append(
                PackageManagerInfo(
                    name="pip",
                    available=False,
                )
            )

        # Check conda
        conda_info = await run_with_timeout(
            ["conda", "--version"],
            timeout=self._timeout,
        )
        if conda_info.returncode == 0:
            version = (
                conda_info.stdout.strip().split()[-1]
                if conda_info.stdout
                else "unknown"
            )
            managers.append(
                PackageManagerInfo(
                    name="conda",
                    version=version,
                    available=True,
                    executable="conda",
                )
            )

        # Check uv
        uv_info = await run_with_timeout(
            ["uv", "--version"],
            timeout=self._timeout,
        )
        if uv_info.returncode == 0:
            version = (
                uv_info.stdout.strip().split()[-1] if uv_info.stdout else "unknown"
            )
            managers.append(
                PackageManagerInfo(
                    name="uv",
                    version=version,
                    available=True,
                    executable="uv",
                )
            )

        return managers

    def _get_package_managers_sync(self) -> list[PackageManagerInfo]:
        """Get available package managers synchronously."""
        managers = []

        # Check pip
        try:
            import pip

            managers.append(
                PackageManagerInfo(
                    name="pip",
                    version=pip.__version__,
                    available=True,
                    executable=f"{sys.executable} -m pip",
                )
            )
        except ImportError:
            managers.append(
                PackageManagerInfo(
                    name="pip",
                    available=False,
                )
            )

        # Check other package managers with subprocess
        for cmd, name in [("conda", "conda"), ("uv", "uv")]:
            try:
                result = subprocess.run(
                    [cmd, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=False,
                )
                if result.returncode == 0:
                    version = (
                        result.stdout.strip().split()[-1]
                        if result.stdout
                        else "unknown"
                    )
                    managers.append(
                        PackageManagerInfo(
                            name=name,
                            version=version,
                            available=True,
                            executable=cmd,
                        )
                    )
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass

        return managers

    def _validate_python_version(
        self,
        version: PythonVersion,
    ) -> tuple[bool, list[str]]:
        """Validate Python version against requirements."""
        messages = []

        if version < MIN_PYTHON_VERSION:
            return False, [
                f"Python {version} is not supported. "
                f"Minimum required version is {MIN_PYTHON_VERSION}"
            ]

        if version < RECOMMENDED_PYTHON_VERSION:
            messages.append(
                f"Python {version} meets minimum requirements. "
                f"Recommended version is {RECOMMENDED_PYTHON_VERSION} for better performance."
            )
        else:
            messages.append(f"Python {version} meets all requirements")

        return True, messages

    def _determine_status(
        self, is_valid: bool, warnings: list[str]
    ) -> ValidationStatus:
        """Determine validation status."""
        if not is_valid:
            return ValidationStatus.ERROR
        elif warnings:
            return ValidationStatus.WARNING
        else:
            return ValidationStatus.VALID

    def _create_summary_message(self, python_info: PythonInfo, is_valid: bool) -> str:
        """Create summary message for validation result."""
        if is_valid:
            return f"Python {python_info.version} environment is valid"
        else:
            return f"Python {python_info.version} environment has issues"
