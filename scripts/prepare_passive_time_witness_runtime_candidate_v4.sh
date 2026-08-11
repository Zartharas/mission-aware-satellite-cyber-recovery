#!/usr/bin/env bash
# WP4 V4 passive time-witness runtime-candidate generator. EMIT ONLY.
set -Eeuo pipefail

readonly ACCEPTED_V3_GENERATOR_SHA256="7140b7ff1aa1873ac020bae24d2a921a343f3d1fde86c6bbb4aece45cf229812"
readonly ACCEPTED_TRANSACTION_V2_SHA256="7419fa18b891ddc7525fa237b12323a092b9ece0f44d5b6fa4069c614322ce29"

fail() { echo "[ERROR] $*" >&2; exit 2; }

physical_tmp_root() {
  python3 - <<'PYTMP'
import os, tempfile
print(os.path.realpath(tempfile.gettempdir()))
PYTMP
}

canonicalize() {
  python3 - "$1" <<'PYCANON'
import os, sys
print(os.path.realpath(sys.argv[1]))
PYCANON
}

emit_path_raw="${PASSIVE_TIME_WITNESS_V4_EMIT_PATH:-}"
[[ -n "$emit_path_raw" ]] || fail "PASSIVE_TIME_WITNESS_V4_EMIT_PATH is required."
command -v python3 >/dev/null 2>&1 || fail "python3 is required."
command -v git >/dev/null 2>&1 || fail "git is required."
command -v bash >/dev/null 2>&1 || fail "bash is required."

repo_root="$(git rev-parse --show-toplevel 2>/dev/null)" ||
  fail "Run the generator from within the governed repository."
repo_root="$(cd "$repo_root" && pwd -P)"
repo_root_real="$(canonicalize "$repo_root")"

v3_generator="$repo_root/scripts/prepare_passive_time_witness_runtime_candidate_v3.sh"
transaction_v2="$repo_root/scripts/nos3_runtime_transaction_v2.py"

[[ -f "$v3_generator" && ! -L "$v3_generator" ]] ||
  fail "Protected V3 generator is not a regular file."
[[ "$(shasum -a 256 "$v3_generator" | awk '{print $1}')" == "$ACCEPTED_V3_GENERATOR_SHA256" ]] ||
  fail "Protected V3 generator identity mismatch."

[[ -f "$transaction_v2" && ! -L "$transaction_v2" ]] ||
  fail "Reviewed transaction-v2 is not a regular file."
[[ "$(shasum -a 256 "$transaction_v2" | awk '{print $1}')" == "$ACCEPTED_TRANSACTION_V2_SHA256" ]] ||
  fail "Reviewed transaction-v2 identity mismatch."

emit_parent_raw="$(dirname "$emit_path_raw")"
emit_leaf="$(basename "$emit_path_raw")"
[[ "$emit_leaf" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ && "$emit_leaf" != "." && "$emit_leaf" != ".." ]] ||
  fail "Invalid emit filename."
[[ -d "$emit_parent_raw" && ! -L "$emit_parent_raw" ]] ||
  fail "Emit parent must be an existing non-symlink directory."

emit_parent_real="$(canonicalize "$emit_parent_raw")"
emit_path_real="$emit_parent_real/$emit_leaf"
tmp_root_real="$(physical_tmp_root)"

case "$emit_path_real" in
  "$tmp_root_real"/*) ;;
  *) fail "V4 emission is restricted to the physical system temporary tree." ;;
esac
case "$emit_path_real" in
  "$repo_root_real"|"$repo_root_real"/*)
    fail "V4 emission must not target the repository." ;;
esac
[[ ! -e "$emit_path_real" && ! -L "$emit_path_real" ]] ||
  fail "Emit destination already exists."

umask 077
workdir="$(mktemp -d "$tmp_root_real/.wp4-v4-generator.XXXXXX")"
v3_candidate="$workdir/candidate-v3.sh"
tmp_emit="$(mktemp "$emit_parent_real/.${emit_leaf}.v4.XXXXXX")"

cleanup() {
  rc=$?
  rm -f -- "$v3_candidate" "$tmp_emit"
  rmdir "$workdir" 2>/dev/null || true
  trap - EXIT
  exit "$rc"
}
trap cleanup EXIT

PASSIVE_TIME_WITNESS_V3_EMIT_PATH="$v3_candidate" \
PASSIVE_TIME_WITNESS_V3_REVIEW_DIR="$workdir" \
  bash "$v3_generator" >/dev/null

[[ -f "$v3_candidate" && ! -L "$v3_candidate" ]] ||
  fail "V3 base-candidate emission failed."

python3 - "$v3_candidate" "$tmp_emit" <<'PYTRANSFORM'
from pathlib import Path
import sys

source_path = Path(sys.argv[1])
output_path = Path(sys.argv[2])
text = source_path.read_text(encoding="utf-8")

def replace_exact(text, old, new, expected, label):
    count = text.count(old)
    if count != expected:
        raise SystemExit(
            f"{label}: expected {expected} source anchors; found {count}"
        )
    return text.replace(old, new)

def replace_one(text, old, new, label):
    return replace_exact(text, old, new, 1, label)

text = text.replace("V3", "V4").replace("v3", "v4")

text = replace_exact(
    text,
    "nos3_runtime_transaction_v1.py",
    "nos3_runtime_transaction_v2.py",
    2,
    "transaction-v2 path and contract binding",
)

text = replace_one(
    text,
    '"runtime_attempt", "d064_disposition", "exclusive_writer_prerequisite",',
    '"runtime_attempt", "d064_disposition", "host_exclusive_writer_evidence",\n'
    '    "exclusive_writer_controls", "exclusive_writer_prerequisite",',
    "receipt V4 field extension",
)

text = replace_one(
    text,
    '"SATISFIED_DEEP_IMMUTABLE_CONTEXT", "exclusive-writer reference invalid")',
    '"TECHNICAL_CONTROLS_AND_HASH_BOUND_HOST_EVIDENCE_REQUIRED", '
    '"exclusive-writer reference invalid")',
    "receipt exclusive-writer prerequisite successor",
)

anchor = (
    'require(receipt["fortytwo_scratch_present"] is True, '
    '"Fortytwo presence invalid")'
)

validation = r'''
contract_obj = json.loads(open(contract_path, "rb").read().decode("utf-8"))
v4_amendment = contract_obj.get(
    "passive_time_witness_runtime_candidate_v4_design_amendment_1"
)
require(isinstance(v4_amendment, dict), "V4 amendment missing")
v4_impl = v4_amendment.get(
    "passive_time_witness_runtime_candidate_v4_implementation"
)
require(isinstance(v4_impl, dict), "V4 implementation missing")
expected_host_evidence = v4_impl.get("host_exclusive_writer_evidence")
require(
    isinstance(expected_host_evidence, dict),
    "V4 host-evidence contract binding missing",
)

receipt_host_evidence = receipt.get("host_exclusive_writer_evidence")
require(
    isinstance(receipt_host_evidence, dict),
    "receipt host-evidence block missing",
)
require(
    receipt_host_evidence.get("relative_path")
    == expected_host_evidence.get("path"),
    "receipt host-evidence path mismatch",
)
require(
    receipt_host_evidence.get("sha256")
    == expected_host_evidence.get("sha256"),
    "receipt host-evidence SHA mismatch",
)
require(
    receipt_host_evidence.get("schema")
    == expected_host_evidence.get("schema"),
    "receipt host-evidence schema mismatch",
)
require(
    receipt_host_evidence.get("status")
    == expected_host_evidence.get("status"),
    "receipt host-evidence status mismatch",
)

exclusive_controls = receipt.get("exclusive_writer_controls")
require(
    isinstance(exclusive_controls, dict),
    "receipt exclusive-writer controls missing",
)
require(
    exclusive_controls.get("acl_policy")
    == "NO_EXTENDED_ACL_ENTRIES_FOR_FIRST_D064_ATTEMPT",
    "receipt ACL policy mismatch",
)
require(
    exclusive_controls.get("initial_extended_acl_entry_count") == 0,
    "receipt initial ACL entry count mismatch",
)
require(
    exclusive_controls.get("serialization_method")
    == "fcntl.flock_LOCK_EX_LOCK_NB",
    "receipt serialization method mismatch",
)
require(
    exclusive_controls.get("lock_mode") == "0600",
    "receipt serialization lock mode mismatch",
)
require(
    exclusive_controls.get("lock_nlink") == 1,
    "receipt serialization lock nlink mismatch",
)
require(
    exclusive_controls.get("lock_held_through_transaction_finally") is True,
    "receipt lock lifetime claim mismatch",
)
require(
    exclusive_controls.get("advisory_only") is True,
    "receipt advisory-limit marker missing",
)
require(
    exclusive_controls.get(
        "external_noncooperating_writer_absence_proven"
    ) is False,
    "receipt external-writer claim must remain false",
)
'''

text = replace_one(
    text,
    anchor,
    anchor + validation,
    "receipt V4 semantic validation insertion",
)

required = (
    "PASSIVE_TIME_WITNESS_V4_RUNTIME_CANDIDATE",
    "nos3_runtime_transaction_v2.py",
    "--materialize-v4-transaction",
    "host_exclusive_writer_evidence",
    "exclusive_writer_controls",
    "NO_EXTENDED_ACL_ENTRIES_FOR_FIRST_D064_ATTEMPT",
    "fcntl.flock_LOCK_EX_LOCK_NB",
    "external_noncooperating_writer_absence_proven",
    "TECHNICAL_CONTROLS_AND_HASH_BOUND_HOST_EVIDENCE_REQUIRED",
)
for token in required:
    if token not in text:
        raise SystemExit(f"V4 candidate required token missing: {token}")

for forbidden in (
    "nos3_runtime_transaction_v1.py",
    "--materialize-v3-transaction",
    "PASSIVE_TIME_WITNESS_V3_RUNTIME_CANDIDATE",
    "SATISFIED_DEEP_IMMUTABLE_CONTEXT",
):
    if forbidden in text:
        raise SystemExit(f"V4 candidate forbidden historical token: {forbidden}")

output_path.write_text(text, encoding="utf-8", newline="\n")
PYTRANSFORM

bash -n "$tmp_emit" || fail "Generated V4 candidate Bash syntax invalid."

python3 - "$tmp_emit" "$emit_path_real" <<'PYPUBLISH'
import os, sys
source, destination = sys.argv[1:3]
os.link(source, destination, follow_symlinks=False)
os.chmod(destination, 0o700)
os.unlink(source)
PYPUBLISH

echo "PASSIVE_TIME_WITNESS_V4_CANDIDATE_EMITTED=$emit_path_real"
