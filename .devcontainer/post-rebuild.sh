#!/bin/bash
# Post-rebuild initialization script
# Ensures all performance optimizations are applied after devcontainer rebuild

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Post-Rebuild Initialization ==="

# Load environment configurations
source "$SCRIPT_DIR/config/load-env.sh"
load_env_files

# Apply performance optimizations through the unified orchestrator
echo "Applying performance optimizations..."
if [[ $EUID -eq 0 ]]; then
    # Use the master orchestrator instead of individual scripts
    "$SCRIPT_DIR/master-orchestrator.modular.sh" --parallel cpu memory io binary
else
    echo "Note: Performance optimizations require root privileges"
fi

# Verify Python environment
echo "Verifying Python environment..."
python3 -c "
import sys
print(f'Python {sys.version}')

# Test performance packages
packages = ['uvloop', 'orjson', 'numba', 'psutil']
for pkg in packages:
    try:
        __import__(pkg)
        print(f'✓ {pkg} available')
    except ImportError:
        print(f'❌ {pkg} not available')

# Test jemalloc
import os
ld_preload = os.environ.get('LD_PRELOAD', '')
if 'jemalloc' in ld_preload:
    print('✓ jemalloc configured')
else:
    print('❌ jemalloc not configured')
"

# Initialize tools
echo "Loading development tools..."
source "$SCRIPT_DIR/tools/dt.sh"

# Run validation
echo "Running performance validation..."
"$SCRIPT_DIR/scripts/validation/performance-validator.sh" || echo "Some validations failed (expected during rebuild)"

echo "Post-rebuild initialization completed!"
echo "Use 'dt list' to see available development tools"
