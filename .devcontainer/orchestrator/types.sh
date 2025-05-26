#!/bin/bash
# DevContainer Orchestrator Types
# Centralized type definitions for bash scripts

# Import constants
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/constants.sh"

# ====== RESULT TYPE DEFINITION ======
# Define a standardized result structure
# Usage: 
#   local result
#   create_result result "success" "Operation completed" 0
#   echo "${result[status]}"  # Prints "success"
create_result() {
    # shellcheck disable=SC2034  # Used by reference in caller
    local -n result_ref="$1"
    local status="$2"
    local message="$3"
    local code="${4:-0}"
    local data="${5:-}"
    local timestamp
    timestamp="$(date +%s)"
    
    # shellcheck disable=SC2034
    result_ref=()
    # shellcheck disable=SC2034
    result_ref[status]="$status"     # success, error, warning
    # shellcheck disable=SC2034
    result_ref[message]="$message"   # Human-readable message
    # shellcheck disable=SC2034
    result_ref[code]="$code"         # Numeric code
    # shellcheck disable=SC2034
    result_ref[data]="$data"         # Optional data payload
    # shellcheck disable=SC2034
    result_ref[timestamp]="$timestamp"
}

# ====== CONFIG TYPE DEFINITION ======
# Define a standardized config structure
# Usage:
#   local cpu
#   create_config cpu "memory_optimization" "true" "boolean" "Enable CPU optimizations"
create_config() {
    # shellcheck disable=SC2034  # Used by reference in caller
    local -n config_ref="$1"
    local key="$2"
    local value="$3"
    local type="${4:-string}"  # string, boolean, number, array
    local description="${5:-}"
    
    # shellcheck disable=SC2034
    config_ref=()
    # shellcheck disable=SC2034
    config_ref[key]="$key"
    # shellcheck disable=SC2034
    config_ref[value]="$value"
    # shellcheck disable=SC2034
    config_ref[type]="$type"
    # shellcheck disable=SC2034
    config_ref[description]="$description"
}

# ====== MODULE TYPE DEFINITION ======
# Define a standardized module descriptor
# Usage:
#   local module
#   create_module module "memory" "memory_optimize.sh" "Optimizes memory settings" "true"
create_module() {
    # shellcheck disable=SC2034  # Used by reference in caller
    local -n module_ref="$1"
    local id="$2"
    local file="$3"
    local description="${4:-}"
    local enabled="${5:-true}"
    
    # shellcheck disable=SC2034
    module_ref=()
    # shellcheck disable=SC2034
    module_ref[id]="$id"
    # shellcheck disable=SC2034
    module_ref[file]="$file"
    # shellcheck disable=SC2034
    module_ref[description]="$description"
    # shellcheck disable=SC2034
    module_ref[enabled]="$enabled"
}

# ====== VALIDATION TEST TYPE DEFINITION ======
# Define a standardized validation test descriptor
# Usage:
#   local test
#   create_test test "memory_test" "memory-tests.sh" "Validates memory settings" "medium"
create_test() {
    # shellcheck disable=SC2034  # Used by reference in caller
    local -n test_ref="$1"
    local id="$2"
    local file="$3"
    local description="${4:-}"
    local priority="${5:-medium}"  # high, medium, low
    
    # shellcheck disable=SC2034
    test_ref=()
    # shellcheck disable=SC2034
    test_ref[id]="$id"
    # shellcheck disable=SC2034
    test_ref[file]="$file"
    # shellcheck disable=SC2034
    test_ref[description]="$description"
    # shellcheck disable=SC2034
    test_ref[priority]="$priority"
}

# ====== TOOL TYPE DEFINITION ======
# Define a standardized tool descriptor
# Usage:
#   local tool
#   create_tool tool "build_status" "utils/build-status.sh" "Check build status" "all,processes,docker"
create_tool() {
    # shellcheck disable=SC2034  # Used by reference in caller
    local -n tool_ref="$1"
    local id="$2"
    local path="$3"
    local description="${4:-}"
    local options="${5:-}"
    
    # shellcheck disable=SC2034
    tool_ref=()
    # shellcheck disable=SC2034
    tool_ref[id]="$id"
    # shellcheck disable=SC2034
    tool_ref[path]="$path"
    # shellcheck disable=SC2034
    tool_ref[description]="$description"
    # shellcheck disable=SC2034
    tool_ref[options]="$options"
}
