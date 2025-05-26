# syntax=docker/dockerfile:1.4
# Development Tools Component
# Uses global build arguments with GLOBAL_ prefix
FROM python-base AS dev-tools

ARG GLOBAL_BUILDKIT_INLINE_CACHE=${GLOBAL_BUILDKIT_INLINE_CACHE:-1}
ARG GLOBAL_DOCKER_BUILDKIT=${GLOBAL_DOCKER_BUILDKIT:-1}

USER root

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    gcc-11 \
    g++-11 \
    cmake \
    ninja-build \
    ccache \
    && update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-11 100 \
    && update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-11 100 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends \
    htop \
    iotop \
    sysstat \
    perf-tools-unstable \
    strace \
    valgrind \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

ENV CCACHE_DIR=/opt/mcp-cache/ccache
ENV PATH="/usr/lib/ccache:$PATH"

USER mcp