#!/usr/bin/env bash
set -eo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WS_ROOT="$REPO_ROOT/bcr_ws"
VENV_PATH="$REPO_ROOT/.venv"

export PYENV_VERSION=system
export BCR_TP3_ROOT="$REPO_ROOT"
export ROS_HOME="$REPO_ROOT/.ros"
export ROS_LOG_DIR="$ROS_HOME/log"
export PIP_CACHE_DIR="$REPO_ROOT/.cache/pip"
export MPLCONFIGDIR="$REPO_ROOT/.cache/matplotlib"
export VIRTUAL_ENV_DISABLE_PROMPT=1
mkdir -p "$ROS_LOG_DIR"
mkdir -p "$PIP_CACHE_DIR" "$MPLCONFIGDIR"

had_nounset=0
if [[ $- == *u* ]]; then
  had_nounset=1
  set +u
fi

if [ -f "$VENV_PATH/bin/activate" ]; then
  source "$VENV_PATH/bin/activate"
fi

source /opt/ros/humble/setup.bash

if [ -f "$WS_ROOT/install/setup.bash" ]; then
  source "$WS_ROOT/install/setup.bash"
fi

if [ "$had_nounset" -eq 1 ]; then
  set -u
fi

echo "ROS_DISTRO=${ROS_DISTRO:-unset}"
echo "python3=$(command -v python3)"
if [ -n "${VIRTUAL_ENV:-}" ]; then
  echo "VIRTUAL_ENV=$VIRTUAL_ENV"
fi
