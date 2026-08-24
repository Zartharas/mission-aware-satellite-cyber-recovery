from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DECISION_ID = "R-066"
REQUEST_CLASSIFICATION = "WP9_R066_FINAL_CAMPAIGN_RUNTIME_REQUEST"


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _load(path: Path | str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_fresh_campaign_evidence(
    request: dict[str, Any],
    *,
    root: Path = ROOT,
) -> dict[str, Any]:
    _require(request.get("decision_id") == DECISION_ID, "not an R-066 request")
    _require(
        request.get("classification") == REQUEST_CLASSIFICATION,
        "R-066 request classification changed",
    )

    run_id = str(request.get("run_id", ""))
    cell_id = str(request.get("cell_id", ""))
    seed = int(request.get("campaign_seed"))
    _require(bool(run_id), "R-066 run_id is required")
    _require(cell_id.startswith("A") and len(cell_id) == 3, "R-066 cell_id is invalid")

    expected = f"results/wp9/campaign/seed-{seed}/{cell_id}/{run_id}"
    evidence = str(request.get("evidence_directory", ""))
    _require(evidence == expected, "R-066 exact campaign evidence path changed")
    _require(
        "results/wp9/development" not in evidence,
        "R-066 campaign evidence escaped into development namespace",
    )

    target = root / evidence
    _require(
        not target.exists() and not target.is_symlink(),
        "R-066 campaign evidence directory already exists; hidden rerun blocked",
    )

    return {
        "schema": 1,
        "decision_id": DECISION_ID,
        "classification": "WP9_R066_CAMPAIGN_EVIDENCE_FRESHNESS_PASS",
        "run_id": run_id,
        "campaign_seed": seed,
        "cell_id": cell_id,
        "evidence_directory": evidence,
        "evidence_directory_fresh": True,
        "hidden_rerun_blocked": True,
        "filesystem_write_performed": False,
        "runtime_execution_performed": False,
        "campaign_seed_consumed": False,
        "campaign_data_generated": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    check = sub.add_parser("check")
    check.add_argument("--request-json", type=Path, required=True)
    args = parser.parse_args(argv)

    result = validate_fresh_campaign_evidence(_load(args.request_json))
    print("WP9_R066_CAMPAIGN_EVIDENCE_FRESHNESS=PASS")
    print("run_id=" + result["run_id"])
    print("campaign_seed=" + str(result["campaign_seed"]))
    print("cell_id=" + result["cell_id"])
    print("evidence_directory_fresh=true")
    print("hidden_rerun_blocked=true")
    print("runtime_execution_performed=false")
    print("campaign_seed_consumed=false")
    print("campaign_data_generated=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
