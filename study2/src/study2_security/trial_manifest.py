from __future__ import annotations

import hashlib
import json
from typing import Any

from .cell_matrix import materialize_cell_matrix, matrix_sha256


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=True,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def materialize_trial_manifest() -> dict[str, Any]:
    matrix = materialize_cell_matrix()
    positions: list[dict[str, Any]] = []
    global_order_index = 1

    for cell in matrix["cells"]:
        seed_set = matrix["seed_sets"][cell["seed_set"]]
        cell_sha256 = hashlib.sha256(canonical_bytes(cell)).hexdigest()
        for seed in range(int(seed_set["start"]), int(seed_set["end"]) + 1):
            positions.append(
                {
                    "global_order_index": global_order_index,
                    "trial_id": f"{matrix['experiment_id']}:{cell['cell_id']}:{seed}",
                    "cell_id": cell["cell_id"],
                    "block": cell["block"],
                    "seed": seed,
                    "seed_set": cell["seed_set"],
                    "cell_sha256": cell_sha256,
                }
            )
            global_order_index += 1

    return {
        "schema": 1,
        "experiment_id": matrix["experiment_id"],
        "status": "TRIAL_MANIFEST_FROZEN_PRE_RUNTIME",
        "cell_matrix_sha256": matrix_sha256(matrix),
        "position_count": len(positions),
        "positions": positions,
    }


def trial_manifest_sha256(manifest: dict[str, Any] | None = None) -> str:
    return hashlib.sha256(canonical_bytes(manifest or materialize_trial_manifest())).hexdigest()
