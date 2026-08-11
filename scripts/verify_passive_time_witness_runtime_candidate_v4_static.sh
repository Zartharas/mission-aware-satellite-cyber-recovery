#!/usr/bin/env bash
# WP4 V4 passive time-witness runtime-candidate STATIC VERIFIER.
# --selftest is authorized in source implementation. Production --verify is not.
set -Eeuo pipefail

readonly ACCEPTED_GENERATOR_SHA256="5e7cec82032b16edc30a7c0f5d4bfe0a5ddb567ed6a13f6c3075f4db3c97f2a7"
readonly ACCEPTED_GENERATOR_PATH="scripts/prepare_passive_time_witness_runtime_candidate_v4.sh"
readonly ACCEPTED_TRANSACTION_V2_SHA256="7419fa18b891ddc7525fa237b12323a092b9ece0f44d5b6fa4069c614322ce29"
readonly ACCEPTED_TRANSACTION_V2_PATH="scripts/nos3_runtime_transaction_v2.py"
readonly ACCEPTED_MANIFEST_SHA256="5026176de3084c8015fd7f84827ce8a4e5d44df7e986bc142815eb0d649e81cd"
readonly ACCEPTED_MANIFEST_PATH="manifests/nos3-runtime-material-manifest.json"
readonly REQUIRED_CONTRACT_VERSION="0.4.14"
readonly REQUIRED_V4_SCHEMA="1"
readonly PASS_MARKER="V4_STATIC_VERIFICATION=PASS"

mode=""
repo_root=""
contract_path=""
candidate_path=""
report_dir=""

while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --selftest)
      [[ -z "$mode" ]] || { echo "conflicting mode" >&2; exit 2; }
      mode="selftest"; shift ;;
    --verify)
      [[ -z "$mode" ]] || { echo "conflicting mode" >&2; exit 2; }
      mode="verify"; shift ;;
    --repo-root) repo_root="${2:-}"; shift 2 ;;
    --contract) contract_path="${2:-}"; shift 2 ;;
    --candidate) candidate_path="${2:-}"; shift 2 ;;
    --report-dir) report_dir="${2:-}"; shift 2 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

[[ -n "$mode" ]] || { echo "missing mode" >&2; exit 2; }
if [[ "$mode" == "verify" ]]; then
  [[ -n "$repo_root" && -n "$contract_path" && -n "$candidate_path" && -n "$report_dir" ]] ||
    { echo "missing --verify arguments" >&2; exit 2; }
fi

export V4_VERIFIER_MODE="$mode"
export V4_VERIFIER_REPO_ROOT="$repo_root"
export V4_VERIFIER_CONTRACT="$contract_path"
export V4_VERIFIER_CANDIDATE="$candidate_path"
export V4_VERIFIER_REPORT_DIR="$report_dir"
export V4_VERIFIER_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)/$(basename "${BASH_SOURCE[0]}")"
export V4_VERIFIER_ACCEPTED_GENERATOR_SHA256="$ACCEPTED_GENERATOR_SHA256"
export V4_VERIFIER_ACCEPTED_TRANSACTION_SHA256="$ACCEPTED_TRANSACTION_V2_SHA256"
export V4_VERIFIER_ACCEPTED_MANIFEST_SHA256="$ACCEPTED_MANIFEST_SHA256"

python3 - <<'PYENGINE'
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile

MODE = os.environ["V4_VERIFIER_MODE"]
VERIFIER_PATH = Path(os.environ["V4_VERIFIER_PATH"])
EXPECTED_GENERATOR_SHA = os.environ["V4_VERIFIER_ACCEPTED_GENERATOR_SHA256"]
EXPECTED_TRANSACTION_SHA = os.environ["V4_VERIFIER_ACCEPTED_TRANSACTION_SHA256"]
EXPECTED_MANIFEST_SHA = os.environ["V4_VERIFIER_ACCEPTED_MANIFEST_SHA256"]

GEN_REL = "scripts/prepare_passive_time_witness_runtime_candidate_v4.sh"
TX_REL = "scripts/nos3_runtime_transaction_v2.py"
MAN_REL = "manifests/nos3-runtime-material-manifest.json"
VER_REL = "scripts/verify_passive_time_witness_runtime_candidate_v4_static.sh"

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def read_regular(path):
    path = Path(path)
    st = os.lstat(path)
    if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1:
        raise RuntimeError("not single-link regular file: %s" % path)
    raw = path.read_bytes()
    st2 = os.lstat(path)
    if (st.st_dev, st.st_ino, st.st_mode, st.st_nlink, st.st_size) != (
        st2.st_dev, st2.st_ino, st2.st_mode, st2.st_nlink, st2.st_size
    ):
        raise RuntimeError("file identity changed during read: %s" % path)
    if len(raw) != st.st_size:
        raise RuntimeError("file size/read mismatch: %s" % path)
    return raw

def candidate_findings(text):
    findings = []
    required = (
        "PASSIVE_TIME_WITNESS_V4_RUNTIME_CANDIDATE",
        "passive_time_witness_runtime_candidate_v4_contract_schema",
        "passive_time_witness_runtime_candidate_v4_static_verification",
        "accepted_runtime_entrypoint_v4_sha256",
        "nos3_runtime_transaction_v2.py",
        "--materialize-v4-transaction",
        "host_exclusive_writer_evidence",
        "exclusive_writer_controls",
        "NO_EXTENDED_ACL_ENTRIES_FOR_FIRST_D064_ATTEMPT",
        "fcntl.flock_LOCK_EX_LOCK_NB",
        "external_noncooperating_writer_absence_proven",
        "TECHNICAL_CONTROLS_AND_HASH_BOUND_HOST_EVIDENCE_REQUIRED",
    )
    forbidden = (
        "nos3_runtime_transaction_v1.py",
        "--materialize-v3-transaction",
        "PASSIVE_TIME_WITNESS_V3_RUNTIME_CANDIDATE",
        "SATISFIED_DEEP_IMMUTABLE_CONTEXT",
    )
    for token in required:
        if token not in text:
            findings.append("missing:" + token)
    for token in forbidden:
        if token in text:
            findings.append("forbidden:" + token)
    return findings

def validate_contract(contract, candidate_sha, generator_sha, verifier_sha):
    findings = []
    def need(condition, code):
        if not condition:
            findings.append(code)

    need(type(contract) is dict, "contract_not_object")
    if type(contract) is not dict:
        return findings
    need(contract.get("contract_version") == "0.4.14", "wrong_contract_version")

    for key in (
        "scientific_outcome_allowed",
        "event_injection_allowed",
        "command_transmission_allowed",
        "baseline_execution_allowed",
        "cryptographic_semantics_claim_allowed",
    ):
        need(type(contract.get(key)) is bool and contract[key] is False,
             "permission_open:" + key)

    gate = contract.get("gate")
    need(type(gate) is dict, "gate_missing")
    if type(gate) is not dict:
        return findings

    need(
        type(gate.get("passive_time_witness_runtime_candidate_v4_contract_schema")) is int
        and gate["passive_time_witness_runtime_candidate_v4_contract_schema"] == 1,
        "v4_schema",
    )
    need(
        gate.get("passive_time_witness_runtime_candidate_v4_static_verification")
        == "PENDING",
        "v4_static_not_pending",
    )
    need(gate.get("accepted_runtime_entrypoint_v4_sha256") == "",
         "accepted_v4_not_empty")
    need(gate.get("accepted_runtime_entrypoint_v4_identity_only_not_authorized") is False,
         "accepted_identity_flag")
    need(gate.get("proposed_runtime_entrypoint_v4_sha256") == candidate_sha,
         "proposed_candidate_mismatch")
    need(gate.get("diagnostic_runtime_authorized") is False,
         "runtime_authorized")
    need(
        type(gate.get("diagnostic_runtime_attempts_authorized")) is int
        and gate["diagnostic_runtime_attempts_authorized"] == 0,
        "runtime_attempts",
    )
    for key in (
        "baseline_run_1_authorized",
        "baseline_run_2_authorized",
        "event_injection_authorized",
    ):
        need(gate.get(key) is False, "gate_permission_open:" + key)

    amendment = contract.get(
        "passive_time_witness_runtime_candidate_v4_design_amendment_1"
    )
    need(type(amendment) is dict, "v4_amendment_missing")
    if type(amendment) is not dict:
        return findings

    need(amendment.get("runtime_authorized") is False,
         "amendment_runtime_authorized")
    need(
        type(amendment.get("runtime_attempts")) is int
        and amendment["runtime_attempts"] == 0,
        "amendment_runtime_attempts",
    )
    need(
        amendment.get("d064_status")
        == "BLOCKED_PENDING_V4_STATIC_VERIFICATION_AND_SEPARATE_D064_DECISION",
        "amendment_d064_status",
    )

    impl = amendment.get(
        "passive_time_witness_runtime_candidate_v4_implementation"
    )
    need(type(impl) is dict, "v4_impl_missing")
    if type(impl) is not dict:
        return findings

    def identity(name, path, expected_sha):
        obj = impl.get(name)
        need(type(obj) is dict, name + "_missing")
        if type(obj) is dict:
            need(obj.get("path") == path, name + "_path")
            need(obj.get("sha256") == expected_sha, name + "_sha")

    identity("runtime_candidate_generator", GEN_REL, generator_sha)
    identity("runtime_material_tool", TX_REL, EXPECTED_TRANSACTION_SHA)
    identity("canonical_manifest", MAN_REL, EXPECTED_MANIFEST_SHA)
    identity("static_verifier", VER_REL, verifier_sha)

    generated = impl.get("generated_runtime_candidate_v4")
    need(type(generated) is dict, "generated_v4_missing")
    if type(generated) is dict:
        need(
            generated.get("path") == "TEMPORARY_DETERMINISTIC_EMISSION_ONLY",
            "generated_v4_path",
        )
        need(generated.get("sha256") == candidate_sha, "generated_v4_sha")
        need(generated.get("accepted") is False, "generated_v4_accepted")

    evidence = impl.get("host_exclusive_writer_evidence")
    need(type(evidence) is dict, "host_evidence_missing")
    if type(evidence) is dict:
        need(evidence.get("path") == "", "host_evidence_path_not_empty")
        need(evidence.get("sha256") == "", "host_evidence_sha_not_empty")
        need(type(evidence.get("schema")) is int and evidence["schema"] == 1,
             "host_evidence_schema")
        need(evidence.get("status") == "NOT_CREATED_NOT_AUTHORIZED",
             "host_evidence_status")
    return findings

def transaction_semantics(path):
    findings = []
    if sha256(path) != EXPECTED_TRANSACTION_SHA:
        return ["transaction_hash"]
    text = Path(path).read_text(encoding="utf-8")
    for token in (
        "NO_EXTENDED_ACL_ENTRIES_FOR_FIRST_D064_ATTEMPT",
        ".wp4-d064-v4-transaction.lock",
        "fcntl.LOCK_EX|fcntl.LOCK_NB",
        "host_exclusive_writer_evidence",
        "external_noncooperating_writer_absence_proven",
    ):
        if token not in text:
            findings.append("transaction_missing:" + token)
    banned = "SATISFIED_DEEP_" + "IMMUTABLE_CONTEXT"
    if banned in text:
        findings.append("legacy_exclusive_writer_overclaim")
    return findings

def emit_twice(generator, repo):
    physical_tmp = os.path.realpath(tempfile.gettempdir())
    root = tempfile.mkdtemp(prefix="wp4-v4-verifier-", dir=physical_tmp)
    try:
        outputs = []
        for leaf in ("candidate-a.sh", "candidate-b.sh"):
            p = os.path.join(root, leaf)
            env = os.environ.copy()
            env["PASSIVE_TIME_WITNESS_V4_EMIT_PATH"] = p
            cp = subprocess.run(
                ["bash", str(generator)],
                cwd=str(repo),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if cp.returncode != 0:
                raise RuntimeError(
                    "generator failed rc=%d stderr=%s"
                    % (cp.returncode, cp.stderr.strip())
                )
            outputs.append(Path(p).read_bytes())
        if outputs[0] != outputs[1]:
            raise RuntimeError("generator double emission differs")
        return outputs[0]
    finally:
        shutil.rmtree(root, ignore_errors=True)

def run_bash_n(path):
    cp = subprocess.run(
        ["bash", "-n", str(path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if cp.returncode != 0:
        raise RuntimeError("bash -n failed: " + cp.stderr.strip())

def run_selftest():
    repo = Path(
        subprocess.check_output(
            ["/usr/bin/git", "rev-parse", "--show-toplevel"],
            text=True,
        ).strip()
    ).resolve()
    generator = Path(
        os.environ.get(
            "V4_VERIFIER_SELFTEST_GENERATOR",
            str(repo / GEN_REL),
        )
    ).resolve()
    transaction = (repo / TX_REL).resolve()

    results = []
    def check(name, fn):
        try:
            ok = fn()
            if ok is False:
                raise RuntimeError("returned false")
            results.append((name, "PASS", ""))
        except Exception as exc:
            results.append((name, "FAIL", str(exc)))

    check("transaction_exact_sha",
          lambda: sha256(transaction) == EXPECTED_TRANSACTION_SHA)

    # The 205-test transaction-v2 suite is replayed by the implementation gate
    # before the live contract transitions from 0.4.13 to 0.4.14. Verifier-v4
    # selftest therefore binds the reviewed V2 SHA plus required V4 source
    # semantics rather than treating the historical suite as a live invariant.
    def transaction_reviewed_semantics():
        return transaction_semantics(transaction) == []
    check("transaction_reviewed_semantics", transaction_reviewed_semantics)

    check("generator_exact_sha",
          lambda: sha256(generator) == EXPECTED_GENERATOR_SHA)

    emitted = {"bytes": None}
    def deterministic():
        emitted["bytes"] = emit_twice(generator, repo)
        return True
    check("generator_double_emission", deterministic)

    def syntax():
        root = tempfile.mkdtemp(prefix="wp4-v4-verifier-syntax-")
        try:
            p = Path(root) / "candidate.sh"
            p.write_bytes(emitted["bytes"])
            run_bash_n(p)
            return True
        finally:
            shutil.rmtree(root, ignore_errors=True)
    check("candidate_bash_syntax", syntax)

    check(
        "candidate_source_accept",
        lambda: candidate_findings(
            emitted["bytes"].decode("utf-8")
        ) == [],
    )

    def historical_rejected():
        text = emitted["bytes"].decode("utf-8").replace(
            "nos3_runtime_transaction_v2.py",
            "nos3_runtime_transaction_v1.py",
            1,
        )
        return bool(candidate_findings(text))
    check("candidate_v1_transaction_rejected", historical_rejected)

    def evidence_required():
        text = emitted["bytes"].decode("utf-8").replace(
            "host_exclusive_writer_evidence",
            "host_evidence_removed",
        )
        return bool(candidate_findings(text))
    check("candidate_host_evidence_controls_required", evidence_required)

    good_contract = {
        "contract_version": "0.4.14",
        "scientific_outcome_allowed": False,
        "event_injection_allowed": False,
        "command_transmission_allowed": False,
        "baseline_execution_allowed": False,
        "cryptographic_semantics_claim_allowed": False,
        "gate": {
            "passive_time_witness_runtime_candidate_v4_contract_schema": 1,
            "passive_time_witness_runtime_candidate_v4_static_verification": "PENDING",
            "accepted_runtime_entrypoint_v4_sha256": "",
            "accepted_runtime_entrypoint_v4_identity_only_not_authorized": False,
            "proposed_runtime_entrypoint_v4_sha256": "a" * 64,
            "diagnostic_runtime_authorized": False,
            "diagnostic_runtime_attempts_authorized": 0,
            "baseline_run_1_authorized": False,
            "baseline_run_2_authorized": False,
            "event_injection_authorized": False,
        },
        "passive_time_witness_runtime_candidate_v4_design_amendment_1": {
            "runtime_authorized": False,
            "runtime_attempts": 0,
            "d064_status":
                "BLOCKED_PENDING_V4_STATIC_VERIFICATION_AND_SEPARATE_D064_DECISION",
            "passive_time_witness_runtime_candidate_v4_implementation": {
                "runtime_candidate_generator": {
                    "path": GEN_REL,
                    "sha256": EXPECTED_GENERATOR_SHA,
                },
                "runtime_material_tool": {
                    "path": TX_REL,
                    "sha256": EXPECTED_TRANSACTION_SHA,
                },
                "canonical_manifest": {
                    "path": MAN_REL,
                    "sha256": EXPECTED_MANIFEST_SHA,
                },
                "static_verifier": {
                    "path": VER_REL,
                    "sha256": "b" * 64,
                },
                "generated_runtime_candidate_v4": {
                    "path": "TEMPORARY_DETERMINISTIC_EMISSION_ONLY",
                    "sha256": "a" * 64,
                    "accepted": False,
                },
                "host_exclusive_writer_evidence": {
                    "path": "",
                    "sha256": "",
                    "schema": 1,
                    "status": "NOT_CREATED_NOT_AUTHORIZED",
                },
            },
        },
    }

    check(
        "contract_implementation_state_accept",
        lambda: validate_contract(
            good_contract,
            "a" * 64,
            EXPECTED_GENERATOR_SHA,
            "b" * 64,
        ) == [],
    )

    def contract_mutations():
        mutations = (
            (("gate", "diagnostic_runtime_authorized"), True),
            (("gate", "diagnostic_runtime_attempts_authorized"), 1),
            (
                (
                    "gate",
                    "passive_time_witness_runtime_candidate_v4_static_verification",
                ),
                "PASS",
            ),
            (
                (
                    "passive_time_witness_runtime_candidate_v4_design_amendment_1",
                    "d064_status",
                ),
                "AUTHORIZED_FOR_ONE_BOUNDED_PASSIVE_ATTEMPT",
            ),
        )
        rejected = []
        for path, value in mutations:
            c = copy.deepcopy(good_contract)
            cur = c
            for key in path[:-1]:
                cur = cur[key]
            cur[path[-1]] = value
            rejected.append(
                bool(
                    validate_contract(
                        c,
                        "a" * 64,
                        EXPECTED_GENERATOR_SHA,
                        "b" * 64,
                    )
                )
            )
        return all(rejected)
    check("contract_open_gate_mutations_rejected", contract_mutations)

    failed = [r for r in results if r[1] != "PASS"]
    for name, status, detail in results:
        print(
            "  %-48s %s%s"
            % (name, status, (" " + detail) if detail else "")
        )
    print(
        "SELFTEST passed=%d failed=%d skips=0"
        % (len(results) - len(failed), len(failed))
    )
    return 0 if not failed and len(results) == 10 else 1

def run_verify():
    repo = Path(os.environ["V4_VERIFIER_REPO_ROOT"]).resolve()
    contract_path = Path(os.environ["V4_VERIFIER_CONTRACT"]).resolve()
    candidate_path = Path(os.environ["V4_VERIFIER_CANDIDATE"]).resolve()
    report_dir = Path(os.environ["V4_VERIFIER_REPORT_DIR"]).resolve()

    generator = repo / GEN_REL
    transaction = repo / TX_REL
    manifest = repo / MAN_REL

    if sha256(generator) != EXPECTED_GENERATOR_SHA:
        raise RuntimeError("generator identity mismatch")
    if sha256(transaction) != EXPECTED_TRANSACTION_SHA:
        raise RuntimeError("transaction identity mismatch")
    if sha256(manifest) != EXPECTED_MANIFEST_SHA:
        raise RuntimeError("manifest identity mismatch")

    candidate_raw = read_regular(candidate_path)
    candidate_sha = hashlib.sha256(candidate_raw).hexdigest()
    verifier_sha = sha256(VERIFIER_PATH)
    contract = json.loads(read_regular(contract_path).decode("utf-8"))

    findings = validate_contract(
        contract, candidate_sha, EXPECTED_GENERATOR_SHA, verifier_sha
    )
    if findings:
        raise RuntimeError("contract findings: " + ",".join(findings))

    generated = emit_twice(generator, repo)
    if hashlib.sha256(generated).hexdigest() != candidate_sha:
        raise RuntimeError("deterministic generator candidate hash mismatch")
    if generated != candidate_raw:
        raise RuntimeError("generated candidate bytes differ from candidate")

    run_bash_n(candidate_path)

    findings = candidate_findings(candidate_raw.decode("utf-8"))
    if findings:
        raise RuntimeError("candidate source findings: " + ",".join(findings))

    tx_findings = transaction_semantics(transaction)
    if tx_findings:
        raise RuntimeError(
            "transaction source findings: " + ",".join(tx_findings)
        )

    report_dir.mkdir(parents=True, exist_ok=False)
    report = {
        "schema": 1,
        "status": "PASS",
        "contract_version": "0.4.14",
        "candidate_sha256": candidate_sha,
        "generator_sha256": EXPECTED_GENERATOR_SHA,
        "transaction_v2_sha256": EXPECTED_TRANSACTION_SHA,
        "manifest_sha256": EXPECTED_MANIFEST_SHA,
        "verifier_sha256": verifier_sha,
        "candidate_executed": False,
        "docker_invoked": False,
        "runtime_authorized": False,
        "d064_authorized": False,
    }
    raw = (
        json.dumps(
            report,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")
    (report_dir / "v4-static-verification.json").write_bytes(raw)
    print("V4_STATIC_VERIFICATION=PASS")
    return 0

if MODE == "selftest":
    raise SystemExit(run_selftest())

try:
    raise SystemExit(run_verify())
except Exception as exc:
    print("V4_STATIC_VERIFICATION=FAIL_CLOSED", file=sys.stderr)
    print(str(exc), file=sys.stderr)
    raise SystemExit(4)
PYENGINE
