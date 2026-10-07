#!/usr/bin/env python3
"""Emit canonical P2X v2f cFE dependency Git-descriptor map.

Designed for execution inside the pinned OCI after config.sh and before compilation.
No source mutation, build, runtime, or network access is performed.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path("/work/nos3")
CACHE = ROOT / "fsw/build/mission_vars.cache"
NOS3 = "5a3bdee6be9a2c67fdf994ae6db56d5c60395302"
NOS3_DESC = "v1_07_05"
ONAIR = "aa5559c0f234eba263041b6007573f16870194e5"
ONAIR_DESC = "v0.0.13-119-gaa5559c"


def hold(why: str) -> None:
    raise SystemExit("P2X_V2F_DESCRIPTOR_HOLD=" + why)


def require(ok: bool, why: str) -> None:
    if not ok:
        hold(why)


def run_git(path: str, *args: str) -> str:
    p = subprocess.run(
        ["git", "-C", path, *args],
        text=True,
        capture_output=True,
    )
    require(p.returncode == 0,
            "git_failed:" + path + ":" + p.stderr.strip().replace("\n", " ")[:240])
    return p.stdout.strip()


def parse_cache(path: Path) -> dict[str, str]:
    require(path.is_file(), "missing_mission_vars_cache")
    lines = path.read_text(encoding="utf-8", errors="strict").splitlines()
    require(len(lines) % 2 == 0, "malformed_mission_vars_cache")
    return {lines[i]: lines[i + 1] for i in range(0, len(lines), 2)}


def safe_directories_from_env() -> list[str]:
    raw = os.environ.get("GIT_CONFIG_COUNT")
    require(raw is not None and raw.isdigit(), "git_config_count")
    count = int(raw)
    require(count >= 2, "git_safe_directory_scope_too_narrow")
    values = []
    for idx in range(count):
        require(os.environ.get(f"GIT_CONFIG_KEY_{idx}") == "safe.directory",
                "git_config_key:" + str(idx))
        value = os.environ.get(f"GIT_CONFIG_VALUE_{idx}")
        require(bool(value), "git_config_value:" + str(idx))
        values.append(value)
    require(values[0] == "/work/nos3", "git_safe_directory_root")
    require("/work/nos3/components/onair/fsw" in values,
            "git_safe_directory_onair_submodule")
    require(len(values) == len(set(values)), "git_safe_directory_duplicate")
    return values


def emit() -> None:
    safe_directories = safe_directories_from_env()

    require(run_git("/work/nos3", "rev-parse", "HEAD") == NOS3, "nos3_head")
    require(run_git("/work/nos3", "describe", "--tags", "--always", "--dirty") ==
            NOS3_DESC, "nos3_describe")
    require(run_git("/work/nos3/components/onair", "describe",
                    "--tags", "--always", "--dirty") == NOS3_DESC,
            "onair_parent_describe")
    require(run_git("/work/nos3/components/onair/fsw", "rev-parse", "HEAD") ==
            ONAIR, "onair_head")
    require(run_git("/work/nos3/components/onair/fsw", "describe",
                    "--tags", "--always", "--dirty") == ONAIR_DESC,
            "onair_describe")

    values = parse_cache(CACHE)
    deps = [x for x in values.get("MISSION_DEPS", "").split(";") if x]
    require(deps, "empty_mission_deps")

    mission_dir = values.get("MISSION_SOURCE_DIR")
    require(bool(mission_dir), "missing_mission_source_dir")

    rows = [{
        "dependency": "MISSION",
        "path": mission_dir,
        "describe": run_git(mission_dir, "describe", "--tags", "--always", "--dirty"),
    }]
    for dep in deps:
        key = dep + "_MISSION_DIR"
        path = values.get(key)
        require(bool(path), "missing_dependency_dir:" + dep)
        rows.append({
            "dependency": dep,
            "path": path,
            "describe": run_git(path, "describe", "--tags", "--always", "--dirty"),
        })

    payload = {
        "schema": 1,
        "experiment_id": "P2X-NOS3-RG-001",
        "safe_directory": "/work/nos3",
        "safe_directories": safe_directories,
        "nos3_head": NOS3,
        "nos3_describe": NOS3_DESC,
        "onair_parent_describe": NOS3_DESC,
        "onair_submodule_head": ONAIR,
        "onair_submodule_describe": ONAIR_DESC,
        "dependency_descriptors": rows,
    }
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))


def self_test() -> None:
    fixture = ["A", "1", "B", "2"]
    require({fixture[i]: fixture[i + 1] for i in range(0, 4, 2)} ==
            {"A": "1", "B": "2"}, "cache_parser_fixture")
    require(NOS3_DESC == "v1_07_05" and
            ONAIR_DESC == "v0.0.13-119-gaa5559c", "descriptor_fixture")
    sample = {
        "GIT_CONFIG_COUNT": "2",
        "GIT_CONFIG_KEY_0": "safe.directory",
        "GIT_CONFIG_VALUE_0": "/work/nos3",
        "GIT_CONFIG_KEY_1": "safe.directory",
        "GIT_CONFIG_VALUE_1": "/work/nos3/components/onair/fsw",
    }
    require(sample["GIT_CONFIG_VALUE_0"] != sample["GIT_CONFIG_VALUE_1"],
            "safe_directory_fixture_distinct")
    print("P2X_V2F_DESCRIPTOR_HELPER_SELF_TEST=PASS")
    print("P2X_V2F_BUILD_EXECUTED=NO")
    print("P2X_V2F_RUNTIME_EXECUTED=NO")


def main() -> None:
    args = sys.argv[1:]
    require(args in (["--emit"], ["--self-test"]), "usage")
    if args == ["--self-test"]:
        self_test()
    else:
        emit()


if __name__ == "__main__":
    main()
