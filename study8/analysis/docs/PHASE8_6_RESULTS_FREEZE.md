# Phase 8.6 Results-Freeze Candidate

**Experiment:** `S8-PQC-ICR-001`  
**Authorization:** `S8-RESULTS-FREEZE-001`  
**Status:** `HASH_BINDING_PENDING_PR_VALIDATION_MERGE_NOT_AUTHORIZED`

## Source evidence

- Canonical evidence commit: `a31c574e4887e3b92b72dad84933905feb100ef8`
- Canonical dataset SHA-256: `cfc65b6663be4e9f17a00ed102730f8642efcbbd844045acce032ff09a0bcabf`
- Prespecified analysis-plan lock: `4ecbe51fda3d053a4b950a2ad7c95439146b14ae`
- Phase-8.5 analysis trigger: `e661e070e481d8a0fea14ec96f777a7253de1f10`
- Phase-8.5 analysis run: `33713616663`, attempt `1`, conclusion `success`
- Audited analysis evidence commit: `b9c1c2c1ca59cc5bdc04e3226b1858577d3ea0f3`
- Interpretation-audit source head: `171b2c6282c207a69f0c718f19cd06f91a31ee17`

## Findings disposition being frozen

The primary policy-success finding is negative and must remain so: all four recovery policies have the same exact trusted-recovery success proportion, `635/864`, and the prespecified `P3 - P1` risk difference is exactly `0/1` (`0.000000` percentage points). No hypothesis-rescue interpretation is authorized.

The accompanying secondary findings remain bounded to the deterministic logical-contact model and standardized cryptographic-object byte budgets. They are not empirical spacecraft, RF-link, onboard-compute, energy, ground-station, flight, or operational CCSDS/PQC performance measurements.

## Freeze method

Phase 8.6 does not rewrite Phase-8.5 scientific outputs. It freezes their exact bytes by SHA-256 manifest after PR-side validation confirms:

1. the canonical dataset still matches its frozen hash;
2. primary and independent statistical findings remain byte-identical;
3. the complete deterministic 3,456-position finite-population inference boundary is preserved;
4. no sampling p-values, sampling confidence intervals, bootstrap, or permutation tests were introduced;
5. the Phase-8.5 scientific evidence files are unchanged from source head `171b2c6282c207a69f0c718f19cd06f91a31ee17`;
6. the interpretation audit preserves the negative primary finding and claim boundary;
7. repository-wide CI and the dedicated results-freeze workflow both pass on the final hash-bound PR head.

## Closed gates

- Results merge: **not authorized**
- Publication: **not authorized**
- Canonical re-execution: **not authorized**
- Statistical re-execution: **not authorized**

A later explicit authorization is required to merge the final results-freeze PR.
