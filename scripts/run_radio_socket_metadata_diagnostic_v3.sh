#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE="$ROOT/scripts/run_radio_socket_metadata_diagnostic_v2.sh"
TEMP=""

cleanup() {
  local rc=$?
  [[ -z "$TEMP" ]] || rm -f "$TEMP"
  trap - EXIT
  exit "$rc"
}
trap cleanup EXIT

[[ -f "$SOURCE" ]] || {
  echo "[ERROR] Missing v2 metadata runtime wrapper: $SOURCE" >&2
  exit 1
}

bash -n "$SOURCE"
source_sha_before="$(shasum -a 256 "$SOURCE" | awk '{print $1}')"
TEMP="$(mktemp "$ROOT/scripts/.run-radio-socket-metadata-v3.XXXXXX.sh")"

python3 - "$SOURCE" "$TEMP" <<'PY'
import ast
import re
import sys
from pathlib import Path

source = Path(sys.argv[1])
output = Path(sys.argv[2])
text = source.read_text(encoding="utf-8")

anchor = "updated = text[:start] + replacement + text[end:]\n\nlegacy_docker_guard ="
if text.count(anchor) != 1:
    raise SystemExit(
        "v2 integration anchor changed: "
        f"expected 1, found {text.count(anchor)}"
    )

mode_patch = r'''updated = text[:start] + replacement + text[end:]

static_status_old = "RADIO_SOCKET_METADATA_RUNTIME_WRAPPER_STATIC_VALIDATION_PENDING"
static_status_new = "RADIO_SOCKET_METADATA_RUNTIME_ATTEMPT_CONSUMED_PRE_RUNTIME_ASSERTION_FAILED"
runtime_status_old = "RADIO_SOCKET_METADATA_RUNTIME_STATIC_GATE_PASS_RUNTIME_PENDING"
runtime_status_new = "RADIO_SOCKET_METADATA_RUNTIME_V3_STATIC_GATE_PASS_RUNTIME_PENDING"
for old_status, new_status, label in (
    (static_status_old, static_status_new, "v3 fail-closed static status"),
    (runtime_status_old, runtime_status_new, "v3 runtime status"),
):
    count = updated.count(old_status)
    if count < 2:
        raise SystemExit(f"{label}: expected at least two occurrences; found {count}")
    updated = updated.replace(old_status, new_status)

legacy_gate_assertion = (
    "    + 'assert contract[\"gate\"]"
    "[\"radio_socket_metadata_runtime_wrapper_static_verification\"] "
    "== \"PENDING\"\\n'\n"
)
mode_aware_gate_assertion = (
    "    + 'assert contract[\"gate\"]"
    "[\"radio_socket_metadata_runtime_wrapper_v3_static_verification\"] "
    "== (\"PENDING\" if verify_only else \"PASS\")\\n'\n"
)
if updated.count(legacy_gate_assertion) != 1:
    raise SystemExit(
        "legacy wrapper-gate assertion changed: "
        f"expected 1, found {updated.count(legacy_gate_assertion)}"
    )
updated = updated.replace(
    legacy_gate_assertion,
    mode_aware_gate_assertion,
    1,
)

assert ("PENDING" if True else "PASS") == "PENDING"
assert ("PENDING" if False else "PASS") == "PASS"

legacy_docker_guard ='''

updated = text.replace(anchor, mode_patch, 1)
for required in (
    "RADIO_SOCKET_METADATA_RUNTIME_ATTEMPT_CONSUMED_PRE_RUNTIME_ASSERTION_FAILED",
    "RADIO_SOCKET_METADATA_RUNTIME_V3_STATIC_GATE_PASS_RUNTIME_PENDING",
    "radio_socket_metadata_runtime_wrapper_v3_static_verification",
    '("PENDING" if verify_only else "PASS")',
    "legacy wrapper-gate assertion changed",
):
    if required not in updated:
        raise SystemExit(f"v3 wrapper requirement missing: {required}")

lines = updated.splitlines()
marker = re.compile(r"<<'(?P<delimiter>PY[A-Z0-9_]*)'")
parsed = 0
index = 0
while index < len(lines):
    match = marker.search(lines[index])
    if match is None:
        index += 1
        continue
    delimiter = match.group("delimiter")
    start = index + 1
    index = start
    while index < len(lines) and lines[index] != delimiter:
        index += 1
    if index >= len(lines):
        raise SystemExit(f"unterminated v3 Python heredoc: {delimiter}")
    ast.parse("\n".join(lines[start:index]) + "\n", filename=f"<{delimiter}>")
    parsed += 1
    index += 1
if parsed < 1:
    raise SystemExit("no v3 Python heredocs were validated")

output.write_text(updated, encoding="utf-8")
PY

chmod 700 "$TEMP"
bash -n "$TEMP"
source_sha_after="$(shasum -a 256 "$SOURCE" | awk '{print $1}')"
[[ "$source_sha_before" == "$source_sha_after" ]] || {
  echo "[ERROR] V2 metadata wrapper changed during v3 preparation." >&2
  exit 1
}

echo "[OK] Prepared mode-aware metadata wrapper gate without modifying v2."
bash "$TEMP" "$@"
