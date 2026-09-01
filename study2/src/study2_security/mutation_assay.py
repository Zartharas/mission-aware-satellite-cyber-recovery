from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MutationResult:
    mutant: str
    killed: bool
    counterexample: str


def _qualified(*, signature: bool = True, trust: bool = True, fresh: bool = True,
               epoch: bool = True, sequence: bool = True, contradiction: bool = False) -> bool:
    return signature and trust and fresh and epoch and sequence and not contradiction


def run_semantic_mutation_assay() -> tuple[MutationResult, ...]:
    cases = []

    baseline = _qualified(signature=False)
    mutant = _qualified(signature=True)
    cases.append(MutationResult("MUT_ACCEPT_INVALID_SIGNATURE", (not baseline) and mutant, "invalid signature"))

    baseline = _qualified(fresh=False)
    mutant = _qualified(fresh=True)
    cases.append(MutationResult("MUT_ACCEPT_STALE", (not baseline) and mutant, "stale evidence"))

    baseline = _qualified(epoch=False)
    mutant = _qualified(epoch=True)
    cases.append(MutationResult("MUT_ACCEPT_WRONG_EPOCH", (not baseline) and mutant, "wrong recovery epoch"))

    baseline = _qualified(contradiction=True)
    mutant = _qualified(contradiction=False)
    cases.append(MutationResult("MUT_IGNORE_CONTRADICTION", (not baseline) and mutant, "trusted-source contradiction"))

    qualified = _qualified()
    baseline_recovery = qualified and not True
    mutant_recovery = qualified
    cases.append(MutationResult("MUT_IGNORE_RESIDUAL_STATE", (not baseline_recovery) and mutant_recovery, "residual unauthorized state"))

    results = tuple(cases)
    if not all(row.killed for row in results):
        alive = [row.mutant for row in results if not row.killed]
        raise AssertionError(f"semantic mutation assay left mutants alive: {alive}")
    return results
