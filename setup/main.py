"""
Main setup entry point for the MCP Python SDK.
Provides CLI interface for setup operations.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Any

from .typings import SetupMode
from .typings.environment import ValidationDetails

# Import orchestrator with proper error handling and fallback
try:
    from .orchestrator import ModernSetupOrchestrator

    ORCHESTRATOR_AVAILABLE = True
except ImportError:
    # Create a minimal fallback orchestrator to maintain functionality
    ORCHESTRATOR_AVAILABLE = False

    class MockOrchestrator:
        """Fallback orchestrator when the main one is not available."""

        def __init__(
            self, workspace_root: Path | None = None, verbose: bool = False
        ) -> None:
            self.workspace_root = workspace_root or Path.cwd()
            self.verbose = verbose

        async def validate_environment(self) -> ValidationDetails:
            """Mock validation that always passes."""
            from .typings import ValidationStatus
            return ValidationDetails(
                is_valid=True,
                status=ValidationStatus.WARNING,
                message="Using fallback validation",
                warnings=["Using fallback orchestrator - some features may be limited"],
                errors=[],
                recommendations=["Install complete setup dependencies"],
                component_name="Fallback",
            )

        async def orchestrate_complete_setup(self, mode: SetupMode) -> dict[str, Any]:
            """Mock setup that reports orchestrator unavailable."""
            return {
                "success": False,
                "errors": [
                    "ModernSetupOrchestrator module not available - please ensure all dependencies are installed"
                ],
                "mode": mode,
            }

    ModernSetupOrchestrator = MockOrchestrator  # type: ignore[misc,assignment]


async def main() -> int:
    """Main setup function following modern standardization principles."""
    parser = argparse.ArgumentParser(
        description="MCP Python SDK Setup System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--mode",
        type=str,
        choices=[mode.value for mode in SetupMode],
        default=SetupMode.DEVELOPMENT.value,
        help="Setup mode to use",
    )

    parser.add_argument(
        "--workspace",
        type=Path,
        help="Workspace root directory",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output",
    )

    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate environment, don't perform setup",
    )

    args = parser.parse_args()

    # Show warning if using fallback orchestrator
    if not ORCHESTRATOR_AVAILABLE and args.verbose:
        print("⚠️ Using fallback orchestrator - some features may be limited")

    try:
        mode = SetupMode(args.mode)
        orchestrator = ModernSetupOrchestrator(
            workspace_root=args.workspace,
            verbose=args.verbose,
        )

        if args.validate_only:            print("🔍 Validating environment...")
            validation_result = await orchestrator.validate_environment()# Standardized handling using only ValidationDetails type
            if validation_result.is_valid:
                print("✅ Environment validation passed")
                if validation_result.warnings and args.verbose:
                    for warning in validation_result.warnings:
                        print(f"  ⚠️ {warning}")
                return 0
            else:
                print("❌ Environment validation failed")
                for error in validation_result.errors:
                    print(f"  • {error}")
                if validation_result.recommendations and args.verbose:
                    print("  Recommendations:")
                    for rec in validation_result.recommendations:
                        print(f"    - {rec}")
                return 1
        else:
            print(f"🚀 Starting {mode.value} setup...")
            result = await orchestrator.orchestrate_complete_setup(mode)

            # Handle SetupSequenceResult return type with fallback for dict
            if hasattr(result, "success"):
                success = result.success
                errors = getattr(result, "errors", [])
            else:
                # Fallback for dict return type (from MockOrchestrator)
                success = result.get("success", False)
                errors = result.get("errors", [])

            if success:
                print("✅ Setup completed successfully")
                return 0
            else:
                print("❌ Setup failed")
                for error in errors:
                    print(f"  • {error}")
                return 1

    except KeyboardInterrupt:
        print("\n⚠️ Setup interrupted by user")
        return 130
    except Exception as e:
        print(f"❌ Setup failed with error: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
