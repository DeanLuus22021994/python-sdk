#!/bin/bash
# DevContainer Orchestrator Types
# Centralized type definitions for bash scripts

# shellcheck disable=SC2034  # Variables are used via nameref by calling functions

# Import constants
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./constants.sh
source "$SCRIPT_DIR/constants.sh"

# ====== RESULT TYPE DEFINITION ======
# Define a standardized result structure
# Usage: 
#   local result
#   create_result result "success" "Operation completed" 0
#   echo "${result[status]}"  # Prints "success"
create_result() {
    local -n result_ref="$1"
    local status="$2"
    local message="$3"
    local code="${4:-0}"
    local data="${5:-}"
    local timestamp
    timestamp="$(date +%s)"
    
    result_ref=()
    result_ref[status]="$status"     # success, error, warning
    result_ref[message]="$message"   # Human-readable message
    result_ref[code]="$code"         # Numeric code
    result_ref[data]="$data"         # Optional data payload
    result_ref[timestamp]="$timestamp"
}

# ====== CONFIG TYPE DEFINITION ======
# Define a standardized config structure
# Usage:
#   local config
#   create_config config "memory_optimization" "true" "boolean" "Enable memory optimizations"
create_config() {
    local -n config_ref="$1"
    local key="$2"
    local value="$3"
    local type="${4:-string}"  # string, boolean, number, array
    local description="${5:-}"
    
    config_ref=()
    config_ref[key]="$key"
    config_ref[value]="$value"
    config_ref[type]="$type"
    config_ref[description]="$description"
}

# ====== MODULE TYPE DEFINITION ======
# Define a standardized module descriptor
# Usage:
#   local module
#   create_module module "memory" "memory_optimize.sh" "Optimizes memory settings" "true"
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

# ====== VALIDATION TEST TYPE DEFINITION ======
# Define a standardized validation test descriptor
# Usage:
#   local test
#   create_test test "memory_test" "memory-tests.sh" "Validates memory settings" "medium"
create_test() {
    local -n test_ref="$1"
    local id="$2"
    local file="$3"
    local description="${4:-}"
    local priority="${5:-medium}"  # high, medium, low
    
    test_ref=()
    test_ref[id]="$id"
    test_ref[file]="$file"
    test_ref[description]="$description"
    test_ref[priority]="$priority"
}

# ====== TOOL TYPE DEFINITION ======
# Define a standardized tool descriptor
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
