#!/usr/bin/env python3
"""P2X Phase-A v2: finalize two ALREADY completed, separate offline NOS3 builds.

This tool never launches Docker or a simulator, compiles, cleans, or changes historical
study files. It creates only a new manifest and digest table inside the existing
ignored Phase-A build evidence directory. It explicitly handles spaces in legacy
shasum paths (e.g. 'Development Projects').
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = (ROOT / "artifacts" / "runtime").resolve()
LOCK = ROOT / "artifacts" / "nominal-build-lock.txt"
SOURCE = ROOT / "external" / "nos3"
FORTYTWO = ROOT / "external" / "fortytwo"
AUTH = ROOT / "paper2x" / "phase_a" / "ENVIRONMENT_V2_AUTHORIZATION_2026-10-03.json"
PIN_NOS3 = "5a3bdee6be9a2c67fdf994ae6db56d5c60395302"
PIN_42 = "eda252bf31f27850e867e698cfdd963e143ead1f"
HASH_42 = "b4d054bdd8a95dd429201466833fba8403efec4bdef09a9ed7040131dda3006d"
IMAGE = "ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"
FIVE = (
    "cfg/build/launch.sh",
    "fsw/build/exe/cpu1/core-cpu1",
    "sims/build/bin/nos3-single-simulator",
    "sims/build/bin/nos3-sim-cmdbus-bridge",
    "gsw/build/support/standalone",
)
CONFIG = (
    "cfg/build/InOut/Inp_Sim.txt",
    "cfg/build/InOut/Inp_IPC.txt",
    "sims/build/bin/nos_engine_server_config.json",
    "sims/build/bin/nos3-simulator.xml",
)
OLD_LOCKS = (
    "fortytwo-lock.txt", "nominal-build-lock.txt",
    "nominal-runtime-preflight-lock.txt", "nos3-submodule-lock.txt",
)


def hold(reason: str) -> None:
    raise SystemExit("P2X_PHASE_A_V2_FINALIZE_HOLD=" + reason)


def require(ok: bool, reason: str) -> None:
    if not ok:
        hold(reason)


def sha(path: Path) -> str:
    require(path.is_file() and path.stat().st_size > 0, "missing_or_empty:" + str(path))
    h = hashlib.sha256()
    with path.open("rb") as f:
        for buf in iter(lambda: f.read(1024 * 1024), b""):
            h.update(buf)
    return h.hexdigest()


def git(cwd: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(cwd), *args], text=True).strip()


def historical_five(text: str) -> dict[str, str]:
    lines = text.splitlines()
    require(lines.count("artifact_sha256_begin") == 1, "historical_start_marker_missing_or_duplicate")
    require(lines.count("artifact_sha256_end") == 1, "historical_end_marker_missing_or_duplicate")
    start, end = lines.index("artifact_sha256_begin"), lines.index("artifact_sha256_end")
    require(end > start, "historical_marker_order")
    result: dict[str, str] = {}
    for line in lines[start + 1 : end]:
        # Only split once: historical ABSOLUTE paths include 'Development Projects'.
        pieces = line.strip().split(maxsplit=1)
        require(len(pieces) == 2 and re.fullmatch(r"[0-9a-f]{64}", pieces[0]) is not None,
                "malformed_historical_checksum_row")
        reference_path = pieces[1].lstrip(" *")
        for rel in FIVE:
            if reference_path.endswith("/external/nos3/" + rel):
                require(rel not in result, "duplicate_historical_reference:" + rel)
                result[rel] = pieces[0]
    require(set(result) == set(FIVE), "HISTORICAL_FIVE_INVENTORY_INCOMPLETE:" +
            ",".join(sorted(set(FIVE) - set(result))))
    return result


def lock_self_test() -> None:
    original = LOCK.read_text(encoding="utf-8")
    expected = historical_five(original)
    require(len(expected) == 5, "historical_lock_parser_count")
    # Add an extra space-bearing path segment without touching the original lock file.
    synthetic = original.replace("/external/nos3/", "/A Separate Space-Bearing Folder/external/nos3/")
    require(historical_five(synthetic) == expected, "space_bearing_historical_paths")
    print("P2X_V2_HISTORICAL_LOCK_PATH_WITH_SPACES_REGRESSION=PASS")
    print("P2X_V2_JULY_FIVE_REFERENCES=PARSED_DESCRIPTIVELY")


def main() -> None:
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test-lock":
        lock_self_test()
        return
    if len(sys.argv) != 2:
        hold("usage: python3 scripts/finalize_paper2x_phase_a_v2.py ABSOLUTE_EXISTING_EVIDENCE_DIR")
    evidence = Path(sys.argv[1]).expanduser().resolve()
    require(evidence.is_dir() and evidence.parent == RUNTIME and
            evidence.name.startswith("p2xa-nos3-v2-build-"),
            "evidence_outside_registered_ignored_root")
    primary = SOURCE.resolve()
    repeat = (evidence / "repeat" / "source").resolve()
    require(repeat.is_dir() and repeat != primary, "second_source_copy_missing_or_alias")
    manifest = evidence / "p2x-v2-build-manifest.json"
    table = evidence / "artifact-hash-comparison.tsv"
    require(not manifest.exists() and not table.exists(), "existing_finalization_output_do_not_overwrite")
    auth = json.loads(AUTH.read_text(encoding="utf-8"))
    require(auth["decision"] == "AUTHOR_APPROVED_PROSPECTIVE_V2_CANDIDATE_POLICY", "author_policy_not_adopted")
    require(auth["environment_final_acceptance"] is False, "final_environment_not_yet_qualified")
    require(auth["nos3"]["superproject"] == PIN_NOS3 and auth["nos3"]["image"] == IMAGE, "authorization_pin_drift")
    require(auth["fortytwo"]["p2x_candidate_sha256"] == HASH_42, "fortytwo_authorization_drift")
    require(git(ROOT, "status", "--porcelain") == "", "research_tracked_worktree_dirty")
    require(git(primary, "rev-parse", "HEAD") == PIN_NOS3, "primary_source_commit")
    require(git(repeat, "rev-parse", "HEAD") == PIN_NOS3, "repeat_source_commit")
    require(git(primary, "status", "--porcelain") == "", "primary_source_changed")
    require(git(repeat, "status", "--porcelain") == "", "repeat_source_changed")
    require(git(FORTYTWO, "rev-parse", "HEAD") == PIN_42, "fortytwo_source_commit")
    require(git(FORTYTWO, "status", "--porcelain") == "", "fortytwo_source_changed")
    require(sha(FORTYTWO / "42") == HASH_42, "fortytwo_candidate_hash_changed")

    provenance = (evidence / "build-provenance.txt").read_text(encoding="utf-8")
    for token in ("pin_source=" + PIN_NOS3, "pin_image=" + IMAGE,
                  "fortytwo_candidate=" + HASH_42, "network=none"):
        require(token in provenance.splitlines(), "missing_build_provenance:" + token)
    status_file = evidence / "operator-status.txt"
    recovered = status_file.exists()
    if recovered:
        status = status_file.read_text(encoding="utf-8")
        require("terminal_exit_code=" in status, "prior_failed_finalization_not_recorded")
    for label in ("primary", "repeat"):
        log = evidence / (label + "-build.log")
        require(log.is_file() and log.stat().st_size > 0, "missing_compile_log:" + label)
        txt = log.read_text(encoding="utf-8", errors="replace")
        require("container_workdir=/work/nos3" in txt and
                "gcc (Ubuntu 11.4.0-1ubuntu1~22.04.3) 11.4.0" in txt and
                "GNU ld (GNU Binutils for Ubuntu) 2.38" in txt,
                "compiler_identity_or_workdir_missing:" + label)
        require("[100%] Built target standalone" in txt, "offline_compile_incomplete:" + label)
    original_sha_rows = (evidence / "original-locks-sha256.txt").read_text(encoding="utf-8").splitlines()
    require(len(original_sha_rows) == len(OLD_LOCKS), "lock_snapshot_row_count")
    observed_locks: set[str] = set()
    for row in original_sha_rows:
        fields = row.split(maxsplit=1)
        require(len(fields) == 2 and re.fullmatch(r"[0-9a-f]{64}", fields[0]) is not None,
                "invalid_original_lock_digest_row")
        path = Path(fields[1].lstrip(" *")).resolve()
        require(path.parent == (ROOT / "artifacts").resolve() and path.name in OLD_LOCKS,
                "unexpected_original_lock_path")
        require(path.name not in observed_locks, "duplicate_lock_snapshot_row")
        observed_locks.add(path.name)
        require(sha(path) == fields[0], "original_historical_lock_changed:" + path.name)
    require(observed_locks == set(OLD_LOCKS), "original_lock_snapshot_incomplete")
    historic = historical_five(LOCK.read_text(encoding="utf-8"))
    entries = []
    for rel in FIVE + CONFIG:
        a, b = sha(primary / rel), sha(repeat / rel)
        entries.append({
            "path": rel,
            "sha256_primary": a,
            "sha256_repeat": b,
            "repeat_match": a == b,
            "july_reference_sha256": historic.get(rel),
            "july_reference_match": a == historic[rel] if rel in historic else None,
        })
    all_match = all(e["repeat_match"] for e in entries)
    record = {
        "schema": 1,
        "experiment_id": "P2X-NOS3-RG-001",
        "phase": "PHASE_A_ENVIRONMENT_V2_OFFLINE_BUILD_ONLY",
        "classification": ("TWO_INDEPENDENT_OFFLINE_BUILDS_MATCH__RUNTIME_UNTESTED"
                           if all_match else "BUILD_BYTE_REPRODUCTION_HOLD"),
        "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "nos3_revision": PIN_NOS3,
        "fortytwo_revision": PIN_42,
        "fortytwo_p2x_sha256": HASH_42,
        "image": IMAGE,
        "image_platform": "linux/amd64",
        "network": "none",
        "build_recipe": auth["nos3"]["recipe"],
        "primary_source_root": str(primary),
        "repeat_source_root": str(repeat),
        "artifacts": entries,
        "required_artifact_count": len(entries),
        "repeat_match_all": all_match,
        "historical_july_build_lock_replaced": False,
        "no_runtime_performed": True,
        "no_scientific_observations": True,
        "environment_final_acceptance": False,
        "recovered_from_prior_completed_build": recovered,
        "recovery_reason": ("July checksum parser previously split absolute paths with embedded spaces"
                            if recovered else None),
    }
    # Finalizer writes only fresh evidence outputs. Preserve hashes even on a repeat mismatch.
    table_text = "relative_path\tprimary_sha256\trepeat_sha256\trepeat_match\tjuly_reference_sha256\tjuly_reference_match\n"
    for e in entries:
        table_text += "\t".join(str(e[k]) for k in (
            "path", "sha256_primary", "sha256_repeat", "repeat_match",
            "july_reference_sha256", "july_reference_match")) + "\n"
    with table.open("x", encoding="utf-8") as f:
        f.write(table_text)
    with manifest.open("x", encoding="utf-8") as f:
        f.write(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print("P2X_PHASE_A_V2_BUILD_MANIFEST=" + str(manifest))
    print("P2X_PHASE_A_V2_9_ARTIFACT_REPEAT_MATCH=" + ("PASS" if all_match else "HOLD"))
    print("P2X_PHASE_A_V2_HISTORICAL_JULY_COMPARISON=DESCRIPTIVE_ONLY")
    print("P2X_PHASE_A_V2_BUILD_REEXECUTED=NO")
    print("P2X_PHASE_A_V2_RUNTIME_EXECUTED=NO")
    if not all_match:
        hold("independent_build_byte_mismatch_preserve_both_outputs")


if __name__ == "__main__":
    main()
