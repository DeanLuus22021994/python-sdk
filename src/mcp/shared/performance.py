"""
High-performance optimizations for FastMCP server.
This module provides performance enhancements for the MCP Python SDK.
"""

from __future__ import annotations

import asyncio
import gc
import json as stdlib_json
import os
import sys
from typing import Any

# Platform check for uvloop - use lowercase to avoid constant redefinition warnings
_uvloop_available = False
_uvloop_module: Any = None
if sys.platform != "win32":
    try:
        import uvloop  # type: ignore

        _uvloop_module = uvloop
        _uvloop_available = True
    except ImportError:
        pass

UVLOOP_AVAILABLE = _uvloop_available

# JSON backend selection with proper typing
_json_backend = "stdlib"
_orjson: Any = None
_ujson: Any = None

try:
    import orjson  # type: ignore

    _orjson = orjson
    _json_backend = "orjson"
except ImportError:
    try:
        import ujson  # type: ignore

        _ujson = ujson
        _json_backend = "ujson"
    except ImportError:
        pass

JSON_BACKEND = _json_backend

# Compression libraries
_lz4_available = False
_lz4: Any = None
try:
    import lz4.frame  # type: ignore

    _lz4 = lz4.frame
    _lz4_available = True
except ImportError:
    pass

LZ4_AVAILABLE = _lz4_available

_zstd_available = False
_zstd: Any = None
try:
    import zstandard  # type: ignore

    _zstd = zstandard
    _zstd_available = True
except ImportError:
    pass

ZSTD_AVAILABLE = _zstd_available

_xxhash_available = False
_xxhash: Any = None
try:
    import xxhash  # type: ignore

    _xxhash = xxhash
    _xxhash_available = True
except ImportError:
    pass

XXHASH_AVAILABLE = _xxhash_available


class PerformanceOptimizer:
    """High-performance optimizations for MCP operations."""

    def __init__(self):
        self.json_backend = JSON_BACKEND
        self.compression_enabled = LZ4_AVAILABLE or ZSTD_AVAILABLE
        self.hash_enabled = XXHASH_AVAILABLE
        self.setup_gc_optimization()
        self.setup_event_loop()

    def setup_gc_optimization(self) -> None:
        """Optimize garbage collection for performance."""
        # Disable automatic garbage collection for latency-sensitive operations
        gc.disable()

        # Set aggressive garbage collection thresholds
        gc.set_threshold(700, 10, 10)

        # Enable garbage collection debugging if in development
        if os.getenv("FASTMCP_DEBUG", "").lower() == "true":
            gc.set_debug(gc.DEBUG_STATS)

    def setup_event_loop(self) -> None:
        """Set up high-performance event loop."""
        if UVLOOP_AVAILABLE and sys.platform != "win32":
            try:
                if _uvloop_module:
                    _uvloop_module.install()
            except Exception:
                pass  # Fall back to default event loop

    def optimize_json_serialization(self, data: Any) -> bytes:
        """High-performance JSON serialization."""
        if self.json_backend == "orjson" and _orjson:
            # orjson.dumps returns bytes directly
            return _orjson.dumps(data)  # type: ignore
        elif self.json_backend == "ujson" and _ujson:
            # ujson.dumps returns str, need to encode
            result = _ujson.dumps(data)  # type: ignore
            return result.encode("utf-8")
        else:
            # stdlib json.dumps returns str, need to encode
            result = stdlib_json.dumps(data, separators=(",", ":"), ensure_ascii=False)
            return result.encode("utf-8")

    def optimize_json_deserialization(self, data: bytes | str) -> Any:
        """High-performance JSON deserialization."""
        if isinstance(data, str):
            data = data.encode("utf-8")

        if self.json_backend == "orjson" and _orjson:
            return _orjson.loads(data)  # type: ignore
        elif self.json_backend == "ujson" and _ujson:
            return _ujson.loads(data.decode("utf-8"))  # type: ignore
        else:
            return stdlib_json.loads(data.decode("utf-8"))

    def compress_data(self, data: bytes, algorithm: str = "lz4") -> bytes:
        """High-performance data compression."""
        if not self.compression_enabled:
            return data

        if algorithm == "lz4" and LZ4_AVAILABLE and _lz4:
            return _lz4.compress(data, compression_level=1)  # type: ignore
        elif algorithm == "zstd" and ZSTD_AVAILABLE and _zstd:
            cctx = _zstd.ZstdCompressor(level=1)  # Fast compression  # type: ignore
            return cctx.compress(data)  # type: ignore

        return data

    def decompress_data(self, data: bytes, algorithm: str = "lz4") -> bytes:
        """High-performance data decompression."""
        if not self.compression_enabled:
            return data

        if algorithm == "lz4" and LZ4_AVAILABLE and _lz4:
            return _lz4.decompress(data)  # type: ignore
        elif algorithm == "zstd" and ZSTD_AVAILABLE and _zstd:
            dctx = _zstd.ZstdDecompressor()  # type: ignore
            return dctx.decompress(data)  # type: ignore

        return data

    def calculate_hash(self, data: bytes, algorithm: str = "xxhash64") -> str:
        """High-performance hash calculation."""
        if not self.hash_enabled:
            import hashlib

            return hashlib.sha256(data).hexdigest()

        if algorithm == "xxhash64" and _xxhash:
            return _xxhash.xxh64(data).hexdigest()  # type: ignore
        elif algorithm == "xxhash32" and _xxhash:
            return _xxhash.xxh32(data).hexdigest()  # type: ignore
        else:
            import hashlib

            return hashlib.sha256(data).hexdigest()

    def optimize_asyncio_task(self, coro: Any) -> Any:
        """Create optimized asyncio task with performance hints."""
        if hasattr(asyncio, "create_task"):
            task = asyncio.create_task(coro)
            # Set task name for better debugging
            task.set_name(f"mcp_task_{id(task)}")
            return task
        else:
            return asyncio.ensure_future(coro)

    def run_gc_cycle(self, generation: int = 2) -> None:
        """Manual garbage collection for performance-critical sections."""
        collected = gc.collect(generation)
        if os.getenv("FASTMCP_DEBUG", "").lower() == "true":
            print(f"GC: Collected {collected} objects in generation {generation}")


class ConnectionPool:
    """High-performance connection pool for MCP clients."""

    def __init__(self, max_size: int = 100, max_overflow: int = 20):
        self.max_size = max_size
        self.max_overflow = max_overflow
        self._pool: dict[str, Any] = {}
        self._overflow_counter = 0
        self._lock = asyncio.Lock()

    async def get_connection(self, key: str) -> Any:
        """Get or create a connection from the pool."""
        async with self._lock:
            if key in self._pool:
                return self._pool[key]

            if len(self._pool) < self.max_size:
                # Create new connection
                connection = await self._create_connection(key)
                self._pool[key] = connection
                return connection

            if self._overflow_counter < self.max_overflow:
                # Allow overflow
                self._overflow_counter += 1
                return await self._create_connection(key)

            # Pool is full, reuse existing connection
            return next(iter(self._pool.values()))

    async def _create_connection(self, key: str) -> Any:
        """Create a new connection (to be overridden)."""
        raise NotImplementedError("Subclasses must implement _create_connection")

    async def close_all(self) -> None:
        """Close all connections in the pool."""
        async with self._lock:
            for connection in self._pool.values():
                if hasattr(connection, "close"):
                    await connection.close()
            self._pool.clear()
            self._overflow_counter = 0


class PerformanceMonitor:
    """Monitor and report performance metrics."""

    def __init__(self):
        self.metrics: dict[str, Any] = {}
        self.start_time = asyncio.get_event_loop().time()

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
    """Enable high-performance mode for MCP operations."""
    optimizer = get_performance_optimizer()

    # Set environment variables for performance
    os.environ.setdefault("PYTHONOPTIMIZE", "2")
    os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    os.environ.setdefault("PYTHONHASHSEED", "0")

    # Enable garbage collection optimization
    optimizer.setup_gc_optimization()

    # Set up high-performance event loop
    optimizer.setup_event_loop()

    print("🚀 MCP Performance Mode Enabled!")
    print(f"   JSON Backend: {optimizer.json_backend}")
    print(f"   Compression: {'✓' if optimizer.compression_enabled else '✗'}")
    print(f"   Fast Hashing: {'✓' if optimizer.hash_enabled else '✗'}")
    print(f"   Event Loop: {'uvloop' if UVLOOP_AVAILABLE else 'asyncio'}")
