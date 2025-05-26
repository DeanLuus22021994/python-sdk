#!/bin/bash
# DevContainer Orchestrator Registry
# Central registry for all modules, tools, and validation tests

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# shellcheck source=./constants.sh
if [[ -r "$SCRIPT_DIR/constants.sh" ]]; then
    source "$SCRIPT_DIR/constants.sh"
else
    echo "Error: cannot find or read $SCRIPT_DIR/constants.sh"
    exit 1
fi

# shellcheck source=./types.sh
if [[ -r "$SCRIPT_DIR/types.sh" ]]; then
    source "$SCRIPT_DIR/types.sh"
else
    echo "Error: cannot find or read $SCRIPT_DIR/types.sh"
    exit 1
fi

# shellcheck source=./utils.sh
if [[ -r "$SCRIPT_DIR/utils.sh" ]]; then
    source "$SCRIPT_DIR/utils.sh"
else
    echo "Error: cannot find or read $SCRIPT_DIR/utils.sh"
    exit 1
fi

# Initialize registries
declare -a MODULE_REGISTRY=()  # Used to store module descriptors
declare -a TOOL_REGISTRY=()    # Used to store tool descriptors
declare -a TEST_REGISTRY=()    # Used to store validation test descriptors

register_modules() {
    local module_data

    # CPU optimization module
    create_module module_data "cpu" "$MODULES_DIR/cpu-optimize.sh" "CPU performance optimizations" "true"
    MODULE_REGISTRY+=("$(declare -p module_data)")

    # Memory optimization module
    create_module module_data "memory" "$MODULES_DIR/memory-optimize.sh" "Memory performance optimizations" "true"
    MODULE_REGISTRY+=("$(declare -p module_data)")

    # I/O optimization module
    create_module module_data "io" "$MODULES_DIR/io-optimize.sh" "I/O performance optimizations" "true"
    MODULE_REGISTRY+=("$(declare -p module_data)")

    # Binary precompilation module
    create_module module_data "binary" "$MODULES_DIR/binary-precompile.sh" "Python binary precompilation" "true"
    MODULE_REGISTRY+=("$(declare -p module_data)")
}

register_tools() {
    local tool_data

    # Development tools
    create_tool tool_data "dt" "$TOOLS_DIR/dt.sh" "Development Tools Hub" "list,info,help"
    TOOL_REGISTRY+=("$(declare -p tool_data)")

    # Build status
    create_tool tool_data "build-status" "$TOOLS_DIR/utils/build-status.sh" "Check build status" "all,processes,docker,performance"
    TOOL_REGISTRY+=("$(declare -p tool_data)")

    # DevContainer state
    create_tool tool_data "devcontainer-state" "$TOOLS_DIR/inspect/devcontainer-state.sh" "Show DevContainer state" "json,table,summary"
    TOOL_REGISTRY+=("$(declare -p tool_data)")

    # Modular status
    create_tool tool_data "modular-status" "$TOOLS_DIR/inspect/modular-status.sh" "Show modular architecture status" "detailed,summary,validation"
    TOOL_REGISTRY+=("$(declare -p tool_data)")

    # Dev metrics
    create_tool tool_data "dev-metrics" "$TOOLS_DIR/metrics/dev-metrics.sh" "Development metrics" "record,report,benchmark"
    TOOL_REGISTRY+=("$(declare -p tool_data)")

    # System migration
    create_tool tool_data "migrate-system" "$TOOLS_DIR/utils/migrate-system.sh" "Migrate build system" "check,migrate,rollback"
    TOOL_REGISTRY+=("$(declare -p tool_data)")
}

register_tests() {
    local test_data

    # CPU tests
    create_test test_data "cpu" "$VALIDATION_TESTS_DIR/cpu-tests.sh" "CPU configuration tests" "high"
    TEST_REGISTRY+=("$(declare -p test_data)")

    # Memory tests
    create_test test_data "memory" "$VALIDATION_TESTS_DIR/memory-tests.sh" "Memory configuration tests" "high"
    TEST_REGISTRY+=("$(declare -p test_data)")

    # I/O tests
    create_test test_data "io" "$VALIDATION_TESTS_DIR/io-tests.sh" "I/O configuration tests" "medium"
    TEST_REGISTRY+=("$(declare -p test_data)")

    # Python tests
    create_test test_data "python" "$VALIDATION_TESTS_DIR/python-tests.sh" "Python configuration tests" "high"
    TEST_REGISTRY+=("$(declare -p test_data)")

    # Configuration validation
    create_test test_data "config" "$VALIDATION_TESTS_DIR/config-validation.sh" "Config validation tests" "medium"
    TEST_REGISTRY+=("$(declare -p test_data)")

    # Performance validation
    create_test test_data "performance" "$VALIDATION_TESTS_DIR/performance-validator.sh" "Performance validation tests" "low"
    TEST_REGISTRY+=("$(declare -p test_data)")
}

get_module() {
    local module_id="$1"
    for module_decl in "${MODULE_REGISTRY[@]}"; do
        local -A module
        eval "$module_decl"
        if [[ "${module[id]}" == "$module_id" ]]; then
            echo "$module_decl"
            return 0
        fi
    done
    return 1
}

get_tool() {
    local tool_id="$1"
    for tool_decl in "${TOOL_REGISTRY[@]}"; do
        local -A tool
        eval "$tool_decl"
        if [[ "${tool[id]}" == "$tool_id" ]]; then
            echo "$tool_decl"
            return 0
        fi
    done
    return 1
}

get_test() {
    local test_id="$1"
    for test_decl in "${TEST_REGISTRY[@]}"; do
        local -A test
        eval "$test_decl"
        if [[ "${test[id]}" == "$test_id" ]]; then
            echo "$test_decl"
            return 0
        fi
    done
    return 1
}

list_modules() {
    for module_decl in "${MODULE_REGISTRY[@]}"; do
        local -A module
        eval "$module_decl"
        echo "ID: ${module[id]}, File: ${module[file]}, Desc: ${module[description]}, Enabled: ${module[enabled]}"
    done
}

list_tools() {
    for tool_decl in "${TOOL_REGISTRY[@]}"; do
        local -A tool
        eval "$tool_decl"
        echo "ID: ${tool[id]}, Path: ${tool[path]}, Desc: ${tool[description]}, Options: ${tool[options]}"
    done
}

list_tests() {
    for test_decl in "${TEST_REGISTRY[@]}"; do
        local -A test
        eval "$test_decl"
        echo "ID: ${test[id]}, File: ${test[file]}, Desc: ${test[description]}, Priority: ${test[priority]}"
    done
}

# Initialize registries immediately upon sourcing
register_modules
register_tools
register_tests