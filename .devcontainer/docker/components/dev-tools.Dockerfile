# syntax=docker/dockerfile:1.4
# Development Tools Component
FROM python-base AS dev-tools

USER root

# Install essential development tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    gcc-11 \
    g++-11 \
    && update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-11 100 \
    && update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-11 100 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Performance optimization tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    htop \
    iotop \
    sysstat \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

USER mcp
