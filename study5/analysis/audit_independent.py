from __future__ import annotations

from collections import defaultdict
import csv
import json
from pathlib import Path
import sys

ATTACK_LABELS = {"COMMAND_FLOODING", "DATA_INJECTION", "DEFENCE_IMPAIRMENT", "STORAGE_EXHAUSTION"}
EXPECTED_LABELS = {"0": "COMMAND_FLOODING", "1": "DATA_INJECTION", "2": "DEFENCE_IMPAIRMENT", "3": "NORMAL", "4": "STORAGE_EXHAUSTION"}
EXPECTED_POLICIES = {"S2_B0_FAIL_CLOSED", "S2_B1_FAIL_OPERATIONAL", "S2_B2_RISK_THRESHOLD", "S2_S1_EVIDENCE_AWARE"}
EXPECTED_CONTEXTS = {"QUALIFIED_AUTH_AVAILABLE", "QUALIFIED_AUTH_UNAVAILABLE", "INCOMPLETE_EVIDENCE", "UNTRUSTED_SOURCE"}


def as_bool(value: str) -> bool:
    return value == "True"


def expected_action(row: dict[str, str]) -> str:
    qualified = all((as_bool(row["signature_valid"]) and as_bool(row["source_trusted"]), as_bool(row["fresh"]), as_bool(row["epoch_valid"]), not as_bool(row["contradictory"]), as_bool(row["minimum_evidence_complete"])))
    signal = as_bool(row["security_signal"])
    auth = as_bool(row["authorization_available"])
    policy = row["policy"]
    if policy == "S2_B0_FAIL_CLOSED":
        return "PROCEED_TO_RECOVERY_GATE" if qualified else "RESTRICT_AND_REQUEST_AUTHORIZATION"
    if policy == "S2_B1_FAIL_OPERATIONAL":
        return "RESTRICT_AND_REQUEST_AUTHORIZATION" if qualified and signal else "PRESERVE_LIMITED_OPERATION"
    if policy == "S2_B2_RISK_THRESHOLD":
        if not qualified:
            return "HOLD_AND_REQUIRE_EVIDENCE"
        return "RESTRICT_AND_REQUEST_AUTHORIZATION" if signal else "PRESERVE_LIMITED_OPERATION"
    if not qualified:
        return "HOLD_AND_REQUIRE_EVIDENCE"
    if signal and not auth:
        return "RESTRICT_AND_REQUEST_AUTHORIZATION"
    return "PROCEED_TO_RECOVERY_GATE"


def audit(root: Path) -> dict[str, object]:
    with (root / "portability_observations.csv").open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    with (root / "input_sufficiency.csv").open(newline="", encoding="utf-8") as fh:
        suff = list(csv.DictReader(fh))
    with (root / "transferability.csv").open(newline="", encoding="utf-8") as fh:
        transfer = list(csv.DictReader(fh))
    report = json.loads((root / "REPORT.json").read_text(encoding="utf-8"))

    mismatches = 0
    keys = set()
    grouped: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in rows:
        key = (row["label_code"], row["context"], row["policy"])
        if key in keys:
            mismatches += 1
        keys.add(key)
        if EXPECTED_LABELS.get(row["label_code"]) != row["label"]:
            mismatches += 1
        if row["policy"] not in EXPECTED_POLICIES or row["context"] not in EXPECTED_CONTEXTS:
            mismatches += 1
        if row["security_signal_source"] != "OFFLINE_LABEL_ORACLE":
            mismatches += 1
        if as_bool(row["security_signal"]) != (row["label"] != "NORMAL"):
            mismatches += 1
        if expected_action(row) != row["action"]:
            mismatches += 1
        if row["label"] in ATTACK_LABELS:
            grouped[(row["context"], row["policy"])].add(row["action"])

    if len(rows) != 80 or len(keys) != 80:
        mismatches += 1
    if len(suff) != 8 or any(row["directly_available_from_cucdid_row"] != "False" for row in suff):
        mismatches += 1
    if len(transfer) != 5:
        mismatches += 1
    if any(len(actions) != 1 for actions in grouped.values()) or len(grouped) != 16:
        mismatches += 1
    if report.get("direct_recovery_input_coverage_count") != 0 or report.get("row_level_cucdid_policy_benchmark_performed") is not False:
        mismatches += 1

    result = {"experiment_id": "S5-CUCD-001", "observations": len(rows), "sufficiency_rows": len(suff), "transferability_rows": len(transfer), "mismatches": mismatches}
    print("study5_independent_audit=" + ("PASS" if mismatches == 0 else "FAIL"))
    print(json.dumps(result, sort_keys=True))
    return result


if __name__ == "__main__":
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("study5_runtime")
    result = audit(path)
    raise SystemExit(0 if result["mismatches"] == 0 else 1)
