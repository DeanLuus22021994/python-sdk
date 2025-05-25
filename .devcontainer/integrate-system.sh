#!/bin/bash
# System Integration Script
# Integrates all modular components into a cohesive high-performance system

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/.env"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $*${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $*${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $*${NC}"
}

# System Integration Functions
integrate_tools() {
    log "Integrating development tools system..."
    
    # Ensure tools are executable
    find "$SCRIPT_DIR/tools" -name "*.sh" -exec chmod +x {} \;
    
    # Add tools to PATH for easy access
    if ! grep -q "tools" ~/.bashrc 2>/dev/null; then
        echo 'export PATH="$PATH:/workspaces/python-sdk/.devcontainer/tools"' >> ~/.bashrc
        echo 'source /workspaces/python-sdk/.devcontainer/tools/dt.sh' >> ~/.bashrc
    fi
    
    log "Tools system integrated successfully"
}

integrate_docker_swarm() {
    log "Preparing Docker Swarm integration..."
    
    # Check if swarm is initialized
    if ! docker info --format '{{.Swarm.LocalNodeState}}' | grep -q "active"; then
        warn "Docker Swarm not initialized. Initialize with: docker swarm init"
    fi
    
    # Validate swarm configuration
    if [[ -f "$SCRIPT_DIR/docker/swarm/docker-stack.yml" ]]; then
        log "Docker Swarm stack configuration available"
        log "Deploy with: docker stack deploy -c docker/swarm/docker-stack.yml mcp-stack"
    fi
}

integrate_gpu_passthrough() {
    log "Integrating GPU passthrough system..."
    
    # Run GPU detection and setup
    if [[ -f "$SCRIPT_DIR/scripts/setup/gpu-passthrough.sh" ]]; then
        bash "$SCRIPT_DIR/scripts/setup/gpu-passthrough.sh"
    fi
}

validate_integration() {
    log "Validating system integration..."
    
    local errors=0
    
    # Check critical files
    for file in ".env" "master-orchestrator.sh" "tools/index.sh"; do
        if [[ ! -f "$SCRIPT_DIR/$file" ]]; then
            error "Missing critical file: $file"
            ((errors++))
        fi
    done
    
    # Check directory structure
    for dir in "scripts" "docker" "config" "tools"; do
        if [[ ! -d "$SCRIPT_DIR/$dir" ]]; then
            error "Missing directory: $dir"
            ((errors++))
        fi
    done
    
    # Check script executability
    if [[ ! -x "$SCRIPT_DIR/master-orchestrator.sh" ]]; then
        error "Master orchestrator is not executable"
        ((errors++))
    fi
    
    if [[ $errors -eq 0 ]]; then
        log "System integration validation passed"
        return 0
    else
        error "System integration validation failed with $errors errors"
        return 1
    fi
}

# Main integration workflow
main() {
    log "Starting MCP Python SDK system integration..."
    
    integrate_tools
    integrate_docker_swarm
    integrate_gpu_passthrough
    
    if validate_integration; then
        log "System integration completed successfully!"
        log "Available commands:"
        echo "  - dt list                    # Show all development tools"
        echo "  - ./master-orchestrator.sh   # Run performance optimization"
        echo "  - ./tools/index.sh 001       # Check devcontainer state"
        
        # Record integration metrics
        if [[ -x "$SCRIPT_DIR/tools/metrics/003-dev-metrics.sh" ]]; then
            bash "$SCRIPT_DIR/tools/metrics/003-dev-metrics.sh" record
        fi
    else
        error "System integration failed!"
        exit 1
    fi
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
