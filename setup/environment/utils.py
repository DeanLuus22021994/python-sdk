"""
Environment Utilities
Common utilities for environment operations.
"""

from __future__ import annotations

import asyncio
import functools
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class CommandResult:
    """Result of a command execution."""

    returncode: int
    stdout: str | None = None
    stderr: str | None = None
    timeout_expired: bool = False


@functools.lru_cache(maxsize=1)
def get_project_root() -> Path:
    """
    Get the project root directory with caching.

    Returns:
        Path to the project root directory

    Raises:
        RuntimeError: If project root cannot be determined
    """
    current = Path(__file__).resolve()

    # Look for project markers
    markers = ("pyproject.toml", "setup.py", ".git")

    for parent in [current] + list(current.parents):
        if any((parent / marker).exists() for marker in markers):
            return parent

    # Fallback: assume we're in setup/environment, go up 2 levels
    fallback = current.parent.parent
    if fallback.name == "python-sdk" or (fallback / "src").exists():
        return fallback

    raise RuntimeError(f"Cannot determine project root from {current}")


async def run_with_timeout(
    cmd: list[str],
    timeout: float = 10.0,
    cwd: Path | None = None,
) -> CommandResult:
    """
    Run a command with timeout asynchronously.

    Args:
        cmd: Command to run
        timeout: Timeout in seconds
        cwd: Working directory

    Returns:
        Command result
    """
    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd,
        )

        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=timeout,
        )

        return CommandResult(
            returncode=process.returncode or 0,
            stdout=stdout.decode() if stdout else None,
            stderr=stderr.decode() if stderr else None,
        )

    except asyncio.TimeoutError:
        return CommandResult(
            returncode=-1,
            timeout_expired=True,
        )
    except Exception:
        return CommandResult(returncode=-1)


def ensure_directory_exists(path: Path) -> Path:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        path: Directory path

    Returns:
        The directory path

    Raises:
        OSError: If directory cannot be created
    """
    try:
        path.mkdir(parents=True, exist_ok=True)
        return path
    except OSError as e:
        raise OSError(f"Failed to create directory {path}: {e}") from e


def clear_caches() -> None:
    """Clear all cached values."""
    get_project_root.cache_clear()
