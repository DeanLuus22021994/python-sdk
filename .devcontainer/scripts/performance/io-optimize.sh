#!/bin/bash
# I/O Performance Optimization Module
# Handles storage, filesystem, and I/O scheduler optimization

# Source common utilities
source "$(dirname "${BASH_SOURCE[0]}")/../utils/common.sh"

# Initialize
init_common

# I/O scheduler optimization
optimize_io_scheduler() {
    log_step "Optimizing I/O scheduler..."
    
    # Get all block devices
    local block_devices=$(lsblk -dn -o NAME | grep -E '^[a-z]+$')
    
    for device in $block_devices; do
        local scheduler_path="/sys/block/$device/queue/scheduler"
        
        if [[ -f "$scheduler_path" ]]; then
            local available_schedulers=$(cat "$scheduler_path")
            log_debug "Device: $device, Available schedulers: $available_schedulers"
            
            # Choose optimal scheduler based on device type
            local optimal_scheduler=""
            
            # Check if it's an SSD/NVMe
            if [[ -f "/sys/block/$device/queue/rotational" ]]; then
                local is_rotational=$(cat "/sys/block/$device/queue/rotational")
                
                if [[ "$is_rotational" == "0" ]]; then
                    # SSD/NVMe - use mq-deadline or none
                    if echo "$available_schedulers" | grep -q "none"; then
                        optimal_scheduler="none"
                    elif echo "$available_schedulers" | grep -q "mq-deadline"; then
                        optimal_scheduler="mq-deadline"
                    fi
                    log_debug "Device $device is SSD/NVMe"
                else
                    # HDD - use mq-deadline or bfq
                    if echo "$available_schedulers" | grep -q "bfq"; then
                        optimal_scheduler="bfq"
                    elif echo "$available_schedulers" | grep -q "mq-deadline"; then
                        optimal_scheduler="mq-deadline"
                    fi
                    log_debug "Device $device is HDD"
                fi
            fi
            
            if [[ -n "$optimal_scheduler" ]]; then
                echo "$optimal_scheduler" > "$scheduler_path"
                log_success "Set I/O scheduler for $device to: $optimal_scheduler"
            else
                log_warning "No optimal scheduler found for $device"
            fi
        fi
    done
}

# Queue depth optimization
optimize_queue_depth() {
    log_step "Optimizing I/O queue depth..."
    
    local block_devices=$(lsblk -dn -o NAME | grep -E '^[a-z]+$')
    
    for device in $block_devices; do
        # Set queue depth for better performance
        local queue_depth_path="/sys/block/$device/queue/nr_requests"
        
        if [[ -f "$queue_depth_path" ]]; then
            # Check if it's SSD/NVMe for higher queue depth
            local is_rotational=$(cat "/sys/block/$device/queue/rotational" 2>/dev/null || echo "1")
            
            if [[ "$is_rotational" == "0" ]]; then
                # SSD/NVMe - higher queue depth
                echo 1024 > "$queue_depth_path"
                log_success "Set queue depth for SSD $device to: 1024"
            else
                # HDD - moderate queue depth
                echo 256 > "$queue_depth_path"
                log_success "Set queue depth for HDD $device to: 256"
            fi
        fi
        
        # Set read-ahead for better sequential performance
        local readahead_path="/sys/block/$device/queue/read_ahead_kb"
        if [[ -f "$readahead_path" ]]; then
            echo 4096 > "$readahead_path"
            log_debug "Set read-ahead for $device to: 4096KB"
        fi
    done
}

# Filesystem optimization
optimize_filesystem() {
    log_step "Optimizing filesystem settings..."
    
    # Mount options optimization for different filesystems
    local mount_points=$(mount | grep -E '^/dev/' | awk '{print $3}')
    
    for mount_point in $mount_points; do
        local filesystem=$(mount | grep " $mount_point " | awk '{print $5}')
        log_debug "Mount point: $mount_point, Filesystem: $filesystem"
        
        case "$filesystem" in
            ext4)
                # Optimize ext4 parameters
                if command_exists tune2fs; then
                    local device=$(mount | grep " $mount_point " | awk '{print $1}')
                    
                    # Set commit interval for better performance
                    tune2fs -o journal_data_writeback "$device" 2>/dev/null || true
                    
                    log_debug "Optimized ext4 filesystem on $device"
                fi
                ;;
            xfs)
                # XFS is already well-optimized by default
                log_debug "XFS filesystem detected on $mount_point"
                ;;
            btrfs)
                # Optimize btrfs if needed
                log_debug "BTRFS filesystem detected on $mount_point"
                ;;
        esac
    done
    
    log_success "Filesystem optimization completed"
}

# Disk I/O optimization
optimize_disk_io() {
    log_step "Optimizing disk I/O settings..."
    
    # Set global I/O settings
    local block_devices=$(lsblk -dn -o NAME | grep -E '^[a-z]+$')
    
    for device in $block_devices; do
        local device_path="/sys/block/$device/queue"
        
        # Optimize I/O merge settings
        if [[ -f "$device_path/nomerges" ]]; then
            echo 0 > "$device_path/nomerges"  # Enable merges
        fi
        
        # Set optimal I/O size
        if [[ -f "$device_path/max_sectors_kb" ]]; then
            echo 1024 > "$device_path/max_sectors_kb"
        fi
        
        # Enable NCQ for SATA drives
        if [[ -f "$device_path/iosched/low_latency" ]]; then
            echo 0 > "$device_path/iosched/low_latency"
        fi
        
        # Optimize for throughput
        if [[ -f "$device_path/iosched/slice_idle" ]]; then
            echo 0 > "$device_path/iosched/slice_idle"
        fi
        
        log_debug "Optimized I/O settings for device: $device"
    done
    
    log_success "Disk I/O optimization completed"
}

# Network I/O optimization
optimize_network_io() {
    log_step "Optimizing network I/O settings..."
    
    # TCP buffer optimization
    echo 134217728 > /proc/sys/net/core/rmem_max
    echo 134217728 > /proc/sys/net/core/wmem_max
    echo "4096 16384 134217728" > /proc/sys/net/ipv4/tcp_rmem
    echo "4096 65536 134217728" > /proc/sys/net/ipv4/tcp_wmem
    
    # Network queue optimization
    echo 5000 > /proc/sys/net/core/netdev_max_backlog
    echo 1000 > /proc/sys/net/core/netdev_budget
    
    # TCP congestion control
    if grep -q bbr /proc/sys/net/ipv4/tcp_available_congestion_control; then
        echo bbr > /proc/sys/net/ipv4/tcp_congestion_control
        log_success "TCP congestion control set to BBR"
    else
        echo cubic > /proc/sys/net/ipv4/tcp_congestion_control
        log_success "TCP congestion control set to CUBIC"
    fi
    
    # TCP optimization
    echo 1 > /proc/sys/net/ipv4/tcp_window_scaling
    echo 1 > /proc/sys/net/ipv4/tcp_timestamps
    echo 1 > /proc/sys/net/ipv4/tcp_sack
    echo 0 > /proc/sys/net/ipv4/tcp_slow_start_after_idle
    
    log_success "Network I/O optimization completed"
}

# Storage cache optimization
optimize_storage_cache() {
    log_step "Optimizing storage cache..."
    
    # Create dedicated cache directories with optimal settings
    local cache_dirs=(
        "$CACHE_ROOT"
        "${UV_CACHE_DIR}"
        "${PIP_CACHE_DIR}"
        "${NUMBA_CACHE_DIR}"
        "${CUDA_CACHE_PATH}"
        "${RUST_CACHE_DIR}"
    )
    
    for cache_dir in "${cache_dirs[@]}"; do
        if [[ -n "$cache_dir" ]]; then
            create_dir "$cache_dir" 755 root:root
            
            # Set optimal directory attributes if on ext4
            if command_exists chattr && mount | grep "$(df "$cache_dir" | tail -1 | awk '{print $1}')" | grep -q ext4; then
                chattr +F "$cache_dir" 2>/dev/null || true  # Set directory for fast access
                log_debug "Set fast access attribute for: $cache_dir"
            fi
        fi
    done
    
    # Mount tmpfs for high-speed temporary storage
    if ! mount | grep -q "tmpfs on ${TMPDIR:-/tmp}"; then
        mount -t tmpfs -o size=${TMPFS_SIZE:-8G},mode=1777 tmpfs "${TMPDIR:-/tmp}"
        log_success "Mounted tmpfs for high-speed temporary storage: ${TMPFS_SIZE:-8G}"
    fi
    
    log_success "Storage cache optimization completed"
}

# I/O priority optimization
optimize_io_priority() {
    log_step "Optimizing I/O priority settings..."
    
    # Set I/O nice levels for current processes
    if command_exists ionice; then
        # Set current shell to best-effort class with high priority
        ionice -c 1 -n 4 -p $$ 2>/dev/null || true
        log_debug "Set I/O priority for current process"
    fi
    
    # Optimize kernel I/O priority
    if [[ -f /proc/sys/kernel/pid_max ]]; then
        local current_pid_max=$(cat /proc/sys/kernel/pid_max)
        if [[ $current_pid_max -lt 4194304 ]]; then
            echo 4194304 > /proc/sys/kernel/pid_max
            log_success "Increased PID max to 4194304"
        fi
    fi
    
    log_success "I/O priority optimization completed"
}

# Monitoring setup for I/O
setup_io_monitoring() {
    log_step "Setting up I/O monitoring..."
    
    # Create I/O monitoring script
    local monitor_script="/opt/mcp-cache/io-monitor.sh"
    cat > "$monitor_script" << 'EOF'
#!/bin/bash
# I/O monitoring script

while true; do
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Monitor disk I/O
    if command -v iostat >/dev/null 2>&1; then
        echo "[$timestamp] Disk I/O Statistics:"
        iostat -x 1 1 | tail -n +4
    fi
    
    # Monitor network I/O
    if [[ -f /proc/net/dev ]]; then
        echo "[$timestamp] Network I/O Statistics:"
        cat /proc/net/dev | grep -E 'eth|ens|wl' | head -3
    fi
    
    echo "----------------------------------------"
    sleep 60
done
EOF
    
    chmod +x "$monitor_script"
    log_success "I/O monitoring script created: $monitor_script"
}

# Main I/O optimization function
optimize_io() {
    log_step "Starting I/O optimization..."
    
    check_root
    check_system_requirements
    
    optimize_io_scheduler
    optimize_queue_depth
    optimize_filesystem
    optimize_disk_io
    optimize_network_io
    optimize_storage_cache
    optimize_io_priority
    setup_io_monitoring
    
    log_success "I/O optimization completed successfully"
}

# Execute if script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    optimize_io "$@"
fi
