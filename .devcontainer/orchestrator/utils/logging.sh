#!/bin/bash
# Logging Utilities - Centralized logging functions
# Provides consistent logging across all orchestrator components

# shellcheck disable=SC2034  # Variables are used by sourcing scripts

# Color codes for output
declare -g RED='\033[0;31m'
declare -g GREEN='\033[0;32m'
declare -g YELLOW='\033[1;33m'
declare -g BLUE='\033[0;34m'
declare -g PURPLE='\033[0;35m'
declare -g CYAN='\033[0;36m'
declare -g NC='\033[0m'

# Log levels
declare -g LOG_LEVEL="${LOG_LEVEL:-INFO}"
declare -g LOG_FILE="${LOG_FILE:-/var/log/orchestrator.log}"

log() {
    local level="${1:-INFO}"
    local message="$2"
    local timestamp
    timestamp=$(date +'%Y-%m-%d %H:%M:%S')
    
    case "$level" in
        "ERROR")
            echo -e "${RED}[$timestamp] ERROR: $message${NC}" >&2
            ;;
        "WARN")
            echo -e "${YELLOW}[$timestamp] WARN: $message${NC}"
            ;;
        "INFO")
            echo -e "${GREEN}[$timestamp] INFO: $message${NC}"
            ;;
        "DEBUG")
            [[ "$LOG_LEVEL" == "DEBUG" ]] && echo -e "${BLUE}[$timestamp] DEBUG: $message${NC}"
            ;;
        *)
            echo -e "${GREEN}[$timestamp] $level${NC}"
            ;;
    esac
    
    # Write to log file if specified
    [[ -n "$LOG_FILE" ]] && echo "[$timestamp] $level: $message" >> "$LOG_FILE"
}

error() {
    log "ERROR" "$*"
}

warn() {
    log "WARN" "$*"
}

info() {
    log "INFO" "$*"
}

debug() {
    log "DEBUG" "$*"
}

# Legacy compatibility
log() {
    if [[ $# -eq 1 ]]; then
        info "$1"
    else
        log "$@"
    fi
}
