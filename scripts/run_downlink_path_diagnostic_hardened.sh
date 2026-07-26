#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE="$ROOT/scripts/run_downlink_path_diagnostic.sh"
TEMP=""

cleanup() {
  local rc=$?
  [[ -z "$TEMP" ]] || rm -f "$TEMP"
  trap - EXIT
  exit "$rc"
}
trap cleanup EXIT

[[ -f "$SOURCE" ]] || {
  echo "[ERROR] Missing diagnostic runner: $SOURCE" >&2
  exit 1
}
bash -n "$SOURCE"
source_sha_before="$(shasum -a 256 "$SOURCE" | awk '{print $1}')"
TEMP="$(mktemp "$ROOT/scripts/.run-downlink-diagnostic-hardened.XXXXXX.sh")"

python3 - "$SOURCE" "$TEMP" <<'PY'
from pathlib import Path
import sys

source = Path(sys.argv[1])
output = Path(sys.argv[2])
text = source.read_text(encoding="utf-8")

replacements = (
    ("start radio-egress-witness cryptolib false", "start radio-egress-witness cryptolib true", 2),
    ("start to-radio-witness active-gs false", "start to-radio-witness active-gs true", 2),
    ("'record expected_runtime_component_count 20\\n'", "'record expected_runtime_component_count 22\\n'", 1),
)
for old, new, expected in replacements:
    count = text.count(old)
    if count != expected:
        raise SystemExit(f"unexpected occurrence count for {old!r}: {count}, expected {expected}")
    text = text.replace(old, new)

for required in (
    "start radio-egress-witness cryptolib true",
    "start to-radio-witness active-gs true",
    "record expected_runtime_component_count 22",
    "check_runtime startup",
    "check_runtime observation",
    "check_runtime final",
):
    if required not in text:
        raise SystemExit(f"hardened diagnostic requirement missing: {required}")

output.write_text(text, encoding="utf-8")
PY

chmod 700 "$TEMP"
bash -n "$TEMP"
source_sha_after="$(shasum -a 256 "$SOURCE" | awk '{print $1}')"
[[ "$source_sha_before" == "$source_sha_after" ]] || {
  echo "[ERROR] Canonical diagnostic runner changed during hardening." >&2
  exit 1
}

echo "[OK] Hardened both telemetry witnesses as required runtime components without modifying the canonical diagnostic runner."
bash "$TEMP" "$@"
rc=$?
if [[ "${DOWNLINK_DIAGNOSTIC_VERIFY_ONLY:-0}" == 1 && "$rc" -eq 0 ]]; then
  echo "DOWNLINK_DIAGNOSTIC_HARDENED_WRAPPER_VERIFICATION_STATUS=PASS"
fi
exit "$rc"
