#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 5 ]; then
  echo "usage: $0 <ESA-Mission1.zip> <ESA-Mission1-dir> <ESA-Mission2.zip> <ESA-Mission2-dir> <output-dir>" >&2
  exit 2
fi

M1_ARCHIVE="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
M1_DIR="$(cd "$2" && pwd)"
M2_ARCHIVE="$(cd "$(dirname "$3")" && pwd)/$(basename "$3")"
M2_DIR="$(cd "$4" && pwd)"
OUT="$(mkdir -p "$5" && cd "$5" && pwd)"

REPO_ROOT="$(git rev-parse --show-toplevel)"
INSPECTOR="$REPO_ROOT/scripts/inspect_s3x_esa_schema.py"
FINALIZER="$REPO_ROOT/study3x/validation/finalize_esa_v2_source_freeze.py"

python3 "$INSPECTOR" "$M1_DIR" --output "$OUT/ESA-Mission1.schema.json"
python3 "$INSPECTOR" "$M2_DIR" --output "$OUT/ESA-Mission2.schema.json"

python3 "$FINALIZER" \
  --mission1-archive "$M1_ARCHIVE" \
  --mission2-archive "$M2_ARCHIVE" \
  --mission1-schema "$OUT/ESA-Mission1.schema.json" \
  --mission2-schema "$OUT/ESA-Mission2.schema.json" \
  --output "$OUT/S3X_SOURCE_FREEZE_001.json"

echo "S3X_LOCAL_SOURCE_VERIFICATION=PASS"
echo "output_dir=$OUT"
echo "scientific_execution=NO"
