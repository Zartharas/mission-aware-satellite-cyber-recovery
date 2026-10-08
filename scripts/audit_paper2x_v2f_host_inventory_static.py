#!/usr/bin/env python3
"""CI-only static fence for P2X v2f author-host inventory source."""
import ast
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "paper2x/phase_a/V2F_NOMINAL_RUNTIME_QUALIFICATION_GATE_2026-10-07.json"
TOOL = ROOT / "scripts/inventory_paper2x_v2f_sources_readonly.py"

def chk(ok: bool, why: str) -> None:
    if not ok:
        raise SystemExit("P2X_V2F_HOST_INVENTORY_STATIC_HOLD=" + why)

def main() -> None:
    g = json.loads(GATE.read_text(encoding="utf-8"))
    s = TOOL.read_text(encoding="utf-8")
    result_path = ROOT / "paper2x/phase_a/V2F_HOST_INVENTORY_AUTHOR_REPORTED_RESULT_2026-10-08.json"
    reported = json.loads(result_path.read_text(encoding="utf-8"))
    reconciliation_path = ROOT / "paper2x/phase_a/V2F_UPLOADED_INVENTORY_RECONCILIATION_2026-10-08.json"
    reconciliation = json.loads(reconciliation_path.read_text(encoding="utf-8"))
    chk(g["read_only_host_inventory_authorized"] is False and
        g["read_only_host_inventory_completed"] is True and
        g["read_only_host_inventory_status"] ==
        "UPLOADED_JSONL_RECONCILED__55_METADATA_AND_CMAKE_LOG_HASH_VARIANCES__RUNTIME_UNTESTED" and
        g["read_only_host_inventory_result"] == "AUTHOR_REPORTED_READ_ONLY_PASS" and
        g["read_only_host_inventory_parent_head"] ==
        "ee3f4f4736b19982e375170eb2479ed3c6584db9" and
        g["read_only_host_inventory_parent_workflow"] == 1423 and
        g["read_only_host_inventory_authorized_attempt_limit"] == 0 and
        g["read_only_host_inventory_attempts_executed"] == 1 and
        g["authorization_scope"]["read_only_host_inventory"] is False and
        g["read_only_host_inventory_report_sha256"] ==
        "edeba9101e56000a4ca1eb12f67105a05865627c5d39416db521991b6bf50e38" and
        g["read_only_host_inventory_entries_reported"] == 50617 and
        g["read_only_host_inventory_raw_report_received"] is True and
        g["read_only_host_inventory_full_file_level_review_completed"] is True and
        g["read_only_host_inventory_full_primary_repeat_hash_differences"] == 55 and
        g["read_only_host_inventory_git_index_hash_differences"] == 51 and
        g["read_only_host_inventory_cmake_log_hash_differences"] == 4 and
        g["read_only_host_inventory_all_files_byte_identical"] is False and
        g["read_only_host_inventory_reconciliation_record"] ==
        "paper2x/phase_a/V2F_UPLOADED_INVENTORY_RECONCILIATION_2026-10-08.json" and
        g["read_only_host_inventory_runtime_dependency_closure"] == "UNRESOLVED" and
        reported["classification"] ==
        "AUTHOR_HOST_REPORT_PASS__UPLOADED_JSONL_INDEPENDENTLY_RECONCILED__55_HASH_VARIANCES" and
        reported["reported_entries"] == 50617 and
        reported["raw_jsonl_received_by_assistant"] is True and
        reported["full_inventory_path_reviewed"] is True and
        reported["all_20089_primary_repeat_file_hashes_independently_compared"] is True and
        reported["all_regular_files_byte_identical"] is False and
        reported["file_hashes_differ_count"] == 55 and
        reconciliation["classification"] ==
        "COMPLETE_UPLOADED_JSONL_REVIEW__55_HASH_VARIANCES__RUNTIME_DEPENDENCY_CLOSURE_UNRESOLVED" and
        reconciliation["uploaded_evidence_zip_member_inventory_sha256"] ==
        "edeba9101e56000a4ca1eb12f67105a05865627c5d39416db521991b6bf50e38" and
        reconciliation["jsonl_structure"]["entries"] == 50617 and
        reconciliation["jsonl_structure"]["invalid_records"] == 0 and
        reconciliation["primary_repeat_reconciliation"]["regular_file_sha256_match"] == 20034 and
        reconciliation["primary_repeat_reconciliation"]["regular_file_sha256_differ"] == 55 and
        reconciliation["primary_repeat_reconciliation"]["differing_hashes_git_index_metadata"] == 51 and
        reconciliation["primary_repeat_reconciliation"]["differing_hashes_cmake_configure_log"] == 4 and
        reconciliation["primary_repeat_reconciliation"]["full_population_tree_byte_identical"] is False and
        reconciliation["evidence_integrity"]["actual_host_source_bytes_reread_by_assistant"] is False and
        reconciliation["runtime_dependency_closure"] == "UNRESOLVED" and
        reconciliation["nominal_runtime_authorized"] is False and
        reported["runtime_dependency_closure"] == "UNRESOLVED" and
        sum(x[t] for x in reported["reported_totals"].values()
              for t in ("regular_file","directory","symlink","special")) == 50617 and
        g["execution_authorized"] is False and
        g["runtime_workspace_materialization_authorized"] is False and
        g["runtime_workspace_materialized"] is False and
        g["authorization_scope"]["nominal_runtime_execution"] is False and
        g["authorization_scope"]["cosmos"] is False and
        g["authorization_scope"]["faults"] is False and
        g["authorization_scope"]["merge_pr215"] is False,
        "scope_firewall")
    tree = ast.parse(s)
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        if isinstance(node, ast.ImportFrom):
            imported.add((node.module or "").split(".")[0])
    chk(not imported.intersection({"subprocess","shutil","socket","ctypes"}),
        "unsafe_import")
    for forbidden in ("os.remove(", "os.rename(", "os.replace(", "os.mkdir(",
                      "os.makedirs(", "os.unlink(", "os.system(",
                      ".write_text(", ".write_bytes(", "P2X_V2_MANIFEST",
                      "run_nominal_runtime_preflight.sh", "docker run",
                      "O_CREAT", "O_WRONLY", "O_RDWR"):
        chk(forbidden not in s, "source_mutation_or_runtime_token:"+forbidden)
    chk("os.O_RDONLY" in s and "os.scandir(" in s and
        "follow_symlinks=False" in s and
        "P2X_V2F_RUNTIME_DEPENDENCY_CLOSURE=UNRESOLVED" in s and
        "P2X_V2F_WORKSPACE_MATERIALIZED=NO" in s,
        "read_only_contract_missing")
    tests = [("--self-test",True,"P2X_V2F_HOST_INVENTORY_SELF_TEST=PASS"),
             ("--inspect",True,"P2X_V2F_HOST_INVENTORY_AUTHORIZATION=CLOSED_CONSUMED"),
             ("--inventory",False,"P2X_V2F_HOST_INVENTORY_HOLD=not_authorized_or_gate_drift")]
    for mode,ok,marker in tests:
        p = subprocess.run([sys.executable,str(TOOL),mode],
            cwd=ROOT,capture_output=True,text=True)
        chk((p.returncode==0) is ok and marker in p.stdout+p.stderr,
            "self_test_failed:"+mode+":"+p.stderr[:160])
    print("P2X_V2F_HOST_INVENTORY_STATIC_AUDIT=PASS")
    print("P2X_V2F_HOST_INVENTORY_EXECUTED_IN_CI=NO")
    print("P2X_V2F_RUNTIME_EXECUTED=NO")

if __name__ == "__main__":
    main()
