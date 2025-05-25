#!/bin/bash
# System Monitor
# Real-time monitoring of system resources and performance

set -euo pipefail

monitor_cpu() {
    echo "=== CPU Monitoring ==="
    echo "CPU Usage by Core:"
    mpstat -P ALL 1 1 | grep -v "^$"
    
    echo "Top CPU-consuming processes:"
    ps aux --sort=-%cpu | head -10
}

monitor_memory() {
    echo "=== Memory Monitoring ==="
    echo "Memory usage breakdown:"
    free -h
    echo
    
    echo "Memory usage by process:"
    ps aux --sort=-%mem | head -10
    echo
    
    echo "Memory usage details:"
    cat /proc/meminfo | grep -E "(MemTotal|MemFree|MemAvailable|Buffers|Cached|SwapTotal|SwapFree)"
}

monitor_gpu() {
    echo "=== GPU Monitoring ==="
    
    if command -v nvidia-smi &> /dev/null; then
        echo "NVIDIA GPU status:"
        nvidia-smi --query-gpu=index,name,utilization.gpu,memory.used,memory.total,temperature.gpu --format=csv,noheader,nounits
    fi
    
    if command -v radeontop &> /dev/null; then
        echo "AMD GPU status:"
        timeout 5s radeontop -d - -l 1 | tail -1
    fi
}

monitor_disk() {
    echo "=== Disk I/O Monitoring ==="
    echo "Disk usage:"
    df -h | grep -E "(Filesystem|/dev/)"
    echo
    
    echo "Disk I/O statistics:"
    iostat -x 1 1 | grep -v "^$"
}

monitor_network() {
    echo "=== Network Monitoring ==="
    echo "Network interface statistics:"
    cat /proc/net/dev | head -2
    cat /proc/net/dev | grep -E "(eth|wlan|ens|enp)" | head -5
    echo
    
    echo "Active network connections:"
    ss -tuln | head -10
}

monitor_containers() {
    echo "=== Container Monitoring ==="
    if command -v docker &> /dev/null && docker info &> /dev/null; then
        echo "Container resource usage:"
        docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}" | head -10
    else
        echo "Docker not available or not running"
    fi
}

continuous_monitor() {
    local interval="${1:-5}"
    
    echo "Starting continuous monitoring (interval: ${interval}s)..."
    echo "Press Ctrl+C to stop"
    
    while true; do
        clear
        echo "System Monitor - $(date)"
        echo "========================================"
        
        monitor_cpu
        echo
        monitor_memory
        echo
        monitor_gpu
        echo
        monitor_disk
        echo
        monitor_network
        echo
        monitor_containers
        
        sleep "$interval"
    done
}

main() {
    case "${1:-all}" in
        "cpu")
            monitor_cpu
            ;;
        "memory"|"mem")
            monitor_memory
            ;;
        "gpu")
            monitor_gpu
            ;;
        "disk"|"io")
            monitor_disk
            ;;
        "network"|"net")
            monitor_network
            ;;
        "containers"|"docker")
            monitor_containers
            ;;
        "continuous"|"watch")
            continuous_monitor "${2:-5}"
            ;;
        "all"|*)
            monitor_cpu
            echo
            monitor_memory
            echo
            monitor_gpu
            echo
            monitor_disk
            echo
            monitor_network
            echo
            monitor_containers
            ;;
    esac
}

main "$@"
