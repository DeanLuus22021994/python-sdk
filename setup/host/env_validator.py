"""
Host Environment Validator
Modern host system validation with comprehensive checks.
"""

import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

from ..typings import ValidationDetails, ValidationStatus

if TYPE_CHECKING:
    pass


class HostEnvironmentValidator:
    """
    Modern host environment validator with comprehensive system checks.
    """

    def __init__(self, workspace_root: Path) -> None:
        """
        Initialize validator.

        Args:
            workspace_root: Root directory of the workspace
        """
        self.workspace_root = Path(workspace_root).resolve()

    def validate_complete_environment(self) -> ValidationDetails:
        """
        Perform complete host environment validation.

        Returns:
            ValidationDetails with comprehensive results
        """
        warnings: list[str] = []
        errors: list[str] = []
        recommendations: list[str] = []

        try:
            # System requirements validation
            system_valid = self._validate_system_requirements()
            if not system_valid:
                errors.append("System requirements not met")

            # Python installation validation
            python_valid = self._validate_python_installation()
            if not python_valid:
                errors.append("Python installation issues detected")

            # Development tools validation
            tools_valid = self._validate_development_tools()
            if not tools_valid:
                warnings.append("Some development tools are missing")
                recommendations.append("Install missing development tools")

            # Performance checks
            perf_issues = self._check_performance_indicators()
            if perf_issues:
                warnings.extend(perf_issues)
                recommendations.append("Consider system optimizations")

            # Security validation
            security_issues = self._validate_security_settings()
            if security_issues:
                warnings.extend(security_issues)
                recommendations.append("Review security settings")

            # Determine overall status
            if errors:
                status = ValidationStatus.ERROR
                is_valid = False
                message = f"Host validation failed: {len(errors)} error(s)"
            elif warnings:
                status = ValidationStatus.WARNING
                is_valid = True
                message = f"Host validation passed with {len(warnings)} warning(s)"
            else:
                status = ValidationStatus.VALID
                is_valid = True
                message = "Host environment is fully validated"

            return ValidationDetails(
                is_valid=is_valid,
                status=status,
                message=message,
                warnings=warnings,
                errors=errors,
                recommendations=recommendations,
                metadata={
                    "platform": platform.system(),
                    "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
                    "workspace_root": str(self.workspace_root),
                },
            )

        except Exception as e:
            return ValidationDetails(
                is_valid=False,
                status=ValidationStatus.ERROR,
                message=f"Validation failed: {e}",
                errors=[str(e)],
            )

    def _validate_system_requirements(self) -> bool:
        """Validate basic system requirements."""
        try:
            # Check available disk space
            if not self._check_disk_space():
                return False

            # Check memory requirements
            if not self._check_memory_requirements():
                return False

            # Check OS compatibility
            if not self._check_os_compatibility():
                return False

            return True

        except Exception:
            return False

    def _validate_python_installation(self) -> bool:
        """Validate Python installation quality."""
        try:
            # Check Python executable
            if not sys.executable:
                return False

            # Check Python version (modernized version check)
            if sys.version_info < (3, 11):
                return False

            # Check critical modules
            critical_modules = ["ssl", "sqlite3", "json", "pathlib"]
            for module in critical_modules:
                try:
                    __import__(module)
                except ImportError:
                    return False

            return True

        except Exception:
            return False

    def _validate_development_tools(self) -> bool:
        """Validate development tools availability."""
        tools_found = 0
        required_tools = ["git", "pip"]
        optional_tools = ["docker", "code", "make"]

        # Check required tools
        for tool in required_tools:
            if self._check_command_available(tool):
                tools_found += 1

        # Check optional tools
        for tool in optional_tools:
            if self._check_command_available(tool):
                tools_found += 1

        # Return True if we have at least the required tools
        return tools_found >= len(required_tools)

    def _check_performance_indicators(self) -> list[str]:
        """Check for performance-related issues."""
        issues: list[str] = []

        try:
            # Check if running on slow storage
            if self._is_slow_storage():
                issues.append("Project appears to be on slow storage (HDD/network)")

            # Check available memory
            if self._is_low_memory():
                issues.append("System has limited available memory")

            # Check CPU performance indicators
            if self._is_low_performance_cpu():
                issues.append("CPU may impact development performance")

        except Exception:
            issues.append("Could not assess performance indicators")

        return issues

    def _validate_security_settings(self) -> list[str]:
        """Validate security-related settings."""
        issues: list[str] = []

        try:
            # Check if running as admin/root (security risk)
            if self._is_running_privileged():
                issues.append("Running with elevated privileges (security risk)")

            # Check for insecure paths in workspace
            if self._has_insecure_paths():
                issues.append("Workspace contains potentially insecure paths")

        except Exception:
            pass

        return issues

    def _check_disk_space(self) -> bool:
        """Check available disk space with platform compatibility."""
        try:
            # Modern cross-platform approach using shutil
            import shutil

            total, used, free = shutil.disk_usage(self.workspace_root)
            return free > 1024 * 1024 * 1024  # 1GB minimum

        except Exception:
            return True  # Can't check, assume OK

    def _check_memory_requirements(self) -> bool:
        """Check memory requirements with optional psutil."""
        try:
            import psutil  # type: ignore[import-untyped]

            memory = psutil.virtual_memory()
            # Require at least 4GB total memory
            return memory.total > 4 * 1024 * 1024 * 1024
        except ImportError:
            return True  # Can't check, assume OK
        except Exception:
            return True

    def _check_os_compatibility(self) -> bool:
        """Check OS compatibility."""
        supported_platforms = ["Windows", "Darwin", "Linux"]
        return platform.system() in supported_platforms

    def _check_command_available(self, command: str) -> bool:
        """Check if a command is available in PATH."""
        try:
            result = subprocess.run(
                [command, "--version"], capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except (
            subprocess.TimeoutExpired,
            FileNotFoundError,
            subprocess.SubprocessError,
        ):
            return False

    def _is_slow_storage(self) -> bool:
        """Check if project is on slow storage."""
        try:
            # Simple heuristic: check if workspace is on network drive
            workspace_str = str(self.workspace_root)
            if platform.system() == "Windows":
                return workspace_str.startswith("\\\\") or workspace_str.startswith(
                    "//"
                )
            return "/mnt/" in workspace_str or "/media/" in workspace_str
        except Exception:
            return False

    def _is_low_memory(self) -> bool:
        """Check if system has low memory."""
        try:
            import psutil  # type: ignore[import-untyped]

            memory = psutil.virtual_memory()
            # Consider low if less than 8GB total or less than 2GB available
            return (
                memory.total < 8 * 1024 * 1024 * 1024
                or memory.available < 2 * 1024 * 1024 * 1024
            )
        except ImportError:
            return False
        except Exception:
            return False

    def _is_low_performance_cpu(self) -> bool:
        """Check for low-performance CPU indicators."""
        try:
            import psutil  # type: ignore[import-untyped]

            cpu_count = psutil.cpu_count()
            # Consider low performance if less than 4 cores
            return cpu_count < 4 if cpu_count else False
        except ImportError:
            return False
        except Exception:
            return False

    def _is_running_privileged(self) -> bool:
        """Check if running with elevated privileges."""
        try:
            if platform.system() == "Windows":
                import ctypes

                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                # Use hasattr check for cross-platform compatibility
                if hasattr(os, "geteuid"):
                    return os.geteuid() == 0  # type: ignore[attr-defined]
                return False
        except Exception:
            return False

    def _has_insecure_paths(self) -> bool:
        """Check for potentially insecure paths."""
        try:
            workspace_str = str(self.workspace_root)
            # Check for common insecure locations
            insecure_patterns = ["/tmp/", "\\Temp\\", "/var/tmp/"]
            return any(pattern in workspace_str for pattern in insecure_patterns)
        except Exception:
            return False

    def get_environment_info(self) -> dict[str, Any]:
        """
        Get detailed environment information.

        Returns:
            Dictionary with environment details
        """
        info: dict[str, Any] = {
            "platform": {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
            },
            "python": {
                "version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "executable": sys.executable,
                "implementation": platform.python_implementation(),
            },
            "workspace": {
                "root": str(self.workspace_root),
                "exists": self.workspace_root.exists(),
                "is_dir": self.workspace_root.is_dir(),
            },
        }

        # Add system resources if available
        try:
            import psutil  # type: ignore[import-untyped]

            info["resources"] = {
                "cpu_count": psutil.cpu_count(),
                "memory_gb": round(psutil.virtual_memory().total / (1024**3), 2),
                "disk_free_gb": round(
                    psutil.disk_usage(str(self.workspace_root)).free / (1024**3), 2
                ),
            }
        except ImportError:
            info["resources"] = {"status": "psutil not available"}
        except Exception:
            info["resources"] = {"status": "resource check failed"}

        return info
