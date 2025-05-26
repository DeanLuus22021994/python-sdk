"""
Constants and Configuration Values
Centralized constants for the MCP Python SDK setup
"""

# Python version requirements
MIN_PYTHON_VERSION = (3, 10)
RECOMMENDED_PYTHON_VERSION = (3, 11)

# Project structure requirements
REQUIRED_PROJECT_PATHS = ["src/mcp", "pyproject.toml", ".vscode"]

# Optional project paths
OPTIONAL_PROJECT_PATHS = ["tests", "docs", "examples", "README.md", "LICENSE"]

# VS Code extension recommendations
RECOMMENDED_EXTENSIONS = [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-python.black-formatter",
    "ms-python.mypy-type-checker",
    "charliermarsh.ruff",
    "ms-python.debugpy",
    "github.copilot",
    "github.copilot-chat",
    "ms-vscode.errorlens",
    "ms-vscode.vscode-json",
    "tamasfe.even-better-toml",
    "redhat.vscode-yaml",
    "yzhang.markdown-all-in-one",
]

# Performance settings
PERFORMANCE_SETTINGS = {
    "python.analysis.userFileIndexingLimit": 5000,
    "python.analysis.packageIndexDepths": [{"name": "mcp", "depth": 5}],
    "files.watcherExclude": {
        "**/__pycache__/**": True,
        "**/.git/objects/**": True,
        "**/.git/subtree-cache/**": True,
        "**/node_modules/**": True,
        "**/.pytest_cache/**": True,
        "**/.mypy_cache/**": True,
        "**/.ruff_cache/**": True,
        "**/.venv/**": True,
        "**/venv/**": True,
        "**/build/**": True,
        "**/dist/**": True,
        "**/.coverage/**": True,
        "**/.tox/**": True,
        "**/htmlcov/**": True,
    },
    "search.exclude": {
        "**/.venv": True,
        "**/venv": True,
        "**/__pycache__": True,
        "**/*.pyc": True,
        "**/.pytest_cache": True,
        "**/.mypy_cache": True,
        "**/.ruff_cache": True,
        "**/build": True,
        "**/dist": True,
        "**/*.egg-info": True,
        "**/.coverage": True,
        "**/.tox": True,
        "**/htmlcov": True,
        "**/uv.lock": True,
    },
}
