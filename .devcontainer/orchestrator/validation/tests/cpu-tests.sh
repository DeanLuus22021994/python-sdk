#!/bin/bash
# CPU Performance Tests
# Validates CPU optimization effectiveness

set -euo pipefail

source "$(dirname "$0")/../../orchestrator/utils/logging.sh"

cpu_tests_main() {
    info "Running CPU performance tests"
    
    test_cpu_governor
    test_cpu_frequency
    test_cpu_load_performance
    
    info "CPU tests completed"
}

test_cpu_governor() {
    info "Testing CPU governor configuration"
    
    local governor_file="/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor"
    if [[ -f "$governor_file" ]]; then
        local current_governor
        current_governor=$(cat "$governor_file")
        if [[ "$current_governor" == "performance" ]]; then
            info "✓ CPU governor set to performance mode"
        else
            warn "⚠ CPU governor is $current_governor (expected: performance)"
        fi
    else
        warn "⚠ CPU governor file not accessible"
    fi
}

test_cpu_frequency() {
    info "Testing CPU frequency scaling"
    
    local freq_file="/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq"
    if [[ -f "$freq_file" ]]; then
        local current_freq
        current_freq=$(cat "$freq_file")
        local max_freq
        max_freq=$(cat "/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq" 2>/dev/null || echo "0")
        
        if [[ $current_freq -ge $((max_freq * 80 / 100)) ]]; then
            info "✓ CPU frequency optimized: ${current_freq}kHz"
        else
            warn "⚠ CPU frequency may not be optimized: ${current_freq}kHz"
        fi
    fi
}

test_cpu_load_performance() {
    info "Testing CPU load performance"
    
    # Simple CPU benchmark
    local start_time
    start_time=$(date +%s.%N)
    python3 -c "
import math
result = sum(math.sqrt(i) for i in range(100000))
" 2>/dev/null || true
    local end_time
    end_time=$(date +%s.%N)
    
    local duration
    duration=$(echo "$end_time - $start_time" | bc)
    info "CPU benchmark completed in ${duration}s"
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    cpu_tests_main "$@"
fi
