#!/bin/bash
# DevContainer Orchestrator Utilities
# Common utility functions used across the orchestrator system

SCRIPT_DIR=""
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ -r "$SCRIPT_DIR/constants.sh" ]]; then
    source "$SCRIPT_DIR/constants.sh"
else
    echo "Error: cannot find or read $SCRIPT_DIR/constants.sh"
    exit 1
fi

if [[ -r "$SCRIPT_DIR/types.sh" ]]; then
    source "$SCRIPT_DIR/types.sh"
else
    echo "Error: cannot find or read $SCRIPT_DIR/types.sh"
    exit 1
fi

# ====== STRING UTILITIES ======
to_lowercase() {
    printf "%s" "$1" | tr '[:upper:]' '[:lower:]'
}

to_uppercase() {
    printf "%s" "$1" | tr '[:lower:]' '[:upper:]'
}

strip_whitespace() {
    # Remove leading and trailing whitespace
    sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//'
}

contains_string() {
    local string="$1"
    local substring="$2"
    case "$string" in
        *"$substring"*) return 0 ;;
        *) return 1 ;;
    esac
}

string_length() {
    printf "%d" "${#1}"
}

# ====== FILE UTILITIES ======
is_file_readable() {
    [[ -f "$1" && -r "$1" ]]
}

is_dir_writable() {
    [[ -d "$1" && -w "$1" ]]
}

ensure_directory() {
    local dir="$1"
    if [[ ! -d "$dir" ]]; then
        mkdir -p "$dir" || return $?
    fi
}

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
join_array() {
    local separator="$1"
    shift
    local IFS="$separator"
    echo "$*"
}

array_contains() {
    local element="$1"
    shift
    local item
    for item in "$@"; do
        if [[ "$item" == "$element" ]]; then
            return 0
        fi
    done
    return 1
}

array_length() {
    printf "%d" "$#"
}

# ====== VALIDATION UTILITIES ======
is_set() {
    [[ -n "${1+x}" ]]
}

is_integer() {
    [[ "$1" =~ ^-?[0-9]+$ ]]
}

is_float() {
    [[ "$1" =~ ^-?[0-9]+(\.[0-9]+)?$ ]]
}

is_ip_address() {
    [[ "$1" =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]
}

is_hostname() {
    [[ "$1" =~ ^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$ ]]
}

# ====== SYSTEM UTILITIES ======
get_system_memory() {
    local mem=""
    mem="$(free -m | awk '/Mem:/ {print $2}' 2>/dev/null || true)"
    printf "%s" "${mem:-0}"
}

get_cpu_count() {
    nproc 2>/dev/null || \
    grep -c processor /proc/cpuinfo 2>/dev/null || \
    sysctl -n hw.ncpu 2>/dev/null || \
    echo "1"
}

get_load_average() {
    # Parsable 1-minute load average
    uptime | awk -F'[a-z]:' '{ print $2 }' | awk -F',' '{ print $1 }' | tr -d ' '
}

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# ====== TIME UTILITIES ======
get_timestamp() {
    date +%s
}

format_timestamp() {
    date -d "@$1" "+%Y-%m-%d %H:%M:%S" 2>/dev/null || date -r "$1" "+%Y-%m-%d %H:%M:%S" 2>/dev/null
}

time_diff() {
    if [[ $# -lt 2 ]]; then
        echo 0
    else
        echo $(( "$2" - "$1" ))
    fi
}

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
run_with_timeout() {
    local timeout_val="$1"
    shift

    if command_exists timeout; then
        timeout "$timeout_val" "$@"
        return $?
    fi

    local pid=""
    "$@" &
    pid=$!

    (
        sleep "$timeout_val"
        kill -TERM "$pid" 2>/dev/null || true
    ) &
    local timer_pid=$!

    wait "$pid" 2>/dev/null
    local exit_code=$?

    kill -TERM "$timer_pid" 2>/dev/null || true
    return $exit_code
}

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