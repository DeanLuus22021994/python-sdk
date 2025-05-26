#!/usr/bin/env bash
# shellcheck shell=bash
# shellcheck source="../utils/logging.sh"
# shellcheck source="./validator.sh"
# shellcheck source="./sequential.sh"
# shellcheck source="./parallel.sh"
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Import needed scripts
source "$SCRIPT_DIR/../utils/logging.sh"
source "$SCRIPT_DIR/validator.sh"
source "$SCRIPT_DIR/sequential.sh"
source "$SCRIPT_DIR/parallel.sh"

main() {
    log_info "Starting orchestrator main procedure..."
    run_sequential
    run_parallel
    validate_system
    log_info "Main procedure completed."
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
