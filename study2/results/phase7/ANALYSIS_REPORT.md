# Study 2 Phase 7 Prespecified Statistical Analysis

## Analysis boundary

- Frozen Phase-6 observations analyzed: **3,872**.
- Invalid attempts: **0**.
- Recovery and containment time-to-event outcomes use restricted time at **240 s**.
- Primary Block-A contrasts are reported as paired effect sizes with 95% confidence intervals; no primary p-value gate is used.
- Secondary multiplicity is Holm-adjusted separately within each named contrast family and primary endpoint.
- No weighted global policy score or global policy rank is computed.

## RQ1 — Evidence conditions and partial compromise

Block A contributes 90 treatment-within-policy endpoint contrasts and 72 policy-within-profile endpoint contrasts. Interpret authenticated V5 evidence as policy-visible evidence, not as an objective correctness oracle.

## RQ2 — Contact and authorization constraints

K0–K3 are treated as the ordered contact series; K4 intermittent/flapping contact is reported separately. Policy-by-contact effects are paired difference-in-differences.

## RQ3 — Matched benign/adversarial ambiguity

C-family contrasts are adversarial minus benign under matched policy-visible evidence. Hidden cause labels are used only for adjudication/analysis.

## RQ4 — Context contribution

D-family estimates compare each prespecified context ablation with the full evidence-aware selector within the same context and paired seed.

## RQ5 — Baselines and adversary-budget stress

E-family stress estimates include A1/K0, A2/K2, and A3/K0 profiles. Any contrast involving A2/K2 is explicitly a coupled adversary/contact profile contrast, not an unconfounded adversary-only effect.

## Secondary multiplicity summary

- `B_CONTACT_VS_K0`: 28 Holm-rejected endpoint contrasts out of 96.
- `B_K0_K3_ORDERED_TREND`: 7 Holm-rejected endpoint contrasts out of 24.
- `B_POLICY_BY_CONTACT_INTERACTION`: 28 Holm-rejected endpoint contrasts out of 72.
- `C_AMBIGUITY`: 0 Holm-rejected endpoint contrasts out of 54.
- `D_ABLATION`: 10 Holm-rejected endpoint contrasts out of 96.
- `E_STRESS_PROFILE`: 12 Holm-rejected endpoint contrasts out of 54.
- `E_POLICY_WITHIN_PROFILE`: 9 Holm-rejected endpoint contrasts out of 36.

## Interpretation constraints

- Evidence-qualified trusted recovery is not identical to objectively safe recovery.
- The adjudication oracle was not a selector input.
- Secondary n=32 blocks are estimation/sensitivity blocks and are not claimed to be powered for small effects.
- No Study-1 empirical result is recalculated here.

Full estimates are in `cell_summary.csv`, `primary_contrasts.csv`, `secondary_contrasts.csv`, and `terminal_state_summary.csv`.
