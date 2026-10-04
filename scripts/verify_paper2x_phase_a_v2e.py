#!/usr/bin/env python3
"""Independent, read-only P2X Phase-A v2e nine-artifact byte verifier.

Does not import the v2e builder, does not launch Docker, and never patches,
strips, deletes, or normalizes either ELF or historical study evidence.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = (ROOT / "artifacts/runtime").resolve()
CANONICAL = ROOT / "external/nos3"
FT = ROOT / "external/fortytwo"
LAUNCHER = ROOT / "scripts/p2x_v2e_seed_launcher.py"
OLD = RUNTIME / "p2xa-nos3-v2-build-20261003T192146Z-99065"
PIN = "5a3bdee6be9a2c67fdf994ae6db56d5c60395302"
PIN_LC = "5daef363c95d71c1ff3c5e9dcd4dddab560e8b39"
PIN_HW = "d65f77dea94467b7cb71053eb2f58f7a0cde3b02"
PIN_FT = "eda252bf31f27850e867e698cfdd963e143ead1f"
HASH_FT = "b4d054bdd8a95dd429201466833fba8403efec4bdef09a9ed7040131dda3006d"
IMAGE = "ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"
OLD_PRIMARY = "db64bf080232d64d5c39301e2f712885cf85e86d93c33c94fb46325fda1533fb"
OLD_REPEAT = "5a0d746a01eeac38ee555d664673ae68f0b4f4b1b96c38e06923109867ea296b"
NINE = (
    "cfg/build/launch.sh", "fsw/build/exe/cpu1/core-cpu1",
    "sims/build/bin/nos3-single-simulator", "sims/build/bin/nos3-sim-cmdbus-bridge",
    "gsw/build/support/standalone", "cfg/build/InOut/Inp_Sim.txt",
    "cfg/build/InOut/Inp_IPC.txt", "sims/build/bin/nos_engine_server_config.json",
    "sims/build/bin/nos3-simulator.xml",
)
LOCKS = ("fortytwo-lock.txt", "nominal-build-lock.txt",
         "nominal-runtime-preflight-lock.txt", "nos3-submodule-lock.txt")
RECIPE = ("bash ./scripts/cfg/config.sh", "make build-fsw", "make build-sim",
          "make build-cryptolib")


def deny(reason: str) -> None:
    raise SystemExit("P2X_V2E_INDEPENDENT_READBACK_HOLD=" + reason)


def check(ok: bool, reason: str) -> None:
    if not ok:
        deny(reason)


def hash_file(path: Path) -> str:
    check(path.is_file() and path.stat().st_size > 0, "missing_or_empty:" + str(path))
    hash_obj = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            data = f.read(1024 * 1024)
            if not data:
                break
            hash_obj.update(data)
    return hash_obj.hexdigest()


def git(where: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(where), *args], text=True, stderr=subprocess.PIPE
    ).strip()


def seed_value(source: str, obj: str) -> str:
    return "P2X-NOS3-RG-001:v2e:" + hashlib.sha256(
        ("P2X-v2e\x00" + source + "\x00" + obj).encode("utf-8")
    ).hexdigest()


def test_algorithms() -> None:
    with tempfile.TemporaryDirectory(prefix="p2x-v2e-verify-fixture-") as directory:
        a, b = Path(directory) / "a", Path(directory) / "b"
        a.write_bytes(b"raw source A")
        b.write_bytes(b"raw source A")
        check(hash_file(a) == hash_file(b), "equal_raw_bytes_failed")
        b.write_bytes(b"raw source B")
        check(hash_file(a) != hash_file(b), "unequal_raw_bytes_falsely_passed")
        check(seed_value("f/a.c", "x/a.o") == seed_value("f/a.c", "x/a.o"),
              "seed_repeat_drift")
        check(seed_value("f/a.c", "x/a.o") != seed_value("f/b.c", "x/b.o"),
              "seed_distinct_source")
        check(seed_value("f/a.c", "x/a.o") != seed_value("f/a.c", "y/a.o"),
              "seed_missing_object_component")
    print("P2X_V2E_RAW_BYTE_NEGATIVE_CONTROL=PASS")
    print("P2X_V2E_INDEPENDENT_SEED_NEGATIVE_CONTROL=PASS")
    print("P2X_V2E_RUNTIME=NOT_TESTED")


def source_check(src: Path) -> None:
    check(git(src, "rev-parse", "HEAD") == PIN and
          git(src, "status", "--porcelain") == "", "source_revision_or_worktree_drift")
    check(git(src / "fsw/apps/lc", "rev-parse", "HEAD") == PIN_LC and
          git(src / "fsw/apps/hwlib", "rev-parse", "HEAD") == PIN_HW,
          "submodule_revision_drift")
    for rel in ("fsw/apps/lc", "fsw/apps/hwlib"):
        target = Path(git(src / rel, "rev-parse", "--absolute-git-dir")).resolve()
        check(target.is_relative_to(src.resolve()), "copied_submodule_external_gitdir:" + rel)
        check(Path(git(src / rel, "rev-parse", "--show-toplevel")).resolve()
              == (src / rel).resolve(), "copied_submodule_external_worktree:" + rel)
    check(not any(line[:1] in ("+", "-", "U") for line in
                  git(src, "submodule", "status", "--recursive").splitlines()),
          "recursive_submodule_drift")


def main() -> None:
    if sys.argv[1:] == ["--self-test"]:
        test_algorithms()
        return
    check(len(sys.argv) == 2, "usage:absolute_v2e_build_manifest")
    path = Path(sys.argv[1]).expanduser().resolve()
    e = path.parent
    check(path.name == "p2x-v2e-build-manifest.json" and
          e.parent == RUNTIME and e.name.startswith("p2xa-nos3-v2e-build-"),
          "manifest_not_in_distinct_new_ignored_evidence_root")
    manifest = json.loads(path.read_text(encoding="utf-8"))
    check(manifest["schema"] == 1 and manifest["experiment_id"] == "P2X-NOS3-RG-001" and
          manifest["phase"] == "P2X_PHASE_A_PROSPECTIVE_V2E_OFFLINE_BUILD_ONLY",
          "manifest_population_or_phase")
    check(manifest["classification"] ==
          "V2E_DUAL_OFFLINE_BUILD_BYTE_IDENTITY_PASS__RUNTIME_UNTESTED",
          "raw_nine_identity_not_accepted")
    check(manifest["required_artifact_count"] == 9 and manifest["repeat_match_all"] is True,
          "nine_raw_artifact_identity_not_proven")
    check(manifest["nos3_revision"] == PIN and manifest["fortytwo_revision"] == PIN_FT and
          manifest["fortytwo_p2x_sha256"] == HASH_FT, "source_fortytwo_authority")
    check(manifest["image"] == IMAGE and manifest["platform"] == "linux/amd64" and
          manifest["network"] == "none" and manifest["container_workdir"] == "/work/nos3" and
          tuple(manifest["build_recipe"]) == RECIPE, "image_platform_or_original_recipe")
    check(manifest["synthetic_reproducibility_labels_not_actual_build_timestamps"] is True and
          manifest["synthetic_build_date"] == "202610030000" and
          manifest["synthetic_build_host"] == "p2x-v2e-builder" and
          manifest["synthetic_build_user"] == "p2x-builder", "unregistered_synthetic_metadata")
    for key in ("old_failed_v2_evidence_overwritten", "historical_july_build_lock_replaced",
                "environment_final_acceptance"):
        check(manifest[key] is False, "forbidden_claim:" + key)
    check(manifest["no_runtime_performed"] is True and
          manifest["no_scientific_observations"] is True, "runtime_or_science_claim")

    primary, repeat = (e / "primary/source").resolve(), (e / "repeat/source").resolve()
    check(primary != repeat and primary != CANONICAL.resolve() and
          repeat != CANONICAL.resolve(), "canonical_or_duplicate_source_alias")
    check(Path(manifest["primary_source_root"]).resolve() == primary and
          Path(manifest["repeat_source_root"]).resolve() == repeat,
          "manifest_source_root_alias")
    for src in (primary, repeat):
        check(src.parent.parent == e, "source_not_inside_new_evidence_root")
        source_check(src)
    check(git(ROOT, "status", "--porcelain") == "" and
          git(CANONICAL, "rev-parse", "HEAD") == PIN and
          git(CANONICAL, "status", "--porcelain") == "",
          "canonical_or_research_tracked_worktree_changed")
    check(git(FT, "rev-parse", "HEAD") == PIN_FT and
          git(FT, "status", "--porcelain") == "" and
          hash_file(FT / "42") == HASH_FT, "fortytwo_october_candidate_drift")

    old_manifest_path = OLD / "p2x-v2-build-manifest.json"
    old = json.loads(old_manifest_path.read_text(encoding="utf-8"))
    check(old["classification"] == "BUILD_BYTE_REPRODUCTION_HOLD" and
          old["repeat_match_all"] is False and len(old["artifacts"]) == 9 and
          sum(row["repeat_match"] is True for row in old["artifacts"]) == 8,
          "original_eight_of_nine_hold_not_preserved")
    check(hash_file(old_manifest_path) == manifest["original_v2_hold_manifest_sha256"],
          "old_manifest_bytes_drift")
    check(hash_file(CANONICAL / "fsw/build/exe/cpu1/core-cpu1") == OLD_PRIMARY and
          hash_file(OLD / "repeat/source/fsw/build/exe/cpu1/core-cpu1") == OLD_REPEAT,
          "original_failed_core_bytes_changed")
    locks = {name: hash_file(ROOT / "artifacts" / name) for name in LOCKS}
    check(manifest["historical_locks_sha256_before"] == locks and
          manifest["historical_locks_sha256_after"] == locks,
          "original_july_lock_snapshot_drift")
    check(hash_file(LAUNCHER) == manifest["launcher_sha256"], "launcher_provenance_drift")

    maps = manifest["seed_maps"]
    check(set(maps) == {"primary", "repeat"}, "seed_map_labels")
    for label in ("primary", "repeat"):
        entries = maps[label]
        check(len(entries) >= 5, "missing_launcher_seed_entries:" + label)
        units: set[tuple[str, str]] = set()
        seeds: set[str] = set()
        for item in entries:
            src, obj, seed = item["source"], item["object"], item["seed"]
            check(src.endswith(".c") and obj.endswith(".o") and
                  ".." not in Path(src).parts and ".." not in Path(obj).parts and
                  not src.startswith("/") and not obj.startswith("/"),
                  "noncanonical_seed_identity:" + label)
            key = (src, obj)
            check(key not in units and seed not in seeds and seed == seed_value(src, obj),
                  "seed_identity_mismatch_or_collision:" + label)
            units.add(key)
            seeds.add(seed)
        for name in ("nos_link.c", "libcan.c", "libi2c.c", "libspi.c", "libuart.c"):
            check(any(src.endswith("/" + name) for src, _ in units),
                  "missing_known_coverage_unit:" + label + ":" + name)
        log = (e / (label + "-build.log")).read_text(encoding="utf-8", errors="replace")
        check("container_workdir=/work/nos3" in log and
              "[100%] Built target standalone" in log and
              "CFE_SYNTHETIC_BUILDDATE=202610030000" in log and
              "HOSTNAME=p2x-v2e-builder USER=p2x-builder" in log,
              "compile_log_or_synthetic_environment_witness_missing:" + label)
        for item in entries:
            needle = ("P2X_V2E_SEED_SOURCE=" + item["source"] +
                      " OBJECT=" + item["object"] + " SEED=" + item["seed"])
            check(needle in log.splitlines(), "seed_witness_missing:" + label)
    check(maps["primary"] == maps["repeat"], "independent_seed_maps_not_reproduced")

    rows = manifest["artifacts"]
    check([entry["path"] for entry in rows] == list(NINE), "exact_ordered_nine_paths")
    for row in rows:
        rel = row["path"]
        a, b = primary / rel, repeat / rel
        check(a.resolve().is_relative_to(primary) and b.resolve().is_relative_to(repeat),
              "artifact_symlink_outside_new_population:" + rel)
        ha, hb = hash_file(a), hash_file(b)
        check(ha == hb == row["primary_sha256"] == row["repeat_sha256"] and
              row["repeat_match"] is True and
              a.stat().st_size == row["primary_size_bytes"] and
              b.stat().st_size == row["repeat_size_bytes"],
              "raw_sha_or_byte_size_difference:" + rel)
    for src in (primary, repeat):
        p = src / "fsw/build/amd64-nos3/default_cpu1/cpu1/cfe_build_env_table.c"
        generated = p.read_text(encoding="utf-8")
        for exact in ('{ "BUILDDATE", "202610030000" }',
                      '{ "BUILDHOST", "p2x-v2e-builder" }',
                      '{ "BUILDUSER", "p2x-builder" }'):
            check(exact in generated, "actual_cfe_metadata_drift:" + exact)
    print("P2X_V2E_INDEPENDENT_NINE_RAW_SHA256_READBACK=PASS")
    print("P2X_V2E_TWO_NEW_CANDIDATES=9_OF_9_BYTE_IDENTICAL")
    print("P2X_V2E_OLD_EIGHT_OF_NINE_HOLD_AND_JULY_LOCKS=PRESERVED")
    print("P2X_V2E_RUNTIME=NOT_TESTED")
    print("P2X_V2E_ENVIRONMENT_FINAL_ACCEPTANCE=NO")


if __name__ == "__main__":
    main()
