#!/bin/bash
# CPU Performance Optimization Module
# Handles CPU governor, frequency scaling, and threading optimization

# Source common utilities
source "$(dirname "${BASH_SOURCE[0]}")/../utils/common.sh"

# Initialize
init_common

# CPU governor optimization
optimize_cpu_governor() {
    log_step "Optimizing CPU governor settings..."
    
    local governor="${CPU_GOVERNOR:-performance}"
    local available_governors
    
    # Check available governors
    if [[ -f /sys/devices/system/cpu/cpu0/cpufreq/scaling_available_governors ]]; then
        available_governors=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_available_governors)
        log_debug "Available governors: $available_governors"
        
        if echo "$available_governors" | grep -q "$governor"; then
            log_debug "Setting CPU governor to: $governor"
            echo "$governor" | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor > /dev/null
            log_success "CPU governor set to: $governor"
        else
            log_warning "Governor '$governor' not available, using default"
        fi
    else
        log_warning "CPU frequency scaling not available"
    fi
}

# CPU frequency optimization
optimize_cpu_frequency() {
    log_step "Optimizing CPU frequency settings..."
    
    # Set minimum frequency to maximum for performance
    if [[ -f /sys/devices/system/cpu/cpu0/cpufreq/scaling_min_freq ]] && 
       [[ -f /sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq ]]; then
        
        local max_freq=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq)
        
        for cpu in /sys/devices/system/cpu/cpu*/cpufreq/scaling_min_freq; do
            echo "$max_freq" > "$cpu" 2>/dev/null || true
        done
        
        log_success "CPU frequency optimization completed"
    else
        log_warning "CPU frequency control not available"
    fi
}

# CPU affinity optimization
optimize_cpu_affinity() {
    log_step "Optimizing CPU affinity for performance..."
    
    local cpu_count=$(nproc)
    local irq_cpus=$((cpu_count / 2))
    
    # Move IRQs to first half of CPUs for better cache locality
    if [[ -d /proc/irq ]]; then
        for irq in /proc/irq/*/smp_affinity; do
            if [[ -w "$irq" ]]; then
                printf "%x" $((2**irq_cpus - 1)) > "$irq" 2>/dev/null || true
            fi
        done
        log_success "IRQ affinity optimized"
    fi
}

# NUMA optimization
optimize_numa() {
    log_step "Optimizing NUMA settings..."
    
    if command_exists numactl; then
        local numa_nodes=$(numactl --hardware | grep "available:" | awk '{print $2}')
        
        if [[ $numa_nodes -gt 1 ]]; then
            log_debug "NUMA nodes detected: $numa_nodes"
            
            # Set NUMA policy for better memory locality
            echo 1 > /proc/sys/kernel/numa_balancing 2>/dev/null || true
            
            log_success "NUMA optimization completed for $numa_nodes nodes"
        else
            log_debug "Single NUMA node system, skipping NUMA optimization"
        fi
    else
        log_debug "numactl not available, skipping NUMA optimization"
    fi
}

# CPU cache optimization
optimize_cpu_cache() {
    log_step "Optimizing CPU cache settings..."
    
    # Get cache information
    local l1_cache_size=$(getconf LEVEL1_DCACHE_SIZE 2>/dev/null || echo "32768")
    local l2_cache_size=$(getconf LEVEL2_CACHE_SIZE 2>/dev/null || echo "262144")
    local l3_cache_size=$(getconf LEVEL3_CACHE_SIZE 2>/dev/null || echo "8388608")
    
    log_debug "L1 cache: $((l1_cache_size / 1024))KB, L2 cache: $((l2_cache_size / 1024))KB, L3 cache: $((l3_cache_size / 1024))KB"
    
    # Export cache sizes for applications
    export L1_CACHE_SIZE="$l1_cache_size"
    export L2_CACHE_SIZE="$l2_cache_size"
    export L3_CACHE_SIZE="$l3_cache_size"
    
    log_success "CPU cache information exported"
}

# Threading optimization
optimize_threading() {
    log_step "Optimizing threading settings..."
    
    local cpu_count=$(nproc)
    
    # Set optimal thread counts based on CPU architecture
    export OMP_NUM_THREADS="${OMP_NUM_THREADS:-$cpu_count}"
    export MKL_NUM_THREADS="${MKL_NUM_THREADS:-$cpu_count}"
    export OPENBLAS_NUM_THREADS="${OPENBLAS_NUM_THREADS:-$cpu_count}"
    export VECLIB_MAXIMUM_THREADS="${VECLIB_MAXIMUM_THREADS:-$cpu_count}"
    export NUMEXPR_NUM_THREADS="${NUMEXPR_NUM_THREADS:-$cpu_count}"
    
    # Set thread affinity
    export OMP_PROC_BIND=true
    export OMP_PLACES=cores
    export OMP_SCHEDULE=static
    
    log_success "Threading optimization completed for $cpu_count cores"
}

# CPU power management
optimize_power_management() {
    log_step "Optimizing CPU power management..."
    
    # Disable CPU idle states for maximum performance
    if [[ -f /sys/devices/system/cpu/cpu0/cpuidle/state1/disable ]]; then
        for state in /sys/devices/system/cpu/cpu*/cpuidle/state*/disable; do
            echo 1 > "$state" 2>/dev/null || true
        done
        log_success "CPU idle states disabled for maximum performance"
    fi
    
    # Set energy performance preference
    if [[ -f /sys/devices/system/cpu/cpu0/cpufreq/energy_performance_preference ]]; then
        for pref in /sys/devices/system/cpu/cpu*/cpufreq/energy_performance_preference; do
            echo "performance" > "$pref" 2>/dev/null || true
        done
        log_success "Energy performance preference set to performance"
    fi
}

# CPU microcode optimization
check_microcode() {
    log_step "Checking CPU microcode..."
    
    if [[ -f /proc/cpuinfo ]]; then
        local microcode=$(grep microcode /proc/cpuinfo | head -1 | awk '{print $3}')
        if [[ -n "$microcode" ]]; then
            log_success "CPU microcode version: $microcode"
        else
            log_warning "CPU microcode information not available"
        fi
    fi
}

# Main CPU optimization function
optimize_cpu() {
    log_step "Starting CPU optimization..."
    
    check_root
    check_system_requirements
    
    optimize_cpu_governor
    optimize_cpu_frequency
    optimize_cpu_affinity
    optimize_numa
    optimize_cpu_cache
    optimize_threading
    optimize_power_management
    check_microcode
    
    log_success "CPU optimization completed successfully"
}

# Execute if script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    optimize_cpu "$@"
fi
