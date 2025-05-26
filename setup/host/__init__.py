"""
Host Setup Package
Provides host-based development environment setup for MCP Python SDK.
"""

from pathlib import Path

from ..vscode.integration import VSCodeIntegrationManager
from .env_validator import get_environment_info, validate_environment
from .package_manager import check_package_availability, setup_packages
from .sdk_validator import check_sdk_completeness, validate_sdk


class HostSetupManager:
    """
    Host-based setup manager following Single Responsibility Principle.

    Coordinates host environment setup without Docker dependencies.
    """

    def __init__(self, verbose: bool = False) -> None:
        self.verbose = verbose
        self._setup_results: dict[str, bool] = {}

    def setup(self) -> tuple[bool, dict[str, bool]]:
        """
        Perform complete host-based setup.

        Returns:
            Tuple of (success, setup_results)
        """
        print("🏠 Starting host-based setup...")

        # Environment validation
        env_valid, env_info = validate_environment()
        self._setup_results["environment"] = env_valid
        if self.verbose:
            print(f"Environment validation: {'✓' if env_valid else '✗'}")

        # Package setup
        packages_success = setup_packages()
        self._setup_results["packages"] = packages_success
        if self.verbose:
            print(
                f"Package setup: {'✓' if packages_success else '✗'}"
            )  # VS Code configuration
        try:
            vscode_manager = VSCodeIntegrationManager(Path.cwd())
            vscode_success = vscode_manager.create_all_configurations()
        except Exception:
            vscode_success = False
        self._setup_results["vscode"] = vscode_success
        if self.verbose:
            print(f"VS Code setup: {'✓' if vscode_success else '✗'}")

        # SDK validation
        sdk_valid = validate_sdk()
        self._setup_results["sdk"] = sdk_valid
        if self.verbose:
            print(f"SDK validation: {'✓' if sdk_valid else '✗'}")

        overall_success = all(self._setup_results.values())

        if overall_success:
            print("✅ Host setup completed successfully!")
        else:
            print("❌ Host setup completed with some issues.")

        return overall_success, self._setup_results

    def validate(self) -> bool:
        """
        Validate current host environment.

        Returns:
            True if environment is valid for development
        """
        env_valid, _ = validate_environment()
        sdk_completeness = check_sdk_completeness()

        return env_valid and all(sdk_completeness.values())

    def get_status(self) -> dict[str, bool | dict[str, bool]]:
        """
        Get current host environment status.

        Returns:
            Dictionary with environment status information
        """
        env_valid, env_info = validate_environment()
        sdk_status = check_sdk_completeness()

        return {
            "environment_valid": env_valid,
            "environment_details": env_info,
            "sdk_components": sdk_status,
            "setup_results": self._setup_results,
        }


__version__ = "1.0.0"
__all__ = [
    # Main manager
    "HostSetupManager",
    # Validation functions
    "validate_environment",
    "get_environment_info",
    "validate_sdk",
    "check_sdk_completeness",
    # Setup functions
    "setup_packages",
    "VSCodeIntegrationManager",
    # Utility functions
    "check_package_availability",
    "get_current_vscode_settings",
]
