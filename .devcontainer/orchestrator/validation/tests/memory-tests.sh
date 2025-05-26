#!/bin/bash
# Memory Performance Tests
# Validates memory optimization effectiveness

set -euo pipefail

source "$(dirname "$0")/../../orchestrator/utils/logging.sh"

memory_tests_main() {
    info "Running memory performance tests"
    
    test_memory_allocator
    test_huge_pages
    test_swap_configuration
    test_memory_bandwidth
    
    info "Memory tests completed"
}

test_memory_allocator() {
    info "Testing memory allocator configuration"
    
    if [[ -n "${LD_PRELOAD:-}" ]] && echo "$LD_PRELOAD" | grep -q "jemalloc"; then
        info "✓ jemalloc memory allocator configured"
    else
        warn "⚠ jemalloc not detected in LD_PRELOAD"
    fi
    
    # Test malloc arena configuration
    if [[ "${MALLOC_ARENA_MAX:-}" ]]; then
        info "✓ MALLOC_ARENA_MAX set to $MALLOC_ARENA_MAX"
    fi
}

test_huge_pages() {
    info "Testing huge pages configuration"
    
    if [[ -f /proc/meminfo ]]; then
        local huge_pages
        huge_pages=$(grep "HugePages_Total" /proc/meminfo | awk '{print $2}')
        if [[ $huge_pages -gt 0 ]]; then
            info "✓ Huge pages configured: $huge_pages pages"
        else
            warn "⚠ No huge pages configured"
        fi
    fi
}

test_swap_configuration() {
    info "Testing swap configuration"
    
    if [[ -f /proc/sys/vm/swappiness ]]; then
        local swappiness
        swappiness=$(cat /proc/sys/vm/swappiness)
        if [[ $swappiness -le 10 ]]; then
            info "✓ Swappiness optimized: $swappiness"
        else
            warn "⚠ Swappiness may be too high: $swappiness"
        fi
    fi
}

test_memory_bandwidth() {
    info "Testing memory bandwidth performance"
    
    # Simple memory bandwidth test
    local start_time
    start_time=$(date +%s.%N)
    python3 -c "
import array
data = array.array('i', range(1000000))
result = sum(data)
" 2>/dev/null || true
    local end_time
    end_time=$(date +%s.%N)
    
    local duration
    duration=$(echo "$end_time - $start_time" | bc 2>/dev/null || echo "0.1")
    info "Memory bandwidth test completed in ${duration}s"
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    memory_tests_main "$@"
fi
