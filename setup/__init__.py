"""
MCP Python SDK Setup Package

Modern, modular setup system for the MCP Python SDK with support for:
- Host-based development environment
- Docker containerization
- Performance optimization
- Clean architecture following SOLID principles
"""

from typing import Final

__version__: Final[str] = "2.0.0"
__author__: Final[str] = "MCP Python SDK Team"

# Core setup modules
from setup.environment import EnvironmentManager
from setup.sequence import SetupOrchestrator

# Host setup capabilities
try:
    from setup.host import HostSetupManager
except ImportError:
    HostSetupManager = None

# Docker setup capabilities
try:
    from setup.docker import DockerSetupManager
except ImportError:
    DockerSetupManager = None

__all__ = [
    "__version__",
    "__author__",
    "EnvironmentManager",
    "SetupOrchestrator",
    "HostSetupManager",
    "DockerSetupManager",
]
