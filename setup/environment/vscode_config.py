"""
VS Code Configuration Management
Modern VS Code settings, tasks, and launch configurations for optimal Python development
"""

import json
from pathlib import Path
from typing import Any

from .constants import PERFORMANCE_SETTINGS, RECOMMENDED_EXTENSIONS
from .path_utils import ensure_directory_exists, get_project_root


def get_modern_vscode_settings() -> dict[str, Any]:
    """
    Get modern VS Code settings optimized for Python SDK development.

    Returns:
        Dictionary with comprehensive VS Code settings
    """
    return {
        # Python interpreter and analysis
        "python.defaultInterpreterPath": "./venv/Scripts/python.exe",
        "python.analysis.autoImportCompletions": True,
        "python.analysis.diagnosticMode": "workspace",
        "python.analysis.inlayHints.variableTypes": True,
        "python.analysis.inlayHints.functionReturnTypes": True,
        "python.analysis.inlayHints.callArgumentNames": "partial",
        "python.analysis.inlayHints.pytestParameters": True,
        "python.analysis.completeFunctionParens": True,
        "python.analysis.indexing": True,
        "python.analysis.autoFormatStrings": True,
        "python.analysis.fixAll": [
            "source.unusedImports",
            "source.convertImportFormat",
        ],
        # Performance settings
        **PERFORMANCE_SETTINGS,
        # File management
        "files.exclude": {
            "**/__pycache__": True,
            "**/*.pyc": True,
            ".pytest_cache": True,
            "*.egg-info": True,
            "**/.mypy_cache": True,
            "**/.ruff_cache": True,
            "**/node_modules": True,
            "**/.venv": True,
            "**/venv": True,
            "**/.env": True,
            "**/build": True,
            "**/dist": True,
            "**/*.egg-info": True,
            "**/.coverage": True,
            "**/.tox": True,
            "**/htmlcov": True,
        },
        "files.insertFinalNewline": True,
        "files.trimFinalNewlines": True,
        "files.trimTrailingWhitespace": True,
        "files.associations": {
            "*.toml": "toml",
            "pyproject.toml": "toml",
            "*.lock": "yaml",
            "uv.lock": "yaml",
        },
        # Python testing
        "python.testing.pytestEnabled": True,
        "python.testing.unittestEnabled": False,
        "python.testing.pytestArgs": [
            "tests",
            "-v",
            "--tb=short",
            "--strict-markers",
            "--strict-config",
            "--color=yes",
        ],
        "python.testing.autoTestDiscoverOnSaveEnabled": True,
        "python.testing.cwd": "${workspaceFolder}",
        "python.testing.debugPort": 3000,
        # Python formatting and linting
        "[python]": {
            "editor.defaultFormatter": "ms-python.black-formatter",
            "editor.formatOnSave": True,
            "editor.codeActionsOnSave": {
                "source.organizeImports": "explicit",
                "source.fixAll.ruff": "explicit",
            },
            "editor.rulers": [88],
            "editor.tabSize": 4,
            "editor.insertSpaces": True,
            "editor.wordWrap": "off",
            "editor.trimAutoWhitespace": True,
            "editor.insertFinalNewline": True,
            "editor.trimFinalNewlines": True,
            "editor.guides.bracketPairs": "active",
            "editor.guides.indentation": True,
            "editor.semanticHighlighting.enabled": True,
            "editor.inlayHints.enabled": "on",
        },
        # Tool configurations
        "python.linting.enabled": False,  # Using Ruff instead
        "ruff.enable": True,
        "ruff.organizeImports": True,
        "ruff.fixAll": True,
        "ruff.lint.args": ["--config=pyproject.toml"],
        "isort.args": ["--profile", "black", "--settings-path=pyproject.toml"],
        "mypy-type-checker.importStrategy": "fromEnvironment",
        "mypy-type-checker.args": ["--config-file=pyproject.toml"],
        "mypy-type-checker.preferDaemon": True,
        "black-formatter.args": ["--config=pyproject.toml"],
        # Global editor settings
        "editor.formatOnSave": True,
        "editor.codeActionsOnSave": {
            "source.organizeImports": "explicit",
            "source.fixAll.ruff": "explicit",
        },
        "editor.inlayHints.enabled": "on",
        "editor.bracketPairColorization.enabled": True,
        "editor.guides.bracketPairs": "active",
        "editor.renderWhitespace": "trailing",
        "editor.unicodeHighlight.ambiguousCharacters": False,
        "editor.unicodeHighlight.invisibleCharacters": False,
        # Terminal configuration
        "terminal.integrated.defaultProfile.windows": "PowerShell",
        "terminal.integrated.cwd": "${workspaceFolder}",
        "terminal.integrated.env.windows": {"PYTHONPATH": "${workspaceFolder}/src"},
        # Git configuration
        "git.enableSmartCommit": True,
        "git.confirmSync": False,
        "git.autofetch": True,
        "git.ignoreLimitWarning": True,
        "git.openRepositoryInParentFolders": "never",
        # Error lens
        "errorLens.enabledDiagnosticLevels": ["error", "warning", "info"],
        "errorLens.enabledInDiffView": True,
        "errorLens.followCursor": "allLinesExceptActive",
        "errorLens.gutterIconsEnabled": True,
        # GitHub Copilot
        "github.copilot.enable": {
            "*": True,
            "yaml": True,
            "plaintext": True,
            "markdown": True,
            "python": True,
            "toml": True,
            "json": True,
            "jsonc": True,
        },
        "github.copilot.chat.localeOverride": "en",
        "github.copilot.advanced": {"debug.overrideEngine": "copilot-chat"},
        # Jupyter notebooks
        "workbench.editorAssociations": {"*.ipynb": "jupyter-notebook"},
        "notebook.cellToolbarLocation": {
            "default": "right",
            "jupyter-notebook": "left",
        },
        "jupyter.askForKernelRestart": False,
        "jupyter.alwaysTrustNotebooks": True,
        "jupyter.interactiveWindow.creationMode": "perFile",
        "jupyter.jupyterServerType": "local",
        # Python environment
        "python.envFile": "${workspaceFolder}/.env",
        "python.terminal.activateEnvironment": True,
        "python.terminal.activateEnvInCurrentTerminal": True,
        "python.terminal.executeInFileDir": False,
        "python.terminal.launchArgs": [],
        "python.experiments.optInto": [
            "pythonTerminalEnvVarActivation",
            "pythonTestAdapter",
        ],
        # File nesting
        "explorer.fileNesting.enabled": True,
        "explorer.fileNesting.expand": False,
        "explorer.fileNesting.patterns": {
            "*.py": "${capture}.pyc, ${capture}.pyo, ${capture}.pyd",
            "pyproject.toml": (
                "uv.lock, poetry.lock, Pipfile.lock, requirements*.txt, "
                "setup.py, setup.cfg, MANIFEST.in"
            ),
            "*.md": "${capture}.*.md",
            ".gitignore": (
                ".gitattributes, .gitmodules, .gitmessage, .mailmap, " ".git-blame*"
            ),
            "README*": (
                "AUTHORS, CHANGELOG*, CONTRIBUTING*, HISTORY*, LICENSE*, " "SECURITY*"
            ),
            "Dockerfile": (".dockerignore, docker-compose*.yml, docker-compose*.yaml"),
        },
        # Diff editor
        "diffEditor.experimental.showMoves": True,
        "diffEditor.renderSideBySide": True,
        # Timeline
        "timeline.excludeSources": ["git.fileHistory"],
    }


def get_modern_launch_config() -> dict[str, Any]:
    """
    Get modern launch configuration for debugging.

    Returns:
        Dictionary with VS Code launch configuration
    """
    return {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "Python: Current File",
                "type": "debugpy",
                "request": "launch",
                "program": "${file}",
                "console": "integratedTerminal",
                "cwd": "${workspaceFolder}",
                "env": {"PYTHONPATH": "${workspaceFolder}/src"},
                "justMyCode": True,
                "stopOnEntry": False,
                "showReturnValue": True,
            },
            {
                "name": "Python: Test Current File",
                "type": "debugpy",
                "request": "launch",
                "module": "pytest",
                "args": ["${file}", "-v", "--tb=short"],
                "console": "integratedTerminal",
                "cwd": "${workspaceFolder}",
                "env": {"PYTHONPATH": "${workspaceFolder}/src"},
                "justMyCode": True,
            },
            {
                "name": "Python: All Tests",
                "type": "debugpy",
                "request": "launch",
                "module": "pytest",
                "args": ["tests/", "-v", "--tb=short"],
                "console": "integratedTerminal",
                "cwd": "${workspaceFolder}",
                "env": {"PYTHONPATH": "${workspaceFolder}/src"},
                "justMyCode": True,
            },
            {
                "name": "Python: MCP Server",
                "type": "debugpy",
                "request": "launch",
                "module": "mcp",
                "console": "integratedTerminal",
                "cwd": "${workspaceFolder}",
                "env": {"PYTHONPATH": "${workspaceFolder}/src"},
                "justMyCode": False,
            },
        ],
    }


def get_modern_tasks_config() -> dict[str, Any]:
    """
    Get modern tasks configuration for build and test automation.

    Returns:
        Dictionary with VS Code tasks configuration
    """
    return {
        "version": "2.0.0",
        "tasks": [
            {
                "label": "Install Dependencies",
                "type": "shell",
                "command": "uv",
                "args": ["sync"],
                "group": "build",
                "presentation": {
                    "echo": True,
                    "reveal": "always",
                    "focus": False,
                    "panel": "shared",
                    "showReuseMessage": True,
                    "clear": False,
                },
                "problemMatcher": [],
            },
            {
                "label": "Run Tests",
                "type": "shell",
                "command": "uv",
                "args": ["run", "pytest", "tests/", "-v"],
                "group": {"kind": "test", "isDefault": True},
                "presentation": {
                    "echo": True,
                    "reveal": "always",
                    "focus": False,
                    "panel": "shared",
                },
                "problemMatcher": ["$python"],
            },
            {
                "label": "Run Tests with Coverage",
                "type": "shell",
                "command": "uv",
                "args": [
                    "run",
                    "pytest",
                    "tests/",
                    "--cov=src/mcp",
                    "--cov-report=html",
                    "--cov-report=term",
                ],
                "group": "test",
                "presentation": {
                    "echo": True,
                    "reveal": "always",
                    "focus": False,
                    "panel": "shared",
                },
                "problemMatcher": ["$python"],
            },
            {
                "label": "Format Code",
                "type": "shell",
                "command": "uv",
                "args": ["run", "black", "src/", "tests/", "setup/"],
                "group": "build",
                "presentation": {
                    "echo": True,
                    "reveal": "silent",
                    "focus": False,
                    "panel": "shared",
                },
                "problemMatcher": [],
            },
            {
                "label": "Lint Code",
                "type": "shell",
                "command": "uv",
                "args": ["run", "ruff", "check", "src/", "tests/", "setup/"],
                "group": "build",
                "presentation": {
                    "echo": True,
                    "reveal": "always",
                    "focus": False,
                    "panel": "shared",
                },
                "problemMatcher": ["$ruff"],
            },
            {
                "label": "Type Check",
                "type": "shell",
                "command": "uv",
                "args": ["run", "mypy", "src/"],
                "group": "build",
                "presentation": {
                    "echo": True,
                    "reveal": "always",
                    "focus": False,
                    "panel": "shared",
                },
                "problemMatcher": ["$mypy"],
            },
            {
                "label": "Build Documentation",
                "type": "shell",
                "command": "uv",
                "args": ["run", "mkdocs", "build"],
                "group": "build",
                "presentation": {
                    "echo": True,
                    "reveal": "always",
                    "focus": False,
                    "panel": "shared",
                },
                "problemMatcher": [],
            },
            {
                "label": "Serve Documentation",
                "type": "shell",
                "command": "uv",
                "args": ["run", "mkdocs", "serve"],
                "group": "build",
                "isBackground": True,
                "presentation": {
                    "echo": True,
                    "reveal": "always",
                    "focus": False,
                    "panel": "dedicated",
                },
                "problemMatcher": [],
            },
        ],
    }


def create_vscode_extensions_config() -> dict[str, Any]:
    """
    Get VS Code extensions recommendations.

    Returns:
        Dictionary with extension recommendations
    """
    return {
        "recommendations": RECOMMENDED_EXTENSIONS,
        "unwantedRecommendations": [
            "ms-python.pylint",
            "ms-python.flake8",
            "ms-python.autopep8",
        ],
    }


def get_vscode_settings() -> dict[str, Any]:
    """
    Get the default VS Code settings (legacy compatibility).

    Returns:
        Modern VS Code settings
    """
    return get_modern_vscode_settings()


def create_vscode_directory() -> Path:
    """
    Create the .vscode directory if it doesn't exist.

    Returns:
        Path to the .vscode directory
    """
    project_root = get_project_root()
    vscode_path = project_root / ".vscode"
    return ensure_directory_exists(vscode_path)


def should_create_settings_json() -> bool:
    """
    Check if VS Code settings.json should be created.

    Returns:
        True if settings.json doesn't exist or is invalid
    """
    project_root = get_project_root()
    settings_path = project_root / ".vscode" / "settings.json"

    if not settings_path.exists():
        return True

    try:
        with open(settings_path, encoding="utf-8") as f:
            json.load(f)
        return False  # Valid JSON exists
    except (json.JSONDecodeError, Exception):
        return True  # Invalid or unreadable JSON


def create_modern_vscode_settings() -> bool:
    """
    Create modern VS Code configuration files.

    Returns:
        True if successful, False otherwise
    """
    try:
        vscode_dir = create_vscode_directory()

        # Create settings.json
        settings_path = vscode_dir / "settings.json"
        with open(settings_path, "w", encoding="utf-8") as f:
            json.dump(get_modern_vscode_settings(), f, indent=2)

        # Create launch.json
        launch_path = vscode_dir / "launch.json"
        with open(launch_path, "w", encoding="utf-8") as f:
            json.dump(get_modern_launch_config(), f, indent=2)

        # Create tasks.json
        tasks_path = vscode_dir / "tasks.json"
        with open(tasks_path, "w", encoding="utf-8") as f:
            json.dump(get_modern_tasks_config(), f, indent=2)

        # Create extensions.json
        extensions_path = vscode_dir / "extensions.json"
        with open(extensions_path, "w", encoding="utf-8") as f:
            json.dump(create_vscode_extensions_config(), f, indent=2)

        return True
    except Exception:
        return False
