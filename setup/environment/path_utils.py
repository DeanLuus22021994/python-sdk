"""
Path utilities for environment operations.
"""

import functools
from pathlib import Path


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
