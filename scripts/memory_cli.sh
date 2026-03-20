#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="$WORKSPACE_ROOT/.memory-system-v2.conf"
if [[ ! -f "$CONFIG_FILE" ]]; then
  cat > "$CONFIG_FILE" <<EOF
# Persistent memory-system-v2 workspace configuration
MEMORY_DIR="$WORKSPACE_ROOT/clawd/memory"
EOF
fi
export OPENCLAW_WORKSPACE_ROOT="$WORKSPACE_ROOT"
export OPENCLAW_MEMORY_CONFIG="$CONFIG_FILE"
exec /root/.openclaw/skills/memory-system-v2/memory-cli.sh "$@"
