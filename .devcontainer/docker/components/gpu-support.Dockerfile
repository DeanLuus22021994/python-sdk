# syntax=docker/dockerfile:1.4
# GPU Support Component
# Uses global build arguments with GLOBAL_ prefix
FROM dev-tools AS gpu-support

# Global build arguments for GPU configuration
ARG GLOBAL_NVIDIA_VISIBLE_DEVICES=${GLOBAL_NVIDIA_VISIBLE_DEVICES:-all}
ARG GLOBAL_NVIDIA_DRIVER_CAPABILITIES=${GLOBAL_NVIDIA_DRIVER_CAPABILITIES:-all}
ARG GLOBAL_CUDA_VISIBLE_DEVICES=${GLOBAL_CUDA_VISIBLE_DEVICES:-all}
ARG GLOBAL_BUILDKIT_INLINE_CACHE=${GLOBAL_BUILDKIT_INLINE_CACHE:-1}

USER root

# NVIDIA GPU support with global configuration
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends \
    nvidia-cuda-toolkit \
    nvidia-cuda-dev \
    libnvidia-compute-470 \
    libnvidia-decode-470 \
    libnvidia-encode-470 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# AMD GPU support (conditional)
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends \
    rocm-dev \
    rocm-libs \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean || true

# Intel GPU support (conditional) 
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends \
    intel-opencl-icd \
    intel-level-zero-gpu \
    level-zero \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean || true

# Set global GPU environment variables
ENV NVIDIA_VISIBLE_DEVICES=${GLOBAL_NVIDIA_VISIBLE_DEVICES}
ENV NVIDIA_DRIVER_CAPABILITIES=${GLOBAL_NVIDIA_DRIVER_CAPABILITIES}
ENV CUDA_VISIBLE_DEVICES=${GLOBAL_CUDA_VISIBLE_DEVICES}

USER mcp
