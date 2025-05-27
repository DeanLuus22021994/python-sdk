"""SDK validation module for Python SDK setup."""

from importlib import util
from pathlib import Path

try:
    from ..environment.path_utils import get_project_root
except ImportError:

    def get_project_root() -> Path:
        """Get project root directory."""
        current = Path(__file__).resolve()
        while current.parent != current:
            if (current / "pyproject.toml").exists() or (current / "setup.py").exists():
                return current
            current = current.parent
        return Path.cwd()


def validate_mcp_structure() -> tuple[bool, str]:
    """Validate MCP SDK structure exists."""
    project_root = get_project_root()
    mcp_path = project_root / "src" / "mcp"
    if not mcp_path.exists():
        return False, "✗ MCP package structure not found"

    shared_path = mcp_path / "shared"
    if not shared_path.exists():
        return False, "✗ MCP shared module not found"

    return True, "✓ MCP package structure validated"


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


def validate_core_modules() -> tuple[bool, str]:
    """Validate core MCP modules exist."""
    try:
        project_root = get_project_root()
        core_modules = ["client", "server", "types"]
        mcp_path = project_root / "src" / "mcp"

        missing_modules = []
        for module in core_modules:
            module_path = mcp_path / f"{module}.py"
            if not module_path.exists():
                missing_modules.append(module)

        if missing_modules:
            return (False, f"✗ Missing core modules: {', '.join(missing_modules)}")

        return True, "✓ Core MCP modules validated"
    except Exception as e:
        return False, f"✗ Core module validation failed: {str(e)}"


def validate_sdk() -> bool:
    """Main SDK validation flow."""
    print("🔧 Validating MCP SDK...")
    checks = [
        validate_mcp_structure(),
        validate_performance_module(),
        validate_core_modules(),
    ]
    success = True
    for passed, message in checks:
        print(f"  {message}")
        if not passed:
            success = False
    return success


def check_sdk_completeness() -> dict[str, bool]:
    """Check SDK component completeness."""
    results = {}
    checks = [
        ("mcp_structure", validate_mcp_structure),
        ("performance_module", validate_performance_module),
        ("core_modules", validate_core_modules),
    ]

    for check_name, check_func in checks:
        passed, _ = check_func()
        results[check_name] = passed

    return results
