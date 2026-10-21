#!/usr/bin/env bash
set -euo pipefail

CFS_DIR="${1:-/tmp/s7e-aerc-external/cfs-v7.0.1}"
REPORT_DIR="${2:-/tmp/s7e-aerc-feasibility-reports}"
EXPECTED="088b2fa828db9ff7e00733f1908e0eeb59f66ce3"

mkdir -p "$REPORT_DIR"

for cmd in git make cmake gcc; do
  command -v "$cmd" >/dev/null 2>&1 || {
    echo "ERROR: required command missing: $cmd" >&2
    exit 1
  }
done

test -d "$CFS_DIR/.git"
test "$(git -C "$CFS_DIR" rev-parse HEAD)" = "$EXPECTED"
test -z "$(git -C "$CFS_DIR" status --short)"

case "$(uname -s)" in
  Linux) ;;
  *)
    echo "ERROR: cFS native_std qualification must run in Linux. Current OS: $(uname -s)" >&2
    exit 2
    ;;
esac

LOG="$REPORT_DIR/cfs_v701_build.log"
META="$REPORT_DIR/cfs_v701_metadata.txt"

{
  echo "experiment_id=S7E-AERC-001"
  echo "qualification=cfs_build_only"
  echo "scientific_execution=false"
  echo "head=$(git -C "$CFS_DIR" rev-parse HEAD)"
  echo "os=$(uname -a)"
  echo "git=$(git --version)"
  echo "cmake=$(cmake --version | head -1)"
  echo "gcc=$(gcc --version | head -1)"
  echo "make=$(make --version | head -1)"
} > "$META"

(
  cd "$CFS_DIR"
  make native_std.prep
  make native_std.install
  make native_std.runtest
) 2>&1 | tee "$LOG"

test -z "$(git -C "$CFS_DIR" status --short)"

echo "cfs_v701_feasibility=PASS"
echo "metadata=$META"
echo "log=$LOG"
echo "scientific_results_generated=false"
