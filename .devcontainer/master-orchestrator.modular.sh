#!/bin/bash
# MCP Python SDK - Modular Master Orchestrator
# Coordinates all performance optimization modules with maximum efficiency

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config/load-env.sh"
load_env_files
source "$SCRIPT_DIR/orchestrator/utils/logging.sh"

# Configuration
declare -g ORCHESTRATOR_VERSION="2.0.0"
declare -g ORCHESTRATOR_PARALLEL="${ORCHESTRATOR_PARALLEL:-false}"
declare -g ORCHESTRATOR_DRY_RUN="${ORCHESTRATOR_DRY_RUN:-false}"
declare -g ORCHESTRATOR_FORCE="${ORCHESTRATOR_FORCE:-false}"

show_usage() {
    cat << EOF
MCP Python SDK Master Orchestrator v$ORCHESTRATOR_VERSION

USAGE:
    $0 [OPTIONS] [MODULES...]

OPTIONS:
    --parallel, -p      Execute modules in parallel
    --dry-run, -d       Show what would be executed without running
    --force, -f         Force execution even if lock file exists
    --help, -h          Show this help message
    --version, -v       Show version information
    --list, -l          List available modules

MODULES:
    cpu                 CPU optimization module
    memory              Memory optimization module  
    io                  I/O optimization module
    binary              Binary precompilation module
    all                 Execute all modules (default)

EXAMPLES:
    $0                  # Execute all modules sequentially
    $0 --parallel       # Execute all modules in parallel
    $0 cpu memory       # Execute only CPU and memory modules
    $0 --dry-run all    # Show what would be executed
EOF
}

list_available_modules() {
    info "Available orchestrator modules:"
    local modules_dir="$SCRIPT_DIR/orchestrator/modules"
    
    if [[ -d "$modules_dir" ]]; then
        find "$modules_dir" -name "*.sh" -executable | while read -r module; do
            local name=$(basename "$module" .sh)
            local desc=$(grep "^# .*Module$" "$module" | head -1 | sed 's/^# //' || echo "No description")
            printf "  %-15s %s\n" "$name" "$desc"
        done
    else
        warn "Modules directory not found: $modules_dir"
    fi
}

execute_orchestration() {
    local modules=("$@")
    
    # Default to all modules if none specified
    if [[ ${#modules[@]} -eq 0 ]] || [[ "${modules[0]}" == "all" ]]; then
        modules=(cpu memory io binary)
    fi
    
    info "Executing modules: ${modules[*]}"
    
    if [[ "$ORCHESTRATOR_DRY_RUN" == "true" ]]; then
        info "DRY RUN MODE - Would execute:"
        for module in "${modules[@]}"; do
            echo "  - $module optimization"
        done
        return 0
    fi
    
    # Execute the core orchestrator
    ORCHESTRATOR_PARALLEL="$ORCHESTRATOR_PARALLEL" \
    "$SCRIPT_DIR/orchestrator/core/main.sh" "${modules[@]}"
}

main() {
    local modules=()
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --parallel|-p)
                ORCHESTRATOR_PARALLEL="true"
                shift
                ;;
            --dry-run|-d)
                ORCHESTRATOR_DRY_RUN="true"
                shift
                ;;
            --force|-f)
                ORCHESTRATOR_FORCE="true"
                shift
                ;;
            --help|-h)
                show_usage
                exit 0
                ;;
            --version|-v)
                echo "MCP Python SDK Master Orchestrator v$ORCHESTRATOR_VERSION"
                exit 0
                ;;
            --list|-l)
                list_available_modules
                exit 0
                ;;
            *)
                modules+=("$1")
                shift
                ;;
        esac
    done
    
    # Execute orchestration
    execute_orchestration "${modules[@]}"
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
