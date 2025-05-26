"""
MCP Python SDK Setup System Host Package
Implements environment configuration and validation modules
"""

from .env_validator import validate_environment
from .package_manager import setup_packages
from .sdk_validator import validate_sdk
from .vscode_config import setup_vscode_config

__version__ = "1.0.0"
__all__ = [
    "validate_environment",
    "setup_packages",
    "validate_sdk",
    "setup_vscode_config",
]
