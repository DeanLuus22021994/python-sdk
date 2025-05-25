#!/bin/bash
# I/O Performance Optimizer
# Optimizes storage and network I/O for maximum throughput

set -euo pipefail

optimize_block_devices() {
    echo "Optimizing block device settings..."
    
    for device in /sys/block/*/queue; do
        if [[ -d "$device" ]]; then
            # Set scheduler to mq-deadline for SSDs or none for NVMe
            if [[ -f "$device/scheduler" ]]; then
                echo mq-deadline > "$device/scheduler" 2>/dev/null || true
            fi
            
            # Optimize read-ahead for sequential workloads
            if [[ -f "$device/read_ahead_kb" ]]; then
                echo 1024 > "$device/read_ahead_kb" 2>/dev/null || true
            fi
            
            # Disable NCQ depth throttling
            if [[ -f "$device/nr_requests" ]]; then
                echo 1024 > "$device/nr_requests" 2>/dev/null || true
            fi
        fi
    done
}

optimize_network() {
    echo "Optimizing network settings..."
    
    # Increase network buffer sizes
    echo 134217728 > /proc/sys/net/core/rmem_max 2>/dev/null || true
    echo 134217728 > /proc/sys/net/core/wmem_max 2>/dev/null || true
    echo 134217728 > /proc/sys/net/core/rmem_default 2>/dev/null || true
    echo 134217728 > /proc/sys/net/core/wmem_default 2>/dev/null || true
    
    # Optimize TCP settings
    echo bbr > /proc/sys/net/ipv4/tcp_congestion_control 2>/dev/null || true
    echo 1 > /proc/sys/net/ipv4/tcp_window_scaling 2>/dev/null || true
    echo 5000 > /proc/sys/net/core/netdev_max_backlog 2>/dev/null || true
}

optimize_filesystem() {
    echo "Optimizing filesystem settings..."
    
    # Mount tmpfs with optimal settings if not already mounted
    if ! mountpoint -q /tmp; then
        mount -t tmpfs -o size=8G,noatime,mode=1777 tmpfs /tmp 2>/dev/null || true
    fi
    
    # Set optimal mount options for existing filesystems
    mount -o remount,noatime,nodiratime / 2>/dev/null || true
}

main() {
    echo "=== I/O Performance Optimization ==="
    
    if [[ $EUID -ne 0 ]]; then
        echo "Warning: Running without root privileges, some optimizations may not apply"
    fi
    
    optimize_block_devices
    optimize_network
    optimize_filesystem
    
    echo "I/O performance optimization completed"
}

main "$@"
