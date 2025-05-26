#!/bin/bash
# Pre-Rebuild Entry Point
# Delegates to the orchestrator lifecycle system

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Call the lifecycle manager with pre-rebuild event
echo "🔄 Delegating to orchestrator lifecycle system..."
"$SCRIPT_DIR/orchestrator/lifecycle/lifecycle-manager.sh" pre-rebuild "$@"
