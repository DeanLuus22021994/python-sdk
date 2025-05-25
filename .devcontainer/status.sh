#!/bin/bash
# MCP SDK Performance Status Dashboard

echo "🚀 MCP Python SDK - Performance Status Dashboard"
echo "================================================"
echo ""

# Cache status
CACHE_ROOT="/opt/mcp-cache"
if [ -d "$CACHE_ROOT" ]; then
    echo "💾 Binary Cache Status:"
    for cache_dir in python-cache wheels bytecode numba-cache; do
        if [ -d "$CACHE_ROOT/$cache_dir" ]; then
            size=$(du -sh "$CACHE_ROOT/$cache_dir" 2>/dev/null | cut -f1)
            files=$(find "$CACHE_ROOT/$cache_dir" -type f 2>/dev/null | wc -l)
            echo "  ✅ $cache_dir: $size ($files files)"
        else
            echo "  ❌ $cache_dir: Not found"
        fi
    done
    
    total_size=$(du -sh "$CACHE_ROOT" 2>/dev/null | cut -f1)
    echo "  📊 Total cache size: $total_size"
else
    echo "❌ Binary cache not initialized"
fi

echo ""

# Build info
BUILD_INFO="/opt/mcp-cache/build-info.json"
if [ -f "$BUILD_INFO" ]; then
    echo "🏗️  Last Build Information:"
    BUILD_DATE=$(jq -r '.build_completed' "$BUILD_INFO" 2>/dev/null || echo "Unknown")
    BUILD_DURATION=$(jq -r '.build_duration_seconds' "$BUILD_INFO" 2>/dev/null || echo "Unknown")
    echo "  📅 Completed: $BUILD_DATE"
    echo "  ⏱️  Duration: ${BUILD_DURATION}s"
else
    echo "❌ No build information available"
fi

echo ""

# System performance
echo "🖥️  System Performance:"
echo "  🔧 CPU cores: $(nproc)"
echo "  🧠 Memory: $(free -h | awk '/^Mem:/{print $2}') total, $(free -h | awk '/^Mem:/{print $7}') available"
echo "  💾 Disk: $(df -h /opt | awk 'NR==2{print $4}') available"

echo ""

# Environment status
echo "⚙️  Environment Configuration:"
echo "  🐍 Python optimization: $PYTHONOPTIMIZE"
echo "  ⚡ Python GIL: $PYTHON_GIL"
echo "  💾 UV cache: $UV_CACHE_DIR"
echo "  📦 PIP cache: $PIP_CACHE_DIR"
echo "  🔥 Numba cache: $NUMBA_CACHE_DIR"

echo ""

# Performance test
echo "🧪 Quick Performance Test:"
python3 -c "
import time
start = time.time()

# Test imports
import mcp
from mcp.server.fastmcp import FastMCP
import uvloop, orjson, numba

import_time = time.time() - start
print(f'  ✅ Import test: {import_time:.3f}s')

# Test JSON performance
import json
test_data = {'test': list(range(1000))}

json_start = time.time()
json_str = json.dumps(test_data)
json.loads(json_str)
json_time = time.time() - json_start

orjson_start = time.time()
orjson_bytes = orjson.dumps(test_data)
orjson.loads(orjson_bytes)
orjson_time = time.time() - orjson_start

speedup = json_time / orjson_time if orjson_time > 0 else 0
print(f'  ⚡ JSON speedup: {speedup:.1f}x (orjson vs standard)')
"

echo ""
echo "🎯 Ready for high-performance MCP development!"
echo "Run 'bash .devcontainer/validate-performance.sh' for full validation"
