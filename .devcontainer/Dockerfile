# Multi-Stage High-Performance Python Environment with Binary Precompilation
FROM mcr.microsoft.com/devcontainers/python:1-3.12-bullseye AS builder

# Enable full system access and performance
USER root

# Build stage environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONOPTIMIZE=2 \
    PYTHONDONTWRITEBYTECODE=0 \
    PIP_NO_CACHE_DIR=0 \
    PIP_COMPILE=1 \
    UV_COMPILE_BYTECODE=1

# Install build dependencies for compilation
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
        build-essential \
        gcc-11 \
        g++-11 \
        clang-14 \
        llvm-14 \
        libblas-dev \
        liblapack-dev \
        libopenblas-dev \
        jemalloc-dev \
        libtcmalloc-minimal4 \
        libnuma-dev \
        git \
        curl \
        wget \
    && apt-get autoremove -y && apt-get clean -y && rm -rf /var/lib/apt/lists/*

# Install latest uv with performance optimizations
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Create persistent binary cache directories
RUN mkdir -p /opt/python-cache/{pip,uv,numba,site-packages,wheels,bytecode}

# Pre-install and compile performance dependencies to persistent cache
RUN uv pip install --system --cache-dir /opt/python-cache/uv \
        cython==3.0.10 \
        numba==0.59.1 \
        uvloop==0.19.0 \
        orjson==3.9.15 \
        msgpack==1.0.8 \
        lz4==4.3.3 \
        xxhash==3.4.1 \
        pyarrow==15.0.2 \
        polars==0.20.31 \
        fastapi==0.110.3 \
        gunicorn==21.2.0 \
        gevent==23.9.1 \
        psutil==5.9.8 \
        memory_profiler==0.61.0 \
        line_profiler==4.1.3 \
        py-spy==0.3.14 \
        prometheus-client==0.20.0 \
        aiofiles==23.2.1 \
        aiodns==3.2.0 \
        cchardet==2.1.7 \
        brotli==1.1.0 \
        zstandard==0.22.0

# Pre-compile Numba JIT cache
RUN NUMBA_CACHE_DIR=/opt/python-cache/numba python3 -c "import numba; import numpy as np; exec('\\n@numba.jit(nopython=True, cache=True)\\ndef warmup(x): return x * 2\\nwarmup(np.array([1, 2, 3]))\\nprint(\"Numba JIT cache created\")')"

# Pre-compile all installed packages
RUN python3 -m compileall -f -q /usr/local/lib/python3.12/site-packages/

# Cache compiled bytecode in persistent volume
RUN cp -r /usr/local/lib/python3.12/site-packages/* /opt/python-cache/site-packages/

# Create wheel cache for faster installs
RUN pip3 wheel --wheel-dir /opt/python-cache/wheels --no-deps \
        cython numba uvloop orjson msgpack lz4 xxhash pyarrow polars \
        fastapi gunicorn gevent psutil memory_profiler line_profiler

# Runtime stage with optimized binary volumes
FROM mcr.microsoft.com/devcontainers/python:1-3.12-bullseye AS runtime

# Enable full system access and performance
USER root

# Set performance-oriented environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONOPTIMIZE=2 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=0 \
    PYTHON_GIL=0 \
    MALLOC_ARENA_MAX=4 \
    MALLOC_TRIM_THRESHOLD_=131072 \
    MALLOC_TOP_PAD_=131072 \
    MALLOC_MMAP_THRESHOLD_=131072 \
    OMP_NUM_THREADS=auto \
    MKL_NUM_THREADS=auto \
    OPENBLAS_NUM_THREADS=auto \
    VECLIB_MAXIMUM_THREADS=auto \
    NUMEXPR_NUM_THREADS=auto

# Install performance-critical runtime packages
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
        # Performance monitoring and profiling
        htop \
        iotop \
        sysstat \
        perf-tools-unstable \
        strace \
        tcpdump \
        # Memory optimization
        jemalloc-dev \
        libtcmalloc-minimal4 \
        # Network performance
        iperf3 \
        netcat \
        socat \
        # Storage optimization
        nvme-cli \
        fio \
        # Math libraries for acceleration
        libblas-dev \
        liblapack-dev \
        libopenblas-dev \
        # NUMA optimization
        numactl \
        libnuma-dev \
        # Additional utilities
        curl \
        wget \
        git \
        rsync \
        zip \
        unzip \
        # Cleanup
    && apt-get autoremove -y && apt-get clean -y && rm -rf /var/lib/apt/lists/*

# Copy pre-compiled binary cache from builder stage
COPY --from=builder /opt/python-cache /opt/python-cache

# Install latest uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Restore pre-compiled packages from cache
RUN cp -r /opt/python-cache/site-packages/* /usr/local/lib/python3.12/site-packages/

# Configure jemalloc for better memory performance
ENV LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libjemalloc.so.2

# Pre-compile Python standard library with optimizations
RUN python3 -O -m compileall -f /usr/local/lib/python3.12

# Set up performance-optimized pip configuration
RUN mkdir -p /root/.config/pip && echo "[global]\nno-cache-dir = false\ncache-dir = /opt/python-cache/pip\ncompile = yes\noptimize = 2\nfind-links = /opt/python-cache/wheels" > /root/.config/pip/pip.conf

# Set up performance-optimized uv configuration
RUN mkdir -p /root/.config/uv && echo "cache-dir = \"/opt/python-cache/uv\"\ncompile-bytecode = true\nlink-mode = \"copy\"" > /root/.config/uv/uv.toml

# Create optimized cache directories with proper permissions
RUN mkdir -p /opt/python-cache/{pip,uv,numba,cuda} \
    && chmod -R 755 /opt/python-cache \
    && ln -sf /opt/python-cache/numba /tmp/numba-cache \
    && ln -sf /opt/python-cache/cuda /tmp/cuda-cache

# Set container-specific optimizations
COPY <<EOF /etc/sysctl.d/99-performance.conf
# Network performance
net.core.rmem_max = 134217728
net.core.wmem_max = 134217728
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_rmem = 4096 131072 134217728
net.ipv4.tcp_wmem = 4096 131072 134217728
net.ipv4.tcp_congestion_control = bbr
net.ipv4.tcp_slow_start_after_idle = 0

# Memory management
vm.swappiness = 1
vm.dirty_ratio = 15
vm.dirty_background_ratio = 5
vm.dirty_expire_centisecs = 500
vm.dirty_writeback_centisecs = 100

# File system performance
fs.file-max = 2097152
fs.nr_open = 1048576
EOF

# Create binary volume mount points
RUN mkdir -p /mnt/binary-volumes/{python-cache,wheels,bytecode} \
    && ln -sf /mnt/binary-volumes/python-cache /opt/python-cache-persistent \
    && ln -sf /mnt/binary-volumes/wheels /opt/wheels-persistent \
    && ln -sf /mnt/binary-volumes/bytecode /opt/bytecode-persistent

# Set up runtime environment
ENV NUMBA_CACHE_DIR=/opt/python-cache/numba \
    UV_CACHE_DIR=/opt/python-cache/uv \
    PIP_CACHE_DIR=/opt/python-cache/pip \
    CUDA_CACHE_PATH=/opt/python-cache/cuda \
    PYTHONPATH=/opt/python-cache/site-packages:$PYTHONPATH
