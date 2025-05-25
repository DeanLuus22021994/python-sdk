#!/bin/bash
# Master Build and Performance Orchestration Script
# Coordinates all performance optimizations and build processes following modular SRP design

# Source common utilities
source "$(dirname "${BASH_SOURCE[0]}")/scripts/utils/common.sh"

# Initialize
init_common

# Script metadata
readonly SCRIPT_VERSION="2.0.0"
readonly SCRIPT_NAME="MCP Python SDK Master Orchestrator"

# Available modules
declare -A MODULES=(
    ["gpu"]="scripts/setup/gpu-passthrough.sh"
    ["cpu"]="scripts/performance/cpu-optimize.sh"
    ["memory"]="scripts/performance/memory-optimize.sh"
    ["io"]="scripts/performance/io-optimize.sh"
    ["binary"]="scripts/build/binary-precompile.sh"
    ["validation"]="scripts/validation/performance-validate.sh"
    ["monitoring"]="scripts/utils/status-monitor.sh"
)

# Configuration
readonly CONFIG_DIR=".devcontainer"
readonly LOCK_FILE="/tmp/mcp-orchestrator.lock"
readonly LOG_FILE="/tmp/mcp-orchestrator.log"

# Show banner
show_banner() {
    echo -e "${CYAN}"
    echo "=================================================================="
    echo "  $SCRIPT_NAME v$SCRIPT_VERSION"
    echo "  High-Performance MCP Python SDK Optimization Suite"
    echo "=================================================================="
    echo -e "${NC}"
}

# Show usage information
show_usage() {
    cat << EOF
Usage: $0 [OPTIONS] [MODULES...]

OPTIONS:
    -h, --help              Show this help message
    -v, --version           Show version information
    -a, --all               Run all optimization modules
    -f, --force             Force execution even if already optimized
    -q, --quiet             Suppress non-error output
    -d, --debug             Enable debug output
    -c, --config DIR        Use custom configuration directory
    -l, --list              List available modules
    -s, --status            Show current optimization status
    -r, --rollback          Rollback previous optimizations
    --dry-run               Show what would be executed without running
    --parallel              Run compatible modules in parallel
    --skip-validation       Skip performance validation step

MODULES:
    gpu                     GPU passthrough detection and configuration
    cpu                     CPU performance optimization
    memory                  Memory allocation and caching optimization
    io                      I/O and storage performance optimization
    binary                  Binary precompilation and caching
    validation              Performance validation and testing
    monitoring              Status monitoring and dashboard

EXAMPLES:
    $0 --all                            # Run all optimizations
    $0 cpu memory io                    # Run specific modules
    $0 --parallel cpu memory            # Run modules in parallel
    $0 --force binary                   # Force recompilation of binaries
    $0 --status                         # Show optimization status
    $0 --dry-run --all                  # Preview all operations

For more information, visit: https://github.com/modelcontextprotocol/python-sdk
EOF
}

# Parse command line arguments
parse_arguments() {
    local modules_to_run=()
    local run_all=false
    local force_execution=false
    local quiet_mode=false
    local debug_mode=false
    local custom_config=""
    local list_modules=false
    local show_status=false
    local rollback_mode=false
    local dry_run=false
    local parallel_execution=false
    local skip_validation=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage
                exit 0
                ;;
            -v|--version)
                echo "$SCRIPT_NAME v$SCRIPT_VERSION"
                exit 0
                ;;
            -a|--all)
                run_all=true
                shift
                ;;
            -f|--force)
                force_execution=true
                export FORCE_EXECUTION=true
                shift
                ;;
            -q|--quiet)
                quiet_mode=true
                export QUIET_MODE=true
                shift
                ;;
            -d|--debug)
                debug_mode=true
                export DEBUG_MODE=true
                shift
                ;;
            -c|--config)
                custom_config="$2"
                shift 2
                ;;
            -l|--list)
                list_modules=true
                shift
                ;;
            -s|--status)
                show_status=true
                shift
                ;;
            -r|--rollback)
                rollback_mode=true
                shift
                ;;
            --dry-run)
                dry_run=true
                export DRY_RUN=true
                shift
                ;;
            --parallel)
                parallel_execution=true
                export PARALLEL_EXECUTION=true
                shift
                ;;
            --skip-validation)
                skip_validation=true
                export SKIP_VALIDATION=true
                shift
                ;;
            -*)
                log_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
            *)
                modules_to_run+=("$1")
                shift
                ;;
        esac
    done
    
    # Handle special modes
    if $list_modules; then
        list_available_modules
        exit 0
    fi
    
    if $show_status; then
        show_optimization_status
        exit 0
    fi
    
    if $rollback_mode; then
        rollback_optimizations
        exit 0
    fi
    
    # Determine modules to run
    if $run_all; then
        modules_to_run=("${!MODULES[@]}")
    elif [[ ${#modules_to_run[@]} -eq 0 ]]; then
        log_error "No modules specified. Use --all or specify modules explicitly."
        show_usage
        exit 1
    fi
    
    # Export configuration
    export MODULES_TO_RUN=("${modules_to_run[@]}")
    export DRY_RUN=$dry_run
    export PARALLEL_EXECUTION=$parallel_execution
    export SKIP_VALIDATION=$skip_validation
    export FORCE_EXECUTION=$force_execution
    
    if [[ -n "$custom_config" ]]; then
        export CONFIG_DIR="$custom_config"
    fi
}

# List available modules
list_available_modules() {
    echo -e "${BLUE}Available optimization modules:${NC}"
    echo
    
    for module in "${!MODULES[@]}"; do
        local script_path="${MODULES[$module]}"
        local description=""
        
        case $module in
            gpu) description="GPU passthrough detection and configuration" ;;
            cpu) description="CPU performance optimization (governor, frequency, threading)" ;;
            memory) description="Memory allocation and caching optimization" ;;
            io) description="I/O scheduler and storage performance optimization" ;;
            binary) description="Binary precompilation and dependency caching" ;;
            validation) description="Performance validation and benchmarking" ;;
            monitoring) description="Real-time status monitoring and dashboard" ;;
        esac
        
        printf "  %-12s %s\n" "$module" "$description"
    done
    
    echo
}

# Show optimization status
show_optimization_status() {
    log_step "Checking optimization status..."
    
    # Check if optimizations have been applied
    local status_file="$CACHE_ROOT/optimization-status.json"
    
    if [[ -f "$status_file" ]]; then
        local last_run=$(jq -r '.last_run // "never"' "$status_file" 2>/dev/null)
        local modules_run=($(jq -r '.modules_completed[]? // empty' "$status_file" 2>/dev/null))
        
        echo -e "${GREEN}Optimization Status:${NC}"
        echo "  Last run: $last_run"
        echo "  Modules completed: ${modules_run[*]}"
        echo
        
        # Show detailed status for each module
        for module in "${!MODULES[@]}"; do
            local module_status="Not run"
            if [[ " ${modules_run[*]} " =~ " $module " ]]; then
                module_status="Completed"
            fi
            printf "  %-12s %s\n" "$module:" "$module_status"
        done
    else
        echo -e "${YELLOW}No optimizations have been run yet.${NC}"
    fi
    
    echo
    
    # Show system status
    if [[ -x "scripts/utils/status-monitor.sh" ]]; then
        "./scripts/utils/status-monitor.sh" --brief
    fi
}

# Create lock file
create_lock() {
    if [[ -f "$LOCK_FILE" ]]; then
        local lock_pid=$(cat "$LOCK_FILE" 2>/dev/null)
        if [[ -n "$lock_pid" ]] && kill -0 "$lock_pid" 2>/dev/null; then
            log_error "Another instance is already running (PID: $lock_pid)"
            exit 1
        else
            log_warning "Stale lock file found, removing..."
            rm -f "$LOCK_FILE"
        fi
    fi
    
    echo $$ > "$LOCK_FILE"
    log_debug "Created lock file: $LOCK_FILE"
}

# Remove lock file
remove_lock() {
    if [[ -f "$LOCK_FILE" ]]; then
        rm -f "$LOCK_FILE"
        log_debug "Removed lock file: $LOCK_FILE"
    fi
}

# Cleanup on exit
cleanup_on_exit() {
    remove_lock
    cleanup_temp
}

# Set up signal handlers
trap cleanup_on_exit EXIT
trap 'log_error "Script interrupted"; exit 130' INT TERM

# Validate module exists
validate_module() {
    local module="$1"
    local script_path="${MODULES[$module]}"
    
    if [[ -z "$script_path" ]]; then
        log_error "Unknown module: $module"
        return 1
    fi
    
    if [[ ! -f "$script_path" ]]; then
        log_error "Module script not found: $script_path"
        return 1
    fi
    
    if [[ ! -x "$script_path" ]]; then
        log_error "Module script not executable: $script_path"
        return 1
    fi
    
    return 0
}

# Execute module
execute_module() {
    local module="$1"
    local script_path="${MODULES[$module]}"
    
    log_step "Executing module: $module"
    
    if [[ "${DRY_RUN:-false}" == "true" ]]; then
        log_debug "DRY RUN: Would execute $script_path"
        return 0
    fi
    
    local start_time=$(date +%s)
    
    # Execute with timeout and error handling
    if execute_with_timeout 1800 bash "$script_path"; then
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        log_success "Module completed in ${duration}s: $module"
        return 0
    else
        local exit_code=$?
        log_error "Module failed with exit code $exit_code: $module"
        return $exit_code
    fi
}

# Execute modules in parallel
execute_modules_parallel() {
    local modules=("$@")
    local pids=()
    local results=()
    
    log_step "Executing ${#modules[@]} modules in parallel..."
    
    # Start all modules
    for module in "${modules[@]}"; do
        if validate_module "$module"; then
            execute_module "$module" &
            local pid=$!
            pids+=($pid)
            log_debug "Started module $module with PID $pid"
        else
            results+=("$module:FAILED")
        fi
    done
    
    # Wait for all modules to complete
    local index=0
    for pid in "${pids[@]}"; do
        local module="${modules[$index]}"
        
        if wait $pid; then
            results+=("$module:SUCCESS")
            log_success "Parallel module completed: $module"
        else
            results+=("$module:FAILED")
            log_error "Parallel module failed: $module"
        fi
        
        ((index++))
    done
    
    # Report results
    local success_count=0
    local failed_count=0
    
    for result in "${results[@]}"; do
        local module="${result%:*}"
        local status="${result#*:}"
        
        if [[ "$status" == "SUCCESS" ]]; then
            ((success_count++))
        else
            ((failed_count++))
        fi
    done
    
    log_step "Parallel execution completed: $success_count succeeded, $failed_count failed"
    return $failed_count
}

# Execute modules sequentially
execute_modules_sequential() {
    local modules=("$@")
    local failed_modules=()
    
    log_step "Executing ${#modules[@]} modules sequentially..."
    
    for module in "${modules[@]}"; do
        if validate_module "$module"; then
            if execute_module "$module"; then
                log_success "Sequential module completed: $module"
            else
                failed_modules+=("$module")
                log_error "Sequential module failed: $module"
                
                # Stop on first failure unless force mode is enabled
                if [[ "${FORCE_EXECUTION:-false}" != "true" ]]; then
                    log_error "Stopping execution due to failure. Use --force to continue on errors."
                    return 1
                fi
            fi
        else
            failed_modules+=("$module")
        fi
    done
    
    if [[ ${#failed_modules[@]} -gt 0 ]]; then
        log_warning "Failed modules: ${failed_modules[*]}"
        return 1
    fi
    
    return 0
}

# Update optimization status
update_status() {
    local modules=("$@")
    local status_file="$CACHE_ROOT/optimization-status.json"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    # Create status directory
    create_dir "$(dirname "$status_file")"
    
    # Create or update status file
    if [[ -f "$status_file" ]]; then
        # Update existing status
        local temp_file=$(mktemp)
        jq --arg timestamp "$timestamp" \
           --argjson modules "$(printf '%s\n' "${modules[@]}" | jq -R . | jq -s .)" \
           '.last_run = $timestamp | .modules_completed = $modules' \
           "$status_file" > "$temp_file" && mv "$temp_file" "$status_file"
    else
        # Create new status file
        cat > "$status_file" << EOF
{
    "last_run": "$timestamp",
    "modules_completed": [$(printf '"%s",' "${modules[@]}" | sed 's/,$//')],
    "version": "$SCRIPT_VERSION"
}
EOF
    fi
    
    log_debug "Updated optimization status: $status_file"
}

# Main orchestration function
main() {
    show_banner
    
    # Parse arguments
    parse_arguments "$@"
    
    # Check prerequisites
    check_root
    check_privileged
    check_system_requirements
    
    # Create lock
    create_lock
    
    # Change to workspace directory
    cd "${WORKSPACE_FOLDER:-/workspaces/python-sdk}" || {
        log_error "Cannot change to workspace directory"
        exit 1
    }
    
    # Get modules to run
    local modules_to_run=("${MODULES_TO_RUN[@]}")
    
    log_step "Starting optimization for modules: ${modules_to_run[*]}"
    
    # Execute modules
    local execution_success=false
    
    if [[ "${PARALLEL_EXECUTION:-false}" == "true" ]]; then
        # Check which modules can run in parallel
        local parallel_modules=()
        local sequential_modules=()
        
        for module in "${modules_to_run[@]}"; do
            case $module in
                cpu|memory|io)
                    parallel_modules+=("$module")
                    ;;
                *)
                    sequential_modules+=("$module")
                    ;;
            esac
        done
        
        # Execute parallel modules first
        if [[ ${#parallel_modules[@]} -gt 0 ]]; then
            if execute_modules_parallel "${parallel_modules[@]}"; then
                log_success "Parallel modules completed successfully"
            else
                log_error "Some parallel modules failed"
            fi
        fi
        
        # Execute remaining modules sequentially
        if [[ ${#sequential_modules[@]} -gt 0 ]]; then
            if execute_modules_sequential "${sequential_modules[@]}"; then
                execution_success=true
            fi
        else
            execution_success=true
        fi
    else
        # Execute all modules sequentially
        if execute_modules_sequential "${modules_to_run[@]}"; then
            execution_success=true
        fi
    fi
    
    # Update status
    if $execution_success; then
        update_status "${modules_to_run[@]}"
        
        # Run validation unless skipped
        if [[ "${SKIP_VALIDATION:-false}" != "true" ]] && [[ -x "scripts/validation/performance-validate.sh" ]]; then
            log_step "Running performance validation..."
            if ./scripts/validation/performance-validate.sh; then
                log_success "Performance validation completed successfully"
            else
                log_warning "Performance validation completed with warnings"
            fi
        fi
        
        log_success "Optimization orchestration completed successfully"
        log_success "All optimizations are active and cached for instant subsequent builds"
        
        # Show final status
        if [[ -x "scripts/utils/status-monitor.sh" ]]; then
            log_step "Final system status:"
            ./scripts/utils/status-monitor.sh --brief
        fi
        
        exit 0
    else
        log_error "Optimization orchestration failed"
        exit 1
    fi
}

# Execute main function
main "$@"
