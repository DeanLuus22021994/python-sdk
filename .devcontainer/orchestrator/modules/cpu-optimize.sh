#!/bin/bash
# CPU Optimization Module
# Handles CPU-specific performance optimizations

set -euo pipefail

# shellcheck source=../utils/logging.sh
source "$(dirname "$0")/../utils/logging.sh"

cpu_optimization_main() {
    info "Starting CPU optimization module"
    
    # Set CPU governor for performance
    set_cpu_governor
    
    # Configure CPU frequency scaling
    configure_cpu_frequency
    
    # Set CPU affinity optimizations
    configure_cpu_affinity
    
    # Configure NUMA if available
    configure_numa_policy
    
    info "CPU optimization module completed"
}

set_cpu_governor() {
    if [[ -f /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor ]]; then
        info "Setting CPU governor to performance"
        echo "performance" | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor >/dev/null 2>&1 || true
    fi
}

configure_cpu_frequency() {
    if [[ -f "$max_freq_file" ]]; then
        local max_freq
        max_freq=$(cat "$max_freq_file")
        info "Setting CPU frequency to maximum: ${max_freq}kHz"
        info "Setting CPU frequency to maximum: ${max_freq}kHz"
        echo "$max_freq" | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_max_freq >/dev/null 2>&1 || true
    fi
}

configure_cpu_affinity() {
    # Configure process scheduler for performance
    echo 0 > /proc/sys/kernel/sched_autogroup_enabled 2>/dev/null || true
    echo 1 > /proc/sys/kernel/sched_tunable_scaling 2>/dev/null || true
}

configure_numa_policy() {
    if command -v numactl &> /dev/null; then
        info "Configuring NUMA policy for performance"
        export MALLOC_ARENA_MAX="${CPU_MALLOC_ARENA_MAX:-4}"
    fi
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    cpu_optimization_main "$@"
fi
