#!/usr/bin/env bash
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel)"
AUTH="$ROOT/study6x/S6X_CANONICAL_RUNTIME_AUTH_001.json"
SOURCE="$ROOT/study6x/external/cFS-v7.0.1"
ENV_TAR="$ROOT/study6x/workspace/S6X_BUILD_ENVIRONMENT_001.tar"
CAMPAIGN="$ROOT/study6x/workspace/S6X_CANONICAL_EXECUTION_001"
HARNESS="$ROOT/study6x/fixtures/S6X_INVARIANT_HARNESS_EQUALITY_001.patch"
FIXTURE="$ROOT/study6x/fixtures/S6X_FIXTURE_GT_EQ_BOUNDARY_001.patch"
RUNTIME="$ROOT/study6x/runtime/run_canonical_population.py"
VALIDATOR="$ROOT/study6x/audit/validate_canonical_execution.py"
EXPECTED_CFS="088b2fa828db9ff7e00733f1908e0eeb59f66ce3"
EXPECTED_LC="a1c3a47ea1fa5c0d7751d6ff88848dc9bd8a6c7a"
EXPECTED_IMAGE="sha256:3877a5c519fff5266cc4d34e43ac90f6430320851928f42906c79ecd58f7bb43"
EXPECTED_TAR_SHA="7b043f3c330fa992a119996f43f83d8d3c6621650933460bb8f71c587ddeb21d"

if [ "$(git branch --show-current)" != "main" ]; then echo "ERROR: S6X canonical execution must run from main" >&2; exit 2; fi
if ! git diff --quiet || ! git diff --cached --quiet; then echo "ERROR: clean tracked worktree required" >&2; exit 2; fi
git ls-files --error-unmatch "study6x/S6X_CANONICAL_RUNTIME_AUTH_001.json" >/dev/null

python3 - "$AUTH" <<'PY'
import json,sys
a=json.load(open(sys.argv[1])); 
if a.get("authorization_id")!="S6X-CANONICAL-RUNTIME-AUTH-001": raise SystemExit("bad auth id")
s=a["authorization_scope"]
for k in ("frozen_environment_use_authorized","cfs_build_authorized","semantic_fixture_application_to_build_authorized","research_only_artifact_signing_authorized","provenance_observation_generation_authorized","independent_rebuild_authorized","qualification_gate_execution_authorized","scientific_execution_authorized","independent_reference_validation_authorized","deterministic_repeat_execution_authorized"):
    if s.get(k) is not True: raise SystemExit(f"authorization not open: {k}")
for k in ("result_freeze_authorized","canonical_output_commit_authorized","manuscript_claim_use_authorized","figure_revision_authorized","study6_modification_authorized","study6_s6x_pooling_authorized","venue_lock_authorized"):
    if s.get(k) is not False: raise SystemExit(f"prohibited scope open: {k}")
PY

test -f "$ENV_TAR" || { echo "ERROR: frozen environment tar missing" >&2; exit 2; }
ACTUAL_TAR_SHA="$(shasum -a 256 "$ENV_TAR" | awk '{print $1}')"
test "$ACTUAL_TAR_SHA" = "$EXPECTED_TAR_SHA" || { echo "ERROR: environment tar SHA mismatch" >&2; exit 2; }
if ! docker image inspect "$EXPECTED_IMAGE" >/dev/null 2>&1; then docker load -i "$ENV_TAR" >/dev/null; fi
ACTUAL_IMAGE="$(docker image inspect s6x-build-env:001 --format '{{.Id}}')"
test "$ACTUAL_IMAGE" = "$EXPECTED_IMAGE" || { echo "ERROR: frozen image ID mismatch" >&2; exit 2; }

test "$(git -C "$SOURCE" rev-parse HEAD)" = "$EXPECTED_CFS" || exit 2
git -C "$SOURCE" submodule update --init --recursive
test "$(git -C "$SOURCE/apps/lc" rev-parse HEAD)" = "$EXPECTED_LC" || exit 2
test -z "$(git -C "$SOURCE" status --porcelain --untracked-files=no)" || { echo "ERROR: source checkout modified" >&2; exit 2; }

if [ -e "$CAMPAIGN" ] && [ -n "$(find "$CAMPAIGN" -mindepth 1 -maxdepth 1 -print -quit 2>/dev/null)" ]; then
  echo "ERROR: canonical campaign directory must be absent or empty: $CAMPAIGN" >&2; exit 2
fi
mkdir -p "$CAMPAIGN/keys"
openssl genpkey -algorithm ED25519 -out "$CAMPAIGN/keys/private.pem" >/dev/null 2>&1
openssl pkey -in "$CAMPAIGN/keys/private.pem" -pubout -out "$CAMPAIGN/keys/public.pem" >/dev/null 2>&1
PUB_SHA="$(shasum -a 256 "$CAMPAIGN/keys/public.pem" | awk '{print $1}')"

copy_source() {
  local dst="$1"
  python3 - "$SOURCE" "$dst" <<'PY'
from pathlib import Path
import shutil,sys
src=Path(sys.argv[1]); dst=Path(sys.argv[2])
if dst.exists(): raise SystemExit("destination already exists")
shutil.copytree(src,dst,ignore=shutil.ignore_patterns("build-native_std","*.log"))
PY
}

build_one() {
  local run="$1" state_name="$2" kind="$3"
  local src="$CAMPAIGN/$run/builds/${state_name}_${kind}/src"
  mkdir -p "$(dirname "$src")"; copy_source "$src"
  git -C "$src/apps/lc" apply "$HARNESS"
  if [ "$state_name" = "APPROVED_BAD_SOURCE" ]; then git -C "$src/apps/lc" apply "$FIXTURE"; fi
  docker run --rm --platform linux/amd64 --user "$(id -u):$(id -g)" -e HOME=/tmp     -v "$src:/work/cfs" -w /work/cfs "$EXPECTED_IMAGE" bash -lc '
      set -e
      make native_std.prep
      make native_std.install
      set +e
      make native_std.runtest > .s6x_runtest.log 2>&1
      rc=$?
      set -e
      echo "$rc" > .s6x_runtest_rc
      exit 0
    '
  local artifact="$src/build-native_std/exe/cpu1/lc.so"
  test -f "$artifact" || { echo "ERROR: designated LC artifact missing: $artifact" >&2; exit 2; }
  shasum -a 256 "$artifact" | awk '{print $1}'
}

run_once() {
  local run="$1"; local runroot="$CAMPAIGN/$run"; mkdir -p "$runroot/results"
  CLEAN_PRIMARY="$(build_one "$run" CLEAN_APPROVED primary)"
  CLEAN_REBUILD="$(build_one "$run" CLEAN_APPROVED rebuild)"
  BAD_PRIMARY="$(build_one "$run" APPROVED_BAD_SOURCE primary)"
  BAD_REBUILD="$(build_one "$run" APPROVED_BAD_SOURCE rebuild)"
  test "$CLEAN_PRIMARY" = "$CLEAN_REBUILD" || { echo "ERROR: clean rebuild hash mismatch" >&2; exit 2; }
  test "$BAD_PRIMARY" = "$BAD_REBUILD" || { echo "ERROR: bad-source rebuild hash mismatch" >&2; exit 2; }
  test "$CLEAN_PRIMARY" != "$BAD_PRIMARY" || { echo "ERROR: clean/bad artifact hashes unexpectedly equal" >&2; exit 2; }
  CLEAN_SRC="$runroot/builds/CLEAN_APPROVED_primary/src"; BAD_SRC="$runroot/builds/APPROVED_BAD_SOURCE_primary/src"
  CLEAN_RC="$(cat "$CLEAN_SRC/.s6x_runtest_rc")"; BAD_RC="$(cat "$BAD_SRC/.s6x_runtest_rc")"
  test "$CLEAN_RC" -eq 0 || { echo "ERROR: clean test suite failed rc=$CLEAN_RC" >&2; exit 2; }
  test "$BAD_RC" -ne 0 || { echo "ERROR: bad-source test suite unexpectedly passed" >&2; exit 2; }
  CLEAN_ART="$CLEAN_SRC/build-native_std/exe/cpu1/lc.so"; BAD_ART="$BAD_SRC/build-native_std/exe/cpu1/lc.so"
  openssl pkeyutl -sign -rawin -inkey "$CAMPAIGN/keys/private.pem" -in "$CLEAN_ART" -out "$runroot/clean.sig"
  openssl pkeyutl -verify -rawin -pubin -inkey "$CAMPAIGN/keys/public.pem" -sigfile "$runroot/clean.sig" -in "$CLEAN_ART" >/dev/null
  openssl pkeyutl -sign -rawin -inkey "$CAMPAIGN/keys/private.pem" -in "$BAD_ART" -out "$runroot/bad.sig"
  openssl pkeyutl -verify -rawin -pubin -inkey "$CAMPAIGN/keys/public.pem" -sigfile "$runroot/bad.sig" -in "$BAD_ART" >/dev/null
  CLEAN_SIG="$(shasum -a 256 "$runroot/clean.sig" | awk '{print $1}')"; BAD_SIG="$(shasum -a 256 "$runroot/bad.sig" | awk '{print $1}')"
  PYTHONPATH="$ROOT" python3 "$RUNTIME" --authorization-record "$AUTH" --output-dir "$runroot/results"     --clean-artifact-sha256 "$CLEAN_PRIMARY" --bad-artifact-sha256 "$BAD_PRIMARY"     --clean-signature-sha256 "$CLEAN_SIG" --bad-signature-sha256 "$BAD_SIG"     --public-key-sha256 "$PUB_SHA" --clean-runtest-rc "$CLEAN_RC" --bad-runtest-rc "$BAD_RC"
  PYTHONPATH="$ROOT" python3 "$VALIDATOR" --run-dir "$runroot/results"
  cat > "$runroot/build_hashes.txt" <<EOF
clean_artifact_sha256=$CLEAN_PRIMARY
bad_artifact_sha256=$BAD_PRIMARY
clean_runtest_rc=$CLEAN_RC
bad_runtest_rc=$BAD_RC
EOF
}

echo "===== S6X CANONICAL SCIENTIFIC EXECUTION ====="
echo "result_freeze=NO"; echo "manuscript_claim_use=NO"
run_once run1
run_once run2
for name in S6X_GATE_OBSERVATIONS_001.csv S6X_SUMMARY_001.json S6X_EVIDENCE_RECORDS_001.json S6X_INDEPENDENT_VALIDATION_001.json S6X_RESULTS_HASH_MANIFEST_001.json; do
  H1="$(shasum -a 256 "$CAMPAIGN/run1/results/$name" | awk '{print $1}')"
  H2="$(shasum -a 256 "$CAMPAIGN/run2/results/$name" | awk '{print $1}')"
  test "$H1" = "$H2" || { echo "ERROR: repeat output mismatch for $name" >&2; exit 2; }
  echo "$name_sha256=$H1"
done
cmp -s "$CAMPAIGN/run1/build_hashes.txt" "$CAMPAIGN/run2/build_hashes.txt" || { echo "ERROR: repeated build hashes/test outcomes differ" >&2; exit 2; }
echo "S6X_CANONICAL_SCIENTIFIC_EXECUTION_AND_VALIDATION=PASS"
echo "observations_per_run=396"; echo "repetitions=2"; echo "total_builds=8"
echo "result_freeze=NO"; echo "manuscript_claim_use=NO"
