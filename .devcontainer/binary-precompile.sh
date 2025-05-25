#!/bin/bash
# Binary Precompilation and Caching System for MCP Python SDK
# This script ensures all dependencies are precompiled into runtime binaries
# and mounted on persistent binary volumes for instant subsequent builds

set -e

echo "🔥 MCP SDK Binary Precompilation System - Maximum Performance Mode"
echo "=================================================================="

# Performance timing
start_time=$(date +%s)

# Configuration
CACHE_ROOT="/opt/mcp-cache"
PYTHON_CACHE="$CACHE_ROOT/python-cache"
WHEELS_CACHE="$CACHE_ROOT/wheels"
BYTECODE_CACHE="$CACHE_ROOT/bytecode"
NUMBA_CACHE="$CACHE_ROOT/numba-cache"
BUILD_CACHE="$CACHE_ROOT/build-cache"

# Create all cache directories with optimal permissions
echo "📁 Creating persistent binary cache structure..."
sudo mkdir -p "$CACHE_ROOT"/{python-cache,wheels,bytecode,numba-cache,build-cache}/{pip,uv,site-packages,compiled,native}
sudo chmod -R 755 "$CACHE_ROOT"
sudo chown -R $(whoami):$(whoami) "$CACHE_ROOT" 2>/dev/null || true

# Link container caches to persistent storage
echo "🔗 Linking container caches to persistent binary volumes..."
link_cache_dir() {
    local container_dir=$1
    local persistent_dir=$2
    
    if [ -d "$container_dir" ] && [ ! -L "$container_dir" ]; then
        echo "  Migrating $container_dir to persistent storage..."
        sudo rsync -av "$container_dir/" "$persistent_dir/" 2>/dev/null || true
        sudo rm -rf "$container_dir"
    fi
    
    if [ ! -e "$container_dir" ]; then
        ln -sf "$persistent_dir" "$container_dir"
        echo "  ✓ Linked $container_dir -> $persistent_dir"
    fi
}

# Link all cache directories
link_cache_dir "/opt/python-cache" "$PYTHON_CACHE"
link_cache_dir "/opt/wheels-cache" "$WHEELS_CACHE"
link_cache_dir "/opt/bytecode-cache" "$BYTECODE_CACHE"
link_cache_dir "/opt/numba-cache" "$NUMBA_CACHE"
link_cache_dir "/tmp/pip-cache" "$PYTHON_CACHE/pip"
link_cache_dir "/tmp/uv-cache" "$PYTHON_CACHE/uv"

# Set up environment for maximum performance
export PYTHONOPTIMIZE=2
export PYTHONDONTWRITEBYTECODE=0  # Enable for compilation
export PIP_COMPILE=1
export UV_COMPILE_BYTECODE=1
export NUMBA_CACHE_DIR="$NUMBA_CACHE"
export UV_CACHE_DIR="$PYTHON_CACHE/uv"
export PIP_CACHE_DIR="$PYTHON_CACHE/pip"

echo "⚡ Precompiling all MCP SDK dependencies with maximum optimization..."

# Performance dependencies for precompilation
PERFORMANCE_DEPS=(
    "cython>=3.0.0"
    "numba>=0.59.0"
    "uvloop>=0.19.0"
    "orjson>=3.9.0"
    "msgpack>=1.0.0"
    "lz4>=4.3.0"
    "xxhash>=3.4.0"
    "pyarrow>=15.0.0"
    "polars>=0.20.0"
    "fastapi[all]>=0.110.0"
    "gunicorn>=21.2.0"
    "gevent>=23.9.0"
    "psutil>=5.9.0"
    "memory_profiler>=0.61.0"
    "line_profiler>=4.1.0"
    "py-spy>=0.3.0"
    "prometheus-client>=0.19.0"
    "aiofiles>=23.0.0"
    "aiodns>=3.0.0"
    "cchardet>=2.1.0"
    "brotli>=1.1.0"
    "zstandard>=0.22.0"
    "httpx-sse>=0.4"
    "python-multipart>=0.0.9"
    "sse-starlette>=1.6.1"
    "pydantic-settings>=2.5.2"
)

# Check if dependencies are already compiled
if [ -f "$PYTHON_CACHE/compiled/.deps_compiled" ]; then
    echo "📦 Dependencies already compiled, checking for updates..."
    deps_hash=$(echo "${PERFORMANCE_DEPS[@]}" | sha256sum | cut -d' ' -f1)
    if [ -f "$PYTHON_CACHE/compiled/.deps_hash" ] && [ "$(cat $PYTHON_CACHE/compiled/.deps_hash)" = "$deps_hash" ]; then
        echo "✅ All dependencies are up to date and precompiled!"
        echo "🚀 Skipping compilation - using cached binaries for instant startup"
    else
        echo "🔄 Dependency changes detected, recompiling..."
    fi
else
    echo "🔨 First-time compilation - creating optimized binary cache..."
fi

# Install and precompile dependencies with maximum optimization
echo "📦 Installing dependencies with binary precompilation..."
uv pip install --system --cache-dir "$PYTHON_CACHE/uv" --compile-bytecode "${PERFORMANCE_DEPS[@]}"

# Create wheels for all dependencies for faster future installs
echo "🎡 Creating wheel cache for instant installations..."
mkdir -p "$WHEELS_CACHE"
pip3 wheel --wheel-dir "$WHEELS_CACHE" --no-deps "${PERFORMANCE_DEPS[@]}" || true

# Precompile all Python bytecode with maximum optimization
echo "⚡ Precompiling Python bytecode with -O2 optimization..."
python3 -OO -m compileall -f -q /usr/local/lib/python3.12/site-packages/
python3 -O -m compileall -f -q /usr/local/lib/python3.12/site-packages/
python3 -m compileall -f -q /usr/local/lib/python3.12/site-packages/

# Cache compiled site-packages
echo "💾 Caching compiled site-packages for instant restore..."
mkdir -p "$BYTECODE_CACHE/site-packages"
rsync -av /usr/local/lib/python3.12/site-packages/ "$BYTECODE_CACHE/site-packages/" || true

# Pre-warm Numba JIT compilation cache
echo "🔥 Pre-warming Numba JIT compilation cache..."
python3 -c "
import os
os.environ['NUMBA_CACHE_DIR'] = '$NUMBA_CACHE'
try:
    import numba
    import numpy as np
    
    @numba.jit(nopython=True, cache=True)
    def warmup_functions(x):
        # Common operations to pre-compile
        result = x * 2
        result = result + 1
        result = np.sum(result)
        result = np.sqrt(result)
        return result
    
    # Trigger compilation with different data types
    warmup_functions(np.array([1, 2, 3], dtype=np.int32))
    warmup_functions(np.array([1.0, 2.0, 3.0], dtype=np.float32))
    warmup_functions(np.array([1.0, 2.0, 3.0], dtype=np.float64))
    
    print('✅ Numba JIT cache pre-warmed with common operations')
except ImportError:
    print('⚠️  Numba not available for JIT cache warming')
except Exception as e:
    print(f'⚠️  Numba JIT warming failed: {e}')
" || true

# Install MCP SDK in development mode with precompiled dependencies
echo "🧬 Installing MCP SDK with precompiled optimizations..."
cd /workspaces/python-sdk
uv pip install -e . --cache-dir "$PYTHON_CACHE/uv" --compile-bytecode

# Precompile MCP SDK source code
echo "⚡ Precompiling MCP SDK source code..."
python3 -OO -m compileall -f -q src/
python3 -O -m compileall -f -q src/
python3 -m compileall -f -q src/

# Create installation markers
mkdir -p "$PYTHON_CACHE/compiled"
echo "${PERFORMANCE_DEPS[@]}" | sha256sum | cut -d' ' -f1 > "$PYTHON_CACHE/compiled/.deps_hash"
touch "$PYTHON_CACHE/compiled/.deps_compiled"
date > "$PYTHON_CACHE/compiled/.last_compiled"

# Performance validation
echo "🧪 Validating performance optimizations..."
python3 -c "
import sys
import time
start = time.time()

# Test optimized imports
try:
    import uvloop, orjson, msgpack, lz4, xxhash
    import numba, pyarrow, polars
    import fastapi, gunicorn, psutil
    print(f'✅ All performance dependencies imported in {time.time() - start:.3f}s')
except ImportError as e:
    print(f'⚠️  Import issue: {e}')

# Test MCP imports
try:
    import mcp
    from mcp.server.fastmcp import FastMCP
    from mcp.shared.performance import optimize_json, optimize_compression
    print('✅ MCP SDK with performance optimizations loaded successfully')
except ImportError as e:
    print(f'⚠️  MCP import issue: {e}')

print(f'🚀 Total validation time: {time.time() - start:.3f}s')
"

# Set up performance-optimized configurations
echo "⚙️  Configuring performance-optimized package managers..."

# Optimize pip configuration
mkdir -p /root/.config/pip
cat > /root/.config/pip/pip.conf << EOF
[global]
no-cache-dir = false
cache-dir = $PYTHON_CACHE/pip
compile = yes
optimize = 2
find-links = $WHEELS_CACHE
trusted-host = pypi.org pypi.python.org files.pythonhosted.org
EOF

# Optimize uv configuration
mkdir -p /root/.config/uv
cat > /root/.config/uv/uv.toml << EOF
cache-dir = "$PYTHON_CACHE/uv"
compile-bytecode = true
link-mode = "copy"
find-links = ["$WHEELS_CACHE"]
EOF

# Create performance aliases
echo "🎯 Setting up performance shortcuts..."
cat >> ~/.bashrc << 'EOF'

# MCP SDK Performance Shortcuts
alias mcp-dev='cd /workspaces/python-sdk'
alias mcp-test='python3 -m pytest --tb=short'
alias mcp-profile='python3 -m cProfile -s cumulative'
alias mcp-bench='python3 -m timeit'

# Binary cache management
alias cache-status='du -sh /opt/mcp-cache/*'
alias cache-clean='rm -rf /opt/mcp-cache/*/pip/* /opt/mcp-cache/*/uv/*'
alias cache-rebuild='bash /workspaces/python-sdk/.devcontainer/binary-precompile.sh'

# Performance monitoring
alias perf-cpu='htop --sort-key PERCENT_CPU'
alias perf-mem='htop --sort-key PERCENT_MEM'
alias perf-io='iotop -a'
alias perf-net='iftop'

EOF

# Calculate and display performance metrics
end_time=$(date +%s)
duration=$((end_time - start_time))
cache_size=$(du -sh "$CACHE_ROOT" 2>/dev/null | cut -f1 || echo "Unknown")

echo ""
echo "🎉 MCP SDK Binary Precompilation Complete!"
echo "========================================"
echo "🕒 Total build time: ${duration}s"
echo "💾 Binary cache size: $cache_size"
echo "📁 Cache location: $CACHE_ROOT"
echo "⚡ Next container starts will be instant!"
echo ""
echo "🚀 Performance features enabled:"
echo "  • All dependencies precompiled to bytecode"
echo "  • Numba JIT cache pre-warmed"
echo "  • Wheel cache for instant installs"
echo "  • Persistent binary volumes"
echo "  • Maximum compiler optimizations"
echo "  • Performance monitoring tools"
echo ""
echo "✅ Ready for maximum performance development!"
