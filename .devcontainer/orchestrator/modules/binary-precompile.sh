#!/bin/bash
# Binary Precompilation Module
# Handles Python package and dependency precompilation

set -euo pipefail

source "$(dirname "$0")/../utils/logging.sh"

binary_precompilation_main() {
    info "Starting binary precompilation module"
    
    # Set up cache directories
    setup_cache_directories
    
    # Precompile Python packages
    precompile_python_packages
    
    # Optimize bytecode compilation
    optimize_bytecode
    
    # Precompile wheels
    precompile_wheels
    
    info "Binary precompilation module completed"
}

setup_cache_directories() {
    local cache_dirs=(
        "/opt/mcp-cache/python"
        "/opt/mcp-cache/wheels"
        "/opt/mcp-cache/bytecode"
        "/opt/mcp-cache/numba"
        "/opt/mcp-cache/cuda"
    )
    
    for dir in "${cache_dirs[@]}"; do
        mkdir -p "$dir"
        chmod 755 "$dir"
    done
    
    info "Cache directories configured"
}

precompile_python_packages() {
    if command -v uv &> /dev/null; then
        info "Precompiling Python packages with UV"
        uv pip compile --generate-hashes requirements.txt > requirements.lock 2>/dev/null || true
        uv pip sync requirements.lock --cache-dir "${CACHE_UV_DIR}" 2>/dev/null || true
    fi
}

optimize_bytecode() {
    info "Optimizing Python bytecode compilation"
    
    # Precompile standard library
    python3 -m py_compile /usr/local/lib/python*/site-packages/**/*.py 2>/dev/null || true
    
    # Optimize imports
    python3 -c "
import compileall
import sys
compileall.compile_dir('/usr/local/lib/python' + sys.version[:3] + '/site-packages', 
                      force=True, optimize=2, quiet=1)
" 2>/dev/null || true
}

precompile_wheels() {
    local wheel_cache="${CACHE_WHEELS_DIR:-/opt/mcp-cache/wheels}"
    
    if [[ -f requirements.txt ]]; then
        info "Building wheels for requirements"
        pip wheel --wheel-dir "$wheel_cache" -r requirements.txt --cache-dir "${CACHE_PIP_DIR}" 2>/dev/null || true
    fi
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    binary_precompilation_main "$@"
fi
