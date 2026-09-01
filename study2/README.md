# Study 2 — Adversarial Evidence-Aware Security Research

**Status:** `PHASE7_PRESPECIFIED_ANALYSIS_RESULTS_FROZEN_CANONICAL`

Study 2 (`S2-AEATR-001`) is the separately frozen journal-research track for **adversarial evidence-aware cyber response and trusted recovery under intermittent connectivity**. It is scientifically and provenance-separated from the frozen Study-1 campaign; no Study-1 observation, seed, endpoint definition, statistical finding, or analysis membership was changed by Study 2.

## Canonical empirical state

- frozen campaign population: **3,872 VALID observations**, **0 INVALID attempts**, **85 cells**;
- primary Block-A replication: **96 paired seeds per cell**;
- secondary Blocks B–E: **32 paired seeds per cell**;
- frozen Phase-7 analysis: **162 primary paired contrasts** and **432 prespecified secondary contrasts**;
- independent reproduction: **0 mismatches** across cell summaries, primary contrasts, secondary contrasts, Holm adjustments/rejection flags, and terminal-state distributions;
- canonical Phase-7 results merge: PR `#70`, commit `49c62cbed3fb8fc318e44d696faba1854ed6c21a`;
- authoritative result ZIP SHA-256: `0136123a53d150437fefc8ace342af63b11d980cf8cab32ef7a4f03b78267417`;
- durable repository archive: `evidence/phase7/archive/study2-phase7-results-60f64327c45efda24cbb5b342f9d0eac908e1934.zip`.

Canonical interpretation and provenance are recorded in:

- `STUDY2_PROTOCOL.json` — prospectively frozen Study-2 design;
- `docs/PHASE5_RUNTIME_FREEZE.md` — logical-time/runtime calibration and prospective contact-analysis amendment;
- `evidence/phase6/README.md` — immutable campaign-evidence identity;
- `PHASE7_RESULTS_FREEZE.json` — machine-readable canonical statistical freeze;
- `PHASE7_PROVENANCE.json` — execution, reproduction, archive, and canonicalization provenance;
- `docs/PHASE7_RESULTS_FREEZE.md` — journal-facing statistical interpretation boundary.

Historical phase documents intentionally retain their stage-local status language as provenance and should not be read as the current Study-2 state.

## Scientific boundary

The Study-2 campaign is complete and must not be rerun or extended by appending observations to the frozen population. Future experiments require a separately frozen protocol and authorization boundary.

The work does **not** support claims about an operational spacecraft, RF system, real ground station, real credentials, classified/proprietary mission data, flight latency, certification, or universal policy superiority. Logical times are deterministic software-in-the-loop model time.

A valid signature is not treated as truth. In V5, a compromised policy-visible producer may validly sign a false value while the research-only adjudication truth remains unavailable to the runtime selector. This distinction is central to the canonical RQ1 finding that evidence-qualified recovery is not equivalent to objective correctness under the bounded producer-compromise model.

## Frozen factors and evidence semantics

The protocol includes adversary classes A0–A3, evidence treatments V0–V5, contact identities K0–K4, mission/event contexts, four prespecified Study-2 policies, security/context ablations, and a research-only adjudication oracle that is never selector input.

| ID | Study-2 meaning |
|---|---|
| `V0` | complete/current evidence |
| `V1` | omitted evidence |
| `V2` | stale or replayed evidence |
| `V3` | contradictory independent evidence |
| `V4` | post-signature manipulation |
| `V5` | bounded partial evidence-plane producer compromise |

Study-1 T1 remains omission/reduction of selected policy-visible evidence only; it was not retrospectively redefined as V2–V5.

## Contact and time semantics

Phase 5 prospectively froze deterministic logical SIL time:

- decision time: 10 logical seconds;
- recovery-processing increment: 5 logical seconds;
- right-censor horizon: 240 logical seconds;
- K0 immediate modeled contact;
- K1 short modeled outage;
- K2 medium modeled outage;
- K3 extended modeled outage;
- K4 intermittent/flapping modeled contact.

K0–K3 form the prespecified ordered contact series. K4 is a separate intermittent/flapping contrast and is **not** ordinal severity level 4.

## RQ3 interpretation constraint

The Block-C BENIGN/ADVERSARIAL cause label does not alter hidden truth or generated policy-visible evidence within an ambiguity family. The 54 zero C-family contrasts are therefore a **structural label-invariance/control result**, not empirical evidence that the policies distinguish or fail to distinguish genuinely different benign and adversarial causal mechanisms.

## Analysis constraints

- no Study-1 reanalysis;
- no new Study-2 campaign execution;
- no post-hoc seed replacement;
- no outcome-dependent exclusion or stopping;
- no alternate censoring horizon after outcome generation;
- no weighted global policy score;
- no global policy rank;
- A2/K2 remains an explicitly coupled producer-compromise/contact-loss profile;
- secondary n=32 blocks remain estimation/sensitivity evidence rather than small-effect confirmatory tests.

## Journal integration boundary

With Phase 7 canonically frozen, the active next step is **journal-manuscript integration and claim-to-evidence reconciliation**. Manuscript edits may summarize and interpret the frozen Study-2 results but may not modify their statistical identity or the frozen Study-1 science.
