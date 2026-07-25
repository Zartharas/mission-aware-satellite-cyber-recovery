#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_RUNNER="$ROOT/scripts/run_benign_baseline_interface_corrected.sh"
PREPARER="$ROOT/scripts/prepare_runtime_radio_config.py"
TEMP_RUNNER=""

cleanup_wrapper() {
  local rc=$?
  if [[ -n "$TEMP_RUNNER" ]]; then
    rm -f "$TEMP_RUNNER"
  fi
  trap - EXIT
  exit "$rc"
}
trap cleanup_wrapper EXIT

for file in "$SOURCE_RUNNER" "$PREPARER"; do
  [[ -f "$file" ]] || {
    echo "[ERROR] Missing required file: $file" >&2
    exit 1
  }
done

python3 -m py_compile "$PREPARER"
python3 "$PREPARER" --self-test >/dev/null
bash -n "$SOURCE_RUNNER"

source_sha_before="$(shasum -a 256 "$SOURCE_RUNNER" | awk '{print $1}')"
TEMP_RUNNER="$(mktemp "$ROOT/scripts/.run-benign-interface-textsafe.XXXXXX.sh")"

python3 - "$SOURCE_RUNNER" "$TEMP_RUNNER" <<'PY'
from pathlib import Path
import sys

source_path = Path(sys.argv[1])
output_path = Path(sys.argv[2])
text = source_path.read_text(encoding="utf-8")

start_marker = 'python3 - "$INOUT/Inp_Sim.txt" "$RUNTIME_SIM_CONFIG" <<\'PY\'\n'
start = text.find(start_marker)
if start < 0 or text.count(start_marker) != 1:
    raise SystemExit("expected exactly one embedded runtime-configuration block")
end_marker = "\nPY\n"
end = text.find(end_marker, start + len(start_marker))
if end < 0:
    raise SystemExit("embedded runtime-configuration block terminator not found")
end += len(end_marker)

replacement = '''python3 - "$INOUT/Inp_Sim.txt" <<'PY'
from pathlib import Path
import sys

inp_sim = Path(sys.argv[1])
lines = inp_sim.read_text(encoding="utf-8").splitlines()
for index, line in enumerate(lines):
    if "Graphics Front End?" in line:
        comment = line.split("!", 1)[1] if "!" in line else " Graphics Front End?"
        lines[index] = f"FALSE                           !{comment}"
        break
else:
    raise SystemExit("Graphics Front End setting not found")
inp_sim.write_text("\\n".join(lines) + "\\n", encoding="utf-8")
PY

python3 "$ROOT/scripts/prepare_runtime_radio_config.py" \\
  "$NOS3/sims/build/bin/nos3-simulator.xml" \\
  "$RUNTIME_SIM_CONFIG"
'''

updated = text[:start] + replacement + text[end:]
record_line = 'record runtime_radio_ci_port_override 5010_to_5012\n'
if updated.count(record_line) != 1:
    raise SystemExit("runtime interface manifest anchor is missing or ambiguous")
updated = updated.replace(
    record_line,
    record_line + 'record runtime_simulator_config_edit_method bounded_text_single_character\n',
    1,
)

if "xml.etree.ElementTree" in updated:
    raise SystemExit("strict XML parser remained in generated runner")
if 'prepare_runtime_radio_config.py' not in updated:
    raise SystemExit("tolerant runtime configuration preparer was not inserted")
if updated.count('record runtime_simulator_config_edit_method bounded_text_single_character') != 1:
    raise SystemExit("runtime edit method was not recorded exactly once")

output_path.write_text(updated, encoding="utf-8")
PY

chmod 700 "$TEMP_RUNNER"
bash -n "$TEMP_RUNNER"

source_sha_after="$(shasum -a 256 "$SOURCE_RUNNER" | awk '{print $1}')"
[[ "$source_sha_before" == "$source_sha_after" ]] || {
  echo "[ERROR] Canonical interface runner changed during wrapper preparation." >&2
  exit 1
}

echo "[OK] Generated a text-safe bounded runtime runner without modifying the canonical source."
if [[ "${TEXTSAFE_VERIFY_ONLY:-0}" == 1 ]]; then
  echo "BENIGN_BASELINE_TEXTSAFE_WRAPPER_VERIFICATION_STATUS=PASS"
  exit 0
fi

bash "$TEMP_RUNNER" "$@"
