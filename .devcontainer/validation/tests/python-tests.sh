#!/bin/bash
# Python Performance Tests
# Validates Python-specific optimizations

set -euo pipefail

source "$(dirname "$0")/../../orchestrator/utils/logging.sh"

python_tests_main() {
    info "Running Python performance tests"
    
    test_python_configuration
    test_package_manager
    test_bytecode_optimization
    test_import_performance
    
    info "Python tests completed"
}

test_python_configuration() {
    info "Testing Python environment configuration"
    
    # Check Python optimization level
    local opt_level=$(python3 -c "import sys; print(sys.flags.optimize)" 2>/dev/null || echo "0")
    if [[ $opt_level -ge 1 ]]; then
        info "✓ Python optimization level: $opt_level"
    else
        warn "⚠ Python optimization not enabled"
    fi
    
    # Check environment variables
    [[ "${PYTHONOPTIMIZE:-}" == "2" ]] && info "✓ PYTHONOPTIMIZE=2"
    [[ "${PYTHONDONTWRITEBYTECODE:-}" == "1" ]] && info "✓ PYTHONDONTWRITEBYTECODE=1"
    [[ "${PYTHONUNBUFFERED:-}" == "1" ]] && info "✓ PYTHONUNBUFFERED=1"
}

test_package_manager() {
    info "Testing package manager configuration"
    
    if command -v uv &> /dev/null; then
        local uv_version=$(uv --version 2>/dev/null | head -1)
        info "✓ UV package manager available: $uv_version"
    else
        warn "⚠ UV package manager not found"
    fi
    
    # Test cache directories
    local cache_dirs=("${CACHE_UV_DIR:-}" "${CACHE_PIP_DIR:-}" "${CACHE_NUMBA_DIR:-}")
    for cache_dir in "${cache_dirs[@]}"; do
        if [[ -n "$cache_dir" ]] && [[ -d "$cache_dir" ]]; then
            info "✓ Cache directory exists: $cache_dir"
        fi
    done
}

test_bytecode_optimization() {
    info "Testing bytecode optimization"
    
    # Test bytecode compilation
    local start_time=$(date +%s.%N)
    python3 -c "
import py_compile
import tempfile
import os
with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as f:
    f.write(b'print(\"test\")')
    f.flush()
    py_compile.compile(f.name, optimize=2)
    os.unlink(f.name)
" 2>/dev/null || true
    local end_time=$(date +%s.%N)
    
    local duration=$(echo "$end_time - $start_time" | bc 2>/dev/null || echo "0.1")
    info "Bytecode compilation test completed in ${duration}s"
}

test_import_performance() {
    info "Testing import performance"
    
    # Test import speed
    local start_time=$(date +%s.%N)
    python3 -c "
import sys
import os
import json
import re
import datetime
import collections
" 2>/dev/null || true
    local end_time=$(date +%s.%N)
    
    local duration=$(echo "$end_time - $start_time" | bc 2>/dev/null || echo "0.1")
    info "Standard library import test completed in ${duration}s"
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    python_tests_main "$@"
fi
