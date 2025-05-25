#!/bin/bash
# Tool 004: System Migration Helper
# Purpose: Migrate from old build system to new modular architecture
# Usage: ./004-migrate-system.sh [check|migrate|rollback]

migrate_system() {
    local action="${1:-check}"
    local backup_dir="/workspaces/python-sdk/.devcontainer/.migration-backup"
    
    case "$action" in
        "check")
            echo "=== Migration Status Check ==="
            echo "Old Scripts Present:"
            [[ -f "/workspaces/python-sdk/.devcontainer/master-build.sh" ]] && echo "  ✓ master-build.sh" || echo "  ✗ master-build.sh"
            [[ -f "/workspaces/python-sdk/.devcontainer/setup-performance.sh" ]] && echo "  ✓ setup-performance.sh" || echo "  ✗ setup-performance.sh"
            
            echo "New Modular System:"
            [[ -d "/workspaces/python-sdk/.devcontainer/scripts" ]] && echo "  ✓ scripts/ directory" || echo "  ✗ scripts/ directory"
            [[ -f "/workspaces/python-sdk/.devcontainer/master-orchestrator.sh" ]] && echo "  ✓ master-orchestrator.sh" || echo "  ✗ master-orchestrator.sh"
            [[ -f "/workspaces/python-sdk/.devcontainer/.env" ]] && echo "  ✓ .env file" || echo "  ✗ .env file"
            ;;
        "migrate")
            echo "=== Starting System Migration ==="
            mkdir -p "$backup_dir"
            
            # Backup old files
            for file in master-build.sh setup-performance.sh; do
                if [[ -f "/workspaces/python-sdk/.devcontainer/$file" ]]; then
                    cp "/workspaces/python-sdk/.devcontainer/$file" "$backup_dir/"
                    echo "Backed up: $file"
                fi
            done
            
            echo "Migration completed. Old files backed up to $backup_dir"
            ;;
        *)
            echo "Usage: migrate_system [check|migrate|rollback]"
            ;;
    esac
}

migrate_system "$@"
