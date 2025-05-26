#!/bin/bash
# Consolidated Parallel Execution Utilities
# Single source of truth for parallel execution functionality

set -euo pipefail

# Source logging utilities
# shellcheck source=./logging.sh
source "$(dirname "${BASH_SOURCE[0]}")/logging.sh"

# Global configuration with defaults
declare -g MAX_PARALLEL_JOBS="${MAX_PARALLEL_JOBS:-4}"
declare -g JOB_TIMEOUT="${JOB_TIMEOUT:-300}"
declare -g TEMP_DIR="${TEMP_DIR:-/tmp}"

# Execute specified modules in parallel
# Arguments:
#   $1: modules_dir - Directory containing the module scripts
#   $2+: modules - Names of modules to execute (without .sh extension)
execute_modules_parallel() {
    local modules_dir="$1"
    shift
    local modules=("$@")
    
    # If no modules specified, find all executable modules
    if [[ ${#modules[@]} -eq 0 ]]; then
        mapfile -t modules < <(find "$modules_dir" -name "*.sh" -executable -exec basename {} .sh \;)
    fi
    
    info "Executing modules in parallel (max jobs: $MAX_PARALLEL_JOBS)"
    
    local job_pids=()
    local result_files=()
    
    for module in "${modules[@]}"; do
        # Wait if we've reached max parallel jobs
        while [[ ${#job_pids[@]} -ge $MAX_PARALLEL_JOBS ]]; do
            wait_for_job_completion job_pids result_files
        done
        
        # Start module in background
        start_module_job "$modules_dir" "$module" job_pids result_files
    done
    
    # Wait for all remaining jobs
    wait_for_all_jobs job_pids result_files
    
    # Report results
    report_parallel_results result_files
}

# Execute modules sequentially
# Arguments:
#   $1: modules_dir - Directory containing the module scripts
#   $2+: modules - Names of modules to execute (without .sh extension)
execute_modules_sequential() {
    local modules_dir="$1"
    shift
    local modules=("$@")
    
    # If no modules specified, find all executable modules
    if [[ ${#modules[@]} -eq 0 ]]; then
        mapfile -t modules < <(find "$modules_dir" -name "*.sh" -executable -exec basename {} .sh \;)
    fi
    
    info "Executing modules sequentially"
    
    for module in "${modules[@]}"; do
        execute_single_module "$modules_dir" "$module"
    done
}

# Execute a single module
# Arguments:
#   $1: modules_dir - Directory containing the module scripts
#   $2: module - Name of module to execute (without .sh extension)
execute_single_module() {
    local modules_dir="$1"
    local module="$2"
    local module_path="${modules_dir}/${module}.sh"
    
    if [[ ! -x "$module_path" ]]; then
        error "Module not found or not executable: $module"
        return 1
    fi
    
    info "Executing module: $module"
    if timeout "$JOB_TIMEOUT" bash "$module_path"; then
        info "Module $module completed successfully"
        return 0
    else
        local status=$?
        error "Module $module failed with status $status or timed out"
        return $status
    fi
}

# Start a module job in the background
# Arguments:
#   $1: modules_dir - Directory containing the module scripts
#   $2: module - Name of module to execute (without .sh extension)
#   $3: pids_array_name - Name of array variable to store PIDs
#   $4: results_array_name - Name of array variable to store result file paths
start_module_job() {
    local modules_dir="$1"
    local module="$2"
    local -n pids_array="$3"
    local -n results_array="$4"
    local module_path="${modules_dir}/${module}.sh"
    local result_file="${TEMP_DIR}/orchestrator_result_${module}_$$"
    
    debug "Starting background job for module: $module"
    
    (
        if [[ -x "$module_path" ]]; then
            if timeout "$JOB_TIMEOUT" bash "$module_path"; then
                echo "SUCCESS:$module" > "$result_file"
            else
                echo "FAILED:$module" > "$result_file"
            fi
        else
            echo "ERROR:$module:Module not found or not executable" > "$result_file"
        fi
    ) &
    
    pids_array+=($!)
    results_array+=("$result_file")
}

# Wait for a single job to complete
# Arguments:
#   $1: pids_array_name - Name of array variable storing PIDs
#   $2: results_array_name - Name of array variable storing result file paths
wait_for_job_completion() {
    local -n pids_array="$1"
    local -n results_array="$2"
    
    # Wait for any job to complete
    wait -n "${pids_array[@]}" 2>/dev/null || true
    
    # Remove completed jobs from arrays
    local new_pids=()
    local new_results=()
    
    for i in "${!pids_array[@]}"; do
        if kill -0 "${pids_array[$i]}" 2>/dev/null; then
            new_pids+=("${pids_array[$i]}")
            new_results+=("${results_array[$i]}")
        fi
    done
    
    pids_array=("${new_pids[@]}")
    results_array=("${new_results[@]}")
}

# Wait for all jobs to complete
# Arguments:
#   $1: pids_array_name - Name of array variable storing PIDs
#   $2: results_array_name - Name of array variable storing result file paths
wait_for_all_jobs() {
    local -n pids_array="$1"
    local -n results_array="$2"  # Referenced but not modified, keeping for consistency
    
    debug "Waiting for all background jobs to complete"
    
    for pid in "${pids_array[@]}"; do
        wait "$pid" 2>/dev/null || true
    done
    
    pids_array=()
}

# Report results from parallel execution
# Arguments:
#   $1: results_array_name - Name of array variable storing result file paths
report_parallel_results() {
    local -n results_array="$1"
    
    info "Parallel execution results:"
    
    local success_count=0
    local failed_count=0
    local error_count=0
    
    for result_file in "${results_array[@]}"; do
        if [[ -f "$result_file" ]]; then
            local result
            result=$(cat "$result_file")
            local status
            status=$(echo "$result" | cut -d':' -f1)
            local module
            module=$(echo "$result" | cut -d':' -f2)
            
            case "$status" in
                "SUCCESS")
                    info "  ✓ $module completed successfully"
                    ((success_count++))
                    ;;
                "FAILED")
                    error "  ✗ $module failed"
                    ((failed_count++))
                    ;;
                "ERROR")
                    local error_msg
                    error_msg=$(echo "$result" | cut -d':' -f3-)
                    error "  ✗ $module error: $error_msg"
                    ((error_count++))
                    ;;
            esac
            
            rm -f "$result_file"
        fi
    done
    
    info "Execution summary: $success_count successful, $failed_count failed, $error_count errors"
    
    if [[ $failed_count -gt 0 || $error_count -gt 0 ]]; then
        return 1
    fi
    
    return 0
}

# Export functions for use by other scripts
export -f execute_modules_parallel
export -f execute_modules_sequential
export -f execute_single_module
export -f start_module_job
export -f wait_for_job_completion
export -f wait_for_all_jobs
export -f report_parallel_results

# If this script is executed directly, show usage
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "This is a library script, not meant to be executed directly."
    echo "Source it from other scripts to use the parallel execution functions."
    exit 1
fi
