#!/usr/bin/env python3
"""P2X v2f prospective dual offline NOS3 builder. Default: inspect only.

The current tracked gate authorizes implementation/static validation only.
--build must fail before Docker, evidence creation, or source staging unless a
separate explicit author authorization opens the v2f offline-full-build gate.
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
GATE = ROOT / "paper2x/phase_a/V2F_OFFLINE_BUILD_EXECUTION_GATE_2026-10-05.json"
LAUNCHER = ROOT / "scripts/p2x_v2e_seed_launcher.py"
DESCRIPTOR_HELPER = ROOT / "scripts/p2x_v2f_descriptor_map.py"
VERIFIER = ROOT / "scripts/verify_paper2x_phase_a_v2f.py"

OLD_V2 = RUNTIME / "p2xa-nos3-v2-build-20261003T192146Z-99065"
OLD_V2E = RUNTIME / "p2xa-nos3-v2e-build-20261005T141959Z-7c8ceaa570"
IMAGE = "ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"
NOS3 = "5a3bdee6be9a2c67fdf994ae6db56d5c60395302"
LC = "5daef363c95d71c1ff3c5e9dcd4dddab560e8b39"
HW = "d65f77dea94467b7cb71053eb2f58f7a0cde3b02"
FT_REV = "eda252bf31f27850e867e698cfdd963e143ead1f"
FT_HASH = "b4d054bdd8a95dd429201466833fba8403efec4bdef09a9ed7040131dda3006d"

V2_PRIMARY = "db64bf080232d64d5c39301e2f712885cf85e86d93c33c94fb46325fda1533fb"
V2_REPEAT = "5a0d746a01eeac38ee555d664673ae68f0b4f4b1b96c38e06923109867ea296b"
V2E_MANIFEST_SHA = "25c2b15b5344f8c05dde8c4b85881571859d8601d15d972c6908978ecbfa5938"
V2E_PRIMARY = "cab1f6602e7b371171d851b0c6f78a69ddd7c7625457e2e9a12f75c7e0f86001"
V2E_REPEAT = "40b48fc62719be1d01cc104ff51a1ceab6ad42f9e925d30b700a3f2dd8412e7d"
PROBE_MAP_SHA = "499525c90430ae0dd17fc297be0388b2eae51fdb6623f3d338b0a2f392460278"

BUILD_DATE = "202610030000"
BUILD_HOST = "p2x-v2e-builder"
BUILD_USER = "p2x-builder"
SAFE_DIR = "/work/nos3"

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


def require(ok: bool, why: str) -> None:
    if not ok:
        raise SystemExit("P2X_V2F_BUILDER_HOLD=" + why)


def sha(path: Path) -> str:
    require(path.is_file() and path.stat().st_size > 0, "missing_file:" + str(path))
    h = hashlib.sha256()
    with path.open("rb") as fd:
        for chunk in iter(lambda: fd.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def git(where: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(where), *args], text=True, stderr=subprocess.PIPE
    ).strip()


def stamps() -> dict[str, str]:
    return {name: sha(ROOT / "artifacts" / name) for name in LOCKS}


def preserved() -> dict[str, object]:
    v2_path = OLD_V2 / "p2x-v2-build-manifest.json"
    v2 = json.loads(v2_path.read_text(encoding="utf-8"))
    require(v2["classification"] == "BUILD_BYTE_REPRODUCTION_HOLD" and
            v2["required_artifact_count"] == 9 and v2["repeat_match_all"] is False and
            sum(bool(x["repeat_match"]) for x in v2["artifacts"]) == 8,
            "original_v2_hold_changed")
    require(sha(SOURCE / "fsw/build/exe/cpu1/core-cpu1") == V2_PRIMARY,
            "original_v2_primary_changed")
    require(sha(OLD_V2 / "repeat/source/fsw/build/exe/cpu1/core-cpu1") == V2_REPEAT,
            "original_v2_repeat_changed")

    v2e_path = OLD_V2E / "p2x-v2e-build-manifest.json"
    v2e = json.loads(v2e_path.read_text(encoding="utf-8"))
    require(sha(v2e_path) == V2E_MANIFEST_SHA and
            v2e["classification"] == "BUILD_BYTE_REPRODUCTION_HOLD" and
            v2e["required_artifact_count"] == 9 and v2e["repeat_match_all"] is False and
            sum(bool(x["repeat_match"]) for x in v2e["artifacts"]) == 8,
            "v2e_hold_changed")
    require(sha(OLD_V2E / "primary/source/fsw/build/exe/cpu1/core-cpu1") == V2E_PRIMARY and
            sha(OLD_V2E / "repeat/source/fsw/build/exe/cpu1/core-cpu1") == V2E_REPEAT,
            "v2e_held_core_changed")

    return {
        "v2_manifest_sha256": sha(v2_path),
        "v2_primary_core_sha256": V2_PRIMARY,
        "v2_repeat_core_sha256": V2_REPEAT,
        "v2e_manifest_sha256": V2E_MANIFEST_SHA,
        "v2e_primary_core_sha256": V2E_PRIMARY,
        "v2e_repeat_core_sha256": V2E_REPEAT,
        "july_locks_sha256": stamps(),
    }


def verify_pristine(expected: dict[str, object]) -> None:
    require(preserved() == expected, "historical_v2_v2e_or_lock_drift")
    require(git(ROOT, "status", "--porcelain") == "", "research_tree_dirty")
    require(git(SOURCE, "rev-parse", "HEAD") == NOS3, "nos3_revision_changed")
    require(git(SOURCE, "status", "--porcelain") == "", "canonical_source_dirty")
    require(git(SOURCE / "fsw/apps/lc", "rev-parse", "HEAD") == LC, "lc_drift")
    require(git(SOURCE / "fsw/apps/hwlib", "rev-parse", "HEAD") == HW, "hwlib_drift")
    require(not any(line[:1] in ("-", "+", "U") for line in
                    git(SOURCE, "submodule", "status", "--recursive").splitlines()),
            "recursive_source_submodule_drift")
    require(git(FT, "rev-parse", "HEAD") == FT_REV and
            git(FT, "status", "--porcelain") == "" and sha(FT / "42") == FT_HASH,
            "fortytwo_candidate_drift")
    for p in (LAUNCHER, DESCRIPTOR_HELPER, VERIFIER):
        require(p.is_file() and not p.is_symlink() and p.stat().st_size > 0,
                "missing_or_aliased_control:" + str(p))


def ignore_builds(origin: Path):
    parents = {(origin / x).resolve() for x in ("cfg", "fsw", "sims", "gsw")}
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
    require(Path(git(target, "rev-parse", "--show-toplevel")).resolve() == target.resolve(),
            "staged_root_alias")
    for rel, rev in (("fsw/apps/lc", LC), ("fsw/apps/hwlib", HW)):
        sub = target / rel
        require(git(sub, "rev-parse", "HEAD") == rev, "staged_submodule_revision:" + rel)
        require(Path(git(sub, "rev-parse", "--absolute-git-dir")).resolve()
                .is_relative_to(target.resolve()), "staged_external_gitdir:" + rel)
        require(Path(git(sub, "rev-parse", "--show-toplevel")).resolve() == sub.resolve(),
                "staged_external_worktree:" + rel)
    require(not any(line[:1] in ("-", "+", "U") for line in
                    git(target, "submodule", "status", "--recursive").splitlines()),
            "staged_recursive_submodule_drift")


def git_env_args() -> list[str]:
    return [
        "--env", "GIT_CONFIG_COUNT=1",
        "--env", "GIT_CONFIG_KEY_0=safe.directory",
        "--env", "GIT_CONFIG_VALUE_0=" + SAFE_DIR,
    ]


def common_docker(source: Path) -> list[str]:
    return [
        "docker", "run", "--rm", "--platform", "linux/amd64",
        "--network", "none", "--hostname", BUILD_HOST,
        "--user", str(os.getuid()) + ":" + str(os.getgid()),
        "--env", "HOME=/tmp",
        "--env", "BUILDDATE=" + BUILD_DATE,
        "--env", "HOSTNAME=" + BUILD_HOST,
        "--env", "USER=" + BUILD_USER,
        *git_env_args(),
        "--env", "CMAKE_C_COMPILER_LAUNCHER=/usr/bin/python3;/opt/p2x_v2e_seed_launcher.py",
        "--mount", "type=bind,source=" + str(source) + ",target=/work/nos3",
        "--mount", "type=bind,source=" + str(LAUNCHER) +
                   ",target=/opt/p2x_v2e_seed_launcher.py,readonly",
        "--workdir", "/work/nos3", IMAGE,
    ]


def configure_and_descriptor(source: Path, label: str, evidence: Path) -> dict:
    logpath = evidence / (label + "-configure.log")
    cmd = common_docker(source) + [
        "--mount", "type=bind,source=" + str(DESCRIPTOR_HELPER) +
                   ",target=/opt/p2x_v2f_descriptor_map.py,readonly",
        "bash", "-lc",
        'set -Eeuo pipefail; '
        'printf "container_workdir=%s\\n" "$(pwd -P)"; '
        'printf "P2X_V2F_SAFE_DIRECTORY=%s\\n" "$GIT_CONFIG_VALUE_0"; '
        'bash ./scripts/cfg/config.sh; '
        'printf "P2X_V2F_DESCRIPTOR_MAP_JSON="; '
        'python3 /opt/p2x_v2f_descriptor_map.py --emit'
    ]
    with logpath.open("x", encoding="utf-8") as log:
        p = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, check=False)
    require(p.returncode == 0, "configure_or_descriptor_failed:" + label)
    text = logpath.read_text(encoding="utf-8", errors="replace")
    found = re.findall(r"^P2X_V2F_DESCRIPTOR_MAP_JSON=(\{.*\})$", text, re.MULTILINE)
    require(len(found) == 1, "descriptor_map_witness_count:" + label)
    data = json.loads(found[0])
    require(data["safe_directory"] == SAFE_DIR and
            data["nos3_head"] == NOS3 and data["nos3_describe"] == "v1_07_05" and
            data["onair_submodule_head"] == "aa5559c0f234eba263041b6007573f16870194e5" and
            data["onair_submodule_describe"] == "v0.0.13-119-gaa5559c",
            "descriptor_map_expected_pins:" + label)
    require(git(source, "status", "--porcelain") == "", "configured_source_git_drift:" + label)
    pth = evidence / (label + "-descriptor-map.json")
    with pth.open("x", encoding="utf-8") as fd:
        json.dump(data, fd, indent=2, sort_keys=True)
        fd.write("\n")
    return data


def seed_pairs(log: str, label: str) -> dict[tuple[str, str], str]:
    found = re.findall(r"^P2X_V2E_SEED_SOURCE=(\S+) OBJECT=(\S+) SEED=(\S+)$",
                       log, re.MULTILINE)
    require(len(found) >= 5, "launcher_not_executed:" + label)
    mapping: dict[tuple[str, str], str] = {}
    for src, obj, seed in found:
        key = (src, obj)
        require(key not in mapping or mapping[key] == seed, "seed_collision:" + label)
        require(seed.startswith("P2X-NOS3-RG-001:v2e:") and
                re.fullmatch(r"[0-9a-f]{64}", seed.split(":")[-1]) is not None,
                "malformed_seed:" + label)
        mapping[key] = seed
    require(len(set(mapping.values())) == len(mapping), "distinct_seed_collision:" + label)
    for unit in ("nos_link.c", "libcan.c", "libi2c.c", "libspi.c", "libuart.c"):
        require(any(src.endswith("/" + unit) for src, _ in mapping),
                "missing_gcov_target:" + label + ":" + unit)
    return mapping


def compile_configured(source: Path, label: str, evidence: Path) -> dict[tuple[str, str], str]:
    logpath = evidence / (label + "-build.log")
    cmd = common_docker(source) + [
        "bash", "-lc",
        'set -Eeuo pipefail; '
        'printf "container_workdir=%s\\n" "$(pwd -P)"; '
        'printf "CFE_SYNTHETIC_BUILDDATE=%s HOSTNAME=%s USER=%s\\n" '
        '"$BUILDDATE" "$HOSTNAME" "$USER"; '
        'printf "P2X_V2F_SAFE_DIRECTORY=%s\\n" "$GIT_CONFIG_VALUE_0"; '
        'gcc --version | head -n 1; ld --version | head -n 1; '
        'make build-fsw; make build-sim; make build-cryptolib'
    ]
    with logpath.open("x", encoding="utf-8") as log:
        p = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, check=False)
    require(p.returncode == 0, "offline_compilation_failed:" + label)
    text = logpath.read_text(encoding="utf-8", errors="replace")
    require("container_workdir=/work/nos3" in text and
            "P2X_V2F_SAFE_DIRECTORY=/work/nos3" in text and
            "[100%] Built target standalone" in text and
            "CFE_SYNTHETIC_BUILDDATE=" + BUILD_DATE in text and
            "HOSTNAME=" + BUILD_HOST in text and "USER=" + BUILD_USER in text,
            "build_environment_witness_missing:" + label)
    require(git(source, "status", "--porcelain") == "", "compiled_source_git_drift:" + label)
    return seed_pairs(text, label)


def self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="p2x-v2f-stage-fixture-") as temp:
        base = Path(temp)
        src, dst = base / "original", base / "copy"
        for rel in BUILD_DIRS:
            p = src / rel
            p.mkdir(parents=True)
            (p / "MUST_NOT_COPY.txt").write_text("old build")
            (src / rel.split("/")[0] / "preserve.txt").write_text("tracked")
        shutil.copytree(src, dst, symlinks=True, ignore=ignore_builds(src))
        for rel in BUILD_DIRS:
            require(not (dst / rel).exists(), "build_exclusion_failed:" + rel)
            require((src / rel / "MUST_NOT_COPY.txt").exists(), "original_modified:" + rel)
    x = {"dependency_descriptors": [{"dependency": "a", "path": "/work/nos3/a", "describe": "x"}]}
    require(canonical_json(x) == canonical_json(json.loads(canonical_json(x))),
            "descriptor_canonicalization")
    require(git_env_args() == [
        "--env", "GIT_CONFIG_COUNT=1",
        "--env", "GIT_CONFIG_KEY_0=safe.directory",
        "--env", "GIT_CONFIG_VALUE_0=/work/nos3",
    ], "safe_directory_env_contract")
    policy = json.loads(GATE.read_text(encoding="utf-8"))
    closed = (
        policy["execution_authorized"] is False and
        policy["authorization_scope"]["offline_full_build"] is False and
        policy["decision"] ==
        "V2F_IMPLEMENTATION_AND_STATIC_VALIDATION_ONLY__FULL_BUILD_NOT_AUTHORIZED"
    )
    authorized = (
        policy["execution_authorized"] is True and
        policy["authorization_scope"]["offline_full_build"] is True and
        policy["decision"] == "AUTHOR_EXPLICITLY_APPROVED_V2F_OFFLINE_REBUILD"
    )
    require(closed or authorized, "self_test_invalid_v2f_build_gate")
    require(policy["authorization_scope"]["nominal_runtime"] is False and
            policy["authorization_scope"]["cosmos"] is False and
            policy["authorization_scope"]["faults"] is False and
            policy["authorization_scope"]["merge_pr215"] is False and
            policy["environment_final_acceptance"] is False,
            "self_test_runtime_science_or_merge_scope_open")
    print("P2X_V2F_EXCLUDE_OLD_BUILD_OUTPUTS_SELF_TEST=PASS")
    print("P2X_V2F_SAFE_DIRECTORY_ENV_SELF_TEST=PASS")
    print("P2X_V2F_DESCRIPTOR_MAP_GATE_SELF_TEST=PASS")
    print("P2X_V2F_FULL_BUILD_AUTHORIZATION=" +
          ("AUTHORIZED_HOST_ONLY" if authorized else "CLOSED"))


def manifest_for(out: Path, initial: dict[str, object],
                 seed_maps: dict[str, dict[tuple[str, str], str]],
                 descriptor_maps: dict[str, dict]) -> Path:
    primary, repeat = out / "primary/source", out / "repeat/source"
    rows = []
    for rel in ARTIFACTS:
        pa, pb = primary / rel, repeat / rel
        ha, hb = sha(pa), sha(pb)
        rows.append({
            "path": rel, "primary_sha256": ha, "repeat_sha256": hb,
            "primary_size_bytes": pa.stat().st_size,
            "repeat_size_bytes": pb.stat().st_size,
            "repeat_match": ha == hb,
        })
    same = all(row["repeat_match"] for row in rows)
    descriptor_canonical = canonical_json(descriptor_maps["primary"])
    descriptor_sha = hashlib.sha256(descriptor_canonical.encode("utf-8")).hexdigest()
    m = {
        "schema": 1,
        "experiment_id": "P2X-NOS3-RG-001",
        "phase": "P2X_PHASE_A_PROSPECTIVE_V2F_OFFLINE_BUILD_ONLY",
        "classification": ("V2F_DUAL_OFFLINE_BUILD_BYTE_IDENTITY_PASS__RUNTIME_UNTESTED"
                           if same else "BUILD_BYTE_REPRODUCTION_HOLD"),
        "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "preserved_v2_manifest_sha256": initial["v2_manifest_sha256"],
        "preserved_v2e_manifest_sha256": initial["v2e_manifest_sha256"],
        "historical_locks_sha256_before": initial["july_locks_sha256"],
        "historical_locks_sha256_after": stamps(),
        "nos3_revision": NOS3, "fortytwo_revision": FT_REV,
        "fortytwo_p2x_sha256": FT_HASH,
        "image": IMAGE, "platform": "linux/amd64", "network": "none",
        "container_workdir": "/work/nos3",
        "git_safe_directory": SAFE_DIR,
        "git_safe_directory_injected_ephemerally": True,
        "prebuild_dependency_descriptor_maps_identical": True,
        "dependency_descriptor_map_sha256": descriptor_sha,
        "probe_descriptor_map_sha256": PROBE_MAP_SHA,
        "synthetic_reproducibility_labels_not_actual_build_timestamps": True,
        "synthetic_build_date": BUILD_DATE,
        "synthetic_build_host": BUILD_HOST,
        "synthetic_build_user": BUILD_USER,
        "build_recipe": RECIPE,
        "launcher_sha256": sha(LAUNCHER),
        "descriptor_helper_sha256": sha(DESCRIPTOR_HELPER),
        "descriptor_map_file_sha256": {
            label: sha(out / (label + "-descriptor-map.json"))
            for label in ("primary", "repeat")
        },
        "seed_maps": {
            label: [{"source": key[0], "object": key[1], "seed": value}
                    for key, value in sorted(mapping.items())]
            for label, mapping in seed_maps.items()
        },
        "primary_source_root": str(primary.resolve()),
        "repeat_source_root": str(repeat.resolve()),
        "required_artifact_count": 9,
        "artifacts": rows,
        "repeat_match_all": same,
        "historical_july_build_lock_replaced": False,
        "old_v2_evidence_overwritten": False,
        "old_v2e_evidence_overwritten": False,
        "no_runtime_performed": True,
        "no_scientific_observations": True,
        "environment_final_acceptance": False,
    }
    path = out / "p2x-v2f-build-manifest.json"
    with path.open("x", encoding="utf-8") as fd:
        json.dump(m, fd, indent=2, sort_keys=True)
        fd.write("\n")
    with (out / "artifact-hash-comparison.tsv").open("x", encoding="utf-8") as fd:
        fd.write("relative_path\tprimary_sha256\trepeat_sha256\trepeat_match\tprimary_size_bytes\trepeat_size_bytes\n")
        for row in rows:
            fd.write("\t".join(str(row[k]) for k in (
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
            "P2X-PHASE-A-V2F-OFFLINE-BUILD-EXECUTION-GATE-2026-10-05",
            "wrong_execution_gate")

    if mode == ["--build"]:
        require(policy["execution_authorized"] is True and
                policy["decision"] == "AUTHOR_EXPLICITLY_APPROVED_V2F_OFFLINE_REBUILD" and
                policy["authorization_scope"]["offline_full_build"] is True,
                "separate_v2f_authorization_absent__no_build")

    baseline = preserved()
    verify_pristine(baseline)

    if mode == ["--inspect"]:
        closed = (
            policy["execution_authorized"] is False and
            policy["authorization_scope"]["offline_full_build"] is False and
            policy["decision"] ==
            "V2F_IMPLEMENTATION_AND_STATIC_VALIDATION_ONLY__FULL_BUILD_NOT_AUTHORIZED"
        )
        authorized = (
            policy["execution_authorized"] is True and
            policy["authorization_scope"]["offline_full_build"] is True and
            policy["decision"] == "AUTHOR_EXPLICITLY_APPROVED_V2F_OFFLINE_REBUILD"
        )
        require(closed or authorized, "v2f_implementation_gate_unexpected_state")
        require(policy["probe_result"] == "PASS" and
                policy["descriptor_map_sha256"] == PROBE_MAP_SHA,
                "probe_pass_not_bound")
        require(policy["authorization_scope"]["nominal_runtime"] is False and
                policy["authorization_scope"]["cosmos"] is False and
                policy["authorization_scope"]["faults"] is False and
                policy["authorization_scope"]["merge_pr215"] is False and
                policy["environment_final_acceptance"] is False,
                "runtime_science_or_merge_scope_open")
        print("P2X_V2F_IMPLEMENTATION_STATIC_INSPECTION=PASS")
        print("P2X_V2F_PROBE_PASS_BOUND=PASS")
        print("P2X_V2F_FULL_BUILD=" +
              ("AUTHORIZED_NOT_RUN" if authorized else "NOT_AUTHORIZED"))
        print("P2X_V2F_RUNTIME=NOT_AUTHORIZED")
        return

    require(shutil.which("docker") is not None, "docker_unavailable")
    platform = subprocess.check_output(
        ["docker", "image", "inspect", IMAGE, "--format", "{{.Os}}/{{.Architecture}}"],
        text=True
    ).strip()
    require(platform == "linux/amd64", "locked_image_platform_drift")
    require(RUNTIME.is_dir(), "missing_runtime_root")

    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = RUNTIME / ("p2xa-nos3-v2f-build-" + stamp + "-" + uuid.uuid4().hex[:10])
    out.mkdir(mode=0o700)
    with (out / "build-provenance.json").open("x", encoding="utf-8") as fd:
        json.dump({
            "real_build_start_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "synthetic_cfe_labels": [BUILD_DATE, BUILD_HOST, BUILD_USER],
            "image": IMAGE,
            "canonical_nos3": NOS3,
            "safe_directory": SAFE_DIR,
            "preserved_v2_manifest_sha256": baseline["v2_manifest_sha256"],
            "preserved_v2e_manifest_sha256": baseline["v2e_manifest_sha256"],
            "historical_locks_before": baseline["july_locks_sha256"],
            "prospective_execution_gate": policy["decision"],
        }, fd, indent=2, sort_keys=True)
        fd.write("\n")

    print("P2X_V2F_NEW_IGNORED_EVIDENCE=" + str(out), flush=True)
    try:
        for label in ("primary", "repeat"):
            stage(SOURCE, out / label / "source")
            print("P2X_V2F_INDEPENDENT_SOURCE_STAGED=" + label, flush=True)
        verify_pristine(baseline)

        descriptors = {}
        for label in ("primary", "repeat"):
            descriptors[label] = configure_and_descriptor(
                out / label / "source", label, out)
            print("P2X_V2F_CONFIGURED_AND_DESCRIPTOR_CAPTURED=" + label, flush=True)
        require(canonical_json(descriptors["primary"]) ==
                canonical_json(descriptors["repeat"]),
                "prebuild_dependency_descriptor_maps_differ")
        descriptor_sha = hashlib.sha256(
            canonical_json(descriptors["primary"]).encode("utf-8")).hexdigest()
        print("P2X_V2F_PREBUILD_DESCRIPTOR_MAPS=IDENTICAL", flush=True)
        print("P2X_V2F_DESCRIPTOR_MAP_SHA256=" + descriptor_sha, flush=True)

        seeds = {}
        for label in ("primary", "repeat"):
            seeds[label] = compile_configured(out / label / "source", label, out)
            verify_pristine(baseline)
            print("P2X_V2F_BUILD_COMPLETED=" + label, flush=True)
        require(seeds["primary"] == seeds["repeat"],
                "compiler_launcher_seed_maps_differ")

        manifest = manifest_for(out, baseline, seeds, descriptors)
        verify_pristine(baseline)
        print("P2X_V2F_MANIFEST=" + str(manifest), flush=True)
        m = json.loads(manifest.read_text(encoding="utf-8"))
        require(m["repeat_match_all"] is True,
                "nine_raw_SHA_mismatch_preserve_both_new_builds")
        subprocess.run([sys.executable, str(VERIFIER), str(manifest)], check=True)
        print("P2X_V2F_BUILD=RAW_9_OF_9_PASS__RUNTIME_NOT_EXECUTED")
    except BaseException as exc:
        with (out / "operator-status.txt").open("x", encoding="utf-8") as fd:
            fd.write("P2X_V2F_OPERATOR_HOLD=" + str(exc) + "\n")
            fd.write("P2X_V2F_EVIDENCE_PRESERVED=" + str(out) + "\n")
        raise

    print("P2X_V2F_OLD_V2_AND_V2E_HOLDS_UNMODIFIED=PASS")
    print("P2X_V2F_FINAL_ENVIRONMENT_ACCEPTANCE=NO")
    print("P2X_V2F_RUNTIME_EXECUTED=NO")


if __name__ == "__main__":
    main()
