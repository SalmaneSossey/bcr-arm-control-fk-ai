#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if [ ! -d .venv ]; then
  /usr/bin/python3.10 -m venv --system-site-packages .venv
fi

source .venv/bin/activate
export PIP_CACHE_DIR="$REPO_ROOT/.cache/pip"
export MPLCONFIGDIR="$REPO_ROOT/.cache/matplotlib"
mkdir -p "$PIP_CACHE_DIR" "$MPLCONFIGDIR"

pip install matplotlib
pip install --index-url https://download.pytorch.org/whl/cpu torch

echo "Venv ready: $REPO_ROOT/.venv"
python --version
python -c "import sys; print(sys.executable)"
