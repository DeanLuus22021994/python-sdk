#!/bin/bash
# Parallel Execution Utilities
# Handles parallel and sequential execution of orchestrator modules

declare -g MAX_PARALLEL_JOBS="${MAX_PARALLEL_JOBS:-4}"
declare -g JOB_TIMEOUT="${JOB_TIMEOUT:-300}"

execute_modules_parallel() {
    local modules_dir="$1"
    local pids=()
    local results=()
    
    info "Executing modules in parallel mode (max jobs: $MAX_PARALLEL_JOBS)"
    
    # Find all executable modules
    local modules=($(find "$modules_dir" -name "*.sh" -executable | sort))
    
    for module in "${modules[@]}"; do
        # Wait if we've reached max parallel jobs
        while [[ ${#pids[@]} -ge $MAX_PARALLEL_JOBS ]]; do
            wait_for_job_completion pids results
        done
        
        # Start module in background
        start_module_job "$module" pids results
    done
    
    # Wait for all remaining jobs
    wait_for_all_jobs pids results
    
    # Report results
    report_parallel_results results
}

execute_modules_sequential() {
    local modules_dir="$1"
    local modules=($(find "$modules_dir" -name "*.sh" -executable | sort))
    
    info "Executing modules sequentially"
    
    for module in "${modules[@]}"; do
        local module_name=$(basename "$module" .sh)
        info "Executing module: $module_name"
        
        if timeout "$JOB_TIMEOUT" bash "$module"; then
            info "Module $module_name completed successfully"
        else
            error "Module $module_name failed or timed out"
            return 1
        fi
    done
}

start_module_job() {
    local module="$1"
    local -n pids_ref="$2"
    local -n results_ref="$3"
    local module_name=$(basename "$module" .sh)
    
    debug "Starting module job: $module_name"
    
    (
        if timeout "$JOB_TIMEOUT" bash "$module"; then
            echo "SUCCESS:$module_name" > "/tmp/job_result_$$"
        else
            echo "FAILED:$module_name" > "/tmp/job_result_$$"
        fi
    ) &
    
    pids_ref+=($!)
    results_ref[${#pids_ref[@]}]="/tmp/job_result_$$"
}

wait_for_job_completion() {
    local -n pids_ref="$1"
    local -n results_ref="$2"
    
    # Wait for any job to complete
    wait -n "${pids_ref[@]}"
    
    # Remove completed jobs from arrays
    local new_pids=()
    local new_results=()
    
    for i in "${!pids_ref[@]}"; do
        if kill -0 "${pids_ref[$i]}" 2>/dev/null; then
            new_pids+=("${pids_ref[$i]}")
            new_results+=("${results_ref[$i]}")
        fi
    done
    
    pids_ref=("${new_pids[@]}")
    results_ref=("${new_results[@]}")
}
