#!/usr/bin/env python3
"""Independent read-only verifier for a successful P2X Phase-A v2f build."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = (ROOT / "artifacts/runtime").resolve()
CANONICAL = ROOT / "external/nos3"
FT = ROOT / "external/fortytwo"
LAUNCHER = ROOT / "scripts/p2x_v2e_seed_launcher.py"
HELPER = ROOT / "scripts/p2x_v2f_descriptor_map.py"
OLD_V2 = RUNTIME / "p2xa-nos3-v2-build-20261003T192146Z-99065"
OLD_V2E = RUNTIME / "p2xa-nos3-v2e-build-20261005T141959Z-7c8ceaa570"

PIN = "5a3bdee6be9a2c67fdf994ae6db56d5c60395302"
PIN_LC = "5daef363c95d71c1ff3c5e9dcd4dddab560e8b39"
PIN_HW = "d65f77dea94467b7cb71053eb2f58f7a0cde3b02"
PIN_FT = "eda252bf31f27850e867e698cfdd963e143ead1f"
HASH_FT = "b4d054bdd8a95dd429201466833fba8403efec4bdef09a9ed7040131dda3006d"
IMAGE = "ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"
V2_PRIMARY = "db64bf080232d64d5c39301e2f712885cf85e86d93c33c94fb46325fda1533fb"
V2_REPEAT = "5a0d746a01eeac38ee555d664673ae68f0b4f4b1b96c38e06923109867ea296b"
V2E_MANIFEST_SHA = "25c2b15b5344f8c05dde8c4b85881571859d8601d15d972c6908978ecbfa5938"
V2E_PRIMARY = "cab1f6602e7b371171d851b0c6f78a69ddd7c7625457e2e9a12f75c7e0f86001"
V2E_REPEAT = "40b48fc62719be1d01cc104ff51a1ceab6ad42f9e925d30b700a3f2dd8412e7d"
PROBE_MAP_SHA = "499525c90430ae0dd17fc297be0388b2eae51fdb6623f3d338b0a2f392460278"

NINE = (
    "cfg/build/launch.sh", "fsw/build/exe/cpu1/core-cpu1",
    "sims/build/bin/nos3-single-simulator", "sims/build/bin/nos3-sim-cmdbus-bridge",
    "gsw/build/support/standalone", "cfg/build/InOut/Inp_Sim.txt",
    "cfg/build/InOut/Inp_IPC.txt", "sims/build/bin/nos_engine_server_config.json",
    "sims/build/bin/nos3-simulator.xml",
)
LOCKS = ("fortytwo-lock.txt", "nominal-build-lock.txt",
         "nominal-runtime-preflight-lock.txt", "nos3-submodule-lock.txt")
RECIPE = (
    "bash ./scripts/cfg/config.sh",
    "mkdir -p fsw/build",
    "cd fsw/build && cmake -DCMAKE_INSTALL_PREFIX=exe -DCMAKE_BUILD_TYPE=debug ../cfe",
    "P2X v2f dependency-descriptor gate",
    "make --no-print-directory -C fsw/build mission-install",
    "make build-sim",
    "make build-cryptolib",
)


def deny(reason: str) -> None:
    raise SystemExit("P2X_V2F_INDEPENDENT_READBACK_HOLD=" + reason)


def check(ok: bool, reason: str) -> None:
    if not ok:
        deny(reason)


def hash_file(path: Path) -> str:
    check(path.is_file() and path.stat().st_size > 0, "missing_or_empty:" + str(path))
    h = hashlib.sha256()
    with path.open("rb") as fd:
        for chunk in iter(lambda: fd.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def git(where: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(where), *args], text=True, stderr=subprocess.PIPE
    ).strip()


def seed_value(source: str, obj: str) -> str:
    return "P2X-NOS3-RG-001:v2e:" + hashlib.sha256(
        ("P2X-v2e\x00" + source + "\x00" + obj).encode("utf-8")
    ).hexdigest()


def submodule_paths_from_status(text: str) -> list[str]:
    paths = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        check(len(parts) >= 2, "malformed_submodule_status")
        rel = parts[1]
        p = Path(rel)
        check(not p.is_absolute() and ".." not in p.parts,
              "unsafe_submodule_path:" + rel)
        paths.append(rel)
    check(len(paths) == len(set(paths)), "duplicate_submodule_path")
    return sorted(paths)


def safe_directory_paths(src: Path) -> list[str]:
    rels = submodule_paths_from_status(git(src, "submodule", "status", "--recursive"))
    values = ["/work/nos3"] + ["/work/nos3/" + rel for rel in rels]
    check("/work/nos3/components/onair/fsw" in values,
          "onair_submodule_not_registered")
    return values


def source_check(src: Path) -> None:
    check(git(src, "rev-parse", "HEAD") == PIN and
          git(src, "status", "--porcelain") == "", "source_revision_or_worktree_drift")
    check(git(src / "fsw/apps/lc", "rev-parse", "HEAD") == PIN_LC and
          git(src / "fsw/apps/hwlib", "rev-parse", "HEAD") == PIN_HW,
          "submodule_revision_drift")
    for rel in ("fsw/apps/lc", "fsw/apps/hwlib"):
        sub = src / rel
        check(Path(git(sub, "rev-parse", "--absolute-git-dir")).resolve()
              .is_relative_to(src.resolve()), "external_submodule_gitdir:" + rel)
        check(Path(git(sub, "rev-parse", "--show-toplevel")).resolve() == sub.resolve(),
              "external_submodule_worktree:" + rel)
    check(not any(line[:1] in ("+", "-", "U") for line in
                  git(src, "submodule", "status", "--recursive").splitlines()),
          "recursive_submodule_drift")


def self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="p2x-v2f-verify-") as d:
        a, b = Path(d) / "a", Path(d) / "b"
        a.write_bytes(b"A")
        b.write_bytes(b"A")
        check(hash_file(a) == hash_file(b), "equal_bytes")
        b.write_bytes(b"B")
        check(hash_file(a) != hash_file(b), "unequal_bytes")
        check(seed_value("x/a.c", "y/a.o") == seed_value("x/a.c", "y/a.o"),
              "seed_repeat")
        check(seed_value("x/a.c", "y/a.o") != seed_value("x/b.c", "y/b.o"),
              "seed_distinct")
    print("P2X_V2F_RAW_BYTE_NEGATIVE_CONTROL=PASS")
    print("P2X_V2F_INDEPENDENT_SEED_NEGATIVE_CONTROL=PASS")
    print("P2X_V2F_RUNTIME=NOT_TESTED")


def main() -> None:
    if sys.argv[1:] == ["--self-test"]:
        self_test()
        return
    check(len(sys.argv) == 2, "usage:absolute_v2f_manifest")
    path = Path(sys.argv[1]).expanduser().resolve()
    evidence = path.parent
    check(path.name == "p2x-v2f-build-manifest.json" and
          evidence.parent == RUNTIME and evidence.name.startswith("p2xa-nos3-v2f-build-"),
          "manifest_not_in_distinct_v2f_evidence_root")

    m = json.loads(path.read_text(encoding="utf-8"))
    check(m["schema"] == 1 and m["experiment_id"] == "P2X-NOS3-RG-001" and
          m["phase"] == "P2X_PHASE_A_PROSPECTIVE_V2F_OFFLINE_BUILD_ONLY",
          "manifest_scope")
    primary = (evidence / "primary/source").resolve()
    repeat = (evidence / "repeat/source").resolve()
    check(m["classification"] ==
          "V2F_DUAL_OFFLINE_BUILD_BYTE_IDENTITY_PASS__RUNTIME_UNTESTED",
          "raw_nine_identity_not_accepted")
    check(m["required_artifact_count"] == 9 and m["repeat_match_all"] is True,
          "nine_artifact_identity_not_proven")
    check(m["nos3_revision"] == PIN and m["fortytwo_revision"] == PIN_FT and
          m["fortytwo_p2x_sha256"] == HASH_FT, "source_authority")
    check(m["image"] == IMAGE and m["platform"] == "linux/amd64" and
          m["network"] == "none" and m["container_workdir"] == "/work/nos3" and
          tuple(m["build_recipe"]) == RECIPE, "image_platform_recipe")
    expected_safe_dirs = safe_directory_paths(primary)
    check(m["git_safe_directory"] == "/work/nos3" and
          m["git_safe_directories"] == expected_safe_dirs and
          m["git_safe_directory_policy"] ==
          "root_plus_registered_recursive_submodule_worktrees" and
          m["git_safe_directory_injected_ephemerally"] is True and
          m["prebuild_dependency_descriptor_maps_identical"] is True,
          "safe_directory_or_descriptor_gate")
    check(m["probe_descriptor_map_sha256"] == PROBE_MAP_SHA,
          "probe_map_binding")
    check(m["synthetic_reproducibility_labels_not_actual_build_timestamps"] is True and
          m["synthetic_build_date"] == "202610030000" and
          m["synthetic_build_host"] == "p2x-v2e-builder" and
          m["synthetic_build_user"] == "p2x-builder", "synthetic_metadata")
    for key in ("old_v2_evidence_overwritten", "old_v2e_evidence_overwritten",
                "historical_july_build_lock_replaced", "environment_final_acceptance"):
        check(m[key] is False, "forbidden_claim:" + key)
    check(m["no_runtime_performed"] is True and m["no_scientific_observations"] is True,
          "runtime_or_science_claim")

    check(primary != repeat and primary != CANONICAL.resolve() and repeat != CANONICAL.resolve(),
          "source_alias")
    check(Path(m["primary_source_root"]).resolve() == primary and
          Path(m["repeat_source_root"]).resolve() == repeat, "manifest_source_root")
    for src in (primary, repeat):
        source_check(src)

    check(git(ROOT, "status", "--porcelain") == "" and
          git(CANONICAL, "rev-parse", "HEAD") == PIN and
          git(CANONICAL, "status", "--porcelain") == "", "canonical_or_repo_drift")
    check(git(FT, "rev-parse", "HEAD") == PIN_FT and
          git(FT, "status", "--porcelain") == "" and hash_file(FT / "42") == HASH_FT,
          "fortytwo_drift")

    old_v2 = OLD_V2 / "p2x-v2-build-manifest.json"
    old_v2e = OLD_V2E / "p2x-v2e-build-manifest.json"
    v2 = json.loads(old_v2.read_text(encoding="utf-8"))
    v2e = json.loads(old_v2e.read_text(encoding="utf-8"))
    check(v2["classification"] == "BUILD_BYTE_REPRODUCTION_HOLD" and
          sum(bool(x["repeat_match"]) for x in v2["artifacts"]) == 8,
          "v2_hold_not_preserved")
    check(hash_file(CANONICAL / "fsw/build/exe/cpu1/core-cpu1") == V2_PRIMARY and
          hash_file(OLD_V2 / "repeat/source/fsw/build/exe/cpu1/core-cpu1") == V2_REPEAT,
          "v2_core_drift")
    check(hash_file(old_v2) == m["preserved_v2_manifest_sha256"], "v2_manifest_drift")

    check(hash_file(old_v2e) == V2E_MANIFEST_SHA ==
          m["preserved_v2e_manifest_sha256"] and
          v2e["classification"] == "BUILD_BYTE_REPRODUCTION_HOLD" and
          sum(bool(x["repeat_match"]) for x in v2e["artifacts"]) == 8,
          "v2e_hold_not_preserved")
    check(hash_file(OLD_V2E / "primary/source/fsw/build/exe/cpu1/core-cpu1") == V2E_PRIMARY and
          hash_file(OLD_V2E / "repeat/source/fsw/build/exe/cpu1/core-cpu1") == V2E_REPEAT,
          "v2e_core_drift")

    locks = {name: hash_file(ROOT / "artifacts" / name) for name in LOCKS}
    check(m["historical_locks_sha256_before"] == locks and
          m["historical_locks_sha256_after"] == locks, "july_lock_drift")
    check(hash_file(LAUNCHER) == m["launcher_sha256"], "launcher_hash_drift")
    check(hash_file(HELPER) == m["descriptor_helper_sha256"], "descriptor_helper_hash_drift")

    descriptor_maps = {}
    for label in ("primary", "repeat"):
        p = evidence / (label + "-descriptor-map.json")
        check(hash_file(p) == m["descriptor_map_file_sha256"][label],
              "descriptor_map_file_hash:" + label)
        descriptor_maps[label] = json.loads(p.read_text(encoding="utf-8"))
        check(descriptor_maps[label]["safe_directory"] == "/work/nos3" and
              descriptor_maps[label]["safe_directories"] ==
              safe_directory_paths(primary if label == "primary" else repeat) and
              descriptor_maps[label]["nos3_head"] == PIN and
              descriptor_maps[label]["nos3_describe"] == "v1_07_05" and
              descriptor_maps[label]["onair_submodule_head"] ==
              "aa5559c0f234eba263041b6007573f16870194e5" and
              descriptor_maps[label]["onair_submodule_describe"] ==
              "v0.0.13-119-gaa5559c", "descriptor_map_expected:" + label)
    check(canonical(descriptor_maps["primary"]) == canonical(descriptor_maps["repeat"]),
          "descriptor_maps_differ")
    desc_sha = hashlib.sha256(canonical(descriptor_maps["primary"]).encode("utf-8")).hexdigest()
    check(desc_sha == m["dependency_descriptor_map_sha256"], "descriptor_map_sha_drift")

    maps = m["seed_maps"]
    check(set(maps) == {"primary", "repeat"}, "seed_map_labels")
    for label in ("primary", "repeat"):
        entries = maps[label]
        check(len(entries) >= 5, "seed_entries:" + label)
        seen_units, seen_seeds = set(), set()
        log = (evidence / (label + "-build.log")).read_text(encoding="utf-8", errors="replace")
        check("P2X_V2F_SAFE_DIRECTORY=/work/nos3" in log and
              "P2X_V2F_SAFE_DIRECTORY_COUNT=" in log and
              "[100%] Built target standalone" in log and
              "CFE_SYNTHETIC_BUILDDATE=202610030000" in log and
              "HOSTNAME=p2x-v2e-builder USER=p2x-builder" in log,
              "build_log_witness:" + label)
        for item in entries:
            src, obj, seed = item["source"], item["object"], item["seed"]
            check(seed == seed_value(src, obj), "seed_value:" + label)
            check((src, obj) not in seen_units and seed not in seen_seeds,
                  "seed_collision:" + label)
            seen_units.add((src, obj)); seen_seeds.add(seed)
            check(("P2X_V2E_SEED_SOURCE=" + src + " OBJECT=" + obj +
                   " SEED=" + seed) in log.splitlines(), "seed_log_witness:" + label)
    check(maps["primary"] == maps["repeat"], "seed_maps_differ")

    rows = m["artifacts"]
    check([x["path"] for x in rows] == list(NINE), "nine_path_order")
    for row in rows:
        rel = row["path"]
        a, b = primary / rel, repeat / rel
        ha, hb = hash_file(a), hash_file(b)
        check(ha == hb == row["primary_sha256"] == row["repeat_sha256"] and
              row["repeat_match"] is True and
              a.stat().st_size == row["primary_size_bytes"] and
              b.stat().st_size == row["repeat_size_bytes"],
              "raw_sha_or_size:" + rel)

    for src in (primary, repeat):
        env_table = src / "fsw/build/amd64-nos3/default_cpu1/cpu1/cfe_build_env_table.c"
        generated = env_table.read_text(encoding="utf-8")
        for exact in ('{ "BUILDDATE", "202610030000" }',
                      '{ "BUILDHOST", "p2x-v2e-builder" }',
                      '{ "BUILDUSER", "p2x-builder" }'):
            check(exact in generated, "cfe_metadata:" + exact)
        version_table = src / "fsw/build/src/cfe_module_version_table.c"
        version = version_table.read_text(encoding="utf-8")
        check('{ "onair", "git:v1_07_05" }' in version,
              "onair_version_not_stabilized")

    print("P2X_V2F_INDEPENDENT_NINE_RAW_SHA256_READBACK=PASS")
    print("P2X_V2F_DEPENDENCY_DESCRIPTOR_MAP_READBACK=PASS")
    print("P2X_V2F_TWO_NEW_CANDIDATES=9_OF_9_BYTE_IDENTICAL")
    print("P2X_V2F_OLD_V2_AND_V2E_HOLDS_AND_JULY_LOCKS=PRESERVED")
    print("P2X_V2F_RUNTIME=NOT_TESTED")
    print("P2X_V2F_ENVIRONMENT_FINAL_ACCEPTANCE=NO")


if __name__ == "__main__":
    main()
