#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-/tmp/s7e-aerc-external}"
REPORT_DIR="${2:-/tmp/s7e-aerc-feasibility-reports}"
CFS_DIR="$ROOT/cfs-v7.0.1"
NOS3_DIR="$ROOT/nos3-v1.7.5"

mkdir -p "$ROOT" "$REPORT_DIR"

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "ERROR: required command missing: $1" >&2
    exit 1
  }
}
require_cmd git
require_cmd python3

clone_or_verify() {
  local url="$1"
  local tag="$2"
  local expected="$3"
  local dir="$4"

  if [ ! -d "$dir/.git" ]; then
    git clone --branch "$tag" --depth 1 --recurse-submodules --shallow-submodules "$url" "$dir"
  fi

  git -C "$dir" fetch --tags --force
  git -C "$dir" checkout --detach "$tag"
  git -C "$dir" submodule update --init --recursive

  local head
  head="$(git -C "$dir" rev-parse HEAD)"
  test "$head" = "$expected" || {
    echo "ERROR: $dir HEAD=$head expected=$expected" >&2
    exit 1
  }
}

clone_or_verify \
  https://github.com/nasa/cFS.git \
  v7.0.1 \
  088b2fa828db9ff7e00733f1908e0eeb59f66ce3 \
  "$CFS_DIR"

clone_or_verify \
  https://github.com/nasa/nos3.git \
  v1_07_05 \
  5a3bdee6be9a2c67fdf994ae6db56d5c60395302 \
  "$NOS3_DIR"

{
  echo "experiment_id=S7E-AERC-001"
  echo "qualification=external_revision_resolution"
  echo "scientific_execution=false"
  echo "cfs_head=$(git -C "$CFS_DIR" rev-parse HEAD)"
  echo "nos3_head=$(git -C "$NOS3_DIR" rev-parse HEAD)"
  echo
  echo "===== CFS RECURSIVE SUBMODULES ====="
  git -C "$CFS_DIR" submodule status --recursive
  echo
  echo "===== NOS3 RECURSIVE SUBMODULES ====="
  git -C "$NOS3_DIR" submodule status --recursive
} > "$REPORT_DIR/external_revision_resolution.txt"

echo "external_revision_resolution=PASS"
echo "report=$REPORT_DIR/external_revision_resolution.txt"
echo "scientific_results_generated=false"
