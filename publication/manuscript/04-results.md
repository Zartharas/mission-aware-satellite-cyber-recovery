# 4. Results

## 4.1 Frozen analysis population and endpoint integrity

The primary analysis used the complete frozen set of 720 VALID campaign positions, comprising 24 experimental cells with 30 campaign seeds per cell. The nine ledgered INVALID attempts, pre-runtime non-scientific abort evidence, and the quarantined never-ledgered interrupted attempt were retained for provenance and methods reporting but were not members of the statistical analysis population. No VALID observation was removed from the primary analysis.

The verified-recovery endpoint used an explicit event/censor representation. Across the 720 VALID observations, 180 runs contained an observed verified-recovery event and 540 were right-censored at the frozen 30-s administrative horizon. Censored analysis times were not interpreted as observed recoveries. The safety-invariant endpoint, M03, was structurally zero in the locked extraction: no frozen safety-invariant violation was observed in any of the 720 VALID runs. This absence of observed violations is reported descriptively and is not treated as evidence that violations are impossible outside the tested design.

Execution provenance was retained explicitly. Of the 720 VALID observations, 1 was executed at commit `aae2239753119c92e7633db3b6c73aee94c7b6dd`, 9 at `97074d0cdc4261de02bc6f618e891a88f45f9cfc`, and 710 at the final execution baseline `7ed85d5cbeca8f903b3468bc6ccc1c56e29c2446`. The analytical-exchangeability review found no change across these commits to the frozen scientific core, treatment/policy logic, event simulation, timing horizon, primary metric generation, or frozen configuration. The complete-block provenance sensitivity is reported in Section 4.7.

Table R1 summarizes the frozen population and proposition outcomes.

## 4.2 P1 — Mission-state dependence was not demonstrated on the predeclared primary outcomes

P1 evaluated whether response-policy value and cost differed materially by mission state using the predeclared primary outcomes M01 unauthorized-effect completion, M02 mission-objective completion, M03 safety-invariant violations, and M06 legitimate-command rejection. In the applicable P1 block, all retained policy-by-mission-state contrasts and interactions for these outcomes were exactly zero.

Accordingly, the predeclared primary outcomes did not demonstrate mission-state-dependent policy effects in the tested P1 block. The proposition was therefore not supported on its predeclared primary endpoints. No exploratory endpoint was substituted after the fact to reverse this conclusion.

## 4.3 P2 — Modeled contact delay selectively affected the ground-authorized recovery path

P2 tested the effect of one modeled missed-contact window on the ground-authorized P6 path relative to the autonomous P7 path. For M04 containment time, the restricted mean survival time (RMST) contrast for P6 under C1 versus C0 was +10.0831 s (95% seed-block bootstrap interval, 9.8304 to 10.3735 s). The corresponding P7 contrast was −0.0425 s (95% interval, −0.1977 to 0.0899 s). The P6-minus-P7 interaction was +10.1256 s (95% interval, 9.7859 to 10.5176 s).

The same pattern was observed for verified recovery. For M05 RMST through the frozen 30-s horizon, the P6 C1−C0 contrast was +10.4246 s (95% interval, 9.6567 to 11.3598 s), whereas the P7 contrast was −0.1808 s (95% interval, −0.7194 to 0.2767 s). The interaction was +10.6054 s (95% interval, 9.5343 to 11.9023 s).

Modeled ground/spacecraft state divergence, M07, showed a similar contact-dependent difference. The P6 C1−C0 contrast was +10.0676 s (95% interval, 9.8438 to 10.3260 s), the P7 contrast was −0.0390 s (95% interval, −0.1690 to 0.0709 s), and the interaction was +10.1066 s (95% interval, 9.8135 to 10.4499 s).

Thus, the modeled missed-contact condition materially increased containment, verified-recovery, and state-divergence duration for P6, while the P7 path was approximately unchanged on these endpoints. Figure R1 and Table R2 show the retained contrasts and intervals.

The contact condition was synthetic/modelled and should not be interpreted as measured operator latency, ground-station performance, or RF-link timing. A16 and A17 remained requested/effective P6 cases throughout analysis. P6 represented a ground-authorized WAIT policy; after modeled ground authorization, the recovery action delegated to the verified-rollback mechanism associated with P5. These P6 cells were not relabeled as P5 policy cases.

## 4.4 P3 — Degraded policy-visible evidence produced P7 recovery failure in the tested block

P3 examined whether trusted recovery depended on current policy-visible evidence rather than on behavioral restoration alone. In the retained E3/M4/C0 block, fixed P5 achieved trusted recovery in all 30 repetitions under full evidence (A14/T0) and all 30 repetitions under degraded evidence (A15/T1). P7 also achieved trusted recovery in all 30 full-evidence repetitions (A11/T0).

Under degraded evidence, however, P7 changed sharply. In A13/T1, trusted recovery occurred in 0 of 30 repetitions and recovery failed in 30 of 30. The contrast therefore was not a small reduction in recovery probability: in this controlled condition, the P7 path moved from complete trusted recovery under T0 to complete recovery failure under T1. Figure R2 and Table R3 summarize these retained outcomes.

The broader proposition that policy-visible evidence can materially affect trusted recovery was supported in this block. The narrower anticipated mechanism—nominal behavioral restoration without sufficient verification—was not observed in A13. Instead, the degraded-evidence P7 runs terminated as recovery failures. The absent narrower mechanism was retained as a null result rather than being inferred from the predeclared expectation.

## 4.5 P4 — Degraded evidence changed actual policy/action selection and downstream consequences

The P4 semantic audit bound each retained P4 run to actual execution metadata for the effective policy and selected action. Immutable experiment ground truth was not available to the runtime policy as a correctness oracle. The resulting evidence therefore supports observed selection/action pathways and their downstream consequences, not an independent post-hoc classification of actions as objectively correct or incorrect.

For E1 in mission state M2 under immediate modeled contact, full-evidence P7 (A04/T0) selected effective policy P2 and `RESTRICT_HIGH_RISK_COMMANDS`. The corresponding mission-objective completion ratio was 0.5 and the legitimate-command rejection rate was 0.0. Under degraded evidence (A09/T1), P7 selected effective policy P4 and the experimental action `ENTER_SAFE_MODE`. Mission-objective completion was 0.0 and legitimate-command rejection was 1.0. Relative to the full-evidence P7 condition, degraded evidence therefore changed M02 by −0.5 and M06 by +1.0. No M03 safety-invariant violation or mission-loss event was observed in either P7 E1 pathway.

For E3 in mission state M4, full-evidence P7 (A11/T0) selected effective P5 verified rollback and achieved trusted recovery in 30 of 30 repetitions with M02 = 1.0. Under degraded evidence (A13/T1), the selection basis explicitly entered `evidence_insufficient`, the effective policy changed to P2 restriction, trusted recovery fell to 0 of 30, recovery failure increased to 30 of 30, and M02 decreased to 0.5. No M03 safety-invariant violation or mission-loss event was observed in these P7 E3 cells.

Figure R3 displays the deterministic evidence-to-selection-to-consequence pathways, and Table R3 provides the underlying cell-level values. `ENTER_SAFE_MODE` is an experimental modeled response action in this software-in-the-loop environment; it is not evidence of a native spacecraft safe-mode implementation.

## 4.6 P5 — Mission-aware benefit was condition-specific rather than universal

P5 compared P7 with condition-matched fixed, ground-authorized, and recovery-policy alternatives using the five frozen Pareto dimensions M01 unauthorized-effect completion, M02 mission-objective completion, M03 safety-invariant violations, M05 verified-recovery RMST, and M06 legitimate-command rejection. No weighted score or global policy rank was computed.

At the point-estimate level, P7 was a Pareto-front member in five of the nine frozen comparison groups. This count is not a success rate because several front memberships reflected equivalence or delegation rather than incremental adaptive benefit.

In G01, P7/A02 delegated to effective P1 and was empirically tied with A01/P1. In G02, P7/A04 delegated to P2 and tied with A03/P1 and A07/P2. In G03, P7/A06 was tied with A05/P1. These three groups therefore provide evidence of equivalence rather than a distinct P7 advantage.

P7 was point-dominated in G04, G05, G06, and G09. In G04, A09/P7→P4 was dominated by A08/P2; marginal bootstrap intervals supported comparator dominance. In G06, A13/P7→P2 was tied with A12/P2 and dominated by A15/P5, with marginal intervals supporting comparator dominance versus A15. In G09, A24/P7→P4 tied with A23/P4 and was dominated by A22/P0, with marginal intervals supporting comparator dominance versus A22.

G05 was mixed. P7/A11→P5 dominated A10/P2 and A16/P6 at the point-estimate level, and marginal intervals supported P7 dominance versus A10/P2. However, A11 was point-dominated by A14/fixed P5 because M05 RMST was 3.9819393339 s for A11 versus 3.8009359910 s for A14 while the other Pareto dimensions were equal. The A11-versus-A14 marginal classification was uncertain/tied rather than robust comparator dominance.

The clearest positive P7 conditions were G07 and G08. In G07, P7/A18→P5 was the unique point-estimate Pareto-front member and dominated A17/P6; marginal intervals supported P7 dominance. In G08, P7/A21→P1 dominated A19/P0 and tied A20/P1; marginal intervals supported P7 dominance versus A19/P0.

Table R4 and Figure R4 summarize the group-level P7 relations. The retained P5 result therefore contains supported P7 advantages, empirical equivalence, mixed comparisons, and supported comparator advantages. No universal policy winner was observed or inferred.

## 4.7 Robustness and execution-provenance sensitivity

The primary analysis retained all 720 VALID observations despite their versioned execution provenance. The E0 review classified the observations as analytically exchangeable with versioned runtime-orchestration and finalization provenance because the scientific core, treatments, event simulation, timing horizon, primary metric generation, and frozen configuration did not change across the three execution commits.

A complete-block sensitivity restricted the comparison to campaign seeds 10002–10030, yielding 29 complete seeds and 696 observations, all executed at final commit `7ed85d5cbeca8f903b3468bc6ccc1c56e29c2446`. This sensitivity preserved each group's P7 point-estimate Pareto-front membership/non-membership classification across all 9 groups, every P7-versus-comparator point-estimate relation, and every primary-metric effect direction. The sensitivity therefore did not identify a provenance-driven change in the P5 conclusion.

The 696-observation analysis is a robustness check and does not replace the 720-observation primary population. Table S1 records the execution-provenance distribution and sensitivity results.

## 4.8 Results synopsis

Across the frozen campaign, the five propositions produced a deliberately non-uniform result pattern. P1 was not supported on its predeclared primary outcomes. P2 showed a strong modeled contact-delay effect on the ground-authorized P6 path but little corresponding change on the autonomous P7 path. P3 showed pronounced evidence-dependent recovery failure for P7, while the narrower anticipated restoration-without-verification mechanism was absent. P4 showed deterministic evidence-dependent changes in actual policy/action selection with measurable mission and recovery consequences, without supplying an independent correctness oracle. P5 showed condition-specific dominance, equivalence, disadvantage, and mixed outcomes rather than a universal policy winner.

Together, these results preserve the intended multi-objective structure of the experiment: security containment, mission continuity, recovery, command availability, and evidence quality did not collapse into a single performance ordering.