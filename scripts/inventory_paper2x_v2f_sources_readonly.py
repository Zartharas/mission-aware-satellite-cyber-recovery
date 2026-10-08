#!/usr/bin/env python3
"""Author-host P2X v2f SOURCE INVENTORY ONLY; stdout is JSONL, no source writes."""
from __future__ import annotations
import hashlib
import json
import os
import posixpath
import stat
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "paper2x/phase_a/V2F_NOMINAL_RUNTIME_QUALIFICATION_GATE_2026-10-07.json"
EVIDENCE = "p2xa-nos3-v2f-build-20261007T185149Z-a61cae46f1"
MANIFEST_SHA = "cb5e84137cb090adc8fb24b9b2f78c0d239d2fb93c74393a0e8b71815cc86dee"
FORTYTWO_SHA = "b4d054bdd8a95dd429201466833fba8403efec4bdef09a9ed7040131dda3006d"
NINE = (
    "cfg/build/launch.sh", "fsw/build/exe/cpu1/core-cpu1",
    "sims/build/bin/nos3-single-simulator",
    "sims/build/bin/nos3-sim-cmdbus-bridge",
    "gsw/build/support/standalone", "cfg/build/InOut/Inp_Sim.txt",
    "cfg/build/InOut/Inp_IPC.txt",
    "sims/build/bin/nos_engine_server_config.json",
    "sims/build/bin/nos3-simulator.xml",
)
REL = "artifacts/runtime/" + EVIDENCE
SRC = ROOT / REL
FT = ROOT / "external/fortytwo"
OPEN_FLAGS = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
COUNTS = ("regular_file", "directory", "symlink", "special")

def require(ok: bool, why: str) -> None:
    if not ok:
        raise SystemExit("P2X_V2F_HOST_INVENTORY_HOLD=" + why)

def hfile(p: Path) -> str:
    before = p.lstat()
    require(stat.S_ISREG(before.st_mode), "not_regular:" + str(p))
    fd = os.open(str(p), OPEN_FLAGS)
    try:
        opened = os.fstat(fd)
        require(stat.S_ISREG(opened.st_mode) and
                (opened.st_dev, opened.st_ino) == (before.st_dev, before.st_ino),
                "file_changed_during_open:" + str(p))
        h = hashlib.sha256()
        while True:
            chunk = os.read(fd, 1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
        after = os.fstat(fd)
    finally:
        os.close(fd)
    current = p.lstat()
    require((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) ==
            (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns) ==
            (current.st_dev, current.st_ino, current.st_size, current.st_mtime_ns),
            "file_changed_during_hash:" + str(p))
    return h.hexdigest()

def gate_check() -> dict:
    g = json.loads(GATE.read_text(encoding="utf-8"))
    scope = g["authorization_scope"]
    require(g["decision"] == "V2F_MANIFEST_SHA256_BOUND__RUNTIME_NOT_AUTHORIZED"
            and g["parent_v2f_evidence_id"] == EVIDENCE
            and g["parent_v2f_manifest_sha256"] == MANIFEST_SHA
            and g["read_only_host_inventory_authorized"] is True
            and g["read_only_host_inventory_status"] ==
            "AUTHORIZED_HOST_ONLY__NOT_YET_RUN"
            and g["read_only_host_inventory_parent_head"] ==
            "ee3f4f4736b19982e375170eb2479ed3c6584db9"
            and g["read_only_host_inventory_parent_workflow"] == 1423
            and g["read_only_host_inventory_authorized_attempt_limit"] == 1
            and scope["read_only_host_inventory"] is True
            and g["execution_authorized"] is False
            and g["runtime_workspace_materialization_authorized"] is False
            and g["runtime_workspace_materialized"] is False
            and g["runtime_workspace_independent_verification_executed"] is False,
            "not_authorized_or_gate_drift")
    for k in ("nominal_runtime_execution", "benign_internal_cfs_noop", "cosmos",
              "faults", "scientific_observations", "final_environment_acceptance",
              "merge_pr215"):
        require(scope[k] is False, "forbidden_scope:" + k)
    require(g["parent_v2f_manifest_relative_path"] ==
            REL + "/p2x-v2f-build-manifest.json", "manifest_path_drift")
    return g

def classify_symlink(rel: str, target: str) -> str:
    if posixpath.isabs(target):
        return "ABSOLUTE_TARGET_REQUIRES_REVIEW"
    normalized = posixpath.normpath(posixpath.join(posixpath.dirname(rel), target))
    if normalized == ".." or normalized.startswith("../"):
        return "ESCAPES_ROOT_REQUIRES_REVIEW"
    return "LEXICALLY_CONTAINED_NOT_RESOLVED"

def scan(label: str, root: Path, emit, totals: dict, qualified: dict) -> None:
    require(root.is_dir() and not root.is_symlink(), "missing_or_aliased_root:" + label)
    pending = [("", root)]
    seen = {}
    while pending:
        prefix, parent = pending.pop()
        with os.scandir(parent) as it:
            children = sorted(it, key=lambda entry: os.fsencode(entry.name), reverse=True)
        for entry in children:
            name = entry.name
            require(name not in (".", "..") and "/" not in name,
                    "unsafe_entry_name:" + label)
            rel = prefix + "/" + name if prefix else name
            normalized = unicodedata.normalize("NFC", rel).casefold()
            if normalized in seen and seen[normalized] != rel:
                totals[label]["case_unicode_collisions"] += 1
            else:
                seen[normalized] = rel
            st = entry.stat(follow_symlinks=False)
            mode = stat.S_IMODE(st.st_mode)
            row = {"type":"entry", "root":label, "path":rel,
                   "mode_octal":format(mode,"04o"), "nlink":st.st_nlink,
                   "size_bytes":st.st_size}
            if stat.S_ISDIR(st.st_mode):
                row["entry_type"] = "directory"
                pending.append((rel, Path(entry.path)))
            elif stat.S_ISLNK(st.st_mode):
                target = os.readlink(entry.path)
                row.update(entry_type="symlink", symlink_target=target,
                           symlink_policy=classify_symlink(rel, target))
                if row["symlink_policy"] != "LEXICALLY_CONTAINED_NOT_RESOLVED":
                    totals[label]["symlink_review_required"] += 1
            elif stat.S_ISREG(st.st_mode):
                row.update(entry_type="regular_file", sha256=hfile(Path(entry.path)))
                totals[label]["regular_bytes"] += st.st_size
                if rel in NINE and label in ("primary", "repeat"):
                    qualified[label][rel] = row["sha256"]
                if label == "fortytwo" and rel == "42":
                    qualified["fortytwo"]["42"] = row["sha256"]
            else:
                row.update(entry_type="special",
                           file_type_bits=stat.S_IFMT(st.st_mode))
                totals[label]["special_review_required"] += 1
            totals[label][row["entry_type"]] += 1
            if st.st_nlink > 1 and row["entry_type"] == "regular_file":
                totals[label]["hardlink_review_required"] += 1
            emit(row)

def self_test() -> None:
    gate_check()
    require(classify_symlink("x/y", "../../z").startswith("ESCAPES")
            and classify_symlink("x/y", "/tmp/x").startswith("ABSOLUTE")
            and classify_symlink("x/y", "../z") ==
            "LEXICALLY_CONTAINED_NOT_RESOLVED", "symlink_negative_controls")
    print("P2X_V2F_HOST_INVENTORY_SELF_TEST=PASS")
    print("P2X_V2F_HOST_INVENTORY_RUNTIME_EXECUTED=NO")
    print("P2X_V2F_WORKSPACE_MATERIALIZED=NO")

def inventory() -> None:
    gate_check()
    manifest = SRC / "p2x-v2f-build-manifest.json"
    require(manifest.is_file() and hfile(manifest) == MANIFEST_SHA,
            "bound_manifest_changed")
    m = json.loads(manifest.read_text(encoding="utf-8"))
    require(m["classification"] ==
            "V2F_DUAL_OFFLINE_BUILD_BYTE_IDENTITY_PASS__RUNTIME_UNTESTED"
            and m["required_artifact_count"] == 9 and
            m["repeat_match_all"] is True
            and [r["path"] for r in m["artifacts"]] == list(NINE),
            "manifest_build_identity_mismatch")
    require(FT.is_dir() and not FT.is_symlink()
            and hfile(FT / "42") == FORTYTWO_SHA, "fortytwo_drift")
    roots = {"primary":SRC/"primary/source", "repeat":SRC/"repeat/source",
             "fortytwo":FT}
    require(all(p.is_dir() and not p.is_symlink() for p in roots.values()),
            "source_population_missing")
    totals = {label:{**{k:0 for k in COUNTS}, "regular_bytes":0,
                    "symlink_review_required":0,
                    "special_review_required":0,
                    "hardlink_review_required":0,
                    "case_unicode_collisions":0} for label in roots}
    qualified = {label:{} for label in roots}
    digest = hashlib.sha256()
    def emit(row: dict) -> None:
        line = json.dumps(row,sort_keys=True,ensure_ascii=True,separators=(",",":"))+"\n"
        digest.update(line.encode("utf-8"))
        sys.stdout.write(line)
    emit({"type":"header","schema":1,"experiment_id":"P2X-NOS3-RG-001",
          "classification":"READ_ONLY_HOST_TREE_INVENTORY_NOT_RUNTIME_PROOF",
          "authorized_head":"ee3f4f4736b19982e375170eb2479ed3c6584db9","evidence_id":EVIDENCE,
          "manifest_sha256":MANIFEST_SHA,
          "roots":{k:str(v) for k,v in roots.items()}})
    for label, path in roots.items():
        scan(label,path,emit,totals,qualified)
    for item in m["artifacts"]:
        rel = item["path"]
        require(qualified["primary"].get(rel) == qualified["repeat"].get(rel) ==
                item["primary_sha256"] == item["repeat_sha256"],
                "nine_artifact_drift:" + rel)
    require(qualified["fortytwo"].get("42") == FORTYTWO_SHA,
            "fortytwo_tree_binary_drift")
    require(hfile(manifest) == MANIFEST_SHA and hfile(FT/"42") == FORTYTWO_SHA,
            "protected_source_changed_after_scan")
    prior = digest.hexdigest()
    emit({"type":"summary","schema":1,"class":"HOST_INVENTORY_READ_ONLY_PASS",
          "records_sha256_before_summary":prior,"totals":totals,
          "nine_build_artifacts_reverified":True,
          "fortytwo_binary_reverified":True,
          "runtime_dependency_closure":"UNRESOLVED",
          "workspace_materialized":False,"runtime_executed":False})
    print("P2X_V2F_HOST_INVENTORY=READ_ONLY_PASS",file=sys.stderr)
    print("P2X_V2F_HOST_INVENTORY_RECORDS_SHA256="+prior,file=sys.stderr)
    print("P2X_V2F_PRIMARY_REPEAT_NINE_RAW_SHA=PASS",file=sys.stderr)
    print("P2X_V2F_FORTYTWO_BINARY_SHA256=PASS",file=sys.stderr)
    print("P2X_V2F_RUNTIME_DEPENDENCY_CLOSURE=UNRESOLVED",file=sys.stderr)
    print("P2X_V2F_WORKSPACE_MATERIALIZED=NO",file=sys.stderr)
    print("P2X_V2F_RUNTIME_EXECUTED=NO",file=sys.stderr)

def main() -> None:
    args = sys.argv[1:]
    require(args in (["--inspect"],["--self-test"],["--inventory"]),
            "usage:--inspect_--self-test_--inventory")
    if args == ["--inspect"]:
        gate_check()
        print("P2X_V2F_HOST_INVENTORY_AUTHORIZATION=READ_ONLY_HOST_ONLY")
        print("P2X_V2F_RUNTIME_EXECUTED=NO")
    elif args == ["--self-test"]:
        self_test()
    else:
        inventory()

if __name__ == "__main__":
    main()
