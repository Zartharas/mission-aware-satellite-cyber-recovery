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
    chk(g["read_only_host_inventory_authorized"] is False and
        g["read_only_host_inventory_completed"] is True and
        g["read_only_host_inventory_status"] ==
        "HOST_REPORTED_PASS__AUTHORIZATION_CONSUMED__FILE_LEVEL_REVIEW_PENDING" and
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
        g["read_only_host_inventory_raw_report_received"] is False and
        g["read_only_host_inventory_full_file_level_review_completed"] is False and
        g["read_only_host_inventory_runtime_dependency_closure"] == "UNRESOLVED" and
        reported["classification"] ==
        "AUTHOR_HOST_REPORT_PASS__FILE_LEVEL_JSONL_NOT_REVIEWED" and
        reported["reported_entries"] == 50617 and
        reported["raw_jsonl_received_by_assistant"] is False and
        reported["full_inventory_path_reviewed"] is False and
        reported["all_20089_primary_repeat_file_hashes_independently_compared"] is False and
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
