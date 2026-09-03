from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REQUIRED = (
    "study8/PHASE8_1_IMPLEMENTATION_AUTHORIZATION.json",
    "study8/PHASE8_0_AMENDMENT_1.json",
    "study8/src/contact_recovery_model.py",
    "study8/audit/independent_reference.py",
    "study8/tests/test_phase8_models.py",
    "study8/scripts/check_phase8_1_implementation_freeze.py",
    "study8/docs/PHASE8_1_IMPLEMENTATION_FREEZE.md",
)

FORBIDDEN = (
    "study8/results",
    "study8/runtime",
    "study8/CAMPAIGN_AUTHORIZATION.json",
)


def main() -> None:
    auth = json.loads(
        (ROOT / "study8/PHASE8_1_IMPLEMENTATION_AUTHORIZATION.json").read_text(
            encoding="utf-8"
        )
    )
    assert auth["experiment_id"] == "S8-PQC-ICR-001"
    assert auth["phase"] == "8.1"
    assert auth["implementation_construction_authorized"] is True
    assert auth["canonical_execution_authorized"] is False
    assert auth["campaign_authorization_present"] is False
    assert auth["results_generation_authorized"] is False
    assert auth["pre_runtime_pr_authorized"] is False

    protocol = json.loads(
        (ROOT / "study8/STUDY8_PROTOCOL.json").read_text(encoding="utf-8")
    )
    amendment = json.loads(
        (ROOT / "study8/PHASE8_0_AMENDMENT_1.json").read_text(encoding="utf-8")
    )
    assert protocol["expected_population"]["observations"] == 3456
    assert amendment["population_observations_before"] == 3456
    assert amendment["population_observations_after"] == 3456
    assert amendment["factor_lattice_changed"] is False
    assert protocol["gates"]["runtime_authorized"] is False
    assert protocol["gates"]["canonical_execution_authorized"] is False

    for relative in REQUIRED:
        assert (ROOT / relative).is_file(), relative
    for relative in FORBIDDEN:
        assert not (ROOT / relative).exists(), relative

    primary = ROOT / "study8/src/contact_recovery_model.py"
    independent = ROOT / "study8/audit/independent_reference.py"
    for path in (primary, independent):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        imports = {
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
        }
        if path == independent:
            assert not any(module and module.startswith("study8") for module in imports)

    print("phase8_1_static_freeze_check=PASS")
    print("canonical_runtime_gate=CLOSED")
    print("campaign_authorization=ABSENT")


if __name__ == "__main__":
    main()
