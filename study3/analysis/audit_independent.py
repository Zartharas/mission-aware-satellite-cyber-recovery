from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

EPOCH_S = 5
HORIZON_S = 240
K4_WINDOWS = ((25, 35), (75, 90), (145, 165), (220, 240))
PERMISSIVE = {"PRESERVE_LIMITED_OPERATION", "PROCEED_TO_RECOVERY_GATE"}
PROTECTIVE = {"HOLD_AND_REQUIRE_EVIDENCE", "RESTRICT_AND_REQUEST_AUTHORIZATION"}


def _bool(value: str) -> bool:
    if value == "True":
        return True
    if value == "False":
        return False
    raise ValueError(f"not a boolean: {value!r}")


def _optional_bool(value: str) -> bool | None:
    if value == "":
        return None
    return _bool(value)


def _contact(regime: str, t_s: int) -> bool:
    if regime == "K0":
        return 0 <= t_s <= HORIZON_S
    if regime == "K4":
        return any(start <= t_s <= end for start, end in K4_WINDOWS)
    raise ValueError(regime)


def _action(policy: str, evidence_qualified: bool, security_signal: bool, contact: bool) -> str:
    if policy == "S2_B0_FAIL_CLOSED":
        return "PROCEED_TO_RECOVERY_GATE" if evidence_qualified else "RESTRICT_AND_REQUEST_AUTHORIZATION"
    if policy == "S2_B2_RISK_THRESHOLD":
        if not evidence_qualified:
            return "HOLD_AND_REQUIRE_EVIDENCE"
        return "RESTRICT_AND_REQUEST_AUTHORIZATION" if security_signal else "PRESERVE_LIMITED_OPERATION"
    if policy == "S2_S1_EVIDENCE_AWARE":
        if not evidence_qualified:
            return "HOLD_AND_REQUIRE_EVIDENCE"
        if security_signal and not contact:
            return "RESTRICT_AND_REQUEST_AUTHORIZATION"
        return "PROCEED_TO_RECOVERY_GATE"
    raise ValueError(policy)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def audit(root: Path) -> dict[str, int | str]:
    epoch_path = root / "epochs.csv"
    summary_path = root / "trajectory_summary.csv"
    report_path = root / "REPORT.json"
    epochs = _load(epoch_path)
    summaries = _load(summary_path)
    report = json.loads(report_path.read_text(encoding="utf-8"))

    errors: list[str] = []
    if len(epochs) != 67620:
        errors.append(f"epoch_count={len(epochs)}")
    if len(summaries) != 1380:
        errors.append(f"trajectory_count={len(summaries)}")
    if report.get("trajectories") != 1380 or report.get("epoch_rows") != 67620:
        errors.append("report_membership_mismatch")

    for filename in ("epochs.csv", "trajectory_summary.csv", "cell_summary.csv"):
        expected = report.get("files", {}).get(filename)
        actual = _sha256(root / filename)
        if expected != actual:
            errors.append(f"sha_mismatch:{filename}")

    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in epochs:
        tid = row["trajectory_id"]
        grouped[tid].append(row)
        t_s = int(row["t_s"])
        onset = int(row["onset_s"])
        contact = _bool(row["contact_available"])
        expected_contact = _contact(row["contact"], t_s)
        if contact != expected_contact:
            errors.append(f"contact:{tid}:{t_s}")
        hidden = _bool(row["hidden_authorization_valid"])
        if hidden != (t_s < onset):
            errors.append(f"hidden_truth:{tid}:{t_s}")
        security = _bool(row["security_signal"])
        if security != (t_s >= onset):
            errors.append(f"security_signal:{tid}:{t_s}")

        present = _bool(row["record_present"])
        fresh = _bool(row["record_fresh"])
        signature = _bool(row["signature_valid"])
        qualified = _bool(row["evidence_qualified"])
        if qualified != (present and fresh and signature):
            errors.append(f"qualification:{tid}:{t_s}")
        claim = _optional_bool(row["claim_authorization_valid"])
        expected_action = _action(row["policy"], qualified, security, contact)
        if row["action"] != expected_action:
            errors.append(f"action:{tid}:{t_s}")
        gate = _bool(row["gate_qualified"])
        expected_gate = expected_action == "PROCEED_TO_RECOVERY_GATE" and qualified and claim is True
        if gate != expected_gate:
            errors.append(f"gate:{tid}:{t_s}")
        expected_unsafe_permissive = t_s >= onset and not hidden and expected_action in PERMISSIVE
        expected_unsafe_qualified = t_s >= onset and not hidden and expected_gate
        expected_protective = t_s >= onset and expected_action in PROTECTIVE
        if _bool(row["unsafe_permissive"]) != expected_unsafe_permissive:
            errors.append(f"unsafe_permissive:{tid}:{t_s}")
        if _bool(row["unsafe_qualified"]) != expected_unsafe_qualified:
            errors.append(f"unsafe_qualified:{tid}:{t_s}")
        if _bool(row["protective"]) != expected_protective:
            errors.append(f"protective:{tid}:{t_s}")
        if t_s < onset and (expected_unsafe_permissive or expected_unsafe_qualified):
            errors.append(f"pre_onset_exposure:{tid}:{t_s}")

        is_new = present and row["record_age_s"] == "0"
        affected = _bool(row["treatment_affected"])
        if is_new and t_s >= onset and row["evidence"] == "V0":
            if claim is not False or not signature or affected:
                errors.append(f"v0_record:{tid}:{t_s}")
        if is_new and affected and row["evidence"] == "V4":
            if claim is not True or signature or expected_gate:
                errors.append(f"v4_record:{tid}:{t_s}")
        if is_new and affected and row["evidence"] == "V5":
            if claim is not True or not signature:
                errors.append(f"v5_record:{tid}:{t_s}")

        expected_origin = "NONE"
        if expected_unsafe_qualified:
            if row["record_age_s"] == "":
                errors.append(f"origin_missing_record:{tid}:{t_s}")
            else:
                received_at = t_s - int(row["record_age_s"])
                if received_at < onset:
                    expected_origin = "PRE_ONSET_CACHE"
                elif affected and row["evidence"] == "V5":
                    expected_origin = "V5_AFFECTED_RECORD"
                else:
                    expected_origin = "UNEXPECTED"
        if row["unsafe_qualification_origin"] != expected_origin:
            errors.append(f"origin:{tid}:{t_s}:{row['unsafe_qualification_origin']}:{expected_origin}")
        if expected_origin == "UNEXPECTED":
            errors.append(f"unexpected_false_qualification_origin:{tid}:{t_s}")
        if row["evidence"] in {"V0", "V4"} and expected_unsafe_qualified and expected_origin != "PRE_ONSET_CACHE":
            errors.append(f"v0_v4_noncache_false_qualification:{tid}:{t_s}")

    if len(grouped) != 1380:
        errors.append(f"grouped_trajectory_count={len(grouped)}")

    summary_by_id = {row["trajectory_id"]: row for row in summaries}
    for tid, rows in grouped.items():
        rows.sort(key=lambda row: int(row["t_s"]))
        if len(rows) != 49 or [int(row["t_s"]) for row in rows] != list(range(0, 245, 5)):
            errors.append(f"epoch_grid:{tid}")
            continue
        onset = int(rows[0]["onset_s"])
        post = [row for row in rows if int(row["t_s"]) >= onset]
        affected_received = sum(
            _bool(row["treatment_affected"]) and row["record_age_s"] == "0"
            for row in rows
        )
        if rows[0]["persistence"] == "ONE_SHOT" and affected_received != 1:
            errors.append(f"one_shot_count:{tid}:{affected_received}")
        unsafe_p = sum(_bool(row["unsafe_permissive"]) for row in post)
        unsafe_q_flags = [_bool(row["unsafe_qualified"]) for row in post]
        unsafe_q = sum(unsafe_q_flags)
        cache_q = sum(row["unsafe_qualification_origin"] == "PRE_ONSET_CACHE" for row in post)
        v5_q = sum(row["unsafe_qualification_origin"] == "V5_AFFECTED_RECORD" for row in post)
        if cache_q + v5_q != unsafe_q:
            errors.append(f"origin_decomposition:{tid}")
        protective = sum(_bool(row["protective"]) for row in post)
        episodes = sum(flag and (i == 0 or not unsafe_q_flags[i - 1]) for i, flag in enumerate(unsafe_q_flags))
        transitions = sum(post[i]["action"] != post[i - 1]["action"] for i in range(1, len(post)))

        expected = summary_by_id.get(tid)
        if expected is None:
            errors.append(f"missing_summary:{tid}")
            continue
        checks = {
            "post_onset_epochs": len(post),
            "affected_received_records": affected_received,
            "unsafe_permissive_epochs": unsafe_p,
            "unsafe_qualified_epochs": unsafe_q,
            "unsafe_qualified_exposure_s": unsafe_q * EPOCH_S,
            "unsafe_qualified_episode_count": episodes,
            "cache_unsafe_qualified_epochs": cache_q,
            "v5_affected_unsafe_qualified_epochs": v5_q,
            "protective_epochs": protective,
            "action_transition_count": transitions,
        }
        for key, value in checks.items():
            if int(expected[key]) != value:
                errors.append(f"summary:{tid}:{key}")
        float_checks = {
            "unsafe_permissive_epoch_rate": unsafe_p / len(post),
            "unsafe_qualified_epoch_rate": unsafe_q / len(post),
            "protective_epoch_rate": protective / len(post),
        }
        for key, value in float_checks.items():
            if abs(float(expected[key]) - value) > 1e-12:
                errors.append(f"summary_float:{tid}:{key}")

    if errors:
        preview = "\n".join(errors[:25])
        raise SystemExit(f"study3_independent_audit=FAIL errors={len(errors)}\n{preview}")

    return {
        "experiment_id": "S3-K4E-001",
        "trajectory_mismatches": 0,
        "epoch_rule_mismatches": 0,
        "qualification_origin_mismatches": 0,
        "sha_mismatches": 0,
        "trajectories": 1380,
        "epoch_rows": 67620,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="study3/results/campaign")
    args = parser.parse_args()
    result = audit(Path(args.input))
    print("study3_independent_audit=PASS")
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
