#!/bin/bash
# DevContainer Orchestrator Utilities
# Common utility functions used across the orchestrator system

# Import constants and types
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./constants.sh
source "$SCRIPT_DIR/constants.sh"
# shellcheck source=./types.sh
source "$SCRIPT_DIR/types.sh"

# ====== STRING UTILITIES ======

# Convert string to lowercase
to_lowercase() {
    echo "$1" | tr '[:upper:]' '[:lower:]'
}

# Convert string to uppercase
to_uppercase() {
    echo "$1" | tr '[:lower:]' '[:upper:]'
}

# Strip leading and trailing whitespace
strip_whitespace() {
    echo "$1" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//'
}

# Check if string contains substring
contains_string() {
    local string="$1"
    local substring="$2"
    [[ "$string" == *"$substring"* ]]
}

# Get string length
string_length() {
    echo "${#1}"
}

# ====== FILE UTILITIES ======

# Check if file exists and is readable
is_file_readable() {
    [[ -f "$1" && -r "$1" ]]
}

# Check if directory exists and is writable
is_dir_writable() {
    [[ -d "$1" && -w "$1" ]]
}

# Create directory if it doesn't exist
ensure_directory() {
    local dir="$1"
    if [[ ! -d "$dir" ]]; then
        mkdir -p "$dir" || return $?
    fi
}

# Get file size in bytes
get_file_size() {
    if [[ -f "$1" ]]; then
        stat --format="%s" "$1" 2>/dev/null || \
        stat -f "%z" "$1" 2>/dev/null || \
        wc -c < "$1" 2>/dev/null || \
        echo "0"
    else
        echo "0"
    fi
}

# Get file modification time as Unix timestamp
get_file_mtime() {
    if [[ -f "$1" ]]; then
        stat --format="%Y" "$1" 2>/dev/null || \
        stat -f "%m" "$1" 2>/dev/null || \
        date -r "$1" +%s 2>/dev/null || \
        echo "0"
    else
        echo "0"
    fi
}

# ====== ARRAY UTILITIES ======

# Join array elements with separator
# Usage: join_array "," "${array[@]}"
join_array() {
    local IFS="$1"
    shift
    echo "$*"
}

# Check if array contains element
# Usage: array_contains "element" "${array[@]}"
array_contains() {
    local element="$1"
    shift
    local array=("$@")
    for item in "${array[@]}"; do
        [[ "$item" == "$element" ]] && return 0
    done
    return 1
}

# Get array length
# Usage: array_length "${array[@]}"
array_length() {
    echo "$#"
}

# ====== VALIDATION UTILITIES ======

# Check if variable is set
is_set() {
    [[ -n "${1+x}" ]]
}

# Check if string is a valid integer
is_integer() {
    [[ "$1" =~ ^-?[0-9]+$ ]]
}

# Check if string is a valid floating point number
is_float() {
    [[ "$1" =~ ^-?[0-9]+([.][0-9]+)?$ ]]
}

# Check if string is a valid IP address
is_ip_address() {
    [[ "$1" =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]
}

# Check if string is a valid hostname
is_hostname() {
    [[ "$1" =~ ^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$ ]]
}

# ====== SYSTEM UTILITIES ======

# Get system memory in MB
get_system_memory() {
    local mem
    mem=$(free -m | grep Mem: | awk '{print $2}' 2>/dev/null)
    echo "${mem:-0}"
}

# Get system CPU count
get_cpu_count() {
    nproc 2>/dev/null || 
    grep -c processor /proc/cpuinfo 2>/dev/null ||
    sysctl -n hw.ncpu 2>/dev/null ||
    echo "1"
}

# Get system load average (1 minute)
get_load_average() {
    uptime | awk -F'[a-z]:' '{ print $2 }' | awk -F',' '{ print $1 }' | tr -d ' '
}

# Check if command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# ====== TIME UTILITIES ======

# Get current timestamp
get_timestamp() {
    date +%s
}

# Format timestamp as human-readable date
format_timestamp() {
    date -d "@$1" "+%Y-%m-%d %H:%M:%S" 2>/dev/null || date -r "$1" "+%Y-%m-%d %H:%M:%S" 2>/dev/null
}

# Calculate time difference in seconds
time_diff() {
    echo $(( $2 - $1 ))
}

# Format seconds as human-readable duration
format_duration() {
    local seconds="$1"
    local minutes=$(( seconds / 60 ))
    local hours=$(( minutes / 60 ))
    seconds=$(( seconds % 60 ))
    minutes=$(( minutes % 60 ))
    
    if [[ $hours -gt 0 ]]; then
        printf "%dh %dm %ds" "$hours" "$minutes" "$seconds"
    elif [[ $minutes -gt 0 ]]; then
        printf "%dm %ds" "$minutes" "$seconds"
    else
        printf "%ds" "$seconds"
    fi
}

# ====== ERROR HANDLING ======

# Execute command with timeout
# Usage: run_with_timeout 10 command arg1 arg2
run_with_timeout() {
    local timeout="$1"
    shift
    
    if command_exists timeout; then
        timeout "$timeout" "$@"
        return $?
    fi
    
    # Fallback implementation
    local pid
    "$@" &
    pid=$!
    
    (
        sleep "$timeout"
        kill -TERM "$pid" &>/dev/null || true
    ) &
    local timer_pid=$!
    
    wait "$pid" &>/dev/null
    local exit_code=$?
    
    kill -TERM "$timer_pid" &>/dev/null || true
    return $exit_code
}

# Retry command until it succeeds
# Usage: retry 3 2 command arg1 arg2
retry() {
    local attempts="$1"
    local delay="$2"
    shift 2
    
    local count=0
    until "$@"; do
        count=$((count + 1))
        if [[ $count -ge $attempts ]]; then
            return 1
        fi
        sleep "$delay"
    done
    return 0
}
