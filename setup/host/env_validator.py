"""
Host Environment Validator
Modern host system validation with comprehensive checks.
"""

import os
import platform
import shutil
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
                errors.append("System does not meet minimum requirements")
                recommendations.append("Upgrade system to meet minimum requirements")

            # Python installation validation
            python_valid = self._validate_python_installation()
            if not python_valid:
                errors.append("Python installation has issues")
                recommendations.append("Install or update Python to version 3.10+")

            # Development tools validation
            tools_valid = self._validate_development_tools()
            if not tools_valid:
                warnings.append("Missing some development tools")
                recommendations.append("Install recommended development tools")

            # Performance checks
            perf_issues = self._check_performance_indicators()
            if perf_issues:
                warnings.extend(perf_issues)
                recommendations.append("Consider performance optimizations")

            # Security validation
            security_issues = self._validate_security_settings()
            if security_issues:
                warnings.extend(security_issues)
                recommendations.append("Address security concerns")

            # Determine overall status
            if errors:
                status = ValidationStatus.ERROR
                is_valid = False
                message = (
                    f"Host environment validation failed with {len(errors)} errors"
                )
            elif warnings:
                status = ValidationStatus.WARNING
                is_valid = True
                message = (
                    f"Host environment validation passed with {len(warnings)} warnings"
                )
            else:
                status = ValidationStatus.VALID
                is_valid = True
                message = "Host environment validation passed successfully"

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
                component_name="HostEnvironmentValidator",
                validation_time=0.0,
            )

        except Exception as e:
            return ValidationDetails(
                is_valid=False,
                status=ValidationStatus.ERROR,
                message=f"Validation failed: {e}",
                errors=[str(e)],
                warnings=[],
                recommendations=[],
                metadata={},
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
                issues.append("Project is on potentially slow storage")

            # Check available memory
            if self._is_low_memory():
                issues.append("System has limited memory available")

            # Check CPU performance indicators
            if self._is_low_performance_cpu():
                issues.append("CPU may not be optimal for development")

        except Exception:
            issues.append("Could not assess performance indicators")

        return issues

    def _validate_security_settings(self) -> list[str]:
        """Validate security-related settings."""
        issues: list[str] = []

        try:
            # Check if running as admin/root (security risk)
            if self._is_running_privileged():
                issues.append("Running with elevated privileges is a security risk")

            # Check for insecure paths in workspace
            if self._has_insecure_paths():
                issues.append("Workspace has potentially insecure paths")

        except Exception:
            pass

        return issues

    def _check_disk_space(self) -> bool:
        """Check available disk space with platform compatibility."""
        try:
            # Modern cross-platform approach using shutil
            _, _, free = shutil.disk_usage(self.workspace_root)
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
                return workspace_str.startswith("\\\\") or ":" not in workspace_str[:2]
            return "/mnt/" in workspace_str or "/media/" in workspace_str
        except Exception:
            return False

    def _is_low_memory(self) -> bool:
        """Check if system has low memory."""
        try:
            import psutil  # type: ignore[import-untyped]

            memory = psutil.virtual_memory()
            # Less than 8GB is considered low for development
            return memory.total < 8 * 1024 * 1024 * 1024
        except ImportError:
            return False
        except Exception:
            return False

    def _is_low_performance_cpu(self) -> bool:
        """Check for low-performance CPU indicators."""
        try:
            import psutil  # type: ignore[import-untyped]

            # Less than 4 cores is considered low for development
            cpu_count = psutil.cpu_count(logical=True)
            return cpu_count is not None and cpu_count < 4
        except ImportError:
            return False
        except Exception:
            return False

    def _is_running_privileged(self) -> bool:
        """Check if running with elevated privileges."""
        try:
            if platform.system() == "Windows":
                # Check for admin rights on Windows
                import ctypes

                return ctypes.windll.shell32.IsUserAnAdmin() != 0  # type: ignore
            else:
                # Check for root on Unix-like systems
                return os.geteuid() == 0  # type: ignore
        except Exception:
            return False

    def _has_insecure_paths(self) -> bool:
        """Check for potentially insecure paths."""
        try:
            workspace_str = str(self.workspace_root)
            # Check for world-writable directories in path
            if platform.system() != "Windows":
                path_parts = workspace_str.split("/")
                for i in range(1, len(path_parts)):
                    path = "/" + "/".join(path_parts[1 : i + 1])
                    if os.path.exists(path):
                        try:
                            mode = os.stat(path).st_mode
                            if mode & 0o002:  # World-writable
                                return True
                        except Exception:
                            pass
            return False
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

            memory = psutil.virtual_memory()
            info["resources"] = {
                "memory_total": memory.total,
                "memory_available": memory.available,
                "cpu_count": psutil.cpu_count(logical=True),
                "cpu_usage": psutil.cpu_percent(interval=0.1),
            }
        except ImportError:
            info["resources"] = {"available": False}
        except Exception:
            info["resources"] = {"error": True}

        return info
