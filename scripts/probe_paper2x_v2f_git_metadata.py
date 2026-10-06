#!/usr/bin/env python3
"""P2X v2f read-only pinned-OCI Git metadata mechanism probe.

Host mode (--probe) is separately author-gated. It mounts the preserved v2e
primary/repeat source trees READ-ONLY into the pinned OCI and reproduces cFE's
build-time git-describe dependency map with an ephemeral safe.directory config.
It performs no CMake, make, build, runtime, source mutation, or evidence mutation.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "paper2x" / "phase_a" / "V2F_OFFLINE_BUILD_EXECUTION_GATE_2026-10-05.json"
EVIDENCE = ROOT / "artifacts" / "runtime" / "p2xa-nos3-v2e-build-20261005T141959Z-7c8ceaa570"
MANIFEST = EVIDENCE / "p2x-v2e-build-manifest.json"
IMAGE = "ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"
NOS3 = "5a3bdee6be9a2c67fdf994ae6db56d5c60395302"
NOS3_DESC = "v1_07_05"
ONAIR = "aa5559c0f234eba263041b6007573f16870194e5"
ONAIR_DESC = "v0.0.13-119-gaa5559c"
MANIFEST_SHA = "25c2b15b5344f8c05dde8c4b85881571859d8601d15d972c6908978ecbfa5938"
PRIMARY_CORE_SHA = "cab1f6602e7b371171d851b0c6f78a69ddd7c7625457e2e9a12f75c7e0f86001"
REPEAT_CORE_SHA = "40b48fc62719be1d01cc104ff51a1ceab6ad42f9e925d30b700a3f2dd8412e7d"
TRIALS = 5


def hold(why: str) -> None:
    raise SystemExit("P2X_V2F_PROBE_HOLD=" + why)


def require(ok: bool, why: str) -> None:
    if not ok:
        hold(why)


def sha256(path: Path) -> str:
    require(path.is_file(), "missing_file:" + str(path))
    h = hashlib.sha256()
    with path.open("rb") as fd:
        for chunk in iter(lambda: fd.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(ROOT), *args],
        text=True,
        stderr=subprocess.PIPE,
    ).strip()


def gate() -> dict:
    g = json.loads(GATE.read_text(encoding="utf-8"))
    require(g["record_id"] ==
            "P2X-PHASE-A-V2F-OFFLINE-BUILD-EXECUTION-GATE-2026-10-05",
            "wrong_gate")
    require(g["decision"] == "AUTHOR_EXPLICITLY_APPROVED_V2F_READ_ONLY_HOST_PROBE",
            "probe_decision_closed")
    require(g.get("probe_authorized") is True,
            "probe_not_authorized")
    require(g["execution_authorized"] is False,
            "full_execution_must_remain_closed")
    scope = g["authorization_scope"]
    require(scope["read_only_host_probe"] is True and
            scope["offline_full_build"] is False and
            scope["nominal_runtime"] is False and
            scope["cosmos"] is False and
            scope["faults"] is False and
            scope["merge_pr215"] is False,
            "scope_widened")
    require(g["environment_final_acceptance"] is False,
            "final_acceptance_open")
    return g


def preserved_hashes() -> dict[str, str]:
    return {
        "manifest": sha256(MANIFEST),
        "primary_core": sha256(EVIDENCE / "primary/source/fsw/build/exe/cpu1/core-cpu1"),
        "repeat_core": sha256(EVIDENCE / "repeat/source/fsw/build/exe/cpu1/core-cpu1"),
    }


def require_preserved() -> dict[str, str]:
    h = preserved_hashes()
    require(h["manifest"] == MANIFEST_SHA, "v2e_manifest_drift")
    require(h["primary_core"] == PRIMARY_CORE_SHA, "v2e_primary_core_drift")
    require(h["repeat_core"] == REPEAT_CORE_SHA, "v2e_repeat_core_drift")
    return h


def run_git(path: str, *args: str) -> str:
    p = subprocess.run(
        ["git", "-C", path, *args],
        text=True,
        capture_output=True,
    )
    if p.returncode != 0:
        hold("inner_git_failed:" + path + ":" + p.stderr.strip().replace("\n", " ")[:300])
    return p.stdout.strip()


def inner() -> None:
    require(os.environ.get("GIT_CONFIG_COUNT") == "1", "missing_git_config_count")
    require(os.environ.get("GIT_CONFIG_KEY_0") == "safe.directory", "wrong_git_config_key")
    require(os.environ.get("GIT_CONFIG_VALUE_0") == "/work/nos3", "wrong_safe_directory")

    require(run_git("/work/nos3", "rev-parse", "HEAD") == NOS3, "nos3_head")
    require(run_git("/work/nos3", "describe", "--tags", "--always", "--dirty") ==
            NOS3_DESC, "nos3_describe")
    require(run_git("/work/nos3/components/onair", "describe", "--tags", "--always", "--dirty") ==
            NOS3_DESC, "onair_parent_describe")
    require(run_git("/work/nos3/components/onair/fsw", "rev-parse", "HEAD") ==
            ONAIR, "onair_submodule_head")
    require(run_git("/work/nos3/components/onair/fsw", "describe", "--tags", "--always", "--dirty") ==
            ONAIR_DESC, "onair_submodule_describe")

    cache = Path("/work/nos3/fsw/build/mission_vars.cache")
    require(cache.is_file(), "missing_mission_vars_cache")
    lines = cache.read_text(encoding="utf-8", errors="strict").splitlines()
    require(len(lines) % 2 == 0, "malformed_mission_vars_cache")
    values = {lines[i]: lines[i + 1] for i in range(0, len(lines), 2)}

    deps = [x for x in values.get("MISSION_DEPS", "").split(";") if x]
    require(deps, "empty_mission_deps")
    entries: list[tuple[str, str, str]] = []

    mission_dir = values.get("MISSION_SOURCE_DIR")
    require(bool(mission_dir), "missing_mission_source_dir")
    entries.append(("MISSION", mission_dir,
                    run_git(mission_dir, "describe", "--tags", "--always", "--dirty")))

    for dep in deps:
        key = dep + "_MISSION_DIR"
        path = values.get(key)
        require(bool(path), "missing_dependency_dir:" + dep)
        desc = run_git(path, "describe", "--tags", "--always", "--dirty")
        entries.append((dep, path, desc))

    result = {
        "schema": 1,
        "nos3_head": NOS3,
        "nos3_describe": NOS3_DESC,
        "onair_parent_describe": NOS3_DESC,
        "onair_submodule_head": ONAIR,
        "onair_submodule_describe": ONAIR_DESC,
        "dependency_descriptors": [
            {"dependency": dep, "path": path, "describe": desc}
            for dep, path, desc in entries
        ],
    }
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))


def docker_probe(source: Path) -> dict:
    require(source.is_dir(), "missing_preserved_source:" + str(source))
    cmd = [
        "docker", "run", "--rm", "--read-only",
        "--platform", "linux/amd64", "--network", "none",
        "--hostname", "p2x-v2f-probe",
        "--user", f"{os.getuid()}:{os.getgid()}",
        "--env", "HOME=/tmp",
        "--env", "PYTHONDONTWRITEBYTECODE=1",
        "--env", "GIT_CONFIG_COUNT=1",
        "--env", "GIT_CONFIG_KEY_0=safe.directory",
        "--env", "GIT_CONFIG_VALUE_0=/work/nos3",
        "--tmpfs", "/tmp:rw,nosuid,nodev,noexec",
        "--mount", f"type=bind,source={source},target=/work/nos3,readonly",
        "--mount", f"type=bind,source={Path(__file__).resolve()},target=/opt/p2x_v2f_probe.py,readonly",
        "--workdir", "/work/nos3",
        IMAGE,
        "python3", "/opt/p2x_v2f_probe.py", "--inner",
    ]
    p = subprocess.run(cmd, text=True, capture_output=True)
    require(p.returncode == 0,
            "docker_probe_failed:" + p.stdout[-500:] + p.stderr[-500:])
    out = p.stdout.strip().splitlines()
    require(len(out) == 1, "unexpected_inner_output")
    try:
        return json.loads(out[0])
    except json.JSONDecodeError as exc:
        hold("invalid_inner_json:" + str(exc))


def self_test() -> None:
    sample = {
        "MISSION_DEPS": "a;b",
        "a_MISSION_DIR": "/work/nos3/a",
        "b_MISSION_DIR": "/work/nos3/b",
    }
    require(sample["MISSION_DEPS"].split(";") == ["a", "b"], "dep_split")
    require(IMAGE.endswith("06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"),
            "image_pin")
    require(TRIALS == 5, "trial_count")
    print("P2X_V2F_PROBE_STATIC_SELF_TEST=PASS")
    print("P2X_V2F_BUILD_EXECUTED=NO")
    print("P2X_V2F_RUNTIME_EXECUTED=NO")


def probe() -> None:
    gate()
    require(ROOT.name == "mission-aware-satellite-cyber-recovery", "wrong_root")
    require(git("status", "--porcelain") == "", "research_tree_dirty")
    require(subprocess.run(["docker", "version"], stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL).returncode == 0,
            "docker_unavailable")
    platform = subprocess.check_output(
        ["docker", "image", "inspect", IMAGE, "--format", "{{.Os}}/{{.Architecture}}"],
        text=True,
    ).strip()
    require(platform == "linux/amd64", "image_platform")

    before = require_preserved()
    all_results: dict[str, list[dict]] = {}
    for label in ("primary", "repeat"):
        source = EVIDENCE / label / "source"
        trials = []
        for trial in range(1, TRIALS + 1):
            result = docker_probe(source)
            trials.append(result)
            print(f"P2X_V2F_PROBE_TRIAL={label}:{trial}=PASS")
        canonical = json.dumps(trials[0], sort_keys=True, separators=(",", ":"))
        require(all(json.dumps(x, sort_keys=True, separators=(",", ":")) == canonical
                    for x in trials), "within_tree_descriptor_instability:" + label)
        all_results[label] = trials

    p = json.dumps(all_results["primary"][0], sort_keys=True, separators=(",", ":"))
    r = json.dumps(all_results["repeat"][0], sort_keys=True, separators=(",", ":"))
    require(p == r, "primary_repeat_descriptor_map_mismatch")
    map_sha = hashlib.sha256(p.encode("utf-8")).hexdigest()

    require(require_preserved() == before, "preserved_evidence_mutated")
    require(git("status", "--porcelain") == "", "research_tree_mutated")

    print("P2X_V2F_SAFE_DIRECTORY_PINNED_OCI_PROBE=PASS")
    print("P2X_V2F_DEPENDENCY_DESCRIPTOR_MAP_REPEATABILITY=PASS")
    print("P2X_V2F_PRIMARY_REPEAT_DESCRIPTOR_MAP=IDENTICAL")
    print("P2X_V2F_DESCRIPTOR_MAP_SHA256=" + map_sha)
    print("P2X_V2F_BUILD_EXECUTED=NO")
    print("P2X_V2F_RUNTIME_EXECUTED=NO")
    print("P2X_V2F_EVIDENCE_MUTATED=NO")
    print("P2X_V2F_FULL_BUILD_AUTHORIZATION=NO")
    print("P2X_V2F_ENVIRONMENT_FINAL_ACCEPTANCE=NO")


def main() -> None:
    args = sys.argv[1:]
    require(len(args) == 1 and args[0] in ("--self-test", "--probe", "--inner"), "usage")
    if args[0] == "--self-test":
        self_test()
    elif args[0] == "--inner":
        inner()
    else:
        probe()


if __name__ == "__main__":
    main()
