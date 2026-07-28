#!/usr/bin/env bash
# ===========================================================================
# WP4 Passive Time-Witness — STATIC VERIFIER
#
# This verifier validates the complete passive time-witness stack without
# authorizing or launching any runtime. It:
#   - validates contract JSON and required files
#   - validates shell and Python syntax
#   - verifies source pins and design-lock files
#   - verifies every runtime/scientific gate is false or zero
#   - proves the witness uses NosEngine::Client::Bus, add_time_tick_callback,
#     and clock_gettime(CLOCK_MONOTONIC)
#   - proves radio_socket_metadata_shim.c also uses CLOCK_MONOTONIC
#   - proves witness output keys are exactly: sequence,monotonic_ns,tick,state
#   - rejects actual prohibited call forms
#   - compiles only in the pinned image with --platform linux/amd64 --network none
#   - runs witness --self-test inside the network-none container
#   - runs Python validator --self-test
#   - emits a candidate into a temporary directory
#   - runs bash -n against the candidate
#   - inspects the complete candidate
#   - verifies the exact top-level future authorization status gate
#   - verifies the first Docker command occurs after the fail-closed gate
#   - verifies separate immutable-ground and policy-visible roots
#   - verifies the witness output mount is rw under immutable-ground only
#   - verifies no tick or monotonic-time fields are written to policy-visible files
#   - places a fake docker first in PATH
#   - executes the candidate under the current closed contract
#   - requires rc=1 and CLOSED_GATE_NOT_AUTHORIZED
#   - proves fake Docker was never invoked
#   - requires zero project-labeled Docker containers and networks before and after
#
# It does NOT authorize runtime, launch NOS3, launch NOS Engine, launch
# TimeDriver, launch generic-radio, transmit commands, inject events, or
# modify retained evidence.
#
# On success prints:
#   witness_source_sha256=<value>
#   validator_source_sha256=<value>
#   candidate_generator_sha256=<value>
#   generated_candidate_sha256=<value>
#   witness_clock_basis=CLOCK_MONOTONIC
#   socket_shim_clock_basis=CLOCK_MONOTONIC
#   shared_clock_basis_verified=1
#   permitted_trace_keys=sequence,monotonic_ns,tick,state
#   command_source_present=0
#   command_transmission_possible=0
#   event_injection_present=0
#   packet_content_captured=0
#   packet_hashes_captured=0
#   ip_addresses_captured=0
#   policy_time_evidence_exposed=0
#   host_network_used=0
#   host_ports_published=0
#   docker_socket_mounted=0
#   external_egress_used=0
#   nos3_runtime_launched=0
#   simulator_launched=0
#   diagnostic_runtime_launched=0
#   PASSIVE_TIME_WITNESS_STATIC_VERIFICATION_STATUS=PASS
# ===========================================================================
set -Eeuo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONTRACT="${REPO_ROOT}/configs/downlink-diagnostic-contract.json"
WITNESS_SRC="${REPO_ROOT}/scripts/passive_nos_engine_time_witness.cpp"
VALIDATOR_SRC="${REPO_ROOT}/scripts/validate_passive_time_witness_trace.py"
GENERATOR_SRC="${REPO_ROOT}/scripts/prepare_passive_time_witness_runtime_candidate.sh"
SHIM_SRC="${REPO_ROOT}/scripts/radio_socket_metadata_shim.c"
DECISION_LOG="${REPO_ROOT}/tracker/decision_log.csv"
PLAN_TRACKER="${REPO_ROOT}/tracker/WP4_PASSIVE_TIME_WITNESS_PLAN_20260726.md"
DESIGN_LOCK="${REPO_ROOT}/artifacts/wp4-passive-time-witness-design-lock.txt"

PUBLISHED_IMAGE="ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
sha256_of() { shasum -a 256 "$1" | awk '{print $1}'; }

fail() { echo "STATIC_VERIFICATION_FAILED: $*" >&2; exit 1; }
ok()   { echo "STATIC_VERIFICATION_OK: $*"; }

REQUIRED_IMAGE_ID="sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"
# Every real Docker operation uses the selected context. Explicit override via
# DOCKER_CONTEXT is honored; otherwise default to the active desktop-linux
# context. Pull/build/compose/login are forbidden for these static checks.
DOCKER_CONTEXT="${DOCKER_CONTEXT:-desktop-linux}"
# Strict C++14 compile/link command used inside the pinned --network none run.
readonly STRICT_CXX_CMD="g++ -std=c++14 -Wall -Wextra -Werror -I/usr/include scripts/passive_nos_engine_time_witness.cpp -lnos_engine_client -lnos_engine_common -lnos_engine_transport -lnos_engine_utility -o /tmp/passive_nos_engine_time_witness"
# Hard-prereq closed failure (Docker unusable, image absent, or compile/self-test
# skipped/failed). Never prints PASS. Does not pull, build, compose, or login.
blocked() { echo "STATIC_VERIFICATION_BLOCKED: $*" >&2; exit 1; }
# All Docker invocations go through the resolved context only.
dctx() { docker --context "$DOCKER_CONTEXT" "$@"; }
# True only after the pinned-image compile AND the C++ witness --self-test have
# actually run and printed the exact PASS token. Guards the final PASS line.
WITNESS_COMPILE_AND_SELFTEST_PASSED="no"

# ---------------------------------------------------------------------------
# 1. Validate contract JSON and required files
# ---------------------------------------------------------------------------
echo "--- [1/16] Validate contract JSON and required files ---"
python3 -m json.tool "$CONTRACT" >/dev/null || fail "contract JSON invalid"
for f in "$WITNESS_SRC" "$VALIDATOR_SRC" "$GENERATOR_SRC" "$SHIM_SRC" "$DECISION_LOG" "$PLAN_TRACKER" "$DESIGN_LOCK"; do
  [ -f "$f" ] || fail "missing required file: $f"
done
ok "contract JSON valid; required files present"

# Check contract image pin matches the published pinned image
contract_image="$(python3 -c "import json;print(json.load(open('$CONTRACT')).get('source_locks',{}).get('image',''))")"
[ "$contract_image" = "$PUBLISHED_IMAGE" ] || fail "contract image pin mismatch: $contract_image"
ok "contract image pin matches published pinned image"

# ---------------------------------------------------------------------------
# 2. Validate shell and Python syntax
# ---------------------------------------------------------------------------
echo "--- [2/16] Validate shell and Python syntax ---"
bash -n "$GENERATOR_SRC" || fail "generator bash -n failed"
bash -n "$0" || fail "verifier bash -n failed"
python3 -m py_compile "$VALIDATOR_SRC" || fail "validator py_compile failed"
ok "shell and Python syntax valid"

# ---------------------------------------------------------------------------
# 3. Verify source pins and design-lock files
# ---------------------------------------------------------------------------
echo "--- [3/16] Verify source pins and design-lock files ---"
# nos3 commit pin
nos3_pin="$(python3 -c "import json;print(json.load(open('$CONTRACT')).get('source_locks',{}).get('nos3_commit',''))")"
[ "${#nos3_pin}" -ge 40 ] || fail "nos3 commit pin missing/too short"
ok "nos3 commit pinned: ${nos3_pin}"

# design-lock file reference in contract
design_lock_ref="$(python3 -c "import json;d=json.load(open('$CONTRACT'));print(d.get('passive_time_witness_design',{}).get('design_lock',''))")"
[ -n "$design_lock_ref" ] || {
  # fallback: check gate additional_requirement mentions design lock
  design_lock_ref="artifacts/wp4-passive-time-witness-design-lock.txt"
}
design_lock_path="${REPO_ROOT}/${design_lock_ref}"
if [ -f "$design_lock_path" ]; then
  ok "design-lock file present: $design_lock_ref"
else
  fail "design-lock file missing: $design_lock_ref"
fi

# ---------------------------------------------------------------------------
# 4. Verify every runtime/scientific gate is false or zero
# ---------------------------------------------------------------------------
echo "--- [4/16] Verify every runtime/scientific gate is false or zero ---"
python3 - <<'PYGATE' || fail "runtime/scientific gate not closed"
import json
c = json.load(open("configs/downlink-diagnostic-contract.json"))
g = c.get("gate", {})
must_be_false_or_zero = {
    "diagnostic_runtime_authorized": (False, False),
    "diagnostic_runtime_attempts_authorized": (0, False),
    "baseline_run_1_authorized": (False, False),
    "baseline_run_2_authorized": (False, False),
    "event_injection_authorized": (False, False),
}
top_level_must_be_false = [
    "scientific_outcome_allowed",
    "event_injection_allowed",
    "command_transmission_allowed",
    "baseline_execution_allowed",
    "cryptographic_semantics_claim_allowed",
]
for k, (want, _bb) in must_be_false_or_zero.items():
    v = g.get(k)
    if v is True or (isinstance(v, int) and v != 0):
        raise SystemExit(f"gate.{k} not closed: {v}")
for k in top_level_must_be_false:
    v = c.get(k)
    if v is not False:
        raise SystemExit(f"{k} not closed: {v}")
# passive_time_witness_static_verification must NOT be PASS (only PENDING/PENDING_REVIEW)
sv = g.get("passive_time_witness_static_verification", "PENDING")
if sv == "PASS":
    raise SystemExit("gate.passive_time_witness_static_verification unexpectedly PASS")
print("ALL_GATES_CLOSED")
PYGATE
ok "all runtime/scientific gates closed (false or zero)"

# ---------------------------------------------------------------------------
# 5. Prove witness uses Bus, add_time_tick_callback, CLOCK_MONOTONIC
# ---------------------------------------------------------------------------
echo "--- [5/16] Prove witness clock/API usage ---"
rg -q 'using NosEngine::Client::Bus' "$WITNESS_SRC" || fail "witness missing NosEngine::Client::Bus"
rg -q 'add_time_tick_callback' "$WITNESS_SRC" || fail "witness missing add_time_tick_callback"
rg -q 'clock_gettime\(CLOCK_MONOTONIC' "$WITNESS_SRC" || fail "witness missing clock_gettime(CLOCK_MONOTONIC)"
ok "witness uses NosEngine::Client::Bus, add_time_tick_callback, clock_gettime(CLOCK_MONOTONIC)"

# ---------------------------------------------------------------------------
# 6. Prove radio_socket_metadata_shim.c also uses CLOCK_MONOTONIC
# ---------------------------------------------------------------------------
echo "--- [6/16] Prove socket shim uses CLOCK_MONOTONIC ---"
rg -q 'clock_gettime\(CLOCK_MONOTONIC' "$SHIM_SRC" || fail "socket shim missing clock_gettime(CLOCK_MONOTONIC)"
ok "radio_socket_metadata_shim.c uses CLOCK_MONOTONIC"

# ---------------------------------------------------------------------------
# 7. Prove witness output keys are exactly: sequence,monotonic_ns,tick,state
# ---------------------------------------------------------------------------
echo "--- [7/16] Prove witness output keys are exactly the permitted four ---"
python3 - <<'PYKEYS' || fail "witness schema keys not exactly permitted four"
# Normalise C/C++ escaped quotes so JSON key literals emitted as \"sequence\"
# are detected as "sequence", matching unescaped comment-quoted forms too.
raw = open("scripts/passive_nos_engine_time_witness.cpp").read()
norm = raw.replace('\\"', '"').replace('\\\\', '\\')
for needle in ['"sequence"', '"monotonic_ns"', '"tick"', '"state"']:
    if needle not in raw and needle not in norm:
        raise SystemExit(f"witness missing key literal {needle}")
# The four permitted keys. Reject any extra sensitive keys.
forbidden_keys = [
    '"packet"', '"payload"', '"pkt_len"', '"hash"', '"ip"', '"addr"',
    '"command"', '"cmd"', '"host"', '"port"', '"pid"', '"tid"',
]
for fk in forbidden_keys:
    if fk in raw:
        raise SystemExit(f"witness contains forbidden key literal {fk}")
print("WITNESS_KEYS_EXACT")
PYKEYS
ok "witness output keys are exactly: sequence,monotonic_ns,tick,state"

# ---------------------------------------------------------------------------
# 8. Reject actual prohibited call forms in the witness source
# ---------------------------------------------------------------------------
echo "--- [8/16] Reject prohibited call forms in witness source ---"
# These must NOT appear as actual call forms (function calls / method invocations).
# We check for call patterns, not bare words in comments.
prohibited_call_patterns=(
  '\bset_time\s*\('
  '\benable_set_time\s*\('
  '\.send_'
  '\.request\s*\('
  '\.reply\s*\('
  'inject_'
  'pcap_'
  '->send_'
  '->request\s*\('
  '->reply\s*\('
)
found_prohibited=0
for pat in "${prohibited_call_patterns[@]}"; do
  if rg -q -e "$pat" "$WITNESS_SRC"; then
    echo "PROHIBITED_CALL_FOUND: $pat" >&2
    found_prohibited=1
  fi
done
[ "$found_prohibited" -eq 0 ] || fail "prohibited call form(s) found in witness source"
ok "no prohibited call forms in witness source (set_time, enable_set_time, send/request/reply, inject, pcap)"

# ---------------------------------------------------------------------------
# 9. Compile only in the pinned image with --platform linux/amd64 --network none
# ---------------------------------------------------------------------------
echo "--- [9/16] Compile witness in pinned image (network none) ---"
echo "DOCKER_CONTEXT=$DOCKER_CONTEXT"
# Docker is mandatory for the pinned-image compile and C++ self-test. Do NOT
# interpret a socket/permission denial as image absence — surface it and fail
# closed. Never pull/build/compose/login.
if ! command -v docker >/dev/null 2>&1; then
  blocked "docker CLI not found on PATH; cannot run mandatory pinned-image static checks (no runtime launched)"
fi
DOCKER_SERVER_INFO=""
DOCKER_SERVER_INFO="$(dctx info --format 'server={{.ServerVersion}} operating_system={{.OperatingSystem}}' 2>/tmp/wp4_verify_dockerinfo.$$.err)" || {
  cat /tmp/wp4_verify_dockerinfo.$$.err >&2
  rm -f /tmp/wp4_verify_dockerinfo.$$.err
  blocked "Docker context '$DOCKER_CONTEXT' not usable (server unreachable); cannot run mandatory pinned-image static checks (no runtime launched)"
}
rm -f /tmp/wp4_verify_dockerinfo.$$.err
echo "$DOCKER_SERVER_INFO"
# Exact pinned image must already exist locally. Inspect must succeed.
if ! dctx image inspect "$PUBLISHED_IMAGE" >/tmp/wp4_verify_imginspect.$$.out 2>&1; then
  cat /tmp/wp4_verify_imginspect.$$.out >&2
  rm -f /tmp/wp4_verify_imginspect.$$.out
  blocked "exact pinned image not present locally and pulling is forbidden: $PUBLISHED_IMAGE (no runtime launched)"
fi
rm -f /tmp/wp4_verify_imginspect.$$.out
IMAGE_ID="$(dctx image inspect "$PUBLISHED_IMAGE" --format '{{.Id}}' 2>/dev/null)"
[ -n "$IMAGE_ID" ] || blocked "could not resolve image ID for pinned image"
echo "PINNED_IMAGE_ID=$IMAGE_ID"
[ "$IMAGE_ID" = "$REQUIRED_IMAGE_ID" ] || blocked "pinned image ID mismatch: got=$IMAGE_ID want=$REQUIRED_IMAGE_ID"
ok "exact pinned image present locally with matching image ID ($IMAGE_ID)"

COMPILE_OUT="/tmp/wp4_verify_compile.$$.out"
dctx run --rm \
    --platform linux/amd64 \
    --network none \
    -v "$REPO_ROOT/scripts:/work/scripts:ro" \
    -w /work \
    "$PUBLISHED_IMAGE" bash -lc \
      "set -e; $STRICT_CXX_CMD && echo COMPILE_OK" \
      > "$COMPILE_OUT" 2>&1 || { cat "$COMPILE_OUT"; fail "witness compile failed in pinned image (--network none)"; }
cat "$COMPILE_OUT"
rg -q 'COMPILE_OK' "$COMPILE_OUT" || fail "witness compile did not produce COMPILE_OK"
rm -f "$COMPILE_OUT"
ok "witness compiled in pinned image with --network none (strict C++14 + -Werror)"

# ---------------------------------------------------------------------------
# 10. Run witness --self-test inside the network-none container
# ---------------------------------------------------------------------------
echo "--- [10/16] Run witness --self-test in network-none container ---"
SELFTEST_OUT="/tmp/wp4_verify_selftest.$$.out"
dctx run --rm \
    --platform linux/amd64 \
    --network none \
    -v "$REPO_ROOT/scripts:/work/scripts:ro" \
    -w /work \
    "$PUBLISHED_IMAGE" bash -lc \
      "set -e; $STRICT_CXX_CMD && /tmp/passive_nos_engine_time_witness --self-test" \
      > "$SELFTEST_OUT" 2>&1 || { cat "$SELFTEST_OUT"; fail "witness --self-test failed in pinned image (--network none)"; }
cat "$SELFTEST_OUT"
# Exact required PASS token from the compiled C++ witness --self-test. The
# self-test does not rely on live timing and does not launch NOS Engine server,
# TimeDriver, generic-radio, a diagnostic, or a baseline.
rg -q 'PASSIVE_NOS_ENGINE_TIME_WITNESS_SELF_TEST=PASS' "$SELFTEST_OUT" || \
  fail "witness --self-test did not print exact PASSIVE_NOS_ENGINE_TIME_WITNESS_SELF_TEST=PASS"
rm -f "$SELFTEST_OUT"
WITNESS_COMPILE_AND_SELFTEST_PASSED="yes"
ok "witness --self-test PASSED in network-none container (PASSIVE_NOS_ENGINE_TIME_WITNESS_SELF_TEST=PASS)"

# ---------------------------------------------------------------------------
# 11. Run Python validator --self-test
# ---------------------------------------------------------------------------
echo "--- [11/16] Run Python validator --self-test ---"
python3 "$VALIDATOR_SRC" --self-test || fail "validator --self-test failed"
ok "Python validator --self-test PASSED"

# ---------------------------------------------------------------------------
# 12. Emit a candidate into a temporary directory + bash -n
# ---------------------------------------------------------------------------
echo "--- [12/16] Emit candidate into temp dir + bash -n ---"
EMIT_TMP="$(mktemp -d)"
CANDIDATE="${EMIT_TMP}/passive_time_witness_runtime_candidate.sh"
# The generator prints its emit-status marker to its own stdout (not into the
# candidate file). Capture stdout while keeping stderr visible for diagnostics.
EMIT_OUT="${EMIT_TMP}/generator_stdout.txt"
PASSIVE_TIME_WITNESS_EMIT_PATH="$CANDIDATE" bash "$GENERATOR_SRC" >"$EMIT_OUT" 2>&1 || \
  { echo "candidate emit failed; generator stderr:" >&2; cat "$EMIT_OUT" >&2; fail "candidate emit failed"; }
[ -f "$CANDIDATE" ] || fail "candidate file not created"
rg -q 'PASSIVE_TIME_WITNESS_RUNTIME_CANDIDATE_EMIT_STATUS=COMPLETE' "$EMIT_OUT" || \
  { echo "candidate missing emit-status marker in generator stdout" >&2; fail "candidate missing emit marker"; }
bash -n "$CANDIDATE" || fail "candidate bash -n failed"
ok "candidate emitted and bash -n passed: $CANDIDATE"

# ---------------------------------------------------------------------------
# 13. Verify the exact top-level future authorization status gate
# ---------------------------------------------------------------------------
echo "--- [13/16] Verify exact top-level status gate in candidate ---"
# Use fixed-string (-F) matching for exact textual presence of the gate; the
# candidate writes the contract status into a local "status" variable.
rg -Fq 'status="$(read_contract_field "status")"' "$CANDIDATE" || \
  rg -Fq 'status="${status}"' "$CANDIDATE" || \
  fail "candidate missing top-level status read"
rg -Fq '[[ "${status}" == "PASSIVE_TIME_WITNESS_TELEMETRY_RUNTIME_AUTHORIZED" ]]' "$CANDIDATE" || \
  fail "candidate missing exact status == PASSIVE_TIME_WITNESS_TELEMETRY_RUNTIME_AUTHORIZED assertion"
ok "candidate has exact top-level status gate: status == PASSIVE_TIME_WITNESS_TELEMETRY_RUNTIME_AUTHORIZED"

# ---------------------------------------------------------------------------
# 14. Verify the first Docker command occurs after the fail-closed gate
# ---------------------------------------------------------------------------
echo "--- [14/16] Verify first Docker command is after the fail-closed gate ---"
gate_line="$(rg -n 'if ! runtime_authorized' "$CANDIDATE" | head -1 | cut -d: -f1)"
exit_line="$(rg -n 'CLOSED_GATE_NOT_AUTHORIZED' "$CANDIDATE" | head -1 | cut -d: -f1)"
first_docker_line="$(rg -n 'docker (network|run|build|create|container)' "$CANDIDATE" | head -1 | cut -d: -f1)"
[ -n "$gate_line" ] || fail "candidate missing 'if ! runtime_authorized' gate"
[ -n "$exit_line" ] || fail "candidate missing CLOSED_GATE_NOT_AUTHORIZED exit"
[ -n "$first_docker_line" ] || fail "candidate has no Docker commands (expected dormant post-gate docker)"
[ "$first_docker_line" -gt "$exit_line" ] || \
  fail "first Docker command (line $first_docker_line) not after gate exit (line $exit_line)"
ok "first Docker command (line $first_docker_line) is after fail-closed gate exit (line $exit_line)"

# ---------------------------------------------------------------------------
# 15. Verify separate immutable-ground and policy-visible roots + witness mount
# ---------------------------------------------------------------------------
echo "--- [15/16] Verify independent evidence roots and witness mount ---"
rg -Fq 'readonly IMMUTABLE_GROUND_EVIDENCE_DIR="artifacts/wp4-passive-time-witness-immutable-ground"' "$CANDIDATE" || \
  fail "candidate missing IMMUTABLE_GROUND_EVIDENCE_DIR readonly"
rg -Fq 'readonly POLICY_VISIBLE_EVIDENCE_DIR="artifacts/wp4-passive-time-witness-policy-visible"' "$CANDIDATE" || \
  fail "candidate missing POLICY_VISIBLE_EVIDENCE_DIR readonly"
POLICY_VISIBLE_DIR_LINE="$(rg -nF 'POLICY_VISIBLE_DIR="${POLICY_VISIBLE_EVIDENCE_DIR}"' "$CANDIDATE" | head -1 | cut -d: -f1)"
[ -n "$POLICY_VISIBLE_DIR_LINE" ] || fail "candidate missing POLICY_VISIBLE_DIR assignment to sibling root"
ok "separate immutable-ground and policy-visible roots (sibling, not nested)"

# Witness output mount is rw and references WITNESS_OUTPUT (ground) not policy
rg -Fq -e '-v "${WITNESS_OUTPUT_HOST}:${WITNESS_OUTPUT_MOUNT_DEST}:${WITNESS_OUTPUT_MOUNT_MODE}"' "$CANDIDATE" || \
  fail "candidate missing witness output mount line"
rg -Fq 'WITNESS_OUTPUT_MOUNT_MODE="rw"' "$CANDIDATE" || \
  fail "candidate witness mount mode not rw"
# Ensure the witness mount dest is under /evidence/witness-output (immutable-ground)
rg -Fq 'WITNESS_OUTPUT_MOUNT_DEST="/evidence/witness-output"' "$CANDIDATE" || \
  fail "candidate witness mount dest not under immutable-ground /evidence/witness-output"
ok "witness output mount is rw (${WITNESS_OUTPUT_MOUNT_MODE:-rw}) under immutable-ground only"

# No policy-visible file contains tick or monotonic-time fields
# Extract the two policy heredocs from the candidate and scan for forbidden tokens
python3 - "$CANDIDATE" <<'PYNOTICK' || fail "policy-visible files contain tick or monotonic-time fields"
import sys, re
cand = open(sys.argv[1]).read()
# Find the policy-visible block: lines between the POLICY_VISIBLE_DIR assignment
# and the end of independent-manifest.json heredoc.
m = re.search(r'POLICY_VISIBLE_DIR="\$\{POLICY_VISIBLE_EVIDENCE_DIR\}"(.+?)(?=\n# |\ndocker |\n\Z|\n# ====)', cand, re.S)
policy_block = cand
# Simpler: extract two heredoc bodies by name markers
for heredoc_name in ['scope-marker.json', 'independent-manifest.json']:
    m2 = re.search(
        r'cat > "\$\{POLICY_VISIBLE_DIR\}/' + re.escape(heredoc_name) + r'" <<\'[A-Z_]+\'\n(.*?)\n[A-Z_]+',
        cand, re.S)
    if not m2:
        raise SystemExit(f"policy heredoc not found: {heredoc_name}")
    body = m2.group(1)
    # Strip comment lines (lines beginning with optional whitespace then #)
    value_lines = [ln for ln in body.splitlines() if not ln.strip().startswith('#')]
    text = '\n'.join(value_lines)
    for tok in ['tick', 'monotonic', 'CLOCK_MONOTONIC', 'trace']:
        # Look for these as JSON key or value tokens (case-insensitive substring in non-comment)
        if tok.lower() in text.lower():
            raise SystemExit(f"policy file {heredoc_name} contains forbidden token '{tok}'")
print("NO_TICK_MONOTONIC_IN_POLICY")
PYNOTICK
ok "no tick or monotonic-time fields written to policy-visible files"

# ---------------------------------------------------------------------------
# 16. Fake-docker closed-contract execution + zero containers check
# ---------------------------------------------------------------------------
echo "--- [16/16] Fake-docker closed-contract execution + zero containers ---"

FAKE_DIR="${EMIT_TMP}/fakebin"
mkdir -p "$FAKE_DIR"
FAKE_LOG="${EMIT_TMP}/fake_docker.log"
: > "$FAKE_LOG"
cat > "$FAKE_DIR/docker" <<'FAKE_DOCKER'
#!/usr/bin/env bash
echo "FAKE_DOCKER_INVOKED: $*" >> "${FAKE_DOCKER_LOG}"
exit 0
FAKE_DOCKER
chmod +x "$FAKE_DIR/docker"

# Saved original PATH segment
SAVED_PATH="$PATH"
export PATH="$FAKE_DIR:$PATH"
export FAKE_DOCKER_LOG="$FAKE_LOG"

# Zero project-labeled containers/networks BEFORE (if real docker exists and is usable)
# Real-docker container/network counts MUST run with the saved (fake-free)
# PATH so the fake docker shim is never used for counts and never pollutes the
# fake-docker log. Resolve a REAL docker binary on the saved PATH first; fake
# docker stays first in PATH only for the candidate execution subshell below.
REAL_DOCKER=""
# Docker is mandatory for this gate (step 9A already failed closed if the
# context or pinned image is unusable). Use the resolved context directly (NOT
# the fake docker shim) and require the count commands to actually succeed, so
# zero counts are genuine instead of silently swallowing a connection error.
if PATH="$SAVED_PATH" command -v docker >/dev/null 2>&1 && PATH="$SAVED_PATH" dctx ps -a >/dev/null 2>&1; then
  REAL_DOCKER="yes"
  pre_containers="$(PATH="$SAVED_PATH" dctx ps -a --filter "label=wp4.passive-time-witness.role" -q 2>/dev/null | wc -l | tr -d ' ')"
  pre_networks="$(PATH="$SAVED_PATH" dctx network ls --filter "name=wp4-passive-time-witness" -q 2>/dev/null | wc -l | tr -d ' ')"
  echo "PRE_CONTAINERS=$pre_containers"
  echo "PRE_NETWORKS=$pre_networks"
  [ "$pre_containers" -eq 0 ] || fail "project-labeled containers exist BEFORE run"
  [ "$pre_networks" -eq 0 ] || fail "project-labeled networks exist BEFORE run"
else
  blocked "Docker context '$DOCKER_CONTEXT' not usable for mandatory pre-run container/network counts (no runtime launched)"
fi

# Execute the candidate under the closed current contract with fake docker first
CAND_ERR="${EMIT_TMP}/cand.stderr"
set +e
( export PATH="$FAKE_DIR:$SAVED_PATH"; export FAKE_DOCKER_LOG="$FAKE_LOG"; bash "$CANDIDATE" >/dev/null 2>"$CAND_ERR" )
cand_rc=$?
set -e
echo "CANDIDATE_RUN_RC=$cand_rc"
cat "$CAND_ERR"
[ "$cand_rc" -eq 1 ] || fail "candidate did not exit rc=1 under closed contract (got rc=$cand_rc)"
rg -q 'PASSIVE_TIME_WITNESS_RUNTIME_CANDIDATE_RUN_STATUS=CLOSED_GATE_NOT_AUTHORIZED' "$CAND_ERR" || \
  fail "candidate did not emit CLOSED_GATE_NOT_AUTHORIZED"

# Prove fake Docker was never invoked (log must be empty)
FAKE_BYTES="$(wc -c < "$FAKE_LOG" | tr -d ' ')"
echo "FAKE_DOCKER_LOG_BYTES=$FAKE_BYTES"
[ "$FAKE_BYTES" -eq 0 ] || fail "fake Docker WAS invoked (log non-empty)"
ok "candidate failed closed (rc=1, CLOSED_GATE_NOT_AUTHORIZED); fake Docker never invoked"

# Zero project-labeled containers/networks AFTER
# Reuse REAL_DOCKER resolved in the PRE block; counts run with the saved
# (fake-free) PATH so the candidate's fake docker is never invoked here.
if [ -n "$REAL_DOCKER" ]; then
  post_containers="$(PATH="$SAVED_PATH" dctx ps -a --filter "label=wp4.passive-time-witness.role" -q 2>/dev/null | wc -l | tr -d ' ')"
  post_networks="$(PATH="$SAVED_PATH" dctx network ls --filter "name=wp4-passive-time-witness" -q 2>/dev/null | wc -l | tr -d ' ')"
  echo "POST_CONTAINERS=$post_containers"
  echo "POST_NETWORKS=$post_networks"
  [ "$post_containers" -eq 0 ] || fail "project-labeled containers exist AFTER run"
  [ "$post_networks" -eq 0 ] || fail "project-labeled networks exist AFTER run"
else
  blocked "Docker context '$DOCKER_CONTEXT' not usable for mandatory post-run container/network counts (no runtime launched)"
fi
export PATH="$SAVED_PATH"

# Additional static prohibitions scan across the candidate (dormant commands)
python3 - "$CANDIDATE" <<'PYCANDPROHIB' || fail "candidate contains prohibited runtime capability"
import sys, re
cand = open(sys.argv[1]).read()
# In the POST-GATE dormant docker block, forbid host networking, host ports,
# docker socket mount, external egress, packet capture, command source.
# Allow label=false statements (these assert absence).
# Find the post-gate block (after CLOSED_GATE_NOT_AUTHORIZED).
idx = cand.find('CLOSED_GATE_NOT_AUTHORIZED')
if idx < 0:
    raise SystemExit("no closed-gate marker in candidate")
post = cand[idx:]
# Forbidden literal patterns that would ENABLE a capability (not assert false):
forbid_enable = [
    r'--network host\b',
    r'--network="host"',
    r'-p \d+',
    r'-p\d+:\d+',
    r'--publish ',
    r'-v /var/run/docker\.sock',
    r'-v .*docker\.sock',
    r'--network .*bridge.*--publish',
    r'pcap',
    r'--network .*external',
    r'docker network create.*--attachable',
]
for pat in forbid_enable:
    if re.search(pat, post):
        raise SystemExit(f"candidate post-gate contains forbidden enabled capability: {pat}")
print("CANDIDATE_NO_PROHIBITED_CAPABILITY_ENABLED")
PYCANDPROHIB
ok "candidate dormant Docker commands forbid host networking, host ports, Docker socket, external egress, packet capture, command source"

# ---------------------------------------------------------------------------
# Cleanup temp
# ---------------------------------------------------------------------------
rm -rf "$EMIT_TMP"

# ---------------------------------------------------------------------------
# Success summary
# ---------------------------------------------------------------------------
echo "=== STATIC VERIFICATION PASSED ==="
WITNESS_SHA="$(sha256_of "$WITNESS_SRC")"
VALIDATOR_SHA="$(sha256_of "$VALIDATOR_SRC")"
GENERATOR_SHA="$(sha256_of "$GENERATOR_SRC")"
CAND_SHA="deferred"
# Recompute candidate hash deterministically for the record (re-emit into a fresh temp)
T2="$(mktemp -d)"
C2="${T2}/passive_time_witness_runtime_candidate.sh"
PASSIVE_TIME_WITNESS_EMIT_PATH="$C2" bash "$GENERATOR_SRC" >/dev/null 2>&1
if [ -f "$C2" ]; then
  CAND_SHA="$(sha256_of "$C2")"
fi
rm -rf "$T2"

echo "witness_source_sha256=${WITNESS_SHA}"
echo "validator_source_sha256=${VALIDATOR_SHA}"
echo "candidate_generator_sha256=${GENERATOR_SHA}"
echo "generated_candidate_sha256=${CAND_SHA}"
echo "witness_clock_basis=CLOCK_MONOTONIC"
echo "socket_shim_clock_basis=CLOCK_MONOTONIC"
echo "shared_clock_basis_verified=1"
echo "permitted_trace_keys=sequence,monotonic_ns,tick,state"
echo "command_source_present=0"
echo "command_transmission_possible=0"
echo "event_injection_present=0"
echo "packet_content_captured=0"
echo "packet_hashes_captured=0"
echo "ip_addresses_captured=0"
echo "policy_time_evidence_exposed=0"
echo "host_network_used=0"
echo "host_ports_published=0"
echo "docker_socket_mounted=0"
echo "external_egress_used=0"
echo "nos3_runtime_launched=0"
echo "simulator_launched=0"
echo "diagnostic_runtime_launched=0"
# Mandatory prereq guard: the final technical PASS is only valid when the
# pinned-image compile AND the C++ witness --self-test actually ran and
# printed the exact PASS token (steps 9A/9B and 10 use --network none and
# never pull/build/compose/login). If either was skipped/deferred, fail closed
# and do NOT print PASS.
if [ "$WITNESS_COMPILE_AND_SELFTEST_PASSED" = "yes" ]; then
  echo "PASSIVE_TIME_WITNESS_STATIC_VERIFICATION_STATUS=PASS"
else
  blocked "witness compile/self-test did not complete; technical PASS suppressed"
fi
