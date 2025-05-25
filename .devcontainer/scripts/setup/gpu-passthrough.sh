#!/bin/bash
# GPU Passthrough Detection and Configuration Script
# Detects host GPUs without additional software overhead and configures passthrough

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] GPU-PASSTHROUGH:${NC} $1"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] GPU-PASSTHROUGH:${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] GPU-PASSTHROUGH:${NC} $1"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] GPU-PASSTHROUGH:${NC} $1"
}

# GPU detection without additional software
detect_nvidia_gpus() {
    log "Detecting NVIDIA GPUs on host system..."
    
    # Check for NVIDIA devices using direct device files
    local nvidia_devices=()
    local nvidia_count=0
    
    # Check for NVIDIA control device
    if [[ -c /dev/nvidiactl ]]; then
        log_success "NVIDIA control device found: /dev/nvidiactl"
        nvidia_devices+=("/dev/nvidiactl")
    else
        log_warning "No NVIDIA control device found"
        return 1
    fi
    
    # Check for NVIDIA UVM devices
    if [[ -c /dev/nvidia-uvm ]]; then
        log_success "NVIDIA UVM device found: /dev/nvidia-uvm"
        nvidia_devices+=("/dev/nvidia-uvm")
    fi
    
    if [[ -c /dev/nvidia-uvm-tools ]]; then
        log_success "NVIDIA UVM tools device found: /dev/nvidia-uvm-tools"
        nvidia_devices+=("/dev/nvidia-uvm-tools")
    fi
    
    # Detect individual GPU devices
    for device in /dev/nvidia*; do
        if [[ -c "$device" ]] && [[ "$device" =~ /dev/nvidia[0-9]+ ]]; then
            log_success "NVIDIA GPU device found: $device"
            nvidia_devices+=("$device")
            ((nvidia_count++))
        fi
    done
    
    if [[ $nvidia_count -gt 0 ]]; then
        log_success "Detected $nvidia_count NVIDIA GPU(s)"
        
        # Save device list for Docker configuration
        printf '%s\n' "${nvidia_devices[@]}" > /tmp/nvidia_devices.txt
        echo "$nvidia_count" > /tmp/nvidia_count.txt
        
        return 0
    else
        log_warning "No NVIDIA GPU devices found"
        return 1
    fi
}

# AMD GPU detection
detect_amd_gpus() {
    log "Detecting AMD GPUs on host system..."
    
    local amd_devices=()
    local amd_count=0
    
    # Check for AMD DRI devices
    for device in /dev/dri/card*; do
        if [[ -c "$device" ]]; then
            # Check if it's an AMD device by reading vendor info
            local vendor_path="/sys/class/drm/$(basename "$device")/device/vendor"
            if [[ -f "$vendor_path" ]]; then
                local vendor=$(cat "$vendor_path" 2>/dev/null || echo "")
                if [[ "$vendor" == "0x1002" ]]; then
                    log_success "AMD GPU device found: $device"
                    amd_devices+=("$device")
                    ((amd_count++))
                fi
            fi
        fi
    done
    
    # Check for AMD render devices
    for device in /dev/dri/renderD*; do
        if [[ -c "$device" ]]; then
            local card_num=$(echo "$device" | sed 's/.*renderD\([0-9]*\)/\1/')
            local card_path="/dev/dri/card$((card_num - 128))"
            if [[ -c "$card_path" ]]; then
                local vendor_path="/sys/class/drm/card$((card_num - 128))/device/vendor"
                if [[ -f "$vendor_path" ]]; then
                    local vendor=$(cat "$vendor_path" 2>/dev/null || echo "")
                    if [[ "$vendor" == "0x1002" ]]; then
                        log_success "AMD render device found: $device"
                        amd_devices+=("$device")
                    fi
                fi
            fi
        fi
    done
    
    if [[ $amd_count -gt 0 ]]; then
        log_success "Detected $amd_count AMD GPU(s)"
        
        # Save device list for Docker configuration
        printf '%s\n' "${amd_devices[@]}" > /tmp/amd_devices.txt
        echo "$amd_count" > /tmp/amd_count.txt
        
        return 0
    else
        log_warning "No AMD GPU devices found"
        return 1
    fi
}

# Intel GPU detection
detect_intel_gpus() {
    log "Detecting Intel GPUs on host system..."
    
    local intel_devices=()
    local intel_count=0
    
    # Check for Intel DRI devices
    for device in /dev/dri/card*; do
        if [[ -c "$device" ]]; then
            local vendor_path="/sys/class/drm/$(basename "$device")/device/vendor"
            if [[ -f "$vendor_path" ]]; then
                local vendor=$(cat "$vendor_path" 2>/dev/null || echo "")
                if [[ "$vendor" == "0x8086" ]]; then
                    log_success "Intel GPU device found: $device"
                    intel_devices+=("$device")
                    ((intel_count++))
                fi
            fi
        fi
    done
    
    if [[ $intel_count -gt 0 ]]; then
        log_success "Detected $intel_count Intel GPU(s)"
        
        # Save device list for Docker configuration
        printf '%s\n' "${intel_devices[@]}" > /tmp/intel_devices.txt
        echo "$intel_count" > /tmp/intel_count.txt
        
        return 0
    else
        log_warning "No Intel GPU devices found"
        return 1
    fi
}

# Generate Docker device configuration
generate_docker_devices_config() {
    log "Generating Docker device configuration..."
    
    local config_file="/tmp/docker_gpu_devices.txt"
    > "$config_file"
    
    # Add NVIDIA devices
    if [[ -f /tmp/nvidia_devices.txt ]]; then
        log "Adding NVIDIA devices to Docker configuration"
        while IFS= read -r device; do
            echo "      - $device:$device" >> "$config_file"
        done < /tmp/nvidia_devices.txt
    fi
    
    # Add AMD devices
    if [[ -f /tmp/amd_devices.txt ]]; then
        log "Adding AMD devices to Docker configuration"
        while IFS= read -r device; do
            echo "      - $device:$device" >> "$config_file"
        done < /tmp/amd_devices.txt
    fi
    
    # Add Intel devices
    if [[ -f /tmp/intel_devices.txt ]]; then
        log "Adding Intel devices to Docker configuration"
        while IFS= read -r device; do
            echo "      - $device:$device" >> "$config_file"
        done < /tmp/intel_devices.txt
    fi
    
    if [[ -s "$config_file" ]]; then
        log_success "Docker GPU device configuration generated: $config_file"
        cat "$config_file"
    else
        log_warning "No GPU devices found for Docker configuration"
    fi
}

# Check GPU driver availability
check_gpu_drivers() {
    log "Checking GPU driver availability..."
    
    # Check NVIDIA driver
    if command -v nvidia-smi >/dev/null 2>&1; then
        log_success "NVIDIA driver available"
        nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader,nounits 2>/dev/null | while IFS=, read -r name memory driver; do
            log_success "GPU: $name, Memory: ${memory}MB, Driver: $driver"
        done
    else
        log_warning "NVIDIA driver not available or nvidia-smi not found"
    fi
    
    # Check AMD driver (ROCm)
    if command -v rocm-smi >/dev/null 2>&1; then
        log_success "AMD ROCm driver available"
        rocm-smi --showproductname --showmeminfo max 2>/dev/null || log_warning "Failed to query AMD GPU info"
    else
        log_warning "AMD ROCm driver not available"
    fi
    
    # Check Intel GPU driver
    if [[ -f /sys/class/drm/card0/device/vendor ]] && [[ "$(cat /sys/class/drm/card0/device/vendor 2>/dev/null)" == "0x8086" ]]; then
        log_success "Intel GPU driver available"
    else
        log_warning "Intel GPU driver not detected"
    fi
}

# Set up GPU environment variables
setup_gpu_environment() {
    log "Setting up GPU environment variables..."
    
    local env_file="${WORKSPACE_FOLDER:-/workspaces/python-sdk}/.devcontainer/.env"
    
    # Backup existing .env file
    if [[ -f "$env_file" ]]; then
        cp "$env_file" "${env_file}.backup.$(date +%s)"
    fi
    
    # Update GPU configuration in .env file
    if [[ -f /tmp/nvidia_count.txt ]]; then
        local nvidia_count=$(cat /tmp/nvidia_count.txt)
        log "Configuring environment for $nvidia_count NVIDIA GPU(s)"
        
        # Update or add NVIDIA environment variables
        sed -i '/^NVIDIA_VISIBLE_DEVICES=/d' "$env_file" 2>/dev/null || true
        sed -i '/^CUDA_VISIBLE_DEVICES=/d' "$env_file" 2>/dev/null || true
        sed -i '/^GPU_PASSTHROUGH_ENABLED=/d' "$env_file" 2>/dev/null || true
        
        echo "NVIDIA_VISIBLE_DEVICES=all" >> "$env_file"
        echo "CUDA_VISIBLE_DEVICES=all" >> "$env_file"
        echo "GPU_PASSTHROUGH_ENABLED=true" >> "$env_file"
        echo "NVIDIA_DRIVER_CAPABILITIES=compute,utility,graphics" >> "$env_file"
    fi
    
    if [[ -f /tmp/amd_count.txt ]]; then
        local amd_count=$(cat /tmp/amd_count.txt)
        log "Configuring environment for $amd_count AMD GPU(s)"
        
        # Update or add AMD environment variables
        sed -i '/^AMD_VISIBLE_DEVICES=/d' "$env_file" 2>/dev/null || true
        echo "AMD_VISIBLE_DEVICES=all" >> "$env_file"
        echo "HIP_VISIBLE_DEVICES=all" >> "$env_file"
    fi
    
    if [[ -f /tmp/intel_count.txt ]]; then
        local intel_count=$(cat /tmp/intel_count.txt)
        log "Configuring environment for $intel_count Intel GPU(s)"
        
        # Update or add Intel environment variables
        sed -i '/^INTEL_VISIBLE_DEVICES=/d' "$env_file" 2>/dev/null || true
        echo "INTEL_VISIBLE_DEVICES=all" >> "$env_file"
    fi
    
    log_success "GPU environment variables configured in $env_file"
}

# Validate GPU passthrough
validate_gpu_passthrough() {
    log "Validating GPU passthrough configuration..."
    
    local validation_passed=true
    
    # Check device permissions
    if [[ -f /tmp/nvidia_devices.txt ]]; then
        while IFS= read -r device; do
            if [[ -c "$device" ]] && [[ -r "$device" ]] && [[ -w "$device" ]]; then
                log_success "Device $device is accessible"
            else
                log_error "Device $device is not accessible or has incorrect permissions"
                validation_passed=false
            fi
        done < /tmp/nvidia_devices.txt
    fi
    
    # Check for required libraries in host
    local required_libs=(
        "/usr/lib/x86_64-linux-gnu/libcuda.so.1"
        "/usr/lib/x86_64-linux-gnu/libnvidia-ml.so.1"
    )
    
    for lib in "${required_libs[@]}"; do
        if [[ -f "$lib" ]]; then
            log_success "Required library found: $lib"
        else
            log_warning "Required library not found: $lib (may affect GPU functionality)"
        fi
    done
    
    if $validation_passed; then
        log_success "GPU passthrough validation completed successfully"
        return 0
    else
        log_error "GPU passthrough validation failed"
        return 1
    fi
}

# Main execution
main() {
    log "Starting GPU passthrough detection and configuration..."
    
    local gpu_found=false
    
    # Detect GPUs
    if detect_nvidia_gpus; then
        gpu_found=true
    fi
    
    if detect_amd_gpus; then
        gpu_found=true
    fi
    
    if detect_intel_gpus; then
        gpu_found=true
    fi
    
    if ! $gpu_found; then
        log_warning "No GPUs detected on the host system"
        # Still configure environment for potential future GPU detection
        setup_gpu_environment
        return 0
    fi
    
    # Generate Docker configuration
    generate_docker_devices_config
    
    # Check drivers
    check_gpu_drivers
    
    # Setup environment
    setup_gpu_environment
    
    # Validate configuration
    if validate_gpu_passthrough; then
        log_success "GPU passthrough configuration completed successfully"
    else
        log_error "GPU passthrough configuration completed with warnings"
        return 1
    fi
}

# Execute main function
main "$@"
