from __future__ import annotations

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


def validate_contracts(contracts: FrozenContracts) -> None:
    protocol = contracts.protocol
    population = contracts.population
    semantic = contracts.semantic
    rubric = contracts.rubric
    manifest = contracts.manifest

    if protocol.get("experiment_id") != STUDY_ID:
        raise ContractViolation("protocol study id mismatch")
    for name, record in (
        ("population", population),
        ("semantic", semantic),
        ("rubric", rubric),
        ("manifest", manifest),
    ):
        if record.get("study_id") != STUDY_ID:
            raise ContractViolation(f"{name} study id mismatch")

    if protocol.get("status") != (
        "PRIMARY_POPULATION_AND_SEMANTIC_ADJUDICATION_FROZEN_"
        "IMPLEMENTATION_AUTHORIZED_NO_ANALYSIS"
    ):
        raise ContractViolation("protocol implementation-phase status is not locked")

    authorization = protocol.get("authorization", {})
    if authorization.get("implementation_creation_authorized") is not True:
        raise ContractViolation("implementation creation is not authorized")
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
        rubric=_load_json(root / "study9" / "RECOVERY_STATE_MAPPING_RUBRIC.json"),
        manifest=_load_json(root / "study9" / "DATASET_SCHEMA_MANIFEST.json"),
    )
    validate_contracts(contracts)
    return contracts
