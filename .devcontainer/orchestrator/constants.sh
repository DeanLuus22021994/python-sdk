#!/bin/bash
# DevContainer Orchestrator Constants
# Centralized constants for the entire orchestrator system

# shellcheck disable=SC2034  # Variables are used by sourcing scripts

# ====== PATH CONSTANTS ======
if [[ -z "${DEVCONTAINER_DIR:-}" ]]; then DEVCONTAINER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; readonly DEVCONTAINER_DIR; fi
if [[ -z "${CONFIG_DIR:-}" ]]; then CONFIG_DIR="$DEVCONTAINER_DIR/config"; readonly CONFIG_DIR; fi
if [[ -z "${ORCHESTRATOR_DIR:-}" ]]; then ORCHESTRATOR_DIR="$DEVCONTAINER_DIR/orchestrator"; readonly ORCHESTRATOR_DIR; fi
if [[ -z "${VALIDATION_DIR:-}" ]]; then VALIDATION_DIR="$DEVCONTAINER_DIR/validation"; readonly VALIDATION_DIR; fi

if [[ -z "${ENV_DIR:-}" ]]; then ENV_DIR="$CONFIG_DIR/env"; readonly ENV_DIR; fi
if [[ -z "${SETUP_DIR:-}" ]]; then SETUP_DIR="$CONFIG_DIR/setup"; readonly SETUP_DIR; fi

if [[ -z "${CORE_DIR:-}" ]]; then CORE_DIR="$ORCHESTRATOR_DIR/core"; readonly CORE_DIR; fi
if [[ -z "${MODULES_DIR:-}" ]]; then MODULES_DIR="$ORCHESTRATOR_DIR/modules"; readonly MODULES_DIR; fi
if [[ -z "${UTILS_DIR:-}" ]]; then UTILS_DIR="$ORCHESTRATOR_DIR/utils"; readonly UTILS_DIR; fi
if [[ -z "${LIFECYCLE_DIR:-}" ]]; then LIFECYCLE_DIR="$ORCHESTRATOR_DIR/lifecycle"; readonly LIFECYCLE_DIR; fi
if [[ -z "${TOOLS_DIR:-}" ]]; then TOOLS_DIR="$ORCHESTRATOR_DIR/tools"; readonly TOOLS_DIR; fi
if [[ -z "${TYPES_DIR:-}" ]]; then TYPES_DIR="$ORCHESTRATOR_DIR/types"; readonly TYPES_DIR; fi

if [[ -z "${VALIDATION_CORE_DIR:-}" ]]; then VALIDATION_CORE_DIR="$VALIDATION_DIR/core"; readonly VALIDATION_CORE_DIR; fi
if [[ -z "${VALIDATION_TESTS_DIR:-}" ]]; then VALIDATION_TESTS_DIR="$VALIDATION_DIR/tests"; readonly VALIDATION_TESTS_DIR; fi

# ====== COLOR CONSTANTS ======
if [[ -z "${COLOR_RED:-}" ]]; then COLOR_RED='\033[0;31m'; readonly COLOR_RED; fi
if [[ -z "${COLOR_GREEN:-}" ]]; then COLOR_GREEN='\033[0;32m'; readonly COLOR_GREEN; fi
if [[ -z "${COLOR_YELLOW:-}" ]]; then COLOR_YELLOW='\033[1;33m'; readonly COLOR_YELLOW; fi
if [[ -z "${COLOR_BLUE:-}" ]]; then COLOR_BLUE='\033[0;34m'; readonly COLOR_BLUE; fi
if [[ -z "${COLOR_PURPLE:-}" ]]; then COLOR_PURPLE='\033[0;35m'; readonly COLOR_PURPLE; fi
if [[ -z "${COLOR_CYAN:-}" ]]; then COLOR_CYAN='\033[0;36m'; readonly COLOR_CYAN; fi
if [[ -z "${COLOR_GRAY:-}" ]]; then COLOR_GRAY='\033[0;37m'; readonly COLOR_GRAY; fi
if [[ -z "${COLOR_BOLD:-}" ]]; then COLOR_BOLD='\033[1m'; readonly COLOR_BOLD; fi
if [[ -z "${COLOR_RESET:-}" ]]; then COLOR_RESET='\033[0m'; readonly COLOR_RESET; fi

# ====== STATUS CONSTANTS ======
if [[ -z "${STATUS_SUCCESS:-}" ]]; then STATUS_SUCCESS=0; readonly STATUS_SUCCESS; fi
if [[ -z "${STATUS_ERROR:-}" ]]; then STATUS_ERROR=1; readonly STATUS_ERROR; fi
if [[ -z "${STATUS_WARNING:-}" ]]; then STATUS_WARNING=2; readonly STATUS_WARNING; fi

# ====== ENVIRONMENT CONSTANTS ======
if [[ -z "${DEFAULT_OPTIMIZATION_LEVEL:-}" ]]; then DEFAULT_OPTIMIZATION_LEVEL=2; readonly DEFAULT_OPTIMIZATION_LEVEL; fi
if [[ -z "${DEFAULT_MEMORY_ALLOCATOR:-}" ]]; then DEFAULT_MEMORY_ALLOCATOR="jemalloc"; readonly DEFAULT_MEMORY_ALLOCATOR; fi
if [[ -z "${DEFAULT_CPU_GOVERNOR:-}" ]]; then DEFAULT_CPU_GOVERNOR="performance"; readonly DEFAULT_CPU_GOVERNOR; fi

# ====== EXECUTION CONSTANTS ======
if [[ -z "${MAX_PARALLEL_PROCESSES:-}" ]]; then MAX_PARALLEL_PROCESSES=$(nproc 2>/dev/null || echo 4); readonly MAX_PARALLEL_PROCESSES; fi
if [[ -z "${DEFAULT_TIMEOUT:-}" ]]; then DEFAULT_TIMEOUT=30; readonly DEFAULT_TIMEOUT; fi
if [[ -z "${RETRY_COUNT:-}" ]]; then RETRY_COUNT=3; readonly RETRY_COUNT; fi
if [[ -z "${RETRY_DELAY:-}" ]]; then RETRY_DELAY=2; readonly RETRY_DELAY; fi

# ====== MESSAGE CONSTANTS ======
if [[ -z "${MSG_PREFIX:-}" ]]; then MSG_PREFIX="[MCP-DevContainer]"; readonly MSG_PREFIX; fi
if [[ -z "${MSG_SUCCESS:-}" ]]; then MSG_SUCCESS="✅ Success:"; readonly MSG_SUCCESS; fi
if [[ -z "${MSG_ERROR:-}" ]]; then MSG_ERROR="❌ Error:"; readonly MSG_ERROR; fi
if [[ -z "${MSG_WARNING:-}" ]]; then MSG_WARNING="⚠️ Warning:"; readonly MSG_WARNING; fi
if [[ -z "${MSG_INFO:-}" ]]; then MSG_INFO="ℹ️ Info:"; readonly MSG_INFO; fi
if [[ -z "${MSG_DEBUG:-}" ]]; then MSG_DEBUG="🔍 Debug:"; readonly MSG_DEBUG; fi
