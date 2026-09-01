## 4.9 Study 2: adversarial evidence-aware response and trusted recovery

Study 2 analyzed the complete frozen Phase-6 population of **3,872 VALID observations**, with **0 INVALID attempts** across **85 cells**. The frozen Phase-7 implementation produced 162 primary paired contrast rows and 432 prespecified secondary contrast rows. An independent arithmetic reproduction matched all numerical cell summaries, primary contrasts, secondary contrasts, Holm adjustments/rejection flags, and terminal-state distributions with zero mismatches.

### 4.9.1 RQ1 — evidence conditions and bounded partial compromise

Block A compared six frozen evidence profiles within policy using 96 paired seeds per cell. For `S2_B0_FAIL_CLOSED` and `S2_S1_EVIDENCE_AWARE`, V1 omission, V2 stale/replay, V3 contradiction, and V4 post-signature manipulation moved the response from the V0 recovery-gate attempt to restrictive/hold behavior. Under the frozen hidden prerequisites for this block, those changes reduced the adjudicated unsafe-permissive response rate by **1.0** relative to V0. `S2_B2_RISK_THRESHOLD` was already restrictive in the corresponding comparisons, so those contrasts were zero.

V5 exposed a different security boundary. A controlled policy-visible producer could generate evidence that remained authenticated/current enough for the recovery gate while being false relative to the research-only adjudication truth. Under V5, both `S2_B0_FAIL_CLOSED` and `S2_S1_EVIDENCE_AWARE` reached evidence-qualified trusted recovery in all 96 paired primary observations. Relative to V0, the evidence-qualified recovery-rate change was **+1.0** and the restricted recovery-time change was **−230 logical seconds**, yet the adjudicated unsafe-permissive rate under V5 remained **1.0**.

The result therefore does not mean that cryptographic authentication or evidence-qualified recovery failed as implemented. It shows that, under the bounded producer-compromise model, **policy-visible authenticity/currentness is not equivalent to objective correctness** when the producer itself is within the adversary budget. The verifier and research-only adjudication truth remained outside that budget.

Within Block A, the evidence-aware selector and fail-closed baseline had identical primary endpoint estimates. Relative to `S2_B2_RISK_THRESHOLD`, the evidence-aware selector was more permissive under V0 and V5; under V5 that permissiveness yielded evidence-qualified recovery while also carrying an unsafe-permissive difference of +1.0. These are endpoint-specific trade-offs and are not converted into a global policy ranking.

### 4.9.2 RQ2 — modeled contact and authorization constraints

At K0, `S2_B0_FAIL_CLOSED` and `S2_S1_EVIDENCE_AWARE` both reached evidence-qualified recovery at **10 logical seconds** with an unsafe-permissive rate of 0. Under K1, K2, K3, and K4, the evidence-aware selector initially restricted and then proceeded at the next frozen contact opportunity, reaching recovery at **25, 65, 185, and 30 logical seconds**, respectively, while retaining an unsafe-permissive rate of **0**.

The fail-closed baseline also eventually recovered at the modeled contact opportunities, but its initial permissive action while authorization was unavailable produced an unsafe-permissive increase of **+1.0 versus K0** at each non-K0 contact profile. Across the ordered K0–K3 series, its unsafe-permissive slope was **+0.3 per contact-severity step**, whereas the evidence-aware selector's slope was **0**.

K4 is not interpreted as severity level 4. It is the prospectively frozen intermittent/flapping-contact contrast and remains separate from the K0–K3 ordered trend. All reported times in this section are deterministic logical SIL times rather than measured network, orbital-access, operator, or spacecraft latencies.

### 4.9.3 RQ3 — structural label-invariance control

All **54** prespecified C-family endpoint contrasts were zero and **0/54** were rejected after Holm adjustment. This result has a deliberately narrow interpretation. Within each frozen Block-C ambiguity family, changing the `BENIGN`/`ADVERSARIAL` cause label does not alter hidden truth or the generated policy-visible evidence. The zero contrasts therefore verify **structural label invariance**: changing a non-operative analysis/adjudication label alone does not change the measured policy outcomes.

The Block-C result is **not** empirical evidence that the policies distinguish or fail to distinguish genuinely different benign and adversarial causal mechanisms. Testing that question would require a separate design in which the underlying causal mechanisms actually differ while the intended policy-visible ambiguity relationship is controlled.

### 4.9.4 RQ4 — contribution of policy-visible context

The Block-D ablations exposed specific context dependencies rather than one universally dominant input. In the unauthorized-command context, removing mission context or contact context increased the unsafe-permissive rate by **+1.0** relative to the full evidence-aware selector. In the update/recovery context, the security-only ablation reduced evidence-qualified recovery by **1.0** and increased restricted recovery time by **230 logical seconds**.

Other prespecified ablations changed false-conservative and legitimate-command-rejection behavior in replay/evidence-loss contexts. Because Block D used 32 paired seeds per cell, these results remain secondary estimation/sensitivity evidence and are not promoted to primary small-effect confirmatory claims.

### 4.9.5 RQ5 — baseline and adversary-budget stress

In Block E, the A3/K0 profile produced residual unauthorized state in all three evaluated policies, corresponding to a **+1.0** difference versus A1/K0. `S2_B0_FAIL_CLOSED` and `S2_S1_EVIDENCE_AWARE` nevertheless reached evidence-qualified recovery under A3/K0. This independently reinforces the RQ1 boundary: policy-visible recovery qualification does not guarantee objective correctness when multiple evidence producers are controlled within the frozen adversary budget.

Under the **A2/K2 coupled producer-compromise/contact-loss profile**, `S2_S1_EVIDENCE_AWARE` withheld recovery while `S2_B0_FAIL_CLOSED` recovered with an unsafe-permissive response. The profile is explicitly contact-coupled and is not reported as an unconfounded adversary-only effect.

### 4.9.6 Secondary multiplicity summary

Holm rejection counts for the prespecified secondary families were:

| Secondary family | Holm-rejected / tested |
|---|---:|
| `B_CONTACT_VS_K0` | 28 / 96 |
| `B_K0_K3_ORDERED_TREND` | 7 / 24 |
| `B_POLICY_BY_CONTACT_INTERACTION` | 28 / 72 |
| `C_AMBIGUITY` | 0 / 54 |
| `D_ABLATION` | 10 / 96 |
| `E_STRESS_PROFILE` | 12 / 54 |
| `E_POLICY_WITHIN_PROFILE` | 9 / 36 |

These counts summarize multiplicity-controlled secondary contrasts; they do not constitute a global policy score. No weighted global score or global policy rank was computed.

### 4.9.7 Study-2 result boundary

Study 2 extends the Study-1 evidence model without retroactively redefining Study 1. Study-1 T1 remains controlled omission/reduction of selected policy-visible fields. Study-2 V2–V5 separately instantiate stale/replayed, contradictory, post-signature-manipulated, and bounded producer-compromise conditions under their own frozen protocol.

The Study-2 results are software-in-the-loop findings. They do not establish flightworthiness, real RF or orbital-access performance, real operator timing, production incident-response effectiveness, or certification. They also do not identify one universally superior response policy. The strongest security result is instead a boundary condition: **recovery evidence must be evaluated in relation to the trustworthiness of the evidence-producing plane, not only the validity of the evidence presented to the verifier**.
