# syntax=docker/dockerfile:1.4
# Network Optimization Component
# Uses global build arguments with GLOBAL_ prefix
FROM gpu-support AS network-optimized

ARG GLOBAL_BUILDKIT_INLINE_CACHE=${GLOBAL_BUILDKIT_INLINE_CACHE:-1}
ARG GLOBAL_NETWORK_MTU=${GLOBAL_NETWORK_MTU:-9000}

USER root

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends \
    net-tools \
    iputils-ping \
    curl \
    wget \
    netcat-openbsd \
    iperf3 \
    tcpdump \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

RUN echo 'net.core.rmem_max = 134217728' >> /etc/sysctl.conf && \
    echo 'net.core.wmem_max = 134217728' >> /etc/sysctl.conf && \
    echo 'net.core.netdev_max_backlog = 5000' >> /etc/sysctl.conf && \
    echo 'net.ipv4.tcp_congestion_control = bbr' >> /etc/sysctl.conf && \
    echo 'net.ipv4.tcp_rmem = 4096 16384 134217728' >> /etc/sysctl.conf && \
    echo 'net.ipv4.tcp_wmem = 4096 16384 134217728' >> /etc/sysctl.conf && \
    echo 'net.ipv4.tcp_window_scaling = 1' >> /etc/sysctl.conf && \
    echo 'net.ipv4.tcp_timestamps = 1' >> /etc/sysctl.conf

ENV NETWORK_MTU=${GLOBAL_NETWORK_MTU}

USER mcp