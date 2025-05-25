#!/bin/bash
# Performance Validation Core
# Main validation orchestrator for performance testing

set -euo pipefail

source "$(dirname "$0")/../orchestrator/utils/logging.sh"

validation_main() {
    info "Starting performance validation suite"
    
    local validation_start_time=$(date +%s)
    local tests_dir="$(dirname "$0")/tests"
    local reports_dir="$(dirname "$0")/reports"
    
    # Create reports directory
    mkdir -p "$reports_dir"
    
    # Run validation tests
    run_cpu_validation_tests
    run_memory_validation_tests
    run_io_validation_tests
    run_python_validation_tests
    
    local validation_end_time=$(date +%s)
    local validation_duration=$((validation_end_time - validation_start_time))
    
    # Generate final report
    generate_validation_report "$validation_duration"
    
    info "Performance validation completed in ${validation_duration}s"
}

run_cpu_validation_tests() {
    info "Running CPU validation tests"
    if [[ -x "$(dirname "$0")/tests/cpu-tests.sh" ]]; then
        bash "$(dirname "$0")/tests/cpu-tests.sh"
    fi
}

run_memory_validation_tests() {
    info "Running memory validation tests"
    if [[ -x "$(dirname "$0")/tests/memory-tests.sh" ]]; then
        bash "$(dirname "$0")/tests/memory-tests.sh"
    fi
}

run_io_validation_tests() {
    info "Running I/O validation tests"
    if [[ -x "$(dirname "$0")/tests/io-tests.sh" ]]; then
        bash "$(dirname "$0")/tests/io-tests.sh"
    fi
}

run_python_validation_tests() {
    info "Running Python validation tests"
    if [[ -x "$(dirname "$0")/tests/python-tests.sh" ]]; then
        bash "$(dirname "$0")/tests/python-tests.sh"
    fi
}

generate_validation_report() {
    local duration="$1"
    local report_file="$(dirname "$0")/reports/validation-$(date +%Y%m%d-%H%M%S).json"
    
    cat > "$report_file" << EOF
{
    "timestamp": "$(date -Iseconds)",
    "duration_seconds": $duration,
    "system_info": {
        "cpu_cores": "$(nproc)",
        "memory_gb": "$(free -g | awk 'NR==2{print $2}')",
        "python_version": "$(python3 --version | cut -d' ' -f2)"
    },
    "validation_status": "completed"
}
EOF
    
    info "Validation report generated: $report_file"
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    validation_main "$@"
fi
