#!/bin/bash
# DevContainer Orchestrator Types
# Centralized type definitions for bash scripts

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# shellcheck source=./constants.sh
if [[ -r "$SCRIPT_DIR/constants.sh" ]]; then
    source "$SCRIPT_DIR/constants.sh"
else
    echo "Error: cannot find or read $SCRIPT_DIR/constants.sh"
    exit 1
fi

# Create a standardized result structure (result_ref is used by reference in the caller)
# Usage:
#   local result
#   create_result result "success" "Operation completed" 0
#   echo "${result[status]}"
create_result() {
    local -n result_ref="$1"
    local status="$2"
    local message="$3"
    local code="${4:-0}"
    local data="${5:-}"
    local timestamp=""

    timestamp="$(date +%s)"

    # Reinitialize the array in the caller by name
    result_ref=()
    result_ref[status]="$status"
    result_ref[message]="$message"
    result_ref[code]="$code"
    result_ref[data]="$data"
    result_ref[timestamp]="$timestamp"
}

# Create a standardized config structure (config_ref is used by reference in the caller)
# Usage:
#   local cfg
#   create_config cfg "memory_optimization" "true" "boolean" "Enable CPU optimizations"
create_config() {
    local -n config_ref="$1"
    local key="$2"
    local value="$3"
    local cfgtype="${4:-string}"
    local description="${5:-}"

    config_ref=()
    config_ref[key]="$key"
    config_ref[value]="$value"
    config_ref[cfgtype]="$cfgtype"
    config_ref[description]="$description"
}

# Create a standardized module descriptor (module_ref is used by reference in the caller)
# Usage:
#   local mod
#   create_module mod "memory" "memory_optimize.sh" "Optimizes memory settings" "true"
create_module() {
    local -n module_ref="$1"
    local id="$2"
    local file="$3"
    local description="${4:-}"
    local enabled="${5:-true}"

    module_ref=()
    module_ref[id]="$id"
    module_ref[file]="$file"
    module_ref[description]="$description"
    module_ref[enabled]="$enabled"
}

# Create a standardized validation test descriptor (test_ref is used by reference in the caller)
# Usage:
#   local test
#   create_test test "memory_test" "memory-tests.sh" "Validates memory settings" "medium"
create_test() {
    local -n test_ref="$1"
    local id="$2"
    local file="$3"
    local description="${4:-}"
    local priority="${5:-medium}"

    test_ref=()
    test_ref[id]="$id"
    test_ref[file]="$file"
    test_ref[description]="$description"
    test_ref[priority]="$priority"
}

# Create a standardized tool descriptor (tool_ref is used by reference in the caller)
# Usage:
#   local tool
#   create_tool tool "build_status" "utils/build-status.sh" "Check build status" "all,processes,docker"
create_tool() {
    local -n tool_ref="$1"
    local id="$2"
    local path="$3"
    local description="${4:-}"
    local options="${5:-}"

    tool_ref=()
    tool_ref[id]="$id"
    tool_ref[path]="$path"
    tool_ref[description]="$description"
    tool_ref[options]="$options"
}