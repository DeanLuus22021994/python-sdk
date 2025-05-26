"""
Setup Module 1.3: SDK Validator
Verifies MCP SDK structure and performance module
"""

import sys
from importlib import util
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from setup.environment import get_project_root
except ImportError:

    def get_project_root():
        return Path(__file__).parent.parent.parent


def validate_mcp_structure() -> tuple[bool, str]:
    """Validate MCP SDK structure exists."""
    project_root = get_project_root()
    mcp_path = project_root / "src" / "mcp"
    if not mcp_path.exists():
        return False, "✗ MCP source directory not found"

    shared_path = mcp_path / "shared"
    if not shared_path.exists():
        return False, "✗ MCP shared module directory not found"

    return True, "✓ MCP SDK structure validated"


def validate_performance_module() -> tuple[bool, str]:
    """Validate basic performance module import."""
    try:
        spec = util.find_spec("src.mcp.shared.performance")
        if spec is not None:
            return True, "✓ Performance module found and available"
        return False, "✗ Performance module not found"
    except ImportError as e:
        return False, f"✗ Performance module import failed: {str(e)}"
    except Exception as e:
        return False, f"✗ Performance module error: {str(e)}"


def validate_sdk() -> bool:
    """Main SDK validation flow."""
    print("🔧 Validating MCP SDK...")
    checks = [validate_mcp_structure(), validate_performance_module()]
    success = True
    for passed, message in checks:
        print(f"  {message}")
        if not passed:
            success = False
    return success
