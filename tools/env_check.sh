#!/usr/bin/env bash
set -euo pipefail

echo "pwd: $(pwd)"
echo "uname: $(uname -a)"
if command -v lsb_release >/dev/null 2>&1; then
  lsb_release -a || true
else
  cat /etc/os-release
fi

echo "ROS setup scripts:"
find /opt/ros -maxdepth 2 -name setup.bash 2>/dev/null | sort || true

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/source_ros.sh" >/dev/null

echo "ROS_DISTRO=${ROS_DISTRO:-unset}"
echo "python3=$(command -v python3)"
echo "VIRTUAL_ENV=${VIRTUAL_ENV:-}"
python3 --version
echo "ros2=$(command -v ros2)"
echo "colcon=$(command -v colcon)"
echo "xacro=$(command -v xacro)"
echo "gz=$(command -v gz || true)"
echo "ign=$(command -v ign || true)"
echo "check_urdf=$(command -v check_urdf || true)"
