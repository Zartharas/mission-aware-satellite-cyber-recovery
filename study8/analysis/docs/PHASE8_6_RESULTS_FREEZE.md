# Phase 8.6 Results Freeze

**Experiment:** `S8-PQC-ICR-001`  
**Authorization:** `S8-RESULTS-FREEZE-001`  
**Status:** `STATISTICAL_FINDINGS_HASH_FROZEN_RESULTS_MERGE_NOT_AUTHORIZED`

## Frozen source evidence

- Canonical evidence commit: `a31c574e4887e3b92b72dad84933905feb100ef8`
- Canonical dataset SHA-256: `cfc65b6663be4e9f17a00ed102730f8642efcbbd844045acce032ff09a0bcabf`
- Prespecified analysis-plan lock: `4ecbe51fda3d053a4b950a2ad7c95439146b14ae`
- Phase-8.5 analysis trigger: `e661e070e481d8a0fea14ec96f777a7253de1f10`
- Phase-8.5 analysis run: `33713616663`, attempt `1`, conclusion `success`
- Audited analysis evidence commit: `b9c1c2c1ca59cc5bdc04e3226b1858577d3ea0f3`
- Interpretation-audit source head: `171b2c6282c207a69f0c718f19cd06f91a31ee17`
- Phase-8.6 candidate hash-report run: `33759739837`, conclusion `success`

## Frozen findings disposition

The primary policy-success finding is negative and is frozen as such: all four recovery policies have exact trusted-recovery success `635/864` (`73.4954%`), and the prespecified `P3 - P1` risk difference is exactly `0/1` (`0.000000` percentage points). No hypothesis-rescue interpretation is permitted by this freeze.

The secondary findings remain bounded to deterministic modeled logical-contact/recovery behavior and standardized cryptographic-object byte budgets. They are not empirical spacecraft, RF-link, onboard-compute, energy, flight, ground-station, or operational CCSDS/PQC performance measurements.

## Hash binding

`RESULTS_FREEZE_MANIFEST.json` and `RESULTS_FREEZE_SHA256SUMS.txt` bind 12 source/evidence files with SHA-256, including:

- the canonical observation dataset;
- the consumed campaign authorization;
- Phase-8.5 analysis authorization and prespecified plan;
- primary and independent statistical implementations plus findings auditor;
- primary and independent machine-readable findings;
- the independent findings-audit record;
- analysis provenance;
- the interpretation audit.

Primary and independent findings are byte-identical at SHA-256 `26a8ac4d1039917323e75a294775dd14a2b563adb12a5d2fcdb47ce8f15c992e`. The interpretation audit is bound at SHA-256 `620827f83fb566ff6ceae1b66c8f51f61ef8e5bbdabbb1c4b5a48b5187a82413`.

## Validation requirements

The final PR head must pass:

1. the dedicated `Validate Study 8 results freeze` workflow with manifest/hash verification;
2. the existing Study-8 validation workflow;
3. the complete repository-wide validation workflow;
4. byte-for-byte no-change checks against the Phase-8.5 audited scientific head.

Only after those checks pass may PR #89 be marked ready for review.

## Closed gates

- Results merge: **not authorized**
- Publication: **not authorized**
- Canonical re-execution: **not authorized**
- Statistical re-execution: **not authorized**

A later explicit authorization is required to merge PR #89.
