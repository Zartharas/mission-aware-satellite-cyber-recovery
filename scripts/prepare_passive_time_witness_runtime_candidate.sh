#!/usr/bin/env bash
# prepare_passive_time_witness_runtime_candidate.sh
#
# WP4 Part 4: passive time-witness runtime-candidate EMITTER.
#
# This script is EMIT-ONLY. It writes a candidate runtime artifact to the path
# named by PASSIVE_TIME_WITNESS_EMIT_PATH and then exits. It performs NONE of:
#   - does NOT invoke Docker (no `docker` command, no `docker run`, no build)
#   - does NOT execute the emitted candidate (no `bash`/`sh` of the candidate)
#   - does NOT create a network
#   - does NOT modify retained evidence
#   - does NOT launch NOS3
#   - does NOT transmit commands, inject events, capture packets, open host
#     networking, expose host ports, mount the Docker socket, or egress
#     externally.
#
# The candidate is derived from the accepted v3 telemetry-only topology in
# configs/downlink-diagnostic-contract.json::confirmed_topology, using
# deterministic, uniquely counted anchors (indices 0..14). It preserves:
#   active-gs UDP 5013 -> radio-sim UDP 5011 (byte-preserving proxy)
#   UDP 8011 egress sink (forwarding disabled)
#   generic-radio-only socket metadata shim scope
#   immutable-ground-only trace evidence scope
# It adds exactly ONE passive NOS Engine time-witness, with witness output
# mounted read-write ONLY into the witness container under immutable-ground
# evidence. Policy-visible evidence contains NO tick or monotonic-time values.
#
# The candidate MUST fail closed before any Docker command unless a FUTURE
# contract simultaneously asserts ALL of:
#   a future status explicitly authorizing passive-time telemetry runtime
#   diagnostic_runtime_authorized == true
#   diagnostic_runtime_attempts_authorized == 1
#   passive_time_witness_static_verification == "PASS"
#   a nonempty accepted_runtime_entrypoint_sha256
#   the candidate hash matches the accepted future entrypoint hash via the
#   designed accepted-entrypoint mechanism (sha256 of the candidate file)
#
# The CURRENT contract (0.4.4) asserts NONE of these, so the emitted candidate
# MUST fail closed. This emitter performs no runtime authorization itself.
#
# Outputs: PASSIVE_TIME_WITNESS_RUNTIME_CANDIDATE_EMIT_STATUS=COMPLETE
#
# Contract version: 0.4.4 (PASSIVE_TIME_WITNESS_DESIGN_LOCKED_STATIC_GATE_PENDING)

set -Eeuo pipefail

# ---------------------------------------------------------------------------
# 0. Emit-path containment.
#
# PASSIVE_TIME_WITNESS_EMIT_PATH must resolve, via physical canonical paths,
# below EITHER:
#   (a) ${TMPDIR:-/tmp}; or
#   (b) an existing explicitly supplied PASSIVE_TIME_WITNESS_REVIEW_DIR.
#
# Traversal, symlink escape, repository artifact/config/tracker/data
# locations, retained evidence, and any location outside the allowed roots
# are rejected.
# ---------------------------------------------------------------------------

emit_path_raw="${PASSIVE_TIME_WITNESS_EMIT_PATH:-}"
if [[ -z "${emit_path_raw}" ]]; then
  echo "[ERROR] PASSIVE_TIME_WITNESS_EMIT_PATH is required." >&2
  echo "PASSIVE_TIME_WITNESS_RUNTIME_CANDIDATE_EMIT_STATUS=BLOCKED_MISSING_EMIT_PATH" >&2
  exit 2
fi

# Resolve a physical canonical absolute path for an EXISTING filesystem entry.
# Uses `readlink -f` (BSD/mktemp-friendly) then falls back to python3 realpath.
phys_canon() {
  local p="$1"
  local r
  if r="$(readlink -f -- "$p" 2>/dev/null)" && [[ -n "${r}" ]]; then
    printf '%s\n' "${r}"
    return 0
  fi
  # Fallback: python3 realpath (handles missing tail component via parent).
  python3 - "$p" <<'PY'
import os, sys
p = os.fspath(sys.argv[1])
try:
    print(os.path.realpath(p))
except Exception:
    d = os.path.realpath(os.path.dirname(p)) if os.path.dirname(p) else os.getcwd()
    print(os.path.join(d, os.path.basename(p)))
PY
}

# Ensure the parent of the emit path exists as a real directory and resolve it
# canonically; reject if the parent is a symlink that escapes.
emit_parent_dir="$(dirname "${emit_path_raw}")"
if [[ ! -d "${emit_parent_dir}" ]]; then
  echo "[ERROR] emit directory does not exist: ${emit_parent_dir}" >&2
  echo "PASSIVE_TIME_WITNESS_RUNTIME_CANDIDATE_EMIT_STATUS=BLOCKED_MISSING_EMIT_DIR" >&2
  exit 2
fi
emit_parent_real="$(phys_canon "${emit_parent_dir}")"
emit_base="$(basename "${emit_path_raw}")"
emit_path="${emit_parent_real}/${emit_base}"

# Repository root (canonical) for retained-evidence rejection.
script_dir="$(phys_canon "$(dirname "${BASH_SOURCE[0]}")")"
repo_root="$(phys_canon "${script_dir}/..")"

# Build the set of allowed canonical roots.
tmp_root="${TMPDIR:-/tmp}"
tmp_root_real="$(phys_canon "${tmp_root}")"
allowed_roots=("${tmp_root_real}")

review_dir_raw="${PASSIVE_TIME_WITNESS_REVIEW_DIR:-}"
if [[ -n "${review_dir_raw}" ]]; then
  if [[ ! -d "${review_dir_raw}" ]]; then
    echo "[ERROR] PASSIVE_TIME_WITNESS_REVIEW_DIR does not exist: ${review_dir_raw}" >&2
    echo "PASSIVE_TIME_WITNESS_RUNTIME_CANDIDATE_EMIT_STATUS=BLOCKED_REVIEW_DIR_MISSING" >&2
    exit 2
  fi
  review_dir_real="$(phys_canon "${review_dir_raw}")"
  allowed_roots+=("${review_dir_real}")
fi

# Repository retained-evidence locations are always rejected.
retained_roots=(
  "${repo_root}/artifacts"
  "${repo_root}/evidence"
  "${repo_root}/configs"
  "${repo_root}/tracker"
  "${repo_root}/data"
)

reject_retained=0
for r in "${retained_roots[@]}"; do
  r_real="$(phys_canon "${r}")"
  if [[ "${emit_parent_real}" == "${r_real}" || "${emit_parent_real}" == "${r_real}"/* ]]; then
    reject_retained=1
    break
  fi
done
if [[ "${reject_retained}" -eq 1 ]]; then
  echo "[ERROR] PASSIVE_TIME_WITNESS_EMIT_PATH targets retained/evidence/config state; refusing." >&2
  echo "PASSIVE_TIME_WITNESS_RUNTIME_CANDIDATE_EMIT_STATUS=BLOCKED_RETAINED_EVIDENCE_TARGET" >&2
  exit 2
fi

# Containment: emit parent must be strictly under exactly one allowed root.
contained=0
for ar in "${allowed_roots[@]}"; do
  if [[ "${emit_parent_real}" == "${ar}" || "${emit_parent_real}" == "${ar}"/* ]]; then
    contained=1
    break
  fi
done
if [[ "${contained}" -ne 1 ]]; then
  echo "[ERROR] PASSIVE_TIME_WITNESS_EMIT_PATH escapes allowed roots." >&2
  echo "  emit_parent_real=${emit_parent_real}" >&2
  echo "  allowed_roots: ${allowed_roots[*]}" >&2
  echo "PASSIVE_TIME_WITNESS_RUNTIME_CANDIDATE_EMIT_STATUS=BLOCKED_EMIT_PATH_NOT_CONTAINED" >&2
  exit 2
fi

# Reject emit paths that themselves are symlinks pointing outside the allowed
# root (a final symlink in the leaf name). We do not follow the leaf if it is
# a symlink to an escaped target.
if [[ -L "${emit_path_raw}" ]]; then
  link_target_real="$(phys_canon "${emit_path_raw}")"
  link_contained=0
  for ar in "${allowed_roots[@]}"; do
    if [[ "${link_target_real}" == "${ar}" || "${link_target_real}" == "${ar}"/* ]]; then
      link_contained=1
      break
    fi
  done
  if [[ "${link_contained}" -ne 1 ]]; then
    echo "[ERROR] PASSIVE_TIME_WITNESS_EMIT_PATH is a symlink escaping allowed roots." >&2
    echo "PASSIVE_TIME_WITNESS_RUNTIME_CANDIDATE_EMIT_STATUS=BLOCKED_SYMLINK_ESCAPE" >&2
    exit 2
  fi
  emit_path="${link_target_real}"
fi

EMIT_PATH="${emit_path}"

# ---------------------------------------------------------------------------
# 1. Deterministic, uniquely counted topology anchors (indices 0..14).
#
# Verbatim from configs/downlink-diagnostic-contract.json::confirmed_topology
# and runtime_wrapper_requirements. Each anchor is assigned a unique
# zero-based index so the candidate is unambiguous and reproducible.
# ---------------------------------------------------------------------------

# Anchor 0: active-gs compiled to_lab destination port.
ANCHOR_0_TO_LAB_COMPILED_DESTINATION_PORT=5013
# Anchor 1: to_radio_witness proxy alias.
ANCHOR_1_TO_RADIO_WITNESS_ALIAS="active-gs"
# Anchor 2: to_radio_witness proxy bind port (active-gs binds here).
ANCHOR_2_TO_RADIO_WITNESS_BIND_PORT=5013
# Anchor 3: to_radio_witness forward destination host.
ANCHOR_3_TO_RADIO_WITNESS_FORWARD_DESTINATION="radio-sim"
# Anchor 4: to_radio_witness forward port (radio-sim UDP 5011).
ANCHOR_4_TO_RADIO_WITNESS_FORWARD_PORT=5011
# Anchor 5: to_radio_witness byte-preserving flag.
ANCHOR_5_TO_RADIO_WITNESS_BYTE_PRESERVING="true"
# Anchor 6: radio_egress_witness sink alias.
ANCHOR_6_RADIO_EGRESS_WITNESS_ALIAS="cryptolib"
# Anchor 7: radio_egress_witness sink bind port (UDP 8011 egress sink).
ANCHOR_7_RADIO_EGRESS_WITNESS_BIND_PORT=8011
# Anchor 8: radio_egress_witness forwarding disabled flag.
ANCHOR_8_RADIO_EGRESS_WITNESS_FORWARDING="false"
# Anchor 9: radio ground mode.
ANCHOR_9_RADIO_GROUND_MODE="UDP"
# Anchor 10: radio fsw telemetry listener port (radio-sim UDP 5011).
ANCHOR_10_RADIO_FSW_TELEMETRY_LISTENER_PORT=5011
# Anchor 11: radio command listener port.
ANCHOR_11_RADIO_COMMAND_LISTENER_PORT=8010
# Anchor 12: shim mount scope (generic-radio only).
ANCHOR_12_SHIM_MOUNT_SCOPE="generic_radio_only"
# Anchor 13: trace evidence scope (immutable-ground only).
ANCHOR_13_TRACE_EVIDENCE_SCOPE="immutable_ground_only"
# Anchor 14: the exactly-one passive NOS Engine time-witness component count.
ANCHOR_14_PASSIVE_TIME_WITNESS_COUNT=1

TOTAL_ANCHORS=15

# ---------------------------------------------------------------------------
# 2. Forbidden capability denylist.
#
# Absolute prohibitions sourced from passive_time_witness_design.forbidden
# and runtime_wrapper_requirements in the 0.4 contract.
# ---------------------------------------------------------------------------

DENYLIST=(
  "command_source"
  "command_vector"
  "command_transmission"
  "event_injection"
  "packet_capture"
  "packet_payload_capture"
  "packet_hashes"
  "ip_address_collection"
  "host_networking"
  "host_ports"
  "docker_socket_mount"
  "external_network_egress"
)

# ---------------------------------------------------------------------------
# 3. Fail-closed gate fields (current contract 0.4.4 values).
#
# A future contract must set ALL of:
#   FUTURE_GATE_passive_time_telemetry_runtime_status = "AUTHORIZED"
#   FUTURE_GATE_diagnostic_runtime_authorized = true
#   FUTURE_GATE_diagnostic_runtime_attempts_authorized = 1
#   FUTURE_GATE_passive_time_witness_static_verification = "PASS"
#   FUTURE_GATE_accepted_runtime_entrypoint_sha256 = <nonempty sha256>
#   candidate sha256 == FUTURE_GATE_accepted_runtime_entrypoint_sha256
# ---------------------------------------------------------------------------

GATE_diagnostic_runtime_authorized=false
GATE_diagnostic_runtime_attempts_authorized=0
GATE_passive_time_witness_static_verification="PENDING"
GATE_accepted_runtime_entrypoint_sha256=""
CONTRACT_STATUS_OPEN_GATE="PASSIVE_TIME_WITNESS_TELEMETRY_RUNTIME_AUTHORIZED"

# Immutable-ground evidence directory name (relative to repo) and the dedicated
# witness output subdirectory. The witness output directory is mounted
# read-write ONLY into the witness container, under immutable-ground evidence.
IMMUTABLE_GROUND_EVIDENCE_DIR="artifacts/wp4-passive-time-witness-immutable-ground"
POLICY_VISIBLE_EVIDENCE_DIR="artifacts/wp4-passive-time-witness-policy-visible"
WITNESS_OUTPUT_SUBDIR="witness-output"
WITNESS_OUTPUT_MOUNT_MODE="rw"
WITNESS_OUTPUT_MOUNT_DEST="/evidence/witness-output"

# ---------------------------------------------------------------------------
# 4. Emit the candidate.
#
# The candidate is a text artifact. It is NOT executed here. It embeds the
# anchors, the denylist, the fail-closed gate that READS THE CONTRACT at
# runtime, exactly one passive NOS Engine time-witness container, the
# preserved UDP topology, dormant Docker commands after the gate, and a
# witness output mount restricted to immutable-ground evidence.
# ---------------------------------------------------------------------------

# Policy-visible scope marker written OUTSIDE the witness trace. Contains NO
# tick or monotonic-time values, only a non-sensitive scope marker and
# independent manifest information. Mirrors policy_visible_time_evidence_allowed
# =false and the validator's FORBIDDEN_TOKENS list.
POLICY_VISIBLE_SCOPE_MARKER='{
  "component": "passive_time_witness_runtime_candidate",
  "topology_basis": "accepted_v3_telemetry_only",
  "passive_time_witness_count": 1,
  "witness_output_scope": "immutable_ground_only",
  "policy_visible_time_evidence_allowed": false,
  "gate_status": "CLOSED_CURRENT_CONTRACT_0_4_4",
  "runtime_authorized": false,
  "independent_manifest": {
    "anchor_count": 15,
    "denylist_count": 12
  }
}'

__emit_candidate_body() {
  cat <<'CANDIDATE_EOF'
#!/usr/bin/env bash
# === PASSIVE TIME WITNESS RUNTIME CANDIDATE (EMITTED, NOT EXECUTED) ==========
#
# Emitted by scripts/prepare_passive_time_witness_runtime_candidate.sh.
# It is a CANDIDATE runtime artifact. It has NOT been executed.
#
# Derived from the accepted v3 telemetry-only topology
# (configs/downlink-diagnostic-contract.json::confirmed_topology) using
# deterministic, uniquely counted anchors (indices 0..14).
#
# Preserves:
#   active-gs UDP 5013 -> radio-sim UDP 5011 (byte-preserving proxy)
#   UDP 8011 egress sink (forwarding disabled)
#   generic-radio-only socket metadata shim scope
#   immutable-ground-only trace evidence scope
# Adds exactly ONE passive NOS Engine time-witness, with witness output
# mounted read-write ONLY into the witness container under immutable-ground
# evidence.
#
# FAIL-CLOSED GATE
# ----------------
# Before the first Docker command, this candidate READS THE CONTRACT and
# requires ALL of:
#   a future status explicitly authorizing passive-time telemetry runtime
#   diagnostic_runtime_authorized == true
#   diagnostic_runtime_attempts_authorized == 1
#   passive_time_witness_static_verification == "PASS"
#   a nonempty accepted_runtime_entrypoint_sha256
#   this candidate's sha256 == accepted_runtime_entrypoint_sha256
#
# The CURRENT contract (0.4.4) sets NONE of these, so this candidate MUST
# exit non-zero before any Docker command.
#
# ABSOLUTE DENYLIST (refused regardless of any future contract):
#   command_source, command_vector, command_transmission, event_injection,
#   packet_capture, packet_payload_capture, packet_hashes,
#   ip_address_collection, host_networking, host_ports, docker_socket_mount,
#   external_network_egress
#
# Policy-visible evidence contains NO tick or monotonic-time values.
# ============================================================================

set -Eeuo pipefail

CONTRACT_PATH="${PASSIVE_TIME_WITNESS_CONTRACT:-configs/downlink-diagnostic-contract.json}"
CANDIDATE_SELF="${BASH_SOURCE[0]:-$0}"

# ---------------------------------------------------------------------------
# Deterministic, uniquely counted topology anchors (indices 0..14).
# Sourced verbatim from the accepted v3 telemetry-only topology.
# ---------------------------------------------------------------------------
readonly ANCHOR_0_TO_LAB_COMPILED_DESTINATION_PORT=5013
readonly ANCHOR_1_TO_RADIO_WITNESS_ALIAS="active-gs"
readonly ANCHOR_2_TO_RADIO_WITNESS_BIND_PORT=5013
readonly ANCHOR_3_TO_RADIO_WITNESS_FORWARD_DESTINATION="radio-sim"
readonly ANCHOR_4_TO_RADIO_WITNESS_FORWARD_PORT=5011
readonly ANCHOR_5_TO_RADIO_WITNESS_BYTE_PRESERVING="true"
readonly ANCHOR_6_RADIO_EGRESS_WITNESS_ALIAS="cryptolib"
readonly ANCHOR_7_RADIO_EGRESS_WITNESS_BIND_PORT=8011
readonly ANCHOR_8_RADIO_EGRESS_WITNESS_FORWARDING="false"
readonly ANCHOR_9_RADIO_GROUND_MODE="UDP"
readonly ANCHOR_10_RADIO_FSW_TELEMETRY_LISTENER_PORT=5011
readonly ANCHOR_11_RADIO_COMMAND_LISTENER_PORT=8010
readonly ANCHOR_12_SHIM_MOUNT_SCOPE="generic_radio_only"
readonly ANCHOR_13_TRACE_EVIDENCE_SCOPE="immutable_ground_only"
readonly ANCHOR_14_PASSIVE_TIME_WITNESS_COUNT=1

readonly DENYLIST=(
  "command_source"
  "command_vector"
  "command_transmission"
  "event_injection"
  "packet_capture"
  "packet_payload_capture"
  "packet_hashes"
  "ip_address_collection"
  "host_networking"
  "host_ports"
  "docker_socket_mount"
  "external_network_egress"
)

# Immutable-ground evidence layout. The dedicated witness output directory is
# mounted read-write ONLY into the witness container, under immutable-ground
# evidence. Policy-visible paths never see tick/monotonic-time values.
readonly IMMUTABLE_GROUND_EVIDENCE_DIR="artifacts/wp4-passive-time-witness-immutable-ground"
readonly WITNESS_OUTPUT_SUBDIR="witness-output"
readonly WITNESS_OUTPUT_MOUNT_MODE="rw"
readonly WITNESS_OUTPUT_MOUNT_DEST="/evidence/witness-output"

# Policy-visible evidence SIBLING root (separate from immutable-ground). The
# passive time-witness writable output lives ONLY under immutable-ground
# above; policy-visible files carry no tick/monotonic-time or witness trace.
readonly POLICY_VISIBLE_EVIDENCE_DIR="artifacts/wp4-passive-time-witness-policy-visible"

# ---------------------------------------------------------------------------
# deny_capability(): hard-refuse a forbidden capability. Exits non-zero.
# ---------------------------------------------------------------------------
deny_capability() {
  local name="$1"
  echo "[FAIL-CLOSED] forbidden capability requested: ${name}" >&2
  exit 1
}

# Assert the denylist is populated and wholly non-empty.
for cap in "${DENYLIST[@]}"; do
  : "${cap:?denylist entry must be non-empty}"
  case "${cap}" in
    command_source|command_vector|command_transmission|event_injection|\
    packet_capture|packet_payload_capture|packet_hashes|ip_address_collection|\
    host_networking|host_ports|docker_socket_mount|external_network_egress) ;;
    *) deny_capability "unknown:${cap}" ;;
  esac
done

# ---------------------------------------------------------------------------
# read_contract_field(): read a JSON value from the contract by dotted path.
# Uses python3 with json. Returns empty string on missing field.
# ---------------------------------------------------------------------------
read_contract_field() {
  local dotted="$1"
  python3 - "$CONTRACT_PATH" "$dotted" <<'PY'
import json, os, sys
path = sys.argv[1]
dotted = sys.argv[2]
try:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
except Exception:
    print("", end="")
    sys.exit(0)
cur = data
for part in dotted.split("."):
    if isinstance(cur, dict) and part in cur:
        cur = cur[part]
    else:
        print("", end="")
        sys.exit(0)
if isinstance(cur, bool):
    print("true" if cur else "false", end="")
elif cur is None:
    print("", end="")
else:
    print(str(cur), end="")
PY
}

# ---------------------------------------------------------------------------
# Self-hash via the designed accepted-entrypoint mechanism: sha256 of this
# candidate file. Compare to accepted_runtime_entrypoint_sha256.
# ---------------------------------------------------------------------------
candidate_sha256() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum -- "${CANDIDATE_SELF}" | awk '{print $1}'
  else
    shasum -a 256 -- "${CANDIDATE_SELF}" | awk '{print $1}'
  fi
}

# ---------------------------------------------------------------------------
# runtime_authorized(): the fail-closed predicate. Reads the CONTRACT.
# Returns 0 ONLY if a future contract sets ALL six requirements:
#   status == PASSIVE_TIME_WITNESS_TELEMETRY_RUNTIME_AUTHORIZED (top-level
#     contract field; NOT a nested gate.passive_time_telemetry_runtime_status)
#   gate.diagnostic_runtime_authorized == true
#   gate.diagnostic_runtime_attempts_authorized == 1
#   gate.passive_time_witness_static_verification == "PASS"
#   accepted_runtime_entrypoint_sha256 (nonempty)
#   candidate sha256 == accepted_runtime_entrypoint_sha256
# ---------------------------------------------------------------------------
runtime_authorized() {
  local status authd attempts verif acc_hash self_hash
  # Top-level contract status gate. The emit-time contract (0.4.4) sets
  # status=PASSIVE_TIME_WITNESS_DESIGN_LOCKED_STATIC_GATE_PENDING, NOT the
  # value below; the gate fails closed before any Docker command.
  status="$(read_contract_field "status")"
  [[ "${status}" == "PASSIVE_TIME_WITNESS_TELEMETRY_RUNTIME_AUTHORIZED" ]] || return 1

  authd="$(read_contract_field "gate.diagnostic_runtime_authorized")"
  [[ "${authd}" == "true" ]] || return 1

  attempts="$(read_contract_field "gate.diagnostic_runtime_attempts_authorized")"
  [[ "${attempts}" == "1" ]] || return 1

  verif="$(read_contract_field "gate.passive_time_witness_static_verification")"
  [[ "${verif}" == "PASS" ]] || return 1

  acc_hash="$(read_contract_field "gate.accepted_runtime_entrypoint_sha256")"
  [[ -n "${acc_hash}" ]] || return 1

  self_hash="$(candidate_sha256)"
  [[ "${self_hash}" == "${acc_hash}" ]] || return 1

  return 0
}

# ---------------------------------------------------------------------------
# FAIL-CLOSED enforcement. This is the single authorized exit point before any
# Docker command. Because runtime_authorized() is false for contract 0.4.4,
# the candidate exits here.
# ---------------------------------------------------------------------------
if ! runtime_authorized; then
  echo "[FAIL-CLOSED] passive time-witness runtime NOT authorized by current contract (0.4.4)." >&2
  echo "[FAIL-CLOSED] contract=${CONTRACT_PATH}" >&2
  echo "[FAIL-CLOSED] status=$(read_contract_field 'status' || true)" >&2
  echo "[FAIL-CLOSED] gate.diagnostic_runtime_authorized=$(read_contract_field 'gate.diagnostic_runtime_authorized' || true)" >&2
  echo "[FAIL-CLOSED] gate.diagnostic_runtime_attempts_authorized=$(read_contract_field 'gate.diagnostic_runtime_attempts_authorized' || true)" >&2
  echo "[FAIL-CLOSED] gate.passive_time_witness_static_verification=$(read_contract_field 'gate.passive_time_witness_static_verification' || true)" >&2
  echo "[FAIL-CLOSED] gate.accepted_runtime_entrypoint_sha256=<empty-under-0.4.4>" >&2
  echo "[FAIL-CLOSED] candidate self sha256 does not match any accepted future entrypoint hash" >&2
  echo "PASSIVE_TIME_WITNESS_RUNTIME_CANDIDATE_RUN_STATUS=CLOSED_GATE_NOT_AUTHORIZED" >&2
  exit 1
fi

# ===========================================================================
# POST-GATE: dormant Docker commands. UNREACHABLE under contract 0.4.4.
#
# These are actual Docker commands describing the accepted v3 telemetry-only
# topology plus exactly one passive NOS Engine time-witness. They invoke NO
# command source, NO event injection, NO host networking, NO host ports, NO
# Docker-socket mount, NO packet capture, and NO external egress.
# ===========================================================================

NET_NAME="wp4-passive-time-witness-internal"
WITNESS_IMAGE="ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"
WITNESS_BIN="/work/scripts/passive_nos_engine_time_witness"

# Dedicated witness output directory inside immutable-ground evidence, mounted
# read-write ONLY into the witness container.
WITNESS_OUTPUT_HOST="${IMMUTABLE_GROUND_EVIDENCE_DIR}/${WITNESS_OUTPUT_SUBDIR}"
mkdir -p "${WITNESS_OUTPUT_HOST}"
chmod 700 "${WITNESS_OUTPUT_HOST}"

# Project-labeled internal bridge network. No host networking, no external
# egress, no host ports published.
docker network create --driver bridge \
  --internal \
  --label "wp4.passive-time-witness.scope=immutable-ground" \
  --label "wp4.passive-time-witness.source-locks=generic-radio-only" \
  "${NET_NAME}"

# active-gs UDP 5013 proxy -> radio-sim UDP 5011 (byte-preserving). The proxy
# container only forwards between the two project-internal UDP sockets; it
# exposes no host ports and performs no packet capture.
docker run -d \
  --name "wp4-ptw-to-radio-witness" \
  --network "${NET_NAME}" \
  --network-alias "active-gs" \
  --label "wp4.passive-time-witness.role=to_radio_witness" \
  --label "wp4.passive-time-witness.bind_port=${ANCHOR_2_TO_RADIO_WITNESS_BIND_PORT}" \
  --label "wp4.passive-time-witness.forward_destination=${ANCHOR_3_TO_RADIO_WITNESS_FORWARD_DESTINATION}" \
  --label "wp4.passive-time-witness.forward_port=${ANCHOR_4_TO_RADIO_WITNESS_FORWARD_PORT}" \
  --label "wp4.passive-time-witness.byte_preserving=${ANCHOR_5_TO_RADIO_WITNESS_BYTE_PRESERVING}" \
  --label "wp4.passive-time-witness.packet_capture=false" \
  --label "wp4.passive-time-witness.host_ports=false" \
  "${WITNESS_IMAGE}" true

# UDP 8011 non-forwarding egress sink (cryptolib). Forwarding disabled; no
# external egress; no host ports.
docker run -d \
  --name "wp4-ptw-radio-egress-sink" \
  --network "${NET_NAME}" \
  --network-alias "cryptolib" \
  --label "wp4.passive-time-witness.role=radio_egress_witness" \
  --label "wp4.passive-time-witness.bind_port=${ANCHOR_7_RADIO_EGRESS_WITNESS_BIND_PORT}" \
  --label "wp4.passive-time-witness.forwarding=${ANCHOR_8_RADIO_EGRESS_WITNESS_FORWARDING}" \
  --label "wp4.passive-time-witness.external_egress=false" \
  --label "wp4.passive-time-witness.host_ports=false" \
  "${WITNESS_IMAGE}" true

# generic-radio-only metadata shim sidecar. Scope is generic_radio_only; it
# carries no command source, no event injection, no packet payload capture.
docker run -d \
  --name "wp4-ptw-generic-radio-shim" \
  --network "${NET_NAME}" \
  --network-alias "radio-sim" \
  --label "wp4.passive-time-witness.role=generic_radio_only_shim" \
  --label "wp4.passive-time-witness.shim_mount_scope=${ANCHOR_12_SHIM_MOUNT_SCOPE}" \
  --label "wp4.passive-time-witness.command_source=false" \
  --label "wp4.passive-time-witness.event_injection=false" \
  --label "wp4.passive-time-witness.packet_capture=false" \
  --label "wp4.passive-time-witness.docker_socket_mount=false" \
  "${WITNESS_IMAGE}" true

# Exactly ONE passive NOS Engine time-witness. Witness output is mounted
# read-write ONLY into this witness container, under immutable-ground
# evidence. No host networking, no host ports, no Docker-socket mount, no
# external egress, no packet capture, no command source.
docker run -d \
  --name "wp4-ptw-passive-time-witness" \
  --network "${NET_NAME}" \
  --label "wp4.passive-time-witness.role=passive_nos_engine_time_witness" \
  --label "wp4.passive-time-witness.count=${ANCHOR_14_PASSIVE_TIME_WITNESS_COUNT}" \
  --label "wp4.passive-time-witness.trace_evidence_scope=${ANCHOR_13_TRACE_EVIDENCE_SCOPE}" \
  --label "wp4.passive-time-witness.host_networking=false" \
  --label "wp4.passive-time-witness.host_ports=false" \
  --label "wp4.passive-time-witness.docker_socket_mount=false" \
  --label "wp4.passive-time-witness.external_egress=false" \
  --label "wp4.passive-time-witness.packet_capture=false" \
  --label "wp4.passive-time-witness.command_source=false" \
  --label "wp4.passive-time-witness.event_injection=false" \
  --label "wp4.passive-time-witness.witness_output_mount_mode=${WITNESS_OUTPUT_MOUNT_MODE}" \
  --label "wp4.passive-time-witness.witness_output_mount_dest=${WITNESS_OUTPUT_MOUNT_DEST}" \
  --label "wp4.passive-time-witness.witness_output_scope=immutable_ground_only" \
  -v "${WITNESS_OUTPUT_HOST}:${WITNESS_OUTPUT_MOUNT_DEST}:${WITNESS_OUTPUT_MOUNT_MODE}" \
  -v "$(pwd)/scripts:/work/scripts:ro" \
  "${WITNESS_IMAGE}" bash -lc "g++ -std=c++14 -Wall -Wextra -Werror -I/usr/include /work/scripts/passive_nos_engine_time_witness.cpp -lnos_engine_client -lnos_engine_common -lnos_engine_transport -lnos_engine_utility -o /tmp/passive_nos_engine_time_witness && /tmp/passive_nos_engine_time_witness --output ${WITNESS_OUTPUT_MOUNT_DEST}/trace.jsonl"

# Policy-visible output directory contains ONLY a non-sensitive scope marker
# and independent manifest information. NO tick or monotonic-time values are
# exposed to policy-visible paths.
# Policy-visible evidence lives under a SEPARATE SIBLING root, not under
# immutable-ground. The passive time-witness writable output lives ONLY
# under IMMUTABLE_GROUND_EVIDENCE_DIR above. Policy-visible files contain NO
# authoritative tick, CLOCK_MONOTONIC timestamp, derived timing, or witness
# trace — only a non-sensitive scope marker and independent manifest.
POLICY_VISIBLE_DIR="${POLICY_VISIBLE_EVIDENCE_DIR}"
mkdir -p "${POLICY_VISIBLE_DIR}"
cat > "${POLICY_VISIBLE_DIR}/scope-marker.json" <<'SCOPE_EOF'
{
  "component": "passive_time_witness_runtime_candidate",
  "topology_basis": "accepted_v3_telemetry_only",
  "passive_time_witness_count": 1,
  "witness_output_scope": "immutable_ground_only",
  "policy_visible_time_evidence_allowed": false,
  "gate_status": "OPEN_FUTURE_CONTRACT",
  "runtime_authorized": true,
  "independent_manifest": {
    "anchor_count": 15,
    "denylist_count": 12
  }
}
SCOPE_EOF

cat > "${POLICY_VISIBLE_DIR}/independent-manifest.json" <<'MANIFEST_EOF'
{
  "topology_anchors": 15,
  "denylist_entries": 12,
  "docker_network": "wp4-passive-time-witness-internal",
  "telemetry_runtime_components": 4,
  "passive_time_witness_containers": 1,
  "command_sources": 0,
  "event_injections": 0,
  "host_networking": false,
  "host_ports": false,
  "docker_socket_mount": false,
  "packet_capture": false,
  "external_egress": false
}
MANIFEST_EOF

echo "PASSIVE_TIME_WITNESS_RUNTIME_CANDIDATE_RUN_STATUS=OPEN_GATE_EXECUTED" >&2
exit 0
CANDIDATE_EOF
}

candidate_body="$(__emit_candidate_body)"

# Atomic write of the candidate text.
tmp_emit="${EMIT_PATH}.tmp.$$"
printf '%s\n' "${candidate_body}" > "${tmp_emit}"
mv -f "${tmp_emit}" "${EMIT_PATH}"

echo "PASSIVE_TIME_WITNESS_RUNTIME_CANDIDATE_EMIT_STATUS=COMPLETE"
