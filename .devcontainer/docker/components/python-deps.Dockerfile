# syntax=docker/dockerfile:1.4
# Python Dependencies Component
# Installs all Python packages using global version variables
# This file is executed as shell commands within the main Dockerfile

# Export environment variables for the installation commands
export UV_CACHE_DIR=${GLOBAL_UV_CACHE_DIR:-/opt/mcp-cache/uv}
export PIP_DISABLE_PIP_VERSION_CHECK=${GLOBAL_PIP_DISABLE_PIP_VERSION_CHECK:-true}
export PIP_ROOT_USER_ACTION=${GLOBAL_PIP_ROOT_USER_ACTION:-ignore}

# Install UV package manager
RUN --mount=type=cache,target=${GLOBAL_UV_CACHE_DIR},sharing=locked \
    --mount=type=cache,target=/opt/mcp-cache/python,sharing=locked \
    pip install uv>=${GLOBAL_UV_VERSION}

# Install core framework packages
RUN --mount=type=cache,target=${GLOBAL_UV_CACHE_DIR},sharing=locked \
    --mount=type=cache,target=/opt/mcp-cache/python,sharing=locked \
    uv pip install --system \
    fastapi>=${GLOBAL_FASTAPI_VERSION} \
    "uvicorn[standard]>=${GLOBAL_UVICORN_VERSION}" \
    httpx>=${GLOBAL_HTTPX_VERSION} \
    pydantic>=${GLOBAL_PYDANTIC_VERSION} \
    anyio>=${GLOBAL_ANYIO_VERSION}

# Install testing packages
RUN --mount=type=cache,target=${GLOBAL_UV_CACHE_DIR},sharing=locked \
    --mount=type=cache,target=/opt/mcp-cache/python,sharing=locked \
    uv pip install --system \
    pytest>=${GLOBAL_PYTEST_VERSION} \
    pytest-asyncio>=${GLOBAL_PYTEST_ASYNCIO_VERSION}

# Install formatting and linting packages
RUN --mount=type=cache,target=${GLOBAL_UV_CACHE_DIR},sharing=locked \
    --mount=type=cache,target=/opt/mcp-cache/python,sharing=locked \
    uv pip install --system \
    black>=${GLOBAL_BLACK_VERSION} \
    ruff>=${GLOBAL_RUFF_VERSION}

# Install performance optimization packages
RUN --mount=type=cache,target=${GLOBAL_UV_CACHE_DIR},sharing=locked \
    --mount=type=cache,target=/opt/mcp-cache/python,sharing=locked \
    uv pip install --system \
    uvloop>=${GLOBAL_UVLOOP_VERSION} \
    orjson>=${GLOBAL_ORJSON_VERSION} \
    cython>=${GLOBAL_CYTHON_VERSION} \
    numba>=${GLOBAL_NUMBA_VERSION} \
    psutil>=${GLOBAL_PSUTIL_VERSION} \
    jemalloc>=${GLOBAL_JEMALLOC_VERSION}

# Configure Python environment variables
ENV PYTHONPATH=${GLOBAL_PYTHONPATH:-/workspaces/python-sdk/src} \
    PYTHONUNBUFFERED=${GLOBAL_PYTHONUNBUFFERED:-1} \
    PYTHONDONTWRITEBYTECODE=${GLOBAL_PYTHONDONTWRITEBYTECODE:-1} \
    PYTHONOPTIMIZE=${GLOBAL_PYTHONOPTIMIZE:-2} \
    NUMBA_CACHE_DIR=${GLOBAL_NUMBA_CACHE_DIR:-/opt/mcp-cache/numba} \
    UV_CACHE_DIR=${GLOBAL_UV_CACHE_DIR}
