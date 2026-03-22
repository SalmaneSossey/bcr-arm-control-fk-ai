#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HEADLESS="${BCR_HEADLESS:-false}"

source "$REPO_ROOT/tools/source_ros.sh" >/dev/null

# WSLg and Ogre can be unstable together; software GL is a safer default.
export LIBGL_ALWAYS_SOFTWARE="${LIBGL_ALWAYS_SOFTWARE:-1}"

ros2 launch bcr_arm_gazebo bcr_arm.gazebo.launch.py headless:="$HEADLESS"
