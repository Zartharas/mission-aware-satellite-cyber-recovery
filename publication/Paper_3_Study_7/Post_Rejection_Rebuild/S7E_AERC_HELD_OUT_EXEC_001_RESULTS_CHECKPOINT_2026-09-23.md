# S7E-AERC-001 Held-Out Execution 001 — Results Checkpoint

**Execution:** `S7E-AERC-HELDOUT-EXEC-001`  
**Plan:** `S7E-AERC-HELDOUT-PLAN-001`  
**Model freeze:** `S7E-AERC-MODEL-FREEZE-001`  
**Status:** valid complete-population scientific execution; results checkpointed  
**Publication/result claims:** NOT AUTHORIZED  
**PR #167 merge:** NOT AUTHORIZED

## Execution evidence

- workflow run: `35948870036`
- scientific job: `107472877604`
- source commit: `1cbc4be58a99e9add139e73efc9ab42a4f275864`
- artifact: `10787499194`
- artifact SHA-256: `cc436ee98e20bb13643f58af738f42885b499a81bddad2766cb90f3e0860da35`
- scenario-manifest SHA-256: `2d9e8e4b155cd4fe079010341e9bdbbfc1a1ab5e94f3467c1b5da8063d38c4fb`

The campaign produced exactly 196 held-out scenarios and 784 policy decisions. There were **0 invalid scenarios** and **0 audit mismatches**. Independent post-run recomputation from the raw decision ledger reproduced the endpoint, paired-disagreement, topology/fault, and output-hash records exactly.

## Exact aggregate counts

| Policy | Decision errors | Unsafe proceed | False-conservative hold | Enter | Hold |
|---|---:|---:|---:|---:|---:|
| D0_BASE | 40 | 9 | 31 | 25 | 171 |
| L0_BASE | 47 | 21 | 26 | 42 | 154 |
| D1_CORROBORATED | 49 | 4 | 45 | 6 | 190 |
| L1_CORROBORATED | 43 | 31 | 12 | 66 | 130 |

These are finite-population descriptive counts. This checkpoint does not identify a global policy winner and does not authorize publication claims.

### By held-out block

E1 (84): D0 18/3/15; L0 21/9/12; D1 24/3/21; L1 17/11/6, where each triple is decision-error / unsafe-proceed / false-conservative-hold.

E2 (104): D0 22/6/16; L0 26/12/14; D1 25/1/24; L1 26/20/6.

C0 (8): all four policies produced HOLD in all 8 scenarios with zero error.

### Equal-information policy disagreements

- D0 vs L0: 67/196 overall; E1 27/84; E2 40/104; C0 0/8.
- D1 vs L1: 72/196 overall; E1 29/84; E2 43/104; C0 0/8.

### Corroboration deltas

Corroborated-minus-base, overall:

- deterministic D1-D0: unsafe proceed -5; false-conservative hold +14;
- learned L1-L0: unsafe proceed +10; false-conservative hold -14.

These deltas must be interpreted together with topology/fault strata; the protocol prohibits an aggregate global-superiority conclusion.

## Evidence integrity

The result checkpoint binds the SHA-256 identity of every raw/derived held-out output. The Actions artifact remains the byte-exact execution bundle and is retained by GitHub through 2026-10-24 02:50:03 UTC. The repository checkpoint preserves its digest and all member-file hashes.

## One-shot seal

`S7E-AERC-HELDOUT-EXEC-001` is now sealed. The workflow detector will not repeat scientific inference if the checkpoint exists, including manual dispatch. Any later campaign requires a new execution ID and explicit authorization.

## Next gate

Separate scientific-results review/interpretation and result-freeze decision. No manuscript/publication claim or PR #167 merge is authorized by this checkpoint.
