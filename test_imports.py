#!/usr/bin/env python3
"""
Test script to verify all MCP SDK imports and functionality work correctly.
This addresses the import and type errors seen in VS Code.
"""

import sys
import traceback
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_import(module_name, description=""):
    """Test importing a module and report results."""
    try:
        __import__(module_name)
        print(f"✓ {module_name} - {description}")
        return True
    except Exception as e:
        print(f"✗ {module_name} - {description}: {e}")
        return False


def test_performance_module():
    """Test the performance optimization module specifically."""
    try:
        from mcp.shared.performance import (
            get_performance_optimizer,
            enable_performance_mode,
            UVLOOP_AVAILABLE,
            JSON_BACKEND,
            LZ4_AVAILABLE,
            ZSTD_AVAILABLE,
            XXHASH_AVAILABLE,
        )

        print(f"✓ Performance module imported successfully")
        print(f"  - JSON Backend: {JSON_BACKEND}")
        print(f"  - UVLOOP Available: {UVLOOP_AVAILABLE}")
        print(f"  - LZ4 Available: {LZ4_AVAILABLE}")
        print(f"  - ZSTD Available: {ZSTD_AVAILABLE}")
        print(f"  - XXHASH Available: {XXHASH_AVAILABLE}")

        # Test basic functionality
        optimizer = get_performance_optimizer()
        test_data = {"test": "data", "number": 42}
        json_bytes = optimizer.optimize_json_serialization(test_data)
        print(f"  - JSON serialization test: {len(json_bytes)} bytes")

        test_bytes = b"hello world test data"
        if LZ4_AVAILABLE:
            compressed = optimizer.compress_data(test_bytes)
            print(f"  - Compression test: {len(test_bytes)} -> {len(compressed)} bytes")

        hash_result = optimizer.calculate_hash(test_bytes)
        print(f"  - Hash test: {hash_result[:16]}...")

        return True
    except Exception as e:
        print(f"✗ Performance module test failed: {e}")
        traceback.print_exc()
        return False


def main():
    print("🧪 Testing MCP SDK imports and functionality...")
    print("=" * 60)

    # Core imports
    results = []
    results.append(test_import("mcp", "Main MCP module"))
    results.append(test_import("mcp.types", "MCP types"))
    results.append(test_import("mcp.client", "MCP client"))
    results.append(test_import("mcp.server", "MCP server"))
    results.append(test_import("mcp.shared", "MCP shared utilities"))

    # Specific modules that were causing issues
    results.append(test_import("mcp.shared.performance", "Performance optimizations"))
    results.append(test_import("mcp.client.sse", "SSE client"))
    results.append(test_import("mcp.server.streamable_http", "Streamable HTTP"))

    # Third-party dependencies
    results.append(test_import("asyncpg", "PostgreSQL async driver"))
    results.append(test_import("httpx_sse", "HTTPX SSE"))
    results.append(test_import("sse_starlette", "SSE Starlette"))
    results.append(test_import("pydantic_ai", "Pydantic AI"))
    results.append(test_import("pgvector", "PG Vector"))
    results.append(test_import("orjson", "Optimized JSON"))
    results.append(test_import("lz4", "LZ4 compression"))
    results.append(test_import("ujson", "Ultra JSON"))

    # Optional dependencies
    try:
        import uvloop

        results.append(test_import("uvloop", "UV event loop (optional on Windows)"))
    except ImportError:
        print("⚠ uvloop - UV event loop (not available on Windows - expected)")

    print("\n" + "=" * 60)
    print("🔧 Testing performance module functionality...")
    performance_test = test_performance_module()

    print("\n" + "=" * 60)

    # Summary
    passed = sum(results) + (1 if performance_test else 0)
    total = len(results) + 1
    failed = total - passed

    print(f"📊 Test Results: {passed}/{total} passed")
    if failed == 0:
        print("🎉 All tests passed! MCP SDK is ready for development.")
        return 0
    else:
        print(f"❌ {failed} tests failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
