#!/bin/bash
# Parallel Executor - Executes modules in parallel
# Provides parallel execution mode for orchestrator modules

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../utils/logging.sh"
source "$SCRIPT_DIR/sequential.sh"

execute_modules_parallel() {
    local modules_dir="$1"
    shift
    local modules=("$@")
    
    info "Executing modules in parallel (max jobs: ${MAX_PARALLEL_JOBS:-4})"
    
    local pids_array=()
    local results_array=()
    
    for module in "${modules[@]}"; do
        # Wait if we've reached max parallel jobs
        while [[ ${#pids_array[@]} -ge ${MAX_PARALLEL_JOBS:-4} ]]; do
            wait_for_job_completion_core pids_array results_array
        done
        
        # Start module in background
        start_module_job_core "$modules_dir" "$module" pids_array results_array
    done
    
    # Wait for all remaining jobs
    wait_for_all_jobs_core pids_array results_array
    
    # Report results
    report_parallel_results_core results_array
}

start_module_job_core() {
    local modules_dir="$1"
    local module="$2"
    local -n pids_array_ref="$3"
    local -n results_array_ref="$4"
    
    debug "Starting background job for module: $module"
    
    (
        if execute_single_module "$modules_dir" "$module"; then
            echo "SUCCESS:$module" > "/tmp/orchestrator_result_${module}_$$"
        else
            echo "FAILED:$module" > "/tmp/orchestrator_result_${module}_$$"
        fi
    ) &
    
    pids_array_ref+=($!)
    results_array_ref+=("/tmp/orchestrator_result_${module}_$$")
}

wait_for_all_jobs_core() {
    local -n pids_array_ref="$1"
    local -n results_array_ref="$2"
    
    info "Waiting for all background jobs to complete"
    
    for pid in "${pids_array_ref[@]}"; do
        wait "$pid" || true
    done
    
    pids_array_ref=()
}

report_parallel_results_core() {
    local -n results_array_ref="$1"
    
    info "Parallel execution results:"
    
    local success_count=0
    local failed_count=0
    
    for result_file in "${results_array_ref[@]}"; do
        if [[ -f "$result_file" ]]; then
            local result
            local status
            local module
            
            result=$(cat "$result_file")
            status=$(echo "$result" | cut -d':' -f1)
            module=$(echo "$result" | cut -d':' -f2)
            
            if [[ "$status" == "SUCCESS" ]]; then
                info "  ✓ $module completed successfully"
                ((success_count++))
            else
                error "  ✗ $module failed"
                ((failed_count++))
            fi
            
            rm -f "$result_file"
        fi
    done
    
    info "Parallel execution summary: $success_count successful, $failed_count failed"
    
    if [[ $failed_count -gt 0 ]]; then
        return 1
    fi
}

# Export functions for use in other scripts
export -f execute_modules_parallel

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    execute_modules_parallel "$@"
fi
