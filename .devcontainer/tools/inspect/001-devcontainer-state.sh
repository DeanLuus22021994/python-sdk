#!/bin/bash
# Tool 001: DevContainer State Inspector
# Purpose: Return current state of files in devcontainer directory with machine-readable output
# Usage: ./001-devcontainer-state.sh [json|table|summary]

get_devcontainer_state() {
    local format="${1:-summary}"
    local base_dir="/workspaces/python-sdk/.devcontainer"
    
    case "$format" in
        "json")
            find "$base_dir" -type f -exec stat -c '{"file":"%n","size":%s,"modified":"%Y","permissions":"%a"}' {} \; | jq -s '.'
            ;;
        "table")
            printf "%-50s %-10s %-20s %-10s\n" "FILE" "SIZE" "MODIFIED" "PERMS"
            find "$base_dir" -type f -exec stat -c "%-50n %-10s %-20Y %-10a" {} \;
            ;;
        *)
            echo "DevContainer Files: $(find "$base_dir" -type f | wc -l)"
            echo "Total Size: $(du -sh "$base_dir" | cut -f1)"
            echo "Last Modified: $(find "$base_dir" -type f -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)"
            ;;
    esac
}

get_devcontainer_state "$@"
