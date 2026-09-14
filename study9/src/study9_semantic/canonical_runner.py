from __future__ import annotations

import os
from pathlib import Path
import shutil
import tempfile
from typing import Mapping

from .canonical_engine import analysis_to_record, analyze_native_state_groups
from .contracts import FROZEN_DATASET_IDS, FrozenContracts, load_frozen_contracts
from .deterministic_io import build_output_sha256_manifest, canonical_json_bytes
from .independent_audit import audit_analyze_native_state_groups, audit_collapse_native_states
from .input_identity import InputIdentitySpec, iter_verified_rows, verify_csv_source
from .mapping import materialize_mapping_matrix, records_for_dataset
from .state_groups import NativeStateGroup, collapse_native_states
from .state_projection import build_projection_plan, project_native_row


class RealExecutionNotAuthorized(RuntimeError):
    """Raised before external source paths are touched when real execution is closed."""


class CanonicalRunError(RuntimeError):
    """Raised when guarded canonical orchestration cannot complete exactly."""


def assert_real_execution_authorized(contracts: FrozenContracts) -> None:
    authorization = contracts.protocol.get("authorization", {})
    required_authorization = (
        "dataset_ingestion_authorized",
        "row_level_analysis_authorized",
        "canonical_execution_authorized",
        "results_directory_authorized",
    )
    closed = [name for name in required_authorization if authorization.get(name) is not True]
    phase = contracts.protocol.get("implementation_phase", {})
    required_phase_true = (
        "real_dataset_rows_may_be_opened",
        "study9_endpoints_may_be_computed",
        "results_directory_may_be_created",
        "canonical_execution_authorized",
    )
    closed.extend(name for name in required_phase_true if phase.get(name) is not True)
    if closed:
        raise RealExecutionNotAuthorized(
            "real Study 9 execution remains closed before source-path access: "
            + ", ".join(sorted(set(closed)))
        )


def _identity_contract(contracts: FrozenContracts, dataset_id: str) -> Mapping[str, object]:
    for row in contracts.execution_design["input_identity_contracts"]:
        if row["dataset_id"] == dataset_id:
            return row
    raise CanonicalRunError(f"missing frozen input identity: {dataset_id}")


def _build_specs(
    contracts: FrozenContracts,
    *,
    cucd_zip: Path,
    aegissat_csv: Path,
    unsw_zip: Path,
) -> dict[str, InputIdentitySpec]:
    paths = {
        "CUCD_ID_V3": ("ZIP_CSV_MEMBER", cucd_zip),
        "AEGISSAT_2025": ("DIRECT_CSV", aegissat_csv),
        "UNSW_IOTSAT_2026": ("ZIP_CSV_MEMBER", unsw_zip),
    }
    specs: dict[str, InputIdentitySpec] = {}
    for dataset_id in FROZEN_DATASET_IDS:
        identity = _identity_contract(contracts, dataset_id)
        kind, path = paths[dataset_id]
        specs[dataset_id] = InputIdentitySpec(
            dataset_id=dataset_id,
            source_kind=kind,
            source_path=path,
            canonical_artifact_path=str(identity["canonical_artifact_path"]),
            canonical_artifact_sha256=str(identity["canonical_artifact_sha256"]),
            expected_rows=int(identity["expected_rows"]),
            expected_columns=int(identity["expected_columns"]),
            outer_container_sha256=(
                None
                if identity.get("outer_container_sha256") is None
                else str(identity["outer_container_sha256"])
            ),
        )
    return specs


def _group_record(groups: tuple[NativeStateGroup, ...]) -> list[dict[str, object]]:
    return [
        {
            "dataset_id": group.dataset_id,
            "known": [{"variable": name, "value": value} for name, value in group.known],
            "unresolved": list(group.unresolved),
            "multiplicity": group.multiplicity,
        }
        for group in groups
    ]


def _mapping_and_coverage(contracts: FrozenContracts) -> tuple[list[dict[str, object]], dict[str, object]]:
    rows = materialize_mapping_matrix(contracts)
    mapping_record = [
        {
            "dataset_id": row.dataset_id,
            "recovery_state_variable": row.recovery_state_variable,
            "mapping_class": row.mapping_class,
            "evidence_visibility_role": row.evidence_visibility_role,
            "native_field_names": list(row.native_field_names),
            "derivation_rule_if_any": row.derivation_rule_if_any,
            "excluded_fields": list(row.excluded_fields),
            "excluded_as_substitutes": list(row.excluded_as_substitutes),
        }
        for row in rows
    ]
    per_dataset: list[dict[str, object]] = []
    unresolved_sets: list[set[str]] = []
    for dataset_id in FROZEN_DATASET_IDS:
        selected = records_for_dataset(dataset_id, rows)
        direct = sum(
            row.mapping_class == "DIRECT" and row.evidence_visibility_role == "OPERATIONAL_NATIVE"
            for row in selected
        )
        direct_or_derivable = sum(
            row.mapping_class in {"DIRECT", "DERIVABLE_BY_PREDECLARED_RULE"}
            and row.evidence_visibility_role == "OPERATIONAL_NATIVE"
            for row in selected
        )
        unresolved = {
            row.recovery_state_variable
            for row in selected
            if row.mapping_class in {"AMBIGUOUS", "ABSENT"}
        }
        unresolved_sets.append(unresolved)
        per_dataset.append(
            {
                "dataset_id": dataset_id,
                "required_variable_count": len(selected),
                "operational_direct_coverage": {
                    "numerator": direct,
                    "denominator": len(selected),
                },
                "operational_direct_or_derivable_coverage": {
                    "numerator": direct_or_derivable,
                    "denominator": len(selected),
                },
                "unresolved_variables": [
                    name
                    for name in contracts.protocol["required_recovery_state_variables"]
                    if name in unresolved
                ],
            }
        )
    common_missing = set.intersection(*unresolved_sets)
    coverage = {
        "per_dataset": per_dataset,
        "cross_dataset_common_missing_state_set": [
            name
            for name in contracts.protocol["required_recovery_state_variables"]
            if name in common_missing
        ],
    }
    return mapping_record, coverage


def _sidecar_record(analysis_records: list[dict[str, object]]) -> dict[str, object]:
    return {
        "datasets": [
            {
                "dataset_id": analysis["dataset_id"],
                "policy_strata": [
                    {
                        "policy": stratum["policy"],
                        "groups": [
                            {
                                "group_index": group["group_index"],
                                "multiplicity": group["multiplicity"],
                                "guaranteed_sidecar_cardinality": group[
                                    "guaranteed_sidecar_cardinality"
                                ],
                                "guaranteed_sidecar_sets": group["guaranteed_sidecar_sets"],
                            }
                            for group in stratum["group_results"]
                        ],
                    }
                    for stratum in analysis["policy_strata"]
                ],
            }
            for analysis in analysis_records
        ]
    }


def _write_artifacts_atomically(output_dir: Path, artifacts: Mapping[str, bytes]) -> None:
    if output_dir.exists():
        raise CanonicalRunError(f"output directory already exists: {output_dir}")
    parent = output_dir.parent
    parent.mkdir(parents=True, exist_ok=True)
    temp_dir = Path(tempfile.mkdtemp(prefix=f".{output_dir.name}.tmp.", dir=parent))
    try:
        for name, data in artifacts.items():
            target = temp_dir / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        os.replace(temp_dir, output_dir)
    except Exception:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise


def run_canonical_sources(
    *,
    cucd_zip: str | Path,
    aegissat_csv: str | Path,
    unsw_zip: str | Path,
    output_dir: str | Path,
) -> dict[str, object]:
    """Execute the future canonical pipeline only after all real-execution gates are open."""
    contracts = load_frozen_contracts()
    assert_real_execution_authorized(contracts)

    # No supplied external path is inspected before the authorization guard above.
    specs = _build_specs(
        contracts,
        cucd_zip=Path(cucd_zip),
        aegissat_csv=Path(aegissat_csv),
        unsw_zip=Path(unsw_zip),
    )

    verified = {dataset_id: verify_csv_source(specs[dataset_id]) for dataset_id in FROZEN_DATASET_IDS}
    groups_by_dataset: dict[str, tuple[NativeStateGroup, ...]] = {}
    audit_summaries: dict[str, object] = {}
    analysis_records: list[dict[str, object]] = []

    for dataset_id in FROZEN_DATASET_IDS:
        spec = specs[dataset_id]
        verification = verified[dataset_id]
        plan = build_projection_plan(dataset_id, contracts)
        canonical_groups = collapse_native_states(
            dataset_id,
            (project_native_row(plan, row) for row in iter_verified_rows(spec, verification)),
            expected_row_count=verification.row_count,
        )
        # Re-verify after the semantic pass to fail closed on source mutation during execution.
        if verify_csv_source(spec) != verification:
            raise CanonicalRunError(f"source identity changed during canonical pass: {dataset_id}")
        groups_by_dataset[dataset_id] = canonical_groups
        analysis = analyze_native_state_groups(dataset_id, canonical_groups)
        analysis_records.append(analysis_to_record(analysis))

        audit_groups = audit_collapse_native_states(
            dataset_id,
            (project_native_row(plan, row) for row in iter_verified_rows(spec, verification)),
            expected_row_count=verification.row_count,
        )
        audit_summary = audit_analyze_native_state_groups(dataset_id, audit_groups)
        canonical_group_signature = _group_record(canonical_groups)
        audit_group_signature = [
            {
                "dataset_id": row["dataset_id"],
                "known": row["known"],
                "unresolved": row["unresolved"],
                "multiplicity": row["multiplicity"],
            }
            for row in audit_summary["groups"]
        ]
        if canonical_group_signature != audit_group_signature:
            raise CanonicalRunError(f"canonical/audit native-state grouping mismatch: {dataset_id}")
        canonical_strata = analysis_to_record(analysis)["policy_strata"]
        if canonical_strata != audit_summary["policy_strata"]:
            raise CanonicalRunError(f"canonical/audit endpoint mismatch: {dataset_id}")
        audit_summaries[dataset_id] = audit_summary

    mapping_record, coverage_record = _mapping_and_coverage(contracts)
    group_record = {
        "datasets": [
            {
                "dataset_id": dataset_id,
                "source_row_count": verified[dataset_id].row_count,
                "groups": _group_record(groups_by_dataset[dataset_id]),
            }
            for dataset_id in FROZEN_DATASET_IDS
        ]
    }
    policy_record = {"datasets": analysis_records}
    sidecar_record = _sidecar_record(analysis_records)
    audit_record = {
        "status": "MATCH",
        "datasets": [audit_summaries[dataset_id] for dataset_id in FROZEN_DATASET_IDS],
    }
    run_manifest = {
        "study_id": contracts.protocol["experiment_id"],
        "dataset_order": list(FROZEN_DATASET_IDS),
        "primary_policy_order": list(contracts.policy_scope["primary_policies"]),
        "inputs": [
            {
                "dataset_id": dataset_id,
                "canonical_artifact_sha256": verified[dataset_id].artifact_sha256,
                "outer_container_sha256": verified[dataset_id].outer_container_sha256,
                "row_count": verified[dataset_id].row_count,
                "column_count": verified[dataset_id].column_count,
            }
            for dataset_id in FROZEN_DATASET_IDS
        ],
    }

    values = {
        "run_manifest.json": run_manifest,
        "mapping_matrix.json": mapping_record,
        "coverage_summary.json": coverage_record,
        "native_state_groups.json": group_record,
        "policy_strata.json": policy_record,
        "guaranteed_sidecar.json": sidecar_record,
        "independent_audit.json": audit_record,
    }
    artifacts = {name: canonical_json_bytes(value) for name, value in values.items()}
    output_manifest = build_output_sha256_manifest(artifacts)
    artifacts["output_sha256_manifest.json"] = canonical_json_bytes(output_manifest)
    _write_artifacts_atomically(Path(output_dir), artifacts)
    return {
        "output_dir": str(output_dir),
        "artifact_count": len(artifacts),
        "audit_status": "MATCH",
    }
