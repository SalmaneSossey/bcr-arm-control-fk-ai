#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PKG_ROOT="$REPO_ROOT/bcr_ws/src/bcr_arm_gazebo"

source "$REPO_ROOT/tools/source_ros.sh" >/dev/null

python3 "$PKG_ROOT/scripts/generate_fk_dataset.py" --samples 10000
python3 "$PKG_ROOT/scripts/train_fk_mlp.py"
python3 "$PKG_ROOT/scripts/evaluate_fk_mlp.py"
