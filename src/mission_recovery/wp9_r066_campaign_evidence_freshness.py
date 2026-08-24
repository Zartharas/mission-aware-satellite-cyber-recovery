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
    run_component = Path(run_id)
    _require(
        bool(run_id)
        and not run_component.is_absolute()
        and len(run_component.parts) == 1
        and run_component.parts[0] not in {".", ".."},
        "R-066 run_id must be one relative path component",
    )
    _require(
        len(cell_id) == 3
        and cell_id.startswith("A")
        and cell_id[1:].isdigit()
        and 1 <= int(cell_id[1:]) <= 24,
        "R-066 cell_id is invalid",
    )

    expected = f"results/wp9/campaign/seed-{seed}/{cell_id}/{run_id}"
    evidence = str(request.get("evidence_directory", ""))
    relative = Path(evidence)
    _require(not relative.is_absolute(), "R-066 campaign evidence path is absolute")
    _require(".." not in relative.parts, "R-066 campaign evidence traversal blocked")
    _require(evidence == expected, "R-066 exact campaign evidence path changed")
    _require(
        "results/wp9/development" not in evidence,
        "R-066 campaign evidence escaped into development namespace",
    )

    cursor = root
    for part in relative.parts[:-1]:
        cursor = cursor / part
        _require(
            not cursor.is_symlink(),
            "R-066 campaign evidence parent symlink blocked",
        )

    campaign_root = (root / "results" / "wp9" / "campaign").resolve(strict=False)
    target = root / relative
    resolved_target = target.resolve(strict=False)
    _require(
        resolved_target == campaign_root or campaign_root in resolved_target.parents,
        "R-066 resolved campaign evidence escaped campaign root",
    )
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
        "parent_symlink_free": True,
        "resolved_namespace_confined": True,
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
    print("parent_symlink_free=true")
    print("resolved_namespace_confined=true")
    print("hidden_rerun_blocked=true")
    print("runtime_execution_performed=false")
    print("campaign_seed_consumed=false")
    print("campaign_data_generated=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
