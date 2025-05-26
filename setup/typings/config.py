"""
Configuration data classes for the MCP Python SDK setup system.

This module contains immutable configuration classes for performance settings,
container configuration, and other setup parameters.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, ClassVar

__all__ = [
    "PerformanceSettings",
    "ContainerConfig",
]


@dataclass(frozen=True, slots=True)
class PerformanceSettings:
    """Performance configuration for setup operations with sensible defaults."""

    parallel_operations: bool = True
    """Enable parallel operations for faster setup."""

    max_workers: int = 4
    """Maximum number of worker threads for parallel operations."""

    cache_enabled: bool = True
    """Enable caching for expensive operations."""

    cache_ttl_seconds: int = 3600
    """Cache time-to-live in seconds (1 hour default)."""

    enable_parallel_validation: bool = True
    """Enable parallel validation of multiple components."""

    timeout_seconds: float = 30.0
    """Default timeout for network and I/O operations."""

    cache_size: int = 128
    """Maximum number of items in memory cache."""

    # Class-level constants for validation
    MIN_WORKERS: ClassVar[int] = 1
    MAX_WORKERS: ClassVar[int] = 16
    MIN_TIMEOUT: ClassVar[float] = 1.0
    MAX_TIMEOUT: ClassVar[float] = 300.0

    def __post_init__(self) -> None:
        """Validate configuration parameters after initialization."""
        if not (self.MIN_WORKERS <= self.max_workers <= self.MAX_WORKERS):
            raise ValueError(
                f"max_workers must be between {self.MIN_WORKERS} and {self.MAX_WORKERS}"
            )

        if not (self.MIN_TIMEOUT <= self.timeout_seconds <= self.MAX_TIMEOUT):
            raise ValueError(
                f"timeout_seconds must be between {self.MIN_TIMEOUT} and {self.MAX_TIMEOUT}"
            )

        if self.cache_ttl_seconds <= 0:
            raise ValueError("cache_ttl_seconds must be positive")

        if self.cache_size <= 0:
            raise ValueError("cache_size must be positive")

    @property
    def is_high_performance(self) -> bool:
        """Check if configuration is optimized for high performance."""
        return (
            self.parallel_operations
            and self.cache_enabled
            and self.max_workers >= 4
            and self.enable_parallel_validation
        )


@dataclass(frozen=True, slots=True)
class ContainerConfig:
    """Container runtime configuration for Docker-based setups."""

    base_image: str = "python:3.11-slim"
    """Base Docker image for the container."""

    work_dir: str = "/app"
    """Working directory inside the container."""

    expose_port: int = 8000
    """Port to expose from the container."""

    health_check_interval: int = 30
    """Health check interval in seconds."""

    memory_limit: str = "512m"
    """Memory limit for the container."""

    cpu_limit: str = "0.5"
    """CPU limit for the container (in cores)."""

    # Class-level constants
    SUPPORTED_IMAGES: ClassVar[list[str]] = [
        "python:3.10-slim",
        "python:3.11-slim",
        "python:3.12-slim",
        "python:3.13-slim",
    ]
    MIN_PORT: ClassVar[int] = 1024
    MAX_PORT: ClassVar[int] = 65535

    def __post_init__(self) -> None:
        """Validate container configuration parameters."""
        if not (self.MIN_PORT <= self.expose_port <= self.MAX_PORT):
            raise ValueError(
                f"expose_port must be between {self.MIN_PORT} and {self.MAX_PORT}"
            )

        if self.health_check_interval <= 0:
            raise ValueError("health_check_interval must be positive")

        if not self.work_dir.startswith("/"):
            raise ValueError("work_dir must be an absolute path")

    @property
    def python_version(self) -> str:
        """Extract Python version from base image."""
        if "python:" in self.base_image:
            version_part = self.base_image.split("python:")[1].split("-")[0]
            return version_part
        return "unknown"

    @property
    def is_slim_image(self) -> bool:
        """Check if using a slim image variant."""
        return "slim" in self.base_image

    def get_docker_compose_config(self) -> dict[str, Any]:
        """Generate Docker Compose configuration."""
        return {
            "image": self.base_image,
            "working_dir": self.work_dir,
            "ports": [f"{self.expose_port}:{self.expose_port}"],
            "healthcheck": {
                "interval": f"{self.health_check_interval}s",
                "timeout": "10s",
                "retries": 3,
            },
            "deploy": {
                "resources": {
                    "limits": {
                        "memory": self.memory_limit,
                        "cpus": self.cpu_limit,
                    }
                }
            },
        }
