# WP10-G1 Claim-to-Evidence Matrix

**Date:** 2026-08-29  
**Status:** Locked manuscript-integration control  
**Upstream scientific authority:** `docs/28-wp10-integrated-findings-freeze.md`  
**Analysis artifact authority:** `docs/29-wp10-analysis-artifact-register.md`  
**Analysis population:** 720 frozen VALID campaign positions  
**Analysis-membership SHA-256:** `a2bf0c8f352f4386e74a500d97ea8f73e0c39d03bfe10ac0ebcf02470af9f70e`

## Purpose

This matrix is the manuscript-facing control that maps every material Results claim to the frozen WP10 evidence before prose drafting. It does not create new analysis, reinterpret raw campaign evidence, or strengthen any proposition beyond the integrated findings freeze.

A manuscript statement is admissible only when it can be traced to a claim row below or is plainly descriptive methodology already frozen elsewhere. New quantitative claims, new proposition semantics, weighted policy scores, post-hoc correctness labels, or operational-spacecraft generalizations require a separate evidence review before they may enter the manuscript.

## Claim classes

- `PRIMARY_NULL`: predeclared primary analysis did not support the proposition/effect.
- `PRIMARY_SUPPORTED`: predeclared analysis supports the bounded claim.
- `BOUNDED_SUPPORTED`: evidence supports a narrower selection/consequence or mechanism claim, but not a stronger causal/correctness interpretation.
- `CONDITIONAL_SUPPORTED`: effect/benefit exists only under specified experimental conditions; no universal ranking is implied.
- `SUPPORTING_SENSITIVITY`: robustness or supporting evidence; it may reinforce but not replace the primary conclusion.
- `LIMITATION`: observed boundary, structural zero, censoring, provenance, or external-validity constraint that must accompany interpretation.

## Claim-to-evidence matrix

| ID | Proposition / topic | Admissible manuscript claim | Frozen evidence / quantitative anchor | Claim class | Permitted Results wording | Prohibited escalation |
|---|---|---|---|---|---|---|
| C00 | Analysis population | WP10 analyzes exactly 720 frozen VALID positions from 24 cells × 30 seeds. | Membership SHA-256 `a2bf0c8f...`; WP9/WP10 freeze records. | LIMITATION | “The primary analysis included all 720 frozen VALID campaign positions.” | Do not include the 9 INVALID, pre-runtime, or quarantined attempts as analysis members. |
| C01 | P1 mission-state dependence | Mission-state dependence was not demonstrated on the predeclared P1 primary outcomes. | Applicable M01/M02/M03/M06 contrasts and interactions were exactly `0`. | PRIMARY_NULL | “The predeclared primary outcomes did not demonstrate mission-state-dependent policy effects in the tested P1 block.” | Do not rescue P1 with M07, exploratory patterns, or post-hoc endpoints. |
| C02 | P2 containment timing | A modeled missed contact window materially delayed P6 containment. | M04 RMST P6 C1−C0 `+10.0831 s`, 95% seed-block bootstrap CI `[9.8304, 10.3735]`. | PRIMARY_SUPPORTED | “Modeled missed contact increased P6 containment time by about 10.1 s.” | Do not call C1 real ground-station latency or operator-response delay. |
| C03 | P2 recovery timing | A modeled missed contact window materially delayed P6 verified recovery. | M05 RMST P6 C1−C0 `+10.4246 s`, 95% CI `[9.6567, 11.3598]`. | PRIMARY_SUPPORTED | “Modeled missed contact increased P6 verified-recovery RMST by about 10.4 s.” | Do not treat censored observations as observed recoveries. |
| C04 | P2 divergence timing | A modeled missed contact window materially increased P6 ground/spacecraft-state divergence duration. | M07 P6 C1−C0 `+10.0676 s`, 95% CI `[9.8438, 10.3260]`. | PRIMARY_SUPPORTED | “Modeled missed contact increased P6 state-divergence duration by about 10.1 s.” | Do not describe M07 as a measurement from a real ground/spacecraft link. |
| C05 | P2 P7 contact invariance | P7 timing was approximately unchanged by the modeled contact condition. | M04 P7 `−0.0425 s` CI `[-0.1977, 0.0899]`; M05 P7 `−0.1808 s` CI `[-0.7194, 0.2767]`; M07 P7 `−0.0390 s` CI `[-0.1690, 0.0709]`. | PRIMARY_SUPPORTED | “The autonomous P7 path was approximately invariant to the modeled contact condition on these timing endpoints.” | Do not claim mathematical invariance beyond the tested conditions. |
| C06 | P2 interaction | The contact effect differed strongly between P6 and P7. | Interaction: M04 `+10.1256 s` CI `[9.7859, 10.5176]`; M05 `+10.6054 s` CI `[9.5343, 11.9023]`; M07 `+10.1066 s` CI `[9.8135, 10.4499]`. | PRIMARY_SUPPORTED | “The modeled contact-delay effect was substantially larger for ground-authorized P6 than autonomous P7.” | Do not convert this into a universal P7-over-P6 superiority claim. |
| C07 | P6/P5 semantics | A16/A17 remain P6 cases; verified rollback occurs only after synthetic ground authorization delegates to the P5 mechanism. | Frozen design and integrated findings freeze; A16/A17 requested/effective policy P6. | LIMITATION | “P6 waited for modeled ground authorization and then delegated recovery action to the verified-rollback mechanism.” | Never relabel A16/A17 as P5 policy cases. |
| C08 | P3 evidence-dependent recovery | Degraded evidence produced a pronounced recovery vulnerability for P7 in E3/M4/C0. | A11 P7/T0 trusted recovery `30/30`; A13 P7/T1 trusted recovery `0/30`, recovery failed `30/30`. | PRIMARY_SUPPORTED | “Under degraded policy-visible evidence, P7 changed from 30/30 trusted recoveries to 0/30 in the tested E3 condition.” | Do not generalize to all evidence degradation or all satellite recovery systems. |
| C09 | P3 fixed P5 comparison | Fixed P5 retained trusted recovery under both T0 and T1 in the tested P3 block. | A14 P5/T0 trusted `30/30`; A15 P5/T1 trusted `30/30`. | PRIMARY_SUPPORTED | “Fixed P5 retained trusted recovery across both tested evidence conditions.” | Do not claim evidence quality can never affect fixed recovery outside this controlled block. |
| C10 | P3 anticipated mechanism absent | The narrower anticipated restoration-without-verification mechanism was not observed. | A13 terminated as recovery failure rather than operational restoration without verification. | PRIMARY_NULL | “The broader evidence-dependent vulnerability was observed, but the narrower restoration-without-verification mechanism was not.” | Do not report the predeclared mechanism as if it occurred. |
| C11 | P4 E1 selection pathway | Under E1/P7, degraded evidence changed the actual selected path from P2 restriction to P4 safe-mode action. | A04 P7/T0 → P2 / `RESTRICT_HIGH_RISK_COMMANDS`; A09 P7/T1 → P4 / `ENTER_SAFE_MODE`, deterministic `30/30` per cell. | BOUNDED_SUPPORTED | “Degraded evidence changed the observed P7 effective-policy/action pathway in E1.” | `ENTER_SAFE_MODE` is an experimental action, not proof of native spacecraft safe mode. |
| C12 | P4 E1 consequences | The E1 degraded-evidence P7 path reduced mission completion and increased legitimate-command rejection without observed safety-invariant violation or mission loss. | P7 T1−T0: M02 `−0.5`; M06 `+1.0`; M03 `0`; mission loss `0`. | BOUNDED_SUPPORTED | “The conservative E1 selection imposed measurable mission/rejection costs in the controlled model.” | Do not label the selected action objectively “incorrect.” |
| C13 | P4 E3 selection pathway | Under E3/P7, degraded evidence entered the `evidence_insufficient` basis and changed the path from P5 verified rollback to P2 restriction. | A11 P7/T0 → P5 rollback; A13 P7/T1 → P2 restriction; deterministic `30/30` per cell. | BOUNDED_SUPPORTED | “Degraded evidence changed the actual P7 selection pathway from rollback to restriction.” | Do not derive correctness from acceptance-only expected values. |
| C14 | P4 E3 consequences | The E3 degraded-evidence P7 path eliminated trusted recovery and produced recovery failure with lower mission completion. | Trusted `30/30 → 0/30`; recovery failed `0/30 → 30/30`; M02 `−0.5`; M03 `0`; mission loss `0`. | BOUNDED_SUPPORTED | “The selection change was associated with a complete shift from trusted recovery to recovery failure in this condition.” | Do not infer an independent objective incorrect-action oracle. |
| C15 | P4 safety boundary | No P4 run exhibited an observed M03 safety-invariant violation or mission-loss event. | P4 cells: M03 `0`; mission loss `0`. | LIMITATION | “No safety-invariant violation or mission-loss event was observed in the P4 block.” | Never write that the response is proven safe or cannot cause mission loss. |
| C16 | P5 overall structure | P7 exhibited condition-specific Pareto benefit, equivalence, and disadvantage; no universal policy winner exists. | P7 on point-estimate front in `5/9`; point-dominated groups G04, G05, G06, G09. | CONDITIONAL_SUPPORTED | “P7 produced condition-specific Pareto outcomes rather than universal superiority.” | Do not report `5/9` as a success rate or create a global rank. |
| C17 | P5 equivalence groups | G01–G03 primarily show empirical equivalence/delegation rather than incremental adaptive benefit. | G01 A02 tied A01; G02 A04 tied A03/A07; G03 A06 tied A05. | CONDITIONAL_SUPPORTED | “Several front memberships reflected equivalence with fixed-policy outcomes.” | Do not count these ties as adaptive wins. |
| C18 | P5 comparator-supported disadvantage | Marginal bootstrap intervals support comparator dominance over P7 in G04, G06, and G09. | G04 A08/P2 over A09/P7; G06 A15/P5 over A13/P7; G09 A22/P0 over A24/P7. | CONDITIONAL_SUPPORTED | “Comparator dominance was supported in three condition-specific comparisons.” | No simultaneous 95% Pareto-confidence claim; intervals are marginal. |
| C19 | P5 P7-supported benefit | Marginal bootstrap intervals support P7 dominance in selected comparisons. | G05 A11/P7 over A10/P2; G07 A18/P7 over A17/P6; G08 A21/P7 over A19/P0. | CONDITIONAL_SUPPORTED | “P7 dominance was supported in selected condition-specific comparisons.” | Do not generalize these pairwise results to all fixed policies. |
| C20 | P5 G05 nuance | P7/A11 is point-dominated by A14/P5 only through a small M05 RMST difference; marginal uncertainty does not support robust comparator dominance. | A11 M05 `3.9819393339 s`; A14 `3.8009359910 s`; marginal classification uncertain/tied. | CONDITIONAL_SUPPORTED | “G05 distinguished point-estimate Pareto status from inferential support.” | Do not state fixed P5 is conclusively faster based on this point estimate alone. |
| C21 | Provenance sensitivity | P5 conclusions are not driven by the ten VALID observations from the two earlier execution commits. | Final-commit complete blocks: seeds `10002`–`10030`, 29 seeds / 696 observations; all 9 front memberships, pairwise relations, and metric directions stable. | SUPPORTING_SENSITIVITY | “The P5 structure was unchanged in the final-commit complete-block sensitivity.” | Do not replace the 720-run primary analysis with the 696-run sensitivity. |
| C22 | Execution provenance | The 720 VALID observations span three historical execution commits and remain analytically exchangeable under the completed provenance review. | VALID distribution `1 / 9 / 710`; identical `shim_plan` AST SHA-256 `d933c537...`; no scientific-core/treatment/timing/metric-generation changes. | LIMITATION | “Execution provenance was retained explicitly and evaluated for analytical exchangeability.” | Do not state all 720 observations executed at `7ed85d5...`. |
| C23 | M05 censoring | Verified-recovery analysis uses explicit event status and administrative right censoring at 30 s. | `M05_verified_recovery_event`: 180 observed, 540 censored; all censored analysis times exactly `30 s`. | LIMITATION | “M05 used RMST with explicit event indicators and 30 s administrative censoring.” | Never interpret the 540 censored 30 s values as observed recoveries. |
| C24 | M03 structural zero | No safety-invariant violations were observed across the frozen 720-run analysis population. | M03 count `0` throughout locked extraction. | LIMITATION | “No M03 safety-invariant violation was observed.” | Do not infer impossibility, zero underlying risk, or guaranteed safety. |
| C25 | Global scientific interpretation | The evidence supports conditional mission-aware benefit, with contact delay and degraded evidence acting as important discriminators of response outcome. | Integrated P1–P5 findings, especially P2/P3/P4/P5. | CONDITIONAL_SUPPORTED | “Mission-aware response produced condition-specific benefits rather than universal superiority.” | Do not collapse P1–P5 into a single favorable narrative or weighted composite. |

## Results/Discussion firewall

The Results section may state only observed estimates, intervals, counts, Pareto relations, robustness checks, and bounded proposition outcomes from this matrix. It should not explain why the findings matter relative to prior literature, operational doctrine, spacecraft certification, human operator behavior, or real mission risk; those are Discussion tasks and require separate source support.

The Discussion may interpret the frozen findings, but it may not:

1. reverse the P1 null result;
2. convert P3’s absent narrower mechanism into an observed result;
3. call P4 selected actions objectively correct/incorrect without an independent oracle;
4. convert P5 into an overall policy ranking or weighted score;
5. relabel P6 A16/A17 as P5;
6. treat synthetic contact timing as real operator/ground-station timing;
7. state or imply real spacecraft access, RF interference/transmission, or native spacecraft safe-mode behavior;
8. state that all 720 observations executed at the final campaign commit.

## Quantitative citation rule

Every manuscript sentence containing a WP10 number must be traceable to this matrix and to one of the authoritative artifacts listed in `docs/29-wp10-analysis-artifact-register.md`. If a number cannot be traced, it is excluded until its provenance is established.

## Transition gate

WP10-G1 claim mapping is complete when:

- every major P1–P5 Results claim maps to a row above;
- every null, bounded, conditional, and sensitivity result retains its classification;
- no claim depends on an aborted analysis attempt;
- no weighted score/global policy rank is introduced;
- claim boundaries match `docs/28-wp10-integrated-findings-freeze.md`.

On that basis, the Results-section architecture is defined separately in `docs/31-wp10-g1-results-architecture.md`.
