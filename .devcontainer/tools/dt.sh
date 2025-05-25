#!/bin/bash
# DevContainer Tools Quick Access
# Provides easy access to development tools from any location

TOOLS_DIR="/workspaces/python-sdk/.devcontainer/tools"

# Quick aliases for common tools
dt() {
    case "$1" in
        "state"|"s")
            shift
            "$TOOLS_DIR/index.sh" 001 "$@"
            ;;
        "status"|"st")
            shift
            "$TOOLS_DIR/index.sh" 002 "$@"
            ;;
        "metrics"|"m")
            shift
            "$TOOLS_DIR/index.sh" 003 "$@"
            ;;
        "list"|"l"|"")
            "$TOOLS_DIR/index.sh" list
            ;;
        *)
            "$TOOLS_DIR/index.sh" "$@"
            ;;
    esac
}

# Export the function for use in shell
if [[ "${BASH_SOURCE[0]}" != "${0}" ]]; then
    # Being sourced
    export -f dt
    echo "DevContainer tools loaded. Use 'dt' command or 'dt list' to see available tools."
else
    # Being executed
    dt "$@"
fi
