# S7E-AERC-001 Result Freeze 001

**Freeze:** `S7E-AERC-RESULT-FREEZE-001`  
**Authorization:** `S7E-AERC-RESULT-FREEZE-AUTH-001`  
**Experiment:** `S7E-AERC-001`  
**Execution of record:** `S7E-AERC-HELDOUT-EXEC-001`  
**Date:** 2026-09-23  
**Status:** `ACTIVE_RESULTS_FROZEN__PR_MERGE_NOT_AUTHORIZED__PUBLICATION_NOT_AUTHORIZED`

## Authorization boundary

The author explicitly authorized formal activation of this result freeze and durable preservation of the byte-exact held-out execution artifact.

This authorization does **not** authorize:

- rerunning `S7E-AERC-HELDOUT-EXEC-001`;
- retraining, refitting, tuning, or replacing the frozen models;
- changing endpoints or expanding the held-out population;
- merging PR #167;
- manuscript/publication result claims.

## Frozen execution evidence

The only scientific held-out execution of record remains:

- workflow run: `35948870036`;
- job: `107472877604`;
- source commit: `1cbc4be58a99e9add139e73efc9ab42a4f275864`;
- original Actions artifact ID: `10787499194`;
- ZIP SHA-256: `cc436ee98e20bb13643f58af738f42885b499a81bddad2766cb90f3e0860da35`;
- scenario-manifest SHA-256: `2d9e8e4b155cd4fe079010341e9bdbbfc1a1ab5e94f3467c1b5da8063d38c4fb`;
- population: E1 = 84, E2 = 104, C0 = 8, total = 196 scenarios;
- policy decisions: 784;
- invalid scenarios: 0;
- audit mismatches: 0.

No scientific rerun was performed during result-freeze activation.

## Durable preservation

The original 29,892-byte Actions ZIP is preserved in repository history as five ordered base64 chunks under:

`study7e/frozen_results/S7E-AERC-RESULT-FREEZE-001/`

Concatenating the chunks in manifest order and base64-decoding reconstructs the original ZIP byte-for-byte. The reconstructed ZIP must hash to:

`cc436ee98e20bb13643f58af738f42885b499a81bddad2766cb90f3e0860da35`

The result-freeze manifest also binds all 12 ZIP members by SHA-256. This removes scientific provenance dependence on the original Actions retention window without changing the artifact.

## Frozen scientific disposition

Exact aggregate counts remain:

| Policy | Errors | Unsafe proceed | False-conservative hold | ENTER | HOLD |
|---|---:|---:|---:|---:|---:|
| D0_BASE | 40 | 9 | 31 | 25 | 171 |
| L0_BASE | 47 | 21 | 26 | 42 | 154 |
| D1_CORROBORATED | 49 | 4 | 45 | 6 | 190 |
| L1_CORROBORATED | 43 | 31 | 12 | 66 | 130 |

Hypothesis disposition is frozen as:

- H1: **SUPPORTED**
- H2: **PARTIALLY SUPPORTED**
- H3: **PARTIALLY SUPPORTED**
- H4: **PARTIALLY SUPPORTED**
- H5: **SUPPORTED**

These dispositions include the adverse/null findings documented in `S7E_AERC_RESULT_FREEZE_CANDIDATE_001_REVIEW_2026-09-23.md`.

## Frozen interpretation boundaries

The freeze preserves the following boundaries:

- no global policy winner;
- no global ML superiority;
- no universal corroboration benefit;
- no claim that increasing trust-domain separation monotonically improves policy outcomes;
- exact finite-population counts are not operational spacecraft probabilities;
- no flight-qualification, certification-sufficiency, NASA-endorsement, RF-link, unmeasured hardware-performance, or stronger independence claim is supported.

In particular, the adverse L1 transfer behavior and the C0 null/control result are frozen findings and must not be removed or reframed post hoc.

## Integrity validation

`study7e/validation/validate_result_freeze_001.py` verifies:

1. authorization and governance boundaries;
2. result checkpoint and endpoint consistency;
3. hypothesis disposition consistency;
4. durable base64 reconstruction;
5. exact archive SHA-256;
6. every ZIP-member SHA-256;
7. zero invalid scenarios and zero audit mismatches;
8. continued prohibition of PR merge and publication/result claims.

Dedicated workflow:

`Study 7E result freeze integrity`

## Next gate

After post-freeze CI is green, PR #167 merge remains a separate author decision. Manuscript/publication result claims also remain a separate authorization gate and are not implied by any merge decision.
