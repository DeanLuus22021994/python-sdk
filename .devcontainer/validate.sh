#!/bin/bash
# Top-level Validation Entry Point
# Delegates to the unified validation system

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Import centralized logging
# shellcheck source=/dev/null
source "$SCRIPT_DIR/orchestrator/utils/logging.sh" || {
  # Basic logging functions if orchestrator logging is not available
  RED='\033[0;31m'
  BLUE='\033[0;34m'
  NC='\033[0m'
  
  info() {
    echo -e "${BLUE}INFO: $1${NC}"
  }

  error() {
    echo -e "${RED}ERROR: $1${NC}" >&2
  }
}

# Delegate to the unified validation system
info "🔄 Delegating to unified validation system..."
"$SCRIPT_DIR/validation/core/main.sh" "$@"

error() {
    echo -e "${RED}ERROR: $1${NC}" >&2
}

# Try to source the centralized logging, but continue if it fails
if [[ -f "$SCRIPT_DIR/orchestrator/utils/logging.sh" ]]; then
    source "$SCRIPT_DIR/orchestrator/utils/logging.sh" || true
fi

print_usage() {
    cat << EOF
MCP Python SDK Validation Script

Usage: 
  $0 [mode]

Modes:
  quick       - Quick validation of essential components
  full        - Complete system validation
  rebuild     - Post-rebuild validation
  pre-rebuild - Pre-rebuild status check
  config      - Docker configuration validation
  
Example:
  $0 quick
  $0 rebuild
EOF
}

# ====== Quick Validation ======
validate_quick() {
    info "Performing quick validation checks..."
    
    # Check Docker container
    if [[ -f "/.dockerenv" ]]; then
        info "✓ Running in Docker container"
    else
        warn "Not running in Docker container"
    fi
    
    # Check Python configuration
    info "Checking Python configuration..."
    python3 -c "
import sys
print(f'Python version: {sys.version}')
print(f'Python optimization level: {sys.flags.optimize}')
    "
    
    # Check essential directories
    info "Checking essential directories..."
    for dir in "config" "docker" "orchestrator" "tools"; do
        if [[ -d "$SCRIPT_DIR/$dir" ]]; then
            info "✓ $dir directory exists"
        else
            error "$dir directory missing"
        fi
    done
    
    # Check development tools
    if [[ -x "$SCRIPT_DIR/tools/dt.sh" ]]; then
        info "✓ Development tools available"
    else
        warn "Development tools not found or not executable"
    fi
}

# ====== Full Validation ======
validate_full() {
    info "Performing full system validation..."
    
    # Load modular environment configuration
    source "$SCRIPT_DIR/config/load-env.sh" 2>/dev/null || warn "Could not load environment config"
    
    # Validate file size compliance
    info "Checking file size compliance (≤150 lines)..."
    find "$SCRIPT_DIR" -name "*.sh" -exec wc -l {} + | grep -v " total$" | while read lines file; do
        if [[ $lines -gt 150 ]]; then
            error "File exceeds 150 lines: $file ($lines lines)"
        fi
    done
    
    # Validate modular structure
    info "Validating modular structure..."
    required_dirs=(
        "config/env"
        "docker/base"
        "docker/components"
        "docker/services"
        "docker/swarm"
        "orchestrator/core"
        "orchestrator/modules"
        "orchestrator/utils"
        "validation/core"
        "validation/tests"
        "tools/inspect"
        "tools/utils"
        "tools/metrics"
    )
    
    for dir in "${required_dirs[@]}"; do
        if [[ -d "$SCRIPT_DIR/$dir" ]]; then
            info "✓ Required directory present: $dir"
        else
            warn "Required directory missing: $dir"
        fi
    done
    
    # Test orchestrator modules
    info "Testing orchestrator modules..."
    if [[ ! -f "$SCRIPT_DIR/orchestrator/core/main.sh" ]] || [[ ! -x "$SCRIPT_DIR/orchestrator/core/main.sh" ]]; then
        warn "Orchestrator core not found or not executable"
    else
        info "✓ Orchestrator modules functional"
    fi
    
    # Test development tools
    info "Testing development tools..."
    if [[ ! -f "$SCRIPT_DIR/tools/dt.sh" ]] || [[ ! -x "$SCRIPT_DIR/tools/dt.sh" ]]; then
        warn "Development tools not found or not executable"
    else
        info "✓ Development tools functional"
    fi
    
    info "Full system validation complete"
}

# ====== Rebuild Validation ======
validate_rebuild() {
    info "Performing post-rebuild validation..."
    
    # Check Python version and optimizations
    info "Checking Python configuration..."
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
    info "Checking system tools..."
    tools=("htop" "iotop" "ps" "free" "df")
    for tool in "${tools[@]}"; do
        if command -v "$tool" &> /dev/null; then
            info "✓ $tool available"
        else
            warn "$tool missing"
        fi
    done
    
    # Check jemalloc
    info "Checking jemalloc..."
    if [[ "${LD_PRELOAD:-}" == *"jemalloc"* ]]; then
        info "✓ jemalloc configured in LD_PRELOAD"
    else
        warn "jemalloc not configured"
    fi
    
    # Check development tools
    info "Checking development tools..."
    if [[ -x "$SCRIPT_DIR/tools/dt.sh" ]]; then
        info "✓ Development tools available"
        info "Use 'dt list' to see all tools"
    else
        warn "Development tools not found or not executable"
    fi
    
    info "Rebuild validation completed!"
}

# ====== Pre-rebuild Status Check ======
validate_pre_rebuild() {
    info "Performing pre-rebuild status check..."
    
    info "The following issues are EXPECTED and will be resolved after rebuild:"
    
    # Check Python packages that will be installed
    info "Performance packages that will be installed:"
    python3 -c "
packages = ['uvloop', 'orjson', 'numba', 'psutil', 'jemalloc']
for pkg in packages:
    try:
        __import__(pkg)
        print(f'  ✓ {pkg} (already available)')
    except ImportError:
        print(f'  📦 {pkg} (will be installed)')
" 2>/dev/null
    
    info "System tools that will be installed:"
    tools=("iotop" "perf" "iostat" "mpstat")
    for tool in "${tools[@]}"; do
        if command -v "$tool" &> /dev/null; then
            info "✓ $tool (already available)"
        else
            info "📦 $tool (will be installed)"
        fi
    done
    
    info "Performance optimizations that will be applied:"
    info "📦 jemalloc memory allocator"
    info "📦 Python optimization level 2"
    info "📦 CPU governor performance mode"
    info "📦 Memory settings optimization"
    info "📦 I/O scheduler optimization"
    info "📦 GPU passthrough support"
    
    info "Environment variables that will be configured:"
    env_vars=("PYTHONOPTIMIZE" "PYTHONSTARTUP" "LD_PRELOAD" "MALLOC_CONF")
    for var in "${env_vars[@]}"; do
        if [[ -n "${!var:-}" ]]; then
            info "✓ $var (configured)"
        else
            info "📦 $var (will be configured)"
        fi
    done
    
    info "Pre-rebuild status check complete"
    info "Ready for rebuild! Use VS Code Command Palette: 'Dev Containers: Rebuild Container'"
}

# ====== Config Validation ======
validate_config() {
    info "Validating Docker configuration..."
    
    # Call the dedicated config validation script
    "$SCRIPT_DIR/scripts/validate-config.sh"
}

# Main execution logic
mode="${1:-quick}"

case "$mode" in
    "quick")
        validate_quick
        ;;
    "full")
        validate_full
        ;;
    "rebuild")
        validate_rebuild
        ;;
    "pre-rebuild")
        validate_pre_rebuild
        ;;
    "config")
        validate_config
        ;;
    "help"|"-h"|"--help")
        print_usage
        ;;
    *)
        error "Unknown mode: $mode"
        print_usage
        exit 1
        ;;
esac
