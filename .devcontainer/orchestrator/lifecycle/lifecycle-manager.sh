#!/bin/bash
# DevContainer Lifecycle Manager
# Central entry point for all devcontainer lifecycle events

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source centralized logging
# shellcheck source=/dev/null
source "$ROOT_DIR/orchestrator/utils/logging.sh"

print_usage() {
    cat << EOF
DevContainer Lifecycle Manager

Usage: 
  $0 [event] [options]

Events:
  pre-rebuild   - Run pre-rebuild tasks
  post-rebuild  - Run post-rebuild tasks
  start         - Run container start tasks
  stop          - Run container stop tasks
  
Options:
  --quiet       - Minimal output
  --verbose     - Verbose output
  --debug       - Debug output
  
Example:
  $0 post-rebuild --verbose
EOF
}

event="${1:-}"
shift || true

case "$event" in
    "pre-rebuild")
        info "Executing pre-rebuild lifecycle hook..."
        bash "$SCRIPT_DIR/pre-rebuild.sh" "$@"
        ;;
    "post-rebuild")
        info "Executing post-rebuild lifecycle hook..."
        bash "$SCRIPT_DIR/post-rebuild.sh" "$@"
        ;;
    "start")
        info "Executing container start lifecycle hook..."
        # This will be implemented later
        echo "Container start hooks are not implemented yet"
        ;;
    "stop")
        info "Executing container stop lifecycle hook..."
        # This will be implemented later
        echo "Container stop hooks are not implemented yet"
        ;;
    "help"|"-h"|"--help")
        print_usage
        ;;
    *)
        error "Unknown lifecycle event: $event"
        print_usage
        exit 1
        ;;
esac
