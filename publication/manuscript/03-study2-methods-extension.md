## 3.12 Study 2: adversarial evidence-aware security/dependability extension

Study 2 (`S2-AEATR-001`) was specified and executed as a separate empirical study rather than as additional observations appended to Study 1. Its frozen title is *Adversarial Evidence-Aware Cyber Response and Trusted Recovery for Intermittently Connected Space Systems*. The Study-1 population, estimands, seeds, and findings were not reopened or reanalyzed.

### 3.12.1 Frozen design and sample-size structure

The prospectively frozen Study-2 matrix contained 85 cells and exactly 3,872 planned campaign positions. Five paired seed namespaces were used:

- Block A: 18 cells × 96 seeds (`2100001`–`2100096`) = 1,728 observations;
- Block B: 20 cells × 32 seeds (`2200001`–`2200032`) = 640 observations;
- Block C: 18 cells × 32 seeds (`2300001`–`2300032`) = 576 observations;
- Block D: 20 cells × 32 seeds (`2400001`–`2400032`) = 640 observations;
- Block E: 9 cells × 32 seeds (`2500001`–`2500032`) = 288 observations.

The final campaign retained all 3,872 positions as VALID and recorded zero INVALID attempts. Block A was the primary evidence-mechanism block. Its 96 paired seeds were selected prospectively from a binary precision target: worst-case Wilson 95% half-width no greater than 0.10, corresponding to approximately 0.0981 at `n=96`. The 32-seed secondary blocks were prospectively designated for estimation/sensitivity and were not represented as powered tests for small effects.

### 3.12.2 Evidence, adversary, contact, and policy factors

The frozen evidence conditions were:

| ID | Meaning |
|---|---|
| V0 | complete/current evidence |
| V1 | omitted evidence |
| V2 | stale/replayed evidence |
| V3 | contradictory independent evidence |
| V4 | post-signature manipulation |
| V5 | bounded partial evidence-plane producer compromise |

The adversary classes ranged from A0 (no evidence-plane producer compromise) through A3 (two or more policy-visible producers controlled while the verifier and independent trust anchor remain outside the adversary budget). A1 allowed exactly one policy-visible producer to be controlled. A2 combined one controlled producer with modeled contact unavailability and therefore remained a **coupled producer-compromise/contact-loss profile**, not an unconfounded adversary-only treatment.

The policy set comprised `S2_B0_FAIL_CLOSED`, `S2_B1_FAIL_OPERATIONAL`, `S2_B2_RISK_THRESHOLD`, and `S2_S1_EVIDENCE_AWARE`, with additional security/context ablations in Block D. These are deterministic research mechanisms; none uses machine learning or a generative model.

Study 2 used modeled contact identities K0–K4. A prospective pre-campaign amendment clarified the analysis: K0–K3 form the ordered outage series, while K4 is a separate intermittent/flapping-contact contrast rather than ordinal severity level 4. The deterministic logical-time calibration was frozen before campaign execution: decision time 10 s, current-evidence issue time 8 s, evidence validity 5 s, recovery-processing increment 5 s, and right-censor horizon 240 s. K0 was available over [0,240], K1 from 20 s, K2 from 60 s, K3 from 180 s, and K4 over intermittent windows [25,35], [75,90], [145,165], and [220,240]. These are logical software-in-the-loop model times, not measured spacecraft, RF-link, ground-station, operator, or wall-clock latencies.

### 3.12.3 Experimental blocks

**Block A — primary evidence mechanism.** Eighteen cells crossed six evidence profiles (`V0/A0`, `V1/A0`, `V2/A0`, `V3/A0`, `V4/A1`, `V5/A1`) with three policies (`S2_B0_FAIL_CLOSED`, `S2_B2_RISK_THRESHOLD`, and `S2_S1_EVIDENCE_AWARE`) in a frozen compromised-update/recovery context with M2 and K0. Each cell used 96 paired seeds.

**Block B — contact and authorization.** Twenty cells crossed K0–K4 with the four prespecified policies under V0/A0. Each used 32 paired seeds. K0–K3 supplied the ordered trend; K4 was analyzed separately.

**Block C — matched ambiguity control.** Eighteen cells covered telemetry loss, state inconsistency, and contact/authorization loss with BENIGN/ADVERSARIAL cause labels and three policies. The runtime, however, does not instantiate distinct causal mechanisms behind those cause labels: within an ambiguity family, changing the label does not change hidden truth or generated policy-visible evidence. Block C is therefore interpreted as a structural label-invariance control rather than an empirical benign-versus-adversarial discrimination experiment.

**Block D — context ablation.** Twenty cells compared the full evidence-aware selector with prespecified mission-, evidence-, contact-, and security-context ablations across unauthorized-command, update/recovery, replay, and evidence-loss contexts.

**Block E — adversary-budget stress.** Nine cells compared A1/K0, A2/K2, and A3/K0 profiles across `S2_B0_FAIL_CLOSED`, `S2_B2_RISK_THRESHOLD`, and `S2_S1_EVIDENCE_AWARE`. A2/K2 was retained and reported explicitly as contact-coupled.

### 3.12.4 Trust boundary and research-only adjudication

Study 2 maintained a strict separation between policy-visible evidence and research-only adjudication truth. The simulated adversary could read the policy schema and public keys but could not read or modify experiment ground truth, the adjudication/correctness oracle, seed, treatment identity, provenance controls, or analysis controls; it also could not compromise the verifier or independent trust anchor.

The runtime selector receives only frozen policy-visible evidence/contact/context. The research-only adjudication oracle is used after the action for endpoint classification and is never a selector input. This separation permits a key security distinction: a compromised producer can generate a cryptographically valid, current-looking claim that satisfies policy-visible qualification while being false relative to hidden adjudication truth. Consequently, **evidence-qualified trusted recovery is not defined as objective correctness**.

### 3.12.5 Outcomes and censoring

The six primary outcomes were:

- unsafe-permissive response rate;
- false-conservative response rate;
- evidence-qualified trusted recovery;
- time to evidence-qualified trusted recovery;
- residual unauthorized state;
- legitimate-command rejection rate.

Secondary outcomes were time to containment, ground/spacecraft state divergence, response-selection stability, and recovery terminal state. Recovery and containment time-to-event summaries used the prospectively frozen 240-logical-second restricted-time horizon with right censoring; the horizon was not changed after outcomes were generated.

### 3.12.6 Prespecified analysis and multiplicity

Primary Block-A contrasts were paired by frozen seed and reported as effect estimates with 95% confidence intervals; no primary p-value gate was introduced. Secondary paired contrasts, ordered K0–K3 trends, and policy-by-contact interactions were analyzed within seven named contrast families. Holm adjustment was applied separately within each named secondary family and endpoint. No weighted global policy score or global policy rank was computed.

The interpretation constraints were frozen with the results: K4 is not an ordinal continuation of K0–K3; A2/K2 is not an unconfounded adversary-only effect; secondary `n=32` blocks are sensitivity/estimation evidence; logical SIL seconds are not operational latency; and the Block-C cause contrasts are structural label-invariance controls.

### 3.12.7 Reproducibility and statistical freeze

The Phase-6 campaign artifact was cryptographically bound before analysis. Phase 7 used the frozen analysis implementation at main commit `18207460fc5d419ad6a940f00db2df8610a5e5a0` and generated 85 cell summaries, 162 primary contrast rows, 432 secondary contrast rows, and 85 terminal-state summaries.

A separate standard-library auditor recomputed the results directly from the immutable Phase-6 observations without importing or invoking the primary analyzer. It independently reproduced all 85 numerical cell summaries, all 162 primary effects/standard deviations/confidence intervals, all 432 secondary effects/standard deviations/confidence intervals/raw p-values, all 432 Holm adjustments and rejection flags, and all 85 terminal-state distributions with **zero mismatches**.

The canonical Phase-7 result ZIP has SHA-256 `0136123a53d150437fefc8ace342af63b11d980cf8cab32ef7a4f03b78267417` and is retained durably in repository history under `study2/evidence/phase7/archive/`. The statistical findings were canonically merged and then closed as `PRESPECIFIED_ANALYSIS_RESULTS_FROZEN_CANONICAL`. Subsequent manuscript editing may summarize these results but does not redefine the frozen statistics.
