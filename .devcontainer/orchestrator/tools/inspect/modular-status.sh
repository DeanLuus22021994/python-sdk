#!/bin/bash
# Tool 005: Modular System Status
# Purpose: Comprehensive status check of the new modular architecture
# Usage: ./005-modular-status.sh [detailed|summary|validation]

check_modular_status() {
    local check_type="${1:-summary}"
    
    case "$check_type" in
        "detailed")
            show_detailed_status
            ;;
        "validation")
            run_validation_check
            ;;
        *)
            show_summary_status
            ;;
    esac
}

show_summary_status() {
    echo "=== Modular System Status Summary ==="
    
    # Docker components
    echo "Docker Components:"
    [[ -f "/workspaces/python-sdk/.devcontainer/docker/Dockerfile.main" ]] && echo "  ✓ Modular Dockerfile" || echo "  ✗ Modular Dockerfile"
    [[ -f "/workspaces/python-sdk/.devcontainer/docker-compose.modular.yml" ]] && echo "  ✓ Modular Compose" || echo "  ✗ Modular Compose"
    
    # Orchestrator modules
    echo "Orchestrator Modules:"
    local modules=(cpu-optimize memory-optimize io-optimize binary-precompile)
    for module in "${modules[@]}"; do
        [[ -f "/workspaces/python-sdk/.devcontainer/orchestrator/modules/${module}.sh" ]] && echo "  ✓ $module module" || echo "  ✗ $module module"
    done
    
    # Validation components
    echo "Validation System:"
    [[ -f "/workspaces/python-sdk/.devcontainer/validation/core/main.sh" ]] && echo "  ✓ Validation core" || echo "  ✗ Validation core"
    [[ -d "/workspaces/python-sdk/.devcontainer/validation/tests" ]] && echo "  ✓ Test modules" || echo "  ✗ Test modules"
    
    # Tools system
    echo "Development Tools:"
    local tool_count=$(find /workspaces/python-sdk/.devcontainer/tools -name "*.sh" | wc -l)
    echo "  ✓ $tool_count tools available"
}

show_detailed_status() {
    echo "=== Detailed Modular System Status ==="
    
    echo "File Size Analysis:"
    find /workspaces/python-sdk/.devcontainer -name "*.sh" -exec wc -l {} \; | \
    awk '$1 > 150 {print "  ⚠ " $2 " (" $1 " lines - needs decomposition)"}
         $1 <= 150 {print "  ✓ " $2 " (" $1 " lines)"}' | sort
    
    echo -e "\nDocker Structure:"
    find /workspaces/python-sdk/.devcontainer/docker -type f | sed 's|^|  |'
    
    echo -e "\nOrchestrator Structure:"
    find /workspaces/python-sdk/.devcontainer/orchestrator -type f | sed 's|^|  |'
    
    echo -e "\nValidation Structure:"
    find /workspaces/python-sdk/.devcontainer/validation -type f | sed 's|^|  |'
}

run_validation_check() {
    echo "=== Running Modular System Validation ==="
    
    # Test orchestrator
    if [[ -x "/workspaces/python-sdk/.devcontainer/master-orchestrator.modular.sh" ]]; then
        echo "Testing modular orchestrator..."
        bash /workspaces/python-sdk/.devcontainer/master-orchestrator.modular.sh --dry-run --list
    fi
    
    # Test validation system
    if [[ -x "/workspaces/python-sdk/.devcontainer/validation/core/main.sh" ]]; then
        echo "Testing validation system..."
        bash /workspaces/python-sdk/.devcontainer/validation/core/main.sh 2>/dev/null || echo "Validation test completed"
    fi
}

check_modular_status "$@"
