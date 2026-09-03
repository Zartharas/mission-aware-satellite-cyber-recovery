from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

FORBIDDEN = (
    "study8/results",
    "study8/runtime",
    "study8/CAMPAIGN_AUTHORIZATION.json",
)


def _contains_call(node: ast.AST, attribute: str) -> bool:
    for child in ast.walk(node):
        if isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute):
            if child.func.attr == attribute:
                return True
    return False


def main() -> None:
    pre = json.loads(
        (ROOT / "study8/PHASE8_2_PRE_RUNTIME_AUTHORIZATION.json").read_text(
            encoding="utf-8"
        )
    )
    phase81 = json.loads(
        (ROOT / "study8/PHASE8_1_IMPLEMENTATION_AUTHORIZATION.json").read_text(
            encoding="utf-8"
        )
    )
    protocol = json.loads(
        (ROOT / "study8/STUDY8_PROTOCOL.json").read_text(encoding="utf-8")
    )

    assert pre["authorization_id"] == "S8-PRERUNTIME-001"
    assert pre["experiment_id"] == "S8-PQC-ICR-001"
    assert pre["pull_request_number"] == 88
    assert pre["pre_runtime_pr_authorized"] is True
    assert pre["static_validation_authorized"] is True
    assert pre["development_fixture_execution_authorized"] is True
    assert pre["development_fixture_unique_case_count"] == 4
    assert pre["factor_population_shape_enumeration_authorized"] is True
    assert pre["full_population_case_evaluation_authorized"] is False
    assert pre["canonical_execution_authorized"] is False
    assert pre["campaign_authorization_present"] is False
    assert pre["results_generation_authorized"] is False
    assert pre["scientific_interpretation_authorized"] is False
    assert pre["hash_report_authorized"] is True
    assert pre["hash_binding_authorized"] is True
    assert pre["merge_authorized"] is False

    # Preserve the historical Phase-8.1 construction boundary rather than rewriting it.
    assert phase81["pre_runtime_pr_authorized"] is False
    assert phase81["canonical_execution_authorized"] is False
    assert protocol["expected_population"]["observations"] == 3456
    assert protocol["gates"]["runtime_authorized"] is False
    assert protocol["gates"]["canonical_execution_authorized"] is False

    for relative in FORBIDDEN:
        assert not (ROOT / relative).exists(), relative

    test_path = ROOT / "study8/tests/test_phase8_models.py"
    tree = ast.parse(test_path.read_text(encoding="utf-8"), filename=str(test_path))

    # Structural enumeration of factor_population is allowed, but no test may iterate
    # factor_population and evaluate/recompute those cases as a full scientific campaign.
    for node in ast.walk(tree):
        if not isinstance(node, (ast.For, ast.comprehension)):
            continue
        iterator = node.iter
        if not (
            isinstance(iterator, ast.Call)
            and isinstance(iterator.func, ast.Attribute)
            and iterator.func.attr == "factor_population"
        ):
            continue
        scope = node if isinstance(node, ast.For) else tree
        assert not _contains_call(scope, "evaluate_case")
        assert not _contains_call(scope, "independently_recompute_case")

    primary_text = (ROOT / "study8/src/contact_recovery_model.py").read_text(
        encoding="utf-8"
    )
    audit_text = (ROOT / "study8/audit/independent_reference.py").read_text(
        encoding="utf-8"
    )
    assert "direct or canonical execution is not authorized" in primary_text
    assert "artifact audit execution is not authorized" in audit_text

    print("phase8_2_pre_runtime_gate=PASS")
    print("development_fixture_unique_cases_authorized=4")
    print("full_population_case_evaluation=PROHIBITED")
    print("canonical_execution=PROHIBITED")
    print("campaign_authorization=ABSENT")
    print("merge_authorized=false")


if __name__ == "__main__":
    main()
