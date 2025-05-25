#!/bin/bash
# Module Validator - Validates orchestrator modules
# Ensures all required modules exist and are executable

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../utils/logging.sh"

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

# Export for use in other scripts
export -f validate_modules

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    validate_modules "$@"
fi
