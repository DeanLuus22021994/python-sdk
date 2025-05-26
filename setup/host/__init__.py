"""
MCP Python SDK Setup System (Host Package)
Sequence set 1.x modules for environment setup
"""

from ._1_1_env_validator import validate_environment
from ._1_2_package_manager import setup_packages
from ._1_3_sdk_validator import validate_sdk
from ._1_4_vscode_config import setup_vscode_config

__version__ = "1.0.0"
__all__ = [
    "validate_environment",
    "setup_packages",
    "validate_sdk",
    "setup_vscode_config",
]
