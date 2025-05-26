#!/bin/bash
# DevContainer Orchestrator Constants
# Centralized constants for the entire orchestrator system

# shellcheck disable=SC2034  # Variables are used by sourcing scripts

# ====== PATH CONSTANTS ======
# Base paths
if [[ -z "${DEVCONTAINER_DIR:-}" ]]; then
    DEVCONTAINER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
    readonly DEVCONTAINER_DIR
fi
readonly CONFIG_DIR="$DEVCONTAINER_DIR/config"
readonly ORCHESTRATOR_DIR="$DEVCONTAINER_DIR/orchestrator"
readonly VALIDATION_DIR="$DEVCONTAINER_DIR/validation"

# Config paths
readonly ENV_DIR="$CONFIG_DIR/env"
readonly SETUP_DIR="$CONFIG_DIR/setup"

# Orchestrator paths
readonly CORE_DIR="$ORCHESTRATOR_DIR/core"
readonly MODULES_DIR="$ORCHESTRATOR_DIR/modules"
readonly UTILS_DIR="$ORCHESTRATOR_DIR/utils"
readonly LIFECYCLE_DIR="$ORCHESTRATOR_DIR/lifecycle"
readonly TOOLS_DIR="$ORCHESTRATOR_DIR/tools"
readonly TYPES_DIR="$ORCHESTRATOR_DIR/types"

# Validation paths
readonly VALIDATION_CORE_DIR="$VALIDATION_DIR/core"
readonly VALIDATION_TESTS_DIR="$VALIDATION_DIR/tests"

# ====== COLOR CONSTANTS ======
readonly COLOR_RED='\033[0;31m'
readonly COLOR_GREEN='\033[0;32m'
readonly COLOR_YELLOW='\033[1;33m'
readonly COLOR_BLUE='\033[0;34m'
readonly COLOR_PURPLE='\033[0;35m'
readonly COLOR_CYAN='\033[0;36m'
readonly COLOR_GRAY='\033[0;37m'
readonly COLOR_BOLD='\033[1m'
readonly COLOR_RESET='\033[0m'

# ====== STATUS CONSTANTS ======
readonly STATUS_SUCCESS=0
readonly STATUS_ERROR=1
readonly STATUS_WARNING=2

# ====== ENVIRONMENT CONSTANTS ======
readonly DEFAULT_OPTIMIZATION_LEVEL=2
readonly DEFAULT_MEMORY_ALLOCATOR="jemalloc"
readonly DEFAULT_CPU_GOVERNOR="performance"

# ====== EXECUTION CONSTANTS ======
MAX_PARALLEL_PROCESSES=$(nproc 2>/dev/null || echo 4)
readonly MAX_PARALLEL_PROCESSES
readonly DEFAULT_TIMEOUT=30
readonly RETRY_COUNT=3
readonly RETRY_DELAY=2

# ====== MESSAGE CONSTANTS ======
readonly MSG_PREFIX="[MCP-DevContainer]"
readonly MSG_SUCCESS="✅ Success:"
readonly MSG_ERROR="❌ Error:"
readonly MSG_WARNING="⚠️ Warning:"
readonly MSG_INFO="ℹ️ Info:"
readonly MSG_DEBUG="🔍 Debug:"
