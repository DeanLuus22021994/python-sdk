"""
Setup Sequence Management
Orchestrates the setup process for the MCP Python SDK
"""

from typing import Any

from .environment import (
    check_required_paths,
    validate_python_version,
)
from .packages import get_packages_for_platform


class SetupOrchestrator:
    """
    Main orchestrator for the MCP Python SDK setup process.

    Follows the Single Responsibility Principle by coordinating
    different setup components without implementing their logic.
    """

    def __init__(self, verbose: bool = False) -> None:
        self.verbose = verbose
        self.results: dict[str, Any] = {}

    def run_complete_setup(self) -> bool:
        """
        Run the complete setup sequence.

        Returns:
            True if all setup steps completed successfully
        """
        try:
            # Validate environment
            python_valid, python_msg = validate_python_version()
            self.results["python_validation"] = {
                "valid": python_valid,
                "message": python_msg,
            }

            if not python_valid:
                print(f"❌ Python validation failed: {python_msg}")
                return False

            # Check required paths
            paths_valid, missing_paths = check_required_paths()
            self.results["paths_validation"] = {
                "valid": paths_valid,
                "missing": missing_paths,
            }

            if not paths_valid:
                print(f"❌ Required paths missing: {missing_paths}")
                return False

            # Validate packages
            platform_packages = get_packages_for_platform()
            self.results["platform_packages"] = platform_packages

            if self.verbose:
                print(f"✅ Platform packages: {len(platform_packages)} available")

            return True

        except Exception as e:
            print(f"❌ Setup failed with error: {e}")
            self.results["error"] = str(e)
            return False

    def get_setup_results(self) -> dict[str, Any]:
        """Get detailed setup results."""
        return self.results.copy()


def run_setup_sequence() -> bool:
    """
    Run the complete setup sequence for the MCP Python SDK.

    Returns:
        True if all setup steps completed successfully
    """
    print("🚀 Starting MCP Python SDK Setup")
    print("=" * 50)

    success = True

    # Step 1: Validate Python version
    print("\nStep 1: Validating Python environment")
    python_valid, python_msg = validate_python_version()
    if python_valid:
        print(f"✅ {python_msg}")
    else:
        print(f"❌ {python_msg}")
        success = False

    # Step 2: Check required paths
    print("\nStep 2: Checking project structure")
    paths_valid, missing_paths = check_required_paths()
    if paths_valid:
        print("✅ All required project paths exist")
    else:
        print(f"❌ Missing required paths: {missing_paths}")
        success = False

    # Step 3: Check platform packages
    print("\nStep 3: Checking platform packages")
    try:
        platform_packages = get_packages_for_platform()
        print(f"✅ Platform packages available: {len(platform_packages)}")
    except Exception as e:
        print(f"❌ Package check failed: {e}")
        success = False

    return success


if __name__ == "__main__":
    success = run_setup_sequence()
    exit(0 if success else 1)
