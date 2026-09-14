#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  run_pre_freeze_validation.sh \
    --cucd "/path/to/CubeSat Cybersecurity Dataset for Intrusion Detect.zip" \
    --aegissat "/path/to/AegisSat-AD.csv" \
    --unsw "/path/to/OneDrive_2026-09-13.zip" \
    [--output "/path/to/output-directory"]

Runs the same read-only Study 9 pre-freeze validator natively and in Docker,
then requires the deterministic validation_core.json files to be byte-identical.
The Docker validation runs with no network and read-only input mounts.
EOF
}

CUCD=""
AEGISSAT=""
UNSW=""
OUTPUT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --cucd) CUCD="${2:-}"; shift 2 ;;
    --aegissat) AEGISSAT="${2:-}"; shift 2 ;;
    --unsw) UNSW="${2:-}"; shift 2 ;;
    --output) OUTPUT="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

for pair in "CUCD:$CUCD" "AEGISSAT:$AEGISSAT" "UNSW:$UNSW"; do
  name="${pair%%:*}"
  value="${pair#*:}"
  if [[ -z "$value" || ! -f "$value" ]]; then
    echo "$name input file not found: $value" >&2
    exit 2
  fi
done

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required for the native validation." >&2
  exit 2
fi
if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is required for the cross-environment validation." >&2
  exit 2
fi
if ! docker info >/dev/null 2>&1; then
  echo "Docker is installed but the Docker daemon is not available." >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VALIDATOR="$SCRIPT_DIR/pre_freeze_dataset_validator.py"
DOCKERFILE="$SCRIPT_DIR/Dockerfile"

if [[ ! -f "$VALIDATOR" || ! -f "$DOCKERFILE" ]]; then
  echo "Validation source files are incomplete in $SCRIPT_DIR" >&2
  exit 2
fi

if [[ -z "$OUTPUT" ]]; then
  STAMP="$(date +%Y%m%d_%H%M%S)"
  OUTPUT="$HOME/Downloads/Study9_PreFreeze_Validation_${STAMP}"
fi

if [[ -e "$OUTPUT" ]]; then
  echo "Output path already exists; refusing to overwrite: $OUTPUT" >&2
  exit 2
fi

mkdir -p "$OUTPUT/native" "$OUTPUT/docker"

printf '\n============================================================\n'
printf 'STUDY 9 PRE-FREEZE REPRODUCIBILITY VALIDATION\n'
printf '============================================================\n'
printf 'CuCD-ID:  %s\n' "$CUCD"
printf 'AegisSat: %s\n' "$AEGISSAT"
printf 'UNSW:     %s\n' "$UNSW"
printf 'Output:   %s\n' "$OUTPUT"
printf '============================================================\n\n'

printf '[1/5] Native macOS/host validation\n'
python3 "$VALIDATOR" \
  --cucd-zip "$CUCD" \
  --aegissat-csv "$AEGISSAT" \
  --unsw-zip "$UNSW" \
  --output "$OUTPUT/native" \
  --environment-label native

printf '\n[2/5] Building validation container\n'
IMAGE_TAG="study9-prefreeze-validator:local"
docker build \
  --file "$DOCKERFILE" \
  --tag "$IMAGE_TAG" \
  "$SCRIPT_DIR"

printf '\n[3/5] Docker/Linux validation with read-only inputs and no network\n'
docker run --rm \
  --network none \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=64m \
  --user "$(id -u):$(id -g)" \
  --mount "type=bind,source=$CUCD,target=/inputs/cucd.zip,readonly" \
  --mount "type=bind,source=$AEGISSAT,target=/inputs/AegisSat-AD.csv,readonly" \
  --mount "type=bind,source=$UNSW,target=/inputs/unsw.zip,readonly" \
  --mount "type=bind,source=$OUTPUT/docker,target=/output" \
  "$IMAGE_TAG" \
  --cucd-zip /inputs/cucd.zip \
  --aegissat-csv /inputs/AegisSat-AD.csv \
  --unsw-zip /inputs/unsw.zip \
  --output /output \
  --environment-label docker-linux

printf '\n[4/5] Comparing deterministic native and Docker validation cores\n'
python3 - "$OUTPUT/native/validation_core.json" "$OUTPUT/docker/validation_core.json" "$OUTPUT" <<'PY'
import hashlib
import json
import sys
from pathlib import Path

native = Path(sys.argv[1])
docker = Path(sys.argv[2])
out = Path(sys.argv[3])
nb = native.read_bytes()
db = docker.read_bytes()
ns = hashlib.sha256(nb).hexdigest()
ds = hashlib.sha256(db).hexdigest()
identical = nb == db
comparison = {
    "schema": 1,
    "study_id": "S9-RTSI-001",
    "stage": "PRE_FREEZE_CROSS_ENVIRONMENT_COMPARISON",
    "native_validation_core_sha256": ns,
    "docker_validation_core_sha256": ds,
    "byte_identical": identical,
    "status": "PASS" if identical else "FAIL",
}
(out / "cross_environment_comparison.json").write_text(
    json.dumps(comparison, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)
print(json.dumps(comparison, indent=2, sort_keys=True))
if not identical:
    raise SystemExit("Native and Docker deterministic validation cores differ.")
PY

printf '\n[5/5] Creating compact evidence bundle\n'
python3 - "$OUTPUT" <<'PY'
import hashlib
import json
import sys
import zipfile
from pathlib import Path

out = Path(sys.argv[1])
bundle = out.with_name(out.name + "_evidence.zip")
include = [
    out / "native" / "validation_core.json",
    out / "native" / "validation_report.json",
    out / "docker" / "validation_core.json",
    out / "docker" / "validation_report.json",
    out / "cross_environment_comparison.json",
]
with zipfile.ZipFile(bundle, "w", compression=zipfile.ZIP_DEFLATED) as zf:
    for path in include:
        zf.write(path, arcname=str(path.relative_to(out)))
sha = hashlib.sha256(bundle.read_bytes()).hexdigest()
summary = {
    "bundle": str(bundle),
    "bundle_sha256": sha,
    "files": [str(p.relative_to(out)) for p in include],
}
(out / "EVIDENCE_BUNDLE.json").write_text(
    json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)
print(f"Evidence bundle: {bundle}")
print(f"Bundle SHA-256:  {sha}")
PY

printf '\n============================================================\n'
printf 'PASS: PRE-FREEZE VALIDATION COMPLETE\n'
printf '============================================================\n'
printf 'Evidence directory: %s\n' "$OUTPUT"
printf 'Upload bundle:      %s_evidence.zip\n' "$OUTPUT"
printf '\nNo Study 9 semantic mapping or endpoint computation was performed.\n'
