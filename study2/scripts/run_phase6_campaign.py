from __future__ import annotations

import argparse
import hashlib
import json
import os
from dataclasses import asdict
from pathlib import Path
from typing import Any

from study2_security.attempt_ledger import next_required_trial, validate_attempt_ledger
from study2_security.runtime_authorization import (
    AUTHORIZATION_PATH,
    CampaignAuthorization,
    current_runtime_bindings,
    runtime_bundle_manifest,
)
from study2_security.runtime_engine import run_trial
from study2_security.runtime_freeze import RuntimeMode
from study2_security.trial_manifest import materialize_trial_manifest, trial_manifest_sha256


EXPERIMENT_ID = "S2-AEATR-001"


def _canonical_line(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ) + "\n"


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_authorization() -> CampaignAuthorization:
    if not AUTHORIZATION_PATH.is_file():
        raise ValueError("repository-backed Phase-6 campaign authorization is absent")
    payload = json.loads(AUTHORIZATION_PATH.read_text(encoding="utf-8"))
    auth = CampaignAuthorization(**payload)
    auth.validate()
    return auth


def static_report() -> dict[str, Any]:
    manifest = materialize_trial_manifest()
    return {
        "schema": 1,
        "classification": "PHASE6_CAMPAIGN_OPERATOR_STATIC_READY",
        "experiment_id": EXPERIMENT_ID,
        "trial_manifest_sha256": trial_manifest_sha256(manifest),
        "position_count": manifest["position_count"],
        "runtime_bindings": current_runtime_bindings(),
        "runtime_bundle_manifest": [
            {"path": path, "sha256": sha256}
            for path, sha256 in runtime_bundle_manifest()
        ],
        "phase6_authorization_present": AUTHORIZATION_PATH.is_file(),
        "campaign_seed_consumed": False,
        "campaign_observations_generated": False,
        "automatic_retry_after_invalid_allowed": False,
        "automatic_position_advance_after_valid_allowed": True,
        "invalid_attempt_stops_campaign": True,
        "partial_failure_evidence_retained": True,
    }


def _append_jsonl(path: Path, row: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(_canonical_line(row))
        handle.flush()
        os.fsync(handle.fileno())


def _write_summary_and_hashes(
    *,
    auth: CampaignAuthorization,
    manifest: dict[str, Any],
    attempts: list[dict[str, Any]],
    valid_observations: int,
    observations_path: Path,
    attempts_path: Path,
    bindings_path: Path,
    summary_path: Path,
    hashes_path: Path,
    classification: str,
    failure: dict[str, Any] | None = None,
) -> dict[str, Any]:
    state = validate_attempt_ledger(attempts)
    summary = {
        "schema": 1,
        "classification": classification,
        "experiment_id": EXPERIMENT_ID,
        "authorization_id": auth.authorization_id,
        "trial_manifest_sha256": trial_manifest_sha256(manifest),
        "attempt_count": int(state["attempt_count"]),
        "valid_observations": valid_observations,
        "invalid_attempts": int(state["invalid_attempt_count"]),
        "campaign_complete": bool(state["campaign_complete"]),
        "automatic_retry_after_invalid_allowed": False,
        "automatic_position_advance_after_valid_allowed": True,
        "post_hoc_seed_substitution_allowed": False,
        "campaign_rerun_authorized": False,
        "failure": failure,
    }
    summary_path.write_text(_canonical_line(summary), encoding="utf-8")
    hashes = {
        "schema": 1,
        "experiment_id": EXPERIMENT_ID,
        "files": {
            path.name: _file_sha256(path)
            for path in (observations_path, attempts_path, bindings_path, summary_path)
        },
    }
    hashes_path.write_text(_canonical_line(hashes), encoding="utf-8")
    return {**summary, "evidence_hashes": hashes["files"]}


def execute_campaign(output_dir: Path) -> dict[str, Any]:
    auth = _load_authorization()
    manifest = materialize_trial_manifest()
    if manifest["position_count"] != 3872:
        raise ValueError("frozen Phase-6 campaign requires exactly 3872 positions")

    output_dir.mkdir(parents=True, exist_ok=False)
    observations_path = output_dir / "observations.jsonl"
    attempts_path = output_dir / "attempt_ledger.jsonl"
    bindings_path = output_dir / "runtime_bindings.json"
    summary_path = output_dir / "campaign_summary.json"
    hashes_path = output_dir / "evidence_hashes.json"
    observations_path.touch(exist_ok=False)
    attempts_path.touch(exist_ok=False)

    bindings_payload = {
        "schema": 1,
        "experiment_id": EXPERIMENT_ID,
        "authorization": asdict(auth),
        "runtime_bindings": current_runtime_bindings(),
        "runtime_bundle_manifest": [
            {"path": path, "sha256": sha256}
            for path, sha256 in runtime_bundle_manifest()
        ],
    }
    bindings_path.write_text(_canonical_line(bindings_payload), encoding="utf-8")

    attempts: list[dict[str, Any]] = []
    valid_observations = 0

    for position in manifest["positions"]:
        expected = next_required_trial(attempts)
        if expected is None or expected != position:
            failure = {
                "error_type": "RuntimeError",
                "error_message": "attempt ledger diverged from frozen trial order",
                "global_order_index": int(position["global_order_index"]),
            }
            _write_summary_and_hashes(
                auth=auth,
                manifest=manifest,
                attempts=attempts,
                valid_observations=valid_observations,
                observations_path=observations_path,
                attempts_path=attempts_path,
                bindings_path=bindings_path,
                summary_path=summary_path,
                hashes_path=hashes_path,
                classification="STUDY2_PHASE6_CAMPAIGN_STOPPED_PARTIAL_EVIDENCE_RETAINED",
                failure=failure,
            )
            raise RuntimeError(failure["error_message"])

        order = int(position["global_order_index"])
        run_id = f"S2-P6-{order:04d}-A1"
        attempt = {
            "trial_id": position["trial_id"],
            "cell_id": position["cell_id"],
            "seed": int(position["seed"]),
            "run_id": run_id,
            "attempt_status": "INVALID",
        }

        try:
            result = run_trial(
                cell_id=position["cell_id"],
                seed=int(position["seed"]),
                run_id=run_id,
                mode=RuntimeMode.CAMPAIGN,
                authorization=auth,
            )
            if result.get("attempt_status") != "VALID":
                raise RuntimeError("runtime did not return VALID")
            if (
                result.get("trial_id") != position["trial_id"]
                or result.get("cell_id") != position["cell_id"]
                or int(result.get("seed")) != int(position["seed"])
            ):
                raise RuntimeError("runtime result identity differs from frozen position")

            attempt["attempt_status"] = "VALID"
            _append_jsonl(observations_path, result)
            valid_observations += 1
        except Exception as exc:
            attempt["error_type"] = type(exc).__name__
            attempt["error_message"] = str(exc)
            _append_jsonl(attempts_path, attempt)
            attempts.append(attempt)
            validate_attempt_ledger(attempts)
            _write_summary_and_hashes(
                auth=auth,
                manifest=manifest,
                attempts=attempts,
                valid_observations=valid_observations,
                observations_path=observations_path,
                attempts_path=attempts_path,
                bindings_path=bindings_path,
                summary_path=summary_path,
                hashes_path=hashes_path,
                classification="STUDY2_PHASE6_CAMPAIGN_STOPPED_PARTIAL_EVIDENCE_RETAINED",
                failure={
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                    "global_order_index": order,
                    "trial_id": position["trial_id"],
                },
            )
            raise RuntimeError(
                f"campaign stopped at frozen position {order}; no retry performed"
            ) from exc

        _append_jsonl(attempts_path, attempt)
        attempts.append(attempt)
        state = validate_attempt_ledger(attempts)
        if int(state["valid_position_count"]) != order:
            _write_summary_and_hashes(
                auth=auth,
                manifest=manifest,
                attempts=attempts,
                valid_observations=valid_observations,
                observations_path=observations_path,
                attempts_path=attempts_path,
                bindings_path=bindings_path,
                summary_path=summary_path,
                hashes_path=hashes_path,
                classification="STUDY2_PHASE6_CAMPAIGN_STOPPED_PARTIAL_EVIDENCE_RETAINED",
                failure={
                    "error_type": "RuntimeError",
                    "error_message": "VALID attempt did not advance exactly one frozen position",
                    "global_order_index": order,
                },
            )
            raise RuntimeError("VALID attempt did not advance exactly one frozen position")

    final_state = validate_attempt_ledger(attempts)
    if not final_state["campaign_complete"]:
        raise RuntimeError("campaign ended before frozen membership completed")
    if valid_observations != 3872 or int(final_state["invalid_attempt_count"]) != 0:
        raise RuntimeError("authoritative first campaign run did not complete 3872 VALID observations")

    return _write_summary_and_hashes(
        auth=auth,
        manifest=manifest,
        attempts=attempts,
        valid_observations=valid_observations,
        observations_path=observations_path,
        attempts_path=attempts_path,
        bindings_path=bindings_path,
        summary_path=summary_path,
        hashes_path=hashes_path,
        classification="STUDY2_PHASE6_CAMPAIGN_COMPLETE_CANDIDATE_EVIDENCE_NOT_YET_REPOSITORY_FROZEN",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate-static", action="store_true")
    parser.add_argument("--output-dir")
    args = parser.parse_args()

    if args.validate_static:
        report = static_report()
        print("STUDY2_PHASE6_CAMPAIGN_OPERATOR_STATIC=PASS")
        print(f"position_count={report['position_count']}")
        print(f"trial_manifest_sha256={report['trial_manifest_sha256']}")
        print(f"phase6_authorization_present={str(report['phase6_authorization_present']).lower()}")
        print("partial_failure_evidence_retained=true")
        print("campaign_seed_consumed=false")
        print("campaign_observations_generated=false")
        return 0

    if not args.output_dir:
        parser.error("--output-dir is required for campaign execution")
    result = execute_campaign(Path(args.output_dir))
    print("STUDY2_PHASE6_CAMPAIGN_EXECUTION=PASS")
    print(f"valid_observations={result['valid_observations']}")
    print(f"invalid_attempts={result['invalid_attempts']}")
    print(f"trial_manifest_sha256={result['trial_manifest_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
