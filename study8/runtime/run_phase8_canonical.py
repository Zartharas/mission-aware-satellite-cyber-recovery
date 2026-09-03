from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PRIMARY_PATH = ROOT / "study8/src/contact_recovery_model.py"
AUDITOR_PATH = ROOT / "study8/audit/independent_reference.py"
AUTH_PATH = ROOT / "study8/CAMPAIGN_AUTHORIZATION.json"
RESULTS = ROOT / "study8/results/S8-PQC-ICR-001"

FIELDS = [
    "profile", "policy", "regime", "disruption", "phase_offset", "deadline",
    "trusted_recovery_success", "recovery_completion_slot", "contacts_consumed",
    "cryptographic_bytes_transferred", "transition_attempts", "legacy_exposure_slots",
    "control_unavailable_slots", "dual_epoch_overlap_slots", "rollback_invoked",
    "stale_epoch_acceptance", "terminal_state", "proof_accepted_slot", "commit_slot",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def main() -> int:
    if "--execute-canonical" not in sys.argv:
        raise SystemExit("explicit --execute-canonical flag required")

    auth_before_bytes = AUTH_PATH.read_bytes()
    auth_before_sha = hashlib.sha256(auth_before_bytes).hexdigest()
    auth = json.loads(auth_before_bytes.decode("utf-8"))
    if auth.get("consumed") is not False or auth.get("canonical_execution_authorized") is not True:
        raise SystemExit("canonical authorization is not available for consumption")

    run_id = os.environ.get("GITHUB_RUN_ID", "LOCAL_NOT_CANONICAL")
    run_attempt = os.environ.get("GITHUB_RUN_ATTEMPT", "0")
    trigger_head = os.environ.get("GITHUB_SHA", git("rev-parse", "HEAD"))
    parent_main = git("rev-parse", "HEAD^")
    consumed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    auth["consumed"] = True
    auth["consumed_at_utc"] = consumed_at
    auth["consumed_by_github_run_id"] = int(run_id) if run_id.isdigit() else run_id
    auth["consumed_by_run_attempt"] = int(run_attempt) if run_attempt.isdigit() else run_attempt
    auth["consumed_trigger_head"] = trigger_head
    auth["status"] = "CONSUMED_CANONICAL_EXECUTION_IN_PROGRESS"
    AUTH_PATH.write_text(json.dumps(auth, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    RESULTS.mkdir(parents=True, exist_ok=False)
    primary_csv = RESULTS / "canonical_observations.csv"
    independent_csv = RESULTS / "independent_reproduction.csv"
    mismatch_csv = RESULTS / "audit_mismatches.csv"
    summary_path = RESULTS / "independent_audit_summary.json"
    provenance_path = RESULTS / "provenance.json"
    failure_path = RESULTS / "EXECUTION_FAILURE.json"

    try:
        primary = load_module("study8_primary_canonical", PRIMARY_PATH)
        auditor = load_module("study8_independent_canonical", AUDITOR_PATH)
        cases = primary.factor_population()
        if len(cases) != 3456 or len(set(cases)) != 3456:
            raise AssertionError(f"unexpected population shape: {len(cases)} / {len(set(cases))}")

        primary_rows: list[dict[str, object]] = []
        independent_rows: list[dict[str, object]] = []
        mismatches: list[dict[str, object]] = []

        for index, case in enumerate(cases, start=1):
            actual = primary.evaluate_case(case)
            factors = {key: actual[key] for key in ("profile", "policy", "regime", "disruption", "phase_offset", "deadline")}
            expected = auditor.independently_recompute_case(factors)
            if set(actual) != set(FIELDS) or set(expected) != set(FIELDS):
                raise AssertionError("unexpected observation schema")

            observation_id = f"S8-{index:04d}"
            prow = {"observation_id": observation_id, **{field: actual[field] for field in FIELDS}}
            irow = {"observation_id": observation_id, **{field: expected[field] for field in FIELDS}}
            primary_rows.append(prow)
            independent_rows.append(irow)

            differing = [field for field in FIELDS if actual[field] != expected[field]]
            if differing:
                mismatches.append({
                    "observation_id": observation_id,
                    "profile": actual["profile"],
                    "policy": actual["policy"],
                    "regime": actual["regime"],
                    "disruption": actual["disruption"],
                    "phase_offset": actual["phase_offset"],
                    "deadline": actual["deadline"],
                    "differing_fields": ";".join(differing),
                    "primary_json": json.dumps(actual, sort_keys=True, separators=(",", ":")),
                    "independent_json": json.dumps(expected, sort_keys=True, separators=(",", ":")),
                })

        output_fields = ["observation_id", *FIELDS]
        write_csv(primary_csv, primary_rows, output_fields)
        write_csv(independent_csv, independent_rows, output_fields)
        mismatch_fields = [
            "observation_id", "profile", "policy", "regime", "disruption",
            "phase_offset", "deadline", "differing_fields", "primary_json", "independent_json",
        ]
        write_csv(mismatch_csv, mismatches, mismatch_fields)

        summary = {
            "schema": 1,
            "experiment_id": "S8-PQC-ICR-001",
            "authorization_id": auth["authorization_id"],
            "canonical_github_run_id": auth["consumed_by_github_run_id"],
            "canonical_run_attempt": auth["consumed_by_run_attempt"],
            "expected_population": 3456,
            "primary_rows": len(primary_rows),
            "independent_rows": len(independent_rows),
            "factor_positions_unique": len(set(cases)),
            "exact_row_matches": len(primary_rows) - len(mismatches),
            "mismatch_count": len(mismatches),
            "all_rows_match": not mismatches,
            "scientific_interpretation_performed": False,
            "statistical_findings_frozen": False,
            "status": "INDEPENDENT_ROW_BY_ROW_AUDIT_PASS" if not mismatches else "INDEPENDENT_ROW_BY_ROW_AUDIT_FAIL",
        }
        summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        provenance = {
            "schema": 1,
            "experiment_id": "S8-PQC-ICR-001",
            "authorization_snapshot_sha256_before_consumption": auth_before_sha,
            "trigger_head": trigger_head,
            "authorized_parent_main_commit": parent_main,
            "github_run_id": auth["consumed_by_github_run_id"],
            "github_run_attempt": auth["consumed_by_run_attempt"],
            "generated_at_utc": consumed_at,
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "primary_implementation_sha256": sha256(PRIMARY_PATH),
            "independent_auditor_sha256": sha256(AUDITOR_PATH),
            "canonical_observations_sha256": sha256(primary_csv),
            "independent_reproduction_sha256": sha256(independent_csv),
            "audit_mismatches_sha256": sha256(mismatch_csv),
            "independent_audit_summary_sha256": sha256(summary_path),
            "scientific_interpretation_performed": False,
        }
        provenance_path.write_text(json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        auth["canonical_execution_completed"] = True
        auth["independent_reproduction_completed"] = True
        auth["rowwise_audit_completed"] = True
        auth["rowwise_audit_mismatch_count"] = len(mismatches)
        auth["status"] = "CONSUMED_CANONICAL_EXECUTION_AUDITED_PASS" if not mismatches else "CONSUMED_CANONICAL_EXECUTION_AUDITED_FAIL"
        AUTH_PATH.write_text(json.dumps(auth, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        sums = []
        for path in (primary_csv, independent_csv, mismatch_csv, summary_path, provenance_path, AUTH_PATH):
            sums.append(f"{sha256(path)}  {path.relative_to(ROOT)}")
        (RESULTS / "SHA256SUMS.txt").write_text("\n".join(sums) + "\n", encoding="utf-8")

        print(f"canonical_population_rows={len(primary_rows)}")
        print(f"independent_reproduction_rows={len(independent_rows)}")
        print(f"rowwise_mismatches={len(mismatches)}")
        print(f"canonical_results_sha256={sha256(primary_csv)}")
        print(f"independent_results_sha256={sha256(independent_csv)}")
        return 0 if not mismatches else 2

    except Exception as exc:
        failure = {
            "schema": 1,
            "experiment_id": "S8-PQC-ICR-001",
            "authorization_id": auth["authorization_id"],
            "github_run_id": auth["consumed_by_github_run_id"],
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "scientific_interpretation_performed": False,
            "status": "CANONICAL_EXECUTION_OR_AUDIT_ERROR_AUTHORIZATION_CONSUMED",
        }
        failure_path.write_text(json.dumps(failure, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        auth["canonical_execution_completed"] = False
        auth["independent_reproduction_completed"] = False
        auth["rowwise_audit_completed"] = False
        auth["status"] = "CONSUMED_CANONICAL_EXECUTION_ERROR"
        AUTH_PATH.write_text(json.dumps(auth, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"canonical_execution_error={type(exc).__name__}:{exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
