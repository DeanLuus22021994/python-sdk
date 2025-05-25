#!/bin/bash
# Common utility functions for all MCP SDK scripts
# Provides logging, error handling, and common functionality following DRY principle

set -euo pipefail

# Colors for output
export RED='\033[0;31m'
export GREEN='\033[0;32m'
export YELLOW='\033[1;33m'
export BLUE='\033[0;34m'
export PURPLE='\033[0;35m'
export CYAN='\033[0;36m'
export WHITE='\033[1;37m'
export NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO:${NC} $1"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] SUCCESS:${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
}

log_debug() {
    if [[ "${DEBUG_MODE:-false}" == "true" ]]; then
        echo -e "${PURPLE}[$(date +'%Y-%m-%d %H:%M:%S')] DEBUG:${NC} $1"
    fi
}

log_step() {
    echo -e "${CYAN}[$(date +'%Y-%m-%d %H:%M:%S')] STEP:${NC} $1"
}

# Error handling
handle_error() {
    local exit_code=$?
    local line_number=$1
    log_error "Script failed at line $line_number with exit code $exit_code"
    cleanup_on_error
    exit $exit_code
}

# Set up error trapping
trap 'handle_error $LINENO' ERR

# Cleanup function
cleanup_on_error() {
    log_warning "Performing cleanup on error..."
    # Add any cleanup operations here
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root"
        exit 1
    fi
}

# Check if running in privileged container
check_privileged() {
    if [[ ! -f /.dockerenv ]]; then
        log_warning "Not running in a Docker container"
        return 1
    fi
    
    # Check for privileged capabilities
    if ! capsh --print | grep -q "cap_sys_admin"; then
        log_error "Container must be run in privileged mode"
        exit 1
    fi
}

# Load environment variables from .env file
load_env() {
    local env_file="${1:-${WORKSPACE_FOLDER:-/workspaces/python-sdk}/.devcontainer/.env}"
    
    if [[ -f "$env_file" ]]; then
        log_debug "Loading environment variables from $env_file"
        # Export variables from .env file
        set -a
        source "$env_file"
        set +a
        log_success "Environment variables loaded from $env_file"
    else
        log_warning "Environment file not found: $env_file"
    fi
}

# Create directory with proper permissions
create_dir() {
    local dir_path="$1"
    local permissions="${2:-755}"
    local owner="${3:-root:root}"
    
    if [[ ! -d "$dir_path" ]]; then
        log_debug "Creating directory: $dir_path"
        mkdir -p "$dir_path"
        chmod "$permissions" "$dir_path"
        chown "$owner" "$dir_path"
        log_success "Created directory: $dir_path"
    else
        log_debug "Directory already exists: $dir_path"
    fi
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Install package if not present
install_package() {
    local package="$1"
    local install_cmd="${2:-apt-get install -y}"
    
    if ! dpkg -l | grep -q "^ii  $package "; then
        log_step "Installing package: $package"
        eval "$install_cmd $package"
        log_success "Package installed: $package"
    else
        log_debug "Package already installed: $package"
    fi
}

# Download file with retry logic
download_file() {
    local url="$1"
    local output_path="$2"
    local max_retries="${3:-3}"
    local timeout="${4:-30}"
    
    local retry_count=0
    
    while [[ $retry_count -lt $max_retries ]]; do
        log_debug "Downloading $url (attempt $((retry_count + 1))/$max_retries)"
        
        if curl -fsSL --connect-timeout "$timeout" --max-time $((timeout * 2)) "$url" -o "$output_path"; then
            log_success "Downloaded: $url -> $output_path"
            return 0
        else
            ((retry_count++))
            if [[ $retry_count -lt $max_retries ]]; then
                log_warning "Download failed, retrying in 5 seconds..."
                sleep 5
            fi
        fi
    done
    
    log_error "Failed to download $url after $max_retries attempts"
    return 1
}

# Execute command with timeout
execute_with_timeout() {
    local timeout="$1"
    shift
    local cmd=("$@")
    
    log_debug "Executing with ${timeout}s timeout: ${cmd[*]}"
    
    if timeout "$timeout" "${cmd[@]}"; then
        log_success "Command completed successfully: ${cmd[*]}"
        return 0
    else
        local exit_code=$?
        if [[ $exit_code -eq 124 ]]; then
            log_error "Command timed out after ${timeout}s: ${cmd[*]}"
        else
            log_error "Command failed with exit code $exit_code: ${cmd[*]}"
        fi
        return $exit_code
    fi
}

# Check system requirements
check_system_requirements() {
    log_step "Checking system requirements..."
    
    # Check minimum memory
    local min_memory_gb=8
    local available_memory_gb=$(( $(grep MemTotal /proc/meminfo | awk '{print $2}') / 1024 / 1024 ))
    
    if [[ $available_memory_gb -lt $min_memory_gb ]]; then
        log_warning "Available memory (${available_memory_gb}GB) is less than recommended (${min_memory_gb}GB)"
    else
        log_success "Memory check passed: ${available_memory_gb}GB available"
    fi
    
    # Check minimum disk space
    local min_space_gb=20
    local available_space_gb=$(df / | awk 'NR==2 {print int($4/1024/1024)}')
    
    if [[ $available_space_gb -lt $min_space_gb ]]; then
        log_error "Available disk space (${available_space_gb}GB) is less than required (${min_space_gb}GB)"
        return 1
    else
        log_success "Disk space check passed: ${available_space_gb}GB available"
    fi
    
    # Check CPU cores
    local min_cores=2
    local available_cores=$(nproc)
    
    if [[ $available_cores -lt $min_cores ]]; then
        log_warning "Available CPU cores ($available_cores) is less than recommended ($min_cores)"
    else
        log_success "CPU check passed: $available_cores cores available"
    fi
    
    log_success "System requirements check completed"
}

# Get CPU architecture
get_cpu_architecture() {
    local arch=$(uname -m)
    case "$arch" in
        x86_64)
            echo "x86_64"
            ;;
        aarch64|arm64)
            echo "arm64"
            ;;
        armv7l)
            echo "armv7"
            ;;
        *)
            echo "unknown"
            ;;
    esac
}

# Get CPU features
get_cpu_features() {
    local features=()
    
    if grep -q "avx2" /proc/cpuinfo; then
        features+=("avx2")
    fi
    
    if grep -q "avx512" /proc/cpuinfo; then
        features+=("avx512")
    fi
    
    if grep -q "sse4" /proc/cpuinfo; then
        features+=("sse4")
    fi
    
    if grep -q "fma" /proc/cpuinfo; then
        features+=("fma")
    fi
    
    printf '%s\n' "${features[@]}"
}

# Progress bar function
show_progress() {
    local current="$1"
    local total="$2"
    local width=50
    local percentage=$((current * 100 / total))
    local completed=$((current * width / total))
    local remaining=$((width - completed))
    
    printf "\r["
    printf "%*s" $completed | tr ' ' '='
    printf "%*s" $remaining | tr ' ' '-'
    printf "] %d%% (%d/%d)" $percentage $current $total
}

# Benchmark function
benchmark() {
    local description="$1"
    local command="$2"
    
    log_step "Benchmarking: $description"
    local start_time=$(date +%s.%N)
    
    eval "$command"
    local exit_code=$?
    
    local end_time=$(date +%s.%N)
    local duration=$(echo "$end_time - $start_time" | bc)
    
    if [[ $exit_code -eq 0 ]]; then
        log_success "Benchmark completed in ${duration}s: $description"
    else
        log_error "Benchmark failed after ${duration}s: $description"
    fi
    
    return $exit_code
}

# Cleanup temporary files
cleanup_temp() {
    log_debug "Cleaning up temporary files..."
    
    local temp_dirs=(
        "/tmp/mcp-*"
        "/tmp/python-*"
        "/tmp/build-*"
    )
    
    for pattern in "${temp_dirs[@]}"; do
        if compgen -G "$pattern" > /dev/null; then
            rm -rf $pattern
            log_debug "Cleaned up: $pattern"
        fi
    done
}

# Initialize common variables
init_common() {
    # Load environment variables
    load_env
    
    # Set default values from environment or use defaults
    export WORKSPACE_FOLDER="${WORKSPACE_FOLDER:-/workspaces/python-sdk}"
    export CACHE_ROOT="${CACHE_ROOT:-/opt/mcp-cache}"
    export DEBUG_MODE="${DEBUG_MODE:-false}"
    export LOG_LEVEL="${LOG_LEVEL:-INFO}"
    
    # Create cache directories
    create_dir "$CACHE_ROOT"
    create_dir "${UV_CACHE_DIR:-$CACHE_ROOT/python-cache/uv}"
    create_dir "${PIP_CACHE_DIR:-$CACHE_ROOT/python-cache/pip}"
    create_dir "${NUMBA_CACHE_DIR:-$CACHE_ROOT/numba-cache}"
    create_dir "${CUDA_CACHE_PATH:-$CACHE_ROOT/cuda-cache}"
    create_dir "${RUST_CACHE_DIR:-$CACHE_ROOT/rust-cache}"
    
    log_success "Common utilities initialized"
}

# Export all functions
export -f log log_success log_warning log_error log_debug log_step
export -f handle_error cleanup_on_error check_root check_privileged
export -f load_env create_dir command_exists install_package
export -f download_file execute_with_timeout check_system_requirements
export -f get_cpu_architecture get_cpu_features show_progress
export -f benchmark cleanup_temp init_common
