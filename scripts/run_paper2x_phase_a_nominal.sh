#!/usr/bin/env bash
# P2X Phase A: pinned-host verification and ONE benign cFS SAMPLE NOOP.
# This intentionally does NOT claim COSMOS telemetry or create scientific observations.
set -Eeuo pipefail

MODE="check"
if (( $# > 0 )); then MODE="$1"; fi
case "$MODE" in check|run-ci-noop) ;; *) echo "usage: bash scripts/run_paper2x_phase_a_nominal.sh [check|run-ci-noop]" >&2; exit 2;; esac

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EXPECTED_NOS3="5a3bdee6be9a2c67fdf994ae6db56d5c60395302"
EXPECTED_LC="d65f77dea94467b7cb71053eb2f58f7a0cde3b02"
IMAGE="ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"
NOS3="$ROOT/external/nos3"
FORCE_FRESH_RESULTS="true"
PACKET_HEX="18fac000000100dc"
MARKER="SAMPLE: NOOP command received"

fail() { echo "P2X_PHASE_A_FAIL=$*" >&2; exit 1; }
for x in git docker python3 awk grep sha256sum; do
  if [[ "$x" == sha256sum ]] && ! command -v "$x" >/dev/null 2>&1; then
    command -v shasum >/dev/null 2>&1 || fail "missing_sha256sum_or_shasum"
  elif [[ "$x" != sha256sum ]]; then
    command -v "$x" >/dev/null 2>&1 || fail "missing_$x"
  fi
done
docker info >/dev/null 2>&1 || fail "docker_daemon_unavailable"
test -d "$NOS3/.git" || fail "pinned_local_nos3_checkout_missing"
test "$(git -C "$NOS3" rev-parse HEAD)" = "$EXPECTED_NOS3" || fail "nos3_revision_mismatch"
test -z "$(git -C "$NOS3" status --short)" || fail "nos3_checkout_dirty"
test "$(git -C "$NOS3/fsw/apps/lc" rev-parse HEAD)" = "$EXPECTED_LC" || fail "pinned_NOS3_LC_differs_from_registered_submodule"
grep -Fq '<gsw>cosmos</gsw>' "$NOS3/cfg/nos3-mission.xml" || fail "pinned_gsw_is_not_cosmos"
grep -Fq '<fsw>cfs</fsw>' "$NOS3/cfg/nos3-mission.xml" || fail "pinned_fsw_is_not_cfs"
bash "$ROOT/scripts/verify_nos3_source_lock.sh" || fail "source_lock_validation"
docker image inspect "$IMAGE" >/dev/null 2>&1 || fail "pinned_docker_image_missing"
for f in "$ROOT/artifacts/nominal-build-lock.txt" "$ROOT/artifacts/fortytwo-lock.txt" "$ROOT/artifacts/nominal-runtime-preflight-lock.txt"; do
  test -s "$f" || fail "historical_source_or_runtime_lock_missing"
done
grep -Fqx 'build_status=PASS' "$ROOT/artifacts/nominal-build-lock.txt" || fail "build_lock_not_PASS"
test -f "$NOS3/fsw/build/exe/cpu1/core-cpu1" || fail "built_cfs_missing"
test -f "$NOS3/sims/build/bin/nos3-single-simulator" || fail "built_simulator_missing"
echo "P2X_PHASE_A_HOST_LOCK_CHECK=PASS"
echo "pin_nos3=$EXPECTED_NOS3"
echo "pin_nos3_LC=$EXPECTED_LC"
echo "pin_image=$IMAGE"
echo "ground_config=cosmos"
echo "flight_config=cfs"
echo "historical_lock_not_fresh_runtime=true"
if [[ "$MODE" == check ]]; then
  echo "P2X_PHASE_A_FRESH_RUNTIME=NOT_RUN"
  echo "P2X_PHASE_A_COSMOS_TELEMETRY=NOT_OBSERVED"
  exit 0
fi

# The existing nominal launcher is a PINNED 21-component, INTERNAL-network preflight.
# It starts its own per-run network and cleans up run-scoped containers on exit.
RUN_ID="p2xa-$(date -u +%Y%m%dT%H%M%SZ)-$$"
SAFE_ID="$(printf '%s' "$RUN_ID" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9_.-' '-')"
NETWORK="mascr-$SAFE_ID"
CFS="mascr-$SAFE_ID-cfs"
EV="$ROOT/artifacts/runtime/$RUN_ID"
OUT="$EV/paper2x-phase-a"
mkdir -p "$OUT"
LOG="$OUT/nominal-runtime.log"
PID=""
RESULT="FAILED_CLOSED_BEFORE_COMMAND"
cleanup_phase_a() {
  local rc="$?"
  trap - EXIT INT TERM
  set +e
  if [[ -n "$PID" ]] && kill -0 "$PID" >/dev/null 2>&1; then
    kill -TERM "$PID" >/dev/null 2>&1
    wait "$PID" >/dev/null 2>&1
  fi
  printf 'phase_a_partial_status=%s\nscript_exit_code=%s\n' "$RESULT" "$rc" > "$OUT/phase-a-operator-status.txt"
  echo "P2X_PHASE_A_EVIDENCE_DIRECTORY=$OUT"
  if [[ "$rc" -ne 0 ]]; then echo "P2X_PHASE_A_FRESH_RUNTIME=FAIL_CLOSED" >&2; fi
}
trap cleanup_phase_a EXIT
trap 'exit 130' INT TERM

# No Paper-1/P7 policy code, producer state, scenario truth, fault fixture or gate invoked.
RUN_ID="$RUN_ID" DURATION_SECONDS=60 STARTUP_GRACE_SECONDS=20 \
  bash "$ROOT/scripts/run_nominal_runtime_preflight.sh" > "$LOG" 2>&1 &
PID="$!"
READY=0
for i in $(seq 1 150); do
  kill -0 "$PID" >/dev/null 2>&1 || break
  if [[ "$(docker inspect "$CFS" --format '{{.State.Status}}' 2>/dev/null || echo missing)" == running ]]; then
    READY=1
    break
  fi
  sleep 1
done
test "$READY" -eq 1 || fail "new_pinned_cFS_not_running"
test "$(docker network inspect "$NETWORK" --format '{{.Internal}}' 2>/dev/null)" = true || fail "runtime_not_internal_network"
test -z "$(docker port "$CFS")" || fail "cfs_exposes_host_port"
sleep 20
kill -0 "$PID" >/dev/null 2>&1 || fail "nominal_process_exited_before_NOOP"
before="$(docker logs "$CFS" 2>&1 | grep -Fc "$MARKER" || true)"
[[ "$before" =~ ^[0-9]+$ ]] || fail "invalid_baseline_event_count"

# One explicitly registered harmless packet over the internal ground test socket.
# This establishes cFS command ingestion only; it does NOT establish COSMOS downlink.
docker run --rm --platform linux/amd64 --network "$NETWORK" "$IMAGE" \
  python3 -c '
import datetime, hashlib, json, socket
pkt = bytes.fromhex("18fac000000100dc")
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
try:
    sent = sock.sendto(pkt,("nos-fsw",5012))
finally:
    sock.close()
if sent != len(pkt):
    raise SystemExit("FAIL_SHORT_UDP_SEND")
print(json.dumps({"method":"internal_test_sender_udp_not_COSMOS",
"utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
"destination":"nos-fsw:5012",
"packet_hex":pkt.hex(),"packet_sha256":hashlib.sha256(pkt).hexdigest(),
"bytes_sent":sent},sort_keys=True))
' > "$OUT/one-benign-noop-send.json"
RESULT="BENIGN_CFS_PACKET_SENT_EVENT_PENDING"
expected=$((before + 1))
observed="$before"
for i in $(seq 1 15); do
  sleep 2
  observed="$(docker logs "$CFS" 2>&1 | grep -Fc "$MARKER" || true)"
  [[ "$observed" =~ ^[0-9]+$ ]] || fail "invalid_post_event_count"
  if (( observed > expected )); then fail "unexpected_multiple_cfs_NOOP_markers"; fi
  if (( observed == expected )); then break; fi
done
test "$observed" -eq "$expected" || fail "benign_cFS_NOOP_not_observed"
RESULT="CFS_INTERNAL_CI_NOOP_CONFIRMED_COSMOS_TELEMETRY_PENDING"

# Wait for the nominal runtime script to complete and clean up its own exact run ID.
wait "$PID" || fail "pinned_nominal_runtime_failed"
PID=""
grep -Fq "NOMINAL_RUNTIME_PREFLIGHT_STATUS=PASS" "$LOG" || fail "nominal_runtime_terminal_status_not_PASS"
grep -Fqx "terminal_classification=RUNTIME_PREFLIGHT_PASS" "$EV/runtime-manifest.txt" || fail "manifest_classification"
grep -Fqx "exit_code=0" "$EV/runtime-manifest.txt" || fail "nominal_cleanup_exit_code"
python3 - "$OUT" "$RUN_ID" "$EXPECTED_NOS3" "$EXPECTED_LC" "$IMAGE" "$before" "$observed" <<'PY'
import hashlib, json, sys
from pathlib import Path
folder=Path(sys.argv[1])
packet=json.loads((folder/"one-benign-noop-send.json").read_text(encoding="utf-8"))
assert packet["method"]=="internal_test_sender_udp_not_COSMOS"
assert packet["packet_hex"]=="18fac000000100dc"
assert packet["bytes_sent"]==8
assert packet["packet_sha256"]==hashlib.sha256(bytes.fromhex(packet["packet_hex"])).hexdigest()
before,after=map(int,sys.argv[6:8])
assert after-before==1
report={
 "schema":1,
 "experiment_id":"P2X-NOS3-RG-001",
 "phase":"A_preflight_only",
 "run_id":sys.argv[2],
 "pin_nos3":sys.argv[3],
 "pin_LC_NOS3_submodule":sys.argv[4],
 "pin_image":sys.argv[5],
 "source_lock_verified":True,
 "nominal_21_component_runtime_completed":True,
 "internal_network_only":True,
 "internal_cfs_noop_marker_before":before,
 "internal_cfs_noop_marker_after":after,
 "internal_cfs_noop_increment":1,
 "sender_path":"internal_ground_test_sender_direct_UDP_NOT_COSMOS",
 "COSMOS_to_cFS_to_ground_telemetry_observed":False,
 "classification":"PHASE_A_PARTIAL_CFS_INGEST_PROOF__COSMOS_GROUND_CONFIRMATION_OPEN",
 "new_scientific_data_generated":False,
 "fault_injection_performed":False,
}
(folder/"phase-a-partial-report.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
print("P2X_PHASE_A_PARTIAL_CFS_INGEST=PASS")
print("P2X_PHASE_A_COSMOS_TELEMETRY=PENDING_SEPARATE_EVIDENCE")
PY
echo "P2X_PHASE_A_HOST_EVIDENCE=$OUT"
echo "P2X_PHASE_A_RESULT=PARTIAL_CFS_INGEST_PROOF_ONLY"
