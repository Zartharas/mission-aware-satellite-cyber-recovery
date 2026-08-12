#!/usr/bin/env bash
# WP4 V5 passive time-witness runtime-candidate STATIC VERIFIER.
# --selftest is authorized in source implementation.
# Production --verify requires a later separate authorization.
set -Eeuo pipefail

readonly ACCEPTED_GENERATOR_SHA256="9f006bc7e13e73b9702d2f63c5d97413a77151af0a9d63e3ed88d3cba121bed7"
readonly ACCEPTED_GENERATOR_PATH="scripts/prepare_passive_time_witness_runtime_candidate_v5.sh"
readonly ACCEPTED_TRANSACTION_V3_SHA256="ce1f1f3ad3ba50373e57f36c6490c4ece67f028994155015ed536ce4832fec9e"
readonly ACCEPTED_TRANSACTION_V3_PATH="scripts/nos3_runtime_transaction_v3.py"
readonly ACCEPTED_TRANSACTION_V2_SHA256="7419fa18b891ddc7525fa237b12323a092b9ece0f44d5b6fa4069c614322ce29"
readonly ACCEPTED_TRANSACTION_V2_PATH="scripts/nos3_runtime_transaction_v2.py"
readonly ACCEPTED_V3_EVIDENCE_SHA256="c4783f95de24ae309c6fd1c79ea2bc0d27e1dfdb319259351338d0f75c62de9a"
readonly ACCEPTED_V3_EVIDENCE_PATH="review-evidence/WP4_D064_V4_PRE_D064/host-exclusive-writer-precondition-v3.json"
readonly ACCEPTED_MANIFEST_SHA256="5026176de3084c8015fd7f84827ce8a4e5d44df7e986bc142815eb0d649e81cd"
readonly ACCEPTED_MANIFEST_PATH="manifests/nos3-runtime-material-manifest.json"
readonly PASS_MARKER="V5_STATIC_VERIFICATION=PASS"

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

export V5_VERIFIER_MODE="$mode"
export V5_VERIFIER_REPO_ROOT="$repo_root"
export V5_VERIFIER_CONTRACT="$contract_path"
export V5_VERIFIER_CANDIDATE="$candidate_path"
export V5_VERIFIER_REPORT_DIR="$report_dir"
export V5_VERIFIER_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)/$(basename "${BASH_SOURCE[0]}")"
export V5_VERIFIER_GENERATOR_SHA="$ACCEPTED_GENERATOR_SHA256"
export V5_VERIFIER_TX3_SHA="$ACCEPTED_TRANSACTION_V3_SHA256"
export V5_VERIFIER_TX2_SHA="$ACCEPTED_TRANSACTION_V2_SHA256"

python3 - <<'PYENGINE'
import ast
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

MODE = os.environ["V5_VERIFIER_MODE"]
GEN_SHA = os.environ["V5_VERIFIER_GENERATOR_SHA"]
TX3_SHA = os.environ["V5_VERIFIER_TX3_SHA"]
TX2_SHA = os.environ["V5_VERIFIER_TX2_SHA"]

GEN_REL = "scripts/prepare_passive_time_witness_runtime_candidate_v5.sh"
TX3_REL = "scripts/nos3_runtime_transaction_v3.py"
TX2_REL = "scripts/nos3_runtime_transaction_v2.py"
V3_REL = "review-evidence/WP4_D064_V4_PRE_D064/host-exclusive-writer-precondition-v3.json"

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def candidate_findings(text):
    findings = []
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
    forbidden = (
        "nos3_runtime_transaction_v2.py",
        "--materialize-v4-transaction",
        "PASSIVE_TIME_WITNESS_V4_RUNTIME_CANDIDATE",
    )
    for token in required:
        if token not in text:
            findings.append("missing:" + token)
    for token in forbidden:
        if token in text:
            findings.append("forbidden:" + token)
    return findings

def transaction_findings(path):
    findings = []
    if sha256(path) != TX3_SHA:
        return ["transaction_v3_hash"]
    text = Path(path).read_text(encoding="utf-8")
    tree = ast.parse(text)
    functions = {
        n.name: n
        for n in tree.body
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    for fn in (
        "_validate_host_exclusive_writer_evidence_v5",
        "_validate_structured_authorization_v5",
        "_run_authorize_v5",
        "_v5_compat_selftest",
        "_build_argparser",
    ):
        if fn not in functions:
            findings.append("missing_function:" + fn)
    parser_node = functions.get("_build_argparser")
    if parser_node is None:
        parser = ""
    else:
        parser = ast.get_source_segment(text, parser_node) or ""
    if "--materialize-v4-transaction" in parser:
        findings.append("v4_production_fallback_exposed")
    if "--materialize-v5-transaction" not in parser:
        findings.append("v5_production_cli_missing")
    for token in (
        "_V5_HOST_EVIDENCE_SCHEMA = 2",
        "_V5_SCHEMA1_PRODUCTION_FALLBACK_ALLOWED = False",
        "active_host_exclusive_writer_evidence_v3",
        "passive_time_witness_runtime_candidate_v4_fresh_successor_host_evidence_governance_2",
        "compatibility_governance",
        "governance_binding_verified",
    ):
        if token not in text:
            findings.append("missing_token:" + token)
    return findings

def emit_twice(generator, repo):
    root = tempfile.mkdtemp(
        prefix="wp4-v5-verifier-",
        dir=os.path.realpath(tempfile.gettempdir()),
    )
    try:
        outputs = []
        for leaf in ("candidate-a.sh", "candidate-b.sh"):
            path = os.path.join(root, leaf)
            env = os.environ.copy()
            env["PASSIVE_TIME_WITNESS_V5_EMIT_PATH"] = path
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
                    "generator rc=%d stderr=%s"
                    % (cp.returncode, cp.stderr.strip())
                )
            outputs.append(Path(path).read_bytes())
        if outputs[0] != outputs[1]:
            raise RuntimeError("V5 generator double emission differs")
        return outputs[0]
    finally:
        shutil.rmtree(root, ignore_errors=True)

def current_contract_fail_closed(repo):
    contract = json.loads(
        (repo / "configs/downlink-diagnostic-contract.json").read_text(
            encoding="utf-8"
        )
    )
    return (
        contract.get("contract_version") == "0.4.17"
        and contract.get("gate", {}).get(
            "passive_time_witness_runtime_candidate_v5_contract_schema"
        ) is None
        and contract.get(
            "passive_time_witness_runtime_candidate_v5_design_amendment_1"
        ) is None
        and contract[
            "passive_time_witness_runtime_candidate_v4_design_amendment_1"
        ]["d064_status"]
        == "BLOCKED_PENDING_FRESH_HOST_EVIDENCE_CONSUMER_SCHEMA_COMPATIBILITY_REMEDIATION"
    )

def run_selftest():
    repo = Path(
        subprocess.check_output(
            ["/usr/bin/git", "rev-parse", "--show-toplevel"],
            text=True,
        ).strip()
    ).resolve()
    generator = repo / GEN_REL
    tx3 = repo / TX3_REL
    tx2 = repo / TX2_REL
    v3 = repo / V3_REL

    results = []
    def check(name, fn):
        try:
            if fn() is False:
                raise RuntimeError("returned false")
            results.append((name, "PASS", ""))
        except Exception as exc:
            results.append((name, "FAIL", str(exc)))

    check("transaction_v3_exact_sha", lambda: sha256(tx3) == TX3_SHA)
    check("transaction_v2_predecessor_immutable", lambda: sha256(tx2) == TX2_SHA)
    check("v3_evidence_exact_sha", lambda: sha256(v3) == "c4783f95de24ae309c6fd1c79ea2bc0d27e1dfdb319259351338d0f75c62de9a")
    check("transaction_v5_semantics", lambda: transaction_findings(tx3) == [])
    check("generator_exact_sha", lambda: sha256(generator) == GEN_SHA)

    def tx_v5_selftest():
        cp = subprocess.run(
            [sys.executable, str(tx3), "--v5-compat-selftest"],
            cwd=str(repo),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if cp.returncode != 0:
            raise RuntimeError(cp.stdout + "\n" + cp.stderr)
        if "V5_COMPAT_SELFTEST" not in cp.stdout or "failed=0" not in cp.stdout:
            raise RuntimeError("transaction-v3 V5 selftest did not report zero failures")
        return True
    check("transaction_v3_v5_compat_selftest", tx_v5_selftest)

    emitted = {"raw": None}
    def deterministic():
        emitted["raw"] = emit_twice(generator, repo)
        return True
    check("generator_double_emission", deterministic)

    def syntax():
        root = tempfile.mkdtemp(prefix="wp4-v5-syntax-")
        try:
            p = Path(root) / "candidate.sh"
            p.write_bytes(emitted["raw"])
            cp = subprocess.run(
                ["bash", "-n", str(p)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if cp.returncode != 0:
                raise RuntimeError(cp.stderr)
            return True
        finally:
            shutil.rmtree(root, ignore_errors=True)
    check("candidate_bash_syntax", syntax)
    check(
        "candidate_source_accept",
        lambda: candidate_findings(emitted["raw"].decode("utf-8")) == [],
    )

    def tx2_rejected():
        mutated = emitted["raw"].decode("utf-8").replace(
            "nos3_runtime_transaction_v3.py",
            "nos3_runtime_transaction_v2.py",
            1,
        )
        return bool(candidate_findings(mutated))
    check("candidate_transaction_v2_rejected", tx2_rejected)

    def active_binding_required():
        mutated = emitted["raw"].decode("utf-8").replace(
            "active_host_exclusive_writer_evidence_v3",
            "host_exclusive_writer_evidence",
        )
        return bool(candidate_findings(mutated))
    check("candidate_active_schema2_binding_required", active_binding_required)

    check(
        "current_contract_remains_v5_fail_closed",
        lambda: current_contract_fail_closed(repo),
    )

    passed = sum(1 for _, status, _ in results if status == "PASS")
    failed = len(results) - passed
    return passed, failed, results

def run_verify():
    # This future production static-verification path is source-complete but is
    # not exercised by the source-implementation authorization.
    repo = Path(os.environ["V5_VERIFIER_REPO_ROOT"]).resolve()
    contract_path = Path(os.environ["V5_VERIFIER_CONTRACT"]).resolve()
    candidate_path = Path(os.environ["V5_VERIFIER_CANDIDATE"]).resolve()
    report_dir = Path(os.environ["V5_VERIFIER_REPORT_DIR"]).resolve()
    generator = repo / GEN_REL
    tx3 = repo / TX3_REL
    tx2 = repo / TX2_REL
    v3 = repo / V3_REL

    for path, expected in (
        (generator, GEN_SHA),
        (tx3, TX3_SHA),
        (tx2, TX2_SHA),
        (v3, "c4783f95de24ae309c6fd1c79ea2bc0d27e1dfdb319259351338d0f75c62de9a"),
    ):
        if sha256(path) != expected:
            raise RuntimeError("identity mismatch: " + str(path))

    candidate_raw = candidate_path.read_bytes()
    candidate_text = candidate_raw.decode("utf-8")
    if candidate_findings(candidate_text):
        raise RuntimeError("candidate source findings")
    cp = subprocess.run(
        ["bash", "-n", str(candidate_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if cp.returncode != 0:
        raise RuntimeError("candidate Bash syntax invalid")

    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    gate = contract.get("gate", {})
    if gate.get("passive_time_witness_runtime_candidate_v5_static_verification") != "PENDING":
        raise RuntimeError("V5 pre-static contract not PENDING")
    if gate.get("diagnostic_runtime_authorized") is not False:
        raise RuntimeError("runtime must remain unauthorized during V5 static verification")
    if gate.get("diagnostic_runtime_attempts_authorized") != 0:
        raise RuntimeError("runtime attempts must remain zero during V5 static verification")
    amendment = contract.get(
        "passive_time_witness_runtime_candidate_v5_design_amendment_1", {}
    )
    if amendment.get("runtime_authorized") is not False:
        raise RuntimeError("V5 amendment runtime must remain false")
    if amendment.get("runtime_attempts") != 0:
        raise RuntimeError("V5 amendment runtime attempts must remain zero")
    if amendment.get("d064_status") != (
        "BLOCKED_PENDING_V5_STATIC_VERIFICATION_AND_SEPARATE_D064_DECISION"
    ):
        raise RuntimeError("V5 D064 pre-static status mismatch")
    impl = amendment.get("passive_time_witness_runtime_candidate_v5_implementation")
    if not isinstance(impl, dict):
        raise RuntimeError("V5 implementation missing")
    for key, expected_path, expected_sha in (
        ("runtime_candidate_generator", GEN_REL, GEN_SHA),
        ("runtime_material_tool", TX3_REL, TX3_SHA),
    ):
        obj = impl.get(key)
        if not isinstance(obj, dict):
            raise RuntimeError("V5 identity binding missing: " + key)
        if obj.get("path") != expected_path or obj.get("sha256") != expected_sha:
            raise RuntimeError("V5 identity binding mismatch: " + key)
    evidence = impl.get("active_host_exclusive_writer_evidence_v3")
    if not isinstance(evidence, dict):
        raise RuntimeError("V5 active v3 evidence binding missing")
    for key, expected in (
        ("path", V3_REL),
        ("sha256", "c4783f95de24ae309c6fd1c79ea2bc0d27e1dfdb319259351338d0f75c62de9a"),
        ("bytes", 8400),
        ("schema", 2),
        ("evidence_type", "D064_HOST_EXCLUSIVE_WRITER_PRECONDITION_REFRESH"),
        ("status", "CAPTURED_FRESH_SUCCESSOR_PRECONDITION_EVIDENCE_PENDING_INDEPENDENT_REVIEW_NOT_D064_AUTHORITY"),
        ("independent_review_result", "PASS"),
        ("independent_review_findings", 0),
        ("current_host_reobservation_consistent_with_v3", True),
    ):
        if evidence.get(key) != expected:
            raise RuntimeError("V5 active v3 evidence mismatch: " + key)
    governance = impl.get("compatibility_governance")
    if not isinstance(governance, dict):
        raise RuntimeError("V5 compatibility governance missing")
    if governance.get("successor_consumer_path") != TX3_REL:
        raise RuntimeError("V5 successor consumer path mismatch")
    if governance.get("successor_consumer_sha256") != TX3_SHA:
        raise RuntimeError("V5 successor consumer SHA mismatch")
    if (
        governance.get("fresh_evidence_independent_review_script_sha256")
        != evidence.get("independent_review_script_sha256")
    ):
        raise RuntimeError("V5 fresh-evidence review SHA cross-binding mismatch")
    review_sha = governance.get("successor_consumer_independent_review_script_sha256")
    if (
        not isinstance(review_sha, str)
        or len(review_sha) != 64
        or any(c not in "0123456789abcdef" for c in review_sha)
    ):
        raise RuntimeError("V5 successor-consumer review SHA invalid")
    if governance.get("successor_consumer_independent_review_result") != "PASS":
        raise RuntimeError("V5 successor-consumer review not PASS")
    if governance.get("successor_consumer_independent_review_findings") != 0:
        raise RuntimeError("V5 successor-consumer review findings nonzero")
    if governance.get("schema2_compatible") is not True:
        raise RuntimeError("V5 schema2 compatibility not true")
    if governance.get("schema1_fallback_allowed") is not False:
        raise RuntimeError("V5 schema1 fallback unexpectedly allowed")
    if governance.get("governance_binding_verified") is not True:
        raise RuntimeError("V5 governance binding not verified")

    report_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "schema": 1,
        "status": "PASS",
        "candidate_sha256": hashlib.sha256(candidate_raw).hexdigest(),
        "generator_sha256": GEN_SHA,
        "transaction_v3_sha256": TX3_SHA,
        "transaction_v2_predecessor_sha256": TX2_SHA,
        "v3_evidence_sha256": "c4783f95de24ae309c6fd1c79ea2bc0d27e1dfdb319259351338d0f75c62de9a",
        "schema1_production_fallback_allowed": False,
        "production_candidate_executed": False,
        "d064_authorized": False,
        "runtime_authorized": False,
        "runtime_attempts": 0,
    }
    raw = (
        json.dumps(report, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")
    (report_dir / "V5_STATIC_VERIFICATION_REPORT.json").write_bytes(raw)
    print("V5_STATIC_VERIFICATION=PASS")

if MODE == "selftest":
    passed, failed, results = run_selftest()
    for name, status, detail in results:
        print(
            "  %-52s %s%s"
            % (name, status, (" " + detail) if detail else "")
        )
    print("V5_VERIFIER_SELFTEST passed=%d failed=%d" % (passed, failed))
    raise SystemExit(0 if failed == 0 else 1)

if MODE == "verify":
    run_verify()
    raise SystemExit(0)

raise SystemExit(2)
PYENGINE
