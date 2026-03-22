#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WS_ROOT="$REPO_ROOT/bcr_ws"

source "$REPO_ROOT/tools/source_ros.sh" >/dev/null
cd "$WS_ROOT"
colcon build --symlink-install
