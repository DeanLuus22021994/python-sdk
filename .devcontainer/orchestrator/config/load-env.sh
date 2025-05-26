#!/usr/bin/env bash
# shellcheck shell=bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Point to the actual env directory location
ENV_DIR="$(cd "$SCRIPT_DIR/../../env" && pwd)"

load_env_files() {
    local env_files=(
        "python.env"
        "memory.env" 
        "cpu.env"
        "storage.env"
        "build.env"
        "docker.env"
        "gpu.env"
        "swarm.env"
        "database.env"
        "system.env"
    )
    
    for env_file in "${env_files[@]}"; do
        local file_path="$ENV_DIR/$env_file"
        if [[ -f "$file_path" ]]; then
            echo "Loading environment: $env_file"
            set -a  # Export all variables
            # shellcheck source=/dev/null
            source "$file_path"
            set +a  # Stop exporting
        else
            echo "Warning: Environment file not found: $file_path"
        fi
    done
    
    echo "All environment configurations loaded"
}

load_env() {
    echo "Loading environment variables..."
    # Example environment exports
    export FOO="bar"
    export PATH="$PATH:/opt/custom/bin"
}

# Export functions for use in other scripts
export -f load_env_files
export -f load_env

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    load_env_files
    load_env
fi
