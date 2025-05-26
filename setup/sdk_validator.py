"""
Setup Module 03: SDK Validator
Validates MCP SDK structure and functionality
"""
from pathlib import Path


def validate_mcp_structure() -> tuple[bool, str]:
    """Validate MCP SDK structure exists."""
    project_root = Path(__file__).parent.parent
    mcp_path = project_root / "src" / "mcp"
    
    if not mcp_path.exists():
        return False, "✗ MCP source directory not found"
    
    shared_path = mcp_path / "shared"
    if not shared_path.exists():
        return False, "✗ MCP shared module directory not found"
    
    return True, "✓ MCP SDK structure validated"


def validate_performance_module() -> tuple[bool, str]:
    """Validate performance module can be imported."""
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent))
        
        # Test basic import
        import src.mcp.shared.performance
        return True, "✓ Performance module imports successfully"
    except ImportError as e:
        return False, f"✗ Performance module import failed: {str(e)}"
    except Exception as e:
        return False, f"✗ Performance module error: {str(e)}"


def validate_sdk() -> bool:
    """Main SDK validation."""
    print("🔧 Validating MCP SDK...")
    
    checks = [
        validate_mcp_structure(),
        validate_performance_module()
    ]
    
    success = True
    for check_passed, message in checks:
        print(f"  {message}")
        if not check_passed:
            success = False
    
    return success
