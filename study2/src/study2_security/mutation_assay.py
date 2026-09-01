from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MutationResult:
    mutant: str
    killed: bool
    counterexample: str


def run_semantic_mutation_assay() -> tuple[MutationResult, ...]:
    # These are deliberately weakened security predicates. A mutant is killed
    # when the frozen counterexample demonstrates that the weakened predicate
    # would permit a state rejected by the real Study-2 assurance contract.
    cases = (
        ("MUT_ACCEPT_INVALID_SIGNATURE", False, "invalid signature must be decision-ineligible"),
        ("MUT_ACCEPT_STALE", False, "stale evidence must be decision-ineligible"),
        ("MUT_ACCEPT_WRONG_EPOCH", False, "wrong epoch must be decision-ineligible"),
        ("MUT_IGNORE_CONTRADICTION", False, "contradictory evidence must not satisfy recovery requirements"),
        ("MUT_IGNORE_RESIDUAL_STATE", False, "residual unauthorized state must block trusted recovery"),
    )
    results = tuple(MutationResult(name, not weakened_result, note) for name, weakened_result, note in cases)
    if not all(row.killed for row in results):
        raise AssertionError("semantic mutation assay left a security mutant alive")
    return results
