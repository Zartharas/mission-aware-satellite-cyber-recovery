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
    chk(g["read_only_host_inventory_authorized"] is True and
        g["read_only_host_inventory_parent_head"] ==
        "ee3f4f4736b19982e375170eb2479ed3c6584db9" and
        g["read_only_host_inventory_parent_workflow"] == 1423 and
        g["read_only_host_inventory_status"] ==
        "AUTHORIZED_HOST_ONLY__NOT_YET_RUN" and
        g["read_only_host_inventory_authorized_attempt_limit"] == 1 and
        g["authorization_scope"]["read_only_host_inventory"] is True and
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
             ("--inspect",True,"P2X_V2F_HOST_INVENTORY_AUTHORIZATION=READ_ONLY_HOST_ONLY")]
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
