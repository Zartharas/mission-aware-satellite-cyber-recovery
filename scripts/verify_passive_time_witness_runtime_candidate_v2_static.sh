#!/usr/bin/env bash
# ===========================================================================
# WP4 Passive Time-Witness — V2 RUNTIME CANDIDATE STATIC VERIFIER (D-063A)
#
# Fail-closed single static gate for the D-062 v2 runtime-control candidate.
# It binds a PASS to the exact frozen v2 generator/candidate/witness/validator/
# shim identities, validates the complete emitted candidate structure, encodes
# the mandatory network-disabled pinned-image C++ compile + --self-test, runs
# the Python validator --self-test, performs a fake-Docker closed-gate test,
# and requires zero project-labeled Docker resources before and after.
#
# It does NOT authorize runtime, execute the post-gate runtime path, launch
# NOS3/NOS Engine/TimeDriver/generic-radio, transmit commands, inject events,
# modify retained evidence, modify the contract, or change runtime authorization.
# It never pulls/builds/composes/logs in. It prints PASS only after the pinned
# image compile AND C++ --self-test both actually succeeded.
# ===========================================================================
set -Eeuo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONTRACT="${REPO_ROOT}/configs/downlink-diagnostic-contract.json"
GENERATOR_SRC="${REPO_ROOT}/scripts/prepare_passive_time_witness_runtime_candidate_v2.sh"
WITNESS_SRC="${REPO_ROOT}/scripts/passive_nos_engine_time_witness.cpp"
VALIDATOR_SRC="${REPO_ROOT}/scripts/validate_passive_time_witness_trace.py"
SHIM_SRC="${REPO_ROOT}/scripts/radio_socket_metadata_shim.c"
IMPL_RECORD="${REPO_ROOT}/tracker/WP4_PASSIVE_TIME_WITNESS_RUNTIME_CONTROL_V2_IMPLEMENTATION_20260728.md"
IMPL_LOCK="${REPO_ROOT}/artifacts/wp4-passive-time-witness-runtime-control-v2-implementation-lock.txt"

# Frozen identities (D-062).
readonly FROZEN_GENERATOR_SHA256="504069a6fa6889a998c1b98ea5211c78c2a12006f7f6ead0bc4a060175e22a3b"
readonly FROZEN_CANDIDATE_SHA256="b541d22ecd7a94b2acb1f85bb9478453b090ab11e19fb5b667eed1b588a27322"
readonly FROZEN_WITNESS_SHA256="830cd1a3e336c7ed2fe5c6755a30ee24b5bbc04106d3c14f2a9d26995adaaf7e"
readonly FROZEN_VALIDATOR_SHA256="f75131770ab9020c8c2dfb41102121e12ffd664c02a8a2e03bd8aa8c7b8d9027"
readonly FROZEN_SHIM_SHA256="d15ede657230560178b5648ef5d4e15b1965837a1c384790d9cbd3dc8f01ee1b"
readonly FROZEN_HISTORICAL_D060_SHA256="0fe76023ccc968f0aa12fa27db0a5ae21597b03e53066cebb5cf56bc29572259"
readonly REQUIRED_CONTRACT_VERSION="0.4.8"
readonly REQUIRED_CONTRACT_STATUS="PASSIVE_TIME_WITNESS_RUNTIME_CONTROL_V2_IMPLEMENTED_STATIC_GATE_PENDING"
readonly REQUIRED_IMAGE_ID="sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"
PUBLISHED_IMAGE="ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"

# Docker context: honor DOCKER_CONTEXT, otherwise desktop-linux default. All
# real Docker operations go through this selected context only. No
# pull/build/compose/login.
DOCKER_CONTEXT="${DOCKER_CONTEXT:-desktop-linux}"
dctx() { docker --context "$DOCKER_CONTEXT" "$@"; }
readonly STRICT_CXX_CMD="g++ -std=c++14 -Wall -Wextra -Werror -I/usr/include scripts/passive_nos_engine_time_witness.cpp -lnos_engine_client -lnos_engine_common -lnos_engine_transport -lnos_engine_utility -o /tmp/passive_nos_engine_time_witness"

sha256_of() { shasum -a 256 "$1" | awk '{print $1}'; }
fail()    { echo "V2_STATIC_VERIFICATION_FAILED: $*" >&2; exit 1; }
blocked() { echo "V2_STATIC_VERIFICATION_BLOCKED: $*" >&2; exit 1; }
ok()      { echo "V2_STATIC_VERIFICATION_OK: $*"; }
# All Docker resource counts are derived with count_lines, which always
# succeeds (rc 0) even on an empty input file. Under set -Eeuo pipefail a
# bare `grep -c .` on an empty file exits 1 and would terminate the verifier;
# `awk 'END { print NR }'` prints 0 for empty input with rc 0. The result is
# validated as a decimal integer before any numeric comparison.
count_lines() {
  local f="$1"
  local n
  n="$(awk 'END { print NR }' "$f" 2>/dev/null || true)"
  n="${n:-0}"
  case "$n" in
    ''|*[!0-9]*) fail "non-integer line count from $f: \"$n\"" ;;
  esac
  printf '%s' "$n"
}
# Non-Docker local self-check of the count_lines method: proves empty/1/2-line
# files each yield the correct count with an always-successful invocation (rc 0)
# so the verifier cannot be terminated by an empty successful Docker-output file.
__count_selfcheck_dir="$(mktemp -d)"
__count_empty="${__count_selfcheck_dir}/empty.out"
__count_one="${__count_selfcheck_dir}/one.out"
__count_two="${__count_selfcheck_dir}/two.out"
: >"$__count_empty"
printf 'a\n' >"$__count_one"
printf 'a\nb\n' >"$__count_two"
__ce="$(count_lines "$__count_empty")"
__co="$(count_lines "$__count_one")"
__ct="$(count_lines "$__count_two")"
[ "$__ce" -eq 0 ] || fail "count_lines self-check: empty file != 0 ($__ce)"
[ "$__co" -eq 1 ] || fail "count_lines self-check: one-line file != 1 ($__co)"
[ "$__ct" -eq 2 ] || fail "count_lines self-check: two-line file != 2 ($__ct)"
rm -rf "$__count_selfcheck_dir"
unset __count_selfcheck_dir __count_empty __count_one __count_two __ce __co __ct
ok "count_lines self-check (empty=0, one=1, two=2)"

# Only the pinned-image compile AND C++ witness --self-test actually succeeding
# may set this to yes; the final PASS line is suppressed otherwise.
TECHNICAL_SELFTEST_PASSED="no"

# ---------------------------------------------------------------------------
# Verifier temporary workspace + cleanup of verifier-only temps.
# Never removes repository evidence or any Docker resource; no global prune.
# ---------------------------------------------------------------------------
VWORK="$(mktemp -d)"
cleanup() {
  local rc=$?
  trap - EXIT INT TERM HUP
  set +e
  rm -rf "$VWORK"
  exit "$rc"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
trap 'exit 129' HUP

# ---------------------------------------------------------------------------
# 1. Required files exist + contract JSON valid
# ---------------------------------------------------------------------------
echo "--- [1/14] Required files + contract JSON ---"
python3 -m json.tool "$CONTRACT" >/dev/null || fail "contract JSON invalid"
for f in "$GENERATOR_SRC" "$WITNESS_SRC" "$VALIDATOR_SRC" "$SHIM_SRC" "$IMPL_RECORD" "$IMPL_LOCK"; do
  [ -f "$f" ] || fail "missing required file: $f"
done
ok "contract JSON valid; required files present"

# ---------------------------------------------------------------------------
# 2. Fail-closed contract pre-gate validation
# ---------------------------------------------------------------------------
echo "--- [2/14] Fail-closed contract pre-gate validation ---"
python3 - "$CONTRACT" <<'PYGATE' || fail "contract pre-gate state not exactly required"
import json, sys
c = json.load(open(sys.argv[1]))
g = c.get("gate", {})
def want_str(key, exp, src):
    got = src.get(key)
    if not isinstance(got, str) or got != exp:
        raise SystemExit(f"{key} expected str {exp!r} got {got!r}")
def want_bool_false(key, src):
    got = src.get(key)
    # must be an actual Python bool and exactly False. Reject ints/strings that
    # compare equal (e.g. 0 == False) to avoid type slippage.
    if not isinstance(got, bool) or got is not False:
        raise SystemExit(f"{key} expected bool False got {got!r}")
def want_int_zero(key, src):
    got = src.get(key)
    # must be an actual int (NOT a bool), equal to 0. bool is a subclass of int,
    # so explicitly exclude bool here; do not rely on False == 0 equality.
    if not isinstance(got, int) or isinstance(got, bool) or got != 0:
        raise SystemExit(f"{key} expected int 0 (not bool) got {got!r}")
if not isinstance(c.get("contract_version"), str) or c.get("contract_version") != "0.4.8":
    raise SystemExit("contract_version not 0.4.8")
if not isinstance(c.get("status"), str) or c.get("status") != "PASSIVE_TIME_WITNESS_RUNTIME_CONTROL_V2_IMPLEMENTED_STATIC_GATE_PENDING":
    raise SystemExit("status not required pre-gate value")
# historical passive static gate must already be PASS.
want_str("passive_time_witness_static_verification", "PASS", g)
# v2 gate must be PENDING (not PASS yet).
sv2 = g.get("passive_time_witness_runtime_candidate_v2_static_verification")
if not isinstance(sv2, str) or sv2 != "PENDING":
    raise SystemExit(f"v2 static verification expected str PENDING got {sv2!r}")
# v2 accepted hash must be empty string.
av2 = g.get("accepted_runtime_entrypoint_v2_sha256")
if not isinstance(av2, str) or av2 != "":
    raise SystemExit(f"accepted_runtime_entrypoint_v2_sha256 must be empty str got {av2!r}")
# historical accepted hash unchanged, exact 64-hex string.
ah = g.get("accepted_runtime_entrypoint_sha256")
if not isinstance(ah, str) or ah != "0fe76023ccc968f0aa12fa27db0a5ae21597b03e53066cebb5cf56bc29572259":
    raise SystemExit(f"accepted_runtime_entrypoint_sha256 mismatch got {ah!r}")
# runtime unauthorized (actual bool False), attempts exactly int 0 (not bool).
want_bool_false("diagnostic_runtime_authorized", g)
want_int_zero("diagnostic_runtime_attempts_authorized", g)
want_bool_false("baseline_run_1_authorized", g)
want_bool_false("baseline_run_2_authorized", g)
want_bool_false("event_injection_authorized", g)
# top-level gates must be actual bool False.
for k in ("scientific_outcome_allowed","event_injection_allowed",
         "command_transmission_allowed","baseline_execution_allowed",
         "cryptographic_semantics_claim_allowed"):
    want_bool_false(k, c)
print("CONTRACT_PRE_GATE_OK")
PYGATE
ok "contract pre-gate state exactly matches required D-063A inputs"

# ---------------------------------------------------------------------------
# 3. Exact source and artifact binding
# ---------------------------------------------------------------------------
echo "--- [3/14] Exact frozen source/artifact binding ---"
gen_sha="$(sha256_of "$GENERATOR_SRC")"
wit_sha="$(sha256_of "$WITNESS_SRC")"
val_sha="$(sha256_of "$VALIDATOR_SRC")"
shim_sha="$(sha256_of "$SHIM_SRC")"
[ "$gen_sha"  = "$FROZEN_GENERATOR_SHA256" ]  || fail "generator SHA mismatch: $gen_sha"
[ "$wit_sha"  = "$FROZEN_WITNESS_SHA256" ]    || fail "witness SHA mismatch: $wit_sha"
[ "$val_sha"  = "$FROZEN_VALIDATOR_SHA256" ]   || fail "validator SHA mismatch: $val_sha"
[ "$shim_sha" = "$FROZEN_SHIM_SHA256" ]        || fail "shim SHA mismatch: $shim_sha"
ok "generator/witness/validator/shim SHA-256 match frozen identities"

python3 - "$CONTRACT" <<'PYBIND' || fail "contract D-062 binding mismatch"
import json, sys
c = json.load(open(sys.argv[1]))
ctrl = c.get("passive_time_witness_runtime_control_v2", {})
g = c.get("gate", {})
import hashlib
def sha(s):
    return len(s) == 64 and all(ch in "0123456789abcdef" for ch in s)
if ctrl.get("generator") != "scripts/prepare_passive_time_witness_runtime_candidate_v2.sh":
    raise SystemExit("contract generator path mismatch")
if ctrl.get("generator_sha256") != "504069a6fa6889a998c1b98ea5211c78c2a12006f7f6ead0bc4a060175e22a3b":
    raise SystemExit("contract generator_sha256 mismatch")
if ctrl.get("generated_candidate_sha256") != "b541d22ecd7a94b2acb1f85bb9478453b090ab11e19fb5b667eed1b588a27322":
    raise SystemExit("contract generated_candidate_sha256 mismatch")
dur = ctrl.get("observation_duration_seconds")
if not isinstance(dur, int) or dur != 70:
    raise SystemExit(f"observation duration not integer 70: {dur!r}")
if ctrl.get("observation_duration_operator_override_allowed") is not False:
    raise SystemExit("operator override must be false")
print("CONTRACT_D062_BINDING_OK")
PYBIND
ok "contract D-062 generator/candidate/duration binding matches frozen values"

# ---------------------------------------------------------------------------
# 4. Syntax + deterministic double emission
# ---------------------------------------------------------------------------
echo "--- [4/14] Syntax + deterministic double emission ---"
bash -n "$0"            || fail "verifier bash -n failed"
bash -n "$GENERATOR_SRC" || fail "generator bash -n failed"
# Python syntax validation without writing pyc into the repository.
PYC_CACHE="${VWORK}/pyc"
mkdir -p "$PYC_CACHE"
PYTHONPYCACHEPREFIX="$PYC_CACHE" python3 -m py_compile "$VALIDATOR_SRC" || fail "validator py_compile failed"
ok "syntax valid (verifier, generator, validator)"

E1="${VWORK}/emit1"; mkdir -p "$E1"; C1="${E1}/cand_v2.sh"
E2="${VWORK}/emit2"; mkdir -p "$E2"; C2="${E2}/cand_v2.sh"
o1="${VWORK}/g1.out"; o2="${VWORK}/g2.out"
PASSIVE_TIME_WITNESS_V2_EMIT_PATH="$C1" bash "$GENERATOR_SRC" >"$o1" 2>&1 || { cat "$o1" >&2; fail "first emission failed"; }
PASSIVE_TIME_WITNESS_V2_EMIT_PATH="$C2" bash "$GENERATOR_SRC" >"$o2" 2>&1 || { cat "$o2" >&2; fail "second emission failed"; }
grep -Fx 'PASSIVE_TIME_WITNESS_V2_RUNTIME_CANDIDATE_EMIT_STATUS=COMPLETE' "$o1" >/dev/null || fail "first emission missing exact full-line COMPLETE marker"
grep -Fx 'PASSIVE_TIME_WITNESS_V2_RUNTIME_CANDIDATE_EMIT_STATUS=COMPLETE' "$o2" >/dev/null || fail "second emission missing exact full-line COMPLETE marker"
[ -f "$C1" ] && [ -f "$C2" ] || fail "candidate files not created"
bash -n "$C1" || fail "candidate1 bash -n failed"
bash -n "$C2" || fail "candidate2 bash -n failed"
cmp -s "$C1" "$C2" || fail "double emission not byte-identical"
H1="$(sha256_of "$C1")"; H2="$(sha256_of "$C2")"
[ "$H1" = "$FROZEN_CANDIDATE_SHA256" ] || fail "candidate1 SHA mismatch: $H1"
[ "$H2" = "$FROZEN_CANDIDATE_SHA256" ] || fail "candidate2 SHA mismatch: $H2"
CANDIDATE="$C1"
ok "double emission byte-identical; both candidate SHA match frozen b541d22e..."

# ---------------------------------------------------------------------------
# 5. Candidate structural validation
# ---------------------------------------------------------------------------
echo "--- [5/14] Candidate structural validation ---"
python3 - "$CANDIDATE" <<'PYSTRUCT' || fail "candidate structural validation failed"
import re, sys
src = open(sys.argv[1]).read()
lines = src.splitlines()
# 70-second hard-lock.
if not re.search(r'(?m)^readonly OBSERVATION_DURATION_SECONDS=70\b', src):
    raise SystemExit("OBSERVATION_DURATION_SECONDS not hard-locked to 70")
# No operator/env duration override knob.
if re.search(r'(?i)observation_duration_override|OBSERVATION_DURATION_OVERRIDE', src):
    raise SystemExit("operator duration override knob present")
# Complete fail-closed self-hash gate precedes every Docker invocation. A Docker
# *invocation* is a top-level (column-0) executed command line that runs docker;
# lines inside function bodies (capture/cleanup/start definitions) are
# definitions, not invocations, and the availability `for command in docker ...`
# loop is not a docker call either. The first real invocation is the `docker info`
# preflight.
docker_invoke_lines = []
for i, l in enumerate(lines, 1):
    if l[:1].isspace():                       # indented -> inside a function/branch
        continue
    if re.search(r'^for command in .*\bdocker\b', l):  # availability loop, not a call
        continue
    if re.search(r'\bdocker\s+info\b|"\$DOCKER_BIN"\s+(run|stop|rm|network|ps|inspect|image|exec|logs|port)|\bdocker\s+run\b|\bdocker\s+network\s+create\b', l):
        docker_invoke_lines.append(i)
if not docker_invoke_lines:
    raise SystemExit("no top-level Docker invocations found (expected dormant post-gate docker)")
first_docker = docker_invoke_lines[0]
# The fail-closed gate is the PYGATE heredoc; its marker success line follows.
gate_ok_line = src.find('PASSIVE_TIME_WITNESS_V2_RUNTIME_CANDIDATE_GATE=AUTHORIZED')
if gate_ok_line < 0:
    raise SystemExit("missing gate AUTHORIZED marker")
pygate_idx = src.find("<<'PYGATE'")
if pygate_idx < 0:
    raise SystemExit("missing PYGATE fail-closed gate block")
pygate_line = src[:pygate_idx].count("\n")+1
gate_ok_lineno = src[:gate_ok_line].count("\n")+1
if first_docker <= gate_ok_lineno:
    raise SystemExit(f"first Docker (line {first_docker}) not after gate (line {gate_ok_lineno})")
# The gate block must validate authorization-count, v2-static-PASS, governed
# duration, proposed-attempt-count, and the candidate self-hash.
gate_block = src[pygate_idx:src.find("\nPYGATE\n", pygate_idx+10)+len("\nPYGATE")]
for tok in ['diagnostic_runtime_attempts_authorized', 'passive_time_witness_runtime_candidate_v2_static_verification',
            'observation_duration_seconds', 'proposed_runtime_attempts', 'accepted_runtime_entrypoint_v2_sha256']:
    if tok not in gate_block:
        raise SystemExit(f"gate block missing required check: {tok}")
if "hashlib.sha256(candidate_path.read_bytes())" not in gate_block or "!= accepted" not in src:
    raise SystemExit("gate missing candidate self-hash comparison")
# cleanup defined before first Docker invocation.
cleanup_def = src.find('\ncleanup() {')
if cleanup_def < 0:
    raise SystemExit("cleanup() not defined")
cleanup_line = src[:cleanup_def].count("\n")+1
if first_docker <= cleanup_line:
    raise SystemExit(f"cleanup (line {cleanup_line}) not before first Docker (line {first_docker})")
# traps EXIT/INT/TERM/HUP precede first Docker invocation.
tEXIT = re.search(r'(?m)^trap cleanup EXIT\b', src)
tINT  = re.search(r'(?m)^trap .exit 130. INT\b', src)
tTERM = re.search(r'(?m)^trap .exit 143. TERM\b', src)
tHUP  = re.search(r'(?m)^trap .exit 129. HUP\b', src)
if not (tEXIT and tINT and tTERM and tHUP):
    raise SystemExit("missing one of EXIT/INT/TERM/HUP traps")
trap_line = tEXIT.start()
trap_lineno = src[:trap_line].count("\n")+1
if first_docker <= trap_lineno:
    raise SystemExit(f"traps (line {trap_lineno}) not before first Docker (line {first_docker})")
# reverse creation order teardown.
if not re.search(r'(?m)for \(\(index=\$\{#CREATED_CONTAINERS\[@\]\}-1', src):
    raise SystemExit("cleanup not reverse-creation-order over CREATED_CONTAINERS")
if not re.search(r'docker stop Docker|"\$DOCKER_BIN" stop', src) or '"$DOCKER_BIN" stop' not in src:
    if '"$DOCKER_BIN" stop' not in src:
        raise SystemExit("cleanup missing docker stop")
if '"$DOCKER_BIN" rm -f' not in src:
    raise SystemExit("cleanup missing docker rm -f")
# Python subprocess timeouts on cleanup Docker ops.
if "subprocess.run(command, timeout=timeout)" not in src:
    raise SystemExit("bounded_exec missing subprocess.run timeout")
# only exact same-run labeled network removal; verify three-label check.
if 'research.project=$PROJECT' not in src or 'research.phase=$PHASE' not in src or 'research.run_id=$RUN_ID' not in src:
    raise SystemExit("network removal missing same-run label checks")
if '"$DOCKER_BIN" network rm "$NETWORK"' not in src:
    raise SystemExit("network rm of exact same-run network missing")
# no global/project-wide prune.
if re.search(r'(?i)docker\s+prune|system\s+prune|container\s+prune|network\s+prune|image\s+prune|volume\s+prune', src):
    raise SystemExit("docker prune present")
# retries exactly 10, interval exactly 1.
if not re.search(r'(?m)^readonly POST_CLEANUP_ASSERT_RETRIES=10\b', src):
    raise SystemExit("POST_CLEANUP_ASSERT_RETRIES not 10")
if not re.search(r'(?m)^readonly POST_CLEANUP_RETRY_INTERVAL_SECONDS=1\b', src):
    raise SystemExit("POST_CLEANUP_RETRY_INTERVAL_SECONDS not 1")
# cleanup failure overrides nominal success as invalid infrastructure evidence.
if "PASSIVE_TIME_WITNESS_RUNTIME_INVALID" not in src:
    raise SystemExit("cleanup failure classification to INVALID missing")
if "cleanup_failed=1" not in src:
    raise SystemExit("cleanup_failed flag missing")
# fresh evidence-root collision rejected.
if re.search(r'\[\[ -e "\$EVIDENCE" \]\]', src) and 'Fresh evidence root already exists' in src:
    pass
else:
    if 'Fresh evidence root already exists' not in src and '-e "$EVIDENCE"' not in src:
        raise SystemExit("fresh evidence-root collision guard missing")
# immutable-ground and policy-visible sibling roots.
if 'GROUND="$EVIDENCE/immutable-ground"' not in src or 'POLICY="$EVIDENCE/policy-visible"' not in src:
    raise SystemExit("immutable-ground/policy-visible sibling roots missing")
# independent manifests.
if 'hash_tree(' not in src:
    raise SystemExit("independent manifest hash_tree missing")
# policy-visible content contains no tick, monotonic timestamp, UDP timing
# relationship, or derived timing relationship. The scope.json declares fields
# named *_timing_data_included etc. set to false (these are declarations of
# ABSENCE, not data). Parse it and require every truth/command/scientific/
# timing/derived field is false, and require no numeric timestamp, tick count,
# or monotonic_ns VALUE anywhere in policy-visible content.
policy_scope = re.search(r'cat > "\$POLICY/scope\.json" <<\'EOF\'\n(.*?)\nEOF', src, re.S)
if not policy_scope:
    # also try the unescaped dollar form seen in the emitted candidate
    policy_scope = re.search(r"cat > \"\\$POLICY/scope\\.json\" <<'EOF'\n(.*?)\nEOF", src, re.S)
if not policy_scope:
    raise SystemExit("policy-visible scope.json heredoc missing")
pscope = policy_scope.group(1)
import json as _json
try:
    psobj = _json.loads(pscope)
except Exception as e:
    raise SystemExit(f"policy-visible scope.json not valid JSON: {e}")
absence_keys = [
    "truth_data_included", "command_data_included", "scientific_outcome_included",
    "authoritative_time_data_included", "socket_timing_data_included",
    "derived_timing_data_included",
]
for k in absence_keys:
    if k not in psobj:
        raise SystemExit(f"policy-visible scope missing key {k}")
    if psobj.get(k) is not False:
        raise SystemExit(f"policy-visible scope {k} not false: {psobj.get(k)!r}")
# No literal timing VALUES anywhere in policy-visible content.
if re.search(r'monotonic_ns\s*[:=]\s*\d', pscope):
    raise SystemExit("policy-visible scope contains monotonic_ns value")
if re.search(r'(?m)(^|[,{}])\s*"tick"\s*:\s*\d', pscope):
    raise SystemExit("policy-visible scope contains tick value")
if re.search(r'(?i)udp[_ ]?(?:5011|5013|8011)\b.*\d{6,}', pscope):
    raise SystemExit("policy-visible scope contains UDP timing value")
print("CANDIDATE_STRUCTURE_OK")
PYSTRUCT
ok "candidate structure validated (70s lock, gate-before-docker, cleanup/trap ordering, no prune, 10x retries, sibling roots, no policy timing)"

# ---------------------------------------------------------------------------
# 6. Topology + containment + interpretation validation
# ---------------------------------------------------------------------------
echo "--- [6/14] Topology + containment + claim validation ---"
python3 - "$CANDIDATE" <<'PYTOPO' || fail "topology/containment/claim validation failed"
import re, sys
src = open(sys.argv[1]).read()
# Actual v3 topology components.
topo = {
    "active-gs UDP 5013 proxy": '--bind-port 5013' in src and '--mode proxy' in src,
    "radio-sim UDP 5011 forward": '--forward-port 5011' in src,
    "UDP 8011 sink": '--bind-port 8011' in src and '--mode sink' in src,
    "NOS Engine": 'nos-engine-server' in src or 'nos_engine_server_standalone' in src,
    "TimeDriver": 'nos-time-driver' in src,
    "42": 'fortytwo' in src and '"$IMAGE" ./42' in src,
    "truth sink": 'truth-sink' in src and 'TRUTH_SINK_CONNECTED' in src,
    "command-bus bridge": 'nos-sim-bridge' in src or 'nos3-sim-cmdbus-bridge' in src,
    "cFS": 'nos-fsw' in src or 'core-cpu1' in src,
    "generic-radio socket metadata shim": 'LD_PRELOAD=/tmp/libradio_socket_metadata_shim.so' in src,
    "exactly one passive time witness": src.count('start passive-time-witness') == 1,
}
for k,v in topo.items():
    if not v:
        raise SystemExit(f"topology component missing/incorrect: {k}")
# fourteen hardware simulators.
sims = ['generic-css-sim','generic-eps-sim','generic-fss-sim','gps','generic-imu-sim',
        'generic-mag-sim','generic-reactionwheel-sim0','generic-reactionwheel-sim1',
        'generic-reactionwheel-sim2','generic-radio-sim','sample-sim',
        'generic-star-tracker-sim','generic-thruster-sim','generic-torquer-sim']
missing = [s for s in sims if s not in src]
if missing:
    raise SystemExit(f"hardware simulator(s) missing: {missing}")
# no sleep-infinity placeholder topology.
if re.search(r'(?m)sleep\s+inf(inity)?\b', src):
    raise SystemExit("placeholder sleep-infinity topology present")
# Containment: reject ENABLED command forms. A capability is "enabled" only
# when a real docker run/create network create or in-container command carries
# the prohibited FLAG or WRITE. References inside defensive guards (grep -q ...,
# if ...-then-error, echo "[ERROR] ...", comments, explicit *_allowed=false /
# disabled / 0 records) are rejection logic and must NOT be reported as
# enablement. Logical shell commands are parsed by joining backslash-continued
# lines first so flags split across continuations are seen whole.
def join_continuations(text):
    out=[]
    for line in text.splitlines():
        if out and out[-1].endswith('\\'):
            out[-1]=out[-1][:-1]+line
        else:
            out.append(line)
    return out
jlines = join_continuations(src)
LOGIC = "\n".join(jlines)

def is_guard_logical(l):
    # A logical line is a DEFENSIVE GUARD (rejection logic, not enablement) only
    # if it is a comment, a grep/[[ -test inspection, an if/elif branch, an
    # error/info report, or an explicit false/zero/disabled declaration RECORD.
    # Bare '=' is intentionally NOT a guard signal: legitimate run lines carry
    # --label "research.project=$PROJECT" and --env KEY=VAL which contain '='.
    signals = ('grep -q', 'grep "', "grep -E", "grep -F", 'if [[ ', 'if ! ', 'if bounded_exec',
               'elif ', 'echo "[ERROR]', 'echo "[INFO]', '#', 'is False', '== false',
               '_allowed=false', '_allowed=0', 'disabled', 'record ', 'no host', 'not expose',
               'not allowed', 'ensure no', 'forbid', 'reject', 'must not', '__in',
               'is not False', '!= True', '!= 1')
    return any(sig in l for sig in signals)

def logical_line_index(jlines, char_off):
    # map a char offset in LOGIC back to its logical-line index
    pre = LOGIC[:char_off]
    pre = pre.replace("\n", "\n")
    # find which logical line by counting newlines up to char_off
    return pre.count("\n"+"")

def enabled_on_logical(flagpat):
    for m in re.finditer(flagpat, LOGIC):
        prev = LOGIC.rfind("\n", 0, m.start())
        line = LOGIC[prev+1: LOGIC.find("\n", m.end())]
        if is_guard_logical(line):
            continue
        # only count when this logical line is an actual docker launch/create
        if re.search(r'\$DOCKER_BIN"\s*(run|create)|\bdocker\s+(run|network create|create)|\brun\s+--rm|--name "\$PREFIX', line):
            return True, line
    return False, None

def enabled_anywhere_logical(flagpat):
    for m in re.finditer(flagpat, LOGIC):
        prev = LOGIC.rfind("\n", 0, m.start())
        line = LOGIC[prev+1: LOGIC.find("\n", m.end())]
        if is_guard_logical(line):
            continue
        if re.search(r'inspect.*format|{{.*}}', line):
            continue
        return True, line
    return False, None

# ---- network containment ----
# The candidate's created project network must use --internal.
nc_pat = re.compile(r'\$DOCKER_BIN"\s*network\s+create\b|"?\$DOCKER_BIN"?\s+network\s+create\b|\bdocker\s+network\s+create\b')
net_create_lines = []
for l in jlines:
    if nc_pat.search(l) and not is_guard_logical(l):
        net_create_lines.append(l)
if not net_create_lines:
    raise SystemExit("no project network create found")
for l in net_create_lines:
    if '--internal' not in l:
        raise SystemExit("project network create not --internal")
# reject externally-reachable / attachable / ingress / config-only network creation
bad_net = re.compile(r'--attachable\b|--ingress\b|--config-only\b|--network\s+host\b|--network="host"|--driver\s+(overlay|macvlan|host)')
on, ln = enabled_anywhere_logical(bad_net.pattern)
if on:
    raise SystemExit("externally reachable/attachable/ingress/host network enabled: "+ln.strip()[:120])
# also any non-internal external network flag on a launcher line
if enabled_on_logical(r'--network\s+overlay|--network\s+macvlan|--network\s+host')[0]:
    raise SystemExit("external network driver enabled on container line")

# ---- host networking / host ports / docker.sock (enabled on a docker line) ----
if enabled_on_logical(r'--network\s+host\b|--network="host"')[0]:
    raise SystemExit("host networking enabled on a docker run line")
if enabled_on_logical(r'\s-p\s+\d+|\s-p\d+:\d+|--publish\s+|--publish=')[0]:
    raise SystemExit("host port publication enabled on a docker run line")
if enabled_on_logical(r'-v\s+\S*docker\.sock|--mount[^"]*docker\.sock')[0]:
    raise SystemExit("docker.sock mount enabled on a docker run line")

# ---- packet capture / packet-payload / packet-hash / IP retention (enabled) ----
if enabled_on_logical(r'\bpcap\b|--cap-add\s+(NET_ADMIN|NET_RAW|SYS_PTRACE)')[0]:
    raise SystemExit("packet capture enabled on a docker run line")
# Enabled packet-payload retention: a write mount whose destination is a packet
# payload/capture path, or a command that writes raw packet bytes. The candidate
# writes only socket METADATA (recvfrom/sendto result fields), never payloads.
# Reject an enabled bind whose target name signals packet payload/capture.
for l in jlines:
    if is_guard_logical(l):
        continue
    for mm in re.finditer(r'--mount "type=bind,[^"]*"', l):
        seg = mm.group(0)
        if re.search(r'target=[^,"]*(packet|payload|pcap|capture)', seg, re.I):
            raise SystemExit("packet-payload retention mount enabled: "+seg[:120])
# Enabled packet-hash retention: reject a command that hashes packet bytes and
# retains the digest (the candidate records only metadata counts, not packet hashes).
for l in jlines:
    if is_guard_logical(l):
        continue
    if re.search(r'(sha|md5|blake|hash)\(?\s*(packet|payload|pkt|frame)', l, re.I):
        raise SystemExit("packet-hash retention enabled: "+l.strip()[:120])
    if re.search(r'record\s+(packet_hash|packet_hashes|payload_hash)\b', l, re.I):
        raise SystemExit("packet-hash retention record enabled: "+l.strip()[:120])
# Enabled IP-address retention: the capture() doc says IP addresses are NOT
# retained. Reject an inspect format/template that retains an IPAddress field,
# and reject a record of an IP value (outside guards/false declarations).
for l in jlines:
    if is_guard_logical(l):
        continue
    if re.search(r'\.IPAddress|NetworkSettings\.IPAddress|"IPAddress"', l):
        raise SystemExit("IP-address retention enabled: "+l.strip()[:120])
    if re.search(r'record\s+\S*ip_address\S*\s+(?!false\b|0\b)', l, re.I):
        raise SystemExit("IP-address retention record enabled: "+l.strip()[:120])

# ---- command sources / command transmission / event injection (enabled) ----
# The candidate is telemetry-only: it must not emit a command source, send a
# command, or inject an event. Reject enabled transmit/inject CALL FORM, not the
# many "disabled"/"0"/"_allowed=false" declarations.
for l in jlines:
    if is_guard_logical(l):
        continue
    # command transmission: an active send/write of a command frame
    if re.search(r'\bsend(command|cmd|telecommand|frame)|transmit(command|cmd)|command_transmission_allowed\s*=\s*true', l, re.I):
        raise SystemExit("command transmission enabled: "+l.strip()[:120])
    # event injection: an active inject/poke into the sim runtime
    if re.search(r'\binject(event|command|message)|event_injection_authorized\s*=\s*true', l, re.I):
        raise SystemExit("event injection enabled: "+l.strip()[:120])
    # command source: a candidate-defined command source emitter
    if re.search(r'\bcommand[_ ]?source\s*=|createCommandSource|command_source_present\s*=\s*true', l, re.I):
        raise SystemExit("command source enabled: "+l.strip()[:120])

# ---- broad / global / project-wide Docker cleanup (enabled) ----
# The candidate removes ONLY its exact same-run resources: it stops/removes the
# containers it created by their exact $name (which embeds the run id prefix), and
# removes only the exact labeled $NETWORK after verifying all three labels. A
# project-wider or global teardown would be: any `docker prune`, a removal scoped
# by research.project/phase WITHOUT research.run_id (would touch other runs), or a
# removal driven by an unfiltered `$(docker ps -aq)` expansion. Per-name and
# per-$NETWORK removals, and any filter that includes research.run_id, are allowed.
for l in jlines:
    if is_guard_logical(l):
        continue
    if re.search(r'\bdocker\s+prune\b|docker\s+system\s+prune|docker\s+container\s+prune|docker\s+network\s+prune|docker\s+image\s+prune|docker\s+volume\s+prune', l, re.I):
        raise SystemExit("global/project-wide Docker prune enabled: "+l.strip()[:120])
    if re.search(r'\$DOCKER_BIN"\s*(rm|stop|network rm|container rm)\b|\bdocker\s+(rm|stop|network rm|container rm)\b', l):
        # A filter that includes research.run_id is same-run-scoped and allowed.
        if re.search(r'research\.run_id', l):
            continue
        # Per-name/per-network teardown targets the exact same-run resource:
        # the name is a tracked $name / $NETWORK. Allow rm/stop of &$name or $NETWORK.
        if re.search(r'rm\s+["\$]?\$\{?name|rm\s+-f\s+["\$]?\$\{?name|stop\s+["\$]?\$\{?name|network rm\s+["\$]?\$\{?NETWORK|rm\s+-f\s+["\$]\$name', l):
            continue
        # A removal scoped ONLY by research.project/phase (without run_id) is
        # project-wide and forbidden; an unfiltered $() expansion is forbidden.
        if re.search(r'research\.project|research\.phase', l) and not re.search(r'research\.run_id', l):
            raise SystemExit("project-wide (non-run-scoped) Docker teardown enabled: "+l.strip()[:120])
        if re.search(r'\$\(\s*\$DOCKER_BIN"\s+ps|\$\(\s*docker\s+ps', l) and not re.search(r'research\.run_id', l):
            raise SystemExit("unfiltered $() Docker teardown enabled: "+l.strip()[:120])

# ---- pinned NOS3 source protection ----
# The pinned NOS3 source tree ($NOS3) is mounted at /work/nos3 inside the NOS3
# launcher containers. The candidate must NOT write into the pinned source. The
# correction requires rejecting every write-capable bind whose source is $NOS3 and
# whose target is /work/nos3 or any descendant: a writable bind is itself a
# prohibited capability, and safety is NEVER inferred from the commands that
# appear to run inside the container. Any such mount MUST declare readonly / ,ro
# explicitly. The candidate must also not perform enabled writes (redirections, cp,
# tee, mkdir, compile -o, etc.) into the pinned source tree, failing closed when a
# write destination under /work/nos3 cannot be classified. Bounded build-output
# locations OUTSIDE /work/nos3 (/out, /evidence-*, etc.) remain permitted.
NOS3_SRC_TARGETS = ("/work/nos3",)
BOUNDED_BUILD_OUTPUT = (
    "/out",                          # shim compile output
    "/evidence/passive-time-witness",  # passive witness trace output
    "/evidence-socket-metadata",       # socket metadata output
)
# known pre-built run locations under /work/nos3 that the candidate only reads.
PREBUILT_RUN_DIRS = (
    "/work/nos3/sims/build/bin",
    "/work/nos3/fsw/build/exe/cpu1",
)
def under(path, base):
    return path == base or path.startswith(base.rstrip("/") + "/")
def classify_write_target(dst):
    # 'source'   = destination is inside the pinned source tree AND not a known
    #              prebuilt read-only run location (=> a write into pinned source).
    # 'ok'       = destination is a bounded build-output / evidence location, or
    #              outside the pinned source tree entirely.
    # 'prebuilt'  = destination is a known pre-built run location (read-only at
    #              runtime in this candidate).
    # 'unclass'   = destination is empty/malformed and cannot be classified.
    d = dst.strip().strip('"').strip("'")
    if not d:
        return "unclass"
    for b in ("/out", "/evidence/passive-time-witness", "/evidence-socket-metadata"):
        if d == b or d.startswith(b.rstrip("/") + "/"):
            return "ok"
    if not any(under(d, b) for b in NOS3_SRC_TARGETS):
        return "ok"
    # destination is inside the pinned source tree (root /work/nos3 OR any
    # descendant). A write-capable bind of the whole tree is itself a
    # prohibited capability: do NOT infer safety from the commands that run
    # inside the container. Only a known prebuilt read-only run location is
    # classified "prebuilt"; everything else under /work/nos3 (including the
    # exact tree root) is "source" and must be mounted readonly.
    for pr in PREBUILT_RUN_DIRS:
        if d == pr or under(d, pr):
            return "prebuilt"
    return "source"

# 1) Reject every candidate mount whose target is inside the pinned NOS3 source
#    tree (/work/nos3 or any descendant) unless the mount is EXPLICITLY read-only.
#    A write-capable bind of the whole tree is itself a prohibited capability;
#    safety is NOT inferred from the commands that appear to execute inside the
#    container. The candidate must declare readonly / ,ro on any such mount.
#    (Known prebuilt read-only run locations are classified "prebuilt" and are
#    still required to be mounted readonly here if the bind is write-capable,
#    because a writable bind of pinned source is never permitted.)
for l in jlines:
    if is_guard_logical(l):
        continue
    # accept either --mount "type=bind," or -v style lines for NOS3 source binds
    for mm in re.finditer(r'--mount "type=bind,[^"]*"|-v\s+\S*:?/work/nos3[:;]', l):
        seg = mm.group(0)
        # extract source and target of the bind
        msrc = re.search(r'source=([^,";]+)', seg) or re.search(r'-v\s+([^,]+)', seg)
        mto = re.search(r'target=([^,";]+)', seg) or re.search(r'-v\s+[^,]+:(/work/nos3[^;]*)', seg)
        if not (msrc and mto):
            continue
        src = msrc.group(1)
        dst = mto.group(1).strip('"').strip("'")
        cls = classify_write_target(dst)
        if cls not in ("source", "prebuilt"):
            # outside pinned source tree or a bounded ok location: not NOS3-source
            continue
        # Only enforce when the bind source is the pinned NOS3 source ($NOS3).
        if not re.search(r'\$NOS3\b|"\$NOS3"', src):
            continue
        cap_write = ('readonly' not in seg) and (re.search(r'\bro\b|,ro\b', seg) is None)
        if cap_write:
            raise SystemExit(
                "write-capable mount of pinned NOS3 source (source=$NOS3 -> "
                + dst + ") is prohibited; must be explicitly read-only: " + seg[:120])

# 2) Reject any ENABLED command WRITE whose destination lands inside the pinned
#    source tree outside a known prebuilt read-only run location. This catches
#    the real mutation vector: redirections, cp, tee, mkdir, cat >, and compile
#    -o into /work/nos3/<...>. The candidate's only compile writes /out (bounded),
#    and every other write goes to /evidence-* (bounded). A destination under
#    /work/nos3 that is not a prebuilt run dir fails closed.
write_op = re.compile(
    r'(>>?|tee|cp|mv|mkdir|cat\s*>|cc|g\+\+|make|cmake|install)\b[^\n]*?(/work/nos3[^\s"\';,|]*)',
    re.I)
for l in jlines:
    if is_guard_logical(l):
        continue
    for w in write_op.finditer(l):
        dst = w.group(2)
        cls = classify_write_target(dst)
        if cls == "source":
            raise SystemExit("write into pinned NOS3 source tree: "+l.strip()[:120])
        if cls == "unclass":
            raise SystemExit("unclassifiable write destination under /work/nos3: "+l.strip()[:120])

# 3) Compile/build outputs must land in bounded build-output locations outside the
#    pinned source. The candidate's only in-container compile writes /out; reject
#    a compile whose -o lands in /work/nos3 (which nothing classifies as bounded).
for l in jlines:
    if is_guard_logical(l):
        continue
    m = re.search(r'\bcc\b|\bg\+\+\b', l)
    if m and '-o' in l:
        # find the -o target argument
        om = re.search(r'-o\s+(\S+)', l)
        if om:
            cls = classify_write_target(om.group(1).strip('"').strip("'"))
            if cls in ("source", "unclass"):
                raise SystemExit("pinned-source-targeted compile output: "+l.strip()[:120])

# ---- affirmative forbidden-claim claims (guards allowed) ----
affirmative_claims = [
    r'callback\s+invocation\s+(proven|established|confirmed|demonstrated)',
    r'queue\s+visibility\s+(proven|established|confirmed)',
    r'due.?time\s+evaluation\s+(proven|established|confirmed)',
    r'(generic-radio\s+)?source\s+defect\s+(proven|established|confirmed)',
    r'mission\s+impact\s+(proven|established|confirmed)',
    r'scientific\s+outcome\s+(proven|established|confirmed|demonstrated)',
    r'CryptoLib\s+behavior\s+(proven|established|confirmed)',
    r'SDLS\s+behavior\s+(proven|established|confirmed)',
]
for pat in affirmative_claims:
    for m in re.finditer(pat, LOGIC, re.I):
        prev = LOGIC.rfind("\n", 0, m.start())
        line = LOGIC[prev+1: LOGIC.find("\n", m.end())]
        if is_guard_logical(line):
            continue
        raise SystemExit(f"affirmative forbidden claim present: {pat}")
print("TOPOLOGY_CONTAINMENT_OK")
PYTOPO
ok "topology (v3), containment, and non-claim validation passed"

# ---------------------------------------------------------------------------
# 7. Witness clock/API + validator schema quick static checks (network-disabled)
# ---------------------------------------------------------------------------
echo "--- [7/14] Witness/validator source static checks ---"
rg -q 'using NosEngine::Client::Bus' "$WITNESS_SRC" || fail "witness missing NosEngine::Client::Bus"
rg -q 'add_time_tick_callback' "$WITNESS_SRC" || fail "witness missing add_time_tick_callback"
rg -q 'clock_gettime\(CLOCK_MONOTONIC' "$WITNESS_SRC" || fail "witness missing CLOCK_MONOTONIC"
rg -q 'clock_gettime\(CLOCK_MONOTONIC' "$SHIM_SRC" || fail "shim missing CLOCK_MONOTONIC"
ok "witness/shim clock basis + NOS Engine Bus API present"

# ---------------------------------------------------------------------------
# 8. Genuine pre-run resource-state checks (real Docker, selected context)
# ---------------------------------------------------------------------------
echo "--- [8/14] Pre-run project-labeled Docker resource counts (real Docker) ---"
if ! command -v docker >/dev/null 2>&1; then
  blocked "docker CLI not found; cannot run mandatory pinned-image static checks"
fi
if ! dctx info --format 'server={{.ServerVersion}}' >/dev/null 2>&1; then
  blocked "Docker context '$DOCKER_CONTEXT' server unreachable; mandatory static checks blocked"
fi
PROJECT_LABEL="mission-aware-satellite-cyber-recovery"
# Capture each Docker command result FIRST; on failure call blocked with a clear
# message; derive counts ONLY from successfully captured output (never treat a
# Docker error as zero).
PRE_CONTAINERS_OUT="${VWORK}/pre_containers.out"
PRE_NETWORKS_OUT="${VWORK}/pre_networks.out"
set +e
dctx ps -a --filter "label=research.project=${PROJECT_LABEL}" -q >"$PRE_CONTAINERS_OUT" 2>"${VWORK}/pre_containers.err"
pre_cnt_rc=$?
dctx network ls --filter "label=research.project=${PROJECT_LABEL}" -q >"$PRE_NETWORKS_OUT" 2>"${VWORK}/pre_networks.err"
pre_net_rc=$?
set -e
if [ "$pre_cnt_rc" -ne 0 ]; then
  cat "${VWORK}/pre_containers.err" >&2
  blocked "pre-run container count failed (Docker rc=${pre_cnt_rc}); cannot verify zero state"
fi
if [ "$pre_net_rc" -ne 0 ]; then
  cat "${VWORK}/pre_networks.err" >&2
  blocked "pre-run network count failed (Docker rc=${pre_net_rc}); cannot verify zero state"
fi
pre_containers="$(count_lines "$PRE_CONTAINERS_OUT")"
pre_networks="$(count_lines "$PRE_NETWORKS_OUT")"
case "$pre_containers" in ''|*[!0-9]*) fail "pre_containers not decimal integer: \"$pre_containers\"" ;; esac
case "$pre_networks"  in ''|*[!0-9]*) fail "pre_networks not decimal integer: \"$pre_networks\"" ;; esac
[ "$pre_containers" -eq 0 ] || fail "pre-run project-labeled containers not zero: $pre_containers"
[ "$pre_networks"  -eq 0 ] || fail "pre-run project-labeled networks not zero: $pre_networks"
echo "pre_project_containers=${pre_containers}"
echo "pre_project_networks=${pre_networks}"
ok "zero project-labeled containers/networks before static checks"

# ---------------------------------------------------------------------------
# 9. Exact pinned image present locally + image ID match (no pull)
# ---------------------------------------------------------------------------
echo "--- [9/14] Pinned image local presence + exact image ID ---"
if ! dctx image inspect "$PUBLISHED_IMAGE" >/dev/null 2>&1; then
  blocked "exact pinned image not present locally (pulling forbidden): $PUBLISHED_IMAGE"
fi
IMAGE_ID="$(dctx image inspect "$PUBLISHED_IMAGE" --format '{{.Id}}' 2>/dev/null)"
[ -n "$IMAGE_ID" ] || blocked "could not resolve pinned image ID"
[ "$IMAGE_ID" = "$REQUIRED_IMAGE_ID" ] || blocked "pinned image ID mismatch: got=$IMAGE_ID want=$REQUIRED_IMAGE_ID"
echo "PINNED_IMAGE_ID=$IMAGE_ID"
ok "exact pinned image present with matching image ID (no pull/build/compose/login)"

# ---------------------------------------------------------------------------
# 10. Mandatory pinned-image C++ compile (--network none) + witness --self-test
# ---------------------------------------------------------------------------
echo "--- [10/14] Pinned-image C++ compile + witness --self-test (network none) ---"
COMPILE_OUT="${VWORK}/compile.out"
dctx run --rm --platform linux/amd64 --network none \
    -v "${REPO_ROOT}/scripts:/work/scripts:ro" -w /work \
    "$PUBLISHED_IMAGE" bash -lc "set -e; $STRICT_CXX_CMD && echo COMPILE_OK" \
    >"$COMPILE_OUT" 2>&1 || { cat "$COMPILE_OUT" >&2; fail "witness compile failed in pinned image (--network none)"; }
# Require the exact full build-output marker line produced by `echo COMPILE_OK`.
grep -Fx 'COMPILE_OK' "$COMPILE_OUT" >/dev/null || fail "witness compile did not produce exact full-line COMPILE_OK"
ok "witness compiled in pinned image (--network none, strict C++14 -Werror)"

SELFTEST_OUT="${VWORK}/selftest.out"
dctx run --rm --platform linux/amd64 --network none \
    -v "${REPO_ROOT}/scripts:/work/scripts:ro" -w /work \
    "$PUBLISHED_IMAGE" bash -lc "set -e; $STRICT_CXX_CMD && /tmp/passive_nos_engine_time_witness --self-test" \
    >"$SELFTEST_OUT" 2>&1 || { cat "$SELFTEST_OUT" >&2; fail "witness --self-test failed in pinned image (--network none)"; }
# Require the exact full output line printed by the compiled C++ witness --self-test.
grep -Fx 'PASSIVE_NOS_ENGINE_TIME_WITNESS_SELF_TEST=PASS' "$SELFTEST_OUT" >/dev/null || \
  fail "witness --self-test did not print exact full line PASSIVE_NOS_ENGINE_TIME_WITNESS_SELF_TEST=PASS"
ok "C++ witness --self-test PASSED in network-none container"

# ---------------------------------------------------------------------------
# 11. Host Python validator --self-test
# ---------------------------------------------------------------------------
echo "--- [11/14] Host Python validator --self-test ---"
# Capture the validator's own stdout/stderr into verifier temporary storage, require
# a successful exit, and require the exact full output line printed BY the validator.
# Do NOT echo a substitute marker on the validator's behalf.
VAL_OUT="${VWORK}/validator_selftest.out"
set +e
python3 "$VALIDATOR_SRC" --self-test >"$VAL_OUT" 2>&1
val_rc=$?
set -e
if [ "$val_rc" -ne 0 ] || ! grep -Fx 'PASSIVE_TIME_WITNESS_TRACE_VALIDATOR_SELF_TEST=PASS' "$VAL_OUT" >/dev/null; then
  cat "$VAL_OUT" >&2
  fail "validator --self-test failed or did not print exact full line PASSIVE_TIME_WITNESS_TRACE_VALIDATOR_SELF_TEST=PASS (rc=${val_rc})"
fi
ok "host validator --self-test printed exact PASS full line"

TECHNICAL_SELFTEST_PASSED="yes"

# ---------------------------------------------------------------------------
# 12. Closed-contract candidate test (fake docker first; only closed-gate path)
# ---------------------------------------------------------------------------
echo "--- [12/14] Closed-contract candidate test (fake docker, closed gate only) ---"
FAKE_DIR="${VWORK}/fakebin"; mkdir -p "$FAKE_DIR"
FAKE_LOG="${VWORK}/fake_docker.log"; : >"$FAKE_LOG"
printf '#!/usr/bin/env bash\necho "FAKE_DOCKER_INVOKED: $*" >> "%s"\nexit 0\n' "$FAKE_LOG" >"$FAKE_DIR/docker"
chmod +x "$FAKE_DIR/docker"
CAND_ERR="${VWORK}/cand_closed.stderr"
SAVED_PATH="$PATH"
# Evidence-root integrity guard: record a deterministic Python tree digest of the
# artifacts/downlink-diagnostics evidence root before/after the closed-gate test to
# prove no evidence directory was created or modified. The digest hashes relative
# path, object type, regular-file bytes, and symlink target; an absent root is
# represented deterministically and symlinks are NOT followed outside the root.
EVIDENCE_ROOT="${REPO_ROOT}/artifacts/downlink-diagnostics"
PRE_TREE="$(python3 - "$EVIDENCE_ROOT" <<'PYDIGEST'
import hashlib, os, sys
root = os.path.abspath(sys.argv[1])
def digest_dir(root):
    entries = []
    for dirpath, dirnames, filenames in os.walk(root, topdown=True, followlinks=False):
        dirnames.sort()
        for d in dirnames:
            full = os.path.join(dirpath, d)
            rel = os.path.relpath(full, root)
            if os.path.islink(full):
                target = os.readlink(full)
                entries.append((rel, "symlink", target.encode()))
            else:
                entries.append((rel, "dir", b""))
        for f in sorted(filenames):
            full = os.path.join(dirpath, f)
            rel = os.path.relpath(full, root)
            if os.path.islink(full):
                entries.append((rel, "symlink", os.readlink(full).encode()))
            elif os.path.isfile(full):
                with open(full, "rb") as fh:
                    entries.append((rel, "file", hashlib.sha256(fh.read()).digest()))
            else:
                entries.append((rel, "other", b""))
    entries.sort(key=lambda e: e[0])
    h = hashlib.sha256()
    for rel, typ, data in entries:
        h.update(rel.encode("utf-8")); h.update(b"\0")
        h.update(typ.encode("utf-8")); h.update(b"\0")
        h.update(data); h.update(b"\n")
    return h.hexdigest()
if not os.path.isdir(root):
    # absent root: deterministic representation
    print(hashlib.sha256(b"ABSENT_ROOT:" + root.encode("utf-8")).hexdigest())
else:
    print(digest_dir(root))
PYDIGEST
)"

# Run ONLY the candidate's current closed-gate path with a fake docker first in
# PATH. Capture rc=1 WITHOUT triggering premature errexit: disable errexit around
# the candidate, restore strict mode immediately after, and use env to set PATH
# for the candidate process only.
CAND_RC_FILE="${VWORK}/cand_rc"
: > "$CAND_RC_FILE"
set +e
env PATH="$FAKE_DIR:$SAVED_PATH" bash "$CANDIDATE" >/dev/null 2>"$CAND_ERR"
echo "$?" > "$CAND_RC_FILE"
set -e
CAND_RC="$(cat "$CAND_RC_FILE" 2>/dev/null || echo unknown)"

# Strict mode is restored above (set -e). Require exact rc=1 and the exact full
# closed-gate stderr marker line produced by the candidate's fail-closed gate.
[ "$CAND_RC" -eq 1 ] || fail "candidate closed-gate rc not 1 (got $CAND_RC)"
grep -Fx 'PASSIVE_TIME_WITNESS_V2_RUNTIME_CANDIDATE_STATUS=CLOSED_GATE_NOT_AUTHORIZED' "$CAND_ERR" >/dev/null || \
  fail "candidate did not emit exact full-line CLOSED_GATE_NOT_AUTHORIZED marker"

# Fake Docker log must remain zero bytes (only the closed-gate path ran).
FAKE_BYTES="$(wc -c < "$FAKE_LOG" | tr -d ' ')"
[ "$FAKE_BYTES" -eq 0 ] || fail "fake Docker WAS invoked (log non-empty): $FAKE_BYTES bytes"

POST_TREE="$(python3 - "$EVIDENCE_ROOT" <<'PYDIGEST'
import hashlib, os, sys
root = os.path.abspath(sys.argv[1])
def digest_dir(root):
    entries = []
    for dirpath, dirnames, filenames in os.walk(root, topdown=True, followlinks=False):
        dirnames.sort()
        for d in dirnames:
            full = os.path.join(dirpath, d)
            rel = os.path.relpath(full, root)
            if os.path.islink(full):
                entries.append((rel, "symlink", os.readlink(full).encode()))
            else:
                entries.append((rel, "dir", b""))
        for f in sorted(filenames):
            full = os.path.join(dirpath, f)
            rel = os.path.relpath(full, root)
            if os.path.islink(full):
                entries.append((rel, "symlink", os.readlink(full).encode()))
            elif os.path.isfile(full):
                with open(full, "rb") as fh:
                    entries.append((rel, "file", hashlib.sha256(fh.read()).digest()))
            else:
                entries.append((rel, "other", b""))
    entries.sort(key=lambda e: e[0])
    h = hashlib.sha256()
    for rel, typ, data in entries:
        h.update(rel.encode("utf-8")); h.update(b"\0")
        h.update(typ.encode("utf-8")); h.update(b"\0")
        h.update(data); h.update(b"\n")
    return h.hexdigest()
if not os.path.isdir(root):
    print(hashlib.sha256(b"ABSENT_ROOT:" + root.encode("utf-8")).hexdigest())
else:
    print(digest_dir(root))
PYDIGEST
)"
[ "$PRE_TREE" = "$POST_TREE" ] || fail "closed-gate test modified evidence directory tree"
ok "candidate failed closed (rc=1, full-line CLOSED_GATE_NOT_AUTHORIZED); fake Docker never invoked; evidence unmodified"

# ---------------------------------------------------------------------------
# 13. Post-run resource-state checks (real Docker)
# ---------------------------------------------------------------------------
echo "--- [13/14] Post-run project-labeled Docker resource counts (real Docker) ---"
# Capture each Docker command result FIRST; on failure blocked; derive counts only
# from successfully captured output (never treat a Docker error as zero).
POST_CONTAINERS_OUT="${VWORK}/post_containers.out"
POST_NETWORKS_OUT="${VWORK}/post_networks.out"
set +e
dctx ps -a --filter "label=research.project=${PROJECT_LABEL}" -q >"$POST_CONTAINERS_OUT" 2>"${VWORK}/post_containers.err"
post_cnt_rc=$?
dctx network ls --filter "label=research.project=${PROJECT_LABEL}" -q >"$POST_NETWORKS_OUT" 2>"${VWORK}/post_networks.err"
post_net_rc=$?
set -e
if [ "$post_cnt_rc" -ne 0 ]; then
  cat "${VWORK}/post_containers.err" >&2
  blocked "post-run container count failed (Docker rc=${post_cnt_rc}); cannot verify zero state"
fi
if [ "$post_net_rc" -ne 0 ]; then
  cat "${VWORK}/post_networks.err" >&2
  blocked "post-run network count failed (Docker rc=${post_net_rc}); cannot verify zero state"
fi
post_containers="$(count_lines "$POST_CONTAINERS_OUT")"
post_networks="$(count_lines "$POST_NETWORKS_OUT")"
case "$post_containers" in ''|*[!0-9]*) fail "post_containers not decimal integer: \"$post_containers\"" ;; esac
case "$post_networks"  in ''|*[!0-9]*) fail "post_networks not decimal integer: \"$post_networks\"" ;; esac
[ "$post_containers" -eq 0 ] || fail "post-run project-labeled containers not zero: $post_containers"
[ "$post_networks"  -eq 0 ] || fail "post-run project-labeled networks not zero: $post_networks"
echo "post_project_containers=${post_containers}"
echo "post_project_networks=${post_networks}"
ok "zero project-labeled containers/networks after static checks"

# ---------------------------------------------------------------------------
# 14. Static-gate result
# ---------------------------------------------------------------------------
echo "--- [14/14] Static-gate result ---"
if [ "$TECHNICAL_SELFTEST_PASSED" != "yes" ]; then
  blocked "pinned-image compile/self-test did not complete; technical PASS suppressed"
fi
echo "PASSIVE_TIME_WITNESS_RUNTIME_CANDIDATE_V2_STATIC_VERIFICATION_STATUS=PASS"
echo "generator_sha256=${FROZEN_GENERATOR_SHA256}"
echo "generated_candidate_sha256=${FROZEN_CANDIDATE_SHA256}"
echo "witness_sha256=${FROZEN_WITNESS_SHA256}"
echo "trace_validator_sha256=${FROZEN_VALIDATOR_SHA256}"
echo "socket_shim_sha256=${FROZEN_SHIM_SHA256}"
echo "observation_duration_seconds=70"
echo "double_emission=IDENTICAL"
echo "candidate_closed_gate_rc=1"
echo "fake_docker_invoked=0"
echo "pre_project_containers=${pre_containers}"
echo "pre_project_networks=${pre_networks}"
echo "post_project_containers=${post_containers}"
echo "post_project_networks=${post_networks}"
echo "docker_network_mode=none"
echo "runtime_candidate_executed=0"
echo "nos3_runtime_launched=0"
echo "diagnostic_runtime_launched=0"
echo "retained_evidence_modified=0"
echo "runtime_authorized=0"
echo "runtime_attempts_authorized=0"
