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
    
    # Use global arrays to avoid nameref conflicts
    declare -ag PARALLEL_PIDS=()
    declare -ag PARALLEL_RESULTS=()
    
    for module in "${modules[@]}"; do
        # Wait if we've reached max parallel jobs
        while [[ ${#PARALLEL_PIDS[@]} -ge ${MAX_PARALLEL_JOBS:-4} ]]; do
            wait_for_job_completion_core
        done
        
        # Start module in background
        start_module_job_core "$modules_dir" "$module"
    done
    
    # Wait for all remaining jobs
    wait_for_all_jobs_core
    
    # Report results
    report_parallel_results_core
}

start_module_job_core() {
    local modules_dir="$1"
    local module="$2"
    
    debug "Starting background job for module: $module"
    
    (
        if execute_single_module "$modules_dir" "$module"; then
            echo "SUCCESS:$module" > "/tmp/orchestrator_result_${module}_$$"
        else
            echo "FAILED:$module" > "/tmp/orchestrator_result_${module}_$$"
        fi
    ) &
    
    PARALLEL_PIDS+=($!)
    PARALLEL_RESULTS+=("/tmp/orchestrator_result_${module}_$$")
}

wait_for_job_completion_core() {
    # Wait for any job to complete
    wait -n "${PARALLEL_PIDS[@]}" 2>/dev/null || true
    
    # Remove completed jobs from arrays
    local new_pids=()
    local new_results=()
    
    for i in "${!PARALLEL_PIDS[@]}"; do
        if kill -0 "${PARALLEL_PIDS[$i]}" 2>/dev/null; then
            new_pids+=("${PARALLEL_PIDS[$i]}")
            new_results+=("${PARALLEL_RESULTS[$i]}")
        fi
    done
    
    PARALLEL_PIDS=("${new_pids[@]}")
    PARALLEL_RESULTS=("${new_results[@]}")
}

wait_for_all_jobs_core() {
    info "Waiting for all background jobs to complete"
    
    for pid in "${PARALLEL_PIDS[@]}"; do
        wait "$pid" || true
    done
    
    PARALLEL_PIDS=()
}

report_parallel_results_core() {
    info "Parallel execution results:"
    
    local success_count=0
    local failed_count=0
    
    for result_file in "${PARALLEL_RESULTS[@]}"; do
        if [[ -f "$result_file" ]]; then
            local result
            result=$(cat "$result_file")
            
            local status
            status=$(echo "$result" | cut -d':' -f1)
            
            local module
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
