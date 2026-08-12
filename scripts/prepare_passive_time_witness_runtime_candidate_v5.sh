#!/usr/bin/env bash
# WP4 V5 passive time-witness runtime-candidate generator. EMIT ONLY.
set -Eeuo pipefail

readonly ACCEPTED_V4_GENERATOR_SHA256="5e7cec82032b16edc30a7c0f5d4bfe0a5ddb567ed6a13f6c3075f4db3c97f2a7"
readonly ACCEPTED_TRANSACTION_V3_SHA256="ce1f1f3ad3ba50373e57f36c6490c4ece67f028994155015ed536ce4832fec9e"
readonly ACCEPTED_V3_EVIDENCE_SHA256="c4783f95de24ae309c6fd1c79ea2bc0d27e1dfdb319259351338d0f75c62de9a"

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

emit_path_raw="${PASSIVE_TIME_WITNESS_V5_EMIT_PATH:-}"
[[ -n "$emit_path_raw" ]] || fail "PASSIVE_TIME_WITNESS_V5_EMIT_PATH is required."
command -v python3 >/dev/null 2>&1 || fail "python3 is required."
command -v git >/dev/null 2>&1 || fail "git is required."
command -v bash >/dev/null 2>&1 || fail "bash is required."

repo_root="$(git rev-parse --show-toplevel 2>/dev/null)" ||
  fail "Run the generator from within the governed repository."
repo_root="$(cd "$repo_root" && pwd -P)"
repo_root_real="$(canonicalize "$repo_root")"

v4_generator="$repo_root/scripts/prepare_passive_time_witness_runtime_candidate_v4.sh"
transaction_v3="$repo_root/scripts/nos3_runtime_transaction_v3.py"
v3_evidence="$repo_root/review-evidence/WP4_D064_V4_PRE_D064/host-exclusive-writer-precondition-v3.json"

[[ -f "$v4_generator" && ! -L "$v4_generator" ]] ||
  fail "Protected V4 generator is not a regular file."
[[ "$(shasum -a 256 "$v4_generator" | awk '{print $1}')" == "$ACCEPTED_V4_GENERATOR_SHA256" ]] ||
  fail "Protected V4 generator identity mismatch."

[[ -f "$transaction_v3" && ! -L "$transaction_v3" ]] ||
  fail "Successor transaction-v3 is not a regular file."
[[ "$(shasum -a 256 "$transaction_v3" | awk '{print $1}')" == "$ACCEPTED_TRANSACTION_V3_SHA256" ]] ||
  fail "Successor transaction-v3 identity mismatch."

[[ -f "$v3_evidence" && ! -L "$v3_evidence" ]] ||
  fail "Fresh v3 host evidence is not a regular file."
[[ "$(shasum -a 256 "$v3_evidence" | awk '{print $1}')" == "$ACCEPTED_V3_EVIDENCE_SHA256" ]] ||
  fail "Fresh v3 host-evidence identity mismatch."

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
  *) fail "V5 emission is restricted to the physical system temporary tree." ;;
esac
case "$emit_path_real" in
  "$repo_root_real"|"$repo_root_real"/*)
    fail "V5 emission must not target the repository." ;;
esac
[[ ! -e "$emit_path_real" && ! -L "$emit_path_real" ]] ||
  fail "Emit destination already exists."

umask 077
workdir="$(mktemp -d "$tmp_root_real/.wp4-v5-generator.XXXXXX")"
v4_candidate="$workdir/candidate-v4.sh"
tmp_emit="$(mktemp "$emit_parent_real/.${emit_leaf}.v5.XXXXXX")"

cleanup() {
  rc=$?
  rm -f -- "$v4_candidate" "$tmp_emit"
  rmdir "$workdir" 2>/dev/null || true
  trap - EXIT
  exit "$rc"
}
trap cleanup EXIT

PASSIVE_TIME_WITNESS_V4_EMIT_PATH="$v4_candidate" \
  bash "$v4_generator" >/dev/null

[[ -f "$v4_candidate" && ! -L "$v4_candidate" ]] ||
  fail "V4 base-candidate emission failed."

python3 - "$v4_candidate" "$tmp_emit" <<'PYTRANSFORM'
from pathlib import Path
import sys

source_path = Path(sys.argv[1])
output_path = Path(sys.argv[2])
text = source_path.read_text(encoding="utf-8")

def replace_exact(text, old, new, expected, label):
    count = text.count(old)
    if count != expected:
        raise SystemExit(
            "%s: expected %d source anchors; found %d"
            % (label, expected, count)
        )
    return text.replace(old, new)

text = text.replace("V4", "V5").replace("v4", "v5")

text = replace_exact(
    text,
    "nos3_runtime_transaction_v2.py",
    "nos3_runtime_transaction_v3.py",
    2,
    "transaction-v3 path and binding",
)

text = replace_exact(
    text,
    'expected_host_evidence = v5_impl.get("host_exclusive_writer_evidence")',
    'expected_host_evidence = v5_impl.get("active_host_exclusive_writer_evidence_v3")',
    1,
    "active schema2 evidence selector",
)

anchor = '''require(
    receipt_host_evidence.get("status")
    == expected_host_evidence.get("status"),
    "receipt host-evidence status mismatch",
)
'''

extension = r'''
require(
    receipt_host_evidence.get("evidence_type")
    == expected_host_evidence.get("evidence_type"),
    "receipt host-evidence type mismatch",
)
require(
    receipt_host_evidence.get("size")
    == expected_host_evidence.get("bytes"),
    "receipt host-evidence byte count mismatch",
)
require(
    receipt_host_evidence.get("observed_at_utc")
    == expected_host_evidence.get("observed_at_utc"),
    "receipt host-evidence observed-at mismatch",
)

expected_governance = v5_impl.get("compatibility_governance")
require(
    isinstance(expected_governance, dict),
    "V5 compatibility governance missing",
)
receipt_governance = receipt.get("host_evidence_governance")
require(
    isinstance(receipt_governance, dict),
    "receipt host-evidence governance missing",
)
for key in (
    "decision",
    "contract_version",
    "successor_consumer_path",
    "successor_consumer_sha256",
    "fresh_evidence_independent_review_script_sha256",
    "successor_consumer_independent_review_script_sha256",
    "successor_consumer_independent_review_result",
    "successor_consumer_independent_review_findings",
    "governance_binding_verified",
    "schema2_compatible",
    "schema1_fallback_allowed",
):
    require(
        receipt_governance.get(key) == expected_governance.get(key),
        "receipt host-evidence governance mismatch: " + key,
    )
require(
    receipt_governance.get("contract_sha256")
    == receipt.get("contract", {}).get("sha256"),
    "receipt governance contract SHA mismatch",
)
require(
    expected_governance.get("fresh_evidence_independent_review_script_sha256")
    == expected_host_evidence.get("independent_review_script_sha256"),
    "V5 fresh-evidence review SHA cross-binding mismatch",
)
require(
    expected_governance.get("successor_consumer_independent_review_result") == "PASS",
    "V5 successor-consumer review not PASS",
)
require(
    expected_governance.get("successor_consumer_independent_review_findings") == 0,
    "V5 successor-consumer review findings nonzero",
)
require(expected_governance.get("schema2_compatible") is True,
        "V5 schema2 compatibility not true")
require(expected_governance.get("schema1_fallback_allowed") is False,
        "V5 schema1 fallback must remain false")
require(expected_governance.get("governance_binding_verified") is True,
        "V5 governance binding not verified")
require(expected_host_evidence.get("independent_review_result") == "PASS",
        "V5 evidence review not PASS")
require(expected_host_evidence.get("independent_review_findings") == 0,
        "V5 evidence review findings nonzero")
require(
    expected_host_evidence.get("current_host_reobservation_consistent_with_v3")
    is True,
    "V5 current-host reobservation not true",
)
'''

text = replace_exact(
    text,
    anchor,
    anchor + extension,
    1,
    "V5 receipt-governance validation",
)

required = (
    "PASSIVE_TIME_WITNESS_V5_RUNTIME_CANDIDATE",
    "passive_time_witness_runtime_candidate_v5_contract_schema",
    "passive_time_witness_runtime_candidate_v5_static_verification",
    "accepted_runtime_entrypoint_v5_sha256",
    "nos3_runtime_transaction_v3.py",
    "--materialize-v5-transaction",
    "active_host_exclusive_writer_evidence_v3",
    "compatibility_governance",
    "host_evidence_governance",
    "schema1_fallback_allowed",
    "schema2_compatible",
    "fresh_evidence_independent_review_script_sha256",
    "successor_consumer_independent_review_script_sha256",
    "successor_consumer_independent_review_result",
    "successor_consumer_independent_review_findings",
    "external_noncooperating_writer_absence_proven",
)
for token in required:
    if token not in text:
        raise SystemExit("V5 candidate required token missing: " + token)

for forbidden in (
    "nos3_runtime_transaction_v2.py",
    "--materialize-v4-transaction",
    "PASSIVE_TIME_WITNESS_V4_RUNTIME_CANDIDATE",
):
    if forbidden in text:
        raise SystemExit("V5 candidate forbidden production token: " + forbidden)

output_path.write_text(text, encoding="utf-8", newline="\n")
PYTRANSFORM

bash -n "$tmp_emit" || fail "Generated V5 candidate Bash syntax invalid."

python3 - "$tmp_emit" "$emit_path_real" <<'PYPUBLISH'
import os, sys
source, destination = sys.argv[1:3]
os.link(source, destination, follow_symlinks=False)
os.chmod(destination, 0o700)
os.unlink(source)
PYPUBLISH

echo "PASSIVE_TIME_WITNESS_V5_CANDIDATE_EMITTED=$emit_path_real"
