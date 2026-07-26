#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_VERIFIER="$ROOT/scripts/verify_radio_socket_metadata_runtime_wrapper.sh"
WRAPPER_V2="$ROOT/scripts/run_radio_socket_metadata_diagnostic_v2.sh"
TEMP=""

cleanup() {
  local rc=$?
  [[ -z "$TEMP" ]] || rm -f "$TEMP"
  trap - EXIT
  exit "$rc"
}
trap cleanup EXIT

for file in "$SOURCE_VERIFIER" "$WRAPPER_V2"; do
  [[ -f "$file" ]] || {
    echo "[ERROR] Missing required compatibility-gate file: $file" >&2
    exit 1
  }
done

bash -n "$SOURCE_VERIFIER"
bash -n "$WRAPPER_V2"
python3 - "$WRAPPER_V2" <<'PY'
import sys
from pathlib import Path

text = Path(sys.argv[1]).read_text(encoding="utf-8")
required = (
    "radio_anchor = ''.join((",
    "radio_instrumented = ''.join((",
    "ast.parse(body",
    "unterminated generated Python heredoc",
    "no generated Python heredocs were validated",
    "legacy multiline radio anchor remained after v2 preparation",
)
for token in required:
    if token not in text:
        raise SystemExit(f"v2 overlay regression guard missing: {token}")
if 'f"      --mount \\"type=bind' in text:
    raise SystemExit("v2 overlay retained unsafe nested mount f-string quoting")
PY

source_sha_before="$(shasum -a 256 "$SOURCE_VERIFIER" | awk '{print $1}')"
TEMP="$(mktemp "$ROOT/scripts/.verify-radio-socket-metadata-v2.XXXXXX.sh")"

python3 - "$SOURCE_VERIFIER" "$TEMP" <<'PY'
import sys
from pathlib import Path

source = Path(sys.argv[1])
output = Path(sys.argv[2])
text = source.read_text(encoding="utf-8")
old = 'WRAPPER="$ROOT/scripts/run_radio_socket_metadata_diagnostic.sh"'
new = 'WRAPPER="$ROOT/scripts/run_radio_socket_metadata_diagnostic_v2.sh"'
count = text.count(old)
if count != 1:
    raise SystemExit(f"verifier wrapper anchor changed: expected 1, found {count}")
updated = text.replace(old, new, 1)
if new not in updated:
    raise SystemExit("v2 verifier wrapper path was not installed")
output.write_text(updated, encoding="utf-8")
PY

chmod 700 "$TEMP"
bash -n "$TEMP"
source_sha_after="$(shasum -a 256 "$SOURCE_VERIFIER" | awk '{print $1}')"
[[ "$source_sha_before" == "$source_sha_after" ]] || {
  echo "[ERROR] Original metadata wrapper verifier changed during v2 preparation." >&2
  exit 1
}

bash "$TEMP"
echo "RADIO_SOCKET_METADATA_RUNTIME_WRAPPER_V2_STATIC_VERIFICATION_STATUS=PASS"
