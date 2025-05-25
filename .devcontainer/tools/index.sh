#!/bin/bash
# DevContainer Tools Index
# Centralized registry and launcher for all development utilities

TOOLS_DIR="/workspaces/python-sdk/.devcontainer/tools"

# Tool Registry - Format: "ID:Category:Name:Description:Usage"
TOOL_REGISTRY=(
    "devcontainer-state:inspect:DevContainer State:Return current state of files in devcontainer directory:devcontainer-state.sh [json|table|summary]"
    "build-status:utils:Build Status:Check current build status and active processes:build-status.sh [processes|docker|performance]"
    "dev-metrics:metrics:Dev Metrics:Track development cycle metrics and performance benchmarks:dev-metrics.sh [record|report|benchmark]"
    "migrate-system:utils:System Migration:Migrate from old build system to new modular architecture:migrate-system.sh [check|migrate|rollback]"
    "modular-status:inspect:Modular Status:Comprehensive status check of the new modular architecture:modular-status.sh [detailed|summary|validation]"
)

show_tools() {
    echo "=== DevContainer Tools Registry ==="
    printf "%-4s %-10s %-20s %-50s\n" "ID" "CATEGORY" "NAME" "DESCRIPTION"
    echo "$(printf '=%.0s' {1..90})"
    
    for tool in "${TOOL_REGISTRY[@]}"; do
        IFS=':' read -r id category name description usage <<< "$tool"
        printf "%-4s %-10s %-20s %-50s\n" "$id" "$category" "$name" "$description"
    done
}

run_tool() {
    local tool_id="$1"
    shift
    
    for tool in "${TOOL_REGISTRY[@]}"; do
        IFS=':' read -r id category name description usage <<< "$tool"
        if [[ "$id" == "$tool_id" ]]; then
            local script_name=$(echo "$usage" | awk '{print $1}')
            local script_path="$TOOLS_DIR/$category/$script_name"
            
            if [[ -x "$script_path" ]]; then
                echo "Running: $name ($id)"
                "$script_path" "$@"
            else
                echo "Error: Tool script not found or not executable: $script_path"
                return 1
            fi
            return 0
        fi
    done
    
    echo "Error: Tool $tool_id not found"
    return 1
}

case "${1:-help}" in
    "list"|"show"|"help")
        show_tools
        echo -e "\nUsage: $0 <tool_id> [arguments...]"
        echo "       $0 list                    # Show all available tools"
        ;;
    *)
        run_tool "$@"
        ;;
esac
