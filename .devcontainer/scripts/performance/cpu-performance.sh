#!/bin/bash
# CPU Performance Optimizer
# Optimizes CPU performance settings for maximum throughput

set -euo pipefail

optimize_cpu_governor() {
    echo "Setting CPU governor to performance mode..."
    for cpu in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
        if [[ -f "$cpu" ]]; then
            echo performance | tee "$cpu" > /dev/null 2>&1 || true
        fi
    done
}

optimize_cpu_scaling() {
    echo "Optimizing CPU scaling settings..."
    for cpu in /sys/devices/system/cpu/cpu*/cpufreq/scaling_max_freq; do
        if [[ -f "$cpu" ]]; then
            cat "${cpu%/*}/cpuinfo_max_freq" | tee "$cpu" > /dev/null 2>&1 || true
        fi
    done
}

optimize_irq_affinity() {
    echo "Optimizing IRQ affinity for better CPU distribution..."
    local cpu_count
    cpu_count=$(nproc)
    local cpu_mask
    cpu_mask=$((2**cpu_count - 1))
    
    for irq in /proc/irq/*/smp_affinity; do
        if [[ -f "$irq" ]]; then
            printf "%x" $cpu_mask | tee "$irq" > /dev/null 2>&1 || true
        fi
    done
}

disable_cpu_idle() {
    echo "Disabling CPU idle states for minimum latency..."
    for idle in /sys/devices/system/cpu/cpu*/cpuidle/state*/disable; do
        if [[ -f "$idle" ]]; then
            echo 1 | tee "$idle" > /dev/null 2>&1 || true
        fi
    done
}

main() {
    echo "=== CPU Performance Optimization ==="
    
    if [[ $EUID -ne 0 ]]; then
        echo "Warning: Running without root privileges, some optimizations may not apply"
    fi
    
    optimize_cpu_governor
    optimize_cpu_scaling
    optimize_irq_affinity
    disable_cpu_idle
    
    echo "CPU performance optimization completed"
}

main "$@"
