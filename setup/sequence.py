import subprocess
import sys
from pathlib import Path


def check_isort_installed() -> bool:
    """Check if isort is installed and available."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "isort", "--version"],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0
    except (FileNotFoundError, Exception):
        return False


def sort_imports_in_directory(directory_path, dry_run=False, verbose=False):
    """
    Sort imports in all Python files within the specified directory and subdirectories.

    Args:
        directory_path (str): Path to the directory to process
        dry_run (bool): If True, only show what would be changed without making changes
        verbose (bool): If True, show detailed output
    """
    directory = Path(directory_path)

    if not directory.exists():
        print(f"Error: Directory '{directory_path}' does not exist.")
        return False

    # Check if isort is installed
    if not check_isort_installed():
        print(
            "Error: isort is not installed. "
            "Please install it with: pip install isort"
        )
        print("You can also install it with: uv add --dev isort")
        return False

    # Find all Python files recursively
    python_files = list(directory.rglob("*.py"))

    if not python_files:
        print(f"No Python files found in '{directory_path}'")
        return True

    success = True
    files_modified = 0
    files_checked = 0

    print(f"Found {len(python_files)} Python files to process...")
    if dry_run:
        print("DRY RUN MODE: No files will be modified")
    print()

    # Build common isort arguments - ensure we use project configuration
    # and configure correctly for Ruff compatibility
    isort_args = [
        "--profile",
        "black",  # Use black profile for compatibility
        "--use-parentheses",  # Use parentheses for imports
        "--combine-as",  # Combine as imports
        "--force-sort-within-sections",  # Force sort within sections
        "--ensure-newline-before-comments",  # Ensure newline before comments
    ]

    # Look for pyproject.toml in project root
    project_root = directory
    while project_root != project_root.parent:
        if (project_root / "pyproject.toml").exists():
            # Found pyproject.toml, use it for configuration
            isort_args.append("--settings-path")
            isort_args.append(str(project_root))
            break
        project_root = project_root.parent

    for py_file in python_files:
        files_checked += 1
        try:
            # Always check if file needs sorting first
            check_cmd = [sys.executable, "-m", "isort", "--check-only", "--diff"]
            check_cmd.extend(isort_args)
            check_cmd.append(str(py_file))

            check_result = subprocess.run(
                check_cmd,
                capture_output=True,
                text=True,
                check=False,
            )

            # If check shows differences, the file needs sorting
            if check_result.returncode != 0:
                action = "[DRY RUN] Would fix" if dry_run else "Fixing"
                print(f"{action} {py_file}")

                if verbose and check_result.stdout:
                    print("  Changes to be made:")
                    for line in check_result.stdout.split("\n"):
                        if line.strip():
                            print(f"    {line}")

                if not dry_run:
                    # Run the actual sort
                    sort_cmd = [sys.executable, "-m", "isort"]
                    sort_cmd.extend(isort_args)
                    sort_cmd.append(str(py_file))

                    sort_result = subprocess.run(
                        sort_cmd,
                        capture_output=True,
                        text=True,
                        check=False,
                    )

                    if sort_result.returncode == 0:
                        files_modified += 1
                        if verbose:
                            print(f"  ✓ Successfully sorted imports in {py_file}")
                    else:
                        print(f"  ✗ Error processing {py_file}: {sort_result.stderr}")
                        if verbose and sort_result.stdout:
                            print(f"    Output: {sort_result.stdout}")
                        success = False
                else:
                    files_modified += 1  # Count would-be modifications in dry run
            else:
                # File is already sorted
                if verbose:
                    print(f"✓ {py_file} (already sorted)")

        except FileNotFoundError:
            print("Error: Could not find isort. Please ensure it's installed.")
            return False
        except Exception as e:
            print(f"Error processing {py_file}: {str(e)}")
            success = False

    print()
    if dry_run:
        print(
            f"DRY RUN SUMMARY: {files_modified} files would be modified "
            f"out of {files_checked} checked"
        )
    else:
        print(
            f"SUMMARY: Modified {files_modified} files "
            f"out of {files_checked} checked"
        )

    return success


def main():
    """Main entry point for the script."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Sort imports in Python files using isort",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python setup/tools/isort.py                    # Sort all files in setup/
  python setup/tools/isort.py --dry-run          # Show what would be changed
  python setup/tools/isort.py --verbose          # Show detailed output
  python setup/tools/isort.py src/               # Sort files in src/ directory
        """,
    )
    parser.add_argument(
        "directory", nargs="?", help="Directory to process (default: setup/)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without making changes",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed output"
    )
    parser.add_argument(
        "--fix-all",
        action="store_true",
        help="Process the entire project directory instead of just setup/",
    )

    args = parser.parse_args()

    # Determine which directory to process
    if args.directory:
        target_dir = Path(args.directory)
    elif args.fix_all:
        # Go up from tools/ to setup/ to project root
        target_dir = Path(__file__).parent.parent.parent
    else:
        # Default to the setup directory relative to this script
        target_dir = Path(__file__).parent.parent  # Go up from tools/ to setup/

    print(f"Sorting imports in: {target_dir}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'MODIFY FILES'}")
    print()

    success = sort_imports_in_directory(
        target_dir, dry_run=args.dry_run, verbose=args.verbose
    )

    if success:
        print("Import sorting completed successfully.")
    else:
        print("Import sorting completed with errors.")
        sys.exit(1)


if __name__ == "__main__":
    main()
