from __future__ import annotations

import hashlib
import json
from pathlib import Path

from study2_security.cell_matrix import materialize_cell_matrix, matrix_sha256
from study2_security.runtime_authorization import AUTHORIZATION_PATH, current_runtime_bindings
from study2_security.runtime_engine import development_fixture_report
from study2_security.runtime_freeze import (
    ASSURANCE_DOCKERFILE_SHA256,
    EXPECTED_TRIAL_MANIFEST_SHA256,
    PROTOCOL_AMENDMENT_SHA256,
    REQUIREMENTS_SHA256,
    freeze_payload,
    is_campaign_seed,
    is_development_seed,
    runtime_freeze_sha256,
)
from study2_security.trial_manifest import materialize_trial_manifest, trial_manifest_sha256


ROOT = Path(__file__).resolve().parents[2]
AMENDMENT = ROOT / "study2" / "STUDY2_PROTOCOL_AMENDMENT_1.json"


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    frozen = json.loads(
        (ROOT / "study2" / "PHASE5_RUNTIME_FREEZE.json").read_text(encoding="utf-8")
    )
    if frozen != freeze_payload():
        raise SystemExit("Phase-5 runtime-freeze JSON differs from executable freeze")
    if file_sha256(ROOT / "study2" / "Dockerfile") != ASSURANCE_DOCKERFILE_SHA256:
        raise SystemExit("Study-2 Dockerfile content drifted from Phase-5 freeze")
    if file_sha256(ROOT / "study2" / "requirements.txt") != REQUIREMENTS_SHA256:
        raise SystemExit("Study-2 requirements content drifted from Phase-5 freeze")
    if file_sha256(AMENDMENT) != PROTOCOL_AMENDMENT_SHA256:
        raise SystemExit("Study-2 protocol amendment content drifted")
    amendment = json.loads(AMENDMENT.read_text(encoding="utf-8"))
    expected_flags = (
        "cell_matrix_changed",
        "seed_membership_changed",
        "sample_size_changed",
        "primary_outcomes_changed",
        "campaign_data_observed_before_amendment",
        "campaign_seed_consumed_before_amendment",
    )
    if amendment["status"] != "FROZEN_PRE_RUNTIME_NO_CAMPAIGN_DATA_OBSERVED":
        raise SystemExit("protocol amendment is not prospective")
    if any(amendment[key] is not False for key in expected_flags):
        raise SystemExit("protocol amendment changed frozen membership/outcomes or followed data")
    if AUTHORIZATION_PATH.exists():
        raise SystemExit("Phase-5 branch must not contain an active Phase-6 authorization")

    matrix = materialize_cell_matrix()
    if len(matrix["cells"]) != 85 or matrix_sha256(matrix) != frozen["cell_matrix_sha256"]:
        raise SystemExit("frozen cell matrix changed")
    manifest = materialize_trial_manifest()
    if manifest["position_count"] != 3872:
        raise SystemExit("trial-manifest position count changed")
    if (
        trial_manifest_sha256(manifest) != EXPECTED_TRIAL_MANIFEST_SHA256
        or trial_manifest_sha256(manifest) != frozen["trial_manifest_sha256"]
    ):
        raise SystemExit("trial-manifest canonical hash changed")
    campaign_seeds = {row["seed"] for row in manifest["positions"]}
    if len(campaign_seeds) != 224 or not all(is_campaign_seed(seed) for seed in campaign_seeds):
        raise SystemExit("trial manifest contains unexpected campaign seeds")
    if any(is_development_seed(seed) for seed in campaign_seeds):
        raise SystemExit("development and campaign seed namespaces overlap")

    report = development_fixture_report()
    if report["cell_types_exercised"] != 85 or not report["all_valid"]:
        raise SystemExit("development fixtures did not validate all 85 cell types")
    if report["campaign_seed_consumed"] or report["campaign_observations_generated"]:
        raise SystemExit("Phase-5 development validation crossed campaign boundary")

    protocol = json.loads(
        (ROOT / "study2" / "STUDY2_PROTOCOL.json").read_text(encoding="utf-8")
    )
    if (
        protocol["study2_campaign_runtime_authorized"] is not False
        or protocol["runtime_gate"] != "CLOSED"
    ):
        raise SystemExit("Study-2 campaign runtime must remain CLOSED in Phase 5")

    bindings = current_runtime_bindings()
    if bindings["protocol_amendment_sha256"] != PROTOCOL_AMENDMENT_SHA256:
        raise SystemExit("self-derived authorization amendment binding changed")

    print("STUDY2_PHASE5_RUNTIME_FREEZE=PASS")
    print(f"cell_matrix_sha256={matrix_sha256(matrix)}")
    print(f"trial_manifest_sha256={trial_manifest_sha256(manifest)}")
    print(f"runtime_freeze_sha256={runtime_freeze_sha256(frozen)}")
    print(f"protocol_sha256={bindings['protocol_sha256']}")
    print(f"protocol_amendment_sha256={bindings['protocol_amendment_sha256']}")
    print(f"runtime_bundle_sha256={bindings['runtime_bundle_sha256']}")
    print(f"container_recipe_sha256={bindings['container_recipe_sha256']}")
    print("exact_cell_count=85")
    print("target_valid_observations=3872")
    print("development_cell_types_exercised=85")
    print("phase6_authorization_present=false")
    print("campaign_seed_consumed=false")
    print("campaign_observations_generated=false")
    print("study2_campaign_runtime_authorized=false")
    print("runtime_gate=CLOSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
