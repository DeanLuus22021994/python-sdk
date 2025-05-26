"""
High-performance optimizations for FastMCP server.
This module provides performance enhancements for the MCP Python SDK.
"""

from __future__ import annotations

import asyncio
import gc
import hashlib
import os
import sys
from typing import Any


# Platform check for uvloop (Windows not supported)
_uvloop_available = False
if sys.platform != "win32":
    try:
        import uvloop  # type: ignore

        _uvloop_available = True
    except ImportError:
        pass

UVLOOP_AVAILABLE = _uvloop_available

# JSON backend selection with proper module handling
_json_module: Any = None
_json_backend = "stdlib"

try:
    import orjson  # type: ignore

    _json_module = orjson
    _json_backend = "orjson"
except ImportError:
    try:
        import ujson  # type: ignore

        _json_module = ujson
        _json_backend = "ujson"
    except ImportError:
        import json

        _json_module = json
        _json_backend = "stdlib"

JSON_BACKEND = _json_backend

# Compression libraries
_lz4_available = False
_lz4_module: Any = None
try:
    import lz4.frame  # type: ignore

    _lz4_module = lz4.frame
    _lz4_available = True
except ImportError:
    pass

LZ4_AVAILABLE = _lz4_available

_zstd_available = False
_zstd_module: Any = None
try:
    import zstandard  # type: ignore

    _zstd_module = zstandard
    _zstd_available = True
except ImportError:
    pass

ZSTD_AVAILABLE = _zstd_available

_xxhash_available = False
_xxhash_module: Any = None
try:
    import xxhash  # type: ignore

    _xxhash_module = xxhash
    _xxhash_available = True
except ImportError:
    pass

XXHASH_AVAILABLE = _xxhash_available


class PerformanceOptimizer:
    """High-performance optimizations for MCP operations."""

    def __init__(self) -> None:
        self.json_backend = JSON_BACKEND
        self.compression_enabled = LZ4_AVAILABLE or ZSTD_AVAILABLE
        self.hash_enabled = XXHASH_AVAILABLE
        self._setup_gc_optimization()
        self._setup_event_loop()

    def _setup_gc_optimization(self) -> None:
        """Optimize garbage collection for performance."""
        # Disable automatic garbage collection for latency-sensitive operations
        gc.disable()

        # Set aggressive garbage collection thresholds
        gc.set_threshold(700, 10, 10)

        # Enable garbage collection debugging if in development
        if os.getenv("FASTMCP_DEBUG", "").lower() == "true":
            gc.set_debug(gc.DEBUG_STATS)

    def _setup_event_loop(self) -> None:
        """Set up high-performance event loop."""
        if UVLOOP_AVAILABLE and sys.platform != "win32":
            try:
                if _uvloop_available:
                    import uvloop  # type: ignore

                    uvloop.install()
            except Exception:
                pass  # Fall back to default event loop

    def optimize_json_serialization(self, data: Any) -> bytes:
        """High-performance JSON serialization."""
        if self.json_backend == "orjson" and _json_module:
            return _json_module.dumps(data)
        elif self.json_backend == "ujson" and _json_module:
            result = _json_module.dumps(data)
            return result.encode("utf-8") if isinstance(result, str) else result
        else:
            if _json_module:
                return _json_module.dumps(
                    data, separators=(",", ":"), ensure_ascii=False
                ).encode("utf-8")
            return b"{}"

    def optimize_json_deserialization(self, data: bytes | str) -> Any:
        """High-performance JSON deserialization."""
        if isinstance(data, str):
            data = data.encode("utf-8")

        if not _json_module:
            return {}

        if self.json_backend == "orjson":
            return _json_module.loads(data)
        elif self.json_backend == "ujson":
            return _json_module.loads(data.decode("utf-8"))
        else:
            return _json_module.loads(data.decode("utf-8"))

    def compress_data(self, data: bytes, algorithm: str = "lz4") -> bytes:
        """High-performance data compression."""
        if not self.compression_enabled:
            return data

        if algorithm == "lz4" and LZ4_AVAILABLE and _lz4_module:
            return _lz4_module.compress(data, compression_level=1)
        elif algorithm == "zstd" and ZSTD_AVAILABLE and _zstd_module:
            cctx = _zstd_module.ZstdCompressor(level=1)  # Fast compression
            return cctx.compress(data)

        return data

    def decompress_data(self, data: bytes, algorithm: str = "lz4") -> bytes:
        """High-performance data decompression."""
        if not self.compression_enabled:
            return data

        if algorithm == "lz4" and LZ4_AVAILABLE and _lz4_module:
            return _lz4_module.decompress(data)
        elif algorithm == "zstd" and ZSTD_AVAILABLE and _zstd_module:
            dctx = _zstd_module.ZstdDecompressor()
            return dctx.decompress(data)

        return data

    def calculate_hash(self, data: bytes, algorithm: str = "xxhash64") -> str:
        """High-performance hash calculation."""
        if not self.hash_enabled or not _xxhash_module:
            return hashlib.sha256(data).hexdigest()

        if algorithm == "xxhash64":
            return _xxhash_module.xxh64(data).hexdigest()
        elif algorithm == "xxhash32":
            return _xxhash_module.xxh32(data).hexdigest()
        else:
            return hashlib.sha256(data).hexdigest()

    def optimize_asyncio_task(self, coro: Any) -> Any:
        """Create optimized asyncio tasks."""
        if hasattr(asyncio, "create_task"):
            task = asyncio.create_task(coro)
            task.set_name(f"mcp_task_{id(task)}")
            return task
        else:
            return asyncio.ensure_future(coro)

    def run_gc_cycle(self, generation: int = 2) -> None:
        """Manual garbage collection for performance-critical sections."""
        gc.collect(generation)


class ConnectionPool:
    """High-performance connection pool."""

    def __init__(self, max_size: int = 100) -> None:
        self.max_size = max_size
        self._pool: dict[str, Any] = {}
        self._lock = asyncio.Lock()
        self._overflow_counter = 0

    async def get_connection(self, key: str) -> Any:
        """Get a connection from the pool."""
        async with self._lock:
            if key in self._pool:
                return self._pool[key]

            if len(self._pool) < self.max_size:
                connection = await self._create_connection(key)
                self._pool[key] = connection
                return connection
            else:
                self._overflow_counter += 1
                return await self._create_connection(key)

    async def close_all(self) -> None:
        """Close all connections in the pool."""
        async with self._lock:
            for connection in self._pool.values():
                if hasattr(connection, "close"):
                    await connection.close()
            self._pool.clear()
            self._overflow_counter = 0

    async def _create_connection(self, key: str) -> Any:
        """Create a new connection (override in subclasses)."""
        # This is a placeholder implementation
        return f"connection_{key}"


class PerformanceMetrics:
    """Performance metrics collection."""

    def __init__(self) -> None:
        self.metrics: dict[str, list[dict[str, Any]]] = {}

    def record_metric(
        self, name: str, value: float, tags: dict[str, str] | None = None
    ) -> None:
        """Record a performance metric."""
        timestamp = asyncio.get_event_loop().time()
        if name not in self.metrics:
            self.metrics[name] = []

        self.metrics[name].append(
            {"value": value, "timestamp": timestamp, "tags": tags or {}}
        )

    def get_stats(self, name: str) -> dict[str, float]:
        """Get statistics for a metric."""
        if name not in self.metrics:
            return {}

        values = [m["value"] for m in self.metrics[name]]
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "total": sum(values),
        }


# Global performance optimizer instance
_performance_optimizer: PerformanceOptimizer | None = None


def get_performance_optimizer() -> PerformanceOptimizer:
    """Get the global performance optimizer instance."""
    global _performance_optimizer
    if _performance_optimizer is None:
        _performance_optimizer = PerformanceOptimizer()
    return _performance_optimizer


def enable_performance_mode() -> None:
    """Enable high-performance mode for the MCP server."""
    optimizer = get_performance_optimizer()
    optimizer._setup_gc_optimization()
    optimizer._setup_event_loop()

    # Print performance status
    print("🚀 MCP Performance Mode Enabled!")
    print(f"   JSON Backend: {JSON_BACKEND}")
    print(f"   Compression: {'✓' if optimizer.compression_enabled else '✗'}")
    print(f"   Hashing: {'✓' if optimizer.hash_enabled else '✗'}")
    print(f"   Event Loop: {'uvloop' if UVLOOP_AVAILABLE else 'asyncio'}")


# Convenience functions
def optimize_json(data: Any) -> bytes:
    """Optimize JSON serialization."""
    return get_performance_optimizer().optimize_json_serialization(data)


def optimize_json_loads(data: bytes | str) -> Any:
    """Optimize JSON deserialization."""
    return get_performance_optimizer().optimize_json_deserialization(data)


def compress(data: bytes, algorithm: str = "lz4") -> bytes:
    """Compress data using the best available algorithm."""
    return get_performance_optimizer().compress_data(data, algorithm)


def decompress(data: bytes, algorithm: str = "lz4") -> bytes:
    """Decompress data using the specified algorithm."""
    return get_performance_optimizer().decompress_data(data, algorithm)


def hash_data(data: bytes, algorithm: str = "xxhash64") -> str:
    """Calculate hash using the best available algorithm."""
    return get_performance_optimizer().calculate_hash(data, algorithm)
