"""
MCP Python SDK Setup - Package Entry Point

Modern, modular setup system entry point following standardization principles.
Enables running the setup system via: python -m setup

Follows modernization principles:
- DRY: No code duplication, clean import handling
- SRP: Single responsibility for CLI coordination
- STRUCTURED: Clean architecture with proper separation
- MONOLITHIC: Single entry point with standardized interface
- MODERNIZATION: Modern Python patterns and type annotations
- STANDARDIZATION: Consistent patterns throughout
- IDEMPOTENCY: Safe to run multiple times
- SOLID: All SOLID principles implemented
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

# Robust import handling for package execution
_setup_path = Path(__file__).parent
if str(_setup_path.parent) not in sys.path:
    sys.path.insert(0, str(_setup_path.parent))

if TYPE_CHECKING:
    from .orchestrator import ModernSetupOrchestrator
    from .typings.enums import SetupMode
else:
    ModernSetupOrchestrator = None
    SetupMode = None

    # Try multiple import strategies following DRY principle
    try:
        # Strategy 1: Relative imports (standard package execution)
        from .orchestrator import ModernSetupOrchestrator
        from .typings.enums import SetupMode
    except ImportError:
        try:
            # Strategy 2: Absolute imports (fallback)
            from setup.orchestrator import ModernSetupOrchestrator
            from setup.typings.enums import SetupMode
        except ImportError:
            # Strategy 3: Create minimal fallback classes following SRP
            class _FallbackSetupMode:
                """Fallback SetupMode implementation following SOLID principles."""

                DEVELOPMENT = "development"
                PRODUCTION = "production"
                DOCKER = "docker"

                def __init__(self, value: str) -> None:
                    self.value = value

                @classmethod
                def get_values(cls) -> list[str]:
                    """Get all available setup mode values."""
                    return [cls.DEVELOPMENT, cls.PRODUCTION, cls.DOCKER]

            class _FallbackOrchestrator:
                """Fallback orchestrator implementation following SOLID principles."""

                def __init__(
                    self, workspace_root: Path | None = None, verbose: bool = False
                ) -> None:
                    self.workspace_root = workspace_root
                    self.verbose = verbose

                async def validate_environment(self) -> Any:
                    """Fallback validation with clear messaging."""
                    print(
                        "⚠️ Using fallback orchestrator - full functionality not available"
                    )
                    return type(
                        "ValidationResult",
                        (),
                        {
                            "is_valid": True,
                            "warnings": ["Fallback mode active"],
                            "errors": [],
                            "recommendations": ["Install full setup dependencies"],
                        },
                    )()

                async def orchestrate_complete_setup(self, mode: Any) -> Any:
                    """Fallback setup with clear messaging."""
                    print("⚠️ Using fallback orchestrator - setup not performed")
                    return type(
                        "SetupResult",
                        (),
                        {
                            "success": False,
                            "errors": ["Full orchestrator not available"],
                            "warnings": ["Using minimal fallback implementation"],
                        },
                    )()

            SetupMode = _FallbackSetupMode
            ModernSetupOrchestrator = _FallbackOrchestrator


def create_argument_parser() -> argparse.ArgumentParser:
    """
    Create and configure the argument parser.

    Follows SRP by handling only argument parsing configuration.
    Implements STANDARDIZATION through consistent CLI interface.
    """
    parser = argparse.ArgumentParser(
        description="MCP Python SDK Setup System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m setup                           # Development mode setup
  python -m setup --mode production         # Production mode setup
  python -m setup --mode docker             # Docker mode setup
  python -m setup --validate-only           # Validation only
  python -m setup --verbose                 # Verbose output
        """,
    )

    # Handle both enum and fallback SetupMode following MODERNIZATION
    if hasattr(SetupMode, "__members__"):
        # Real enum implementation
        choices = [mode.value for mode in SetupMode]
        default = SetupMode.DEVELOPMENT.value
    else:
        # Fallback class implementation
        choices = SetupMode.get_values()
        default = SetupMode.DEVELOPMENT

    parser.add_argument(
        "--mode",
        type=str,
        choices=choices,
        default=default,
        help="Setup mode to use (default: %(default)s)",
        metavar="MODE",
    )

    parser.add_argument(
        "--workspace",
        type=Path,
        help="Workspace root directory (default: current directory)",
        metavar="PATH",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output with detailed logging",
    )

    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate environment, don't perform setup",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="MCP Python SDK Setup System 2.0.0",
    )

    return parser


async def handle_validation_only(orchestrator: Any, verbose: bool) -> int:
    """
    Handle validation-only operations.

    Follows SRP by handling only validation display logic.
    Implements STRUCTURED output formatting.
    """
    print("🔍 Validating environment...")
    validation_result = await orchestrator.validate_environment()

    if validation_result.is_valid:
        print("✅ Environment validation passed")

        if hasattr(validation_result, "warnings") and validation_result.warnings:
            if verbose:
                print("⚠️ Warnings found:")
                for warning in validation_result.warnings:
                    print(f"    • {warning}")
            else:
                print(
                    f"⚠️ {len(validation_result.warnings)} warning(s) found (use --verbose for details)"
                )

        return 0
    else:
        print("❌ Environment validation failed")

        if hasattr(validation_result, "errors") and validation_result.errors:
            print("❌ Errors:")
            for error in validation_result.errors:
                print(f"    • {error}")

        if (
            hasattr(validation_result, "recommendations")
            and validation_result.recommendations
        ):
            if verbose:
                print("💡 Recommendations:")
                for rec in validation_result.recommendations:
                    print(f"    • {rec}")
            else:
                print(
                    f"💡 {len(validation_result.recommendations)} recommendation(s) available (use --verbose for details)"
                )

        return 1


async def handle_setup_mode(orchestrator: Any, mode: Any, verbose: bool) -> int:
    """
    Handle setup operations for the specified mode.

    Follows SRP by handling only setup execution and result display.
    Implements IDEMPOTENCY through safe execution patterns.
    """
    mode_name = getattr(mode, "value", str(mode))
    print(f"🚀 Starting setup in {mode_name} mode...")

    result = await orchestrator.orchestrate_complete_setup(mode)

    if result.success:
        print("✅ Setup completed successfully")

        if hasattr(result, "warnings") and result.warnings:
            if verbose:
                print("⚠️ Warnings during setup:")
                for warning in result.warnings:
                    print(f"    • {warning}")
            else:
                print(
                    f"⚠️ {len(result.warnings)} warning(s) during setup (use --verbose for details)"
                )

        return 0
    else:
        print("❌ Setup failed")

        if hasattr(result, "errors") and result.errors:
            print("❌ Errors:")
            for error in result.errors:
                print(f"    • {error}")

        if hasattr(result, "warnings") and result.warnings and verbose:
            print("⚠️ Warnings:")
            for warning in result.warnings:
                print(f"    • {warning}")

        return 1


async def main() -> int:
    """
    Main setup function following modern standardization principles.

    Follows SOLID principles:
    - Single Responsibility: Coordinates setup operations
    - Open/Closed: Extensible through mode selection
    - Liskov Substitution: Uses standardized orchestrator interface
    - Interface Segregation: Clear separation of concerns
    - Dependency Inversion: Depends on orchestrator abstraction

    Implements MODERNIZATION through async/await patterns and proper error handling.
    Ensures IDEMPOTENCY through safe operation design.
    """
    parser = create_argument_parser()
    args = parser.parse_args()

    try:
        # Handle both enum and fallback SetupMode following STANDARDIZATION
        if hasattr(SetupMode, "__call__"):
            # Fallback class implementation
            mode = SetupMode(args.mode)
        else:
            # Real enum - find the matching member
            mode_value = args.mode
            mode = None
            for enum_mode in SetupMode:
                if enum_mode.value == mode_value:
                    mode = enum_mode
                    break
            if mode is None:
                # Fallback to development mode following defensive programming
                mode = SetupMode.DEVELOPMENT

        # Initialize orchestrator following DI principle
        orchestrator = ModernSetupOrchestrator(
            workspace_root=args.workspace or Path.cwd(),
            verbose=args.verbose,
        )

        # Execute based on operation mode following SRP
        if args.validate_only:
            return await handle_validation_only(orchestrator, args.verbose)
        else:
            return await handle_setup_mode(orchestrator, mode, args.verbose)

    except KeyboardInterrupt:
        print("\n⚠️ Setup interrupted by user")
        return 130
    except Exception as e:
        print(f"❌ Setup failed with error: {e}")
        if args.verbose:
            import traceback

            print("\n📋 Full error traceback:")
            traceback.print_exc()
        else:
            print("💡 Use --verbose flag for detailed error information")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
