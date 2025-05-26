# syntax=docker/dockerfile:1.4
# Python Dependencies Component
# Installs all Python packages using global version variables
# Refer to docker-globals.yml for the environment variable definitions

FROM python:3.12-bullseye AS python-deps

ARG GLOBAL_UV_CACHE_DIR
ARG GLOBAL_PIP_DISABLE_PIP_VERSION_CHECK
ARG GLOBAL_PIP_ROOT_USER_ACTION
ARG GLOBAL_UV_VERSION
ARG GLOBAL_FASTAPI_VERSION
ARG GLOBAL_UVICORN_VERSION
ARG GLOBAL_HTTPX_VERSION
ARG GLOBAL_PYDANTIC_VERSION
ARG GLOBAL_ANYIO_VERSION
ARG GLOBAL_PYTEST_VERSION
ARG GLOBAL_PYTEST_ASYNCIO_VERSION
ARG GLOBAL_BLACK_VERSION
ARG GLOBAL_RUFF_VERSION
ARG GLOBAL_UVLOOP_VERSION
ARG GLOBAL_ORJSON_VERSION
ARG GLOBAL_CYTHON_VERSION
ARG GLOBAL_NUMBA_VERSION
ARG GLOBAL_PSUTIL_VERSION
ARG GLOBAL_JEMALLOC_VERSION
ARG GLOBAL_PYTHONPATH
ARG GLOBAL_PYTHONUNBUFFERED
ARG GLOBAL_PYTHONDONTWRITEBYTECODE
ARG GLOBAL_PYTHONOPTIMIZE
ARG GLOBAL_NUMBA_CACHE_DIR

ENV UV_CACHE_DIR="${GLOBAL_UV_CACHE_DIR}" \
    PIP_DISABLE_PIP_VERSION_CHECK="${GLOBAL_PIP_DISABLE_PIP_VERSION_CHECK}" \
    PIP_ROOT_USER_ACTION="${GLOBAL_PIP_ROOT_USER_ACTION}" \
    PYTHONPATH="${GLOBAL_PYTHONPATH}" \
    PYTHONUNBUFFERED="${GLOBAL_PYTHONUNBUFFERED}" \
    PYTHONDONTWRITEBYTECODE="${GLOBAL_PYTHONDONTWRITEBYTECODE}" \
    PYTHONOPTIMIZE="${GLOBAL_PYTHONOPTIMIZE}" \
    NUMBA_CACHE_DIR="${GLOBAL_NUMBA_CACHE_DIR}"

# 1) Install UV package manager
RUN --mount=type=cache,target="${UV_CACHE_DIR}",sharing=locked \
    --mount=type=cache,target=/opt/mcp-cache/python,sharing=locked \
    pip install "uv>=${GLOBAL_UV_VERSION}"

# 2) Install core framework packages
RUN --mount=type=cache,target="${UV_CACHE_DIR}",sharing=locked \
    --mount=type=cache,target=/opt/mcp-cache/python,sharing=locked \
    uv pip install --system \
      "fastapi>=${GLOBAL_FASTAPI_VERSION}" \
      "uvicorn[standard]>=${GLOBAL_UVICORN_VERSION}" \
      "httpx>=${GLOBAL_HTTPX_VERSION}" \
      "pydantic>=${GLOBAL_PYDANTIC_VERSION}" \
      "anyio>=${GLOBAL_ANYIO_VERSION}"

# 3) Install testing packages
RUN --mount=type=cache,target="${UV_CACHE_DIR}",sharing=locked \
    --mount=type=cache,target=/opt/mcp-cache/python,sharing=locked \
    uv pip install --system \
      "pytest>=${GLOBAL_PYTEST_VERSION}" \
      "pytest-asyncio>=${GLOBAL_PYTEST_ASYNCIO_VERSION}"

# 4) Install formatting and linting packages
RUN --mount=type=cache,target="${UV_CACHE_DIR}",sharing=locked \
    --mount=type=cache,target=/opt/mcp-cache/python,sharing=locked \
    uv pip install --system \
      "black>=${GLOBAL_BLACK_VERSION}" \
      "ruff>=${GLOBAL_RUFF_VERSION}"

# 5) Install performance optimization packages
RUN --mount=type=cache,target="${UV_CACHE_DIR}",sharing=locked \
    --mount=type=cache,target=/opt/mcp-cache/python,sharing=locked \
    uv pip install --system \
      "uvloop>=${GLOBAL_UVLOOP_VERSION}" \
      "orjson>=${GLOBAL_ORJSON_VERSION}" \
      "cython>=${GLOBAL_CYTHON_VERSION}" \
      "numba>=${GLOBAL_NUMBA_VERSION}" \
      "psutil>=${GLOBAL_PSUTIL_VERSION}" \
      "jemalloc>=${GLOBAL_JEMALLOC_VERSION}"