from __future__ import annotations

import ast
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import sys
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

CLOSED_PROTOCOL_STATUS = (
    "PRIMARY_POPULATION_AND_SEMANTIC_ADJUDICATION_AND_POLICY_SCOPE_AND_"
    "EXECUTION_DESIGN_FROZEN_LOADER_RUNNER_HARDENED_NO_ANALYSIS"
)
OPEN_PROTOCOL_STATUS = (
    "PRIMARY_POPULATION_AND_SEMANTIC_ADJUDICATION_AND_POLICY_SCOPE_AND_"
    "EXECUTION_DESIGN_FROZEN_CANONICAL_EXECUTION_AUTHORIZED"
)
PROTOCOL_STATUS = OPEN_PROTOCOL_STATUS
EXECUTION_DESIGN_STATUS = "CANONICAL_EXECUTION_DESIGN_FROZEN_NO_ROW_ANALYSIS"
PRE_REAL_DATA_AUDIT_STATUS = (
    "PRE_REAL_DATA_ADVERSARIAL_AUDIT_FROZEN_REMEDIATION_REQUIRED_NO_REAL_DATA"
)
STATE_COLLAPSE_RULE_ID = "EIGHT_STATE_SELECTOR_INPUT_EQUIVALENCE_WITH_EXACT_MULTIPLICITY_V1"
GUARANTEED_SIDECAR_DEFINITION_ID = (
    "ALL_REVEALED_ASSIGNMENTS_YIELD_SINGLETON_REACHABLE_ACTION_SET_V1"
)

LOADER_RUNNER_MODULES = (
    "study9/src/study9_semantic/input_identity.py",
    "study9/src/study9_semantic/state_projection.py",
    "study9/src/study9_semantic/state_groups.py",
    "study9/src/study9_semantic/canonical_engine.py",
    "study9/src/study9_semantic/deterministic_io.py",
    "study9/src/study9_semantic/canonical_runner.py",
)

RUN_IDENTITY_GOVERNANCE_PATHS = (
    "study9/STUDY9_PROTOCOL.json",
    "study9/PRIMARY_POPULATION_FREEZE.json",
    "study9/SEMANTIC_ADJUDICATION_FREEZE.json",
    "study9/POLICY_SCOPE_FREEZE.json",
    "study9/CANONICAL_EXECUTION_DESIGN_FREEZE.json",
    "study9/PRE_REAL_DATA_ADVERSARIAL_AUDIT.json",
    "study9/RECOVERY_STATE_MAPPING_RUBRIC.json",
    "study9/DATASET_SCHEMA_MANIFEST.json",
)
RUN_IDENTITY_IMPLEMENTATION_PATHS = (
    "study9/src/study9_semantic/completions.py",
    "study9/src/study9_semantic/contracts.py",
    "study9/src/study9_semantic/mapping.py",
    "study9/src/study9_semantic/selector_adapter.py",
    "study9/src/study9_semantic/sidecar.py",
    "study9/src/study9_semantic/input_identity.py",
    "study9/src/study9_semantic/state_projection.py",
    "study9/src/study9_semantic/state_groups.py",
    "study9/src/study9_semantic/canonical_engine.py",
    "study9/src/study9_semantic/deterministic_io.py",
    "study9/src/study9_semantic/independent_audit.py",
    "study9/src/study9_semantic/canonical_runner.py",
    "study2/src/study2_security/selectors.py",
)
RUN_IDENTITY_BASE_PATHS = RUN_IDENTITY_GOVERNANCE_PATHS + RUN_IDENTITY_IMPLEMENTATION_PATHS

CODE_FREEZE_COMPUTATIONAL_PATHS = (
    "study9/src/study9_semantic/completions.py",
    "study9/src/study9_semantic/mapping.py",
    "study9/src/study9_semantic/selector_adapter.py",
    "study9/src/study9_semantic/sidecar.py",
    "study9/src/study9_semantic/input_identity.py",
    "study9/src/study9_semantic/state_projection.py",
    "study9/src/study9_semantic/state_groups.py",
    "study9/src/study9_semantic/canonical_engine.py",
    "study9/src/study9_semantic/deterministic_io.py",
    "study9/src/study9_semantic/independent_audit.py",
    "study9/src/study9_semantic/canonical_runner.py",
    "study2/src/study2_security/selectors.py",
)
CANONICAL_RUN_TESTED_COMMIT = "039bca319987ceebdba52f080fb0f87b1d4e67ed"
CANONICAL_RUN_CODE_FREEZE_PATH = "study9/CANONICAL_RUN_CODE_FREEZE.json"
UNSW_SEMANTIC_DEVIATION_PATH = (
    "study9/PROTOCOL_DEVIATION_UNSW_POSITION_ANOMALY_DOMAIN_20260915.json"
)
POST_DEVIATION_VALIDATOR_ALIGNMENT_PATH = (
    "study9/POST_DEVIATION_VALIDATOR_ALIGNMENT_20260915.json"
)

CANONICAL_EXECUTION_AUTHORIZATION_FLAGS = (
    "dataset_ingestion_authorized",
    "row_level_analysis_authorized",
    "canonical_execution_authorized",
    "results_directory_authorized",
)
IMPLEMENTATION_EXECUTION_FLAGS = (
    "real_dataset_rows_may_be_opened",
    "study9_endpoints_may_be_computed",
    "results_directory_may_be_created",
    "canonical_execution_authorized",
)
DOWNSTREAM_AUTHORIZATION_FLAGS = (
    "manuscript_creation_authorized",
    "submission_authorized",
)
REAL_EXECUTION_FLAGS = CANONICAL_EXECUTION_AUTHORIZATION_FLAGS + DOWNSTREAM_AUTHORIZATION_FLAGS


class ContractViolation(RuntimeError):
    """Raised when implementation metadata diverges from frozen/prospective governance."""


@dataclass(frozen=True)
class FrozenContracts:
    repo_root: Path
    protocol: dict[str, Any]
    population: dict[str, Any]
    semantic: dict[str, Any]
    policy_scope: dict[str, Any]
    execution_design: dict[str, Any]
    pre_real_data_audit: dict[str, Any]
    rubric: dict[str, Any]
    manifest: dict[str, Any]


def repository_root(start: Path | None = None) -> Path:
    root = Path(start).resolve() if start is not None else Path(__file__).resolve().parents[3]
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
    try:
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
    except OSError as exc:
        raise ContractViolation(f"cannot hash required file {path}: {exc}") from exc
    return digest.hexdigest()


def _require_exact_sequence(name: str, observed: Any, expected: tuple[str, ...]) -> None:
    if tuple(observed or ()) != expected:
        raise ContractViolation(
            f"{name} mismatch: observed={tuple(observed or ())!r} expected={expected!r}"
        )


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


def _study2_policy_enum_items(selector_path: Path) -> tuple[tuple[str, str], ...]:
    try:
        tree = ast.parse(selector_path.read_text(encoding="utf-8"), filename=str(selector_path))
    except (OSError, SyntaxError) as exc:
        raise ContractViolation(f"cannot inspect frozen Study2Policy enum: {exc}") from exc
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "Study2Policy":
            items: list[tuple[str, str]] = []
            for statement in node.body:
                if not isinstance(statement, ast.Assign) or len(statement.targets) != 1:
                    continue
                target = statement.targets[0]
                if (
                    isinstance(target, ast.Name)
                    and isinstance(statement.value, ast.Constant)
                    and isinstance(statement.value.value, str)
                ):
                    items.append((target.id, statement.value.value))
            return tuple(items)
    raise ContractViolation("Study2Policy enum not found in frozen selector")


def _validate_policy_scope(contracts: FrozenContracts) -> None:
    protocol = contracts.protocol
    policy_scope = contracts.policy_scope
    semantic = contracts.semantic
    if policy_scope.get("status") != "POLICY_SCOPE_FROZEN_NO_ROW_ANALYSIS":
        raise ContractViolation("policy-scope freeze status mismatch")
    _require_exact_sequence("policy-scope primary policies", policy_scope.get("primary_policies"), PRIMARY_POLICY_VALUES)
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
    for key in (
        "all_primary_policies_evaluated",
        "evaluated_separately",
        "semantic_coverage_is_policy_independent",
        "action_identifiability_is_policy_stratified",
        "minimal_sidecar_is_policy_stratified",
    ):
        if rule.get(key) is not True:
            raise ContractViolation(f"policy primary-analysis rule must be true: {key}")
    for key in (
        "policy_pooling_permitted",
        "policy_averaging_permitted",
        "policies_treated_as_interchangeable_replicates",
        "policy_superiority_or_preference_claim_permitted",
    ):
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
    if (
        stratification.get("dataset_count") != 3
        or stratification.get("primary_policy_count") != 4
        or stratification.get("dataset_policy_stratum_count") != 12
    ):
        raise ContractViolation("policy-scope stratification count mismatch")
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
    if protocol_scope.get("frozen") is not True or protocol_scope.get("freeze_record") != "study9/POLICY_SCOPE_FREEZE.json":
        raise ContractViolation("protocol policy-scope binding mismatch")
    _require_exact_sequence("protocol primary policies", protocol_scope.get("primary_policies"), PRIMARY_POLICY_VALUES)
    _require_exact_sequence(
        "protocol excluded ablations",
        protocol_scope.get("excluded_mechanistic_ablations"),
        EXCLUDED_ABLATION_VALUES,
    )
    if protocol_scope.get("dataset_policy_stratum_count") != 12:
        raise ContractViolation("protocol policy-scope stratum count mismatch")
    if protocol_scope.get("policy_pooling_permitted") is not False or protocol_scope.get("policy_averaging_permitted") is not False:
        raise ContractViolation("protocol policy pooling/averaging must remain prohibited")
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


def _validate_execution_design(contracts: FrozenContracts) -> None:
    protocol = contracts.protocol
    execution_design = contracts.execution_design
    semantic = contracts.semantic
    policy_scope = contracts.policy_scope
    manifest = contracts.manifest
    if execution_design.get("status") != EXECUTION_DESIGN_STATUS:
        raise ContractViolation("canonical execution-design freeze status mismatch")

    dependencies = execution_design.get("frozen_dependencies", {})
    expected_dependencies = {
        "primary_population_freeze": "study9/PRIMARY_POPULATION_FREEZE.json",
        "semantic_adjudication_freeze": "study9/SEMANTIC_ADJUDICATION_FREEZE.json",
        "policy_scope_freeze": "study9/POLICY_SCOPE_FREEZE.json",
        "schema_manifest": "study9/DATASET_SCHEMA_MANIFEST.json",
    }
    for key, value in expected_dependencies.items():
        if dependencies.get(key) != value:
            raise ContractViolation(f"execution design dependency binding mismatch: {key}")
    semantic_selector = semantic.get("frozen_downstream_interface", {})
    policy_selector = policy_scope.get("frozen_selector_dependency", {})
    if dependencies.get("selector_path") != semantic_selector.get("selector_path") or dependencies.get("selector_path") != policy_selector.get("path"):
        raise ContractViolation("execution selector path mismatch")
    if dependencies.get("selector_sha256") != semantic_selector.get("selector_sha256") or dependencies.get("selector_sha256") != policy_selector.get("sha256"):
        raise ContractViolation("execution selector SHA-256 mismatch")

    identities = execution_design.get("input_identity_contracts")
    if not isinstance(identities, list):
        raise ContractViolation("execution design input identities must be a list")
    _require_exact_sequence(
        "execution input datasets",
        [row.get("dataset_id") for row in identities if isinstance(row, dict)],
        FROZEN_DATASET_IDS,
    )
    manifest_by_id = {row["dataset_id"]: row for row in manifest["datasets"]}
    for identity in identities:
        dataset_id = identity["dataset_id"]
        manifest_row = manifest_by_id[dataset_id]
        canonical = manifest_row.get("canonical_artifact", {})
        expected = {
            "outer_container_sha256": manifest_row.get("download_package", {}).get("sha256"),
            "canonical_artifact_path": canonical.get("path"),
            "canonical_artifact_sha256": canonical.get("sha256"),
            "expected_rows": canonical.get("rows"),
            "expected_columns": canonical.get("columns"),
        }
        if {key: identity.get(key) for key in expected} != expected:
            raise ContractViolation(f"execution input identity drift: {dataset_id}")

    input_rule = execution_design.get("input_validation_rule", {})
    for key in (
        "verify_outer_container_hash_when_declared_before_member_use",
        "verify_canonical_artifact_sha256_before_semantic_row_processing",
        "verify_expected_row_and_column_counts",
    ):
        if input_rule.get(key) is not True:
            raise ContractViolation(f"execution input validation must be true: {key}")
    if input_rule.get("hash_or_shape_mismatch_behavior") != "FAIL_CLOSED_NO_ENDPOINT_OUTPUT":
        raise ContractViolation("execution input mismatch behavior must fail closed")
    if input_rule.get("dataset_bytes_may_be_committed_to_repository") is not False:
        raise ContractViolation("dataset bytes must not be committed to repository")

    state = execution_design.get("primary_state_construction", {})
    _require_exact_sequence("execution required variable order", state.get("required_variable_order"), REQUIRED_VARIABLES)
    _require_exact_sequence(
        "execution known mapping classes",
        state.get("known_state_mapping_classes"),
        ("DIRECT", "DERIVABLE_BY_PREDECLARED_RULE"),
    )
    _require_exact_sequence(
        "execution unresolved mapping classes",
        state.get("unresolved_state_mapping_classes"),
        ("AMBIGUOUS", "ABSENT"),
    )
    if state.get("permitted_deterministic_derivation_rule_count") != 0:
        raise ContractViolation("execution derivation-rule count must remain zero")
    for key in (
        "missing_or_ambiguous_state_may_be_defaulted",
        "missing_or_ambiguous_state_may_be_imputed",
        "attack_or_scenario_label_may_supply_operational_state",
    ):
        if state.get(key) is not False:
            raise ContractViolation(f"execution state-construction prohibition violated: {key}")
    if state.get("invalid_direct_value_behavior") != "FAIL_CLOSED_NO_ENDPOINT_OUTPUT":
        raise ContractViolation("invalid direct value must fail closed")
    if state.get("unsw_position_anomaly_normalization") != "0 -> false; 1 -> true":
        raise ContractViolation("UNSW Position_Anomaly normalization drift")
    if state.get("unsw_position_anomaly_normalization_status") != (
        "HISTORICAL_SUPERSEDED_NON_OPERATIVE_BY_PROSPECTIVE_SEMANTIC_DEVIATION"
    ):
        raise ContractViolation("UNSW historical normalization status drift")
    if state.get("active_unsw_security_signal_mapping_class") != "AMBIGUOUS":
        raise ContractViolation("UNSW active security_signal mapping must remain AMBIGUOUS")

    collapse = execution_design.get("lossless_state_collapse", {})
    if collapse.get("rule_id") != STATE_COLLAPSE_RULE_ID:
        raise ContractViolation("state-collapse rule id mismatch")
    for key in (
        "enabled_for_canonical_primary_execution",
        "multiplicity_must_be_positive_integer",
        "sum_of_group_multiplicities_must_equal_verified_dataset_row_count",
    ):
        if collapse.get(key) is not True:
            raise ContractViolation(f"lossless state-collapse requirement must be true: {key}")
    for key in (
        "raw_fields_outside_qualifying_direct_or_derivable_state_may_enter_key",
        "attack_or_scenario_labels_may_enter_key",
        "policy_may_enter_native_state_group_key",
        "result_driven_grouping_changes_permitted",
    ):
        if collapse.get(key) is not False:
            raise ContractViolation(f"lossless state-collapse prohibition violated: {key}")

    completion = execution_design.get("admissible_completion_rule", {})
    for key in ("unresolved_variables_are_binary", "enumerate_complete_cartesian_boolean_assignments"):
        if completion.get(key) is not True:
            raise ContractViolation(f"admissible-completion requirement must be true: {key}")
    for key in ("sampling_or_pruning_permitted", "probability_model_permitted", "attack_label_conditioning_permitted"):
        if completion.get(key) is not False:
            raise ContractViolation(f"admissible-completion prohibition violated: {key}")

    sidecar = execution_design.get("guaranteed_minimal_sidecar", {})
    if sidecar.get("definition_id") != GUARANTEED_SIDECAR_DEFINITION_ID:
        raise ContractViolation("guaranteed-sidecar definition id mismatch")
    for key in (
        "actual_unresolved_values_required",
        "actual_unresolved_values_may_be_substituted",
        "assignment_conditioned_synthetic_helper_is_primary_endpoint",
    ):
        if sidecar.get(key) is not False:
            raise ContractViolation(f"guaranteed-sidecar no-imputation boundary violated: {key}")
    for key in (
        "all_minimum_cardinality_ties_must_be_retained",
        "full_revelation_must_be_sufficient_for_deterministic_selector",
        "policy_stratified",
    ):
        if sidecar.get(key) is not True:
            raise ContractViolation(f"guaranteed-sidecar requirement must be true: {key}")

    endpoint = execution_design.get("primary_endpoint_execution_contract", {})
    _require_exact_sequence("execution primary policy order", endpoint.get("primary_policy_order"), PRIMARY_POLICY_VALUES)
    _require_exact_sequence("execution dataset order", endpoint.get("dataset_order"), FROZEN_DATASET_IDS)
    if endpoint.get("dataset_policy_stratum_count") != 12:
        raise ContractViolation("execution dataset-policy stratum count mismatch")
    for key in ("policy_pooling_permitted", "policy_averaging_permitted", "cross_dataset_row_pooling_permitted"):
        if endpoint.get(key) is not False:
            raise ContractViolation(f"execution endpoint pooling prohibition violated: {key}")

    label = execution_design.get("label_boundary", {})
    for key in (
        "offline_ground_truth_may_influence_primary_state",
        "offline_ground_truth_may_influence_state_collapse",
        "offline_ground_truth_may_influence_primary_selector_action",
        "offline_ground_truth_may_influence_primary_sidecar_endpoint",
    ):
        if label.get(key) is not False:
            raise ContractViolation(f"execution label boundary violated: {key}")
    if label.get("descriptive_secondary_use_requires_primary_endpoints_to_be_frozen_first") is not True:
        raise ContractViolation("descriptive label use must remain downstream of primary freeze")

    deterministic = execution_design.get("deterministic_output_contract", {})
    if deterministic.get("randomness_permitted") is not False:
        raise ContractViolation("canonical execution must not use randomness")
    for key in (
        "stable_dataset_order_required",
        "stable_policy_order_required",
        "stable_required_variable_order_required",
        "exact_counts_must_be_stored_as_integers",
        "fractions_must_store_integer_numerator_and_denominator",
        "canonical_json_utf8",
        "canonical_json_sorted_keys",
        "canonical_json_trailing_newline",
        "output_sha256_manifest_required",
    ):
        if deterministic.get(key) is not True:
            raise ContractViolation(f"deterministic output requirement must be true: {key}")
    if deterministic.get("source_dataset_bytes_in_results_permitted") is not False:
        raise ContractViolation("source dataset bytes must not appear in results")

    audit = execution_design.get("independent_audit_contract", {})
    for key in (
        "required",
        "must_use_separately_implemented_completion_and_sidecar_logic",
        "must_not_read_canonical_result_files_as_inputs",
        "must_reconstruct_group_multiplicities_from_hash_verified_source_artifacts",
        "must_reconstruct_primary_endpoint_counts_independently",
    ):
        if audit.get(key) is not True:
            raise ContractViolation(f"independent-audit requirement must be true: {key}")
    if audit.get("canonical_and_audit_mismatch_behavior") != "FAIL_CLOSED_NO_RESULTS_FREEZE":
        raise ContractViolation("canonical/audit mismatch must fail closed")

    for key in (
        "real_dataset_rows_opened",
        "dataset_ingestion_executed",
        "row_level_analysis_executed",
        "canonical_execution_executed",
        "results_directory_created",
        "study9_endpoints_computed",
        "manuscript_creation_executed",
        "submission_executed",
    ):
        if execution_design.get("execution_boundary", {}).get(key) is not False:
            raise ContractViolation(f"execution-design boundary violated: {key}")

    protocol_design = protocol.get("canonical_execution_design_freeze", {})
    if protocol_design.get("frozen") is not True or protocol_design.get("freeze_record") != "study9/CANONICAL_EXECUTION_DESIGN_FREEZE.json":
        raise ContractViolation("protocol canonical execution-design binding mismatch")
    if protocol_design.get("state_collapse_rule_id") != STATE_COLLAPSE_RULE_ID:
        raise ContractViolation("protocol state-collapse rule id mismatch")
    if protocol_design.get("guaranteed_sidecar_definition_id") != GUARANTEED_SIDECAR_DEFINITION_ID:
        raise ContractViolation("protocol guaranteed-sidecar definition id mismatch")
    for key in ("lossless_state_collapse_enabled", "exact_multiplicity_weighting_required", "independent_audit_required"):
        if protocol_design.get(key) is not True:
            raise ContractViolation(f"protocol execution-design requirement must be true: {key}")
    for key in (
        "actual_missing_values_may_be_substituted_for_sidecar",
        "attack_labels_may_influence_primary_execution",
        "real_dataset_rows_opened",
        "study9_endpoints_computed",
    ):
        if protocol_design.get(key) is not False:
            raise ContractViolation(f"protocol execution-design boundary violated: {key}")


def _validate_unsw_semantic_deviation(contracts: FrozenContracts) -> None:
    protocol = contracts.protocol
    semantic = contracts.semantic
    execution_design = contracts.execution_design
    manifest = contracts.manifest

    binding = protocol.get("prospective_semantic_deviation", {})
    expected_binding = {
        "deviation_id": "S9-RTSI-001-DEV-UNSW-POSITION-ANOMALY-DOMAIN-20260915",
        "record": UNSW_SEMANTIC_DEVIATION_PATH,
        "classification": "SOURCE_FIELD_DOMAIN_DEFECT_DIRECT_TO_AMBIGUOUS_NO_REPAIR",
        "dataset_id": "UNSW_IOTSAT_2026",
        "recovery_state_variable": "security_signal",
        "native_field": "Position_Anomaly",
        "prior_mapping_class": "DIRECT",
        "prospective_mapping_class": "AMBIGUOUS",
        "canonical_population_rows": 404798,
        "binary_rows": 404726,
        "nonbinary_rows": 72,
    }
    for key, value in expected_binding.items():
        if binding.get(key) != value:
            raise ContractViolation(f"UNSW semantic-deviation protocol binding mismatch: {key}")
    expected_sha = binding.get("record_sha256")
    if not isinstance(expected_sha, str) or len(expected_sha) != 64:
        raise ContractViolation("UNSW semantic-deviation record SHA-256 missing")
    record_path = contracts.repo_root / UNSW_SEMANTIC_DEVIATION_PATH
    if sha256_file(record_path) != expected_sha:
        raise ContractViolation("UNSW semantic-deviation record SHA-256 mismatch")
    record = _load_json(record_path)
    if record.get("study_id") != STUDY_ID:
        raise ContractViolation("UNSW semantic-deviation study id mismatch")
    if record.get("record_type") != "PROSPECTIVE_PROTOCOL_DEVIATION":
        raise ContractViolation("UNSW semantic-deviation record type mismatch")
    if record.get("deviation_id") != expected_binding["deviation_id"]:
        raise ContractViolation("UNSW semantic-deviation id mismatch")
    if record.get("classification") != expected_binding["classification"]:
        raise ContractViolation("UNSW semantic-deviation classification mismatch")
    if record.get("status") != "PROSPECTIVE_SEMANTIC_RECLASSIFICATION_BEFORE_PERSISTED_CANONICAL_RESULTS":
        raise ContractViolation("UNSW semantic-deviation status mismatch")

    trigger = record.get("trigger", {})
    if trigger.get("canonical_execution_completed") is not False:
        raise ContractViolation("UNSW semantic deviation must precede completed canonical execution")
    if trigger.get("result_artifacts_written") is not False:
        raise ContractViolation("UNSW semantic deviation must precede persisted result artifacts")
    if trigger.get("results_directory_created") is not False:
        raise ContractViolation("UNSW semantic deviation must precede result-directory creation")

    audit = record.get("unsw_iotsat_2026_population_audit", {})
    audit_expected = {
        "canonical_artifact_sha256": "06ef6681c90fbf4c43c0e8993cc2ccc803c21fa32ed30cbf54165b526c851521",
        "row_count": 404798,
        "column_count": 49,
        "field": "Position_Anomaly",
        "binary_zero_count": 404720,
        "binary_one_count": 6,
        "binary_count": 404726,
        "numeric_nonbinary_count": 71,
        "nonnumeric_count": 1,
        "empty_count": 0,
        "nonbinary_total": 72,
        "audit_result": "POSITION_ANOMALY_FULL_DOMAIN_FAIL",
    }
    for key, value in audit_expected.items():
        if audit.get(key) != value:
            raise ContractViolation(f"UNSW semantic-deviation population-audit mismatch: {key}")
    if audit.get("repository_write_performed_by_audit") is not False:
        raise ContractViolation("UNSW domain audit must not have written repository data")
    if audit.get("result_artifacts_created_by_audit") is not False:
        raise ContractViolation("UNSW domain audit must not have created result artifacts")

    disposition = record.get("scientific_disposition", {})
    disposition_expected = {
        "dataset_id": "UNSW_IOTSAT_2026",
        "recovery_state_variable": "security_signal",
        "native_field_retained_as_relevant_evidence": "Position_Anomaly",
        "prior_mapping_class": "DIRECT",
        "prospective_mapping_class": "AMBIGUOUS",
    }
    for key, value in disposition_expected.items():
        if disposition.get(key) != value:
            raise ContractViolation(f"UNSW semantic-deviation disposition mismatch: {key}")
    if disposition.get("apply_ambiguity_to_entire_finite_population") is not True:
        raise ContractViolation("UNSW ambiguity must apply to the entire finite population")
    for key in (
        "selective_salvage_of_apparently_binary_rows",
        "dataset_population_membership_changed",
        "dataset_artifact_changed",
        "dataset_substitution",
        "derivation_rule_added",
    ):
        if disposition.get(key) is not False:
            raise ContractViolation(f"UNSW semantic-deviation disposition boundary violated: {key}")

    prohibited = record.get("prohibited_remediations", {})
    for key in (
        "drop_domain_violating_rows",
        "coerce_nonzero_to_true",
        "derive_from_Speed_ms",
        "realign_from_neighboring_columns",
        "substitute_Attack_Flag_or_other_attack_labels",
        "use_label_conditioned_CCSDS_companion_as_operational_state",
        "use_engineered_companion_as_primary_operational_state",
        "selectively_salvage_only_binary_Position_Anomaly_rows",
        "impute_missing_or_ambiguous_state",
    ):
        if prohibited.get(key) is not False:
            raise ContractViolation(f"UNSW prohibited remediation became permitted: {key}")

    boundary = record.get("execution_boundary_at_correction", {})
    if boundary.get("canonical_execution_completed") is not False:
        raise ContractViolation("UNSW correction boundary cannot record completed canonical execution")
    if boundary.get("persisted_canonical_result_artifacts") != 0:
        raise ContractViolation("UNSW correction boundary must record zero persisted canonical artifacts")
    if boundary.get("results_directory_created") is not False:
        raise ContractViolation("UNSW correction boundary must record no result directory")
    if boundary.get("persisted_study9_endpoints") is not False:
        raise ContractViolation("UNSW correction boundary must record no persisted endpoints")
    if boundary.get("dataset_bytes_ingested_into_repository") is not False:
        raise ContractViolation("UNSW correction boundary must keep dataset bytes outside repository")

    change = record.get("change_boundary", {})
    if change.get("semantic_mapping_changed_prospectively") is not True:
        raise ContractViolation("UNSW deviation must record prospective semantic reclassification")
    if change.get("real_execution_authorization_remains_open_after_validation") is not True:
        raise ContractViolation("UNSW deviation must preserve execution authorization after validation")
    for key in (
        "computational_runtime_changed",
        "canonical_run_code_freeze_changed",
        "study2_selector_changed",
        "primary_population_changed",
        "policy_scope_changed",
        "endpoint_definition_changed",
        "sidecar_definition_changed",
        "manuscript_creation_authorized",
        "submission_authorized",
    ):
        if change.get(key) is not False:
            raise ContractViolation(f"UNSW deviation change boundary violated: {key}")

    semantic_binding = semantic.get("prospective_semantic_deviation", {})
    for key in (
        "deviation_id",
        "record",
        "classification",
        "dataset_id",
        "recovery_state_variable",
        "native_field",
        "prior_mapping_class",
        "prospective_mapping_class",
    ):
        if semantic_binding.get(key) != expected_binding[key]:
            raise ContractViolation(f"UNSW semantic-freeze deviation binding mismatch: {key}")
    if semantic_binding.get("full_population_row_count") != 404798:
        raise ContractViolation("UNSW semantic-freeze population count mismatch")
    if semantic_binding.get("binary_count") != 404726 or semantic_binding.get("nonbinary_count") != 72:
        raise ContractViolation("UNSW semantic-freeze domain counts mismatch")
    for key in (
        "selective_salvage_permitted",
        "repair_or_realign_permitted",
        "derivation_or_substitution_permitted",
        "computational_runtime_changed",
        "canonical_run_code_freeze_changed",
    ):
        if semantic_binding.get(key) is not False:
            raise ContractViolation(f"UNSW semantic-freeze deviation boundary violated: {key}")

    execution_binding = execution_design.get("prospective_semantic_deviation", {})
    for key in (
        "deviation_id",
        "record",
        "classification",
        "dataset_id",
        "recovery_state_variable",
        "native_field",
        "prior_mapping_class",
        "prospective_mapping_class",
    ):
        if execution_binding.get(key) != expected_binding[key]:
            raise ContractViolation(f"UNSW execution-design deviation binding mismatch: {key}")
    if execution_binding.get("historical_normalization_record_retained") is not True:
        raise ContractViolation("UNSW execution design must retain historical normalization metadata")
    if execution_binding.get("historical_normalization_is_operational_after_deviation") is not False:
        raise ContractViolation("UNSW historical normalization must be non-operative")
    if execution_binding.get("apply_ambiguity_to_entire_finite_population") is not True:
        raise ContractViolation("UNSW execution design must apply ambiguity to entire finite population")
    for key in (
        "computational_runtime_changed",
        "canonical_run_code_freeze_changed",
        "persisted_result_artifacts_existed_before_correction",
    ):
        if execution_binding.get(key) is not False:
            raise ContractViolation(f"UNSW execution-design deviation boundary violated: {key}")

    manifest_unsw = next(
        row for row in manifest["datasets"] if row["dataset_id"] == "UNSW_IOTSAT_2026"
    )
    domain = manifest_unsw.get("position_anomaly_domain_audit", {})
    domain_expected = {
        "deviation_record": UNSW_SEMANTIC_DEVIATION_PATH,
        "canonical_population_rows": 404798,
        "binary_zero_count": 404720,
        "binary_one_count": 6,
        "binary_count": 404726,
        "numeric_nonbinary_count": 71,
        "nonnumeric_count": 1,
        "empty_count": 0,
        "nonbinary_count": 72,
        "disposition": "SECURITY_SIGNAL_AMBIGUOUS_FOR_ENTIRE_FINITE_POPULATION",
    }
    for key, value in domain_expected.items():
        if domain.get(key) != value:
            raise ContractViolation(f"UNSW manifest domain-audit mismatch: {key}")
    for key in (
        "row_exclusion_permitted",
        "selective_binary_row_salvage_permitted",
        "coercion_permitted",
        "speed_derivation_permitted",
        "neighboring_column_realign_permitted",
        "attack_label_substitution_permitted",
    ):
        if domain.get(key) is not False:
            raise ContractViolation(f"UNSW manifest remediation boundary violated: {key}")

    semantic_unsw = next(
        row for row in semantic["dataset_contracts"] if row["dataset_id"] == "UNSW_IOTSAT_2026"
    )
    security = next(
        row for row in semantic_unsw["variable_contracts"]
        if row["recovery_state_variable"] == "security_signal"
    )
    if security.get("frozen_mapping_class") != "AMBIGUOUS":
        raise ContractViolation("UNSW security_signal must be prospectively AMBIGUOUS")
    if security.get("evidence_visibility_role") != "OPERATIONAL_NATIVE":
        raise ContractViolation("UNSW security_signal evidence role drift")
    if security.get("native_field_names") != ["Position_Anomaly"]:
        raise ContractViolation("UNSW security_signal native field drift")
    if "value_rule" in security:
        raise ContractViolation("UNSW ambiguous security_signal must not retain an active value_rule")
    if security.get("claim_boundary") != (
        "Position_Anomaly remains relevant evidence about an intended operational coarse "
        "position-spoofing guard, but it supplies no known primary security_signal value "
        "after the prospective domain-defect deviation."
    ):
        raise ContractViolation("UNSW security_signal claim boundary drift")

    historical = protocol.get("semantic_adjudication_freeze", {}).get(
        "direct_operational_native_exception", {}
    )
    if historical.get("dataset_id") != "UNSW_IOTSAT_2026":
        raise ContractViolation("historical UNSW direct exception dataset drift")
    if historical.get("field") != "Position_Anomaly":
        raise ContractViolation("historical UNSW direct exception field drift")
    if historical.get("recovery_state_variable") != "security_signal":
        raise ContractViolation("historical UNSW direct exception variable drift")
    if historical.get("normalization") != "0 -> false; 1 -> true":
        raise ContractViolation("historical UNSW direct normalization metadata drift")
    if historical.get("status") != "HISTORICAL_SUPERSEDED_NON_OPERATIVE":
        raise ContractViolation("historical UNSW direct exception must remain superseded")
    if historical.get("superseded_by") != UNSW_SEMANTIC_DEVIATION_PATH:
        raise ContractViolation("historical UNSW direct exception supersession binding mismatch")


def _validate_post_deviation_validator_alignment(contracts: FrozenContracts) -> None:
    binding = contracts.protocol.get("post_deviation_validator_alignment", {})
    expected_binding = {
        "recorded": True,
        "record_date": "2026-09-15",
        "record": POST_DEVIATION_VALIDATOR_ALIGNMENT_PATH,
        "basis_head": "2f6434e8a84f69b001ad8072f3a03a92afb9a8b8",
        "classification": "GOVERNANCE_VALIDATOR_AND_TEST_ALIGNMENT_NO_FROZEN_RUNTIME_CHANGE",
        "authorized_file_count": 7,
        "frozen_computational_file_count": 12,
        "frozen_computational_files_changed": False,
        "full_study9_suite_required_before_canonical_rerun": True,
        "canonical_execution_rerun_performed": False,
        "results_created": False,
        "manuscript_creation_authorized": False,
        "submission_authorized": False,
    }
    for key, value in expected_binding.items():
        if binding.get(key) != value:
            raise ContractViolation(f"post-deviation validator-alignment binding mismatch: {key}")
    expected_sha = binding.get("record_sha256")
    if not isinstance(expected_sha, str) or len(expected_sha) != 64:
        raise ContractViolation("post-deviation validator-alignment SHA-256 missing")
    path = contracts.repo_root / POST_DEVIATION_VALIDATOR_ALIGNMENT_PATH
    if sha256_file(path) != expected_sha:
        raise ContractViolation("post-deviation validator-alignment SHA-256 mismatch")
    record = _load_json(path)
    if record.get("study_id") != STUDY_ID:
        raise ContractViolation("post-deviation validator-alignment study id mismatch")
    if record.get("record_type") != "POST_DEVIATION_VALIDATOR_ALIGNMENT":
        raise ContractViolation("post-deviation validator-alignment record type mismatch")
    if record.get("status") != "VALIDATOR_ALIGNMENT_RECORDED_FULL_SUITE_REQUIRED_BEFORE_CANONICAL_RERUN":
        raise ContractViolation("post-deviation validator-alignment status mismatch")
    authorization = record.get("authorization", {})
    if authorization.get("explicit_author_authorization") is not True:
        raise ContractViolation("post-deviation validator alignment lacks explicit author authorization")
    if authorization.get("authorization_date") != "2026-09-15":
        raise ContractViolation("post-deviation validator-alignment authorization date mismatch")

    basis = record.get("basis", {})
    if basis.get("base_head") != expected_binding["basis_head"]:
        raise ContractViolation("post-deviation validator-alignment basis head mismatch")
    if basis.get("validation_return_code") != 1:
        raise ContractViolation("post-deviation validator-alignment trigger return code mismatch")
    if basis.get("canonical_result_directory_absent") is not True:
        raise ContractViolation("post-deviation validator alignment must preserve absent result directory")
    if basis.get("repository_spillover") != 0:
        raise ContractViolation("post-deviation validator alignment must record zero repository spillover")
    if basis.get("real_dataset_rows_opened_by_this_validation_attempt") is not False:
        raise ContractViolation("post-deviation validation attempt must not have opened real rows")
    if basis.get("prior_failed_canonical_execution_is_separately_preserved_in") != UNSW_SEMANTIC_DEVIATION_PATH:
        raise ContractViolation("post-deviation alignment prior-execution provenance mismatch")

    findings = record.get("static_root_cause_findings")
    if not isinstance(findings, list):
        raise ContractViolation("post-deviation validator-alignment findings must be a list")
    _require_exact_sequence(
        "post-deviation validator-alignment findings",
        [item.get("finding_id") for item in findings if isinstance(item, dict)],
        ("PDVA-01", "PDVA-02", "PDVA-03", "PDVA-04"),
    )

    _require_exact_sequence(
        "post-deviation validator-alignment authorized scope",
        record.get("authorized_scope_files"),
        (
            "study9/DATASET_SCHEMA_MANIFEST.json",
            "study9/src/study9_semantic/contracts.py",
            "study9/tests/test_contracts.py",
            "study9/tests/test_canonical_runner.py",
            "study9/tests/test_state_groups.py",
            "study9/POST_DEVIATION_VALIDATOR_ALIGNMENT_20260915.json",
            "study9/STUDY9_PROTOCOL.json",
        ),
    )

    change = record.get("change_boundary", {})
    if change.get("frozen_computational_file_count") != len(CODE_FREEZE_COMPUTATIONAL_PATHS):
        raise ContractViolation("post-deviation alignment frozen-computational count mismatch")
    for key in (
        "frozen_computational_files_changed",
        "canonical_run_code_freeze_changed",
        "study2_selector_changed",
        "primary_population_changed",
        "policy_scope_changed",
        "endpoint_definition_changed",
        "dataset_artifacts_changed",
        "semantic_disposition_changed",
    ):
        if change.get(key) is not False:
            raise ContractViolation(f"post-deviation alignment change boundary violated: {key}")
    for key in (
        "manifest_claim_boundary_text_aligned_only",
        "contracts_validator_alignment_only",
        "tests_aligned_to_current_governance_and_semantics",
    ):
        if change.get(key) is not True:
            raise ContractViolation(f"post-deviation alignment remediation not recorded: {key}")

    required = record.get("required_validation_before_canonical_rerun", {})
    for key in (
        "json_parse_all_changed_json",
        "python_syntax_compile_changed_python",
        "load_frozen_contracts_must_pass",
        "full_study9_test_suite_must_pass",
        "canonical_run_frozen_byte_audit_must_pass_12_of_12",
        "working_tree_must_be_clean",
        "canonical_result_directory_must_remain_absent_before_rerun",
    ):
        if required.get(key) is not True:
            raise ContractViolation(f"post-deviation rerun validation requirement missing: {key}")

    boundary = record.get("execution_boundary", {})
    for key in (
        "canonical_execution_rerun_performed",
        "results_created",
        "dataset_bytes_ingested_into_repository",
        "manuscript_creation_authorized",
        "submission_authorized",
    ):
        if boundary.get(key) is not False:
            raise ContractViolation(f"post-deviation validator-alignment boundary violated: {key}")


def _validate_pre_real_data_audit(contracts: FrozenContracts) -> None:
    audit = contracts.pre_real_data_audit
    protocol = contracts.protocol
    if audit.get("status") != PRE_REAL_DATA_AUDIT_STATUS:
        raise ContractViolation("pre-real-data adversarial-audit status mismatch")
    if audit.get("audit_basis_commit") != "f7723ffd7d2e9a6127f260f83d5a0d36cf7ffff1":
        raise ContractViolation("pre-real-data adversarial-audit basis commit mismatch")
    clone = audit.get("actual_clone_validation", {})
    if clone.get("head") != audit.get("audit_basis_commit") or clone.get("test_count") != 57 or clone.get("result") != "PASS":
        raise ContractViolation("pre-real-data actual-clone validation binding mismatch")
    if clone.get("real_dataset_rows_opened") is not False:
        raise ContractViolation("pre-real-data audit must precede real-row access")
    findings = audit.get("findings")
    if not isinstance(findings, list) or [item.get("finding_id") for item in findings] != [
        "PRAA-01", "PRAA-02", "PRAA-03", "PRAA-04", "PRAA-05"
    ]:
        raise ContractViolation("pre-real-data adversarial finding set/order mismatch")
    remediations = audit.get("required_remediations", {})
    for key in (
        "independent_raw_row_projection",
        "independent_policy_independent_mapping_and_coverage",
        "full_synthetic_end_to_end_runner_test",
        "run_manifest_governance_and_implementation_sha256_identity",
        "atomic_future_execution_phase_transition",
    ):
        if remediations.get(key) is not True:
            raise ContractViolation(f"pre-real-data remediation requirement missing: {key}")

    future = audit.get("future_execution_phase_transition", {})
    if future.get("atomic_transition_required") is not True or future.get("partial_transition_permitted") is not False:
        raise ContractViolation("pre-real-data phase transition must be atomic")
    _require_exact_sequence(
        "audit future canonical authorization flags",
        future.get("canonical_execution_authorization_flags"),
        CANONICAL_EXECUTION_AUTHORIZATION_FLAGS,
    )
    _require_exact_sequence(
        "audit future implementation execution flags",
        future.get("implementation_phase_execution_flags"),
        IMPLEMENTATION_EXECUTION_FLAGS,
    )
    if future.get("future_open_requires_canonical_run_code_freeze") is not True:
        raise ContractViolation("future open phase must require canonical-run code freeze")
    if future.get("future_code_freeze_record") != CANONICAL_RUN_CODE_FREEZE_PATH:
        raise ContractViolation("future code-freeze path mismatch")
    if future.get("future_open_requires_synthetic_only_false") is not True:
        raise ContractViolation("future open phase must leave synthetic-only mode")
    if future.get("future_open_requires_loader_runner_synthetic_test_only_false") is not True:
        raise ContractViolation("future open phase must leave loader-runner synthetic-only mode")
    if future.get("manuscript_creation_and_submission_remain_separate_authorizations") is not True:
        raise ContractViolation("manuscript/submission authorization must remain separate")

    for key in (
        "real_dataset_rows_opened",
        "real_dataset_paths_probed",
        "study9_endpoints_computed",
        "results_directory_created",
        "manuscript_creation_executed",
        "submission_executed",
    ):
        if audit.get("execution_boundary", {}).get(key) is not False:
            raise ContractViolation(f"pre-real-data audit execution boundary violated: {key}")

    bound = protocol.get("pre_real_data_adversarial_audit", {})
    if bound.get("completed") is not True:
        raise ContractViolation("protocol does not mark pre-real-data audit complete")
    if bound.get("audit_record") != "study9/PRE_REAL_DATA_ADVERSARIAL_AUDIT.json":
        raise ContractViolation("protocol pre-real-data audit record binding mismatch")
    if bound.get("audit_basis_commit") != audit.get("audit_basis_commit"):
        raise ContractViolation("protocol pre-real-data audit basis mismatch")
    if bound.get("finding_count") != 5 or bound.get("actual_clone_test_count_at_audit") != 57 or bound.get("actual_clone_result_at_audit") != "PASS":
        raise ContractViolation("protocol pre-real-data audit evidence mismatch")
    for key in (
        "independent_raw_row_projection_implemented",
        "independent_policy_independent_mapping_and_coverage_implemented",
        "full_synthetic_end_to_end_runner_test_implemented",
        "run_manifest_reproducibility_identity_implemented",
        "atomic_future_execution_phase_transition_implemented",
    ):
        if bound.get(key) is not True:
            raise ContractViolation(f"protocol pre-real-data remediation not recorded: {key}")
    if bound.get("real_dataset_rows_opened") is not False or bound.get("study9_endpoints_computed") is not False:
        raise ContractViolation("protocol pre-real-data boundary must remain closed")


def _validate_canonical_run_code_freeze(contracts: FrozenContracts) -> None:
    protocol = contracts.protocol
    binding = protocol.get("canonical_run_code_freeze", {})
    if binding.get("frozen") is not True:
        raise ContractViolation("canonical-run code freeze must be active before execution authorization")
    if binding.get("freeze_record") != CANONICAL_RUN_CODE_FREEZE_PATH:
        raise ContractViolation("canonical-run code-freeze record binding mismatch")
    if binding.get("tested_commit") != CANONICAL_RUN_TESTED_COMMIT:
        raise ContractViolation("canonical-run tested commit binding mismatch")
    if binding.get("computational_file_count") != len(CODE_FREEZE_COMPUTATIONAL_PATHS):
        raise ContractViolation("canonical-run computational file-count mismatch")
    if binding.get("actual_clone_full_suite_test_count") != 69:
        raise ContractViolation("canonical-run full-suite test-count binding mismatch")
    if binding.get("actual_clone_canonical_runner_test_count") != 6:
        raise ContractViolation("canonical-run runner-suite test-count binding mismatch")
    if binding.get("actual_clone_result") != "PASS":
        raise ContractViolation("canonical-run actual-clone result must be PASS")
    for key in ("real_dataset_rows_opened", "study9_endpoints_computed", "results_directory_created"):
        if binding.get(key) is not False:
            raise ContractViolation(f"canonical-run code freeze must precede execution: {key}")

    record_path = contracts.repo_root / CANONICAL_RUN_CODE_FREEZE_PATH
    if not record_path.is_file():
        raise ContractViolation("canonical-run code-freeze record does not exist")
    record = _load_json(record_path)
    if record.get("study_id") != STUDY_ID:
        raise ContractViolation("canonical-run code-freeze study id mismatch")
    if record.get("status") != "CANONICAL_RUN_CODE_FROZEN_FOR_REAL_EXECUTION":
        raise ContractViolation("canonical-run code-freeze status mismatch")
    if record.get("tested_branch") != "study9/recovery-state-semantic-interoperability":
        raise ContractViolation("canonical-run tested branch mismatch")
    if record.get("tested_commit") != CANONICAL_RUN_TESTED_COMMIT:
        raise ContractViolation("canonical-run tested commit mismatch")
    if record.get("performance_remediation_record") != "study9/PRE_REAL_DATA_PERFORMANCE_REMEDIATION.json":
        raise ContractViolation("canonical-run performance-remediation binding mismatch")
    if record.get("performance_remediation_classification") != "computational_redundancy_not_scientific_logic_error":
        raise ContractViolation("canonical-run performance-remediation classification mismatch")

    clone = record.get("actual_clone_validation", {})
    full_suite = clone.get("full_suite", {})
    runner_suite = clone.get("canonical_runner_suite", {})
    if (
        full_suite.get("expected_test_count") != 69
        or full_suite.get("observed_test_count") != 69
        or full_suite.get("result") != "PASS"
        or full_suite.get("return_code") != 0
    ):
        raise ContractViolation("canonical-run full-suite validation evidence mismatch")
    if (
        runner_suite.get("expected_test_count") != 6
        or runner_suite.get("observed_test_count") != 6
        or runner_suite.get("result") != "PASS"
        or runner_suite.get("return_code") != 0
    ):
        raise ContractViolation("canonical-run runner-suite validation evidence mismatch")
    if clone.get("working_tree_clean") is not True:
        raise ContractViolation("canonical-run tested working tree was not recorded clean")
    for key in ("real_dataset_rows_opened", "study9_endpoints_computed", "results_directory_created"):
        if clone.get(key) is not False:
            raise ContractViolation(f"canonical-run test evidence crossed execution boundary: {key}")

    identity = record.get("computational_identity", {})
    if identity.get("algorithm") != "sha256":
        raise ContractViolation("canonical-run computational identity algorithm mismatch")
    if identity.get("file_count") != len(CODE_FREEZE_COMPUTATIONAL_PATHS):
        raise ContractViolation("canonical-run computational identity file count mismatch")
    if identity.get("contracts_py_self_freeze_excluded") is not True:
        raise ContractViolation("contracts.py self-freeze exclusion must be explicit")
    files = identity.get("files")
    if not isinstance(files, list):
        raise ContractViolation("canonical-run computational identity files must be a list")
    _require_exact_sequence(
        "canonical-run computational path set",
        [item.get("path") for item in files if isinstance(item, dict)],
        CODE_FREEZE_COMPUTATIONAL_PATHS,
    )
    for item in files:
        relative = item.get("path")
        expected_size = item.get("size_bytes")
        expected_sha = item.get("sha256")
        if type(expected_size) is not int or expected_size <= 0:
            raise ContractViolation(f"canonical-run code-freeze byte size invalid: {relative}")
        if not isinstance(expected_sha, str) or len(expected_sha) != 64 or any(ch not in "0123456789abcdef" for ch in expected_sha):
            raise ContractViolation(f"canonical-run code-freeze SHA-256 invalid: {relative}")
        path = contracts.repo_root / str(relative)
        if not path.is_file():
            raise ContractViolation(f"canonical-run frozen computational file missing: {relative}")
        if path.stat().st_size != expected_size:
            raise ContractViolation(f"canonical-run computational byte-size drift: {relative}")
        if sha256_file(path) != expected_sha:
            raise ContractViolation(f"canonical-run computational SHA-256 drift: {relative}")

    boundary = record.get("execution_boundary", {})
    for key in (
        "real_dataset_rows_opened",
        "dataset_ingestion_executed",
        "row_level_analysis_executed",
        "canonical_execution_executed",
        "study9_endpoints_computed",
        "results_directory_created",
        "manuscript_creation_executed",
        "submission_executed",
    ):
        if boundary.get(key) is not False:
            raise ContractViolation(f"canonical-run code-freeze boundary violated: {key}")

    performance = protocol.get("pre_real_data_performance_remediation", {})
    if performance.get("actual_clone_validation_pending") is not False:
        raise ContractViolation("performance remediation actual-clone validation must be closed")
    if performance.get("actual_clone_validation_head") != CANONICAL_RUN_TESTED_COMMIT:
        raise ContractViolation("performance remediation validation head mismatch")
    if performance.get("actual_clone_full_suite_test_count") != 69 or performance.get("actual_clone_full_suite_result") != "PASS":
        raise ContractViolation("performance remediation full-suite evidence mismatch")
    if performance.get("actual_clone_runner_suite_test_count") != 6 or performance.get("actual_clone_runner_suite_result") != "PASS":
        raise ContractViolation("performance remediation runner-suite evidence mismatch")

    phase = protocol.get("implementation_phase", {})
    if phase.get("canonical_run_code_frozen") is not True:
        raise ContractViolation("implementation phase does not mark canonical-run code frozen")
    if phase.get("canonical_run_code_freeze_record") != CANONICAL_RUN_CODE_FREEZE_PATH:
        raise ContractViolation("implementation phase code-freeze record mismatch")
    if phase.get("canonical_run_code_tested_commit") != CANONICAL_RUN_TESTED_COMMIT:
        raise ContractViolation("implementation phase tested-commit mismatch")


def _validate_execution_phase_alignment(contracts: FrozenContracts) -> None:
    protocol = contracts.protocol
    transition = protocol.get("execution_phase_transition_contract", {})
    if transition.get("atomic_transition_required") is not True or transition.get("partial_transition_permitted") is not False:
        raise ContractViolation("execution phase transition must be atomic")
    if transition.get("closed_protocol_status") != CLOSED_PROTOCOL_STATUS or transition.get("future_open_protocol_status") != OPEN_PROTOCOL_STATUS:
        raise ContractViolation("execution phase status contract drift")
    _require_exact_sequence(
        "protocol execution authorization flags",
        transition.get("canonical_execution_authorization_flags"),
        CANONICAL_EXECUTION_AUTHORIZATION_FLAGS,
    )
    _require_exact_sequence(
        "protocol implementation execution flags",
        transition.get("implementation_phase_execution_flags"),
        IMPLEMENTATION_EXECUTION_FLAGS,
    )
    if transition.get("future_open_requires_canonical_run_code_freeze") is not True:
        raise ContractViolation("future open phase must require canonical-run code freeze")
    if transition.get("future_code_freeze_record") != CANONICAL_RUN_CODE_FREEZE_PATH:
        raise ContractViolation("future execution code-freeze path mismatch")
    if transition.get("future_open_requires_synthetic_only_false") is not True:
        raise ContractViolation("future open phase synthetic-only transition rule missing")
    if transition.get("future_open_requires_loader_runner_synthetic_test_only_false") is not True:
        raise ContractViolation("future open phase loader-runner transition rule missing")
    if transition.get("manuscript_and_submission_remain_separate_authorizations") is not True:
        raise ContractViolation("manuscript/submission must remain separate authorizations")

    authorization = protocol.get("authorization", {})
    phase = protocol.get("implementation_phase", {})
    auth_values = tuple(authorization.get(name) for name in CANONICAL_EXECUTION_AUTHORIZATION_FLAGS)
    phase_values = tuple(phase.get(name) for name in IMPLEMENTATION_EXECUTION_FLAGS)
    closed = all(value is False for value in auth_values + phase_values)
    opened = all(value is True for value in auth_values + phase_values)
    if not (closed or opened):
        raise ContractViolation(
            "partial canonical execution transition detected; all authorization and implementation flags must move atomically"
        )

    for flag in DOWNSTREAM_AUTHORIZATION_FLAGS:
        if authorization.get(flag) is not False:
            raise ContractViolation(f"downstream authorization must remain false during Study 9 execution phase: {flag}")
    if phase.get("dataset_bytes_may_be_ingested_into_repository") is not False:
        raise ContractViolation("dataset bytes must remain outside repository in every execution phase")

    status = protocol.get("status")
    if closed:
        if status != CLOSED_PROTOCOL_STATUS:
            raise ContractViolation("closed execution flags require the closed hardened protocol status")
        if phase.get("synthetic_only") is not True:
            raise ContractViolation("closed phase must remain synthetic-only")
        if phase.get("loader_runner_synthetic_test_only") is not True:
            raise ContractViolation("closed phase loader/runner must remain synthetic-test only")
        return

    if status != OPEN_PROTOCOL_STATUS:
        raise ContractViolation("open execution flags require the canonical-execution-authorized status")
    if phase.get("synthetic_only") is not False:
        raise ContractViolation("open phase requires synthetic_only=false")
    if phase.get("loader_runner_synthetic_test_only") is not False:
        raise ContractViolation("open phase requires loader_runner_synthetic_test_only=false")


def _validate_loader_runner_phase(contracts: FrozenContracts) -> None:
    authorization = contracts.protocol.get("authorization", {})
    if authorization.get("loader_runner_implementation_authorized") is not True:
        raise ContractViolation("loader/runner implementation authorization is not recorded")
    if authorization.get("pre_real_data_adversarial_hardening_authorized") is not True:
        raise ContractViolation("pre-real-data adversarial hardening authorization is not recorded")

    phase = contracts.protocol.get("implementation_phase", {})
    for key in (
        "loader_runner_implemented",
        "loader_runner_standard_library_only",
        "loader_runner_external_paths_required",
        "loader_runner_hard_authorization_guard_before_source_path_access",
        "pre_real_data_adversarial_hardening_implemented",
        "independent_raw_row_projection_implemented",
        "independent_policy_independent_mapping_and_coverage_implemented",
        "full_synthetic_end_to_end_runner_test_implemented",
        "run_manifest_reproducibility_identity_required",
        "atomic_execution_phase_transition_required",
    ):
        if phase.get(key) is not True:
            raise ContractViolation(f"loader/runner hardening requirement must be true: {key}")
    if phase.get("loader_runner_hardcoded_local_paths_permitted") is not False:
        raise ContractViolation("hard-coded local dataset paths must remain prohibited")
    _require_exact_sequence("loader/runner module set", phase.get("loader_runner_modules"), LOADER_RUNNER_MODULES)
    _require_exact_sequence(
        "run-manifest reproducibility identity paths",
        phase.get("run_manifest_reproducibility_identity_paths"),
        RUN_IDENTITY_BASE_PATHS,
    )

    parsed_modules: dict[str, ast.Module] = {}
    for relative in LOADER_RUNNER_MODULES:
        path = contracts.repo_root / relative
        if not path.is_file():
            raise ContractViolation(f"loader/runner module missing: {relative}")
        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(path))
        except (OSError, SyntaxError) as exc:
            raise ContractViolation(f"cannot inspect loader/runner module {relative}: {exc}") from exc
        parsed_modules[relative] = tree
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str) and "/Users/" in node.value:
                raise ContractViolation(f"hard-coded local user path found in {relative}")
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split(".", 1)[0]
                    if root not in sys.stdlib_module_names:
                        raise ContractViolation(f"non-standard-library absolute import in {relative}: {alias.name}")
            elif isinstance(node, ast.ImportFrom) and node.level == 0:
                root = (node.module or "").split(".", 1)[0]
                if root not in sys.stdlib_module_names and root != "__future__":
                    raise ContractViolation(f"non-standard-library absolute import in {relative}: {node.module}")

    independent_path = contracts.repo_root / "study9/src/study9_semantic/independent_audit.py"
    independent_tree = ast.parse(independent_path.read_text(encoding="utf-8"), filename=str(independent_path))
    forbidden_independent_modules = {"state_projection", "mapping", "state_groups", "canonical_engine"}
    for node in ast.walk(independent_tree):
        if isinstance(node, ast.ImportFrom) and node.level > 0:
            leaf = (node.module or "").split(".")[-1]
            if leaf in forbidden_independent_modules:
                raise ContractViolation(f"independent audit imports forbidden canonical module: {leaf}")

    runner = next(
        (
            node
            for node in parsed_modules["study9/src/study9_semantic/canonical_runner.py"].body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "run_canonical_sources"
        ),
        None,
    )
    if runner is None:
        raise ContractViolation("run_canonical_sources not found in guarded canonical runner")
    body = list(runner.body)
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
        body = body[1:]
    if len(body) < 2:
        raise ContractViolation("canonical runner does not contain the required guard sequence")
    first, second = body[:2]
    if not (
        isinstance(first, ast.Assign)
        and len(first.targets) == 1
        and isinstance(first.targets[0], ast.Name)
        and first.targets[0].id == "contracts"
        and isinstance(first.value, ast.Call)
        and isinstance(first.value.func, ast.Name)
        and first.value.func.id == "load_frozen_contracts"
    ):
        raise ContractViolation("canonical runner must load frozen contracts first")
    if not (
        isinstance(second, ast.Expr)
        and isinstance(second.value, ast.Call)
        and isinstance(second.value.func, ast.Name)
        and second.value.func.id == "assert_real_execution_authorized"
        and len(second.value.args) == 1
        and isinstance(second.value.args[0], ast.Name)
        and second.value.args[0].id == "contracts"
    ):
        raise ContractViolation("canonical runner authorization guard must immediately follow frozen-contract loading")


def validate_contracts(contracts: FrozenContracts) -> None:
    protocol = contracts.protocol
    population = contracts.population
    semantic = contracts.semantic
    policy_scope = contracts.policy_scope
    execution_design = contracts.execution_design
    pre_real_data_audit = contracts.pre_real_data_audit
    rubric = contracts.rubric
    manifest = contracts.manifest

    if protocol.get("experiment_id") != STUDY_ID:
        raise ContractViolation("protocol study id mismatch")
    for name, record in (
        ("population", population),
        ("semantic", semantic),
        ("policy_scope", policy_scope),
        ("execution_design", execution_design),
        ("pre_real_data_audit", pre_real_data_audit),
        ("rubric", rubric),
        ("manifest", manifest),
    ):
        if record.get("study_id") != STUDY_ID:
            raise ContractViolation(f"{name} study id mismatch")

    if protocol.get("status") not in {CLOSED_PROTOCOL_STATUS, OPEN_PROTOCOL_STATUS}:
        raise ContractViolation("protocol execution-phase status is not recognized")
    authorization = protocol.get("authorization", {})
    for key in (
        "implementation_creation_authorized",
        "loader_runner_implementation_authorized",
        "pre_real_data_adversarial_hardening_authorized",
        "policy_scope_freeze_authorized",
        "canonical_execution_design_freeze_authorized",
        "canonical_run_code_freeze_authorized",
    ):
        if authorization.get(key) is not True:
            raise ContractViolation(f"required implementation/governance authorization missing: {key}")

    implementation_phase = protocol.get("implementation_phase", {})
    if implementation_phase.get("canonical_policy_scope_frozen") is not True:
        raise ContractViolation("canonical policy scope must be frozen")
    if implementation_phase.get("canonical_execution_design_frozen") is not True:
        raise ContractViolation("canonical execution design must be frozen")
    if implementation_phase.get("canonical_run_code_frozen") is not True:
        raise ContractViolation("canonical run code must be frozen")

    population_freeze = protocol.get("primary_population_freeze", {})
    if population_freeze.get("frozen") is not True:
        raise ContractViolation("primary population is not frozen")
    _require_exact_sequence("primary population", population_freeze.get("members"), FROZEN_DATASET_IDS)

    if semantic.get("status") != "SEMANTIC_ADJUDICATION_FROZEN_NO_ROW_ANALYSIS":
        raise ContractViolation("semantic adjudication freeze status mismatch")
    if semantic.get("permitted_deterministic_derivation_rules") != []:
        raise ContractViolation("semantic derivation registry must remain empty")
    if tuple(semantic.get("target_semantics", {})) != REQUIRED_VARIABLES:
        raise ContractViolation("target semantic variable order/set mismatch")

    population_members = tuple(
        row.get("dataset_id")
        for row in population.get("primary_population_members", [])
        if isinstance(row, dict)
    )
    _require_exact_sequence("population-freeze datasets", population_members, FROZEN_DATASET_IDS)
    _require_exact_sequence("semantic dataset contracts", _dataset_ids_from_semantic(semantic), FROZEN_DATASET_IDS)
    _require_exact_sequence("manifest datasets", _dataset_ids_from_manifest(manifest), FROZEN_DATASET_IDS)

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
        dataset_id = dataset.get("dataset_id")
        for lock in ("artifact_locked", "population_inclusion_locked", "schema_locked"):
            if dataset.get(lock) is not True:
                raise ContractViolation(f"dataset lock is not active: {dataset_id}:{lock}")
        fields = dataset.get("field_schema")
        if not isinstance(fields, list) or len(fields) != len(REQUIRED_VARIABLES):
            raise ContractViolation(f"field_schema must contain 8 rows: {dataset_id}")
        _require_exact_sequence(
            f"{dataset_id} field-schema variables",
            [row.get("recovery_state_variable") for row in fields],
            REQUIRED_VARIABLES,
        )
        if dataset.get("permitted_deterministic_derivation_rules") != []:
            raise ContractViolation(f"dataset derivation registry must remain empty: {dataset_id}")
        semantic_dataset = next(row for row in semantic["dataset_contracts"] if row["dataset_id"] == dataset_id)
        for manifest_row, semantic_row in zip(fields, semantic_dataset["variable_contracts"], strict=True):
            expected = {
                "recovery_state_variable": semantic_row["recovery_state_variable"],
                "mapping_class": semantic_row["frozen_mapping_class"],
                "evidence_visibility_role": semantic_row["evidence_visibility_role"],
                "native_field_names": semantic_row.get("native_field_names", []),
            }
            for optional in ("excluded_fields", "excluded_as_substitutes", "value_rule", "claim_boundary"):
                if optional in semantic_row:
                    expected[optional] = semantic_row[optional]
            if {key: manifest_row.get(key) for key in expected} != expected:
                raise ContractViolation(
                    f"manifest/semantic mapping drift for {dataset_id}:{manifest_row.get('recovery_state_variable')}"
                )

    direct_rows = [
        (dataset["dataset_id"], row["recovery_state_variable"], tuple(row.get("native_field_names", ())))
        for dataset in semantic["dataset_contracts"]
        for row in dataset["variable_contracts"]
        if row["frozen_mapping_class"] == "DIRECT"
    ]
    if direct_rows != []:
        raise ContractViolation(f"unexpected DIRECT mapping set after UNSW deviation: {direct_rows!r}")

    _validate_unsw_semantic_deviation(contracts)
    _validate_post_deviation_validator_alignment(contracts)

    selector = semantic.get("frozen_downstream_interface", {})
    selector_path = selector.get("selector_path")
    expected_sha256 = selector.get("selector_sha256")
    if selector_path != "study2/src/study2_security/selectors.py":
        raise ContractViolation("frozen selector path mismatch")
    if not isinstance(expected_sha256, str) or len(expected_sha256) != 64:
        raise ContractViolation("frozen selector SHA-256 missing")
    actual_sha256 = sha256_file(contracts.repo_root / selector_path)
    if actual_sha256 != expected_sha256:
        raise ContractViolation(f"frozen selector SHA-256 mismatch: {actual_sha256} != {expected_sha256}")

    _validate_policy_scope(contracts)
    _validate_execution_design(contracts)
    _validate_pre_real_data_audit(contracts)
    _validate_canonical_run_code_freeze(contracts)
    _validate_loader_runner_phase(contracts)
    _validate_execution_phase_alignment(contracts)

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
        execution_design=_load_json(root / "study9" / "CANONICAL_EXECUTION_DESIGN_FREEZE.json"),
        pre_real_data_audit=_load_json(root / "study9" / "PRE_REAL_DATA_ADVERSARIAL_AUDIT.json"),
        rubric=_load_json(root / "study9" / "RECOVERY_STATE_MAPPING_RUBRIC.json"),
        manifest=_load_json(root / "study9" / "DATASET_SCHEMA_MANIFEST.json"),
    )
    validate_contracts(contracts)
    return contracts
