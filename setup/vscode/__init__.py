"""
VS Code configuration module for MCP Python SDK setup.

This module provides comprehensive VS Code configuration management following
SRP (Single Responsibility Principle) and DRY (Don't Repeat Yourself) principles.
Each configuration file is handled by a dedicated module for maintainability.
"""

from .extensions import VSCodeExtensionsManager
from .integration import VSCodeIntegrationManager
from .launch import VSCodeLaunchManager
from .settings import VSCodeSettingsManager
from .tasks import VSCodeTasksManager

__all__ = [
    "VSCodeExtensionsManager",
    "VSCodeIntegrationManager",
    "VSCodeLaunchManager",
    "VSCodeSettingsManager",
    "VSCodeTasksManager",
]
