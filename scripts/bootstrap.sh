#!/usr/bin/env bash
set -euo pipefail

PROFILE="full"
LAUNCH_CONTROL_CENTER="1"
RELAYTIC_ARGS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --profile)
      PROFILE="${2:-full}"
      shift 2
      ;;
    --no-launch-control-center)
      LAUNCH_CONTROL_CENTER="0"
      shift
      ;;
    *)
      RELAYTIC_ARGS+=("$1")
      shift
      ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
VENV_DIR="${REPO_ROOT}/.venv"
VENV_PYTHON="${VENV_DIR}/bin/python"

if [[ ! -x "${VENV_PYTHON}" ]]; then
  python3 -m venv "${VENV_DIR}"
fi

cd "${REPO_ROOT}"
"${VENV_PYTHON}" -m pip install --upgrade pip

COMMAND=("scripts/install_relaytic.py" "--profile" "${PROFILE}")
if [[ "${LAUNCH_CONTROL_CENTER}" == "1" ]]; then
  COMMAND+=("--launch-control-center")
fi
COMMAND+=("${RELAYTIC_ARGS[@]}")

"${VENV_PYTHON}" "${COMMAND[@]}"
