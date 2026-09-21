# Rebuilt Paper 4 Figure Plan

No figure may introduce a new scientific endpoint or post-hoc analysis.

## Figure 1 — Trusted-recovery state machine and policy semantics

Derive only from the frozen Study 8 protocol.

Show the common state progression:

`COMPROMISED -> RECOVERY_AUTHORITY_ESTABLISHED -> SUCCESSOR_CRYPTO_PROFILE_SELECTED -> SUCCESSOR_KEY_MATERIAL_STAGED -> TRANSITION_PROOF_ACCEPTED -> NEW_EPOCH_COMMITTED -> OLD_EPOCH_REVOKED -> TRUST_RESTORED`

Overlay predecessor/successor acceptance semantics for P0-P3 and identify P3's nominal pre-commit capacity guard.

## Figure 2 — Two evidence layers

Panel A: Study 8 logical 48-slot contact schedules and fixed byte budgets.

Panel B: Study 8E elapsed-time SatNOGS observation-opportunity windows with a solved hypothetical uniform effective payload-rate threshold.

Required visual note:

**No slot-to-seconds conversion. No pooled population. SatNOGS observation opportunity is not authenticated command contact.**

## Figure 3 — Study 8 fixed-capacity feasibility

Use frozen Study 8 values only.

Recommended panels:

- profile success: 93.7500%, 64.9306%, 61.8056%;
- contact-regime success for P1/P3: 79.1667%, 80.0926%, 76.8519%, 57.8704%.

## Figure 4 — Study 8E feasibility by horizon

Use frozen Results-002 values only:

- 6 h: 0.052863 finite;
- 12 h: 0.205947 finite;
- 24 h: 0.550661 finite.

Label the y-axis as **fraction of frozen extension cases with a finite modeled minimum-rate threshold**.

Do not label as operational success probability.

## Figure 5 — Cross-study burden interpretation

Conceptual synthesis only.

Left: fixed modeled capacity in Study 8 -> larger object bundle can reduce trusted-recovery success.

Right: solved-rate endpoint in Study 8E -> profile finite/non-finite classification is identical, while matched required-rate burden ordering is preserved in 21,792/21,792 comparisons.

Do not plot Study 8 success percentages and Study 8E rate-threshold fractions on one common quantitative axis.
