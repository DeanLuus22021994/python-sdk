#!/bin/bash
# Memory Performance Optimizer  
# Optimizes memory settings for maximum performance and low latency

set -euo pipefail

optimize_memory_settings() {
    echo "Optimizing memory performance settings..."
    
    # Optimize swappiness for performance
    echo 1 > /proc/sys/vm/swappiness 2>/dev/null || true
    
    # Optimize dirty memory settings for better write performance
    echo 15 > /proc/sys/vm/dirty_ratio 2>/dev/null || true
    echo 5 > /proc/sys/vm/dirty_background_ratio 2>/dev/null || true
    
    # Reduce cache pressure for better memory utilization
    echo 50 > /proc/sys/vm/vfs_cache_pressure 2>/dev/null || true
    
    # Optimize memory overcommit for performance
    echo 1 > /proc/sys/vm/overcommit_memory 2>/dev/null || true
    echo 100 > /proc/sys/vm/overcommit_ratio 2>/dev/null || true
}

configure_huge_pages() {
    echo "Configuring transparent huge pages..."
    
    # Enable transparent huge pages for better memory performance
    echo always > /sys/kernel/mm/transparent_hugepage/enabled 2>/dev/null || true
    echo always > /sys/kernel/mm/transparent_hugepage/defrag 2>/dev/null || true
}

optimize_numa() {
    echo "Optimizing NUMA settings..."
    
    # Disable zone reclaim for better NUMA performance
    echo 0 > /proc/sys/vm/zone_reclaim_mode 2>/dev/null || true
    
    # Optimize NUMA balancing
    echo 1 > /proc/sys/kernel/numa_balancing 2>/dev/null || true
}

main() {
    echo "=== Memory Performance Optimization ==="
    
    if [[ $EUID -ne 0 ]]; then
        echo "Warning: Running without root privileges, some optimizations may not apply"
    fi
    
    optimize_memory_settings
    configure_huge_pages
    optimize_numa
    
    echo "Memory performance optimization completed"
}

main "$@"
