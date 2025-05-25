#!/bin/bash
# Rebuild Validation Script
# Quick check to ensure rebuild was successful

set -euo pipefail

echo "=== DevContainer Rebuild Validation ==="

# Check if we're in the rebuilt container
if [[ -f "/.dockerenv" ]]; then
    echo "✓ Running in Docker container"
else
    echo "❌ Not running in Docker container"
fi

# Check Python version and optimizations
echo "Checking Python configuration..."
python3 -c "
import sys
import os

print(f'Python version: {sys.version}')
print(f'Python optimization level: {sys.flags.optimize}')
print(f'Python hash seed: {os.environ.get(\"PYTHONHASHSEED\", \"not set\")}')

# Check if performance packages are available
performance_packages = {
    'uvloop': 'Event loop optimization',
    'orjson': 'Fast JSON serialization',
    'numba': 'JIT compilation',
    'psutil': 'System monitoring'
}

print('\nPerformance packages:')
for pkg, desc in performance_packages.items():
    try:
        __import__(pkg)
        print(f'  ✓ {pkg} - {desc}')
    except ImportError:
        print(f'  ❌ {pkg} - {desc} (missing)')
"

# Check system tools
echo "Checking system tools..."
tools=("htop" "iotop" "ps" "free" "df")
for tool in "${tools[@]}"; do
    if command -v "$tool" &> /dev/null; then
        echo "  ✓ $tool available"
    else
        echo "  ❌ $tool missing"
    fi
done

# Check jemalloc
echo "Checking jemalloc..."
if [[ "${LD_PRELOAD:-}" == *"jemalloc"* ]]; then
    echo "  ✓ jemalloc configured in LD_PRELOAD"
else
    echo "  ❌ jemalloc not configured"
fi

# Check development tools
echo "Checking development tools..."
if [[ -x "/workspaces/python-sdk/.devcontainer/tools/dt.sh" ]]; then
    echo "  ✓ Development tools available"
    echo "  Use 'dt list' to see all tools"
else
    echo "  ❌ Development tools not found"
fi

echo "Validation completed!"
echo "For full validation, run: ./scripts/validation/performance-validator.sh"
