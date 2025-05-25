#!/bin/bash
# Sequential Executor - Executes modules one by one
# Provides sequential execution mode for orchestrator modules

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../utils/logging.sh"

execute_modules_sequential() {
    local modules_dir="$1"
    shift
    local modules=("$@")
    
    info "Executing modules sequentially"
    
    for module in "${modules[@]}"; do
        execute_single_module "$modules_dir" "$module"
    done
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

# Export functions for use in other scripts
export -f execute_modules_sequential
export -f execute_single_module

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    execute_modules_sequential "$@"
fi
