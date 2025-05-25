#!/bin/bash
# Performance Validator
# Validates that all performance optimizations are properly applied

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../../config/load-env.sh"

validate_cpu_optimizations() {
    echo "=== CPU Optimization Validation ==="
    
    local issues=0
    
    # Check CPU governor
    echo "Checking CPU governor..."
    for cpu in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
        if [[ -f "$cpu" ]]; then
            local governor=$(cat "$cpu")
            if [[ "$governor" != "performance" ]]; then
                echo "❌ CPU governor not set to performance: $governor"
                ((issues++))
            else
                echo "✓ CPU governor set to performance"
                break
            fi
        fi
    done
    
    # Check CPU frequency scaling
    echo "Checking CPU frequency scaling..."
    local max_freq_set=false
    for cpu in /sys/devices/system/cpu/cpu*/cpufreq/scaling_max_freq; do
        if [[ -f "$cpu" ]]; then
            local current_max=$(cat "$cpu")
            local available_max=$(cat "${cpu%/*}/cpuinfo_max_freq")
            if [[ "$current_max" -lt "$available_max" ]]; then
                echo "❌ CPU not running at maximum frequency"
                ((issues++))
            else
                echo "✓ CPU running at maximum frequency"
                max_freq_set=true
                break
            fi
        fi
    done
    
    return $issues
}

validate_memory_optimizations() {
    echo "=== Memory Optimization Validation ==="
    
    local issues=0
    
    # Check swappiness
    echo "Checking swappiness..."
    local swappiness=$(cat /proc/sys/vm/swappiness)
    if [[ $swappiness -gt 10 ]]; then
        echo "❌ Swappiness too high: $swappiness (should be ≤10)"
        ((issues++))
    else
        echo "✓ Swappiness optimized: $swappiness"
    fi
    
    # Check dirty ratios
    echo "Checking dirty ratios..."
    local dirty_ratio=$(cat /proc/sys/vm/dirty_ratio)
    if [[ $dirty_ratio -gt 20 ]]; then
        echo "❌ Dirty ratio too high: $dirty_ratio (should be ≤20)"
        ((issues++))
    else
        echo "✓ Dirty ratio optimized: $dirty_ratio"
    fi
    
    # Check huge pages
    echo "Checking transparent huge pages..."
    if [[ -f /sys/kernel/mm/transparent_hugepage/enabled ]]; then
        local thp=$(cat /sys/kernel/mm/transparent_hugepage/enabled)
        if [[ "$thp" == *"[never]"* ]]; then
            echo "❌ Transparent huge pages disabled"
            ((issues++))
        else
            echo "✓ Transparent huge pages enabled"
        fi
    fi
    
    return $issues
}

validate_io_optimizations() {
    echo "=== I/O Optimization Validation ==="
    
    local issues=0
    
    # Check disk schedulers
    echo "Checking disk schedulers..."
    for scheduler in /sys/block/*/queue/scheduler; do
        if [[ -f "$scheduler" ]]; then
            local current=$(cat "$scheduler" | grep -o '\[.*\]' | tr -d '[]')
            if [[ "$current" != "mq-deadline" && "$current" != "none" ]]; then
                echo "❌ Suboptimal disk scheduler: $current"
                ((issues++))
            else
                echo "✓ Optimal disk scheduler: $current"
                break
            fi
        fi
    done
    
    # Check network buffer sizes
    echo "Checking network buffer sizes..."
    local rmem_max=$(cat /proc/sys/net/core/rmem_max)
    if [[ $rmem_max -lt 134217728 ]]; then
        echo "❌ Network receive buffer too small: $rmem_max"
        ((issues++))
    else
        echo "✓ Network receive buffer optimized: $rmem_max"
    fi
    
    return $issues
}

validate_gpu_setup() {
    echo "=== GPU Setup Validation ==="
    
    local issues=0
    
    # Check for NVIDIA GPU
    if command -v nvidia-smi &> /dev/null; then
        echo "Checking NVIDIA GPU..."
        if nvidia-smi &> /dev/null; then
            echo "✓ NVIDIA GPU detected and working"
            
            # Check Docker GPU support
            if command -v docker &> /dev/null; then
                if docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi &> /dev/null; then
                    echo "✓ Docker GPU support working"
                else
                    echo "❌ Docker GPU support not working"
                    ((issues++))
                fi
            fi
        else
            echo "❌ NVIDIA GPU detected but not working"
            ((issues++))
        fi
    else
        echo "ℹ No NVIDIA GPU detected"
    fi
    
    return $issues
}

validate_docker_setup() {
    echo "=== Docker Setup Validation ==="
    
    local issues=0
    
    # Check Docker daemon
    echo "Checking Docker daemon..."
    if ! docker info &> /dev/null; then
        echo "❌ Docker daemon not running"
        ((issues++))
    else
        echo "✓ Docker daemon running"
    fi
    
    # Check Docker Swarm
    echo "Checking Docker Swarm..."
    local swarm_state=$(docker info --format '{{.Swarm.LocalNodeState}}')
    if [[ "$swarm_state" != "active" ]]; then
        echo "❌ Docker Swarm not active: $swarm_state"
        ((issues++))
    else
        echo "✓ Docker Swarm active"
    fi
    
    # Check volumes
    echo "Checking external volumes..."
    local required_volumes=("mcp-cache" "python-wheels" "postgres-data" "redis-data")
    for volume in "${required_volumes[@]}"; do
        if ! docker volume inspect "$volume" &> /dev/null; then
            echo "❌ Volume missing: $volume"
            ((issues++))
        else
            echo "✓ Volume exists: $volume"
        fi
    done
    
    return $issues
}

validate_environment() {
    echo "=== Environment Validation ==="
    
    local issues=0
    
    # Load environment files
    load_env_files
    
    # Check critical environment variables
    local required_vars=("PYTHONOPTIMIZE" "OMP_NUM_THREADS" "CACHE_ROOT")
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            echo "❌ Environment variable not set: $var"
            ((issues++))
        else
            echo "✓ Environment variable set: $var=${!var}"
        fi
    done
    
    return $issues
}

main() {
    echo "Performance Optimization Validation"
    echo "===================================="
    echo
    
    local total_issues=0
    
    validate_cpu_optimizations
    total_issues=$((total_issues + $?))
    echo
    
    validate_memory_optimizations
    total_issues=$((total_issues + $?))
    echo
    
    validate_io_optimizations
    total_issues=$((total_issues + $?))
    echo
    
    validate_gpu_setup
    total_issues=$((total_issues + $?))
    echo
    
    validate_docker_setup
    total_issues=$((total_issues + $?))
    echo
    
    validate_environment
    total_issues=$((total_issues + $?))
    echo
    
    echo "===================================="
    if [[ $total_issues -eq 0 ]]; then
        echo "🎉 All performance optimizations validated successfully!"
        exit 0
    else
        echo "❌ Found $total_issues optimization issues"
        exit 1
    fi
}

main "$@"
