"""
High-performance optimizations for FastMCP server.
This module provides performance enhancements for the MCP Python SDK.
"""

from __future__ import annotations

import asyncio
import gc
import os
import sys
from typing import Any, Dict, Optional

try:
    import uvloop
    UVLOOP_AVAILABLE = True
except ImportError:
    UVLOOP_AVAILABLE = False

try:
    import orjson as json
    JSON_BACKEND = "orjson"
except ImportError:
    try:
        import ujson as json
        JSON_BACKEND = "ujson"
    except ImportError:
        import json
        JSON_BACKEND = "stdlib"

try:
    import lz4.frame as lz4
    LZ4_AVAILABLE = True
except ImportError:
    LZ4_AVAILABLE = False

try:
    import zstandard as zstd
    ZSTD_AVAILABLE = True
except ImportError:
    ZSTD_AVAILABLE = False

try:
    import xxhash
    XXHASH_AVAILABLE = True
except ImportError:
    XXHASH_AVAILABLE = False


class PerformanceOptimizer:
    """High-performance optimizations for MCP operations."""

    def __init__(self):
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
                uvloop.install()
            except Exception:
                pass  # Fall back to default event loop

    def optimize_json_serialization(self, data: Any) -> bytes:
        """High-performance JSON serialization."""
        if self.json_backend == "orjson":
            return json.dumps(data)
        elif self.json_backend == "ujson":
            return json.dumps(data).encode('utf-8')
        else:
            return json.dumps(data, separators=(',', ':'), ensure_ascii=False).encode('utf-8')

    def optimize_json_deserialization(self, data: bytes | str) -> Any:
        """High-performance JSON deserialization."""
        if isinstance(data, str):
            data = data.encode('utf-8')

        if self.json_backend == "orjson":
            return json.loads(data)
        elif self.json_backend == "ujson":
            return json.loads(data.decode('utf-8'))
        else:
            return json.loads(data.decode('utf-8'))

    def compress_data(self, data: bytes, algorithm: str = "lz4") -> bytes:
        """High-performance data compression."""
        if not self.compression_enabled:
            return data

        if algorithm == "lz4" and LZ4_AVAILABLE:
            return lz4.compress(data, compression_level=1)  # Fast compression
        elif algorithm == "zstd" and ZSTD_AVAILABLE:
            cctx = zstd.ZstdCompressor(level=1)  # Fast compression
            return cctx.compress(data)

        return data

    def decompress_data(self, data: bytes, algorithm: str = "lz4") -> bytes:
        """High-performance data decompression."""
        if not self.compression_enabled:
            return data

        if algorithm == "lz4" and LZ4_AVAILABLE:
            return lz4.decompress(data)
        elif algorithm == "zstd" and ZSTD_AVAILABLE:
            dctx = zstd.ZstdDecompressor()
            return dctx.decompress(data)

        return data

    def calculate_hash(self, data: bytes, algorithm: str = "xxhash64") -> str:
        """High-performance hash calculation."""
        if not self.hash_enabled:
            import hashlib
            return hashlib.sha256(data).hexdigest()

        if algorithm == "xxhash64":
            return xxhash.xxh64(data).hexdigest()
        elif algorithm == "xxhash32":
            return xxhash.xxh32(data).hexdigest()
        else:
            import hashlib
            return hashlib.sha256(data).hexdigest()

    def optimize_asyncio_task(self, coro):
        """Create optimized asyncio task with performance hints."""
        if hasattr(asyncio, 'create_task'):
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
            print(
                f"GC: Collected {collected} objects in generation {generation}")


class ConnectionPool:
    """High-performance connection pool for MCP clients."""

    def __init__(self, max_size: int = 100, max_overflow: int = 20):
        self.max_size = max_size
        self.max_overflow = max_overflow
        self._pool: Dict[str, Any] = {}
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
        raise NotImplementedError(
            "Subclasses must implement _create_connection")

    async def close_all(self) -> None:
        """Close all connections in the pool."""
        async with self._lock:
            for connection in self._pool.values():
                if hasattr(connection, 'close'):
                    await connection.close()
            self._pool.clear()
            self._overflow_counter = 0


class PerformanceMonitor:
    """Monitor and report performance metrics."""

    def __init__(self):
        self.metrics: Dict[str, Any] = {}
        self.start_time = asyncio.get_event_loop().time()

    def record_metric(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Record a performance metric."""
        timestamp = asyncio.get_event_loop().time()

        if name not in self.metrics:
            self.metrics[name] = []

        self.metrics[name].append({
            'value': value,
            'timestamp': timestamp,
            'tags': tags or {}
        })

    def get_stats(self, name: str) -> Dict[str, float]:
        """Get statistics for a metric."""
        if name not in self.metrics:
            return {}

        values = [m['value'] for m in self.metrics[name]]

        return {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values),
            'total': sum(values)
        }


# Global performance optimizer instance
_performance_optimizer: Optional[PerformanceOptimizer] = None


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
    optimizer._setup_gc_optimization()

    # Set up high-performance event loop
    optimizer._setup_event_loop()

    print(f"🚀 MCP Performance Mode Enabled!")
    print(f"   JSON Backend: {optimizer.json_backend}")
    print(f"   Compression: {'✓' if optimizer.compression_enabled else '✗'}")
    print(f"   Fast Hashing: {'✓' if optimizer.hash_enabled else '✗'}")
    print(f"   Event Loop: {'uvloop' if UVLOOP_AVAILABLE else 'asyncio'}")
