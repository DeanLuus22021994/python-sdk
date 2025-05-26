#!/usr/bin/env bash
# shellcheck shell=bash
set -euo pipefail

TOOLS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Tool Registry (ID:Category:Name:Description:Usage)
TOOL_REGISTRY=(
    "devcontainer-state:inspect:DevContainer State:Return current devcontainer status:devcontainer-state.sh [json|table|summary]"
    "build-status:utils:Build Status:Check current build status:build-status.sh [processes|docker|performance]"
    "dev-metrics:metrics:Dev Metrics:Track dev cycle metrics:dev-metrics.sh [record|report|benchmark]"
    "migrate-system:utils:System Migration:Migrate from old to new system:migrate-system.sh [check|migrate|rollback]"
    "modular-status:inspect:Modular Status:Check new modular architecture:modular-status.sh [summary|detailed|validation]"
)

show_tools() {
    echo "Available Tools:"
    for entry in "${TOOL_REGISTRY[@]}"; do
        IFS=":" read -r tool_id tool_cat tool_name tool_desc tool_usage <<< "$entry"
        echo " - $tool_id ($tool_cat): $tool_name"
        echo "   $tool_desc"
        echo "   Usage: $tool_usage"
        echo
    done
}

run_tool() {
    local tool_key="$1"
    shift || true
    case "$tool_key" in
        devcontainer-state)
            "$TOOLS_DIR/inspect/devcontainer-state.sh" "$@"
            ;;
        build-status)
            "$TOOLS_DIR/utils/build-status.sh" "$@"
            ;;
        dev-metrics)
            "$TOOLS_DIR/metrics/dev-metrics.sh" "$@"
            ;;
        migrate-system)
            "$TOOLS_DIR/utils/migrate-system.sh" "$@"
            ;;
        modular-status)
            "$TOOLS_DIR/inspect/modular-status.sh" "$@"
            ;;
        *)
            echo "Tool '$tool_key' not found."
            show_tools
            ;;
    esac
}

case "${1:-help}" in
    list|help)
        show_tools
        ;;
    *)
        run_tool "$@"
        ;;
esac