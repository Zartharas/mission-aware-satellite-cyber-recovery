#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NOS3="$ROOT/external/nos3"
FORTYTWO="$ROOT/external/fortytwo"
IMAGE="ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"
NOS3_COMMIT="5a3bdee6be9a2c67fdf994ae6db56d5c60395302"
FORTYTWO_COMMIT="eda252bf31f27850e867e698cfdd963e143ead1f"
PROJECT="mission-aware-satellite-cyber-recovery"
PHASE="wp4-benign-baseline-interface-corrected"
RUN_ID="${RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)}"
SAFE_ID="$(printf '%s' "$RUN_ID" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9_.-' '-')"
NETWORK="mascr-$SAFE_ID"
PREFIX="mascr-$SAFE_ID"
BASELINE_TIMEOUT="${BASELINE_TIMEOUT_SECONDS:-240}"
PROBE_READINESS_TIMEOUT="${PROBE_READINESS_TIMEOUT_SECONDS:-150}"
ACCEPTANCE_TIMEOUT="${ACCEPTANCE_TIMEOUT_SECONDS:-30}"
EVIDENCE="$ROOT/artifacts/baselines/$RUN_ID"
GROUND="$EVIDENCE/immutable-ground"
PROBE_GROUND="$GROUND/probe"
ORCHESTRATION="$GROUND/orchestration"
POLICY="$EVIDENCE/policy-visible"
INOUT="$EVIDENCE/fortytwo/NOS3InOut"
FORTYTWO_INOUT_CONTAINER="/work/fortytwo-inout"
RUNTIME_SIM_CONFIG="$ORCHESTRATION/runtime-config/nos3-simulator.xml"
MANIFEST="$EVIDENCE/baseline-manifest.txt"
NAMES="$EVIDENCE/container-names.txt"
RUNTIME_NAMES="$EVIDENCE/runtime-container-names.txt"
LIVENESS="$ORCHESTRATION/liveness.csv"
RESULT="RUN_INVALID"

HARDWARE_SIMS=(
  generic-css-sim
  generic-eps-sim
  generic-fss-sim
  gps
  generic-imu-sim
  generic-mag-sim
  generic-reactionwheel-sim0
  generic-reactionwheel-sim1
  generic-reactionwheel-sim2
  generic-radio-sim
  sample-sim
  generic-star-tracker-sim
  generic-thruster-sim
  generic-torquer-sim
)

value() {
  awk -F= -v key="$2" '$1 == key {print substr($0,index($0,"=")+1)}' "$1" | tail -n 1
}

record() {
  printf '%s=%s\n' "$1" "$2" >> "$MANIFEST"
}

hash_tree() {
  python3 - "$1" <<'PY'
from __future__ import annotations
import hashlib
import os
import sys
from pathlib import Path

directory = Path(sys.argv[1]).resolve()
manifest = directory / "sha256-manifest.txt"
entries: list[str] = []
for path in sorted(directory.rglob("*")):
    if not path.is_file() or path == manifest or path.name.endswith(".tmp"):
        continue
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    entries.append(f"{digest}  {path.relative_to(directory).as_posix()}")
temporary = manifest.with_suffix(".txt.tmp")
temporary.write_text("\n".join(entries) + "\n", encoding="utf-8")
os.replace(temporary, manifest)
print(hashlib.sha256(manifest.read_bytes()).hexdigest())
PY
}

capture() {
  local name="$1"
  docker inspect "$name" > "$ORCHESTRATION/inspect-$name.json" 2>/dev/null || return 1
  docker logs --timestamps "$name" > "$ORCHESTRATION/$name.log" 2>&1 || return 1
}

cleanup() {
  local rc=$?
  local final_rc="$rc"
  local ids remaining_containers remaining_networks ground_hash policy_hash
  local capture_failed=0 cleanup_failed=0 ground_hash_failed=0 policy_hash_failed=0
  set +e

  if [[ -f "$NAMES" ]]; then
    while IFS= read -r name; do
      [[ -z "$name" ]] || capture "$name" || capture_failed=1
    done < "$NAMES"
  fi

  docker network inspect "$NETWORK" > "$ORCHESTRATION/network-final.json" 2>/dev/null || cleanup_failed=1
  docker ps -a --no-trunc --format '{{json .}}' > "$ORCHESTRATION/docker-ps-final.jsonl" 2>/dev/null || cleanup_failed=1

  ids="$(docker ps -aq --filter "label=research.project=$PROJECT" --filter "label=research.run_id=$RUN_ID")"
  if [[ -n "$ids" ]]; then
    docker rm -f $ids >/dev/null 2>&1 || cleanup_failed=1
  fi
  docker network rm "$NETWORK" >/dev/null 2>&1 || cleanup_failed=1

  remaining_containers="$(docker ps -aq --filter "label=research.project=$PROJECT" --filter "label=research.run_id=$RUN_ID" | wc -l | tr -d ' ')"
  remaining_networks="$(docker network ls -q --filter "label=research.project=$PROJECT" --filter "label=research.run_id=$RUN_ID" | wc -l | tr -d ' ')"
  [[ -n "$remaining_containers" ]] || { remaining_containers=-1; cleanup_failed=1; }
  [[ -n "$remaining_networks" ]] || { remaining_networks=-1; cleanup_failed=1; }

  if (( capture_failed != 0 || cleanup_failed != 0 || remaining_containers != 0 || remaining_networks != 0 )); then
    RESULT="RUN_INVALID"
    final_rc=3
  fi

  cat > "$ORCHESTRATION/terminal-state.txt" <<EOF
run_id=$RUN_ID
capture_failed=$capture_failed
cleanup_failed=$cleanup_failed
cleanup_project_containers_remaining=$remaining_containers
cleanup_project_networks_remaining=$remaining_networks
terminal_classification=$RESULT
pre_hash_exit_code=$final_rc
EOF

  ground_hash="$(hash_tree "$GROUND" 2>/dev/null)" || ground_hash_failed=1
  policy_hash="$(hash_tree "$POLICY" 2>/dev/null)" || policy_hash_failed=1
  [[ -n "$ground_hash" ]] || ground_hash_failed=1
  [[ -n "$policy_hash" ]] || policy_hash_failed=1

  if (( ground_hash_failed != 0 || policy_hash_failed != 0 )); then
    RESULT="RUN_INVALID"
    final_rc=3
  fi

  record cleanup_completed_utc "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  record evidence_capture_failed "$capture_failed"
  record cleanup_failed "$cleanup_failed"
  record cleanup_project_containers_remaining "$remaining_containers"
  record cleanup_project_networks_remaining "$remaining_networks"
  record immutable_ground_hash_failed "$ground_hash_failed"
  record policy_visible_hash_failed "$policy_hash_failed"
  [[ -z "$ground_hash" ]] || record immutable_ground_manifest_sha256 "$ground_hash"
  [[ -z "$policy_hash" ]] || record policy_visible_manifest_sha256 "$policy_hash"
  record terminal_classification "$RESULT"
  record exit_code "$final_rc"

  if [[ "$RESULT" == BENIGN_BASELINE_PASS && "$final_rc" -eq 0 ]]; then
    echo "BENIGN_BASELINE_STATUS=PASS"
    echo "[OK] Evidence retained at: $EVIDENCE"
  elif [[ "$RESULT" == BENIGN_BASELINE_FAIL ]]; then
    echo "BENIGN_BASELINE_STATUS=FAIL" >&2
    echo "[INFO] Evidence retained at: $EVIDENCE" >&2
  else
    echo "BENIGN_BASELINE_STATUS=RUN_INVALID" >&2
    echo "[INFO] Evidence retained at: $EVIDENCE" >&2
  fi

  trap - EXIT
  exit "$final_rc"
}

start() {
  local logical="$1" alias="$2" runtime="$3"
  shift 3
  local name="$PREFIX-$logical"
  docker run -d --platform linux/amd64 --name "$name" --hostname "$alias" \
    --network "$NETWORK" --network-alias "$alias" \
    --env TERM=xterm \
    --label "research.project=$PROJECT" \
    --label "research.phase=$PHASE" \
    --label "research.run_id=$RUN_ID" \
    --log-driver json-file --log-opt max-size=10m --log-opt max-file=2 \
    "$@" >/dev/null
  echo "$name" >> "$NAMES"
  if [[ "$runtime" == true ]]; then
    echo "$name" >> "$RUNTIME_NAMES"
  fi
}

check_container_isolation() {
  local name="$1" networks
  networks="$(docker inspect "$name" --format '{{range $k,$v := .NetworkSettings.Networks}}{{$k}}{{end}}' 2>/dev/null || true)"
  [[ "$networks" == "$NETWORK" ]] || {
    echo "[ERROR] Unexpected network for $name: $networks" >&2
    return 1
  }
  [[ -z "$(docker port "$name" 2>/dev/null)" ]] || {
    echo "[ERROR] Host port published by $name." >&2
    return 1
  }
  if docker inspect "$name" --format '{{range .Mounts}}{{println .Source .Destination}}{{end}}' 2>/dev/null | grep -q '/var/run/docker.sock'; then
    echo "[ERROR] Docker socket mounted in $name." >&2
    return 1
  fi
}

wait_for_log_marker() {
  local name="$1" marker="$2" timeout_seconds="$3" manifest_key="$4"
  local attempt state logs
  for ((attempt=1; attempt<=timeout_seconds; attempt++)); do
    state="$(docker inspect "$name" --format '{{.State.Status}}' 2>/dev/null || echo missing)"
    [[ "$state" == running ]] || {
      echo "[ERROR] $name stopped before readiness marker '$marker' was observed." >&2
      return 1
    }
    logs="$(docker logs "$name" 2>&1 || true)"
    if grep -Fq -- "$marker" <<< "$logs"; then
      record "$manifest_key" ready
      record "${manifest_key}_utc" "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
      return 0
    fi
    sleep 1
  done
  echo "[ERROR] $name did not report readiness marker '$marker' within ${timeout_seconds}s." >&2
  return 1
}

wait_for_tcp_listener() {
  local name="$1" port="$2" timeout_seconds="$3" manifest_key="$4"
  local hex_port attempt state
  hex_port="$(printf '%04X' "$port")"
  for ((attempt=1; attempt<=timeout_seconds; attempt++)); do
    state="$(docker inspect "$name" --format '{{.State.Status}}' 2>/dev/null || echo missing)"
    [[ "$state" == running ]] || {
      echo "[ERROR] $name stopped before TCP port $port became ready." >&2
      return 1
    }
    if docker exec "$name" sh -lc \
      "awk '\$2 ~ /:${hex_port}\$/ && \$4 == \"0A\" {found=1} END {exit found ? 0 : 1}' /proc/net/tcp" \
      >/dev/null 2>&1; then
      record "$manifest_key" ready
      record "${manifest_key}_utc" "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
      return 0
    fi
    sleep 1
  done
  echo "[ERROR] $name did not expose TCP listener $port within ${timeout_seconds}s." >&2
  return 1
}

check_runtime() {
  local phase="$1" failed=0 name state code
  while IFS= read -r name; do
    state="$(docker inspect "$name" --format '{{.State.Status}}' 2>/dev/null || echo missing)"
    code="$(docker inspect "$name" --format '{{.State.ExitCode}}' 2>/dev/null || echo unknown)"
    printf '%s,%s,%s,%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$phase" "$name" "$state:$code" >> "$LIVENESS"
    [[ "$state" == running ]] || {
      echo "[ERROR] $name is $state (exit $code)." >&2
      failed=1
    }
    check_container_isolation "$name" || failed=1
  done < "$RUNTIME_NAMES"
  return "$failed"
}

for number in "$BASELINE_TIMEOUT" "$PROBE_READINESS_TIMEOUT" "$ACCEPTANCE_TIMEOUT"; do
  [[ "$number" =~ ^[0-9]+$ ]] || {
    echo "[ERROR] Baseline timeout values must be integers." >&2
    exit 1
  }
done
(( BASELINE_TIMEOUT >= 120 && BASELINE_TIMEOUT <= 600 )) || {
  echo "[ERROR] BASELINE_TIMEOUT_SECONDS must be 120-600." >&2
  exit 1
}
(( PROBE_READINESS_TIMEOUT >= 60 && PROBE_READINESS_TIMEOUT <= 300 )) || {
  echo "[ERROR] PROBE_READINESS_TIMEOUT_SECONDS must be 60-300." >&2
  exit 1
}
(( ACCEPTANCE_TIMEOUT == 30 )) || {
  echo "[ERROR] ACCEPTANCE_TIMEOUT_SECONDS is frozen at 30." >&2
  exit 1
}

for command in docker git awk shasum python3; do
  command -v "$command" >/dev/null 2>&1 || {
    echo "[ERROR] Missing command: $command" >&2
    exit 1
  }
done

docker info >/dev/null 2>&1 || { echo "[ERROR] Docker daemon is not reachable." >&2; exit 1; }
docker image inspect "$IMAGE" >/dev/null 2>&1 || { echo "[ERROR] Pinned image is unavailable." >&2; exit 1; }

CONTRACT="$ROOT/configs/benign-baseline-contract.json"
PROBE_SCRIPT="$ROOT/scripts/benign_ground_probe_measurement.py"
BUILD_LOCK="$ROOT/artifacts/nominal-build-lock.txt"
PREFLIGHT_LOCK="$ROOT/artifacts/nominal-runtime-preflight-lock.txt"
for file in "$CONTRACT" "$PROBE_SCRIPT" "$BUILD_LOCK" "$PREFLIGHT_LOCK"; do
  [[ -f "$file" ]] || { echo "[ERROR] Missing required file: $file" >&2; exit 1; }
done

python3 -m json.tool "$CONTRACT" >/dev/null
python3 "$PROBE_SCRIPT" --self-test >/dev/null
python3 - "$CONTRACT" <<'PY'
import json
import sys
contract = json.load(open(sys.argv[1], encoding="utf-8"))
assert contract["event_injection_allowed"] is False
assert contract["measured_command"]["name"] == "SAMPLE_NOOP_CC"
assert contract["measured_command"]["maximum_transmissions_per_run"] == 1
assert contract["measured_command"]["expected_packet_hex"] == "18fac000000100dc"
assert contract["telemetry_activation"]["ground_setup_transmissions"] == 0
assert contract["transport"]["cfs_ci"]["port"] == 5012
assert contract["transport"]["cfs_to"]["destination_alias"] == "active-gs"
assert contract["transport"]["host_ports_allowed"] is False
assert contract["transport"]["docker_socket_mount_allowed"] is False
assert contract["transport"]["external_egress_allowed"] is False
PY

[[ "$(value "$BUILD_LOCK" build_status)" == PASS ]] || { echo "[ERROR] NOS3 build lock is not PASS." >&2; exit 1; }
[[ "$(value "$PREFLIGHT_LOCK" runtime_preflight_status)" == PASS ]] || { echo "[ERROR] Runtime preflight lock is not PASS." >&2; exit 1; }
[[ "$(git -C "$NOS3" rev-parse HEAD)" == "$NOS3_COMMIT" ]] || { echo "[ERROR] NOS3 commit mismatch." >&2; exit 1; }
[[ "$(git -C "$FORTYTWO" rev-parse HEAD)" == "$FORTYTWO_COMMIT" ]] || { echo "[ERROR] 42 commit mismatch." >&2; exit 1; }
[[ -z "$(git -C "$NOS3" status --short)" ]] || { echo "[ERROR] NOS3 worktree is not clean." >&2; exit 1; }
[[ -z "$(git -C "$FORTYTWO" status --short)" ]] || { echo "[ERROR] 42 worktree is not clean." >&2; exit 1; }

required=(
  "$NOS3/cfg/build/InOut/Inp_Sim.txt"
  "$NOS3/cfg/build/InOut/Inp_IPC.txt"
  "$NOS3/fsw/build/exe/cpu1/core-cpu1"
  "$NOS3/sims/build/bin/nos3-single-simulator"
  "$NOS3/sims/build/bin/nos3-sim-cmdbus-bridge"
  "$NOS3/sims/build/bin/nos_engine_server_config.json"
  "$NOS3/sims/build/bin/nos3-simulator.xml"
  "$NOS3/gsw/build/support/standalone"
  "$FORTYTWO/42"
)
for file in "${required[@]}"; do
  [[ -f "$file" ]] || { echo "[ERROR] Missing runtime artifact: $file" >&2; exit 1; }
done

[[ -z "$(docker ps -aq --filter "label=research.project=$PROJECT")" ]] || {
  echo "[ERROR] Existing project runtime containers found; run scripts/cleanup_nominal_runtime.sh." >&2
  exit 1
}
[[ -z "$(docker network ls -q --filter "label=research.project=$PROJECT")" ]] || {
  echo "[ERROR] Existing project runtime networks found; run scripts/cleanup_nominal_runtime.sh." >&2
  exit 1
}

mkdir -p "$PROBE_GROUND" "$ORCHESTRATION/runtime-config" "$POLICY" "$INOUT"
: > "$MANIFEST"
: > "$NAMES"
: > "$RUNTIME_NAMES"
printf 'timestamp_utc,phase,container,state_exit_code\n' > "$LIVENESS"
trap cleanup EXIT
trap 'exit 130' INT TERM

docker ps -a --no-trunc --format '{{json .}}' > "$ORCHESTRATION/docker-ps-before.jsonl"
docker network ls --no-trunc --format '{{json .}}' > "$ORCHESTRATION/docker-networks-before.jsonl"
cp -R "$NOS3/cfg/build/InOut/." "$INOUT/"
cp "$NOS3/sims/build/bin/nos3-simulator.xml" "$RUNTIME_SIM_CONFIG"

python3 - "$INOUT/Inp_Sim.txt" "$RUNTIME_SIM_CONFIG" <<'PY'
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

inp_sim = Path(sys.argv[1])
lines = inp_sim.read_text(encoding="utf-8").splitlines()
for index, line in enumerate(lines):
    if "Graphics Front End?" in line:
        comment = line.split("!", 1)[1] if "!" in line else " Graphics Front End?"
        lines[index] = f"FALSE                           !{comment}"
        break
else:
    raise SystemExit("Graphics Front End setting not found")
inp_sim.write_text("\n".join(lines) + "\n", encoding="utf-8")

config = Path(sys.argv[2])
tree = ET.parse(config)
root = tree.getroot()
radio = None
for simulator in root.findall("./simulators/simulator"):
    if (simulator.findtext("name") or "").strip() == "generic-radio-sim":
        radio = simulator
        break
if radio is None:
    raise SystemExit("generic-radio-sim configuration not found")
connections = radio.findall("./hardware-model/connections/connection")
fsw = next((c for c in connections if (c.findtext("name") or "").strip() == "fsw"), None)
gsw = next((c for c in connections if (c.findtext("name") or "").strip() == "gsw"), None)
if fsw is None or gsw is None:
    raise SystemExit("radio FSW/GSW connection configuration missing")
ci_port = fsw.find("ci-port")
to_port = fsw.find("to-port")
if ci_port is None or to_port is None:
    raise SystemExit("radio FSW CI/TO ports missing")
if (ci_port.text or "").strip() != "5010":
    raise SystemExit(f"unexpected source CI port: {ci_port.text!r}")
if (to_port.text or "").strip() != "5011":
    raise SystemExit(f"unexpected source TO port: {to_port.text!r}")
ci_port.text = "5012"
if (gsw.findtext("ip") or "").strip() != "cryptolib":
    raise SystemExit("radio GSW destination is not cryptolib")
if (gsw.findtext("cmd-port") or "").strip() != "8010":
    raise SystemExit("radio GSW command port is not 8010")
if (gsw.findtext("tlm-port") or "").strip() != "8011":
    raise SystemExit("radio GSW telemetry port is not 8011")
tree.write(config, encoding="utf-8", xml_declaration=True)
PY

grep -q '^FALSE[[:space:]]*![[:space:]]*Graphics Front End?' "$INOUT/Inp_Sim.txt" || {
  echo "[ERROR] 42 runtime configuration is not headless." >&2
  exit 1
}
grep -q '<ci-port>5012</ci-port>' "$RUNTIME_SIM_CONFIG" || {
  echo "[ERROR] Runtime radio CI port override is missing." >&2
  exit 1
}

record run_id "$RUN_ID"
record started_utc "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
record project "$PROJECT"
record phase "$PHASE"
record baseline_timeout_seconds "$BASELINE_TIMEOUT"
record probe_readiness_timeout_seconds "$PROBE_READINESS_TIMEOUT"
record acceptance_timeout_seconds "$ACCEPTANCE_TIMEOUT"
record event_injection disabled
record telemetry_activation SC_RTS001_TO_LAB_OUTPUT_ENABLE
record ground_setup_command_transmissions 0
record to_lab_destination_alias active-gs
record to_lab_destination_port 5011
record ci_application CI_LAB
record ci_listen_port 5012
record runtime_radio_ci_port_override 5010_to_5012
record command_name SAMPLE_NOOP_CC
record command_packet_hex 18fac000000100dc
record command_packet_sha256 722b8fe72fb18ee581c970ea92c100f435fa90ccccaf0a05bf3e8bee0c4d13bd
record maximum_command_transmissions 1
record expected_runtime_component_count 21
record expected_total_component_count 22
record simulator_launch_mode individual_pinned_headless_set_runtime_interface_override
record hardware_simulator_count "${#HARDWARE_SIMS[@]}"
record truth_stream_dependency internal_read_only_sink
record truth_sink_policy_visibility none
record ground_evidence_directory immutable-ground
record policy_visible_evidence_directory policy-visible
record network "$NETWORK"
record network_mode internal_bridge
record nos3_commit "$NOS3_COMMIT"
record fortytwo_commit "$FORTYTWO_COMMIT"
record image "$IMAGE"
record image_id "$(docker image inspect "$IMAGE" --format '{{.Id}}')"
record contract_sha256 "$(shasum -a 256 "$CONTRACT" | awk '{print $1}')"
record probe_script_sha256 "$(shasum -a 256 "$PROBE_SCRIPT" | awk '{print $1}')"
record build_lock_sha256 "$(shasum -a 256 "$BUILD_LOCK" | awk '{print $1}')"
record runtime_preflight_lock_sha256 "$(shasum -a 256 "$PREFLIGHT_LOCK" | awk '{print $1}')"
record runtime_inp_sim_sha256 "$(shasum -a 256 "$INOUT/Inp_Sim.txt" | awk '{print $1}')"
record runtime_inp_ipc_sha256 "$(shasum -a 256 "$INOUT/Inp_IPC.txt" | awk '{print $1}')"
record runtime_simulator_config_sha256 "$(shasum -a 256 "$RUNTIME_SIM_CONFIG" | awk '{print $1}')"
record fortytwo_inout_container "$FORTYTWO_INOUT_CONTAINER"

docker network create --driver bridge --internal \
  --label "research.project=$PROJECT" \
  --label "research.phase=$PHASE" \
  --label "research.run_id=$RUN_ID" \
  "$NETWORK" >/dev/null
[[ "$(docker network inspect "$NETWORK" --format '{{.Internal}}')" == true ]] || {
  echo "[ERROR] Baseline network is not internal." >&2
  exit 1
}
docker network inspect "$NETWORK" > "$ORCHESTRATION/network-created.json"

start ground-probe ground-probe false \
  --mount "type=bind,source=$PROBE_SCRIPT,target=/probe/benign_ground_probe_measurement.py,readonly" \
  --mount "type=bind,source=$PROBE_GROUND,target=/evidence-ground" \
  --mount "type=bind,source=$POLICY,target=/evidence-policy" \
  "$IMAGE" python3 -u /probe/benign_ground_probe_measurement.py \
    --run-id "$RUN_ID" \
    --ground-dir /evidence-ground \
    --policy-dir /evidence-policy \
    --telemetry-bind 0.0.0.0 \
    --telemetry-port 6011 \
    --command-host cryptolib \
    --command-port 6010 \
    --readiness-timeout "$PROBE_READINESS_TIMEOUT" \
    --acceptance-timeout "$ACCEPTANCE_TIMEOUT" \
    --minimum-stable 2
wait_for_log_marker "$PREFIX-ground-probe" GROUND_PROBE_READY 20 ground_probe_udp_6011
check_container_isolation "$PREFIX-ground-probe"

start engine nos-engine-server true \
  --interactive --tty --network-alias sc01-nos-engine-server \
  --mount "type=bind,source=$NOS3,target=/work/nos3" --workdir /work/nos3/sims/build/bin \
  "$IMAGE" /usr/bin/nos_engine_server_standalone -f nos_engine_server_config.json
sleep 2
start time nos-time-driver true \
  --mount "type=bind,source=$NOS3,target=/work/nos3" \
  --mount "type=bind,source=$RUNTIME_SIM_CONFIG,target=/runtime-config/nos3-simulator.xml,readonly" \
  --workdir /work/nos3/sims/build/bin \
  "$IMAGE" ./nos3-single-simulator -f /runtime-config/nos3-simulator.xml time
start fortytwo fortytwo true \
  --mount "type=bind,source=$FORTYTWO,target=/work/fortytwo,readonly" \
  --mount "type=bind,source=$INOUT,target=$FORTYTWO_INOUT_CONTAINER" --workdir /work/fortytwo \
  "$IMAGE" ./42 "$FORTYTWO_INOUT_CONTAINER"
start truth-sink truth-sink true \
  --env TRUTH_HOST=fortytwo --env TRUTH_PORT=9999 --env CONNECT_TIMEOUT_SECONDS=75 \
  "$IMAGE" python3 -u -c '
import os, socket, sys, time
host=os.environ["TRUTH_HOST"]; port=int(os.environ["TRUTH_PORT"])
deadline=time.monotonic()+int(os.environ["CONNECT_TIMEOUT_SECONDS"]); last=None
while True:
    try:
        stream=socket.create_connection((host,port),timeout=1.0); stream.settimeout(None)
        print(f"TRUTH_SINK_CONNECTED host={host} port={port}",flush=True); break
    except OSError as exc:
        last=exc
        if time.monotonic()>=deadline:
            print(f"TRUTH_SINK_CONNECT_FAILED host={host} port={port} error={last}",file=sys.stderr,flush=True); raise SystemExit(2)
        time.sleep(0.5)
received=0; last_report=time.monotonic()
while True:
    payload=stream.recv(65536)
    if not payload:
        print(f"TRUTH_SINK_STREAM_CLOSED bytes={received}",file=sys.stderr,flush=True); raise SystemExit(3)
    received+=len(payload); now=time.monotonic()
    if now-last_report>=5.0:
        print(f"TRUTH_SINK_BYTES={received}",flush=True); last_report=now
'

for sim in "${HARDWARE_SIMS[@]}"; do
  if [[ "$sim" == generic-radio-sim ]]; then
    start "$sim" radio-sim true \
      --network-alias generic-radio-sim --network-alias active-gs \
      --env TCP_GROUND=1 --env MULTI_GDS=0 \
      --mount "type=bind,source=$NOS3,target=/work/nos3" \
      --mount "type=bind,source=$RUNTIME_SIM_CONFIG,target=/runtime-config/nos3-simulator.xml,readonly" \
      --workdir /work/nos3/sims/build/bin \
      "$IMAGE" ./nos3-single-simulator -f /runtime-config/nos3-simulator.xml "$sim"
  else
    start "$sim" "$sim" true \
      --mount "type=bind,source=$NOS3,target=/work/nos3" \
      --mount "type=bind,source=$RUNTIME_SIM_CONFIG,target=/runtime-config/nos3-simulator.xml,readonly" \
      --workdir /work/nos3/sims/build/bin \
      "$IMAGE" ./nos3-single-simulator -f /runtime-config/nos3-simulator.xml "$sim"
  fi
done

wait_for_log_marker "$PREFIX-truth-sink" TRUTH_SINK_CONNECTED 75 truth_sink_connection
wait_for_tcp_listener "$PREFIX-generic-radio-sim" 8010 45 radio_tcp_8010_listener

start cryptolib cryptolib true \
  --interactive \
  --env STANDALONE_TCP=1 --env CRYPTO_HOST=0.0.0.0 --env GSWALIAS=ground-probe \
  --mount "type=bind,source=$NOS3,target=/work/nos3" --workdir /work/nos3/gsw/build \
  "$IMAGE" ./support/standalone
start bridge nos-sim-bridge true \
  --mount "type=bind,source=$NOS3,target=/work/nos3" \
  --mount "type=bind,source=$RUNTIME_SIM_CONFIG,target=/runtime-config/nos3-simulator.xml,readonly" \
  --workdir /work/nos3/sims/build/bin \
  "$IMAGE" ./nos3-sim-cmdbus-bridge -f /runtime-config/nos3-simulator.xml
start cfs nos-fsw true \
  --mount "type=bind,source=$NOS3,target=/work/nos3" \
  --env USER=nos3 --env LD_LIBRARY_PATH=/work/nos3/fsw/build/exe/cpu1:/usr/lib:/usr/local/lib \
  --workdir /work/nos3/fsw/build/exe/cpu1 --sysctl fs.mqueue.msg_max=10000 \
  --ulimit rtprio=99 --cap-add SYS_NICE \
  "$IMAGE" bash -lc 'exec ./core-cpu1 -R PO'

wait_for_log_marker "$PREFIX-generic-radio-sim" "Successfully connected to TCP server!" 45 radio_cryptolib_downlink
wait_for_log_marker "$PREFIX-cfs" "CI_LAB listening on UDP port: 5012" 45 ci_lab_udp_5012
wait_for_log_marker "$PREFIX-cfs" "TO telemetry output enabled for IP active-gs" 60 to_lab_active_gs

active_gs_ip="$(docker inspect "$PREFIX-generic-radio-sim" --format '{{(index .NetworkSettings.Networks "'"$NETWORK"'").IPAddress}}')"
[[ -n "$active_gs_ip" ]] || { echo "[ERROR] Radio container has no project-network address." >&2; exit 1; }
record active_gs_radio_ip "$active_gs_ip"

record containers_started_utc "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
record runtime_component_count "$(wc -l < "$RUNTIME_NAMES" | tr -d ' ')"
record total_component_count "$(wc -l < "$NAMES" | tr -d ' ')"
check_runtime startup

probe_name="$PREFIX-ground-probe"
elapsed=0
while (( elapsed < BASELINE_TIMEOUT )); do
  sleep 5
  elapsed=$((elapsed + 5))
  check_runtime "observation-$elapsed"
  probe_state="$(docker inspect "$probe_name" --format '{{.State.Status}}' 2>/dev/null || echo missing)"
  probe_code="$(docker inspect "$probe_name" --format '{{.State.ExitCode}}' 2>/dev/null || echo unknown)"
  record "probe_state_observation_$elapsed" "$probe_state:$probe_code"
  [[ "$probe_state" != exited ]] || break
done

probe_state="$(docker inspect "$probe_name" --format '{{.State.Status}}' 2>/dev/null || echo missing)"
probe_code="$(docker inspect "$probe_name" --format '{{.State.ExitCode}}' 2>/dev/null || echo unknown)"
record ground_probe_exit_state "$probe_state:$probe_code"
[[ "$probe_state" == exited ]] || { echo "[ERROR] Ground probe did not finish within ${BASELINE_TIMEOUT}s." >&2; exit 3; }

PROBE_RESULT="$PROBE_GROUND/probe-result.json"
[[ -f "$PROBE_RESULT" ]] || { echo "[ERROR] Ground probe result is missing." >&2; exit 3; }
probe_classification="$(python3 - "$PROBE_RESULT" <<'PY'
import json, sys
print(json.load(open(sys.argv[1], encoding="utf-8"))["classification"])
PY
)"
record ground_probe_classification "$probe_classification"
record ground_probe_result_sha256 "$(shasum -a 256 "$PROBE_RESULT" | awk '{print $1}')"

case "$probe_classification:$probe_code" in
  BENIGN_BASELINE_PASS:0)
    required_pass_evidence=(
      "$PROBE_GROUND/transmitted-command.bin"
      "$PROBE_GROUND/pre-command-1.bin"
      "$PROBE_GROUND/pre-command-2.bin"
      "$PROBE_GROUND/post-command.bin"
      "$PROBE_GROUND/telemetry-events.jsonl"
      "$POLICY/telemetry.jsonl"
    )
    for file in "${required_pass_evidence[@]}"; do
      [[ -s "$file" ]] || { echo "[ERROR] Required PASS evidence is missing or empty: $file" >&2; exit 3; }
    done
    [[ ! -e "$PROBE_GROUND/transmitted-setup-command.bin" ]] || {
      echo "[ERROR] Unexpected ground setup-command evidence exists." >&2
      exit 3
    }
    [[ "$(shasum -a 256 "$PROBE_GROUND/transmitted-command.bin" | awk '{print $1}')" == 722b8fe72fb18ee581c970ea92c100f435fa90ccccaf0a05bf3e8bee0c4d13bd ]] || {
      echo "[ERROR] Transmitted command evidence hash mismatch." >&2
      exit 3
    }
    probe_latency_ms="$(python3 - "$PROBE_RESULT" <<'PY'
import json, sys
result=json.load(open(sys.argv[1],encoding="utf-8"))
assert result["classification"]=="BENIGN_BASELINE_PASS"
assert result["telemetry_activation"]["ground_setup_transmissions"]==0
assert result["command"]["transmissions"]==1
assert result["command"]["packet_hex"]=="18fac000000100dc"
before=result["before"]; after=result["after"]
assert before is not None and after is not None
assert after["cmd_count"]==(before["cmd_count"]+1)%256
assert after["cmd_err_count"]==before["cmd_err_count"]
assert after["device_err_count"]==before["device_err_count"]
print(result["command_to_acceptance_latency_ms"])
PY
)" || { echo "[ERROR] Ground-probe PASS result failed deterministic assertion review." >&2; exit 3; }
    RESULT="BENIGN_BASELINE_PASS"
    record baseline_status PASS
    record command_to_acceptance_latency_ms "$probe_latency_ms"
    ;;
  BENIGN_BASELINE_FAIL:2)
    RESULT="BENIGN_BASELINE_FAIL"
    record baseline_status FAIL
    exit 2
    ;;
  *)
    echo "[ERROR] Ground probe ended as $probe_classification with exit $probe_code." >&2
    exit 3
    ;;
esac

check_runtime final
docker ps --filter "label=research.project=$PROJECT" --filter "label=research.run_id=$RUN_ID" \
  --no-trunc --format '{{json .}}' > "$ORCHESTRATION/docker-ps-running.jsonl"
record observation_completed_utc "$(date -u +%Y-%m-%dT%H:%M:%SZ)"

echo "[OK] One frozen SAMPLE_NOOP_CC packet was accepted."
echo "[OK] CI_LAB/TO_LAB interface correction and evidence separation remained active."
