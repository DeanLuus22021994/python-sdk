# syntax=docker/dockerfile:1.4
# Base Python Slim Image with Maximum Optimizations
FROM python:3.12-slim AS python-base

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONOPTIMIZE=2 \
    PYTHONHASHSEED=0 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=0 \
    PIP_COMPILE=1

RUN groupadd -r mcp && useradd -r -g mcp mcp && \
    mkdir -p /opt/mcp-cache/{python,wheels,bytecode,numba,cuda} && \
    chown -R mcp:mcp /opt/mcp-cache

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

RUN pip install --no-cache-dir uv

USER mcp
WORKDIR /workspaces