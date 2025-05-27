"""
Docker Volume Management for MCP Python SDK.
This module provides Docker volume configuration and management capabilities
for the MCP Python SDK development environment.
"""

from __future__ import annotations

import asyncio
import gc
import json as stdlib_json
import os
import sys
import time

# Import necessary asyncio types properly for typing
from asyncio.locks import Lock
from asyncio.tasks import Task
from collections.abc import Coroutine
from pathlib import Path
from typing import Any, TypeVar, cast

# Type variable for async operations
T = TypeVar("T")

# Platform check for uvloop - use lowercase to avoid constant redefinition warnings
_uvloop_available: bool = False
_uvloop_module: Any = None
if sys.platform != "win32":
    try:
        import uvloop  # type: ignore

        _uvloop_module = uvloop
        _uvloop_available = True
    except ImportError:
        pass

UVLOOP_AVAILABLE: bool = _uvloop_available

# JSON backend selection with proper typing
_json_backend: str = "stdlib"
_orjson: Any = None
_ujson: Any = None

try:
    import orjson

    _orjson = orjson
    _json_backend = "orjson"
except ImportError:
    try:
        import ujson

        _ujson = ujson
        _json_backend = "ujson"
    except ImportError:
        pass

JSON_BACKEND: str = _json_backend

# Compression libraries
_lz4_available: bool = False
_lz4: Any = None
try:
    import lz4.frame

    _lz4 = lz4.frame
    _lz4_available = True
except ImportError:
    pass

LZ4_AVAILABLE: bool = _lz4_available

_zstd_available: bool = False
_zstd: Any = None
try:
    import zstandard

    _zstd = zstandard
    _zstd_available = True
except ImportError:
    pass

ZSTD_AVAILABLE: bool = _zstd_available

_xxhash_available: bool = False
_xxhash: Any = None
try:
    import xxhash

    _xxhash = xxhash
    _xxhash_available = True
except ImportError:
    pass

XXHASH_AVAILABLE: bool = _xxhash_available


class PerformanceOptimizer:
    """High-performance optimizations for MCP operations."""

    def __init__(self) -> None:
        """Initialize the performance optimizer."""
        self.json_backend: str = JSON_BACKEND
        self.compression_enabled: bool = LZ4_AVAILABLE or ZSTD_AVAILABLE
        self.hash_enabled: bool = XXHASH_AVAILABLE
        self.setup_gc_optimization()
        self.setup_event_loop()

    def setup_gc_optimization(self) -> None:
        """Optimize garbage collection for performance."""
        gc.disable()
        gc.set_threshold(700, 10, 10)
        if os.getenv("FASTMCP_DEBUG", "").lower() == "true":
            gc.set_debug(gc.DEBUG_STATS)

    def setup_event_loop(self) -> None:
        """Set up a high-performance event loop."""
        if UVLOOP_AVAILABLE and sys.platform != "win32":
            if _uvloop_module is not None:
                _uvloop_module.install()

    def optimize_json_serialization(self, data: Any) -> bytes:
        """High-performance JSON serialization."""
        if self.json_backend == "orjson" and _orjson is not None:
            serialized_data: bytes = _orjson.dumps(data)
            return serialized_data
        elif self.json_backend == "ujson" and _ujson is not None:
            json_str: str = _ujson.dumps(data)
            return json_str.encode("utf-8")
        else:
            json_result: str = stdlib_json.dumps(
                data, separators=(",", ":"), ensure_ascii=False
            )
            return json_result.encode("utf-8")

    def optimize_json_deserialization(self, data: bytes | str) -> Any:
        """High-performance JSON deserialization."""
        if isinstance(data, str):
            data_bytes = data.encode("utf-8")
        else:
            data_bytes = data

        if self.json_backend == "orjson" and _orjson is not None:
            return _orjson.loads(data_bytes)
        elif self.json_backend == "ujson" and _ujson is not None:
            return _ujson.loads(data_bytes.decode("utf-8"))
        else:
            return stdlib_json.loads(data_bytes.decode("utf-8"))

    def compress_data(self, data: bytes, algorithm: str = "lz4") -> bytes:
        """High-performance data compression."""
        if not self.compression_enabled:
            return data

        if algorithm == "lz4" and LZ4_AVAILABLE and _lz4 is not None:
            return _lz4.compress(data, compression_level=1)
        elif algorithm == "zstd" and ZSTD_AVAILABLE and _zstd is not None:
            compressor = _zstd.ZstdCompressor(level=1)
            return compressor.compress(data)

        return data

    def decompress_data(self, data: bytes, algorithm: str = "lz4") -> bytes:
        """High-performance data decompression."""
        if not self.compression_enabled:
            return data

        if algorithm == "lz4" and LZ4_AVAILABLE and _lz4 is not None:
            return _lz4.decompress(data)
        elif algorithm == "zstd" and ZSTD_AVAILABLE and _zstd is not None:
            decompressor = _zstd.ZstdDecompressor()
            return decompressor.decompress(data)

        return data

    def calculate_hash(self, data: bytes, algorithm: str = "xxhash64") -> str:
        """High-performance hash calculation."""
        if not self.hash_enabled or _xxhash is None:
            import hashlib

            return hashlib.sha256(data).hexdigest()

        if algorithm == "xxhash64" and _xxhash is not None:
            return _xxhash.xxh64(data).hexdigest()
        elif algorithm == "xxhash32" and _xxhash is not None:
            return _xxhash.xxh32(data).hexdigest()
        else:
            import hashlib

            return hashlib.sha256(data).hexdigest()

    def optimize_asyncio_task(self, coro: Coroutine[Any, Any, T]) -> Task[T]:
        """Create and return an optimized asyncio task with a name."""
        # Create a task from the coroutine - fixed type annotation
        task: Task[T] = asyncio.create_task(coro)
        task_id: int = id(cast(object, task))
        task.set_name(f"mcp_task_{task_id}")
        return task

    def run_gc_cycle(self, generation: int = 2) -> None:
        """Manual garbage collection for performance-critical sections."""
        collected: int = gc.collect(generation)
        if os.getenv("FASTMCP_DEBUG", "").lower() == "true":
            print(f"GC collected {collected} objects")


class ConnectionPool:
    """
    High-performance connection pool for MCP clients.

    This pool uses an asyncio.Lock to serialize access to its
    internal dictionary of connections. Each call to get_connection()
    acquires the lock before inspecting or mutating the _pool.

    See also:
    https://docs.python.org/3/library/asyncio-task.html#asyncio.Lock
    """

    def __init__(self, max_size: int = 100, max_overflow: int = 20) -> None:
        """Initialize the connection pool."""
        self.max_size: int = max_size
        self.max_overflow: int = max_overflow
        self._pool: dict[str, Any] = {}
        self._overflow_counter: int = 0
        self._lock: Lock | None = None

    def _ensure_lock(self) -> Lock:
        """Ensure lock is initialized when needed (lazy instantiation)."""
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock

    async def get_connection(self, key: str) -> Any:
        """
        Acquire the lock, then get or create a connection from the pool.

        This uses 'async with lock:' to guarantee only one coroutine
        can check or mutate the _pool at a time.
        """
        lock = self._ensure_lock()
        async with lock:
            if key in self._pool:
                return self._pool[key]

            # Check if we can create a new connection within the pool size limit
            if len(self._pool) < self.max_size:
                conn = await self._create_connection(key)
                self._pool[key] = conn
                return conn

            # Check if we can create an overflow connection
            if self._overflow_counter < self.max_overflow:
                self._overflow_counter += 1
                return await self._create_connection(key)

            # If we've reached both limits, return an existing connection as fallback
            return next(iter(self._pool.values()))

    async def _create_connection(self, key: str) -> Any:
        """
        Create a new connection (to be overridden by subclasses).

        Args:
            key: Connection identifier used for configuration or routing.
        """
        _ = key
        raise NotImplementedError("Subclasses must implement _create_connection")

    async def close_all(self) -> None:
        """
        Close all connections in the pool.
        Acquires the lock to ensure exclusive access during shutdown.
        """
        if self._lock is not None:
            async with self._lock:
                for connection in self._pool.values():
                    if hasattr(connection, "close") and callable(connection.close):
                        # Try to close the connection
                        try:
                            close_result = connection.close()
                            if hasattr(close_result, "__await__"):
                                await close_result  # type: ignore
                        except Exception:
                            # Ignore close errors during shutdown
                            pass
                self._pool.clear()
                self._overflow_counter = 0


class PerformanceMonitor:
    """Monitor and report performance metrics."""

    def __init__(self) -> None:
        """Initialize the performance monitor."""
        self.metrics: dict[str, list[dict[str, Any]]] = {}
        self.start_time: float = time.monotonic()

    def record_metric(
        self, name: str, value: float, tags: dict[str, str] | None = None
    ) -> None:
        """Record a performance metric."""
        if name not in self.metrics:
            self.metrics[name] = []

        # Fixed: Use proper typing and avoid duplicate append
        metric_data: dict[str, Any] = {
            "value": value,
            "timestamp": time.monotonic(),
            "tags": tags or {},
        }

        self.metrics[name].append(metric_data)

    def get_stats(self, name: str) -> dict[str, float]:
        """Get statistics for a specific metric."""
        if name not in self.metrics or not self.metrics[name]:
            return {"count": 0.0, "min": 0.0, "max": 0.0, "avg": 0.0, "total": 0.0}

        values: list[float] = [m["value"] for m in self.metrics[name]]
        return {
            "count": float(len(values)),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "total": sum(values),
        }

    def get_all_metrics(self) -> dict[str, dict[str, float]]:
        """Get statistics for all metrics."""
        return {name: self.get_stats(name) for name in self.metrics}

    def reset_metrics(self) -> None:
        """Reset all metrics."""
        self.metrics.clear()

    def get_uptime(self) -> float:
        """Get uptime in seconds."""
        current_time: float = time.monotonic()
        return current_time - self.start_time


class DockerVolumeManager:
    """
    Docker volume management for MCP development environment.

    Follows SOLID principles:
    - Single Responsibility: Manages only Docker volumes
    - Open/Closed: Extensible for new volume types
    - Dependency Inversion: Uses abstractions for volume operations
    """

    def __init__(self, workspace_root: Path) -> None:
        """Initialize Docker volume manager."""
        self.workspace_root = Path(workspace_root)
        self.volume_dirs = {
            "data": workspace_root / "data",
            "postgres": workspace_root / "data" / "postgres",
            "cache": workspace_root / "data" / "cache",
        }

    def _get_default_volume_config(self) -> dict[str, dict[str, Any]]:
        """Get default volume configuration."""
        return {
            "mcp-postgres-data": {
                "driver": "local",
                "path": str(self.volume_dirs["postgres"]),
            },
            "mcp-python-cache": {
                "driver": "local",
                "path": str(self.volume_dirs["cache"]),
            },
        }

    def create_volume_directories(self) -> bool:
        """Create volume directories."""
        try:
            # Create parent data directory
            self.volume_dirs["data"].mkdir(exist_ok=True, parents=True)

            # Create specific volume directories
            for name, path in self.volume_dirs.items():
                if name != "data":  # Skip the parent directory
                    path.mkdir(exist_ok=True, parents=True)

            return True
        except (OSError, PermissionError):
            return False

    def validate_volume_config(self) -> bool:
        """Validate volume configuration."""
        try:
            # Check if all volume directories exist
            for path in self.volume_dirs.values():
                if not path.exists():
                    return False

            return True
        except Exception:
            return False

    def get_volume_status(self) -> dict[str, bool]:
        """Get volume status."""
        status: dict[str, bool] = {}
        for name, path in self.volume_dirs.items():
            status[name] = path.exists()
        return status

    def get_volume_config(self) -> dict[str, dict[str, Any]]:
        """Get volume configuration."""
        return self._get_default_volume_config()

    def cleanup_volumes(self) -> bool:
        """Clean up volume directories."""
        try:
            import shutil

            # Only delete contents, not the directories themselves
            for name, path in self.volume_dirs.items():
                if name != "data" and path.exists():  # Skip the parent directory
                    for item in path.iterdir():
                        if item.is_file():
                            item.unlink()
                        elif item.is_dir():
                            shutil.rmtree(item)
            return True
        except (OSError, PermissionError):
            return False

    def get_volume_mount_paths(self) -> dict[str, Path]:
        """Get volume mount paths."""
        return self.volume_dirs


_performance_optimizer: PerformanceOptimizer | None = None


def get_performance_optimizer() -> PerformanceOptimizer:
    """Get the singleton performance optimizer instance."""
    global _performance_optimizer
    if _performance_optimizer is None:
        _performance_optimizer = PerformanceOptimizer()
    return _performance_optimizer


def enable_performance_mode() -> None:
    """Enable high-performance mode."""
    optimizer: PerformanceOptimizer = get_performance_optimizer()
    os.environ.setdefault("PYTHONOPTIMIZE", "2")
    os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    os.environ.setdefault("PYTHONHASHSEED", "0")
    optimizer.setup_gc_optimization()
    optimizer.setup_event_loop()
    print("🚀 MCP Performance Mode Enabled!")
    print(f"   JSON Backend: {optimizer.json_backend}")
    print(f"   Compression: {'✓' if optimizer.compression_enabled else '✗'}")
    print(f"   Fast Hashing: {'✓' if optimizer.hash_enabled else '✗'}")
    print(f"   Event Loop: {'uvloop' if UVLOOP_AVAILABLE else 'asyncio'}")


def create_performance_monitor() -> PerformanceMonitor:
    """Create a new performance monitor."""
    return PerformanceMonitor()


__all__ = [
    "PerformanceOptimizer",
    "ConnectionPool",
    "PerformanceMonitor",
    "DockerVolumeManager",
    "get_performance_optimizer",
    "enable_performance_mode",
    "create_performance_monitor",
    "UVLOOP_AVAILABLE",
    "JSON_BACKEND",
    "LZ4_AVAILABLE",
    "ZSTD_AVAILABLE",
    "XXHASH_AVAILABLE",
]
