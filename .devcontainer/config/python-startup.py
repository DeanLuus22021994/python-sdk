#!/usr/bin/env python3
"""
Python startup script for performance optimizations
This script is loaded by PYTHONSTARTUP environment variable
"""

import builtins
import sys
import os
import gc

# Optimize garbage collection for performance
gc.set_threshold(700, 10, 10)
gc.disable()  # Disable automatic GC for better performance

# Import commonly used modules for faster subsequent imports
try:
    import asyncio
    import json
    import logging
    import multiprocessing
    import threading
    import time
    import uuid
except ImportError:
    pass

# Set optimal recursion limit for performance
sys.setrecursionlimit(2000)

# Configure optimal hash randomization
if 'PYTHONHASHSEED' not in os.environ:
    os.environ['PYTHONHASHSEED'] = '0'

# Optimize import path for MCP SDK
mcp_path = '/workspaces/python-sdk/src'
if mcp_path not in sys.path:
    sys.path.insert(0, mcp_path)

# Performance monitoring utilities


class PerfTimer:
    """Context manager for timing code execution"""

    def __init__(self, name="Operation"):
        self.name = name

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, *args):
        elapsed = time.perf_counter() - self.start
        print(f"{self.name} took {elapsed:.4f} seconds")


# Make performance utilities available globally
builtins.perf_timer = PerfTimer

# Configure uvloop if available (will be installed during rebuild)
try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    # Only print in interactive mode to avoid noise
    if hasattr(sys, 'ps1'):
        print("✓ uvloop event loop policy activated")
except ImportError:
    # uvloop not available, using default event loop policy
    # This is expected during initial setup before rebuild
    if hasattr(sys, 'ps1'):
        print("ℹ uvloop not available - using default event loop (will be fixed after rebuild)")
    pass
