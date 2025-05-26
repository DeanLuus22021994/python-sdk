#!/bin/bash
# DevContainer Orchestrator Types
# Centralized type definitions for bash scripts

SCRIPT_DIR=""
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# shellcheck source=constants.sh
if [[ -r "$SCRIPT_DIR/constants.sh" ]]; then
    source "$SCRIPT_DIR/constants.sh"
else
    echo "Error: cannot find or read $SCRIPT_DIR/constants.sh"
    exit 1
fi

# Create a standardized result structure
# Usage:
#   local result
#   create_result result "success" "Operation completed" 0
#   echo "${result[status]}"
create_result() {
    # Use nameref so that the array is updated in the caller
    local -n result_ref="$1"
    local status="$2"
    local message="$3"
    local code="${4:-0}"
    local data="${5:-}"
    local timestamp=""

    timestamp="$(date +%s)"

    # Reinitialize the array in the caller by name
    # This array remains in the caller's scope (hence, not directly referenced here again).
    result_ref=()
    result_ref[status]="$status"      # e.g. "success", "error", "warning"
    result_ref[message]="$message"    # Human-readable message
    result_ref[code]="$code"          # Numeric code
    result_ref[data]="$data"          # Optional data payload
    result_ref[timestamp]="$timestamp"
}

# Create a standardized config structure
# Usage:
#   local cfg
#   create_config cfg "memory_optimization" "true" "boolean" "Enable CPU optimizations"
create_config() {
    local -n config_ref="$1"
    local key="$2"
    local value="$3"
    local cfgtype="${4:-string}"   # string, boolean, number, array
    local description="${5:-}"

    # This array remains in the caller's scope.
    config_ref=()
    config_ref[key]="$key"
    config_ref[value]="$value"
    config_ref[cfgtype]="$cfgtype"
    config_ref[description]="$description"
}

# Create a standardized module descriptor
# Usage:
#   local mod
#   create_module mod "memory" "memory_optimize.sh" "Optimizes memory settings" "true"
create_module() {
    local -n module_ref="$1"
    local id="$2"
    local file="$3"
    local description="${4:-}"
    local enabled="${5:-true}"

    # This array remains in the caller's scope.
    module_ref=()
    module_ref[id]="$id"
    module_ref[file]="$file"
    module_ref[description]="$description"
    module_ref[enabled]="$enabled"
}

# Create a standardized validation test descriptor
# Usage:
#   local test
#   create_test test "memory_test" "memory-tests.sh" "Validates memory settings" "medium"
create_test() {
    local -n test_ref="$1"
    local id="$2"
    local file="$3"
    local description="${4:-}"
    local priority="${5:-medium}"

    # This array remains in the caller's scope.
    test_ref=()
    test_ref[id]="$id"
    test_ref[file]="$file"
    test_ref[description]="$description"
    test_ref[priority]="$priority"
}

# Create a standardized tool descriptor
# Usage:
#   local tool
#   create_tool tool "build_status" "utils/build-status.sh" "Check build status" "all,processes,docker"
create_tool() {
    local -n tool_ref="$1"
    local id="$2"
    local path="$3"
    local description="${4:-}"
    local options="${5:-}"

    # This array remains in the caller's scope.
    tool_ref=()
    tool_ref[id]="$id"
    tool_ref[path]="$path"
    tool_ref[description]="$description"
    tool_ref[options]="$options"
}