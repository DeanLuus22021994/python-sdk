#!/bin/bash
# Log Analyzer
# Analyzes system and application logs for performance insights

set -euo pipefail

analyze_system_logs() {
    echo "=== System Log Analysis ==="
    
    # Check for OOM killer events
    echo "Checking for out-of-memory events..."
    dmesg | grep -i "killed process" | tail -5
    
    # Check for thermal throttling
    echo "Checking for thermal throttling..."
    dmesg | grep -i "thermal" | tail -5
    
    # Check for I/O errors
    echo "Checking for I/O errors..."
    dmesg | grep -i "i/o error\|ata.*error" | tail -5
}

analyze_docker_logs() {
    echo "=== Docker Log Analysis ==="
    
    # Check Docker daemon logs
    echo "Docker daemon status:"
    systemctl status docker --no-pager -l | head -10
    
    # Check container resource usage
    echo "Container resource usage:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
}

analyze_performance_metrics() {
    echo "=== Performance Metrics Analysis ==="
    
    # CPU usage patterns
    echo "CPU usage:"
    if command -v sar &> /dev/null; then
        sar -u 1 5 | tail -1
    else
        echo "Current load average:"
        cat /proc/loadavg
    fi
    
    # Memory usage patterns  
    echo "Memory usage:"
    free -h
    
    # Disk I/O patterns
    echo "Disk I/O:"
    if command -v iostat &> /dev/null; then
        iostat -x 1 1 | grep -v "^$"
    else
        echo "Disk stats:"
        cat /proc/diskstats | awk '{print $3, $4, $8}' | head -5
    fi
    
    # Network usage
    echo "Network interfaces:"
    if command -v sar &> /dev/null; then
        sar -n DEV 1 1 | grep -v "^$" | tail -n +3
    else
        echo "Network interface stats:"
        cat /proc/net/dev | head -5
    fi
}

generate_performance_report() {
    local report_file="/tmp/performance-report-$(date +%Y%m%d-%H%M%S).txt"
    
    echo "Generating performance report: $report_file"
    
    {
        echo "Performance Report - $(date)"
        echo "=================================="
        echo
        
        analyze_system_logs
        echo
        analyze_docker_logs
        echo
        analyze_performance_metrics
        
    } > "$report_file"
    
    echo "Report saved to: $report_file"
}

main() {
    case "${1:-analyze}" in
        "system")
            analyze_system_logs
            ;;
        "docker")
            analyze_docker_logs
            ;;
        "performance")
            analyze_performance_metrics
            ;;
        "report")
            generate_performance_report
            ;;
        "analyze"|*)
            analyze_system_logs
            analyze_docker_logs
            analyze_performance_metrics
            ;;
    esac
}

main "$@"
