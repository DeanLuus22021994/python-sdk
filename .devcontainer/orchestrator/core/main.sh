#!/bin/bash
# Orchestrator Core - Main coordination logic
# Coordinates execution of all optimization modules

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../utils/logging.sh"
source "$SCRIPT_DIR/validator.sh"
source "$SCRIPT_DIR/sequential.sh"
source "$SCRIPT_DIR/parallel.sh"

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

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    orchestrator_core_main "$@"
fi
