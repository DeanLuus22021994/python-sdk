#!/usr/bin/env bash
# shellcheck shell=bash
# shellcheck source="./constants.sh"
#
# DevContainer Orchestrator Types
# Centralized type definitions for bash scripts

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# shellcheck source="./constants.sh"
if [[ -r "$SCRIPT_DIR/constants.sh" ]]; then
    source "$SCRIPT_DIR/constants.sh"
else
    echo "Error: cannot find or read $SCRIPT_DIR/constants.sh"
    exit 1
fi

# Create a standardized result structure (result_ref is used by reference in the caller).
# This function sets array elements into result_ref but doesn't read them inside the function;
# we ensure a read at the end to indicate usage (avoiding SC2034).
create_result() {
    local -n result_ref="$1"
    local status="$2"
    local message="$3"
    local code="${4:-0}"
    local data="${5:-}"
    local timestamp

    timestamp="$(date +%s)"

    result_ref=()
    result_ref[status]="$status"
    result_ref[message]="$message"
    result_ref[code]="$code"
    result_ref[data]="$data"
    result_ref[timestamp]="$timestamp"

    # Force a read to show usage to ShellCheck (no-op).
    : "${result_ref[status]}" "${result_ref[message]}" "${result_ref[code]}" "${result_ref[data]}" "${result_ref[timestamp]}"
}

# Create a standardized config structure (config_ref is used by reference in the caller).
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

    : "${config_ref[key]}" "${config_ref[value]}" "${config_ref[cfgtype]}" "${config_ref[description]}"
}

# Create a standardized module descriptor (module_ref is used by reference in the caller).
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

    : "${module_ref[id]}" "${module_ref[file]}" "${module_ref[description]}" "${module_ref[enabled]}"
}

# Create a standardized validation test descriptor (test_ref is used by reference in the caller).
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

    : "${test_ref[id]}" "${test_ref[file]}" "${test_ref[description]}" "${test_ref[priority]}"
}

# Create a standardized tool descriptor (tool_ref is used by reference in the caller).
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

    : "${tool_ref[id]}" "${tool_ref[path]}" "${tool_ref[description]}" "${tool_ref[options]}"
}