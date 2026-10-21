#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
OUT="${1:-$REPO_ROOT/study6x/workspace}"
mkdir -p "$OUT"

DOCKERFILE="$REPO_ROOT/study6x/validation/S6X_BUILD_ENVIRONMENT_002.Dockerfile"
TAG="s6x-build-env:002"
TAR="$OUT/S6X_BUILD_ENVIRONMENT_002.tar"
JSON_OUT="$OUT/S6X_BUILD_ENVIRONMENT_FREEZE_CANDIDATE_002.json"

for cmd in docker python3; do
  command -v "$cmd" >/dev/null 2>&1 || {
    echo "ERROR: required command not found: $cmd" >&2
    exit 1
  }
done

echo "===== S6X BUILD ENVIRONMENT V2 PREPARATION ONLY ====="
echo "supersedes_environment=001"
echo "correction=ADD_JQ_REQUIRED_BY_NATIVE_STD_RUNTEST"
echo "cfs_build_authorized=NO"
echo "scientific_execution=NO"

docker build --platform linux/amd64 --pull=false --no-cache --tag "$TAG" - < "$DOCKERFILE"

IMAGE_ID="$(docker image inspect "$TAG" --format '{{.Id}}')"
docker save "$TAG" --output "$TAR"

TAR_SHA256="$(python3 - "$TAR" <<'PYHASH'
import hashlib
import sys
from pathlib import Path
p=Path(sys.argv[1])
h=hashlib.sha256()
with p.open("rb") as f:
    for chunk in iter(lambda:f.read(1024*1024),b""):
        h.update(chunk)
print(h.hexdigest())
PYHASH
)"

VERSIONS="$(docker run --rm --platform linux/amd64 "$TAG" bash -lc '
set -e
printf "gcc="; gcc --version | head -n1
printf "cmake="; cmake --version | head -n1
printf "make="; make --version | head -n1
printf "git="; git --version
printf "jq="; jq --version
printf "python="; python3 --version
printf "openssl="; openssl version
uname -a
')"

python3 - "$JSON_OUT" "$IMAGE_ID" "$TAR_SHA256" "$VERSIONS" <<'PY'
import json
import sys
from pathlib import Path

out=Path(sys.argv[1])
record={
    "schema":1,
    "experiment_id":"S6X-EAP-001",
    "environment_id":"S6X-BUILD-ENVIRONMENT-002",
    "supersedes_environment_id":"S6X-BUILD-ENVIRONMENT-001",
    "status":"ENVIRONMENT_V2_FREEZE_CANDIDATE__NO_CFS_BUILD_EXECUTED",
    "platform":"linux/amd64",
    "base_image":"amd64/ubuntu:noble-20260911@sha256:496754492fb28b4d3049432f2ca787449331e23fb14f0dd3fffea86bf5a93eb4",
    "correction":["add jq required by pinned cFS native_std.runtest"],
    "local_image_id":sys.argv[2],
    "saved_image_tar_sha256":sys.argv[3],
    "tool_versions":sys.argv[4].splitlines(),
    "cfs_build_executed":False,
    "fixture_applied":False,
    "artifact_signing_executed":False,
    "scientific_execution":False,
    "next_gate":"AUTHOR_REVIEW_OF_S6X_ENVIRONMENT_V2_FREEZE_CANDIDATE_BEFORE_CORRECTED_RUNTIME_AUTHORIZATION"
}
out.write_text(json.dumps(record,indent=2)+"\n",encoding="utf-8")
print(f"environment_v2_candidate_json={out}")
PY

echo "S6X_BUILD_ENVIRONMENT_V2_PREP=PASS"
echo "image_id=$IMAGE_ID"
echo "image_tar_sha256=$TAR_SHA256"
echo "cfs_build_executed=NO"
echo "scientific_execution=NO"
