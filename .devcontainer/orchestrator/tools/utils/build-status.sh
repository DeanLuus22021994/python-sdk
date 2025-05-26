#!/bin/bash
# Tool 002: Build Status Checker
# Purpose: Check current build status and active processes
# Usage: ./002-build-status.sh [processes|docker|performance]

check_build_status() {
    local check_type="${1:-all}"
    
    case "$check_type" in
        "processes")
            echo "=== Active Build Processes ==="
            ps aux | grep -E "(docker|python|npm|pip|cmake|make)" | grep -v grep
            ;;
        "docker")
            echo "=== Docker Status ==="
            docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
            echo -e "\n=== Docker Resources ==="
            docker system df
            ;;
        "performance")
            echo "=== System Performance ==="
            echo "CPU: $(nproc) cores, Load: $(uptime | awk '{print $NF}')"
            echo "Memory: $(free -h | awk 'NR==2{print $3"/"$2}')"
            echo "Disk: $(df -h /workspaces | awk 'NR==2{print $3"/"$2" ("$5")"}')"
            ;;
        *)
            check_build_status "processes"
            check_build_status "docker"
            check_build_status "performance"
            ;;
    esac
}

check_build_status "$@"
