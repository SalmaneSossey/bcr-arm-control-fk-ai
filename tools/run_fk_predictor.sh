#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

source "$REPO_ROOT/tools/source_ros.sh" >/dev/null
ros2 run bcr_arm_gazebo predict_fk_mlp.py
