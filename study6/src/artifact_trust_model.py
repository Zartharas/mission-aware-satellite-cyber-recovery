from __future__ import annotations

from dataclasses import dataclass, replace
from itertools import combinations
import json
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
PROTOCOL = json.loads((ROOT / "study6" / "STUDY6_PROTOCOL.json").read_text(encoding="utf-8"))

SIGNALS = tuple(PROTOCOL["assurance_signals"])
GATES = {k: tuple(v) for k, v in PROTOCOL["gates"].items()}


@dataclass(frozen=True)
class ArtifactState:
    state_id: str
    objective_baseline_correct: bool
    signature_valid: bool
    independent_target_digest_match: bool
    provenance_valid: bool
    independent_reproduced_build_match: bool
    source_review_attested: bool
    release_approved: bool

    def signal(self, name: str) -> bool:
        return bool(getattr(self, name))


def baseline_states() -> tuple[ArtifactState, ...]:
    rows = []
    for state_id, values in PROTOCOL["baseline_states"].items():
        rows.append(ArtifactState(state_id=state_id, **values))
    return tuple(rows)


def qualify(state: ArtifactState, gate_id: str) -> bool:
    return all(state.signal(signal) for signal in GATES[gate_id])


def adversarial_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for state in baseline_states():
        for gate_id in GATES:
            qualified = qualify(state, gate_id)
            rows.append({
                "block": "A_ADVERSARIAL_BASELINE",
                "state_id": state.state_id,
                "gate_id": gate_id,
                "qualified": qualified,
                "objective_baseline_correct": state.objective_baseline_correct,
                "unsafe_qualified": qualified and not state.objective_baseline_correct,
                "correct_rejected": (not qualified) and state.objective_baseline_correct,
            })
    return rows


def signal_subsets() -> Iterable[tuple[str, ...]]:
    for size in range(len(SIGNALS) + 1):
        yield from combinations(SIGNALS, size)


def benign_unavailability_rows() -> list[dict[str, object]]:
    clean = next(state for state in baseline_states() if state.state_id == "CLEAN_APPROVED")
    rows: list[dict[str, object]] = []
    for missing in signal_subsets():
        modifications = {name: False for name in missing}
        state = replace(clean, **modifications)
        missing_id = "+".join(missing) if missing else "NONE"
        for gate_id in GATES:
            qualified = qualify(state, gate_id)
            rows.append({
                "block": "B_BENIGN_ASSURANCE_UNAVAILABILITY",
                "missing_signals": missing_id,
                "missing_count": len(missing),
                "gate_id": gate_id,
                "qualified": qualified,
                "objective_baseline_correct": True,
                "benign_availability_loss": not qualified,
            })
    return rows


def all_rows() -> list[dict[str, object]]:
    return adversarial_rows() + benign_unavailability_rows()
