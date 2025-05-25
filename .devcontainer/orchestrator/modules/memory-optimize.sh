#!/bin/bash
# Memory Optimization Module
# Handles memory-specific performance optimizations

set -euo pipefail

source "$(dirname "$0")/../utils/logging.sh"

memory_optimization_main() {
    info "Starting memory optimization module"
    
    # Configure memory allocator
    configure_memory_allocator
    
    # Set up huge pages
    configure_huge_pages
    
    # Configure swap settings
    configure_swap_settings
    
    # Set memory bandwidth optimizations
    configure_memory_bandwidth
    
    info "Memory optimization module completed"
}

configure_memory_allocator() {
    # Use jemalloc for better memory performance
    if [[ -f /usr/lib/x86_64-linux-gnu/libjemalloc.so.2 ]]; then
        export LD_PRELOAD="/usr/lib/x86_64-linux-gnu/libjemalloc.so.2:$LD_PRELOAD"
        info "jemalloc memory allocator configured"
    fi
    
    # Set memory allocation parameters
    export MALLOC_ARENA_MAX="${MEMORY_MALLOC_ARENA_MAX:-4}"
    export MALLOC_TRIM_THRESHOLD_="${MEMORY_MALLOC_TRIM_THRESHOLD:-131072}"
}

configure_huge_pages() {
    local huge_pages="${MEMORY_HUGE_PAGES:-1024}"
    
    if [[ -f /proc/sys/vm/nr_hugepages ]]; then
        echo "$huge_pages" > /proc/sys/vm/nr_hugepages 2>/dev/null || true
        info "Configured $huge_pages huge pages"
    fi
    
    # Configure transparent huge pages
    if [[ -f /sys/kernel/mm/transparent_hugepage/enabled ]]; then
        echo "madvise" > /sys/kernel/mm/transparent_hugepage/enabled 2>/dev/null || true
    fi
}

configure_swap_settings() {
    # Set swappiness for performance
    echo "${MEMORY_SWAPPINESS:-1}" > /proc/sys/vm/swappiness 2>/dev/null || true
    
    # Configure dirty page settings
    echo "${MEMORY_DIRTY_RATIO:-15}" > /proc/sys/vm/dirty_ratio 2>/dev/null || true
    echo "${MEMORY_DIRTY_BACKGROUND_RATIO:-5}" > /proc/sys/vm/dirty_background_ratio 2>/dev/null || true
}

configure_memory_bandwidth() {
    # Configure memory bandwidth settings
    echo "${MEMORY_OVERCOMMIT_MEMORY:-1}" > /proc/sys/vm/overcommit_memory 2>/dev/null || true
    echo "${MEMORY_MAX_MAP_COUNT:-262144}" > /proc/sys/vm/max_map_count 2>/dev/null || true
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    memory_optimization_main "$@"
fi
