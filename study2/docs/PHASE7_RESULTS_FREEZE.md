# Study 2 Phase 7 — Prespecified Analysis Results Freeze

**Status:** `PRESPECIFIED_ANALYSIS_RESULTS_FROZEN_PENDING_CANONICAL_MERGE`

This freeze records the deterministic Phase-7 analysis of the immutable Phase-6 Study-2 campaign. It does not generate new campaign data, alter the frozen trial population, rerun Study 1, or create a weighted/global policy score. Pull request `#70` is the canonical merge gate into `main`; until that merge occurs, the frozen branch identity remains the authoritative Phase-7 freeze candidate.

## Evidence and implementation boundary

- authoritative Phase-6 population: **3,872 VALID observations**, **0 INVALID attempts**, **85 cells**
- Phase-6 artifact SHA-256: `195860bd44b38ccf170f02cb1cb392583217296d08640c99b18b52286403e133`
- Phase-7 implementation freeze: main commit `18207460fc5d419ad6a940f00db2df8610a5e5a0`
- analysis entrypoint SHA-256: `351039f0d6d79eb605c7dc027a5427da862b0f544815f862a85bc997df56c8bd`
- Phase-7 execution run/job: `33553370460` / `100008137499`
- Phase-7 result artifact SHA-256: `0136123a53d150437fefc8ace342af63b11d980cf8cab32ef7a4f03b78267417`

The analysis produced **162 primary paired contrasts** and **432 prespecified secondary contrasts**. Recovery and containment time-to-event outcomes use the frozen 240-logical-second restriction. These are deterministic logical SIL seconds, not measured spacecraft or network wall-clock latency.

## Independent reproduction and arithmetic audit

Before freezing the results, the generated tables were independently recomputed directly from the immutable Phase-6 observations. A second, repository-retained independent auditor provides a machine-reproducible check without importing or invoking the primary Phase-7 analyzer.

- independent auditor: `study2/scripts/audit_phase7_independent.py`
- auditor SHA-256: `3e738e2c27d621073a8c1bba49044df3fc83d099abdd244894537f4c4b22142d`
- independent CI run/job: `33558376612` / `100024673115`
- CI conclusion: **PASS**
- all 85 cell-level numerical summaries matched;
- all 162 primary paired effect estimates, paired standard deviations, and 95% confidence intervals matched;
- all 432 secondary paired/trend/interaction effect estimates, paired standard deviations, confidence intervals, and raw p-values matched;
- all 432 Holm-adjusted p-values and rejection flags matched;
- all 85 terminal-state distributions matched.

No mismatch was found.

## Principal prespecified findings

### RQ1 — Evidence conditions and bounded partial compromise

In Block A, V1 omission, V2 stale/replay, V3 contradiction, and V4 post-signature manipulation changed the fail-closed and evidence-aware policies from a recovery-gate attempt under V0 to restrictive/hold behavior; for the frozen hidden prerequisites in this block this reduced the adjudicated unsafe-permissive rate by 1.0 for `S2_B0_FAIL_CLOSED` and `S2_S1_EVIDENCE_AWARE`. `S2_B2_RISK_THRESHOLD` was already restrictive, so those contrasts were zero.

V5 is qualitatively different. A controlled producer can create policy-visible evidence that remains authenticated/current enough for the recovery gate while being false relative to the research-only adjudication truth. Under V5, `S2_B0_FAIL_CLOSED` and `S2_S1_EVIDENCE_AWARE` each reached evidence-qualified trusted recovery in all A96 observations (recovery-rate change +1.0 versus V0 and restricted recovery-time change -230 logical seconds), yet the adjudicated unsafe-permissive rate remained 1.0. This is evidence that authenticated/evidence-qualified recovery is not equivalent to objectively correct recovery under the bounded compromise model.

Within Block A, the evidence-aware selector and the fail-closed baseline had identical primary endpoint estimates. Relative to `S2_B2_RISK_THRESHOLD`, the evidence-aware selector was more permissive under V0 and V5; under V5 that permissiveness produced evidence-qualified recovery but also an unsafe-permissive difference of +1.0. These are endpoint-specific trade-offs, not a global policy ranking.

### RQ2 — Contact and authorization constraints

At K0, `S2_B0_FAIL_CLOSED` and `S2_S1_EVIDENCE_AWARE` both reached evidence-qualified recovery at 10 logical seconds without an unsafe-permissive response. Under K1, K2, K3, and K4, the evidence-aware selector initially restricted and then proceeded at the next frozen contact opportunity, recovering at 25, 65, 185, and 30 logical seconds respectively while retaining an unsafe-permissive rate of 0.

The fail-closed baseline also eventually recovered at those contact opportunities, but its initial permissive action under unavailable authorization produced an unsafe-permissive increase of +1.0 versus K0 at each non-K0 contact profile. The K0-K3 ordered unsafe-permissive slope for this baseline was +0.3 per contact-severity step, whereas the evidence-aware selector's unsafe-permissive slope was 0. K4 remains a separate intermittent/flapping contrast and is not treated as ordinal severity 4.

### RQ3 — Matched benign/adversarial ambiguity: structural label-invariance control

All 54 prespecified C-family endpoint contrasts were zero after Holm adjustment (0 rejected). However, the frozen Block-C runtime does **not** instantiate distinct benign and adversarial causal mechanisms behind those labels. Within each ambiguity family, the `BENIGN`/`ADVERSARIAL` cause value does not alter the hidden truth state or the generated policy-visible evidence; it is retained as an adjudication/analysis label. The zero contrasts are therefore a **structural label-invariance/control result** under intentionally identical runtime truth and policy-visible evidence.

Accordingly, this result must **not** be reported as evidence that the policies distinguish, fail to distinguish, or otherwise perform across genuinely different benign versus adversarial causal mechanisms. It verifies that changing a non-operative cause label alone does not change the analyzed outcomes. A journal claim about empirical benign-versus-adversarial discrimination would require a separate design in which the causal mechanisms differ while the intended observable ambiguity relationship is explicitly controlled.

The hash-bound generated `ANALYSIS_REPORT.md` is retained unchanged as an execution artifact. Where its shorter RQ3 wording could be read more broadly, this freeze document supplies the authoritative interpretation boundary without changing any numerical result or generated-file identity.

### RQ4 — Context contribution

The context ablations exposed specific dependencies rather than a single dominant context variable. In the unauthorized-command context, removing mission context or contact context increased the unsafe-permissive rate by +1.0 relative to the full evidence-aware selector. In the update/recovery context, the security-only ablation reduced evidence-qualified recovery by 1.0 and increased restricted recovery time by 230 logical seconds. Other ablations changed false-conservative and legitimate-command-rejection behavior in replay/evidence-loss contexts. These are secondary n=32 sensitivity results and should not be promoted to primary confirmatory claims.

### RQ5 — Baselines and adversary-budget stress

In Block E, A3/K0 produced residual unauthorized state in all three policies (+1.0 versus A1/K0). `S2_B0_FAIL_CLOSED` and `S2_S1_EVIDENCE_AWARE` nevertheless reached evidence-qualified recovery under A3/K0, reinforcing that policy-visible qualification does not guarantee objective correctness when multiple producers are controlled.

Under the A2/K2 coupled producer-compromise/contact-loss profile, `S2_S1_EVIDENCE_AWARE` withheld recovery while `S2_B0_FAIL_CLOSED` recovered with an unsafe-permissive response. Any contrast involving A2/K2 is explicitly a coupled profile contrast and must not be described as an unconfounded adversary-only effect.

## Multiplicity and interpretation boundary

Holm rejection counts across the prespecified secondary families were:

- `B_CONTACT_VS_K0`: 28 / 96
- `B_K0_K3_ORDERED_TREND`: 7 / 24
- `B_POLICY_BY_CONTACT_INTERACTION`: 28 / 72
- `C_AMBIGUITY`: 0 / 54
- `D_ABLATION`: 10 / 96
- `E_STRESS_PROFILE`: 12 / 54
- `E_POLICY_WITHIN_PROFILE`: 9 / 36

Secondary blocks use 32 paired seeds and remain estimation/sensitivity evidence; they were not prospectively powered for small effects.

No global weighted score, global policy rank, operational spacecraft claim, RF claim, or real-link latency claim is supported by these results.

## Freeze rule

No statistical estimate, contrast definition, multiplicity result, or interpretation claim in this Phase-7 freeze may change without an explicit post-freeze amendment that preserves the frozen identity and explains the reason for the change. Study-1 empirical findings remain untouched.
