"""
Path Utilities
Modern path-related utilities for project structure validation with performance
optimization.
"""

import functools
import os
import threading
from pathlib import Path
from typing import Any

from .constants import OPTIONAL_PROJECT_PATHS, REQUIRED_PROJECT_PATHS

# Thread-safe caching for expensive path operations
_path_cache: dict[str, Any] = {}
_cache_lock = threading.RLock()


@functools.lru_cache(maxsize=128)
def get_project_root() -> Path:
    """
    Get the project root directory with caching for performance.

    Returns:
        Path: Absolute path to the project root

    Raises:
        RuntimeError: If project root cannot be determined
    """
    current = Path(__file__).resolve()

    # Look for project markers going up the directory tree
    markers = ("pyproject.toml", "setup.py", ".git")

    for parent in [current] + list(current.parents):
        if any((parent / marker).exists() for marker in markers):
            return parent

    # Fallback: assume we're in setup/environment, so go up 2 levels
    fallback = current.parent.parent
    if fallback.name == "python-sdk" or (fallback / "src").exists():
        return fallback

    raise RuntimeError(f"Cannot determine project root from {current}")


def check_required_paths() -> tuple[bool, list[str]]:
    """
    Check if all required project paths exist.

    Returns:
        Tuple of (all_exist, missing_paths)
    """
    cache_key = "required_paths_check"

    with _cache_lock:
        if cache_key in _path_cache:
            return _path_cache[cache_key]

    project_root = get_project_root()
    missing_paths: list[str] = []

    for required_path in REQUIRED_PROJECT_PATHS:
        path = project_root / required_path
        if not path.exists():
            missing_paths.append(required_path)

    result = (len(missing_paths) == 0, missing_paths)

    with _cache_lock:
        _path_cache[cache_key] = result

    return result


def get_optional_paths_status() -> dict[str, bool]:
    """
    Get the existence status of optional project paths.

    Returns:
        Dict mapping path names to their existence status
    """
    cache_key = "optional_paths_status"

    with _cache_lock:
        if cache_key in _path_cache:
            return _path_cache[cache_key]

    project_root = get_project_root()
    status = {}

    for optional_path in OPTIONAL_PROJECT_PATHS:
        path = project_root / optional_path
        status[optional_path] = path.exists()

    with _cache_lock:
        _path_cache[cache_key] = status

    return status


def ensure_directory_exists(directory_path: Path) -> Path:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        directory_path: Path to the directory

    Returns:
        Path: The directory path (for chaining)

    Raises:
        OSError: If directory cannot be created
    """
    try:
        directory_path.mkdir(parents=True, exist_ok=True)
        return directory_path
    except OSError as e:
        raise OSError(f"Failed to create directory {directory_path}: {e}") from e


def clear_path_cache() -> None:
    """Clear the path cache for testing or when project structure changes."""
    with _cache_lock:
        _path_cache.clear()

    # Clear the LRU cache as well
    get_project_root.cache_clear()


def get_directory_size(directory_path: Path) -> int:
    """
    Get the total size of a directory in bytes.

    Args:
        directory_path: Path to the directory

    Returns:
        Total size in bytes
    """
    total_size = 0

    if not directory_path.exists() or not directory_path.is_dir():
        return total_size

    try:
        for dirpath, _dirnames, filenames in os.walk(directory_path):
            for filename in filenames:
                filepath = Path(dirpath) / filename
                try:
                    total_size += filepath.stat().st_size
                except (OSError, FileNotFoundError):
                    # Skip files we can't access
                    continue
    except (OSError, PermissionError):
        # Return partial size if we can't access everything
        pass

    return total_size


def is_project_structure_valid() -> bool:
    """
    Quick validation of project structure.

    Returns:
        True if the project structure appears valid
    """
    all_exist, _ = check_required_paths()
    return all_exist


def get_relative_path(full_path: Path, base_path: Path | None = None) -> str:
    """
    Get a relative path string from a full path.

    Args:
        full_path: The full path to convert
        base_path: The base path to make relative to (defaults to project root)

    Returns:
        Relative path as string
    """
    if base_path is None:
        base_path = get_project_root()

    try:
        return str(full_path.relative_to(base_path))
    except ValueError:
        # Path is not relative to base_path
        return str(full_path)


def find_files_by_pattern(pattern: str, base_path: Path | None = None) -> list[Path]:
    """
    Find files matching a pattern in the project.

    Args:
        pattern: Glob pattern to search for
        base_path: Base path to search from (defaults to project root)

    Returns:
        List of matching file paths
    """
    if base_path is None:
        base_path = get_project_root()

    return list(base_path.rglob(pattern))
