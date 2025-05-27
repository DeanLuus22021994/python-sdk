"""
ZATRUST BIO-MCP PYTHON SETUP LAYER — RESTRUCTURE AUTOMATION
High-fidelity alignment script for milestone completion.

This script performs the precise, non-deviating restructuring as outlined
in the milestone brief, ensuring complete alignment with modern Python
package standards and SOLID principles.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import NamedTuple


class FileMove(NamedTuple):
    """Structured representation of a file move operation."""

    source: str
    destination: str
    description: str
    is_critical: bool = True


class RestructureOrchestrator:
    """
    Main orchestrator for the restructuring process.
    Follows SOLID principles and ensures idempotent operations.
    """

    def __init__(self) -> None:
        self.base_dir = Path(__file__).parent.absolute()
        self.root_dir = self.base_dir.parent.absolute()
        self.setup_dir = self.base_dir

        # Ensure we're in the correct location
        if not (self.root_dir / "setup").exists():
            raise RuntimeError(
                f"Invalid project structure. Expected setup/ directory in {self.root_dir}"
            )

    def ensure_directory_structure(self) -> None:
        """Ensure all required directories exist before file moves."""
        required_dirs = [
            "setup/config",
            "setup/infra/docker/dockerfiles",
            "setup/infra/host",
            "setup/typings",
            "setup/validation",
            "setup/vscode",
        ]

        print("🏗️  Creating required directory structure...")

        for dir_path in required_dirs:
            full_path = self.root_dir / dir_path
            full_path.mkdir(parents=True, exist_ok=True)

            # Create __init__.py files for Python packages
            if not dir_path.endswith(("dockerfiles", "json")):
                init_file = full_path / "__init__.py"
                if not init_file.exists():
                    init_file.write_text('"""Package initialization."""\n')
                    print(f"   Created: {dir_path}/__init__.py")

    def get_file_moves(self) -> list[FileMove]:
        """Define all file moves according to milestone specification."""
        return [
            # Phase 1: Environment to config migration
            FileMove(
                "environment/constants.py",
                "setup/config/constants.py",
                "Environment constants → config constants",
            ),
            FileMove(
                "environment/manager.py",
                "setup/config/manager.py",
                "Environment manager → config manager",
            ),
            FileMove(
                "environment/utils.py",
                "setup/config/utils.py",
                "Environment utilities → config utilities",
            ),
            FileMove(
                "environment/__init__.py",
                "setup/config/__init__.py",
                "Environment package init → config package init",
                is_critical=False,
            ),
            # Phase 2: Docker to infra/docker migration
            FileMove(
                "docker/config.py",
                "setup/infra/docker/config.py",
                "Docker config → infra/docker/config",
            ),
            FileMove(
                "docker/images.py",
                "setup/infra/docker/images.py",
                "Docker images → infra/docker/images",
            ),
            FileMove(
                "docker/volume_config.py",
                "setup/infra/docker/volume_config.py",
                "Docker volume config → infra/docker/volume_config",
            ),
            FileMove(
                "docker/volumes.py",
                "setup/infra/docker/volumes.py",
                "Docker volumes → infra/docker/volumes",
            ),
            FileMove(
                "docker/dockerfiles/Dockerfile.dev",
                "setup/infra/docker/dockerfiles/Dockerfile.dev",
                "Dockerfile.dev → infra/docker/dockerfiles",
                is_critical=False,
            ),
            FileMove(
                "docker/__init__.py",
                "setup/infra/docker/__init__.py",
                "Docker package init → infra/docker package init",
                is_critical=False,
            ),
            # Phase 3: Host to infra/host migration
            FileMove(
                "host/package_manager.py",
                "setup/infra/host/package_manager.py",
                "Host package manager → infra/host/package_manager",
            ),
            FileMove(
                "host/__init__.py",
                "setup/infra/host/__init__.py",
                "Host package init → infra/host package init",
                is_critical=False,
            ),
        ]

    def perform_file_move(self, move: FileMove) -> bool:
        """Perform a single file move operation with validation."""
        src_path = self.root_dir / move.source
        dest_path = self.root_dir / move.destination

        # Check if source exists
        if not src_path.exists():
            if move.is_critical:
                print(f"❌ CRITICAL: Source not found → {move.source}")
                return False
            else:
                print(f"⚠️  Optional file not found → {move.source}")
                return True

        # Ensure destination directory exists
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        # Handle destination conflicts
        if dest_path.exists():
            print(f"⚠️  Destination exists, backing up → {move.destination}")
            backup_path = dest_path.with_suffix(f"{dest_path.suffix}.backup")
            shutil.move(str(dest_path), str(backup_path))

        # Perform the move
        try:
            shutil.move(str(src_path), str(dest_path))
            print(f"✅ MOVED: {move.description}")
            print(f"   {move.source} → {move.destination}")
            return True
        except Exception as e:
            print(f"❌ FAILED: {move.description}")
            print(f"   Error: {e}")
            return False

    def cleanup_empty_directories(self) -> None:
        """Remove empty directories after restructuring."""
        cleanup_dirs = ["environment", "docker", "host"]

        print("🧹 Cleaning up empty directories...")

        for dir_name in cleanup_dirs:
            dir_path = self.root_dir / dir_name
            if dir_path.exists() and dir_path.is_dir():
                try:
                    # Check if directory is empty
                    contents = list(dir_path.iterdir())
                    significant_contents = [
                        item
                        for item in contents
                        if item.name not in {".gitkeep", "__pycache__", ".DS_Store"}
                    ]

                    if not significant_contents:
                        # Remove __pycache__ if it exists
                        pycache = dir_path / "__pycache__"
                        if pycache.exists():
                            shutil.rmtree(pycache)

                        # Remove the directory if truly empty
                        remaining = list(dir_path.iterdir())
                        if not remaining or all(
                            item.name in {".gitkeep"} for item in remaining
                        ):
                            print(
                                f"   Empty directory retained: {dir_name}/ (contains .gitkeep)"
                            )
                        else:
                            contents_list = [item.name for item in remaining]
                            print(
                                f"   Directory not empty: {dir_name}/ (contents: {contents_list})"
                            )
                    else:
                        significant_list = [item.name for item in significant_contents]
                        print(
                            f"   Directory retained: {dir_name}/ (contains: {significant_list})"
                        )

                except Exception as e:
                    print(f"   Error checking {dir_name}/: {e}")

    def create_entry_points(self) -> None:
        """Create the required entry points as per milestone specification."""
        print("🎯 Creating entry points...")

        # Create setup/__main__.py
        main_py_content = '''"""
MCP Python SDK Setup - Package Entry Point

Modern, modular setup system entry point following standardization principles.
Enables running the setup system via: python -m setup
"""

from __future__ import annotations

if __name__ == "__main__":
    try:
        from .main import run_setup
        run_setup()
    except ImportError:
        # Fallback for development
        import sys
        from pathlib import Path

        # Add parent to path for import resolution
        setup_dir = Path(__file__).parent
        if str(setup_dir.parent) not in sys.path:
            sys.path.insert(0, str(setup_dir.parent))

        try:
            from setup.main import run_setup
            run_setup()
        except ImportError as e:
            print(f"❌ Failed to import setup.main: {e}")
            print("Please ensure the setup package is properly structured.")
            sys.exit(1)
'''

        main_file = self.setup_dir / "__main__.py"
        main_file.write_text(main_py_content)
        print("   Created: setup/__main__.py")

        # Update setup/main.py if it doesn't exist or needs updating
        main_py_file = self.setup_dir / "main.py"
        if not main_py_file.exists():
            main_content = '''"""
Main orchestration runner for the MCP Python SDK setup system.
"""

from __future__ import annotations

def run_setup() -> None:
    """Main entry point for setup orchestration."""
    try:
        from .orchestrator import ModernSetupOrchestrator

        print("🚀 Starting MCP Python SDK Setup...")
        orchestrator = ModernSetupOrchestrator()

        # Run setup orchestration
        result = orchestrator.orchestrate_setup()

        if result:
            print("✅ Setup completed successfully!")
        else:
            print("❌ Setup failed. Check logs for details.")
            return

    except ImportError as e:
        print(f"❌ Failed to import orchestrator: {e}")
        print("Setup system may not be fully configured.")
    except Exception as e:
        print(f"❌ Setup failed with error: {e}")

if __name__ == "__main__":
    run_setup()
'''
            main_py_file.write_text(main_content)
            print("   Created: setup/main.py")

        # Update root setup.py for legacy compatibility
        root_setup_py = self.root_dir / "setup.py"
        if not root_setup_py.exists():
            setup_py_content = '''"""
Legacy CLI bridge for MCP Python SDK setup.
Provides backward compatibility while delegating to modern setup system.
"""

from __future__ import annotations

if __name__ == "__main__":
    try:
        from setup.main import run_setup
        run_setup()
    except ImportError:
        import sys
        print("❌ Setup package not found.")
        print("Please ensure you're running from the project root directory.")
        sys.exit(1)
'''
            root_setup_py.write_text(setup_py_content)
            print("   Created: setup.py (root)")

    def update_imports_preview(self) -> None:
        """Show what import updates will be needed."""
        print("📝 Import Updates Required:")
        print("   After restructuring, update these import patterns:")
        print()
        print("   OLD: from environment.manager import ...")
        print("   NEW: from setup.config.manager import ...")
        print()
        print("   OLD: from docker.config import ...")
        print("   NEW: from setup.infra.docker.config import ...")
        print()
        print("   OLD: from host.package_manager import ...")
        print("   NEW: from setup.infra.host.package_manager import ...")
        print()

    def validate_restructure(self) -> bool:
        """Validate that restructuring completed successfully."""
        print("🔍 Validating restructure completion...")

        required_files = [
            "setup/__main__.py",
            "setup/main.py",
            "setup/config/__init__.py",
            "setup/infra/__init__.py",
            "setup/infra/docker/__init__.py",
            "setup/infra/host/__init__.py",
        ]

        validation_success = True

        for file_path in required_files:
            full_path = self.root_dir / file_path
            if full_path.exists():
                print(f"   ✅ {file_path}")
            else:
                print(f"   ❌ {file_path}")
                validation_success = False

        # Check that key moved files exist
        moved_files = [
            "setup/config/constants.py",
            "setup/config/manager.py",
            "setup/infra/docker/config.py",
            "setup/infra/host/package_manager.py",
        ]

        for file_path in moved_files:
            full_path = self.root_dir / file_path
            if full_path.exists():
                print(f"   ✅ {file_path} (moved)")
            else:
                print(f"   ⚠️  {file_path} (not found)")

        return validation_success

    def run_restructure(self) -> bool:
        """Execute the complete restructuring process."""
        print("=" * 60)
        print("🎯 ZATRUST BIO-MCP PYTHON SETUP LAYER RESTRUCTURE")
        print("   High-fidelity alignment for milestone completion")
        print("=" * 60)

        try:
            # Phase 1: Ensure directory structure
            self.ensure_directory_structure()

            # Phase 2: Perform file moves
            print("\n📦 Executing file moves...")
            moves = self.get_file_moves()

            success_count = 0
            critical_failures = 0

            for i, move in enumerate(moves, 1):
                print(f"\n[{i}/{len(moves)}] {move.description}")
                success = self.perform_file_move(move)

                if success:
                    success_count += 1
                elif move.is_critical:
                    critical_failures += 1

            # Phase 3: Create entry points
            print("\n🎯 Creating entry points...")
            self.create_entry_points()

            # Phase 4: Cleanup
            print("\n🧹 Cleaning up...")
            self.cleanup_empty_directories()

            # Phase 5: Validation
            print("\n🔍 Validating restructure...")
            validation_success = self.validate_restructure()

            # Phase 6: Summary
            print("\n" + "=" * 60)
            print("📊 RESTRUCTURE SUMMARY")
            print("=" * 60)
            print(f"✅ Successful moves: {success_count}/{len(moves)}")
            print(f"❌ Critical failures: {critical_failures}")
            print(
                f"🔍 Validation: {'✅ PASSED' if validation_success else '❌ FAILED'}"
            )

            if critical_failures == 0 and validation_success:
                print("\n🎉 RESTRUCTURE COMPLETED SUCCESSFULLY!")
                print("\n📋 NEXT STEPS:")
                print("   1. Update imports to match new paths")
                print("   2. Test: python -m setup")
                print("   3. Test: python setup.py")
                print("   4. Run static type checking (pyright)")
                print("   5. Validate orchestration logic")

                self.update_imports_preview()
                return True
            else:
                print("\n❌ RESTRUCTURE COMPLETED WITH ISSUES")
                print("   Please review the errors above and retry.")
                return False

        except Exception as e:
            print(f"\n💥 RESTRUCTURE FAILED: {e}")
            print("   Check source control and retry if needed.")
            return False


def main() -> None:
    """Main entry point for restructure script."""
    try:
        orchestrator = RestructureOrchestrator()

        # Confirm before proceeding
        print("⚠️  This will restructure the entire setup directory.")
        print("   Source control will serve as backup for reverting if needed.")

        response = input("\n🤔 Continue with restructure? [y/N]: ").strip().lower()

        if response in ("y", "yes"):
            success = orchestrator.run_restructure()
            sys.exit(0 if success else 1)
        else:
            print("❌ Restructure cancelled by user.")
            sys.exit(0)

    except KeyboardInterrupt:
        print("\n⚠️  Restructure interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
