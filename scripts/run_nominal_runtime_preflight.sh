#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NOS3="$ROOT/external/nos3"
FORTYTWO="$ROOT/external/fortytwo"
IMAGE="ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"
NOS3_COMMIT="5a3bdee6be9a2c67fdf994ae6db56d5c60395302"
FORTYTWO_COMMIT="eda252bf31f27850e867e698cfdd963e143ead1f"
PROJECT="mission-aware-satellite-cyber-recovery"
PHASE="wp4-nominal-runtime-preflight"
DURATION="${DURATION_SECONDS:-60}"
GRACE="${STARTUP_GRACE_SECONDS:-20}"
RUN_ID="${RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)}"
SAFE_ID="$(printf '%s' "$RUN_ID" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9_.-' '-')"
NETWORK="mascr-$SAFE_ID"
PREFIX="mascr-$SAFE_ID"
EVIDENCE="$ROOT/artifacts/runtime/$RUN_ID"
INOUT="$EVIDENCE/fortytwo/NOS3InOut"
FORTYTWO_INOUT_CONTAINER="/work/fortytwo-inout"
MANIFEST="$EVIDENCE/runtime-manifest.txt"
NAMES="$EVIDENCE/container-names.txt"
LIVENESS="$EVIDENCE/liveness.csv"
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
  docker inspect "$name" > "$EVIDENCE/inspect-$name.json" 2>/dev/null || true
  docker logs --timestamps "$name" > "$EVIDENCE/$name.log" 2>&1 || true
}

cleanup() {
  local rc=$?
  set +e
  if [[ -f "$NAMES" ]]; then
    while IFS= read -r name; do
      [[ -n "$name" ]] && capture "$name"
    done < "$NAMES"
  fi
  docker network inspect "$NETWORK" > "$EVIDENCE/network-final.json" 2>/dev/null || true
  docker ps -a --no-trunc --format '{{json .}}' > "$EVIDENCE/docker-ps-final.jsonl" 2>/dev/null || true
  ids="$(docker ps -aq --filter "label=research.project=$PROJECT" --filter "label=research.run_id=$RUN_ID")"
  [[ -z "$ids" ]] || docker rm -f $ids >/dev/null 2>&1
  docker network rm "$NETWORK" >/dev/null 2>&1 || true
  record cleanup_completed_utc "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  record terminal_classification "$RESULT"
  record exit_code "$rc"
  if [[ "$RESULT" == RUNTIME_PREFLIGHT_PASS && "$rc" -eq 0 ]]; then
    echo "NOMINAL_RUNTIME_PREFLIGHT_STATUS=PASS"
  else
    echo "NOMINAL_RUNTIME_PREFLIGHT_STATUS=FAIL" >&2
    echo "[INFO] Evidence retained at: $EVIDENCE" >&2
  fi
}

for number in "$DURATION" "$GRACE"; do
  [[ "$number" =~ ^[0-9]+$ ]] || { echo "[ERROR] Runtime values must be integers." >&2; exit 1; }
done
(( DURATION >= 30 && DURATION <= 300 )) || { echo "[ERROR] DURATION_SECONDS must be 30-300." >&2; exit 1; }
(( GRACE >= 5 && GRACE <= 60 )) || { echo "[ERROR] STARTUP_GRACE_SECONDS must be 5-60." >&2; exit 1; }

mkdir -p "$EVIDENCE" "$INOUT"
: > "$MANIFEST"
: > "$NAMES"
printf 'timestamp_utc,phase,container,state_exit_code\n' > "$LIVENESS"
trap cleanup EXIT
trap 'exit 130' INT TERM

record run_id "$RUN_ID"
record started_utc "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
record project "$PROJECT"
record phase "$PHASE"
record duration_seconds "$DURATION"
record startup_grace_seconds "$GRACE"
record event_injection disabled
record simulator_launch_mode individual_pinned_headless_set
record hardware_simulator_count "${#HARDWARE_SIMS[@]}"
record expected_runtime_component_count 21
record engine_stdin_mode interactive_tty
record terminal_env xterm
record truth42sim_launch omitted_requires_ground_software
record truth_stream_dependency internal_read_only_sink
record truth_sink_port 9999
record truth_sink_capture_mode byte_count_only
record truth_sink_policy_visibility none
record camera_simulator_launch omitted_outside_frozen_pilot
record radio_network_alias radio-sim
record radio_ground_transport tcp
record cryptolib_transport tcp
record cryptolib_stdin_mode interactive
record cryptolib_gsw_mode local_loopback_no_ground_software

for command in docker git awk shasum python3; do
  command -v "$command" >/dev/null 2>&1 || { echo "[ERROR] Missing command: $command" >&2; exit 1; }
done
docker info >/dev/null 2>&1 || { echo "[ERROR] Docker daemon is not reachable." >&2; exit 1; }
docker image inspect "$IMAGE" >/dev/null 2>&1 || { echo "[ERROR] Pinned image is unavailable: $IMAGE" >&2; exit 1; }

NOS3_LOCK="$ROOT/artifacts/nos3-submodule-lock.txt"
FORTYTWO_LOCK="$ROOT/artifacts/fortytwo-lock.txt"
BUILD_LOCK="$ROOT/artifacts/nominal-build-lock.txt"
for file in "$NOS3_LOCK" "$FORTYTWO_LOCK" "$BUILD_LOCK"; do
  [[ -f "$file" ]] || { echo "[ERROR] Missing lock: $file" >&2; exit 1; }
done
[[ "$(value "$FORTYTWO_LOCK" fortytwo_build_status)" == PASS ]] || { echo "[ERROR] 42 lock is not PASS." >&2; exit 1; }
[[ "$(value "$BUILD_LOCK" build_status)" == PASS ]] || { echo "[ERROR] NOS3 build lock is not PASS." >&2; exit 1; }
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

grep -Eq 'fortytwo[[:space:]]+9999[[:space:]]*![[:space:]]*Server Host Name, Port' \
  "$NOS3/cfg/build/InOut/Inp_IPC.txt" || {
  echo "[ERROR] Pinned 42 IPC configuration does not expose the expected truth stream on port 9999." >&2
  exit 1
}

FORTYTWO_BLOCKING_IPC_SEQUENCE="$(
  python3 - "$NOS3/cfg/build/InOut/Inp_IPC.txt" <<'PY_IPC'
from pathlib import Path
import sys

lines = Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()
count = int(lines[1].split()[0])
ports = []
idx = 2

for _ in range(count):
    idx += 1
    mode = lines[idx].split()[0]
    idx += 1
    idx += 1
    role = lines[idx].split()[0]
    idx += 1
    port = int(lines[idx].split("!", 1)[0].split()[1])
    idx += 1
    idx += 1
    idx += 1
    prefix_count = int(lines[idx].split()[0])
    idx += 1 + prefix_count

    if mode in {"TX", "RX", "TXRX"} and role == "SERVER":
        ports.append(port)

print(",".join(str(port) for port in ports))
PY_IPC
)"

EXPECTED_FORTYTWO_BLOCKING_IPC_SEQUENCE="4278,4277,4378,4377,4478,4477,4279,4280,4245,4227,4234,9999,4284,4281,4282,4283,4286"

[[ "$FORTYTWO_BLOCKING_IPC_SEQUENCE" == "$EXPECTED_FORTYTWO_BLOCKING_IPC_SEQUENCE" ]] || {
  echo "[ERROR] Pinned 42 blocking IPC sequence does not match the R-024 startup contract." >&2
  echo "[ERROR] observed=$FORTYTWO_BLOCKING_IPC_SEQUENCE" >&2
  echo "[ERROR] expected=$EXPECTED_FORTYTWO_BLOCKING_IPC_SEQUENCE" >&2
  exit 1
}

record fortytwo_blocking_ipc_sequence "$FORTYTWO_BLOCKING_IPC_SEQUENCE"
record fortytwo_blocking_ipc_sequence_verified true

[[ -z "$(docker ps -aq --filter "label=research.project=$PROJECT")" ]] || {
  echo "[ERROR] Existing project runtime containers found; run scripts/cleanup_nominal_runtime.sh." >&2
  exit 1
}

docker ps -a --no-trunc --format '{{json .}}' > "$EVIDENCE/docker-ps-before.jsonl"
docker network ls --no-trunc --format '{{json .}}' > "$EVIDENCE/docker-networks-before.jsonl"
cp -R "$NOS3/cfg/build/InOut/." "$INOUT/"
python3 - "$INOUT/Inp_Sim.txt" <<'PY'
from pathlib import Path
import sys
p = Path(sys.argv[1])
lines = p.read_text(encoding="utf-8").splitlines()
for i, line in enumerate(lines):
    if "Graphics Front End?" in line:
        comment = line.split("!", 1)[1] if "!" in line else " Graphics Front End?"
        lines[i] = f"FALSE                           !{comment}"
        break
else:
    raise SystemExit("Graphics Front End setting not found")
p.write_text("\n".join(lines) + "\n", encoding="utf-8")
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
record build_lock_sha256 "$(shasum -a 256 "$BUILD_LOCK" | awk '{print $1}')"
record runtime_inp_sim_sha256 "$(shasum -a 256 "$INOUT/Inp_Sim.txt" | awk '{print $1}')"
record runtime_inp_ipc_sha256 "$(shasum -a 256 "$INOUT/Inp_IPC.txt" | awk '{print $1}')"
record fortytwo_inout_container "$FORTYTWO_INOUT_CONTAINER"

docker network create --driver bridge --internal \
  --label "research.project=$PROJECT" \
  --label "research.phase=$PHASE" \
  --label "research.run_id=$RUN_ID" \
  "$NETWORK" >/dev/null
[[ "$(docker network inspect "$NETWORK" --format '{{.Internal}}')" == true ]] || {
  echo "[ERROR] Runtime network is not internal." >&2
  exit 1
}
docker network inspect "$NETWORK" > "$EVIDENCE/network-created.json"

start() {
  local logical="$1" alias="$2"
  shift 2
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

check() {
  local phase="$1" failed=0
  while IFS= read -r name; do
    state="$(docker inspect "$name" --format '{{.State.Status}}' 2>/dev/null || echo missing)"
    code="$(docker inspect "$name" --format '{{.State.ExitCode}}' 2>/dev/null || echo unknown)"
    printf '%s,%s,%s,%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$phase" "$name" "$state:$code" >> "$LIVENESS"
    [[ "$state" == running ]] || { echo "[ERROR] $name is $state (exit $code)." >&2; failed=1; }
    networks="$(docker inspect "$name" --format '{{range $k,$v := .NetworkSettings.Networks}}{{$k}}{{end}}')"
    [[ "$networks" == "$NETWORK" ]] || { echo "[ERROR] Unexpected network for $name: $networks" >&2; failed=1; }
    [[ -z "$(docker port "$name")" ]] || { echo "[ERROR] Host port published by $name." >&2; failed=1; }
    docker inspect "$name" --format '{{range .Mounts}}{{println .Source .Destination}}{{end}}' | \
      grep -q '/var/run/docker.sock' && { echo "[ERROR] Docker socket mounted in $name." >&2; failed=1; }
  done < "$NAMES"
  return "$failed"
}

start_hardware_sim() {
  local sim="$1"

  if [[ "$sim" == "generic-radio-sim" ]]; then
    start "$sim" radio-sim \
      --network-alias generic-radio-sim \
      --env TCP_GROUND=1 --env MULTI_GDS=0 \
      --mount "type=bind,source=$NOS3,target=/work/nos3" --workdir /work/nos3/sims/build/bin \
      "$IMAGE" ./nos3-single-simulator -f nos3-simulator.xml "$sim"
  else
    start "$sim" "$sim" \
      --mount "type=bind,source=$NOS3,target=/work/nos3" --workdir /work/nos3/sims/build/bin \
      "$IMAGE" ./nos3-single-simulator -f nos3-simulator.xml "$sim"
  fi
}

start engine nos-engine-server \
  --interactive --tty --network-alias sc01-nos-engine-server \
  --mount "type=bind,source=$NOS3,target=/work/nos3" --workdir /work/nos3/sims/build/bin \
  "$IMAGE" /usr/bin/nos_engine_server_standalone -f nos_engine_server_config.json
sleep 2
start time nos-time-driver \
  --mount "type=bind,source=$NOS3,target=/work/nos3" --workdir /work/nos3/sims/build/bin \
  "$IMAGE" ./nos3-single-simulator -f nos3-simulator.xml time
start fortytwo fortytwo \
  --mount "type=bind,source=$FORTYTWO,target=/work/fortytwo,readonly" \
  --mount "type=bind,source=$INOUT,target=$FORTYTWO_INOUT_CONTAINER" --workdir /work/fortytwo \
  "$IMAGE" ./42 "$FORTYTWO_INOUT_CONTAINER"

# R-024: Fortytwo initializes SERVER sockets sequentially and blocks in
# accept() on each TX/RX/TXRX entry until that entry's client connects.
# Progress the frozen IPC chain by launching only the owner of the current
# blocking listener. Reaching the next listener proves the prior dependency
# (or reaction-wheel command/telemetry pair) completed.

wait_for_tcp_listener "$PREFIX-fortytwo" 4278 30 fortytwo_ipc_4278_listener
start_hardware_sim generic-reactionwheel-sim0
wait_for_tcp_listener "$PREFIX-fortytwo" 4378 30 fortytwo_after_rw0_pair_4378_listener

start_hardware_sim generic-reactionwheel-sim1
wait_for_tcp_listener "$PREFIX-fortytwo" 4478 30 fortytwo_after_rw1_pair_4478_listener

start_hardware_sim generic-reactionwheel-sim2
wait_for_tcp_listener "$PREFIX-fortytwo" 4279 30 fortytwo_after_rw2_pair_4279_listener

start_hardware_sim generic-torquer-sim
wait_for_tcp_listener "$PREFIX-fortytwo" 4280 30 fortytwo_after_torquer_4280_listener

start_hardware_sim generic-thruster-sim
wait_for_tcp_listener "$PREFIX-fortytwo" 4245 30 fortytwo_after_thruster_4245_listener

start_hardware_sim gps
wait_for_tcp_listener "$PREFIX-fortytwo" 4227 30 fortytwo_after_gps_4227_listener

start_hardware_sim generic-css-sim
wait_for_tcp_listener "$PREFIX-fortytwo" 4234 30 fortytwo_after_css_4234_listener

start_hardware_sim generic-mag-sim
wait_for_tcp_listener "$PREFIX-fortytwo" 9999 30 fortytwo_after_mag_9999_listener

start truth-sink truth-sink \
  --env TRUTH_HOST=fortytwo --env TRUTH_PORT=9999 --env CONNECT_TIMEOUT_SECONDS=30 \
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
wait_for_log_marker "$PREFIX-truth-sink" TRUTH_SINK_CONNECTED 30 truth_sink_connection
wait_for_tcp_listener "$PREFIX-fortytwo" 4284 30 fortytwo_after_truth_4284_listener

start_hardware_sim generic-fss-sim
wait_for_tcp_listener "$PREFIX-fortytwo" 4281 30 fortytwo_after_fss_4281_listener

start_hardware_sim generic-imu-sim
wait_for_tcp_listener "$PREFIX-fortytwo" 4282 30 fortytwo_after_imu_4282_listener

start_hardware_sim generic-star-tracker-sim
wait_for_tcp_listener "$PREFIX-fortytwo" 4283 30 fortytwo_after_star_tracker_4283_listener

start_hardware_sim generic-eps-sim
wait_for_tcp_listener "$PREFIX-fortytwo" 4286 30 fortytwo_after_eps_4286_listener

start_hardware_sim generic-radio-sim
start_hardware_sim sample-sim
wait_for_tcp_listener "$PREFIX-generic-radio-sim" 8010 45 radio_tcp_8010_listener
start bridge nos-sim-bridge \
  --mount "type=bind,source=$NOS3,target=/work/nos3" --workdir /work/nos3/sims/build/bin \
  "$IMAGE" ./nos3-sim-cmdbus-bridge -f nos3-simulator.xml
start cryptolib cryptolib \
  --interactive \
  --env STANDALONE_TCP=1 --env CRYPTO_HOST=0.0.0.0 --env GSWALIAS=127.0.0.1 \
  --mount "type=bind,source=$NOS3,target=/work/nos3" --workdir /work/nos3/gsw/build \
  "$IMAGE" ./support/standalone
start cfs nos-fsw \
  --mount "type=bind,source=$NOS3,target=/work/nos3" \
  --env USER=nos3 --env LD_LIBRARY_PATH=/work/nos3/fsw/build/exe/cpu1:/usr/lib:/usr/local/lib \
  --workdir /work/nos3/fsw/build/exe/cpu1 --sysctl fs.mqueue.msg_max=10000 \
  --ulimit rtprio=99 --cap-add SYS_NICE \
  "$IMAGE" bash -lc 'exec ./core-cpu1 -R PO'

record containers_started_utc "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
sleep "$GRACE"

check startup
elapsed=0
while (( elapsed < DURATION )); do
  sleep 5
  elapsed=$((elapsed + 5))
  check "observation-$elapsed"
done

while IFS= read -r name; do
  capture "$name"
  record "log_bytes_$name" "$(wc -c < "$EVIDENCE/$name.log" | tr -d ' ')"
done < "$NAMES"
docker ps --filter "label=research.project=$PROJECT" --filter "label=research.run_id=$RUN_ID" \
  --no-trunc --format '{{json .}}' > "$EVIDENCE/docker-ps-running.jsonl"

RESULT="RUNTIME_PREFLIGHT_PASS"
record observation_completed_utc "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
record runtime_preflight_status PASS

echo "[OK] Runtime remained live on the project internal network."
echo "[OK] No host ports or Docker-socket mounts were detected."
echo "[OK] Evidence retained at: $EVIDENCE"
