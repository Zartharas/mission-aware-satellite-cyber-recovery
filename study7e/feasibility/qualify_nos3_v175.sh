#!/usr/bin/env bash
set -euo pipefail

NOS3_DIR="${1:-/tmp/s7e-aerc-external/nos3-v1.7.5}"
REPORT_DIR="${2:-/tmp/s7e-aerc-feasibility-reports}"
MODE="${3:---preflight}"
EXPECTED="5a3bdee6be9a2c67fdf994ae6db56d5c60395302"

mkdir -p "$REPORT_DIR"

command -v git >/dev/null 2>&1 || { echo "ERROR: git missing" >&2; exit 1; }
command -v make >/dev/null 2>&1 || { echo "ERROR: make missing" >&2; exit 1; }

test -d "$NOS3_DIR/.git"
test "$(git -C "$NOS3_DIR" rev-parse HEAD)" = "$EXPECTED"
test -z "$(git -C "$NOS3_DIR" status --short)"

META="$REPORT_DIR/nos3_v175_preflight.txt"
{
  echo "experiment_id=S7E-AERC-001"
  echo "qualification=nos3_build_feasibility"
  echo "scientific_execution=false"
  echo "head=$(git -C "$NOS3_DIR" rev-parse HEAD)"
  echo "os=$(uname -a)"
  echo "git=$(git --version)"
  echo "make=$(make --version | head -1)"
  if command -v docker >/dev/null 2>&1; then
    echo "docker=$(docker --version)"
  else
    echo "docker=ABSENT"
  fi
  if command -v vagrant >/dev/null 2>&1; then
    echo "vagrant=$(vagrant --version)"
  else
    echo "vagrant=ABSENT"
  fi
  if command -v VBoxManage >/dev/null 2>&1; then
    echo "virtualbox=$(VBoxManage --version)"
  else
    echo "virtualbox=ABSENT"
  fi
} > "$META"

if [ "$MODE" = "--preflight" ]; then
  echo "nos3_v175_preflight=PASS"
  echo "report=$META"
  echo "build_not_run=true"
  exit 0
fi

if [ "$MODE" != "--build" ]; then
  echo "ERROR: mode must be --preflight or --build" >&2
  exit 1
fi

if [ "$(uname -s)" != "Linux" ]; then
  echo "ERROR: --build must run inside the supported Linux/VM environment described by NOS3 documentation" >&2
  exit 2
fi

command -v docker >/dev/null 2>&1 || {
  echo "ERROR: docker is required for the Linux NOS3 build path" >&2
  exit 1
}

LOG="$REPORT_DIR/nos3_v175_build.log"
(
  cd "$NOS3_DIR"
  make prep
  make
) 2>&1 | tee "$LOG"

echo "nos3_v175_build_feasibility=PASS"
echo "report=$META"
echo "log=$LOG"
echo "make_launch_run=false"
echo "scientific_results_generated=false"
