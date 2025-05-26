"""
Path Utilities
Path-related utilities for project structure validation
"""

from pathlib import Path

from setup.environment.constants import OPTIONAL_PROJECT_PATHS, REQUIRED_PROJECT_PATHS


def get_project_root() -> Path:
    """
    Get the project root directory.

    Returns:
        Path to the project root directory
    """
    # Start from the current file and go up to find the project root
    current_file = Path(__file__)
    project_root = current_file.parent.parent.parent

    # Verify this is actually the project root by checking for key files
    if (project_root / "pyproject.toml").exists():
        return project_root

    # If not found, try going up one more level
    project_root = project_root.parent
    if (project_root / "pyproject.toml").exists():
        return project_root

    # Fallback to current working directory
    return Path.cwd()


def check_required_paths() -> tuple[bool, list[str]]:
    """
    Check if all required project paths exist.

    Returns:
        Tuple of (all_exist, missing_paths)
    """
    project_root = get_project_root()
    missing_paths = [
        path for path in REQUIRED_PROJECT_PATHS if not (project_root / path).exists()
    ]

    return len(missing_paths) == 0, missing_paths


def get_optional_paths_status() -> dict[str, bool]:
    """
    Get the status of optional project paths.

    Returns:
        Dictionary mapping path to existence status
    """
    project_root = get_project_root()
    return {path: (project_root / path).exists() for path in OPTIONAL_PROJECT_PATHS}


def ensure_directory_exists(directory_path: Path) -> Path:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        directory_path: Path to the directory to ensure exists

    Returns:
        Path to the directory
    """
    directory_path.mkdir(parents=True, exist_ok=True)
    return directory_path


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
