#!/bin/bash
# Memory Performance Optimization Module
# Handles memory allocation, swap, and caching optimization

# Source common utilities
source "$(dirname "${BASH_SOURCE[0]}")/../utils/common.sh"

# Initialize
init_common

# Memory allocator optimization
optimize_memory_allocator() {
    log_step "Optimizing memory allocator..."
    
    # Install and configure jemalloc for better memory performance
    if ! dpkg -l | grep -q libjemalloc; then
        install_package "libjemalloc2"
    fi
    
    # Set jemalloc as default allocator
    local jemalloc_path="/usr/lib/x86_64-linux-gnu/libjemalloc.so.2"
    if [[ -f "$jemalloc_path" ]]; then
        export LD_PRELOAD="$jemalloc_path"
        
        # Configure jemalloc for performance
        export MALLOC_CONF="background_thread:true,metadata_thp:auto,dirty_decay_ms:10000,muzzy_decay_ms:10000"
        
        log_success "jemalloc configured as memory allocator"
    else
        log_warning "jemalloc not found, using system default"
    fi
    
    # Set glibc malloc tuning
    export MALLOC_ARENA_MAX="${MALLOC_ARENA_MAX:-4}"
    export MALLOC_TRIM_THRESHOLD_="${MALLOC_TRIM_THRESHOLD_:-131072}"
    export MALLOC_TOP_PAD_="${MALLOC_TOP_PAD_:-131072}"
    export MALLOC_MMAP_THRESHOLD_="${MALLOC_MMAP_THRESHOLD_:-131072}"
    
    log_success "Memory allocator optimization completed"
}

# Swap optimization
optimize_swap() {
    log_step "Optimizing swap settings..."
    
    # Get current swap usage
    local swap_total=$(grep SwapTotal /proc/meminfo | awk '{print $2}')
    local swap_free=$(grep SwapFree /proc/meminfo | awk '{print $2}')
    local swap_used=$((swap_total - swap_free))
    
    if [[ $swap_total -gt 0 ]]; then
        log_debug "Swap total: $((swap_total / 1024))MB, used: $((swap_used / 1024))MB"
        
        # Set swappiness for performance (low swappiness)
        echo 10 > /proc/sys/vm/swappiness
        log_success "Swappiness set to 10 for performance"
        
        # Optimize swap cache pressure
        echo 50 > /proc/sys/vm/vfs_cache_pressure
        log_success "VFS cache pressure set to 50"
    else
        log_debug "No swap configured"
    fi
}

# Memory overcommit optimization
optimize_memory_overcommit() {
    log_step "Optimizing memory overcommit settings..."
    
    # Set memory overcommit mode for performance
    echo 1 > /proc/sys/vm/overcommit_memory
    echo 50 > /proc/sys/vm/overcommit_ratio
    
    log_success "Memory overcommit optimized"
}

# Page cache optimization
optimize_page_cache() {
    log_step "Optimizing page cache settings..."
    
    # Set dirty ratio for better I/O performance
    echo 15 > /proc/sys/vm/dirty_ratio
    echo 5 > /proc/sys/vm/dirty_background_ratio
    
    # Set dirty expire time
    echo 3000 > /proc/sys/vm/dirty_expire_centisecs
    echo 500 > /proc/sys/vm/dirty_writeback_centisecs
    
    log_success "Page cache optimization completed"
}

# Huge pages optimization
optimize_huge_pages() {
    log_step "Optimizing huge pages settings..."
    
    local total_memory_kb=$(grep MemTotal /proc/meminfo | awk '{print $2}')
    local total_memory_gb=$((total_memory_kb / 1024 / 1024))
    
    if [[ $total_memory_gb -ge 8 ]]; then
        # Calculate huge pages (2MB pages, allocate 25% of memory)
        local huge_pages_2mb=$((total_memory_gb * 1024 / 4 / 2))
        
        # Configure 2MB huge pages
        echo "$huge_pages_2mb" > /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages
        
        # Configure 1GB huge pages if available and memory >= 16GB
        if [[ $total_memory_gb -ge 16 ]] && [[ -d /sys/kernel/mm/hugepages/hugepages-1048576kB ]]; then
            local huge_pages_1gb=$((total_memory_gb / 8))
            echo "$huge_pages_1gb" > /sys/kernel/mm/hugepages/hugepages-1048576kB/nr_hugepages
            log_success "Configured $huge_pages_1gb x 1GB huge pages"
        fi
        
        # Set huge page allocation policy
        echo "always" > /sys/kernel/mm/transparent_hugepage/enabled
        echo "always" > /sys/kernel/mm/transparent_hugepage/defrag
        
        log_success "Configured $huge_pages_2mb x 2MB huge pages"
    else
        log_warning "Insufficient memory for huge pages optimization (need >= 8GB)"
    fi
}

# Memory compaction optimization
optimize_memory_compaction() {
    log_step "Optimizing memory compaction..."
    
    # Enable memory compaction for better fragmentation handling
    echo 1 > /proc/sys/vm/compact_memory
    
    # Set compaction proactiveness
    if [[ -f /proc/sys/vm/compaction_proactiveness ]]; then
        echo 20 > /proc/sys/vm/compaction_proactiveness
    fi
    
    log_success "Memory compaction optimization completed"
}

# NUMA memory optimization
optimize_numa_memory() {
    log_step "Optimizing NUMA memory settings..."
    
    if command_exists numactl; then
        local numa_nodes=$(numactl --hardware | grep "available:" | awk '{print $2}')
        
        if [[ $numa_nodes -gt 1 ]]; then
            # Enable NUMA balancing
            echo 1 > /proc/sys/kernel/numa_balancing
            
            # Set NUMA zone reclaim mode
            echo 1 > /proc/sys/vm/zone_reclaim_mode
            
            log_success "NUMA memory optimization completed for $numa_nodes nodes"
        else
            log_debug "Single NUMA node, skipping NUMA memory optimization"
        fi
    else
        log_debug "numactl not available, skipping NUMA memory optimization"
    fi
}

# Memory bandwidth optimization
optimize_memory_bandwidth() {
    log_step "Optimizing memory bandwidth..."
    
    # Get memory information
    local memory_speed=$(dmidecode -t memory 2>/dev/null | grep "Speed:" | head -1 | awk '{print $2}' || echo "unknown")
    log_debug "Memory speed: $memory_speed"
    
    # Set memory access patterns for better bandwidth utilization
    if [[ -f /proc/sys/vm/zone_reclaim_mode ]]; then
        echo 0 > /proc/sys/vm/zone_reclaim_mode
    fi
    
    # Optimize readahead for sequential access
    if [[ -b /dev/sda ]]; then
        blockdev --setra 4096 /dev/sda 2>/dev/null || true
    fi
    
    log_success "Memory bandwidth optimization completed"
}

# Memory monitoring setup
setup_memory_monitoring() {
    log_step "Setting up memory monitoring..."
    
    # Create memory monitoring script
    local monitor_script="/opt/mcp-cache/memory-monitor.sh"
    cat > "$monitor_script" << 'EOF'
#!/bin/bash
# Memory monitoring script

while true; do
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    memory_info=$(free -m | grep "Mem:")
    total=$(echo $memory_info | awk '{print $2}')
    used=$(echo $memory_info | awk '{print $3}')
    free=$(echo $memory_info | awk '{print $4}')
    cached=$(echo $memory_info | awk '{print $6}')
    
    usage_percent=$((used * 100 / total))
    
    echo "[$timestamp] Memory: ${used}MB/${total}MB (${usage_percent}%), Free: ${free}MB, Cached: ${cached}MB"
    
    # Alert if memory usage > 90%
    if [[ $usage_percent -gt 90 ]]; then
        echo "[$timestamp] WARNING: High memory usage detected: ${usage_percent}%"
    fi
    
    sleep 60
done
EOF
    
    chmod +x "$monitor_script"
    log_success "Memory monitoring script created: $monitor_script"
}

# Main memory optimization function
optimize_memory() {
    log_step "Starting memory optimization..."
    
    check_root
    check_system_requirements
    
    optimize_memory_allocator
    optimize_swap
    optimize_memory_overcommit
    optimize_page_cache
    optimize_huge_pages
    optimize_memory_compaction
    optimize_numa_memory
    optimize_memory_bandwidth
    setup_memory_monitoring
    
    # Display final memory configuration
    local total_memory=$(grep MemTotal /proc/meminfo | awk '{print int($2/1024)}')
    local available_memory=$(grep MemAvailable /proc/meminfo | awk '{print int($2/1024)}')
    
    log_success "Memory optimization completed successfully"
    log_success "Total memory: ${total_memory}MB, Available: ${available_memory}MB"
}

# Execute if script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    optimize_memory "$@"
fi
