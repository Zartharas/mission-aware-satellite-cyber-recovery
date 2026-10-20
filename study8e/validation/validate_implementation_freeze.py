#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FILES = (
    "study8e/STUDY8E_IMPLEMENTATION_SPEC.json",
    "study8e/src/external_trace_recovery_model.py",
    "study8e/audit/independent_external_trace_reference.py",
    "study8e/tests/test_external_trace_recovery_model.py",
    "study8/STUDY8_CRYPTO_OBJECT_BUDGETS.json",
    "study8/STUDY8_PROTOCOL.json",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    spec = json.loads((ROOT / FILES[0]).read_text(encoding="utf-8"))
    if spec.get("implementation_id") != "S8E-IMPL-001":
        raise SystemExit("unexpected implementation identity")
    if spec.get("canonical_execution_authorized") is not False:
        raise SystemExit("canonical execution must remain disabled")
    if spec.get("real_trace_endpoint_computation_authorized") is not False:
        raise SystemExit("real-trace endpoint computation must remain disabled")

    primary_text = (ROOT / FILES[1]).read_text(encoding="utf-8")
    reference_text = (ROOT / FILES[2]).read_text(encoding="utf-8")
    if "canonical external-trace execution is not authorized" not in primary_text:
        raise SystemExit("primary direct-execution guard missing")
    if "canonical external-trace audit execution is not authorized" not in reference_text:
        raise SystemExit("reference direct-execution guard missing")
    if "study8.src.contact_recovery_model" in primary_text:
        raise SystemExit("Study 8E primary must not import frozen Study 8 implementation")

    budget = json.loads((ROOT / "study8/STUDY8_CRYPTO_OBJECT_BUDGETS.json").read_text(encoding="utf-8"))
    totals = {
        name: int(values["base_transition_crypto_bytes"])
        for name, values in budget["profiles"].items()
    }
    expected = {
        "PROFILE_512_44": 12560,
        "PROFILE_768_65": 17460,
        "PROFILE_1024_87": 24236,
    }
    if totals != expected:
        raise SystemExit(f"unexpected inherited Study 8 object totals: {totals}")

    report = {
        "schema": 1,
        "experiment_id": "S8E-ECTV-001",
        "implementation_id": "S8E-IMPL-001",
        "status": "IMPLEMENTATION_FREEZE_CANDIDATE_VALIDATED_ON_SYNTHETIC_FIXTURES",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "files": {
            rel: {
                "sha256": sha256(ROOT / rel),
                "bytes": (ROOT / rel).stat().st_size,
            }
            for rel in FILES
        },
        "inherited_study8_transition_totals_bytes": totals,
        "scope_boundary": {
            "real_satnogs_trace_loaded": False,
            "real_trace_timing_endpoint_computed": False,
            "canonical_study8e_execution": False,
            "study8_modified": False,
            "acta_package_modified": False,
        },
    }
    out = ROOT / "study8e/evidence/implementation_freeze/IMPLEMENTATION_FREEZE_MANIFEST.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("Study 8E implementation freeze manifest: PASS")
    print(f"manifest_sha256={sha256(out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
