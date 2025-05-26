#!/bin/bash
# Pre-rebuild initialization script
# Ensures all prerequisites are met before devcontainer rebuild

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "=== Pre-Rebuild Initialization ==="

# Source centralized logging
# shellcheck source=/dev/null
source "$ROOT_DIR/orchestrator/utils/logging.sh"

info "Preparing for container rebuild..."

# Capture current environment state
info "Capturing current environment state..."
{
    echo "# Environment state captured on $(date)"
    echo "PYTHON_VERSION=$(python3 --version 2>/dev/null || echo 'Not installed')"
    echo "NODE_VERSION=$(node --version 2>/dev/null || echo 'Not installed')"
    echo "NPM_VERSION=$(npm --version 2>/dev/null || echo 'Not installed')"
    pip freeze 2>/dev/null | sed 's/^/PIP_PACKAGE=/'
} > "$ROOT_DIR/config/env/pre-rebuild.env"

# Check for required files
info "Checking required configuration files..."
required_files=(
    "$ROOT_DIR/config/load-env.sh"
    "$ROOT_DIR/config/env/python.env"
    "$ROOT_DIR/config/env/system.env"
)

for file in "${required_files[@]}"; do
    if [[ ! -f "$file" ]]; then
        error "Required file missing: $file"
        exit 1
    else
        info "✓ Required file exists: $(basename "$file")"
    fi
done

info "Pre-rebuild initialization completed successfully!"
info "You can now proceed with rebuilding the container."
