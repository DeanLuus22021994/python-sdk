#!/bin/bash
# MCP Python SDK - Modular Master Orchestrator
# Coordinates all performance optimization modules with maximum efficiency

set -euo pipefail

SCRIPT_DIR=""
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR=""
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Safely source the required files
# shellcheck source=constants.sh
if [[ -r "$SCRIPT_DIR/constants.sh" ]]; then
    source "$SCRIPT_DIR/constants.sh"
else
    echo "Error: cannot find or read $SCRIPT_DIR/constants.sh"
    exit 1
fi

# shellcheck source=types.sh
if [[ -r "$SCRIPT_DIR/types.sh" ]]; then
    source "$SCRIPT_DIR/types.sh"
else
    echo "Error: cannot find or read $SCRIPT_DIR/types.sh"
    exit 1
fi

# shellcheck source=utils.sh
if [[ -r "$SCRIPT_DIR/utils.sh" ]]; then
    source "$SCRIPT_DIR/utils.sh"
else
    echo "Error: cannot find or read $SCRIPT_DIR/utils.sh"
    exit 1
fi

# shellcheck source=registry.sh
if [[ -r "$SCRIPT_DIR/registry.sh" ]]; then
    source "$SCRIPT_DIR/registry.sh"
else
    echo "Error: cannot find or read $SCRIPT_DIR/registry.sh"
    exit 1
fi

# shellcheck source=../config/load-env.sh
if [[ -r "$ROOT_DIR/config/load-env.sh" ]]; then
    source "$ROOT_DIR/config/load-env.sh"
    # Ensure any load_env_files function is called if defined
    if declare -F load_env_files > /dev/null; then
        load_env_files
    fi
fi

# Logging script is optional but recommended
# shellcheck source=utils/logging.sh
if [[ -r "$SCRIPT_DIR/utils/logging.sh" ]]; then
    source "$SCRIPT_DIR/utils/logging.sh"
fi

# Configuration
export ORCHESTRATOR_VERSION="2.1.0"
export ORCHESTRATOR_PARALLEL="${ORCHESTRATOR_PARALLEL:-false}"
export ORCHESTRATOR_DRY_RUN="${ORCHESTRATOR_DRY_RUN:-false}"
export ORCHESTRATOR_FORCE="${ORCHESTRATOR_FORCE:-false}"

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
    local modules_dir="$SCRIPT_DIR/modules"
    if [[ -d "$modules_dir" ]]; then
        while IFS= read -r -d '' module; do
            local name
            name="$(basename "$module" .sh)"
            local desc
            desc="$(grep "^# .*Module\$" "$module" | head -1 || true)"
            desc="${desc/#"# "/}"
            if [[ -z "$desc" ]]; then
                desc="No description"
            fi
            printf "  %-15s %s\n" "$name" "$desc"
        done < <(find "$modules_dir" -type f -executable -name "*.sh" -print0)
    else
        warn "Modules directory not found: $modules_dir"
    fi
}

execute_orchestration() {
    local modules=("$@")
    if [[ "${#modules[@]}" -eq 0 ]] || [[ "${modules[0]}" == "all" ]]; then
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

    # If there's a core orchestrator script, run it
    if [[ -r "$SCRIPT_DIR/core/main.sh" ]]; then
        ORCHESTRATOR_PARALLEL="$ORCHESTRATOR_PARALLEL" \
        "$SCRIPT_DIR/core/main.sh" "${modules[@]}"
    else
        error "Core orchestrator script not found: $SCRIPT_DIR/core/main.sh"
        return 1
    fi
}

main() {
    local modules=()

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

    execute_orchestration "${modules[@]}"
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi