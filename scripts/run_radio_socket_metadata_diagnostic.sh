#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE="$ROOT/scripts/run_downlink_port_correction_diagnostic.sh"
CONTRACT="$ROOT/configs/downlink-diagnostic-contract.json"
SHIM_SOURCE="$ROOT/scripts/radio_socket_metadata_shim.c"
SHIM_GATE_LOCK="$ROOT/artifacts/radio-socket-metadata-shim-static-gate-lock.txt"
TEMP=""

cleanup() {
  local rc=$?
  [[ -z "$TEMP" ]] || rm -f "$TEMP"
  trap - EXIT
  exit "$rc"
}
trap cleanup EXIT

for file in "$SOURCE" "$CONTRACT" "$SHIM_SOURCE" "$SHIM_GATE_LOCK"; do
  [[ -f "$file" ]] || {
    echo "[ERROR] Missing required file: $file" >&2
    exit 1
  }
done

bash -n "$SOURCE"
python3 -m json.tool "$CONTRACT" >/dev/null
python3 - "$CONTRACT" <<'PY'
import json
import os
import sys
from pathlib import Path

contract = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
verify_only = os.environ.get("RADIO_SOCKET_METADATA_WRAPPER_VERIFY_ONLY") == "1"
assert contract["contract_version"] == "0.4.2"
assert contract["scientific_outcome_allowed"] is False
assert contract["event_injection_allowed"] is False
assert contract["command_transmission_allowed"] is False
assert contract["baseline_execution_allowed"] is False
assert contract["cryptographic_semantics_claim_allowed"] is False
assert contract["gate"]["radio_socket_metadata_shim_static_verification"] == "PASS"
assert contract["gate"]["baseline_run_1_authorized"] is False
assert contract["gate"]["baseline_run_2_authorized"] is False
assert contract["gate"]["event_injection_authorized"] is False
if verify_only:
    assert contract["status"] == "RADIO_SOCKET_METADATA_RUNTIME_WRAPPER_STATIC_VALIDATION_PENDING"
    assert contract["gate"]["diagnostic_runtime_authorized"] is False
    assert contract["gate"]["diagnostic_runtime_attempts_authorized"] == 0
else:
    assert contract["status"] == "RADIO_SOCKET_METADATA_RUNTIME_STATIC_GATE_PASS_RUNTIME_PENDING"
    assert contract["gate"]["diagnostic_runtime_authorized"] is True
    assert contract["gate"]["diagnostic_runtime_attempts_authorized"] == 1
PY

source_sha_before="$(shasum -a 256 "$SOURCE" | awk '{print $1}')"
TEMP="$(mktemp "$ROOT/scripts/.run-radio-socket-metadata.XXXXXX.sh")"

python3 - "$SOURCE" "$TEMP" <<'PY'
import ast
import re
import sys
from pathlib import Path

source = Path(sys.argv[1])
output = Path(sys.argv[2])
text = source.read_text(encoding="utf-8")


def replace_exact(payload: str, old: str, new: str, expected: int, label: str) -> str:
    count = payload.count(old)
    if count != expected:
        raise SystemExit(f"{label}: expected {expected} occurrence(s), found {count}")
    return payload.replace(old, new)


version_count = text.count('"0.2.0"')
if version_count != 4:
    raise SystemExit(f"contract version source shape changed: expected 4, found {version_count}")
text = text.replace('"0.2.0"', '"0.4.2"')

pending_old = "PORT_CORRECTION_STATIC_VALIDATION_PENDING"
pending_new = "RADIO_SOCKET_METADATA_RUNTIME_WRAPPER_STATIC_VALIDATION_PENDING"
if text.count(pending_old) != 3:
    raise SystemExit("pending status source shape changed")
text = text.replace(pending_old, pending_new)

runtime_old = "PORT_CORRECTION_STATIC_GATE_PASS_RUNTIME_PENDING"
runtime_new = "RADIO_SOCKET_METADATA_RUNTIME_STATIC_GATE_PASS_RUNTIME_PENDING"
if text.count(runtime_old) != 4:
    raise SystemExit("runtime status source shape changed")
text = text.replace(runtime_old, runtime_new)

contract_assert_anchor = 'assert contract["cryptographic_semantics_claim_allowed"] is False\n'
contract_assert_insert = (
    contract_assert_anchor
    + 'assert contract["gate"]["radio_socket_metadata_shim_static_verification"] == "PASS"\n'
    + 'assert contract["gate"]["radio_socket_metadata_runtime_wrapper_static_verification"] == "PENDING"\n'
)
text = replace_exact(
    text,
    contract_assert_anchor,
    contract_assert_insert,
    1,
    "outer wrapper contract assertions",
)

integration_lines: list[str] = []


def add(statement: str = "") -> None:
    integration_lines.append(statement)


vars_old = 'ORCHESTRATION="$GROUND/orchestration"\nPOLICY="$EVIDENCE/policy-visible"\n'
vars_new = (
    'ORCHESTRATION="$GROUND/orchestration"\n'
    'SOCKET_METADATA_DIR="$GROUND/radio-socket-metadata"\n'
    'SHIM_BUILD_DIR="$ORCHESTRATION/radio-socket-shim"\n'
    'SHIM_SOURCE="$ROOT/scripts/radio_socket_metadata_shim.c"\n'
    'SHIM_SO="$SHIM_BUILD_DIR/libradio_socket_metadata_shim.so"\n'
    'SOCKET_TRACE="$SOCKET_METADATA_DIR/radio-socket-metadata.log"\n'
    'EXPECTED_SHIM_SOURCE_SHA256="d15ede657230560178b5648ef5d4e15b1965837a1c384790d9cbd3dc8f01ee1b"\n'
    'EXPECTED_SHIM_SO_SHA256="5a1e4f0cb2b5567ee70defa893f7c976453c788b6c9ac70e4f7d646c16223205"\n'
    'POLICY="$EVIDENCE/policy-visible"\n'
)
add(f"updated = replace_once(updated, {vars_old!r}, {vars_new!r}, 'socket metadata variables')")

files_old = 'for file in "$CONTRACT" "$DIAGNOSTIC_CONTRACT" "$WITNESS_SCRIPT" "$BUILD_LOCK" "$PREFLIGHT_LOCK"; do\n'
files_new = 'for file in "$CONTRACT" "$DIAGNOSTIC_CONTRACT" "$WITNESS_SCRIPT" "$SHIM_SOURCE" "$BUILD_LOCK" "$PREFLIGHT_LOCK"; do\n'
add(f"updated = replace_once(updated, {files_old!r}, {files_new!r}, 'shim required file')")

mkdir_old = 'mkdir -p "$PROBE_GROUND" "$ORCHESTRATION/runtime-config" "$POLICY" "$INOUT"\n'
mkdir_new = 'mkdir -p "$PROBE_GROUND" "$ORCHESTRATION/runtime-config" "$SOCKET_METADATA_DIR" "$SHIM_BUILD_DIR" "$POLICY" "$INOUT"\n'
add(f"updated = replace_once(updated, {mkdir_old!r}, {mkdir_new!r}, 'socket metadata directories')")

manifest_old = 'record diagnostic_type telemetry_only_downlink_witness\n'
manifest_new = (
    'record diagnostic_type radio_socket_metadata_observability\n'
    'record socket_metadata_only true\n'
    'record socket_metadata_packet_content false\n'
    'record socket_metadata_ip_addresses false\n'
)
add(f"updated = replace_once(updated, {manifest_old!r}, {manifest_new!r}, 'metadata diagnostic manifest')")

compile_anchor = 'docker network create --driver bridge --internal \\\n'
compile_block = '''actual_shim_source_sha="$(shasum -a 256 "$SHIM_SOURCE" | awk '{print $1}')"
[[ "$actual_shim_source_sha" == "$EXPECTED_SHIM_SOURCE_SHA256" ]] || {
  echo "[ERROR] Radio socket metadata shim source hash mismatch." >&2
  exit 1
}
docker run --rm --platform linux/amd64 --network none \
  --mount "type=bind,source=$SHIM_SOURCE,target=/src/radio_socket_metadata_shim.c,readonly" \
  --mount "type=bind,source=$SHIM_BUILD_DIR,target=/out" \
  "$IMAGE" bash -lc '
set -Eeuo pipefail
cc -std=c11 -Wall -Wextra -Werror -O2 -fPIC -shared \
  /src/radio_socket_metadata_shim.c \
  -o /out/libradio_socket_metadata_shim.so \
  -ldl
'
[[ -s "$SHIM_SO" ]] || {
  echo "[ERROR] Radio socket metadata shim shared object was not produced." >&2
  exit 1
}
actual_shim_so_sha="$(shasum -a 256 "$SHIM_SO" | awk '{print $1}')"
[[ "$actual_shim_so_sha" == "$EXPECTED_SHIM_SO_SHA256" ]] || {
  echo "[ERROR] Radio socket metadata shim shared-object hash mismatch." >&2
  exit 1
}
record radio_socket_metadata_shim_source_sha256 "$actual_shim_source_sha"
record radio_socket_metadata_shim_shared_object_sha256 "$actual_shim_so_sha"
record radio_socket_metadata_trace_path immutable-ground/radio-socket-metadata/radio-socket-metadata.log

docker network create --driver bridge --internal \
'''
add(f"updated = replace_once(updated, {compile_anchor!r}, {compile_block!r}, 'network-disabled shim build')")

radio_old = '''      --network-alias generic-radio-sim \\
      --env TCP_GROUND=0 --env MULTI_GDS=0 \\
      --mount "type=bind,source=$NOS3,target=/work/nos3" --workdir /work/nos3/sims/build/bin \\
'''
radio_new = '''      --network-alias generic-radio-sim \\
      --env TCP_GROUND=0 --env MULTI_GDS=0 \\
      --env LD_PRELOAD=/tmp/libradio_socket_metadata_shim.so \\
      --env RADIO_SOCKET_TRACE_PATH=/evidence-socket-metadata/radio-socket-metadata.log \\
      --mount "type=bind,source=$SHIM_SO,target=/tmp/libradio_socket_metadata_shim.so,readonly" \\
      --mount "type=bind,source=$SOCKET_METADATA_DIR,target=/evidence-socket-metadata" \\
      --mount "type=bind,source=$NOS3,target=/work/nos3" --workdir /work/nos3/sims/build/bin \\
'''
add(f"updated = replace_once(updated, {radio_old!r}, {radio_new!r}, 'generic-radio-only shim mount')")

helper_anchor = 'check_runtime() {\n'
helper_block = '''wait_for_socket_trace() {
  local name="$1" timeout_seconds="$2" manifest_key="$3"
  local attempt state
  for ((attempt=1; attempt<=timeout_seconds; attempt++)); do
    state="$(docker inspect "$name" --format '{{.State.Status}}' 2>/dev/null || echo missing)"
    [[ "$state" == running ]] || {
      echo "[ERROR] $name stopped before radio socket ingress metadata was observed." >&2
      return 1
    }
    if [[ -s "$SOCKET_TRACE" ]] && grep -Eq 'event=recvfrom .*local_port=5011 .*result=[1-9][0-9]* errno=0$' "$SOCKET_TRACE"; then
      record "$manifest_key" ready
      record "${manifest_key}_utc" "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
      return 0
    fi
    sleep 1
  done
  echo "[ERROR] $name produced no successful UDP 5011 recvfrom metadata within ${timeout_seconds}s." >&2
  return 1
}

check_runtime() {
'''
add(f"updated = replace_once(updated, {helper_anchor!r}, {helper_block!r}, 'socket metadata readiness helper')")

egress_wait_old = 'wait_for_log_marker "$PREFIX-radio-egress-witness" "TELEMETRY_WITNESS_RECEIVED mode=sink" 60 radio_egress_received\n'
egress_wait_new = 'wait_for_socket_trace "$PREFIX-generic-radio-sim" 60 radio_socket_recvfrom_5011\n'
add(f"updated = replace_once(updated, {egress_wait_old!r}, {egress_wait_new!r}, 'socket ingress readiness')")

add('invalid_count = updated.count(\'RESULT="DOWNLINK_DIAGNOSTIC_INVALID"\')')
add('if invalid_count != 3:')
add('    raise SystemExit(f"unexpected diagnostic-invalid assignment count: {invalid_count}")')
add('updated = updated.replace(\'RESULT="DOWNLINK_DIAGNOSTIC_INVALID"\', \'RESULT="RADIO_SOCKET_METADATA_DIAGNOSTIC_INVALID"\')')

cleanup_old = '''  if [[ "$RESULT" == DOWNLINK_DIAGNOSTIC_PASS && "$final_rc" -eq 0 ]]; then
    echo "DOWNLINK_DIAGNOSTIC_STATUS=PASS"
    echo "[OK] Evidence retained at: $EVIDENCE"
  else
    echo "DOWNLINK_DIAGNOSTIC_STATUS=RUN_INVALID" >&2
    echo "[INFO] Evidence retained at: $EVIDENCE" >&2
  fi
'''
cleanup_new = '''  if [[ "$RESULT" == RADIO_SOCKET_METADATA_DIAGNOSTIC_COMPLETE && "$final_rc" -eq 0 ]]; then
    echo "RADIO_SOCKET_METADATA_DIAGNOSTIC_STATUS=COMPLETE"
    echo "[OK] Evidence retained at: $EVIDENCE"
  else
    echo "RADIO_SOCKET_METADATA_DIAGNOSTIC_STATUS=RUN_INVALID" >&2
    echo "[INFO] Evidence retained at: $EVIDENCE" >&2
  fi
'''
add(f"updated = replace_once(updated, {cleanup_old!r}, {cleanup_new!r}, 'metadata cleanup classification')")

metadata_tail = '''record containers_started_utc "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
record runtime_component_count "$(wc -l < "$RUNTIME_NAMES" | tr -d ' ')"
record total_component_count "$(wc -l < "$NAMES" | tr -d ' ')"
check_runtime startup
sleep 30
check_runtime observation

[[ -s "$SOCKET_TRACE" ]] || {
  echo "[ERROR] Radio socket metadata trace is missing or empty." >&2
  exit 3
}
if grep -Eqi 'payload|payload_sha|hex=|data=|address=|ip=' "$SOCKET_TRACE"; then
  echo "[ERROR] Radio socket metadata trace contains forbidden content or address material." >&2
  exit 3
fi

to_logs="$(docker logs "$PREFIX-to-radio-witness" 2>&1 || true)"
egress_logs="$(docker logs "$PREFIX-radio-egress-witness" 2>&1 || true)"
to_received="$(grep -Fc 'TELEMETRY_WITNESS_RECEIVED mode=proxy' <<< "$to_logs" || true)"
to_forwarded="$(grep -Fc 'TELEMETRY_WITNESS_FORWARDED mode=proxy' <<< "$to_logs" || true)"
egress_received="$(grep -Fc 'TELEMETRY_WITNESS_RECEIVED mode=sink' <<< "$egress_logs" || true)"
witness_invalid="$(cat <(printf '%s\\n' "$to_logs") <(printf '%s\\n' "$egress_logs") | grep -Fc 'TELEMETRY_WITNESS_INVALID' || true)"
recv_success="$(grep -Ec 'event=recvfrom .*local_port=5011 .*result=[1-9][0-9]* errno=0$' "$SOCKET_TRACE" || true)"
send_success="$(grep -Ec 'event=sendto .*peer_port=8011 .*result=[1-9][0-9]* errno=0$' "$SOCKET_TRACE" || true)"
send_failure="$(grep -Ec 'event=sendto .*peer_port=8011 .*result=-1 errno=[1-9][0-9]*$' "$SOCKET_TRACE" || true)"
trace_records="$(grep -c '^RADIO_SOCKET_METADATA ' "$SOCKET_TRACE" || true)"

(( to_received >= 1 )) || { echo "[ERROR] TO witness received no telemetry." >&2; exit 3; }
(( to_forwarded >= 1 )) || { echo "[ERROR] TO witness forwarded no telemetry." >&2; exit 3; }
(( recv_success >= 1 )) || { echo "[ERROR] Radio socket metadata recorded no successful UDP 5011 recvfrom." >&2; exit 3; }
[[ "$witness_invalid" == 0 ]] || { echo "[ERROR] Telemetry witness recorded an invalid condition." >&2; exit 3; }

if (( send_failure >= 1 )); then
  transport_diagnosis=RADIO_EGRESS_SEND_FAILURE
elif (( send_success >= 1 && egress_received >= 1 )); then
  transport_diagnosis=DOWNLINK_PATH_THROUGH_RADIO_OBSERVED
elif (( send_success >= 1 )); then
  transport_diagnosis=RADIO_EGRESS_DESTINATION_OR_DELIVERY_FAILURE
else
  transport_diagnosis=RADIO_SIMULATION_TIME_QUEUE_RELEASE_FAILURE
fi

record to_witness_received_packet_markers "$to_received"
record to_witness_forwarded_packet_markers "$to_forwarded"
record radio_socket_recvfrom_5011_records "$recv_success"
record radio_socket_sendto_8011_success_records "$send_success"
record radio_socket_sendto_8011_failure_records "$send_failure"
record radio_socket_metadata_records "$trace_records"
record radio_egress_received_packet_markers "$egress_received"
record witness_invalid_count "$witness_invalid"
record transport_diagnosis "$transport_diagnosis"
record measured_command_transmissions 0
record ground_command_sources 0
RESULT="RADIO_SOCKET_METADATA_DIAGNOSTIC_COMPLETE"
record diagnostic_status COMPLETE
check_runtime final
docker ps --filter "label=research.project=$PROJECT" --filter "label=research.run_id=$RUN_ID" \
  --no-trunc --format '{{json .}}' > "$ORCHESTRATION/docker-ps-running.jsonl"
record observation_completed_utc "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "[OK] Radio UDP 5011 ingress was observed through metadata-only socket interposition."
echo "[OK] Transport diagnosis: $transport_diagnosis"
'''
add("tail_marker = 'record containers_started_utc \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"\\n'")
add('tail_start = updated.find(tail_marker)')
add('if tail_start < 0 or updated.count(tail_marker) != 1:')
add('    raise SystemExit("expected exactly one metadata runtime tail marker")')
add(f"metadata_tail = {metadata_tail!r}")
add('updated = updated[:tail_start] + metadata_tail')

add("for required in (")
for token in (
    'SOCKET_METADATA_DIR="$GROUND/radio-socket-metadata"',
    'docker run --rm --platform linux/amd64 --network none',
    '--env LD_PRELOAD=/tmp/libradio_socket_metadata_shim.so',
    '--env RADIO_SOCKET_TRACE_PATH=/evidence-socket-metadata/radio-socket-metadata.log',
    'wait_for_socket_trace',
    'radio_socket_recvfrom_5011_records',
    'RADIO_SOCKET_METADATA_DIAGNOSTIC_STATUS=COMPLETE',
    'ground_command_sources 0',
):
    add(f"    {token!r},")
add("):")
add("    if required not in updated:")
add("        raise SystemExit(f'metadata runtime requirement missing: {required}')")
add("for forbidden in ('--network host', '/var/run/docker.sock', '--cap-add NET_RAW', '--cap-add NET_ADMIN', 'tcpdump', 'tshark'):")
add("    if forbidden in updated:")
add("        raise SystemExit(f'forbidden metadata runtime token present: {forbidden}')")

integration_code = "\n".join(integration_lines) + "\n"
write_anchor = 'output_path.write_text(updated, encoding="utf-8")\nPYWRAP\n'
emit_anchor = 'bash -n "$TEMP_RUNNER"\nsource_sha_after='
emit_replacement = """bash -n "$TEMP_RUNNER"
if [[ -n "${RADIO_SOCKET_METADATA_EMIT_PATH:-}" ]]; then
  mkdir -p "$(dirname "$RADIO_SOCKET_METADATA_EMIT_PATH")"
  cp "$TEMP_RUNNER" "$RADIO_SOCKET_METADATA_EMIT_PATH"
  chmod 700 "$RADIO_SOCKET_METADATA_EMIT_PATH"
fi
source_sha_after="""

extension_lines = [
    f"integration_code = {integration_code!r}",
    f"write_anchor = {write_anchor!r}",
    "write_replacement = integration_code + write_anchor",
    "text = replace_exact(text, write_anchor, write_replacement, 1, 'metadata integration insertion')",
    f"emit_anchor = {emit_anchor!r}",
    f"emit_replacement = {emit_replacement!r}",
    "text = replace_exact(text, emit_anchor, emit_replacement, 1, 'generated runtime emission')",
]
extension_code = "\n".join(extension_lines) + "\n"
extension_anchor = 'validate_top_level_python_heredocs(text)\n'
text = replace_exact(
    text,
    extension_anchor,
    extension_code + extension_anchor,
    1,
    "port-correction metadata extension",
)

for required in (
    'assert contract["contract_version"] == "0.4.2"',
    "RADIO_SOCKET_METADATA_RUNTIME_WRAPPER_STATIC_VALIDATION_PENDING",
    "RADIO_SOCKET_METADATA_RUNTIME_STATIC_GATE_PASS_RUNTIME_PENDING",
    "radio_socket_metadata_shim_static_verification",
    "metadata integration insertion",
    "RADIO_SOCKET_METADATA_EMIT_PATH",
):
    if required not in text:
        raise SystemExit(f"wrapper requirement missing: {required}")

lines = text.splitlines()
marker = re.compile(r"<<'(?P<delimiter>PY[A-Z0-9_]*)'")
parsed = 0
index = 0
while index < len(lines):
    match = marker.search(lines[index])
    if match is None:
        index += 1
        continue
    delimiter = match.group("delimiter")
    body_start = index + 1
    index = body_start
    while index < len(lines) and lines[index] != delimiter:
        index += 1
    if index >= len(lines):
        raise SystemExit(f"unterminated Python heredoc: {delimiter}")
    body = "\n".join(lines[body_start:index]) + "\n"
    ast.parse(body, filename=f"<{delimiter}>")
    parsed += 1
    index += 1
if parsed < 1:
    raise SystemExit("no Python heredocs validated")

output.write_text(text, encoding="utf-8")
PY

chmod 700 "$TEMP"
bash -n "$TEMP"
source_sha_after="$(shasum -a 256 "$SOURCE" | awk '{print $1}')"
[[ "$source_sha_before" == "$source_sha_after" ]] || {
  echo "[ERROR] Port-correction runner changed during metadata wrapper preparation." >&2
  exit 1
}

echo "[OK] Generated a metadata-only generic-radio observability wrapper without modifying historical runners."
if [[ "${RADIO_SOCKET_METADATA_WRAPPER_VERIFY_ONLY:-0}" == 1 ]]; then
  DOWNLINK_DIAGNOSTIC_VERIFY_ONLY=1 bash "$TEMP" "$@"
  echo "RADIO_SOCKET_METADATA_RUNTIME_WRAPPER_GENERATION_STATUS=PASS"
  exit 0
fi

bash "$TEMP" "$@"
