# syntax=docker/dockerfile:1.4
# GPU Support Component
FROM dev-tools AS gpu-support

USER root

# NVIDIA GPU support (conditional)
RUN apt-get update && apt-get install -y --no-install-recommends \
    nvidia-cuda-toolkit \
    nvidia-cuda-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean || true

# AMD GPU support (conditional)
RUN apt-get update && apt-get install -y --no-install-recommends \
    rocm-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean || true

# Intel GPU support (conditional)
RUN apt-get update && apt-get install -y --no-install-recommends \
    intel-opencl-icd \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean || true

USER mcp
