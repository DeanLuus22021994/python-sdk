"""
Main orchestration runner for the MCP Python SDK setup system.
"""

from __future__ import annotations


def run_setup() -> bool:
    """Main entry point for setup orchestration."""
    try:
        from .orchestrator import ModernSetupOrchestrator

        print("🚀 Starting MCP Python SDK Setup...")
        orchestrator = ModernSetupOrchestrator()

        # Run setup orchestration
        result = orchestrator.orchestrate_setup()

        if result:
            print("✅ Setup completed successfully!")
            return True
        else:
            print("❌ Setup failed. Check logs for details.")
            return False

    except ImportError as e:
        print(f"❌ Failed to import orchestrator: {e}")
        print("Setup system may not be fully configured.")
        return False
    except Exception as e:
        print(f"❌ Setup failed with error: {e}")
        return False


if __name__ == "__main__":
    run_setup()
