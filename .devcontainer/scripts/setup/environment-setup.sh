#!/bin/bash
# Environment Setup
# Sets up the complete development environment with all dependencies

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../../config/load-env.sh"

setup_python_environment() {
    echo "Setting up Python environment..."
    
    # Ensure Python 3.12+ is available
    if ! command -v python3.12 &> /dev/null; then
        echo "Installing Python 3.12..."
        apt-get update && apt-get install -y python3.12 python3.12-dev python3.12-venv
    fi
    
    # Install uv for fast package management
    if ! command -v uv &> /dev/null; then
        echo "Installing uv package manager..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        source ~/.cargo/env
    fi
    
    # Install project dependencies
    echo "Installing project dependencies..."
    uv sync --all-extras
}

setup_docker_environment() {
    echo "Setting up Docker environment..."
    
    # Ensure Docker is running
    if ! docker info &> /dev/null; then
        echo "Starting Docker daemon..."
        service docker start || systemctl start docker
    fi
    
    # Initialize Docker Swarm if not already initialized
    if ! docker info --format '{{.Swarm.LocalNodeState}}' | grep -q active; then
        echo "Initializing Docker Swarm..."
        docker swarm init --advertise-addr $(hostname -I | awk '{print $1}')
    fi
    
    # Create external volumes
    echo "Creating external volumes..."
    docker volume create mcp-cache 2>/dev/null || true
    docker volume create python-wheels 2>/dev/null || true
    docker volume create postgres-data 2>/dev/null || true
    docker volume create redis-data 2>/dev/null || true
}

setup_gpu_support() {
    echo "Setting up GPU support..."
    
    # Install NVIDIA Container Toolkit if NVIDIA GPU is detected
    if command -v nvidia-smi &> /dev/null; then
        echo "NVIDIA GPU detected, setting up NVIDIA Container Toolkit..."
        distribution=$(. /etc/os-release;echo "$ID$VERSION_ID")
        curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
        curl -s -L "https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list" | \
            sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
            tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
        apt-get update && apt-get install -y nvidia-container-toolkit
        nvidia-ctk runtime configure --runtime=docker
        systemctl restart docker
    fi
}

main() {
    echo "=== MCP Python SDK Environment Setup ==="
    
    load_env_files
    
    setup_python_environment
    setup_docker_environment
    setup_gpu_support
    
    echo "Environment setup completed successfully!"
    echo "You can now run: ./master-orchestrator.modular.sh"
}

main "$@"
