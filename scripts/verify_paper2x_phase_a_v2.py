#!/usr/bin/env python3
"""Independent local read-back validator for the prospective P2X Phase-A v2 build.
No Docker calls, builds, scientific experiments, or file mutation.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
P2X_ROOT = ROOT / "artifacts" / "runtime"
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


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise SystemExit("P2X_PHASE_A_ENV_V2_VERIFY_HOLD=" + reason)


def digest(p: Path) -> str:
    require(p.is_file() and p.stat().st_size > 0, "artifact_missing:" + str(p))
    h = hashlib.sha256()
    with p.open("rb") as f:
        for buf in iter(lambda: f.read(1024 * 1024), b""):
            h.update(buf)
    return h.hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 scripts/verify_paper2x_phase_a_v2.py PATH_TO_P2X_V2_BUILD_MANIFEST")
    manifest_path = Path(sys.argv[1]).expanduser().resolve()
    require(manifest_path.name == "p2x-v2-build-manifest.json", "wrong_manifest_filename")
    require(manifest_path.parent.parent == P2X_ROOT.resolve(), "manifest_outside_ignored_runtime_root")
    require(manifest_path.parent.name.startswith("p2xa-nos3-v2-build-"), "wrong_evidence_campaign_root")
    require(manifest_path.is_file(), "build_manifest_missing")
    auth = json.loads(AUTH.read_text(encoding="utf-8"))
    require(auth["decision"] == "AUTHOR_APPROVED_PROSPECTIVE_V2_CANDIDATE_POLICY", "author_v2_scope")
    require(auth["environment_final_acceptance"] is False, "scope_improper_final_acceptance")
    require(auth["fortytwo"]["p2x_candidate_sha256"] == HASH_42, "fortytwo_authority")
    require(auth["fortytwo"]["july_status"] == "NOT_BYTE_REPRODUCED__IMMUTABLE_PAPER1_REFERENCE", "historic_reference")
    require(auth["nos3"]["superproject"] == PIN_NOS3 and auth["nos3"]["image"] == IMAGE, "nos3_source_image_authority")

    m = json.loads(manifest_path.read_text(encoding="utf-8"))
    require(m["schema"] == 1 and m["experiment_id"] == "P2X-NOS3-RG-001", "manifest_schema")
    require(m["classification"] == "TWO_INDEPENDENT_OFFLINE_BUILDS_MATCH__RUNTIME_UNTESTED", "no_build_acceptance")
    require(m["phase"] == "PHASE_A_ENVIRONMENT_V2_OFFLINE_BUILD_ONLY", "wrong_phase")
    require(m["nos3_revision"] == PIN_NOS3 and m["fortytwo_revision"] == PIN_42, "build_source_authority")
    require(m["fortytwo_p2x_sha256"] == HASH_42 and m["image"] == IMAGE, "build_binary_image_authority")
    require(m["network"] == "none" and m["image_platform"] == "linux/amd64", "build_isolation")
    require(m["build_recipe"] == auth["nos3"]["recipe"], "build_recipe_change")
    require(m["required_artifact_count"] == 9 and m["repeat_match_all"] is True, "build_repeat")
    for key in ("historical_july_build_lock_replaced", "environment_final_acceptance"):
        require(m[key] is False, "improper_historical_or_final_claim_" + key)
    require(m["no_runtime_performed"] is True and m["no_scientific_observations"] is True, "incorrect_build_only_class")

    a = ROOT / "external" / "nos3"
    b = manifest_path.parent / "repeat" / "source"
    require(Path(m["primary_source_root"]).resolve() == a.resolve(), "primary_root")
    require(Path(m["repeat_source_root"]).resolve() == b.resolve(), "repeat_root")
    require(git("-C", str(a), "rev-parse", "HEAD") == PIN_NOS3, "primary_source_drift")
    require(git("-C", str(b), "rev-parse", "HEAD") == PIN_NOS3, "repeat_source_drift")
    require(git("-C", str(ROOT / "external" / "fortytwo"), "rev-parse", "HEAD") == PIN_42, "fortytwo_source_drift")
    require(digest(ROOT / "external" / "fortytwo" / "42") == HASH_42, "fortytwo_candidate_drift")
    require(git("-C", str(ROOT), "status", "--porcelain") == "", "research_worktree_modified")
    require(git("-C", str(a), "status", "--porcelain") == "", "nos3_source_mutated")
    require(git("-C", str(b), "status", "--porcelain") == "", "independent_source_mutated")

    original_lock = (ROOT / "artifacts" / "nominal-build-lock.txt").read_text(encoding="utf-8")
    lines = original_lock.splitlines()
    beg, end = lines.index("artifact_sha256_begin"), lines.index("artifact_sha256_end")
    july = {}
    for line in lines[beg+1:end]:
        pieces = line.split()
        require(len(pieces) == 2, "malformed_historical_reference_row")
        for rel in FIVE:
            if pieces[1].endswith("/external/nos3/" + rel):
                july[rel] = pieces[0]
    require(set(july) == set(FIVE), "historical_five_artifact_reference")

    entries = m["artifacts"]
    require([e["path"] for e in entries] == list(FIVE + CONFIG), "ordered_exact_nine_artifacts")
    for e in entries:
        rel = e["path"]
        x, y = digest(a / rel), digest(b / rel)
        require(x == y == e["sha256_primary"] == e["sha256_repeat"], "independent_build_drift:" + rel)
        require(e["repeat_match"] is True, "repeat_mismatch_manifest:" + rel)
        if rel in july:
            require(e["july_reference_sha256"] == july[rel], "old_reference_changed:" + rel)
            require(e["july_reference_match"] is (x == july[rel]), "historical_relation_misreported:" + rel)
        else:
            require(e["july_reference_sha256"] is None and e["july_reference_match"] is None, "unexpected_historical_reference")

    before = (manifest_path.parent / "original-locks-sha256.txt").read_text(encoding="utf-8").splitlines()
    require(len(before) == 4, "historical_lock_snapshot_count")
    for row in before:
        fields = row.split(maxsplit=1)
        require(len(fields) == 2, "historical_lock_row")
        file_path = Path(fields[1]).resolve()
        require(file_path.parent == (ROOT / "artifacts").resolve(), "historical_lock_not_under_artifacts")
        require(file_path.name in {
            "fortytwo-lock.txt", "nominal-build-lock.txt", "nominal-runtime-preflight-lock.txt", "nos3-submodule-lock.txt"
        }, "unrecognized_historical_lock")
        require(digest(file_path) == fields[0], "historical_lock_drift:" + file_path.name)

    print("P2X_PHASE_A_ENV_V2_INDEPENDENT_READBACK=PASS")
    print("P2X_PHASE_A_ENV_V2_NINE_ARTIFACTS_TWO_BUILDS=BYTE_IDENTICAL")
    print("P2X_PHASE_A_ENV_V2_FORTYTWO_CANDIDATE=VERIFIED_SEPARATELY_FROM_JULY")
    print("P2X_PHASE_A_ENV_V2_RUNTIME=NOT_VERIFIED")
    print("P2X_PHASE_A_ENV_V2_FINAL_ACCEPTANCE=NO")


if __name__ == "__main__":
    main()
