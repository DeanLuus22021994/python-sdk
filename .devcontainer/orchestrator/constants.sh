#!/usr/bin/env bash
# shellcheck shell=bash
#
# DevContainer Orchestrator Constants
# Centralized constants for the entire orchestrator system

# ====== PATH CONSTANTS ======
if [[ -z "${DEVCONTAINER_DIR:-}" ]]; then
    DEVCONTAINER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
    export DEVCONTAINER_DIR
fi

if [[ -z "${CONFIG_DIR:-}" ]]; then
    CONFIG_DIR="$DEVCONTAINER_DIR/config"
    export CONFIG_DIR
fi

if [[ -z "${ORCHESTRATOR_DIR:-}" ]]; then
    ORCHESTRATOR_DIR="$DEVCONTAINER_DIR/orchestrator"
    export ORCHESTRATOR_DIR
fi

if [[ -z "${VALIDATION_DIR:-}" ]]; then
    VALIDATION_DIR="$DEVCONTAINER_DIR/validation"
    export VALIDATION_DIR
fi

if [[ -z "${ENV_DIR:-}" ]]; then
    ENV_DIR="$CONFIG_DIR/env"
    export ENV_DIR
fi

if [[ -z "${SETUP_DIR:-}" ]]; then
    SETUP_DIR="$CONFIG_DIR/setup"
    export SETUP_DIR
fi

if [[ -z "${CORE_DIR:-}" ]]; then
    CORE_DIR="$ORCHESTRATOR_DIR/core"
    export CORE_DIR
fi

if [[ -z "${MODULES_DIR:-}" ]]; then
    MODULES_DIR="$ORCHESTRATOR_DIR/modules"
    export MODULES_DIR
fi

if [[ -z "${UTILS_DIR:-}" ]]; then
    UTILS_DIR="$ORCHESTRATOR_DIR/utils"
    export UTILS_DIR
fi

if [[ -z "${LIFECYCLE_DIR:-}" ]]; then
    LIFECYCLE_DIR="$ORCHESTRATOR_DIR/lifecycle"
    export LIFECYCLE_DIR
fi

if [[ -z "${TOOLS_DIR:-}" ]]; then
    TOOLS_DIR="$ORCHESTRATOR_DIR/tools"
    export TOOLS_DIR
fi

if [[ -z "${TYPES_DIR:-}" ]]; then
    TYPES_DIR="$ORCHESTRATOR_DIR/types"
    export TYPES_DIR
fi

if [[ -z "${VALIDATION_CORE_DIR:-}" ]]; then
    VALIDATION_CORE_DIR="$VALIDATION_DIR/core"
    export VALIDATION_CORE_DIR
fi

if [[ -z "${VALIDATION_TESTS_DIR:-}" ]]; then
    VALIDATION_TESTS_DIR="$VALIDATION_DIR/tests"
    export VALIDATION_TESTS_DIR
fi

# ====== COLOR CONSTANTS ======
if [[ -z "${COLOR_RED:-}" ]]; then
    COLOR_RED='\033[0;31m'
    export COLOR_RED
fi

if [[ -z "${COLOR_GREEN:-}" ]]; then
    COLOR_GREEN='\033[0;32m'
    export COLOR_GREEN
fi

if [[ -z "${COLOR_YELLOW:-}" ]]; then
    COLOR_YELLOW='\033[1;33m'
    export COLOR_YELLOW
fi

if [[ -z "${COLOR_BLUE:-}" ]]; then
    COLOR_BLUE='\033[0;34m'
    export COLOR_BLUE
fi

if [[ -z "${COLOR_PURPLE:-}" ]]; then
    COLOR_PURPLE='\033[0;35m'
    export COLOR_PURPLE
fi

if [[ -z "${COLOR_CYAN:-}" ]]; then
    COLOR_CYAN='\033[0;36m'
    export COLOR_CYAN
fi

if [[ -z "${COLOR_GRAY:-}" ]]; then
    COLOR_GRAY='\033[0;37m'
    export COLOR_GRAY
fi

if [[ -z "${COLOR_BOLD:-}" ]]; then
    COLOR_BOLD='\033[1m'
    export COLOR_BOLD
fi

if [[ -z "${COLOR_RESET:-}" ]]; then
    COLOR_RESET='\033[0m'
    export COLOR_RESET
fi

# ====== STATUS CONSTANTS ======
if [[ -z "${STATUS_SUCCESS:-}" ]]; then
    STATUS_SUCCESS=0
    export STATUS_SUCCESS
fi

if [[ -z "${STATUS_ERROR:-}" ]]; then
    STATUS_ERROR=1
    export STATUS_ERROR
fi

if [[ -z "${STATUS_WARNING:-}" ]]; then
    STATUS_WARNING=2
    export STATUS_WARNING
fi

# ====== ENVIRONMENT CONSTANTS ======
if [[ -z "${DEFAULT_OPTIMIZATION_LEVEL:-}" ]]; then
    DEFAULT_OPTIMIZATION_LEVEL=2
    export DEFAULT_OPTIMIZATION_LEVEL
fi

if [[ -z "${DEFAULT_MEMORY_ALLOCATOR:-}" ]]; then
    DEFAULT_MEMORY_ALLOCATOR="jemalloc"
    export DEFAULT_MEMORY_ALLOCATOR
fi

if [[ -z "${DEFAULT_CPU_GOVERNOR:-}" ]]; then
    DEFAULT_CPU_GOVERNOR="performance"
    export DEFAULT_CPU_GOVERNOR
fi

# ====== EXECUTION CONSTANTS ======
if [[ -z "${MAX_PARALLEL_PROCESSES:-}" ]]; then
    MAX_PARALLEL_PROCESSES="$(nproc 2>/dev/null || echo 4)"
    export MAX_PARALLEL_PROCESSES
fi

if [[ -z "${DEFAULT_TIMEOUT:-}" ]]; then
    DEFAULT_TIMEOUT=30
    export DEFAULT_TIMEOUT
fi

if [[ -z "${RETRY_COUNT:-}" ]]; then
    RETRY_COUNT=3
    export RETRY_COUNT
fi

if [[ -z "${RETRY_DELAY:-}" ]]; then
    RETRY_DELAY=2
    export RETRY_DELAY
fi

# ====== MESSAGE CONSTANTS ======
if [[ -z "${MSG_PREFIX:-}" ]]; then
    MSG_PREFIX="[MCP-DevContainer]"
    export MSG_PREFIX
fi

if [[ -z "${MSG_SUCCESS:-}" ]]; then
    MSG_SUCCESS="✅ Success:"
    export MSG_SUCCESS
fi

if [[ -z "${MSG_ERROR:-}" ]]; then
    MSG_ERROR="❌ Error:"
    export MSG_ERROR
fi

if [[ -z "${MSG_WARNING:-}" ]]; then
    MSG_WARNING="⚠️ Warning:"
    export MSG_WARNING
fi

if [[ -z "${MSG_INFO:-}" ]]; then
    MSG_INFO="ℹ️ Info:"
    export MSG_INFO
fi

if [[ -z "${MSG_DEBUG:-}" ]]; then
    MSG_DEBUG="🔍 Debug:"
    export MSG_DEBUG
fi