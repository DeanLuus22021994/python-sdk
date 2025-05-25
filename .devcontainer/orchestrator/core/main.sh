#!/bin/bash
# Orchestrator Core - Main coordination logic
# Coordinates execution of all optimization modules

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../utils/logging.sh"
source "$SCRIPT_DIR/../utils/parallel.sh"

orchestrator_core_main() {
    local modules=("$@")
    local modules_dir="$SCRIPT_DIR/../modules"
    
    # Default modules if none specified
    if [[ ${#modules[@]} -eq 0 ]]; then
        modules=("cpu" "memory" "io" "binary")
    fi
    
    info "Starting orchestrator core with modules: ${modules[*]}"
    
    # Validate modules exist
    validate_modules "$modules_dir" "${modules[@]}"
    
    # Execute based on parallel mode
    if [[ "${ORCHESTRATOR_PARALLEL:-false}" == "true" ]]; then
        execute_modules_parallel "$modules_dir" "${modules[@]}"
    else
        execute_modules_sequential "$modules_dir" "${modules[@]}"
    fi
    
    info "Orchestrator core execution completed"
}

validate_modules() {
    local modules_dir="$1"
    shift
    local modules=("$@")
    
    info "Validating modules availability"
    
    for module in "${modules[@]}"; do
        local module_file="$modules_dir/${module}-optimize.sh"
        
        # Handle special case for binary-precompile
        if [[ "$module" == "binary" ]]; then
            module_file="$modules_dir/binary-precompile.sh"
        fi
        
        if [[ ! -f "$module_file" ]]; then
            error "Module not found: $module_file"
            return 1
        fi
        
        if [[ ! -x "$module_file" ]]; then
            error "Module not executable: $module_file"
            return 1
        fi
        
        debug "Module validated: $module"
    done
    
    info "All modules validated successfully"
}

execute_modules_sequential() {
    local modules_dir="$1"
    shift
    local modules=("$@")
    
    info "Executing modules sequentially"
    
    for module in "${modules[@]}"; do
        execute_single_module "$modules_dir" "$module"
    done
}

execute_modules_parallel() {
    local modules_dir="$1"
    shift
    local modules=("$@")
    
    info "Executing modules in parallel (max jobs: ${MAX_PARALLEL_JOBS:-4})"
    
    local pids=()
    local results=()
    
    for module in "${modules[@]}"; do
        # Wait if we've reached max parallel jobs
        while [[ ${#pids[@]} -ge ${MAX_PARALLEL_JOBS:-4} ]]; do
            wait_for_job_completion pids results
        done
        
        # Start module in background
        start_module_job "$modules_dir" "$module" pids results
    done
    
    # Wait for all remaining jobs
    wait_for_all_jobs pids results
    
    # Report results
    report_parallel_results results
}

execute_single_module() {
    local modules_dir="$1"
    local module="$2"
    local module_file="$modules_dir/${module}-optimize.sh"
    
    # Handle special case for binary-precompile
    if [[ "$module" == "binary" ]]; then
        module_file="$modules_dir/binary-precompile.sh"
    fi
    
    info "Executing module: $module"
    
    local start_time=$(date +%s)
    
    if timeout "${JOB_TIMEOUT:-300}" bash "$module_file"; then
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        info "Module $module completed successfully in ${duration}s"
        return 0
    else
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        error "Module $module failed or timed out after ${duration}s"
        return 1
    fi
}

start_module_job() {
    local modules_dir="$1"
    local module="$2"
    local -n pids_ref="$3"
    local -n results_ref="$4"
    
    debug "Starting background job for module: $module"
    
    (
        if execute_single_module "$modules_dir" "$module"; then
            echo "SUCCESS:$module" > "/tmp/orchestrator_result_${module}_$$"
        else
            echo "FAILED:$module" > "/tmp/orchestrator_result_${module}_$$"
        fi
    ) &
    
    pids_ref+=($!)
    results_ref+=("/tmp/orchestrator_result_${module}_$$")
}

wait_for_all_jobs() {
    local -n pids_ref="$1"
    local -n results_ref="$2"
    
    info "Waiting for all background jobs to complete"
    
    for pid in "${pids_ref[@]}"; do
        wait "$pid" || true
    done
    
    pids_ref=()
}

report_parallel_results() {
    local -n results_ref="$1"
    
    info "Parallel execution results:"
    
    local success_count=0
    local failed_count=0
    
    for result_file in "${results_ref[@]}"; do
        if [[ -f "$result_file" ]]; then
            local result=$(cat "$result_file")
            local status=$(echo "$result" | cut -d':' -f1)
            local module=$(echo "$result" | cut -d':' -f2)
            
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

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    orchestrator_core_main "$@"
fi
