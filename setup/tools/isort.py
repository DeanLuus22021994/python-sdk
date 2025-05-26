import subprocess
import sys
from pathlib import Path


def sort_imports_in_directory(directory_path):
    """
    Sort imports in all Python files within the specified directory and subdirectories.

    Args:
        directory_path (str): Path to the directory to process
    """
    directory = Path(directory_path)

    if not directory.exists():
        print(f"Error: Directory '{directory_path}' does not exist.")
        return False

    # Find all Python files recursively
    python_files = list(directory.rglob("*.py"))

    if not python_files:
        print(f"No Python files found in '{directory_path}'")
        return True

    success = True

    for py_file in python_files:
        try:
            # Run isort on each file
            result = subprocess.run(
                [sys.executable, "-m", "isort", str(py_file)],
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode == 0:
                # Check if file was modified by looking at output
                if "Fixing" in result.stderr or result.stderr.strip():
                    print(f"Fixing {py_file}")
                # isort doesn't always output "Fixing" message, so we might
                # not see output for unchanged files
            else:
                print(f"Error processing {py_file}: {result.stderr}")
                success = False

        except Exception as e:
            print(f"Error processing {py_file}: {str(e)}")
            success = False

    return success


def main():
    """Main entry point for the script."""
    # Default to the setup directory relative to this script
    script_dir = Path(__file__).parent.parent  # Go up from tools/ to setup/
    setup_dir = script_dir

    # Allow command line argument to override the directory
    if len(sys.argv) > 1:
        setup_dir = Path(sys.argv[1])

    print(f"Sorting imports in: {setup_dir}")
    success = sort_imports_in_directory(setup_dir)

    if success:
        print("Import sorting completed successfully.")
    else:
        print("Import sorting completed with errors.")
        sys.exit(1)


if __name__ == "__main__":
    main()
