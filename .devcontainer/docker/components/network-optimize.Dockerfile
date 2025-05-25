# syntax=docker/dockerfile:1.4
# Network Optimization Component
FROM gpu-support AS network-optimized

USER root

# Network optimization tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    net-tools \
    iputils-ping \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set network optimizations
RUN echo 'net.core.rmem_max = 134217728' >> /etc/sysctl.conf && \
    echo 'net.core.wmem_max = 134217728' >> /etc/sysctl.conf && \
    echo 'net.core.netdev_max_backlog = 5000' >> /etc/sysctl.conf && \
    echo 'net.ipv4.tcp_congestion_control = bbr' >> /etc/sysctl.conf

USER mcp
