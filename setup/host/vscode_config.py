"""VS Code configuration module for Python SDK setup."""

import json
from pathlib import Path
from typing import Any

from .constants import RECOMMENDED_EXTENSIONS
from .path_utils import get_project_root


def create_vscode_directory() -> Path:
    """
    Create .vscode directory if it doesn't exist.

    Returns:
        Path to the .vscode directory
    """
    project_root = get_project_root()
    vscode_path = project_root / ".vscode"
    vscode_path.mkdir(exist_ok=True)
    return vscode_path


def get_modern_vscode_settings() -> dict[str, Any]:
    """
    Get modern VS Code settings optimized for Python SDK development.

    Returns:
        Dictionary with comprehensive VS Code settings
    """
    return {
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
        "python.linting.enabled": False,
        "ruff.enable": True,
        "ruff.organizeImports": True,
        "ruff.fixAll": True,
        "ruff.lint.args": ["--config=pyproject.toml"],
        "mypy-type-checker.importStrategy": "fromEnvironment",
        "mypy-type-checker.args": ["--config-file=pyproject.toml"],
        "mypy-type-checker.preferDaemon": True,
        "black-formatter.args": ["--config=pyproject.toml"],
        "python.analysis.diagnosticSeverityOverrides": {
            "reportUnknownVariableType": "none",
            "reportOptionalMemberAccess": "none",
            "reportArgumentType": "none",
            "reportMissingImports": "warning",
        },
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
        "terminal.integrated.defaultProfile.windows": "PowerShell",
        "terminal.integrated.cwd": "${workspaceFolder}",
        "terminal.integrated.env.windows": {"PYTHONPATH": "${workspaceFolder}/src"},
        "git.enableSmartCommit": True,
        "git.confirmSync": False,
        "git.autofetch": True,
        "git.ignoreLimitWarning": True,
        "git.openRepositoryInParentFolders": "never",
        "errorLens.enabledDiagnosticLevels": ["error", "warning", "info"],
        "errorLens.enabledInDiffView": True,
        "errorLens.followCursor": "allLinesExceptActive",
        "errorLens.gutterIconsEnabled": True,
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
        "workbench.editorAssociations": {"*.ipynb": "jupyter-notebook"},
        "notebook.cellToolbarLocation": {
            "default": "right",
            "jupyter-notebook": "left",
        },
        "jupyter.askForKernelRestart": False,
        "jupyter.alwaysTrustNotebooks": True,
        "jupyter.interactiveWindow.creationMode": "perFile",
        "jupyter.jupyterServerType": "local",
        "python.envFile": "${workspaceFolder}/.env",
        "python.terminal.activateEnvironment": True,
        "python.terminal.activateEnvInCurrentTerminal": True,
        "python.terminal.executeInFileDir": False,
        "python.terminal.launchArgs": [],
        "python.experiments.optInto": [
            "pythonTerminalEnvVarActivation",
            "pythonTestAdapter",
        ],
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
                "AUTHORS, CHANGELOG*, CONTRIBUTING*, HISTORY*, " "LICENSE*, SECURITY*"
            ),
            "Dockerfile": (".dockerignore, docker-compose*.yml, docker-compose*.yaml"),
        },
        "diffEditor.experimental.showMoves": True,
        "diffEditor.renderSideBySide": True,
        "timeline.excludeSources": ["git.fileHistory"],
        "docker.host": "unix:///var/run/docker.sock",
        "docker.enableTelemetry": False,
        "docker.showStartPage": False,
        "docker.formatComposeFiles": True,
        "docker.truncateStrings": False,
    }


def get_vscode_settings() -> dict[str, Any]:
    """
    Get basic VS Code settings.

    Returns:
        Dictionary with basic VS Code settings
    """
    return {
        "python.defaultInterpreterPath": "./venv/Scripts/python.exe",
        "python.analysis.diagnosticSeverityOverrides": {
            "reportUnknownVariableType": "none",
            "reportOptionalMemberAccess": "none",
            "reportArgumentType": "none",
        },
        "python.testing.pytestEnabled": True,
        "python.testing.unittestEnabled": False,
        "python.testing.pytestArgs": ["tests"],
        "python.linting.enabled": False,
        "ruff.enable": True,
        "ruff.organizeImports": True,
    }


def create_modern_vscode_settings() -> bool:
    """
    Create modern VS Code settings files.

    Returns:
        True if settings were created successfully, False otherwise
    """
    try:
        vscode_dir = create_vscode_directory()
        settings_path = vscode_dir / "settings.json"

        if not settings_path.exists():
            settings = get_modern_vscode_settings()
            with open(settings_path, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2)

        return True
    except Exception:
        return False


def get_modern_launch_config() -> dict[str, Any]:
    """
    Get modern VS Code launch configuration.

    Returns:
        Dictionary with launch configuration
    """
    return {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "Python: Current File",
                "type": "python",
                "request": "launch",
                "program": "${file}",
                "console": "integratedTerminal",
                "justMyCode": True,
            },
            {
                "name": "Python: Run Tests",
                "type": "python",
                "request": "launch",
                "module": "pytest",
                "args": ["tests/", "-v"],
                "console": "integratedTerminal",
                "justMyCode": False,
            },
            {
                "name": "Python: Setup Script",
                "type": "python",
                "request": "launch",
                "program": "${workspaceFolder}/setup.py",
                "console": "integratedTerminal",
                "justMyCode": True,
            },
        ],
    }


def get_modern_tasks_config() -> dict[str, Any]:
    """
    Get modern VS Code tasks configuration.

    Returns:
        Dictionary with tasks configuration
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
                "presentation": {"echo": True, "reveal": "always", "panel": "new"},
                "problemMatcher": [],
            },
            {
                "label": "Run Tests",
                "type": "shell",
                "command": "uv",
                "args": ["run", "pytest", "tests/", "-v"],
                "group": {"kind": "test", "isDefault": True},
                "presentation": {"echo": True, "reveal": "always", "panel": "new"},
                "problemMatcher": [],
            },
            {
                "label": "Format Code",
                "type": "shell",
                "command": "uv",
                "args": ["run", "black", "src/", "tests/", "setup/"],
                "group": "build",
                "presentation": {"echo": True, "reveal": "always", "panel": "new"},
                "problemMatcher": [],
            },
            {
                "label": "Lint Code",
                "type": "shell",
                "command": "uv",
                "args": ["run", "ruff", "check", "src/", "tests/", "setup/"],
                "group": "build",
                "presentation": {"echo": True, "reveal": "always", "panel": "new"},
                "problemMatcher": [],
            },
        ],
    }


def create_vscode_extensions_config() -> dict[str, Any]:
    """
    Get recommended VS Code extensions configuration.

    Returns:
        Dictionary with extensions configuration
    """
    return {
        "recommendations": list(RECOMMENDED_EXTENSIONS),
        "unwantedRecommendations": [
            "ms-python.pylint",
            "ms-python.flake8",
        ],
    }


def should_create_settings_json() -> bool:
    """
    Check if VS Code settings.json should be created.

    Returns:
        True if settings.json doesn't exist or is invalid
    """
    try:
        vscode_dir = create_vscode_directory()
        settings_path = vscode_dir / "settings.json"

        if not settings_path.exists():
            return True

        with open(settings_path, encoding="utf-8") as f:
            json.load(f)  # Test if valid JSON
        return False
    except (json.JSONDecodeError, Exception):
        return True
