#!/usr/bin/env bash
# shellcheck shell=bash
# Dependencies Installer
# Installs all required system and Python dependencies

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

install_system_dependencies() {
    echo "Installing system dependencies..."
    
    apt-get update
    apt-get install -y \
        build-essential \
        cmake \
        ninja-build \
        pkg-config \
        libssl-dev \
        libffi-dev \
        libbz2-dev \
        libreadline-dev \
        libsqlite3-dev \
        libncurses5-dev \
        libncursesw5-dev \
        xz-utils \
        tk-dev \
        libxml2-dev \
        libxmlsec1-dev \
        libffi-dev \
        liblzma-dev \
        curl \
        wget \
        git \
        htop \
        nvtop \
        iotop \
        sysstat \
        perf-tools-unstable \
        linux-tools-generic
}

install_performance_tools() {
    echo "Installing performance monitoring tools..."
    
    apt-get install -y \
        perf \
        valgrind \
        strace \
        tcpdump \
        iperf3 \
        sysbench \
        fio \
        stress-ng
}

install_gpu_tools() {
    echo "Installing GPU monitoring tools..."
    
    # Install NVIDIA tools if GPU is detected
    if lspci | grep -i nvidia; then
        apt-get install -y nvidia-utils-535 || apt-get install -y nvidia-utils-* || true
    fi
    
    # Install AMD tools if GPU is detected
    if lspci | grep -i amd; then
        apt-get install -y radeontop || true
    fi
    
    # Install Intel tools if GPU is detected
    if lspci | grep -i 'intel.*graphics'; then
        apt-get install -y intel-gpu-tools || true
    fi
}

compile_python_optimizations() {
    echo "Compiling Python with optimizations..."
    
    # Install PyPy for additional performance
    apt-get install -y pypy3 pypy3-dev
    
    # Ensure pip and setuptools are latest
    python3 -m pip install --upgrade pip setuptools wheel
    
    # Install performance-critical packages
    pip3 install \
        numpy \
        scipy \
        numba \
        cython \
        psutil \
        uvloop \
        orjson
}

install_dependencies() {
    echo "Installing dependencies..."
    install_system_dependencies
    install_performance_tools
    install_gpu_tools
    compile_python_optimizations
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [[ $EUID -ne 0 ]]; then
        echo "Error: This script must be run as root"
        exit 1
    fi
    
    echo "=== Dependencies Installation ==="
    install_dependencies "$@"
    echo "Dependencies installation completed!"
fi
