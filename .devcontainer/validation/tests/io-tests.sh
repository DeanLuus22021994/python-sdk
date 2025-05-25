#!/bin/bash
# I/O Performance Tests  
# Validates I/O optimization effectiveness

set -euo pipefail

source "$(dirname "$0")/../../orchestrator/utils/logging.sh"

io_tests_main() {
    info "Running I/O performance tests"
    
    test_io_scheduler
    test_filesystem_performance
    test_network_configuration
    test_tmpfs_mounts
    
    info "I/O tests completed"
}

test_io_scheduler() {
    info "Testing I/O scheduler configuration"
    
    for device in /sys/block/*/queue/scheduler; do
        if [[ -f "$device" ]]; then
            local current_scheduler=$(cat "$device" | grep -o '\[.*\]' | tr -d '[]')
            local device_name=$(echo "$device" | cut -d'/' -f4)
            info "I/O scheduler for $device_name: $current_scheduler"
        fi
    done
}

test_filesystem_performance() {
    info "Testing filesystem performance"
    
    # Disk I/O benchmark
    local test_file="/tmp/io_test_$$"
    local start_time=$(date +%s.%N)
    
    dd if=/dev/zero of="$test_file" bs=1M count=100 2>/dev/null || true
    sync
    
    local end_time=$(date +%s.%N)
    local duration=$(echo "$end_time - $start_time" | bc 2>/dev/null || echo "1")
    local throughput=$(echo "100 / $duration" | bc -l 2>/dev/null || echo "0")
    
    rm -f "$test_file"
    info "Filesystem write throughput: ${throughput} MB/s"
}

test_network_configuration() {
    info "Testing network configuration"
    
    # Check network buffer sizes
    local rmem_max=$(cat /proc/sys/net/core/rmem_max 2>/dev/null || echo "0")
    local wmem_max=$(cat /proc/sys/net/core/wmem_max 2>/dev/null || echo "0")
    
    if [[ $rmem_max -ge 134217728 ]]; then
        info "✓ Network read buffer optimized: $rmem_max bytes"
    fi
    
    if [[ $wmem_max -ge 134217728 ]]; then
        info "✓ Network write buffer optimized: $wmem_max bytes"
    fi
}

test_tmpfs_mounts() {
    info "Testing tmpfs mount performance"
    
    if mountpoint -q /tmp; then
        local mount_info=$(mount | grep "on /tmp" | head -1)
        if echo "$mount_info" | grep -q "tmpfs"; then
            info "✓ /tmp mounted as tmpfs for performance"
        else
            warn "⚠ /tmp not mounted as tmpfs"
        fi
    fi
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    io_tests_main "$@"
fi
