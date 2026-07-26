#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE="$ROOT/scripts/run_radio_socket_metadata_diagnostic.sh"
TEMP=""

cleanup() {
  local rc=$?
  [[ -z "$TEMP" ]] || rm -f "$TEMP"
  trap - EXIT
  exit "$rc"
}
trap cleanup EXIT

[[ -f "$SOURCE" ]] || {
  echo "[ERROR] Missing metadata runtime wrapper: $SOURCE" >&2
  exit 1
}

bash -n "$SOURCE"
source_sha_before="$(shasum -a 256 "$SOURCE" | awk '{print $1}')"
TEMP="$(mktemp "$ROOT/scripts/.run-radio-socket-metadata-v2.XXXXXX.sh")"

python3 - "$SOURCE" "$TEMP" <<'PY'
import ast
import re
import sys
from pathlib import Path

source = Path(sys.argv[1])
output = Path(sys.argv[2])
text = source.read_text(encoding="utf-8")

start_token = "radio_old = '''"
end_token = "\nhelper_anchor = 'check_runtime() {\\n'\n"

if text.count(start_token) != 1:
    raise SystemExit(
        f"legacy radio-anchor block count changed: expected 1, found {text.count(start_token)}"
    )
if text.count(end_token) != 1:
    raise SystemExit(
        f"radio helper boundary count changed: expected 1, found {text.count(end_token)}"
    )

start = text.index(start_token)
end = text.index(end_token, start)
replacement = '''slash = chr(92)
radio_anchor = ''.join((
    '      --network-alias generic-radio-sim ' + slash + '\\n',
    '      --env TCP_GROUND=0 --env MULTI_GDS=0 ' + slash + '\\n',
))
radio_instrumented = ''.join((
    '      --network-alias generic-radio-sim ' + slash + '\\n',
    '      --env TCP_GROUND=0 --env MULTI_GDS=0 ' + slash + '\\n',
    '      --env LD_PRELOAD=/tmp/libradio_socket_metadata_shim.so ' + slash + '\\n',
    '      --env RADIO_SOCKET_TRACE_PATH=/evidence-socket-metadata/radio-socket-metadata.log ' + slash + '\\n',
    '      --mount "type=bind,source=$SHIM_SO,target=/tmp/libradio_socket_metadata_shim.so,readonly" ' + slash + '\\n',
    '      --mount "type=bind,source=$SOCKET_METADATA_DIR,target=/evidence-socket-metadata" ' + slash + '\\n',
))
add(
    f"updated = replace_once(updated, {radio_anchor!r}, {radio_instrumented!r}, "
    "'generic-radio-only shim mount')"
)
'''

updated = text[:start] + replacement + text[end:]
for required in (
    "radio_anchor = ''.join((",
    "radio_instrumented = ''.join((",
    "generic-radio-only shim mount",
    "LD_PRELOAD=/tmp/libradio_socket_metadata_shim.so",
    "RADIO_SOCKET_TRACE_PATH=/evidence-socket-metadata/radio-socket-metadata.log",
):
    if required not in updated:
        raise SystemExit(f"v2 wrapper requirement missing: {required}")
if "radio_old = '''" in updated or "radio_new = '''" in updated:
    raise SystemExit("legacy multiline radio anchor remained after v2 preparation")

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
    body_start = index + 1
    index = body_start
    while index < len(lines) and lines[index] != delimiter:
        index += 1
    if index >= len(lines):
        raise SystemExit(f"unterminated generated Python heredoc: {delimiter}")
    body = "\n".join(lines[body_start:index]) + "\n"
    ast.parse(body, filename=f"<{delimiter}>")
    parsed += 1
    index += 1
if parsed < 1:
    raise SystemExit("no generated Python heredocs were validated")

output.write_text(updated, encoding="utf-8")
PY

chmod 700 "$TEMP"
bash -n "$TEMP"
source_sha_after="$(shasum -a 256 "$SOURCE" | awk '{print $1}')"
[[ "$source_sha_before" == "$source_sha_after" ]] || {
  echo "[ERROR] Original metadata runtime wrapper changed during v2 preparation." >&2
  exit 1
}

echo "[OK] Prepared structural generic-radio metadata integration anchor without modifying the original wrapper."
bash "$TEMP" "$@"
