#!/bin/bash
# I/O Optimization Module
# Handles I/O and storage performance optimizations

set -euo pipefail

source "$(dirname "$0")/../utils/logging.sh"

io_optimization_main() {
    info "Starting I/O optimization module"
    
    # Configure I/O scheduler
    configure_io_scheduler
    
    # Set up filesystem optimizations
    configure_filesystem_opts
    
    # Configure network I/O
    configure_network_io
    
    # Set up tmpfs mounts
    configure_tmpfs_mounts
    
    info "I/O optimization module completed"
}

configure_io_scheduler() {
    local scheduler="${IO_SCHEDULER:-mq-deadline}"
    
    for device in /sys/block/*/queue/scheduler; do
        if [[ -f "$device" ]] && grep -q "$scheduler" "$device"; then
            echo "$scheduler" > "$device" 2>/dev/null || true
            info "Set I/O scheduler to $scheduler for $(dirname "$device" | cut -d'/' -f4)"
        fi
    done
}

configure_filesystem_opts() {
    # Configure filesystem read-ahead
    local readahead="${IO_READAHEAD:-8192}"
    
    for device in /sys/block/*/queue/read_ahead_kb; do
        if [[ -f "$device" ]]; then
            echo "$readahead" > "$device" 2>/dev/null || true
        fi
    done
    
    # Configure queue depth
    local queue_depth="${IO_QUEUE_DEPTH:-128}"
    
    for device in /sys/block/*/queue/nr_requests; do
        if [[ -f "$device" ]]; then
            echo "$queue_depth" > "$device" 2>/dev/null || true
        fi
    done
}

configure_network_io() {
    # Network buffer sizes
    echo "${NETWORK_RMEM_MAX:-134217728}" > /proc/sys/net/core/rmem_max 2>/dev/null || true
    echo "${NETWORK_WMEM_MAX:-134217728}" > /proc/sys/net/core/wmem_max 2>/dev/null || true
    echo "${NETWORK_NETDEV_MAX_BACKLOG:-5000}" > /proc/sys/net/core/netdev_max_backlog 2>/dev/null || true
}

configure_tmpfs_mounts() {
    # Ensure performance tmpfs mounts exist
    local tmpfs_size="${TMPFS_SIZE:-8G}"
    
    if ! mountpoint -q /tmp; then
        mount -t tmpfs -o size="$tmpfs_size",mode=1777 tmpfs /tmp 2>/dev/null || true
        info "Configured /tmp as tmpfs with size $tmpfs_size"
    fi
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    io_optimization_main "$@"
fi
