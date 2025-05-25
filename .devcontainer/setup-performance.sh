#!/bin/bash
set -e

echo "🚀 Setting up high-performance environment with binary volume persistence..."

# Create persistent binary cache directories on host
echo "📦 Setting up persistent binary cache volumes..."
sudo mkdir -p /opt/mcp-cache/{python-cache,wheels,bytecode,numba-cache}
sudo chmod -R 755 /opt/mcp-cache

# Link container cache to persistent volumes
if [ -d "/opt/python-cache" ] && [ ! -L "/opt/python-cache" ]; then
    echo "🔗 Linking cache directories to persistent volumes..."
    sudo rsync -av /opt/python-cache/ /opt/mcp-cache/python-cache/ || true
    rm -rf /opt/python-cache
    ln -sf /opt/mcp-cache/python-cache /opt/python-cache
fi

# Create cache symlinks if they don't exist
[ ! -d "/opt/python-cache" ] && ln -sf /opt/mcp-cache/python-cache /opt/python-cache
[ ! -d "/opt/wheels-cache" ] && ln -sf /opt/mcp-cache/wheels /opt/wheels-cache
[ ! -d "/opt/bytecode-cache" ] && ln -sf /opt/mcp-cache/bytecode /opt/bytecode-cache
[ ! -d "/opt/numba-cache" ] && ln -sf /opt/mcp-cache/numba-cache /opt/numba-cache

# Set CPU governor for maximum performance
echo "⚡ Configuring CPU for maximum performance..."
for cpu in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
    [ -w "$cpu" ] && echo performance > "$cpu" || true
done

# Disable CPU idle states for minimum latency
echo "🔧 Disabling CPU idle states for minimum latency..."
for state in /sys/devices/system/cpu/cpu*/cpuidle/state*/disable; do
    [ -w "$state" ] && echo 1 > "$state" || true
done

# Configure transparent huge pages
echo "📊 Optimizing memory management..."
echo always > /sys/kernel/mm/transparent_hugepage/enabled || true
echo always > /sys/kernel/mm/transparent_hugepage/defrag || true

# Set I/O scheduler for NVMe performance
echo "💾 Optimizing I/O scheduler for NVMe..."
for queue in /sys/block/nvme*/queue/scheduler; do
    [ -w "$queue" ] && echo none > "$queue" || true
done

# Configure network performance
echo "🌐 Optimizing network settings..."
sysctl -w net.core.rmem_max=134217728 || true
sysctl -w net.core.wmem_max=134217728 || true
sysctl -w net.core.netdev_max_backlog=5000 || true
sysctl -w net.ipv4.tcp_congestion_control=bbr || true

# Install performance-optimized Python packages with binary caching
echo "🐍 Installing performance-optimized Python packages with binary precompilation..."
bash /workspaces/python-sdk/.devcontainer/binary-precompile.sh

# Pre-compile Numba for JIT optimization
echo "⚡ Pre-compiling Numba JIT cache..."
python3 -c "
import numba
import numpy as np

@numba.jit(nopython=True, cache=True)
def test_func(x):
    return x * 2

# Trigger compilation
test_func(np.array([1, 2, 3]))
print('Numba JIT cache warmed up')
" || true

# Set up performance monitoring aliases
echo "📈 Setting up performance monitoring..."
cat >> ~/.bashrc << 'EOF'
# Performance monitoring aliases
alias cpuinfo='cat /proc/cpuinfo'
alias meminfo='cat /proc/meminfo'
alias diskstats='cat /proc/diskstats'
alias netstat='cat /proc/net/dev'
alias top_cpu='htop --sort-key PERCENT_CPU'
alias top_mem='htop --sort-key PERCENT_MEM'
alias iostat_live='iostat -x 1'
alias netstat_live='sar -n DEV 1'

# Python performance shortcuts
alias py_profile='python3 -m cProfile -s cumulative'
alias py_trace='python3 -m trace --count -C .'
alias py_timeit='python3 -m timeit'

# UV performance shortcuts
alias uv_fast='uv --cache-dir /tmp/uv-cache'
alias pip_fast='pip --cache-dir /tmp/pip-cache'
EOF

# Set up ulimits for maximum performance
echo "🔧 Configuring system limits..."
cat >> /etc/security/limits.conf << 'EOF'
* soft nofile 1048576
* hard nofile 1048576
* soft nproc 1048576
* hard nproc 1048576
* soft memlock unlimited
* hard memlock unlimited
EOF

# Enable core dumps for debugging performance issues
echo "🐛 Enabling core dumps for performance debugging..."
ulimit -c unlimited
echo "/tmp/core.%e.%p.%t" > /proc/sys/kernel/core_pattern || true

# Set up tmpfs for high-performance temporary storage
echo "💨 Setting up high-performance temporary storage..."
mount -t tmpfs -o size=4G,mode=1777 tmpfs /tmp || true

# Install MCP package in development mode with optimizations
echo "📦 Installing MCP package with optimizations..."
cd /workspaces/python-sdk
uv pip install -e . --cache-dir /tmp/uv-cache

# Pre-compile Python bytecode for the entire project
echo "⚡ Pre-compiling Python bytecode..."
python3 -m compileall -f -q src/

echo "✅ High-performance environment setup complete!"
echo ""
echo "🎯 Performance optimizations applied:"
echo "  • CPU governor set to performance mode"
echo "  • CPU idle states disabled for minimum latency"
echo "  • Transparent huge pages enabled"
echo "  • I/O scheduler optimized for NVMe"
echo "  • Network buffers maximized"
echo "  • BBR congestion control enabled"
echo "  • JIT compilation pre-warmed"
echo "  • System limits maximized"
echo "  • Temporary storage moved to tmpfs"
echo "  • Python bytecode pre-compiled"
echo ""
echo "🚀 Ready for maximum performance!"
