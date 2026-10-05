#!/usr/bin/env python3
"""P2X v2e prospective dual offline NOS3 builder. Default: inspect, no mutation.

--build is HARD-LOCKED by a separate tracked author authorization record initially
set to false. It must never overwrite original v2 HOLD, July locks, or canonical
external/nos3. The source copies/outputs live only under a NEW ignored v2e ID.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "artifacts" / "runtime"
SOURCE = ROOT / "external" / "nos3"
FT = ROOT / "external" / "fortytwo"
GATE = ROOT / "paper2x" / "phase_a" / "V2E_OFFLINE_BUILD_EXECUTION_GATE_2026-10-03.json"
LAUNCHER = ROOT / "scripts" / "p2x_v2e_seed_launcher.py"
OLD = RUNTIME / "p2xa-nos3-v2-build-20261003T192146Z-99065"
IMAGE = "ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"
NOS3 = "5a3bdee6be9a2c67fdf994ae6db56d5c60395302"
LC = "5daef363c95d71c1ff3c5e9dcd4dddab560e8b39"
HW = "d65f77dea94467b7cb71053eb2f58f7a0cde3b02"
FT_REV = "eda252bf31f27850e867e698cfdd963e143ead1f"
FT_HASH = "b4d054bdd8a95dd429201466833fba8403efec4bdef09a9ed7040131dda3006d"
OLD_PRIMARY = "db64bf080232d64d5c39301e2f712885cf85e86d93c33c94fb46325fda1533fb"
OLD_REPEAT = "5a0d746a01eeac38ee555d664673ae68f0b4f4b1b96c38e06923109867ea296b"
BUILD_DATE = "202610030000"  # synthetic reproducibility label; NOT actual build time
BUILD_HOST = "p2x-v2e-builder"
BUILD_USER = "p2x-builder"
BUILD_DIRS = ("cfg/build", "fsw/build", "sims/build", "gsw/build")
ARTIFACTS = (
    "cfg/build/launch.sh",
    "fsw/build/exe/cpu1/core-cpu1",
    "sims/build/bin/nos3-single-simulator",
    "sims/build/bin/nos3-sim-cmdbus-bridge",
    "gsw/build/support/standalone",
    "cfg/build/InOut/Inp_Sim.txt",
    "cfg/build/InOut/Inp_IPC.txt",
    "sims/build/bin/nos_engine_server_config.json",
    "sims/build/bin/nos3-simulator.xml",
)
LOCKS = ("fortytwo-lock.txt", "nominal-build-lock.txt",
         "nominal-runtime-preflight-lock.txt", "nos3-submodule-lock.txt")
RECIPE = ("bash ./scripts/cfg/config.sh", "make build-fsw",
          "make build-sim", "make build-cryptolib")


def require(condition: bool, why: str) -> None:
    if not condition:
        raise SystemExit("P2X_V2E_BUILDER_HOLD=" + why)


def sha(path: Path) -> str:
    require(path.is_file() and path.stat().st_size > 0, "missing_file:" + str(path))
    h = hashlib.sha256()
    with path.open("rb") as fd:
        for chunk in iter(lambda: fd.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git(where: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(where), *args], text=True, stderr=subprocess.PIPE
    ).strip()


def stamps() -> dict[str, str]:
    return {name: sha(ROOT / "artifacts" / name) for name in LOCKS}


def preserved() -> dict[str, object]:
    p = OLD / "p2x-v2-build-manifest.json"
    m = json.loads(p.read_text(encoding="utf-8"))
    require(m["classification"] == "BUILD_BYTE_REPRODUCTION_HOLD" and
            m["required_artifact_count"] == 9 and m["repeat_match_all"] is False,
            "original_v2_hold_must_remain")
    require(sum(bool(x["repeat_match"]) for x in m["artifacts"]) == 8,
            "original_v2_eight_of_nine_changed")
    require(sha(SOURCE / "fsw/build/exe/cpu1/core-cpu1") == OLD_PRIMARY,
            "original_v2_primary_mutated")
    require(sha(OLD / "repeat/source/fsw/build/exe/cpu1/core-cpu1") == OLD_REPEAT,
            "original_v2_repeat_mutated")
    return {
        "old_manifest_sha256": sha(p),
        "old_primary_core_sha256": OLD_PRIMARY,
        "old_repeat_core_sha256": OLD_REPEAT,
        "original_july_locks_sha256": stamps(),
    }


def verify_pristine(expected: dict[str, object]) -> None:
    require(preserved() == expected, "old_failed_build_or_july_lock_drift")
    require(git(ROOT, "status", "--porcelain") == "", "research_tree_dirty")
    require(git(SOURCE, "rev-parse", "HEAD") == NOS3, "nos3_revision_changed")
    require(git(SOURCE, "status", "--porcelain") == "", "canonical_source_dirty")
    require(git(SOURCE / "fsw/apps/lc", "rev-parse", "HEAD") == LC, "lc_gitlink_drift")
    require(git(SOURCE / "fsw/apps/hwlib", "rev-parse", "HEAD") == HW, "hwlib_gitlink_drift")
    require(not any(line[:1] in ("-", "+", "U") for line in
                    git(SOURCE, "submodule", "status", "--recursive").splitlines()),
            "recursive_source_submodule_drift")
    require(git(FT, "rev-parse", "HEAD") == FT_REV and
            git(FT, "status", "--porcelain") == "" and
            sha(FT / "42") == FT_HASH, "october_fortytwo_candidate_drift")
    require(LAUNCHER.is_file() and not LAUNCHER.is_symlink() and
            LAUNCHER.stat().st_size > 0, "missing_or_aliased_seed_launcher")


def ignore_builds(origin: Path):
    parents = {(origin / dirname).resolve() for dirname in ("cfg", "fsw", "sims", "gsw")}
    def ignore(folder: str, names: list[str]) -> set[str]:
        return {"build"} if Path(folder).resolve() in parents and "build" in names else set()
    return ignore


def stage(source: Path, target: Path) -> None:
    require(not target.exists() and not target.is_symlink(), "candidate_target_exists")
    shutil.copytree(source, target, symlinks=True, ignore=ignore_builds(source))
    for rel in BUILD_DIRS:
        require(not (target / rel).exists() and not (target / rel).is_symlink(),
                "copied_old_build_directory:" + rel)
    require(git(target, "rev-parse", "HEAD") == NOS3 and
            git(target, "status", "--porcelain") == "", "staged_source_git_drift")
    require(git(target, "rev-parse", "--show-toplevel") == str(target.resolve()),
            "staged_root_aliases_canonical")
    for rel, rev in (("fsw/apps/lc", LC), ("fsw/apps/hwlib", HW)):
        sub = target / rel
        require(git(sub, "rev-parse", "HEAD") == rev, "staged_submodule_revision:" + rel)
        gitdir = Path(git(sub, "rev-parse", "--absolute-git-dir")).resolve()
        require(gitdir.is_relative_to(target.resolve()), "staged_gitdir_external_alias:" + rel)
        require(Path(git(sub, "rev-parse", "--show-toplevel")).resolve() == sub.resolve(),
                "staged_submodule_worktree_external_alias:" + rel)
    require(not any(line[:1] in ("-", "+", "U") for line in
                    git(target, "submodule", "status", "--recursive").splitlines()),
            "staged_recursive_submodule_drift")


def self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="p2x-v2e-stage-fixture-") as temp:
        base = Path(temp)
        src, dst = base / "original", base / "copy"
        for rel in BUILD_DIRS:
            p = src / rel
            p.mkdir(parents=True)
            (p / "MUST_NOT_COPY.txt").write_text("original build")
            (src / rel.split("/")[0] / "preserve.txt").write_text("tracked fixture")
        shutil.copytree(src, dst, symlinks=True, ignore=ignore_builds(src))
        for rel in BUILD_DIRS:
            require(not (dst / rel).exists(), "source_build_exclusion_failed:" + rel)
            require((src / rel / "MUST_NOT_COPY.txt").exists(), "original_modified:" + rel)
            require((dst / rel.split("/")[0] / "preserve.txt").exists(),
                    "nonbuild_source_lost:" + rel)
    a = hashlib.sha256(b"two copies").hexdigest()
    b = hashlib.sha256(b"not identical").hexdigest()
    require(a != b and a == hashlib.sha256(b"two copies").hexdigest(),
            "raw_sha_comparison_self_test")
    gate = json.loads(GATE.read_text())
    require(gate["execution_authorized"] is False and
            gate["authorization_scope"]["offline_full_build"] is False,
            "self_test_requires_design_only_gate")
    print("P2X_V2E_EXCLUDE_OLD_BUILD_OUTPUTS_SELF_TEST=PASS")
    print("P2X_V2E_ORIGINAL_STAGING_INPUT_PRESERVED=PASS")
    print("P2X_V2E_RAW_SHA_SELF_TEST=PASS")
    print("P2X_V2E_FULL_BUILD_AUTHORIZATION=CLOSED")


def seed_pairs(log: str, label: str) -> dict[tuple[str, str], str]:
    found = re.findall(
        r"^P2X_V2E_SEED_SOURCE=(\S+) OBJECT=(\S+) SEED=(\S+)$",
        log, re.MULTILINE
    )
    require(len(found) >= 5, "launcher_not_executed_for_target_units:" + label)
    mapping: dict[tuple[str, str], str] = {}
    for src, obj, seed in found:
        key = (src, obj)
        require(key not in mapping or mapping[key] == seed, "seed_collision:" + label)
        require(seed.startswith("P2X-NOS3-RG-001:v2e:") and
                re.fullmatch(r"[0-9a-f]{64}", seed.split(":")[-1]) is not None,
                "malformed_seed:" + label)
        mapping[key] = seed
    require(len(set(mapping.values())) == len(mapping), "distinct_TU_seed_collision:" + label)
    for unit in ("nos_link.c", "libcan.c", "libi2c.c", "libspi.c", "libuart.c"):
        require(any(src.endswith("/" + unit) for src, _ in mapping),
                "missing_gcov_target:" + label + ":" + unit)
    return mapping


def docker_build(source: Path, label: str, evidence: Path) -> dict[tuple[str, str], str]:
    logpath = evidence / (label + "-build.log")
    cmd = [
        "docker", "run", "--rm", "--platform", "linux/amd64",
        "--network", "none", "--hostname", BUILD_HOST,
        "--user", str(os.getuid()) + ":" + str(os.getgid()),
        "--env", "HOME=/tmp", "--env", "BUILDDATE=" + BUILD_DATE,
        "--env", "HOSTNAME=" + BUILD_HOST, "--env", "USER=" + BUILD_USER,
        "--env", "CMAKE_C_COMPILER_LAUNCHER=/usr/bin/python3;/opt/p2x_v2e_seed_launcher.py",
        "--mount", "type=bind,source=" + str(source) + ",target=/work/nos3",
        "--mount", "type=bind,source=" + str(LAUNCHER) +
                   ",target=/opt/p2x_v2e_seed_launcher.py,readonly",
        "--workdir", "/work/nos3", IMAGE, "bash", "-lc",
        'set -Eeuo pipefail; '
        'printf "container_workdir=%s\\n" "$(pwd -P)"; '
        'printf "CFE_SYNTHETIC_BUILDDATE=%s HOSTNAME=%s USER=%s\\n" '
        '"$BUILDDATE" "$HOSTNAME" "$USER"; '
        'gcc --version | head -n 1; ld --version | head -n 1; '
        'bash ./scripts/cfg/config.sh; '
        'make build-fsw; make build-sim; make build-cryptolib',
    ]
    with logpath.open("x", encoding="utf-8") as log:
        p = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, check=False)
    require(p.returncode == 0, "offline_compilation_failed:" + label)
    log = logpath.read_text(encoding="utf-8", errors="replace")
    require("container_workdir=/work/nos3" in log and
            "[100%] Built target standalone" in log and
            "CFE_SYNTHETIC_BUILDDATE=" + BUILD_DATE in log and
            "HOSTNAME=" + BUILD_HOST in log and "USER=" + BUILD_USER in log,
            "missing_original_recipe_or_environment_witness:" + label)
    require(git(source, "status", "--porcelain") == "", "staged_source_mutated:" + label)
    return seed_pairs(log, label)


def manifest_for(out: Path, initial: dict[str, object],
                 seed_maps: dict[str, dict[tuple[str, str], str]]) -> Path:
    primary, repeat = out / "primary/source", out / "repeat/source"
    rows = []
    for rel in ARTIFACTS:
        pa, pb = primary / rel, repeat / rel
        ha, hb = sha(pa), sha(pb)
        rows.append({
            "path": rel, "primary_sha256": ha, "repeat_sha256": hb,
            "primary_size_bytes": pa.stat().st_size, "repeat_size_bytes": pb.stat().st_size,
            "repeat_match": ha == hb
        })
    same = all(row["repeat_match"] for row in rows)
    m = {
        "schema": 1, "experiment_id": "P2X-NOS3-RG-001",
        "phase": "P2X_PHASE_A_PROSPECTIVE_V2E_OFFLINE_BUILD_ONLY",
        "classification": ("V2E_DUAL_OFFLINE_BUILD_BYTE_IDENTITY_PASS__RUNTIME_UNTESTED"
                           if same else "BUILD_BYTE_REPRODUCTION_HOLD"),
        "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "original_v2_hold_manifest_sha256": initial["old_manifest_sha256"],
        "historical_locks_sha256_before": initial["original_july_locks_sha256"],
        "historical_locks_sha256_after": stamps(),
        "nos3_revision": NOS3, "fortytwo_revision": FT_REV,
        "fortytwo_p2x_sha256": FT_HASH,
        "image": IMAGE, "platform": "linux/amd64", "network": "none",
        "container_workdir": "/work/nos3",
        "synthetic_reproducibility_labels_not_actual_build_timestamps": True,
        "synthetic_build_date": BUILD_DATE, "synthetic_build_host": BUILD_HOST,
        "synthetic_build_user": BUILD_USER,
        "build_recipe": RECIPE, "launcher_sha256": sha(LAUNCHER),
        "seed_maps": {
            label: [{"source": x[0], "object": x[1], "seed": v}
                    for x, v in sorted(mapping.items())]
            for label, mapping in seed_maps.items()
        },
        "primary_source_root": str(primary.resolve()),
        "repeat_source_root": str(repeat.resolve()),
        "required_artifact_count": 9, "artifacts": rows,
        "repeat_match_all": same,
        "historical_july_build_lock_replaced": False,
        "old_failed_v2_evidence_overwritten": False,
        "no_runtime_performed": True, "no_scientific_observations": True,
        "environment_final_acceptance": False
    }
    path = out / "p2x-v2e-build-manifest.json"
    with path.open("x", encoding="utf-8") as fd:
        json.dump(m, fd, indent=2, sort_keys=True)
        fd.write("\n")
    with (out / "artifact-hash-comparison.tsv").open("x", encoding="utf-8") as fd:
        fd.write("relative_path\tprimary_sha256\trepeat_sha256\trepeat_match\tprimary_size_bytes\trepeat_size_bytes\n")
        for row in rows:
            fd.write("\t".join(str(row[key]) for key in (
                "path", "primary_sha256", "repeat_sha256", "repeat_match",
                "primary_size_bytes", "repeat_size_bytes")) + "\n")
    return path


def main() -> None:
    mode = sys.argv[1:] or ["--inspect"]
    require(len(mode) == 1 and mode[0] in ("--inspect", "--self-test", "--build"),
            "usage: --inspect | --self-test | --build")
    if mode == ["--self-test"]:
        self_test()
        return
    require(ROOT.name == "mission-aware-satellite-cyber-recovery", "wrong_research_root")
    require(git(ROOT, "remote", "get-url", "origin").removesuffix(".git").endswith(
            "Zartharas/mission-aware-satellite-cyber-recovery"), "wrong_repo_origin")
    policy = json.loads(GATE.read_text(encoding="utf-8"))
    require(policy["record_id"] ==
            "P2X-PHASE-A-V2E-OFFLINE-BUILD-EXECUTION-GATE-2026-10-03",
            "wrong_execution_gate")
    # Author scope gate is tested BEFORE reading any host evidence or touching Docker.
    # This gives CI a real negative-path test even without locally staged NOS3.
    if mode == ["--build"]:
        require(policy["execution_authorized"] is True and
                policy["decision"] == "AUTHOR_EXPLICITLY_APPROVED_V2E_OFFLINE_REBUILD" and
                policy["authorization_scope"]["offline_full_build"] is True,
                "separate_v2e_authorization_absent__no_build")
    baseline = preserved()
    verify_pristine(baseline)
    if mode == ["--inspect"]:
        closed = (
            policy["decision"] == "DESIGN_AND_STATIC_VALIDATION_ONLY" and
            policy["execution_authorized"] is False and
            policy["authorization_scope"]["offline_full_build"] is False
        )
        authorized = (
            policy["decision"] == "AUTHOR_EXPLICITLY_APPROVED_V2E_OFFLINE_REBUILD" and
            policy["execution_authorized"] is True and
            policy["authorization_scope"]["offline_full_build"] is True
        )
        require(closed or authorized, "invalid_v2e_execution_gate_state")
        require(policy["authorization_scope"]["nominal_runtime"] is False and
                policy["authorization_scope"]["cosmos"] is False and
                policy["authorization_scope"]["faults"] is False and
                policy["authorization_scope"]["merge_pr215"] is False and
                policy["environment_final_acceptance"] is False,
                "runtime_science_or_merge_scope_unexpectedly_open")
        print("P2X_V2E_READ_ONLY_INSPECTION=PASS")
        print("P2X_V2E_ORIGINAL_8_OF_9_HOLD=PRESERVED")
        print("P2X_V2E_BUILD_EXECUTION=" +
              ("AUTHORIZED_NOT_RUN" if authorized else "NOT_AUTHORIZED"))
        print("P2X_V2E_RUNTIME_EXECUTED=NO")
        return
    # Distinct prospective authorization gate. Earlier v2 approval is NOT re-used.
    require(shutil.which("docker") is not None, "docker_unavailable")
    platform = subprocess.check_output(
        ["docker", "image", "inspect", IMAGE, "--format", "{{.Os}}/{{.Architecture}}"],
        text=True
    ).strip()
    require(platform == "linux/amd64", "locked_image_platform_drift")
    # Exclude *existing generated builds* in the two new source trees, never delete
    # or clean the already populated canonical external/nos3 or old v2 root.
    require(RUNTIME.is_dir(), "missing_ignored_runtime_root")
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = RUNTIME / ("p2xa-nos3-v2e-build-" + stamp + "-" + uuid.uuid4().hex[:10])
    out.mkdir(mode=0o700)  # collision -> exception, never overwrite
    with (out / "build-provenance.json").open("x", encoding="utf-8") as fd:
        json.dump({"real_build_start_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
                   "synthetic_cfe_labels": [BUILD_DATE, BUILD_HOST, BUILD_USER],
                   "image": IMAGE, "canonical_nos3": NOS3,
                   "original_failed_v2_manifest_sha256": baseline["old_manifest_sha256"],
                   "historical_locks_before": baseline["original_july_locks_sha256"],
                   "prospective_execution_gate": policy["decision"]},
                  fd, indent=2, sort_keys=True)
        fd.write("\n")
    print("P2X_V2E_NEW_IGNORED_EVIDENCE=" + str(out), flush=True)
    try:
        for label in ("primary", "repeat"):
            stage(SOURCE, out / label / "source")
            print("P2X_V2E_INDEPENDENT_SOURCE_STAGED=" + label, flush=True)
        verify_pristine(baseline)
        seeds = {}
        for label in ("primary", "repeat"):
            seeds[label] = docker_build(out / label / "source", label, out)
            verify_pristine(baseline)
            print("P2X_V2E_BUILD_COMPLETED=" + label, flush=True)
        require(seeds["primary"] == seeds["repeat"],
                "compiler_launcher_seed_maps_differ_between_candidate_copies")
        p = manifest_for(out, baseline, seeds)
        verify_pristine(baseline)
        print("P2X_V2E_MANIFEST=" + str(p), flush=True)
        m = json.loads(p.read_text(encoding="utf-8"))
        require(m["repeat_match_all"] is True, "nine_raw_SHA_mismatch_preserve_both_new_builds")
        subprocess.run([sys.executable, str(ROOT / "scripts/verify_paper2x_phase_a_v2e.py"),
                        str(p)], check=True)
        print("P2X_V2E_BUILD=RAW_9_OF_9_PASS__RUNTIME_NOT_EXECUTED")
    except BaseException as exc:
        with (out / "operator-status.txt").open("x", encoding="utf-8") as f:
            f.write("P2X_V2E_OPERATOR_HOLD=" + str(exc) + "\n")
            f.write("P2X_V2E_EVIDENCE_PRESERVED=" + str(out) + "\n")
        raise
    print("P2X_V2E_OLD_8_OF_9_HOLD_UNMODIFIED=PASS")
    print("P2X_V2E_FINAL_ENVIRONMENT_ACCEPTANCE=NO")
    print("P2X_V2E_RUNTIME_EXECUTED=NO")


if __name__ == "__main__":
    main()
