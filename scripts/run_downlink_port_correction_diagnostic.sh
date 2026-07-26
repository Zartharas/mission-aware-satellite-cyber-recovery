#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE="$ROOT/scripts/run_downlink_path_diagnostic.sh"
CONTRACT="$ROOT/configs/downlink-diagnostic-contract.json"
TEMP=""

cleanup() {
  local rc=$?
  [[ -z "$TEMP" ]] || rm -f "$TEMP"
  trap - EXIT
  exit "$rc"
}
trap cleanup EXIT

for file in "$SOURCE" "$CONTRACT"; do
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
verify_only = os.environ.get("DOWNLINK_DIAGNOSTIC_VERIFY_ONLY") == "1"
assert contract["contract_version"] == "0.2.0"
assert contract["scientific_outcome_allowed"] is False
assert contract["event_injection_allowed"] is False
assert contract["command_transmission_allowed"] is False
assert contract["baseline_execution_allowed"] is False
assert contract["cryptographic_semantics_claim_allowed"] is False
assert contract["root_cause_finding"]["classification"] == "DIRECT_COMPILED_PORT_MISMATCH"
assert contract["root_cause_finding"]["to_lab_compiled_destination_port"] == 5013
assert contract["topology"]["to_radio_witness"]["bind_port"] == 5013
assert contract["topology"]["to_radio_witness"]["forward_port"] == 5011
assert contract["evidence_requirements"]["policy_visible_scope_marker_required"] is True
assert contract["evidence_requirements"]["zero_entry_manifest_allowed"] is False
assert contract["gate"]["baseline_run_1_authorized"] is False
assert contract["gate"]["baseline_run_2_authorized"] is False
assert contract["gate"]["event_injection_authorized"] is False
if verify_only:
    assert contract["status"] == "PORT_CORRECTION_STATIC_VALIDATION_PENDING"
    assert contract["gate"]["diagnostic_runtime_authorized"] is False
else:
    assert contract["status"] == "PORT_CORRECTION_STATIC_GATE_PASS_RUNTIME_PENDING"
    assert contract["gate"]["diagnostic_runtime_authorized"] is True
PY

source_sha_before="$(shasum -a 256 "$SOURCE" | awk '{print $1}')"
TEMP="$(mktemp "$ROOT/scripts/.run-downlink-port-correction.XXXXXX.sh")"

python3 - "$SOURCE" "$TEMP" <<'PY'
from pathlib import Path
import sys

source = Path(sys.argv[1])
output = Path(sys.argv[2])
text = source.read_text(encoding="utf-8")


def replace_exact(payload: str, old: str, new: str, expected: int, label: str) -> str:
    count = payload.count(old)
    if count != expected:
        raise SystemExit(f"{label}: expected {expected} occurrence(s), found {count}")
    return payload.replace(old, new)


text = replace_exact(
    text,
    'assert diagnostic["contract_version"] == "0.1.0"',
    'assert diagnostic["contract_version"] == "0.2.0"',
    1,
    "outer contract version",
)
text = replace_exact(
    text,
    'assert diagnostic["status"] == "STATIC_VALIDATION_PENDING"',
    'assert diagnostic["status"] == "PORT_CORRECTION_STATIC_VALIDATION_PENDING"',
    1,
    "outer verify status",
)
text = replace_exact(
    text,
    'assert diagnostic["status"] == "STATIC_GATE_PASS_RUNTIME_PENDING"',
    'assert diagnostic["status"] == "PORT_CORRECTION_STATIC_GATE_PASS_RUNTIME_PENDING"',
    1,
    "outer runtime status",
)
text = replace_exact(
    text,
    'assert diagnostic["contract_version"]=="0.1.0"',
    'assert diagnostic["contract_version"]=="0.2.0"',
    1,
    "generated contract version",
)
text = replace_exact(
    text,
    'assert diagnostic["status"]=="STATIC_GATE_PASS_RUNTIME_PENDING"',
    'assert diagnostic["status"]=="PORT_CORRECTION_STATIC_GATE_PASS_RUNTIME_PENDING"',
    1,
    "generated runtime status",
)
text = replace_exact(
    text,
    'assert diagnostic["topology"]["to_radio_witness"]["bind_port"] == 5011',
    'assert diagnostic["topology"]["to_radio_witness"]["bind_port"] == 5013',
    1,
    "proxy bind assertion",
)
runtime_line_old = '--mode proxy --bind-host 0.0.0.0 --bind-port 5011 ' + chr(92) * 2
runtime_line_new = '--mode proxy --bind-host 0.0.0.0 --bind-port 5013 ' + chr(92) * 2
text = replace_exact(
    text,
    runtime_line_old,
    runtime_line_new,
    1,
    "proxy bind runtime",
)
text = replace_exact(
    text,
    "'--mode proxy --bind-host 0.0.0.0 --bind-port 5011',",
    "'--mode proxy --bind-host 0.0.0.0 --bind-port 5013',",
    1,
    "proxy bind required token",
)
text = replace_exact(
    text,
    "start radio-egress-witness cryptolib false",
    "start radio-egress-witness cryptolib true",
    2,
    "radio-egress liveness",
)
text = replace_exact(
    text,
    "start to-radio-witness active-gs false",
    "start to-radio-witness active-gs true",
    2,
    "TO witness liveness",
)
text = replace_exact(
    text,
    "'record expected_runtime_component_count 20\\n'",
    "'record expected_runtime_component_count 22\\n'",
    1,
    "runtime component count",
)

runtime_anchor = "updated = replace_once(updated, 'record expected_runtime_component_count 21\\n', 'record expected_runtime_component_count 22\\n', \"runtime count\")\n"
if text.count(runtime_anchor) != 1:
    raise SystemExit("runtime transformation anchor missing")
runtime_insert = '''updated = replace_once(
    updated,
    'record to_lab_destination_port 5011\n',
    'record to_lab_destination_port 5013\n'
    'record to_lab_compiled_destination_port 5013\n'
    'record radio_fsw_telemetry_listener_port 5011\n',
    "compiled TO_LAB destination port",
)
updated = replace_once(updated, 'record expected_runtime_component_count 21\n', 'record expected_runtime_component_count 22\n', "runtime count")
'''
text = text.replace(runtime_anchor, runtime_insert, 1)

hash_anchor = "temporary = manifest.with_suffix(\".txt.tmp\")\n    temporary.write_text(\"\\n\".join(entries) + \"\\n\", encoding=\"utf-8\")\n"
policy_anchor = "mkdir -p \"$PROBE_GROUND\" \"$ORCHESTRATION/runtime-config\" \"$POLICY\" \"$INOUT\"\n"
transform_anchor = "updated = replace_once(\n    updated,\n    'PHASE=\"wp4-benign-baseline-interface-corrected\"',\n"
if text.count(transform_anchor) != 1:
    raise SystemExit("generated-runner transformation insertion anchor missing")
transform_insert = '''updated = replace_once(
    updated,
    ''' + repr(hash_anchor) + ''',
    'if not entries:\n'
    '    raise SystemExit(f"zero-entry evidence manifest rejected: {directory}")\n'
    'temporary = manifest.with_suffix(".txt.tmp")\n'
    'temporary.write_text("\\n".join(entries) + "\\n", encoding="utf-8")\n',
    "zero-entry evidence rejection",
)
updated = replace_once(
    updated,
    ''' + repr(policy_anchor) + ''',
    'mkdir -p "$PROBE_GROUND" "$ORCHESTRATION/runtime-config" "$POLICY" "$INOUT"\n'
    'cat > "$POLICY/scope.json" <<\'EOF\'\n'
    '{\n'
    '  "policy_visible_evidence": "none_by_design",\n'
    '  "truth_data_included": false,\n'
    '  "command_data_included": false,\n'
    '  "scientific_outcome_included": false\n'
    '}\n'
    'EOF\n',
    "policy-visible scope marker",
)

'''
text = text.replace(transform_anchor, transform_insert + transform_anchor, 1)

required_anchor = "    'TCP_GROUND=0',\n"
if text.count(required_anchor) != 1:
    raise SystemExit("required-token insertion anchor missing")
text = text.replace(
    required_anchor,
    "    '--mode proxy --bind-host 0.0.0.0 --bind-port 5013',\n"
    "    'record to_lab_compiled_destination_port 5013',\n"
    "    'policy_visible_evidence',\n"
    "    'zero-entry evidence manifest rejected',\n"
    + required_anchor,
    1,
)

for required in (
    'assert diagnostic["contract_version"] == "0.2.0"',
    'PORT_CORRECTION_STATIC_VALIDATION_PENDING',
    'PORT_CORRECTION_STATIC_GATE_PASS_RUNTIME_PENDING',
    '--bind-port 5013',
    '--forward-host radio-sim --forward-port 5011',
    'start radio-egress-witness cryptolib true',
    'start to-radio-witness active-gs true',
    'record expected_runtime_component_count 22',
    'record to_lab_compiled_destination_port 5013',
    'policy-visible scope marker',
    'zero-entry evidence rejection',
):
    if required not in text:
        raise SystemExit(f"port-correction requirement missing: {required}")

output.write_text(text, encoding="utf-8")
PY

chmod 700 "$TEMP"
bash -n "$TEMP"
source_sha_after="$(shasum -a 256 "$SOURCE" | awk '{print $1}')"
[[ "$source_sha_before" == "$source_sha_after" ]] || {
  echo "[ERROR] Historical diagnostic runner changed during port-correction preparation." >&2
  exit 1
}

echo "[OK] Generated a hardened TO_LAB 5013-to-radio 5011 telemetry-only diagnostic without modifying the historical runner."
bash "$TEMP" "$@"
rc=$?
if [[ "${DOWNLINK_DIAGNOSTIC_VERIFY_ONLY:-0}" == 1 && "$rc" -eq 0 ]]; then
  echo "DOWNLINK_PORT_CORRECTION_WRAPPER_VERIFICATION_STATUS=PASS"
fi
exit "$rc"
