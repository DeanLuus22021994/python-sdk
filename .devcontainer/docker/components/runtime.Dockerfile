# syntax=docker/dockerfile:1.4
# Final Runtime Stage
# Uses global build arguments with GLOBAL_ prefix
FROM network-optimized AS runtime

# Global build arguments
ARG GLOBAL_PYTHONOPTIMIZE=${GLOBAL_PYTHONOPTIMIZE:-2}
ARG GLOBAL_PYTHONHASHSEED=${GLOBAL_PYTHONHASHSEED:-0}
ARG GLOBAL_BUILDKIT_INLINE_CACHE=${GLOBAL_BUILDKIT_INLINE_CACHE:-1}

USER root

# Install Python development dependencies
COPY docker/components/requirements-dev.txt /tmp/
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    --mount=type=cache,target=/tmp/.buildx-cache,sharing=locked \
    uv pip install --system --no-cache-dir -r /tmp/requirements-dev.txt && \
    rm /tmp/requirements-dev.txt

# Set up performance monitoring with global configuration
RUN mkdir -p /var/log/performance && \
    chown mcp:mcp /var/log/performance

# Final optimizations with Python optimization level
ENV PYTHONOPTIMIZE=${GLOBAL_PYTHONOPTIMIZE}
ENV PYTHONHASHSEED=${GLOBAL_PYTHONHASHSEED}

RUN ldconfig && \
    find /usr/local -name "*.pyc" -delete && \
    find /usr/local -name "__pycache__" -type d -exec rm -rf {} + || true

USER mcp

# Health check with global configuration
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"
