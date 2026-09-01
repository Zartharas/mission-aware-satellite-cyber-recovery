from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROTOCOL = ROOT / "study2" / "STUDY2_PROTOCOL.json"


def wilson_half_width(n: int, p: float = 0.5, z: float = 1.959963984540054) -> float:
    denom = 1.0 + z * z / n
    return z * math.sqrt(p * (1.0 - p) / n + z * z / (4.0 * n * n)) / denom


def main() -> None:
    data = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    assert data["status"] == "PROTOCOL_FROZEN_PRE_RUNTIME_RUNTIME_NOT_AUTHORIZED"
    assert data["study1_mutation_authorized"] is False
    assert data["study2_campaign_runtime_authorized"] is False
    assert data["runtime_gate"] == "CLOSED"
    assert data["factors"]["evidence"] == ["V0", "V1", "V2", "V3", "V4", "V5"]
    assert data["factors"]["adversary"] == ["A0", "A1", "A2", "A3"]
    n = data["sample_size_rationale"]["primary_seed_blocks"]
    half = wilson_half_width(n)
    assert half <= 0.10
    recorded = data["sample_size_rationale"]["worst_case_wilson_half_width_at_n96"]
    assert abs(half - recorded) < 0.0001
    assert data["analysis"]["global_weighted_policy_score"] == "PROHIBITED"
    print(f"study2_protocol_status={data['status']}")
    print(f"study2_primary_seed_blocks={n}")
    print(f"study2_primary_wilson_half_width={half:.4f}")
    print("study2_runtime_gate=CLOSED")
    print("study2_protocol_freeze_check=PASS")


if __name__ == "__main__":
    main()
