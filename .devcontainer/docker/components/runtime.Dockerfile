# syntax=docker/dockerfile:1.4
# Final Runtime Stage
FROM network-optimized AS runtime

USER root

# Install Python development dependencies
COPY docker/components/requirements-dev.txt /tmp/
RUN uv pip install --system --no-cache-dir -r /tmp/requirements-dev.txt && \
    rm /tmp/requirements-dev.txt

# Set up performance monitoring
RUN mkdir -p /var/log/performance && \
    chown mcp:mcp /var/log/performance

# Final optimizations
RUN ldconfig && \
    find /usr/local -name "*.pyc" -delete && \
    find /usr/local -name "__pycache__" -type d -exec rm -rf {} + || true

USER mcp

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import sys; sys.exit(0)"

CMD ["sleep", "infinity"]
