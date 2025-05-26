# DevContainer Tools Directory

This directory contains modular development utilities following a structured naming convention and organization system.

## Directory Structure

```structure
tools/
├── index.sh                    # Central tool registry and launcher
├── inspect/                    # State inspection and analysis tools
│   └── 001-devcontainer-state.sh
├── utils/                      # General development utilities
│   └── 002-build-status.sh
└── metrics/                    # Performance and development metrics
    └── 003-dev-metrics.sh
```

## Naming Convention

Tools follow a structured naming pattern: `{ID}-{name}.sh`

- **ID**: 3-digit sequential number (001, 002, 003, ...)
- **Name**: Descriptive kebab-case name
- **Category**: Directory-based organization (inspect, utils, metrics)

## Tool Categories

### inspect/

Tools for examining and analyzing the current state of the development environment.

### utils/

General-purpose utilities for development workflow assistance.

### metrics/

Performance tracking, benchmarking, and development cycle analytics.

## Usage

### Using the Index (Recommended)

```bash
# Show all available tools
./tools/index.sh list

# Run a specific tool by ID
./tools/index.sh 001 json
./tools/index.sh 002 docker
./tools/index.sh 003 record
```

### Direct Execution

```bash
# Make scripts executable
chmod +x tools/*/*.sh

# Run directly
./tools/inspect/001-devcontainer-state.sh summary
./tools/utils/002-build-status.sh performance
./tools/metrics/003-dev-metrics.sh benchmark
```

## Available Tools

| ID  | Category | Name               | Description                                           |
|-----|----------|--------------------|-------------------------------------------------------|
| 001 | inspect  | DevContainer State | Return current state of files in devcontainer        |
| 002 | utils    | Build Status       | Check current build status and active processes      |
| 003 | metrics  | Dev Metrics        | Track development cycle metrics and benchmarks       |
| 004 | utils    | System Migration   | Migrate from old build system to new modular arch    |

## Adding New Tools

1. Choose appropriate category directory (or create new one)
2. Use next sequential ID number
3. Follow naming convention: `{ID}-{descriptive-name}.sh`
4. Add entry to `TOOL_REGISTRY` array in `index.sh`
5. Ensure script is executable and follows the established pattern
6. Update this README with the new tool information

## Design Principles

- **Single Responsibility**: Each tool has one focused purpose
- **≤20 Lines**: Keep tools concise and focused
- **Machine Readable**: Support structured output formats (JSON, table)
- **Composable**: Tools can be chained or used in automation
- **Self-Documenting**: Clear usage and help information
- **Future-Proof**: Extensible naming and organization system

## Integration

These tools are designed to integrate with:

- Master orchestrator workflows
- CI/CD pipelines
- Development environment monitoring
- Performance optimization tracking
- Debugging and troubleshooting workflows
