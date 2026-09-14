from __future__ import annotations

import ast
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any


STUDY_ID = "S9-RTSI-001"

REQUIRED_VARIABLES = (
    "signature_valid",
    "source_trusted",
    "fresh",
    "epoch_valid",
    "contradictory",
    "minimum_evidence_complete",
    "security_signal",
    "authorization_available",
)

FROZEN_DATASET_IDS = (
    "CUCD_ID_V3",
    "AEGISSAT_2025",
    "UNSW_IOTSAT_2026",
)

PRIMARY_POLICY_VALUES = (
    "S2_B0_FAIL_CLOSED",
    "S2_B1_FAIL_OPERATIONAL",
    "S2_B2_RISK_THRESHOLD",
    "S2_S1_EVIDENCE_AWARE",
)

EXCLUDED_ABLATION_VALUES = (
    "S2_ABL_NO_FRESHNESS",
    "S2_ABL_NO_CONTRADICTION",
    "S2_ABL_NO_EPOCH",
    "S2_ABL_NO_SIGNATURE_TRUST",
)

FULL_POLICY_ENUM_ITEMS = (
    ("FAIL_CLOSED", "S2_B0_FAIL_CLOSED"),
    ("FAIL_OPERATIONAL", "S2_B1_FAIL_OPERATIONAL"),
    ("RISK_THRESHOLD", "S2_B2_RISK_THRESHOLD"),
    ("EVIDENCE_AWARE", "S2_S1_EVIDENCE_AWARE"),
    ("NO_FRESHNESS", "S2_ABL_NO_FRESHNESS"),
    ("NO_CONTRADICTION", "S2_ABL_NO_CONTRADICTION"),
    ("NO_EPOCH", "S2_ABL_NO_EPOCH"),
    ("NO_SIGNATURE_TRUST", "S2_ABL_NO_SIGNATURE_TRUST"),
)

FULL_POLICY_ENUM_VALUES = tuple(value for _, value in FULL_POLICY_ENUM_ITEMS)

REAL_EXECUTION_FLAGS = (
    "dataset_ingestion_authorized",
    "row_level_analysis_authorized",
    "canonical_execution_authorized",
    "results_directory_authorized",
    "manuscript_creation_authorized",
    "submission_authorized",
)


class ContractViolation(RuntimeError):
    """Raised when implementation metadata diverges from the frozen protocol."""


@dataclass(frozen=True)
class FrozenContracts:
    repo_root: Path
    protocol: dict[str, Any]
    population: dict[str, Any]
    semantic: dict[str, Any]
    policy_scope: dict[str, Any]
    rubric: dict[str, Any]
    manifest: dict[str, Any]


def repository_root(start: Path | None = None) -> Path:
    if start is not None:
        root = Path(start).resolve()
    else:
        root = Path(__file__).resolve().parents[3]
    if not (root / "study9" / "STUDY9_PROTOCOL.json").is_file():
        raise ContractViolation(f"repository root not found at {root}")
    return root


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractViolation(f"cannot load frozen contract {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractViolation(f"contract must be a JSON object: {path}")
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _dataset_ids_from_manifest(manifest: dict[str, Any]) -> tuple[str, ...]:
    rows = manifest.get("datasets")
    if not isinstance(rows, list):
        raise ContractViolation("schema manifest datasets must be a list")
    ids: list[str] = []
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("dataset_id"), str):
            raise ContractViolation("every schema-manifest dataset requires dataset_id")
        ids.append(row["dataset_id"])
    return tuple(ids)


def _dataset_ids_from_semantic(semantic: dict[str, Any]) -> tuple[str, ...]:
    rows = semantic.get("dataset_contracts")
    if not isinstance(rows, list):
        raise ContractViolation("semantic freeze dataset_contracts must be a list")
    ids: list[str] = []
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("dataset_id"), str):
            raise ContractViolation("every semantic dataset contract requires dataset_id")
        ids.append(row["dataset_id"])
    return tuple(ids)


def _require_exact_sequence(name: str, observed: Any, expected: tuple[str, ...]) -> None:
    if tuple(observed or ()) != expected:
        raise ContractViolation(
            f"{name} mismatch: observed={tuple(observed or ())!r} expected={expected!r}"
        )


def _study2_policy_enum_items(selector_path: Path) -> tuple[tuple[str, str], ...]:
    try:
        source = selector_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(selector_path))
    except (OSError, SyntaxError) as exc:
        raise ContractViolation(f"cannot inspect frozen Study2Policy enum: {exc}") from exc

    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "Study2Policy":
            items: list[tuple[str, str]] = []
            for statement in node.body:
                if not isinstance(statement, ast.Assign) or len(statement.targets) != 1:
                    continue
                target = statement.targets[0]
                if not isinstance(target, ast.Name):
                    continue
                if isinstance(statement.value, ast.Constant) and isinstance(statement.value.value, str):
                    items.append((target.id, statement.value.value))
            return tuple(items)
    raise ContractViolation("Study2Policy enum not found in frozen selector")


def _validate_policy_scope(contracts: FrozenContracts) -> None:
    protocol = contracts.protocol
    policy_scope = contracts.policy_scope
    semantic = contracts.semantic

    if policy_scope.get("status") != "POLICY_SCOPE_FROZEN_NO_ROW_ANALYSIS":
        raise ContractViolation("policy-scope freeze status mismatch")

    _require_exact_sequence(
        "policy-scope primary policies",
        policy_scope.get("primary_policies"),
        PRIMARY_POLICY_VALUES,
    )
    _require_exact_sequence(
        "policy-scope excluded ablations",
        policy_scope.get("excluded_mechanistic_ablations"),
        EXCLUDED_ABLATION_VALUES,
    )
    _require_exact_sequence(
        "policy-scope complete Study2Policy enum",
        policy_scope.get("study2_policy_enum_order"),
        FULL_POLICY_ENUM_VALUES,
    )

    roles = policy_scope.get("policy_roles", {})
    if tuple(roles) != FULL_POLICY_ENUM_VALUES:
        raise ContractViolation("policy-role ordering/set mismatch")
    for value in PRIMARY_POLICY_VALUES:
        if roles.get(value) != "PRIMARY_SUBSTANTIVE_POLICY":
            raise ContractViolation(f"primary policy role mismatch: {value}")
    for value in EXCLUDED_ABLATION_VALUES:
        if roles.get(value) != "EXCLUDED_MECHANISTIC_ABLATION":
            raise ContractViolation(f"ablation role mismatch: {value}")

    rule = policy_scope.get("primary_analysis_rule", {})
    expected_true = (
        "all_primary_policies_evaluated",
        "evaluated_separately",
        "semantic_coverage_is_policy_independent",
        "action_identifiability_is_policy_stratified",
        "minimal_sidecar_is_policy_stratified",
    )
    for key in expected_true:
        if rule.get(key) is not True:
            raise ContractViolation(f"policy primary-analysis rule must be true: {key}")
    expected_false = (
        "policy_pooling_permitted",
        "policy_averaging_permitted",
        "policies_treated_as_interchangeable_replicates",
        "policy_superiority_or_preference_claim_permitted",
    )
    for key in expected_false:
        if rule.get(key) is not False:
            raise ContractViolation(f"policy primary-analysis rule must be false: {key}")
    if rule.get("canonical_default_policy") is not None:
        raise ContractViolation("canonical default policy must remain null")

    stratification = policy_scope.get("primary_stratification", {})
    _require_exact_sequence(
        "policy-scope stratification datasets",
        stratification.get("dataset_ids"),
        FROZEN_DATASET_IDS,
    )
    if stratification.get("dataset_count") != 3:
        raise ContractViolation("policy-scope dataset count mismatch")
    if stratification.get("primary_policy_count") != 4:
        raise ContractViolation("policy-scope primary-policy count mismatch")
    if stratification.get("dataset_policy_stratum_count") != 12:
        raise ContractViolation("policy-scope dataset-policy stratum count mismatch")
    if stratification.get("cross_stratum_pooling_for_primary_endpoints") is not False:
        raise ContractViolation("cross-stratum pooling must remain prohibited")

    endpoint_scope = policy_scope.get("endpoint_policy_scope", {})
    for endpoint in (
        "per_dataset_recovery_state_mapping_matrix",
        "per_dataset_operational_direct_coverage_count_and_fraction",
        "per_dataset_operational_direct_or_derivable_coverage_count_and_fraction",
        "cross_dataset_common_missing_state_set",
    ):
        if endpoint_scope.get(endpoint) != "POLICY_INDEPENDENT":
            raise ContractViolation(f"semantic endpoint policy scope mismatch: {endpoint}")
    for endpoint in (
        "row_level_admissible_action_set_size",
        "row_level_unique_action_identifiability_fraction",
        "minimal_additional_state_required_for_unique_action_identifiability",
    ):
        if endpoint_scope.get(endpoint) != "DATASET_X_PRIMARY_POLICY_STRATIFIED":
            raise ContractViolation(f"downstream endpoint policy scope mismatch: {endpoint}")

    ablation = policy_scope.get("ablation_boundary", {})
    if ablation.get("included_in_primary_analysis") is not False:
        raise ContractViolation("mechanistic ablations must remain outside primary analysis")
    if ablation.get("future_sensitivity_requires_separate_prospective_authorization") is not True:
        raise ContractViolation("future ablation sensitivity must require prospective authorization")

    execution = policy_scope.get("execution_boundary", {})
    for key in (
        "real_dataset_rows_opened",
        "row_level_analysis_executed",
        "canonical_execution_executed",
        "results_created",
        "study9_endpoints_computed",
    ):
        if execution.get(key) is not False:
            raise ContractViolation(f"policy-scope execution boundary violated: {key}")

    protocol_scope = protocol.get("policy_scope_freeze", {})
    if protocol_scope.get("frozen") is not True:
        raise ContractViolation("protocol policy scope is not frozen")
    if protocol_scope.get("freeze_record") != "study9/POLICY_SCOPE_FREEZE.json":
        raise ContractViolation("protocol policy-scope freeze-record binding mismatch")
    _require_exact_sequence(
        "protocol primary policies",
        protocol_scope.get("primary_policies"),
        PRIMARY_POLICY_VALUES,
    )
    _require_exact_sequence(
        "protocol excluded ablations",
        protocol_scope.get("excluded_mechanistic_ablations"),
        EXCLUDED_ABLATION_VALUES,
    )
    if protocol_scope.get("dataset_policy_stratum_count") != 12:
        raise ContractViolation("protocol policy-scope stratum count mismatch")
    if protocol_scope.get("policy_pooling_permitted") is not False:
        raise ContractViolation("protocol policy pooling must remain prohibited")
    if protocol_scope.get("policy_averaging_permitted") is not False:
        raise ContractViolation("protocol policy averaging must remain prohibited")
    if protocol_scope.get("canonical_default_policy") is not None:
        raise ContractViolation("protocol canonical default policy must remain null")

    policy_selector = policy_scope.get("frozen_selector_dependency", {})
    semantic_selector = semantic.get("frozen_downstream_interface", {})
    if policy_selector.get("path") != semantic_selector.get("selector_path"):
        raise ContractViolation("policy/semantic selector path mismatch")
    if policy_selector.get("sha256") != semantic_selector.get("selector_sha256"):
        raise ContractViolation("policy/semantic selector SHA-256 mismatch")

    selector_path = contracts.repo_root / str(policy_selector.get("path"))
    actual_enum_items = _study2_policy_enum_items(selector_path)
    if actual_enum_items != FULL_POLICY_ENUM_ITEMS:
        raise ContractViolation(
            f"frozen Study2Policy enum drift: observed={actual_enum_items!r} expected={FULL_POLICY_ENUM_ITEMS!r}"
        )


def validate_contracts(contracts: FrozenContracts) -> None:
    protocol = contracts.protocol
    population = contracts.population
    semantic = contracts.semantic
    policy_scope = contracts.policy_scope
    rubric = contracts.rubric
    manifest = contracts.manifest

    if protocol.get("experiment_id") != STUDY_ID:
        raise ContractViolation("protocol study id mismatch")
    for name, record in (
        ("population", population),
        ("semantic", semantic),
        ("policy_scope", policy_scope),
        ("rubric", rubric),
        ("manifest", manifest),
    ):
        if record.get("study_id") != STUDY_ID:
            raise ContractViolation(f"{name} study id mismatch")

    if protocol.get("status") != (
        "PRIMARY_POPULATION_AND_SEMANTIC_ADJUDICATION_AND_POLICY_SCOPE_FROZEN_"
        "IMPLEMENTATION_AUTHORIZED_NO_ANALYSIS"
    ):
        raise ContractViolation("protocol implementation/policy-freeze status is not locked")

    authorization = protocol.get("authorization", {})
    if authorization.get("implementation_creation_authorized") is not True:
        raise ContractViolation("implementation creation is not authorized")
    if authorization.get("policy_scope_freeze_authorized") is not True:
        raise ContractViolation("policy-scope freeze is not authorized")
    for flag in REAL_EXECUTION_FLAGS:
        if authorization.get(flag) is not False:
            raise ContractViolation(f"real-execution authorization must remain false: {flag}")

    implementation_phase = protocol.get("implementation_phase", {})
    if implementation_phase.get("synthetic_only") is not True:
        raise ContractViolation("implementation phase must remain synthetic-only")
    if implementation_phase.get("real_dataset_rows_may_be_opened") is not False:
        raise ContractViolation("real dataset row access is not authorized")
    if implementation_phase.get("study9_endpoints_may_be_computed") is not False:
        raise ContractViolation("Study 9 endpoint computation is not authorized")
    if implementation_phase.get("canonical_policy_scope_frozen") is not True:
        raise ContractViolation("canonical policy scope must be frozen")

    population_freeze = protocol.get("primary_population_freeze", {})
    if population_freeze.get("frozen") is not True:
        raise ContractViolation("primary population is not frozen")
    _require_exact_sequence(
        "primary population",
        population_freeze.get("members"),
        FROZEN_DATASET_IDS,
    )

    if semantic.get("status") != "SEMANTIC_ADJUDICATION_FROZEN_NO_ROW_ANALYSIS":
        raise ContractViolation("semantic adjudication freeze status mismatch")
    if semantic.get("permitted_deterministic_derivation_rules") != []:
        raise ContractViolation("semantic derivation registry must remain empty")
    target_semantics = semantic.get("target_semantics", {})
    if tuple(target_semantics) != REQUIRED_VARIABLES:
        raise ContractViolation("target semantic variable order/set mismatch")

    population_members = tuple(
        row.get("dataset_id")
        for row in population.get("primary_population_members", [])
        if isinstance(row, dict)
    )
    _require_exact_sequence("population-freeze datasets", population_members, FROZEN_DATASET_IDS)

    semantic_ids = _dataset_ids_from_semantic(semantic)
    manifest_ids = _dataset_ids_from_manifest(manifest)
    _require_exact_sequence("semantic dataset contracts", semantic_ids, FROZEN_DATASET_IDS)
    _require_exact_sequence("manifest datasets", manifest_ids, FROZEN_DATASET_IDS)

    if rubric.get("status") != "SEMANTIC_ADJUDICATION_FROZEN_NO_ROW_ANALYSIS":
        raise ContractViolation("mapping rubric is not frozen")
    if rubric.get("semantic_adjudication_freeze_record") != "study9/SEMANTIC_ADJUDICATION_FREEZE.json":
        raise ContractViolation("mapping rubric freeze-record binding mismatch")
    if rubric.get("permitted_deterministic_derivation_rules") != []:
        raise ContractViolation("mapping-rubric derivation registry must remain empty")

    if manifest.get("status") != "PRIMARY_POPULATION_AND_SEMANTIC_ADJUDICATION_FROZEN_NO_ANALYSIS_AUTHORIZED":
        raise ContractViolation("schema manifest freeze status mismatch")
    if manifest.get("semantic_adjudication_freeze_record") != "study9/SEMANTIC_ADJUDICATION_FREEZE.json":
        raise ContractViolation("schema manifest freeze-record binding mismatch")

    for dataset in manifest["datasets"]:
        if dataset.get("artifact_locked") is not True:
            raise ContractViolation(f"artifact not locked: {dataset.get('dataset_id')}")
        if dataset.get("population_inclusion_locked") is not True:
            raise ContractViolation(f"population inclusion not locked: {dataset.get('dataset_id')}")
        if dataset.get("schema_locked") is not True:
            raise ContractViolation(f"semantic schema not locked: {dataset.get('dataset_id')}")
        fields = dataset.get("field_schema")
        if not isinstance(fields, list) or len(fields) != len(REQUIRED_VARIABLES):
            raise ContractViolation(f"field_schema must contain 8 rows: {dataset.get('dataset_id')}")
        _require_exact_sequence(
            f"{dataset.get('dataset_id')} field-schema variables",
            [row.get("recovery_state_variable") for row in fields],
            REQUIRED_VARIABLES,
        )
        if dataset.get("permitted_deterministic_derivation_rules") != []:
            raise ContractViolation(
                f"dataset derivation registry must remain empty: {dataset.get('dataset_id')}"
            )

        semantic_dataset = next(
            row for row in semantic["dataset_contracts"]
            if row["dataset_id"] == dataset["dataset_id"]
        )
        semantic_rows = semantic_dataset["variable_contracts"]
        for manifest_row, semantic_row in zip(fields, semantic_rows, strict=True):
            expected = {
                "recovery_state_variable": semantic_row["recovery_state_variable"],
                "mapping_class": semantic_row["frozen_mapping_class"],
                "evidence_visibility_role": semantic_row["evidence_visibility_role"],
                "native_field_names": semantic_row.get("native_field_names", []),
            }
            for optional in (
                "excluded_fields",
                "excluded_as_substitutes",
                "value_rule",
                "claim_boundary",
            ):
                if optional in semantic_row:
                    expected[optional] = semantic_row[optional]
            observed = {key: manifest_row.get(key) for key in expected}
            if observed != expected:
                raise ContractViolation(
                    f"manifest/semantic mapping drift for "
                    f"{dataset['dataset_id']}:{manifest_row.get('recovery_state_variable')}"
                )

    direct_rows = [
        (dataset["dataset_id"], row["recovery_state_variable"], tuple(row.get("native_field_names", ())))
        for dataset in semantic["dataset_contracts"]
        for row in dataset["variable_contracts"]
        if row["frozen_mapping_class"] == "DIRECT"
    ]
    if direct_rows != [("UNSW_IOTSAT_2026", "security_signal", ("Position_Anomaly",))]:
        raise ContractViolation(f"unexpected DIRECT mapping set: {direct_rows!r}")

    selector = semantic.get("frozen_downstream_interface", {})
    selector_path = selector.get("selector_path")
    expected_sha256 = selector.get("selector_sha256")
    if selector_path != "study2/src/study2_security/selectors.py":
        raise ContractViolation("frozen selector path mismatch")
    if not isinstance(expected_sha256, str) or len(expected_sha256) != 64:
        raise ContractViolation("frozen selector SHA-256 missing")
    actual_sha256 = sha256_file(contracts.repo_root / selector_path)
    if actual_sha256 != expected_sha256:
        raise ContractViolation(
            f"frozen selector SHA-256 mismatch: {actual_sha256} != {expected_sha256}"
        )

    _validate_policy_scope(contracts)

    semantic_execution = semantic.get("execution_boundary", {})
    for key, value in semantic_execution.items():
        if key.endswith("_executed") or key.endswith("_computed") or key == "dataset_bytes_ingested_into_repository":
            if value is not False:
                raise ContractViolation(f"semantic execution boundary violated: {key}")


def load_frozen_contracts(repo_root: Path | None = None) -> FrozenContracts:
    root = repository_root(repo_root)
    contracts = FrozenContracts(
        repo_root=root,
        protocol=_load_json(root / "study9" / "STUDY9_PROTOCOL.json"),
        population=_load_json(root / "study9" / "PRIMARY_POPULATION_FREEZE.json"),
        semantic=_load_json(root / "study9" / "SEMANTIC_ADJUDICATION_FREEZE.json"),
        policy_scope=_load_json(root / "study9" / "POLICY_SCOPE_FREEZE.json"),
        rubric=_load_json(root / "study9" / "RECOVERY_STATE_MAPPING_RUBRIC.json"),
        manifest=_load_json(root / "study9" / "DATASET_SCHEMA_MANIFEST.json"),
    )
    validate_contracts(contracts)
    return contracts
