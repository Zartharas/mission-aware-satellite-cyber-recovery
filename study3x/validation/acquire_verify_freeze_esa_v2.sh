#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
BASE="${1:-$REPO_ROOT/study3x/local_source/esa_v2}"
DOWNLOADS="$BASE/downloads"
EXTRACTED="$BASE/extracted"
OUT="$REPO_ROOT/study3x/local_freeze_work"

M1_NAME="ESA-Mission1.zip"
M2_NAME="ESA-Mission2.zip"
M1_URL="https://zenodo.org/records/15237121/files/ESA-Mission1.zip?download=1"
M2_URL="https://zenodo.org/records/15237121/files/ESA-Mission2.zip?download=1"
M1_SIZE="3776246073"
M2_SIZE="4098539932"
M1_MD5="9770ad12ed730238f37c42d5c27ab436"
M2_MD5="bfc72012691427d9327eb41f726ce45e"

mkdir -p "$DOWNLOADS" "$EXTRACTED" "$OUT"

for cmd in curl unzip python3; do
  command -v "$cmd" >/dev/null 2>&1 || {
    echo "ERROR: required command not found: $cmd" >&2
    exit 1
  }
done

python3 - <<'PY'
try:
    import pandas  # noqa: F401
except Exception as exc:
    raise SystemExit(
        "ERROR: pandas is required by scripts/inspect_s3x_esa_schema.py. "
        "Install it in the active Python environment before continuing. "
        f"Original import error: {exc}"
    )
PY

available_kb="$(df -Pk "$BASE" | awk 'NR==2 {print $4}')"
required_kb=$((25 * 1024 * 1024))
if [ "$available_kb" -lt "$required_kb" ]; then
  echo "ERROR: at least 25 GiB free disk is required for the two archives plus extraction." >&2
  echo "available_kb=$available_kb" >&2
  exit 1
fi

file_size() {
  python3 - "$1" <<'PY'
from pathlib import Path
import sys
print(Path(sys.argv[1]).stat().st_size)
PY
}

hash_file() {
  python3 - "$1" "$2" <<'PY'
import hashlib
from pathlib import Path
import sys

path = Path(sys.argv[1])
algo = sys.argv[2]
h = hashlib.new(algo)
with path.open("rb") as f:
    for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
        h.update(chunk)
print(h.hexdigest())
PY
}

download_and_verify() {
  local name="$1"
  local url="$2"
  local expected_size="$3"
  local expected_md5="$4"
  local dest="$DOWNLOADS/$name"

  if [ -f "$dest" ] && [ "$(file_size "$dest")" = "$expected_size" ]; then
    echo "$name already has expected byte length; skipping download."
  else
    echo "Downloading/resuming $name ..."
    curl -L --fail --retry 6 --retry-delay 10 --continue-at - \
      --output "$dest" "$url"
  fi

  local actual_size
  actual_size="$(file_size "$dest")"
  if [ "$actual_size" != "$expected_size" ]; then
    echo "ERROR: $name byte-length mismatch" >&2
    echo "expected=$expected_size actual=$actual_size" >&2
    exit 1
  fi

  local actual_md5
  actual_md5="$(hash_file "$dest" md5)"
  if [ "$actual_md5" != "$expected_md5" ]; then
    echo "ERROR: $name Zenodo MD5 mismatch" >&2
    echo "expected=$expected_md5 actual=$actual_md5" >&2
    exit 1
  fi

  local actual_sha256
  actual_sha256="$(hash_file "$dest" sha256)"
  echo "$name size=$actual_size md5=$actual_md5 sha256=$actual_sha256"
}

resolve_mission_dir() {
  local root="$1"
  local mission="$2"

  if [ -f "$root/$mission/labels.csv" ]; then
    printf '%s\n' "$root/$mission"
    return 0
  fi
  if [ -f "$root/labels.csv" ]; then
    printf '%s\n' "$root"
    return 0
  fi

  echo "ERROR: unable to locate extracted $mission root under $root" >&2
  return 1
}

extract_if_needed() {
  local archive="$1"
  local root="$2"
  local mission="$3"

  if [ -f "$root/$mission/labels.csv" ] || [ -f "$root/labels.csv" ]; then
    echo "$mission already extracted; skipping unzip."
  else
    echo "Extracting $mission ..."
    mkdir -p "$root"
    unzip -q "$archive" -d "$root"
  fi
}

echo "===== S3X ESA v2 LOCAL SOURCE VERIFICATION ====="
echo "scientific_execution=NO"
echo "dataset_doi=10.5281/zenodo.15237121"

download_and_verify "$M1_NAME" "$M1_URL" "$M1_SIZE" "$M1_MD5"
download_and_verify "$M2_NAME" "$M2_URL" "$M2_SIZE" "$M2_MD5"

M1_EXTRACT="$EXTRACTED/mission1"
M2_EXTRACT="$EXTRACTED/mission2"

extract_if_needed "$DOWNLOADS/$M1_NAME" "$M1_EXTRACT" "ESA-Mission1"
extract_if_needed "$DOWNLOADS/$M2_NAME" "$M2_EXTRACT" "ESA-Mission2"

M1_DIR="$(resolve_mission_dir "$M1_EXTRACT" "ESA-Mission1")"
M2_DIR="$(resolve_mission_dir "$M2_EXTRACT" "ESA-Mission2")"

"$REPO_ROOT/study3x/validation/run_local_source_freeze.sh" \
  "$DOWNLOADS/$M1_NAME" "$M1_DIR" \
  "$DOWNLOADS/$M2_NAME" "$M2_DIR" \
  "$OUT"

echo
echo "S3X_LOCAL_SOURCE_FREEZE_WORKFLOW=PASS"
echo "freeze_record=$OUT/S3X_SOURCE_FREEZE_001.json"
echo "mission1_schema=$OUT/ESA-Mission1.schema.json"
echo "mission2_schema=$OUT/ESA-Mission2.schema.json"
echo "gap_rule_frozen=NO"
echo "trace_population_frozen=NO"
echo "recovery_policy_execution=NO"
echo "scientific_execution=NO"
