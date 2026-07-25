#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NOS3="$ROOT/external/nos3"
FORTYTWO="$ROOT/external/fortytwo"
IMAGE="ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"
NOS3_COMMIT="5a3bdee6be9a2c67fdf994ae6db56d5c60395302"
FORTYTWO_COMMIT="eda252bf31f27850e867e698cfdd963e143ead1f"
PROJECT="mission-aware-satellite-cyber-recovery"
PHASE="wp4-benign-baseline"
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

capture() {
  local name="$1"
  docker inspect "$name" > "$ORCHESTRATION/inspect-$name.json" 2>/dev/null || true
  docker logs --timestamps "$name" > "$ORCHESTRATION/$name.log" 2>&1 || true
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

cleanup() {
  local rc=$?
  local ids remaining_containers remaining_networks ground_hash policy_hash
  set +e

  if [[ -f "$NAMES" ]]; then
    while IFS= read -r name; do
      [[ -n "$name" ]] && capture "$name"
    done < "$NAMES"
  fi

  docker network inspect "$NETWORK" > "$ORCHESTRATION/network-final.json" 2>/dev/null || true
  docker ps -a --no-trunc --format '{{json .}}' > "$ORCHESTRATION/docker-ps-final.jsonl" 2>/dev/null || true

  ids="$(docker ps -aq --filter "label=research.project=$PROJECT" --filter "label=research.run_id=$RUN_ID")"
  [[ -z "$ids" ]] || docker rm -f $ids >/dev/null 2>&1
  docker network rm "$NETWORK" >/dev/null 2>&1 || true

  remaining_containers="$(docker ps -aq --filter "label=research.project=$PROJECT" --filter "label=research.run_id=$RUN_ID" | wc -l | tr -d ' ')"
  remaining_networks="$(docker network ls -q --filter "label=research.project=$PROJECT" --filter "label=research.run_id=$RUN_ID" | wc -l | tr -d ' ')"

  record cleanup_completed_utc "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  record cleanup_project_containers_remaining "$remaining_containers"
  record cleanup_project_networks_remaining "$remaining_networks"
  record terminal_classification "$RESULT"
  record exit_code "$rc"

  cp "$MANIFEST" "$ORCHESTRATION/baseline-manifest-final.txt" 2>/dev/null || true
  ground_hash="$(hash_tree "$GROUND" 2>/dev/null || true)"
  policy_hash="$(hash_tree "$POLICY" 2>/dev/null || true)"
  [[ -z "$ground_hash" ]] || record immutable_ground_manifest_sha256 "$ground_hash"
  [[ -z "$policy_hash" ]] || record policy_visible_manifest_sha256 "$policy_hash"

  if [[ "$RESULT" == BENIGN_BASELINE_PASS && "$rc" -eq 0 && "$remaining_containers" -eq 0 && "$remaining_networks" -eq 0 ]]; then
    echo "BENIGN_BASELINE_STATUS=PASS"
    echo "[OK] Evidence retained at: $EVIDENCE"
  elif [[ "$RESULT" == BENIGN_BASELINE_FAIL ]]; then
    echo "BENIGN_BASELINE_STATUS=FAIL" >&2
    echo "[INFO] Evidence retained at: $EVIDENCE" >&2
  else
    echo "BENIGN_BASELINE_STATUS=RUN_INVALID" >&2
    echo "[INFO] Evidence retained at: $EVIDENCE" >&2
  fi
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

mkdir -p "$PROBE_GROUND" "$ORCHESTRATION" "$POLICY" "$INOUT"
: > "$MANIFEST"
: > "$NAMES"
: > "$RUNTIME_NAMES"
printf 'timestamp_utc,phase,container,state_exit_code\n' > "$LIVENESS"
trap cleanup EXIT
trap 'exit 130' INT TERM

record run_id "$RUN_ID"
record started_utc "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
record project "$PROJECT"
record phase "$PHASE"
record baseline_timeout_seconds "$BASELINE_TIMEOUT"
record probe_readiness_timeout_seconds "$PROBE_READINESS_TIMEOUT"
record acceptance_timeout_seconds "$ACCEPTANCE_TIMEOUT"
record event_injection disabled
record command_name SAMPLE_NOOP_CC
record command_packet_hex 18fac000000100dc
record command_packet_sha256 722b8fe72fb18ee581c970ea92c100f435fa90ccccaf0a05bf3e8bee0c4d13bd
record maximum_command_transmissions 1
record expected_runtime_component_count 21
record expected_total_component_count 22
record simulator_launch_mode individual_pinned_headless_set
record hardware_simulator_count "${#HARDWARE_SIMS[@]}"
record truth_stream_dependency internal_read_only_sink
record truth_sink_policy_visibility none
record ground_evidence_directory immutable-ground
record policy_visible_evidence_directory policy-visible

for command in docker git awk shasum python3; do
  command -v "$command" >/dev/null 2>&1 || {
    echo "[ERROR] Missing command: $command" >&2
    exit 1
  }
done

docker info >/dev/null 2>&1 || {
  echo "[ERROR] Docker daemon is not reachable." >&2
  exit 1
}
docker image inspect "$IMAGE" >/dev/null 2>&1 || {
  echo "[ERROR] Pinned image is unavailable: $IMAGE" >&2
  exit 1
}

CONTRACT="$ROOT/configs/benign-baseline-contract.json"
PROBE_SCRIPT="$ROOT/scripts/benign_ground_probe.py"
NOS3_LOCK="$ROOT/artifacts/nos3-submodule-lock.txt"
FORTYTWO_LOCK="$ROOT/artifacts/fortytwo-lock.txt"
BUILD_LOCK="$ROOT/artifacts/nominal-build-lock.txt"
PREFLIGHT_LOCK="$ROOT/artifacts/nominal-runtime-preflight-lock.txt"
for file in "$CONTRACT" "$PROBE_SCRIPT" "$NOS3_LOCK" "$FORTYTWO_LOCK" "$BUILD_LOCK" "$PREFLIGHT_LOCK"; do
  [[ -f "$file" ]] || {
    echo "[ERROR] Missing required file: $file" >&2
    exit 1
  }
done

python3 -m json.tool "$CONTRACT" >/dev/null
python3 "$PROBE_SCRIPT" --self-test >/dev/null
python3 - "$CONTRACT" <<'PY'
import json
import sys

contract = json.load(open(sys.argv[1], encoding="utf-8"))
assert contract["event_injection_allowed"] is False
assert contract["command"]["name"] == "SAMPLE_NOOP_CC"
assert contract["command"]["maximum_transmissions_per_run"] == 1
assert contract["command"]["expected_packet_hex"] == "18fac000000100dc"
assert contract["command"]["expected_packet_sha256"] == "722b8fe72fb18ee581c970ea92c100f435fa90ccccaf0a05bf3e8bee0c4d13bd"
assert contract["assertions"]["acceptance_timeout_seconds"] == 30
assert contract["transport"]["host_ports_allowed"] is False
assert contract["transport"]["docker_socket_mount_allowed"] is False
assert contract["transport"]["external_egress_allowed"] is False
PY

[[ "$(value "$FORTYTWO_LOCK" fortytwo_build_status)" == PASS ]] || {
  echo "[ERROR] 42 lock is not PASS." >&2
  exit 1
}
[[ "$(value "$BUILD_LOCK" build_status)" == PASS ]] || {
  echo "[ERROR] NOS3 build lock is not PASS." >&2
  exit 1
}
[[ "$(value "$PREFLIGHT_LOCK" runtime_preflight_status)" == PASS ]] || {
  echo "[ERROR] Runtime preflight lock is not PASS." >&2
  exit 1
}
[[ "$(git -C "$NOS3" rev-parse HEAD)" == "$NOS3_COMMIT" ]] || {
  echo "[ERROR] NOS3 commit mismatch." >&2
  exit 1
}
[[ "$(git -C "$FORTYTWO" rev-parse HEAD)" == "$FORTYTWO_COMMIT" ]] || {
  echo "[ERROR] 42 commit mismatch." >&2
  exit 1
}
[[ -z "$(git -C "$NOS3" status --short)" ]] || {
  echo "[ERROR] NOS3 worktree is not clean." >&2
  exit 1
}
[[ -z "$(git -C "$FORTYTWO" status --short)" ]] || {
  echo "[ERROR] 42 worktree is not clean." >&2
  exit 1
}

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
  [[ -f "$file" ]] || {
    echo "[ERROR] Missing runtime artifact: $file" >&2
    exit 1
  }
done

grep -Eq 'fortytwo[[:space:]]+9999[[:space:]]*![[:space:]]*Server Host Name, Port' \
  "$NOS3/cfg/build/InOut/Inp_IPC.txt" || {
  echo "[ERROR] Pinned 42 IPC configuration does not expose truth port 9999." >&2
  exit 1
}

[[ -z "$(docker ps -aq --filter "label=research.project=$PROJECT")" ]] || {
  echo "[ERROR] Existing project runtime containers found; run scripts/cleanup_nominal_runtime.sh." >&2
  exit 1
}
[[ -z "$(docker network ls -q --filter "label=research.project=$PROJECT")" ]] || {
  echo "[ERROR] Existing project runtime networks found; run scripts/cleanup_nominal_runtime.sh." >&2
  exit 1
}

cp -R "$NOS3/cfg/build/InOut/." "$INOUT/"
python3 - "$INOUT/Inp_Sim.txt" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
lines = path.read_text(encoding="utf-8").splitlines()
for index, line in enumerate(lines):
    if "Graphics Front End?" in line:
        comment = line.split("!", 1)[1] if "!" in line else " Graphics Front End?"
        lines[index] = f"FALSE                           !{comment}"
        break
else:
    raise SystemExit("Graphics Front End setting not found")
path.write_text("\n".join(lines) + "\n", encoding="utf-8")
PY

grep -q '^FALSE[[:space:]]*![[:space:]]*Graphics Front End?' "$INOUT/Inp_Sim.txt" || {
  echo "[ERROR] 42 runtime configuration is not headless." >&2
  exit 1
}

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
  [[ "$runtime" == true ]] && echo "$name" >> "$RUNTIME_NAMES"
}

wait_for_log_marker() {
  local name="$1" marker="$2" timeout_seconds="$3" manifest_key="$4"
  local attempt state logs
  for ((attempt=1; attempt<=timeout_seconds; attempt++)); do
    state="$(docker inspect "$name" --format '{{.State.Status}}' 2>/dev/null || echo missing)"
    if [[ "$state" != running ]]; then
      echo "[ERROR] $name stopped before readiness marker '$marker' was observed." >&2
      return 1
    fi
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
    if [[ "$state" != running ]]; then
      echo "[ERROR] $name stopped before TCP port $port became ready." >&2
      return 1
    fi
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
  local phase="$1" failed=0 name state code networks
  while IFS= read -r name; do
    state="$(docker inspect "$name" --format '{{.State.Status}}' 2>/dev/null || echo missing)"
    code="$(docker inspect "$name" --format '{{.State.ExitCode}}' 2>/dev/null || echo unknown)"
    printf '%s,%s,%s,%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$phase" "$name" "$state:$code" >> "$LIVENESS"
    [[ "$state" == running ]] || {
      echo "[ERROR] $name is $state (exit $code)." >&2
      failed=1
    }
    networks="$(docker inspect "$name" --format '{{range $k,$v := .NetworkSettings.Networks}}{{$k}}{{end}}' 2>/dev/null || true)"
    [[ "$networks" == "$NETWORK" ]] || {
      echo "[ERROR] Unexpected network for $name: $networks" >&2
      failed=1
    }
    [[ -z "$(docker port "$name" 2>/dev/null)" ]] || {
      echo "[ERROR] Host port published by $name." >&2
      failed=1
    }
    docker inspect "$name" --format '{{range .Mounts}}{{println .Source .Destination}}{{end}}' 2>/dev/null | \
      grep -q '/var/run/docker.sock' && {
      echo "[ERROR] Docker socket mounted in $name." >&2
      failed=1
    }
  done < "$RUNTIME_NAMES"
  return "$failed"
}

start ground-probe ground-probe false \
  --mount "type=bind,source=$PROBE_SCRIPT,target=/probe/benign_ground_probe.py,readonly" \
  --mount "type=bind,source=$PROBE_GROUND,target=/evidence-ground" \
  --mount "type=bind,source=$POLICY,target=/evidence-policy" \
  "$IMAGE" python3 -u /probe/benign_ground_probe.py \
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

start engine nos-engine-server true \
  --interactive --tty --network-alias sc01-nos-engine-server \
  --mount "type=bind,source=$NOS3,target=/work/nos3" --workdir /work/nos3/sims/build/bin \
  "$IMAGE" /usr/bin/nos_engine_server_standalone -f nos_engine_server_config.json
sleep 2
start time nos-time-driver true \
  --mount "type=bind,source=$NOS3,target=/work/nos3" --workdir /work/nos3/sims/build/bin \
  "$IMAGE" ./nos3-single-simulator -f nos3-simulator.xml time
start fortytwo fortytwo true \
  --mount "type=bind,source=$FORTYTWO,target=/work/fortytwo,readonly" \
  --mount "type=bind,source=$INOUT,target=$FORTYTWO_INOUT_CONTAINER" --workdir /work/fortytwo \
  "$IMAGE" ./42 "$FORTYTWO_INOUT_CONTAINER"
start truth-sink truth-sink true \
  --env TRUTH_HOST=fortytwo --env TRUTH_PORT=9999 --env CONNECT_TIMEOUT_SECONDS=75 \
  "$IMAGE" python3 -u -c '
import os
import socket
import sys
import time

host = os.environ["TRUTH_HOST"]
port = int(os.environ["TRUTH_PORT"])
deadline = time.monotonic() + int(os.environ["CONNECT_TIMEOUT_SECONDS"])
last_error = None
while True:
    try:
        stream = socket.create_connection((host, port), timeout=1.0)
        stream.settimeout(None)
        print(f"TRUTH_SINK_CONNECTED host={host} port={port}", flush=True)
        break
    except OSError as exc:
        last_error = exc
        if time.monotonic() >= deadline:
            print(f"TRUTH_SINK_CONNECT_FAILED host={host} port={port} error={last_error}", file=sys.stderr, flush=True)
            raise SystemExit(2)
        time.sleep(0.5)
received = 0
last_report = time.monotonic()
while True:
    payload = stream.recv(65536)
    if not payload:
        print(f"TRUTH_SINK_STREAM_CLOSED bytes={received}", file=sys.stderr, flush=True)
        raise SystemExit(3)
    received += len(payload)
    now = time.monotonic()
    if now - last_report >= 5.0:
        print(f"TRUTH_SINK_BYTES={received}", flush=True)
        last_report = now
'

for sim in "${HARDWARE_SIMS[@]}"; do
  if [[ "$sim" == generic-radio-sim ]]; then
    start "$sim" radio-sim true \
      --network-alias generic-radio-sim \
      --env TCP_GROUND=1 --env MULTI_GDS=0 \
      --mount "type=bind,source=$NOS3,target=/work/nos3" --workdir /work/nos3/sims/build/bin \
      "$IMAGE" ./nos3-single-simulator -f nos3-simulator.xml "$sim"
  else
    start "$sim" "$sim" true \
      --mount "type=bind,source=$NOS3,target=/work/nos3" --workdir /work/nos3/sims/build/bin \
      "$IMAGE" ./nos3-single-simulator -f nos3-simulator.xml "$sim"
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
  --mount "type=bind,source=$NOS3,target=/work/nos3" --workdir /work/nos3/sims/build/bin \
  "$IMAGE" ./nos3-sim-cmdbus-bridge -f nos3-simulator.xml
start cfs nos-fsw true \
  --mount "type=bind,source=$NOS3,target=/work/nos3" \
  --env USER=nos3 --env LD_LIBRARY_PATH=/work/nos3/fsw/build/exe/cpu1:/usr/lib:/usr/local/lib \
  --workdir /work/nos3/fsw/build/exe/cpu1 --sysctl fs.mqueue.msg_max=10000 \
  --ulimit rtprio=99 --cap-add SYS_NICE \
  "$IMAGE" bash -lc 'exec ./core-cpu1 -R PO'

record containers_started_utc "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
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
  if [[ "$probe_state" == exited ]]; then
    break
  fi
done

probe_state="$(docker inspect "$probe_name" --format '{{.State.Status}}' 2>/dev/null || echo missing)"
probe_code="$(docker inspect "$probe_name" --format '{{.State.ExitCode}}' 2>/dev/null || echo unknown)"
record ground_probe_exit_state "$probe_state:$probe_code"

if [[ "$probe_state" != exited ]]; then
  echo "[ERROR] Ground probe did not finish within ${BASELINE_TIMEOUT}s." >&2
  exit 3
fi

PROBE_RESULT="$PROBE_GROUND/probe-result.json"
[[ -f "$PROBE_RESULT" ]] || {
  echo "[ERROR] Ground probe result is missing." >&2
  exit 3
}
probe_classification="$(python3 - "$PROBE_RESULT" <<'PY'
import json
import sys
print(json.load(open(sys.argv[1], encoding="utf-8"))["classification"])
PY
)"
record ground_probe_classification "$probe_classification"
record ground_probe_result_sha256 "$(shasum -a 256 "$PROBE_RESULT" | awk '{print $1}')"

case "$probe_classification:$probe_code" in
  BENIGN_BASELINE_PASS:0)
    RESULT="BENIGN_BASELINE_PASS"
    record baseline_status PASS
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
echo "[OK] Runtime isolation and evidence-separation controls remained active."
