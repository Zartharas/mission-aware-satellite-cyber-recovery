from __future__ import annotations

import json
import math
from pathlib import Path

from study2_security.cell_matrix import matrix_sha256, materialize_cell_matrix, target_valid_observations

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
    assert data["adjudication_oracle"]["runtime_policy_access"] is False
    assert data["adversary_knowledge"]["may_read_ground_truth"] is False
    assert data["adversary_knowledge"]["may_compromise_verifier"] is False
    assert data["factors"]["evidence"] == ["V0", "V1", "V2", "V3", "V4", "V5"]
    assert data["factors"]["adversary"] == ["A0", "A1", "A2", "A3"]

    n = data["sample_size_rationale"]["primary_seed_blocks"]
    half = wilson_half_width(n)
    assert half <= 0.10
    recorded = data["sample_size_rationale"]["worst_case_wilson_half_width_at_n96"]
    assert abs(half - recorded) < 0.0001

    matrix = materialize_cell_matrix()
    assert len(matrix["cells"]) == data["cell_matrix"]["exact_cell_count"] == 85
    assert target_valid_observations(matrix) == data["cell_matrix"]["target_valid_observations"] == 3872
    assert matrix_sha256(matrix) == data["cell_matrix"]["canonical_sha256"]
    ids = [cell["cell_id"] for cell in matrix["cells"]]
    assert len(ids) == len(set(ids))
    for seed_set in matrix["seed_sets"].values():
        assert seed_set["end"] - seed_set["start"] + 1 == seed_set["count"]
    a2 = [row for row in matrix["cells"] if row.get("adversary") == "A2"]
    assert a2 and all(row.get("contact") != "K0" for row in a2)

    assert data["analysis"]["global_weighted_policy_score"] == "PROHIBITED"
    print(f"study2_protocol_status={data['status']}")
    print(f"study2_exact_cells={len(matrix['cells'])}")
    print(f"study2_target_valid_observations={target_valid_observations(matrix)}")
    print(f"study2_cell_matrix_sha256={matrix_sha256(matrix)}")
    print(f"study2_primary_seed_blocks={n}")
    print(f"study2_primary_wilson_half_width={half:.4f}")
    print("study2_adjudication_oracle_runtime_access=FALSE")
    print("study2_runtime_gate=CLOSED")
    print("study2_protocol_freeze_check=PASS")


if __name__ == "__main__":
    main()
