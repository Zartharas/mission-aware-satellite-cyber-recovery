# WP10 Integrated Findings Freeze

**Freeze date:** 2026-08-29  
**Status:** Integrated P1–P5 findings locked for manuscript integration  
**Analysis population:** 720 frozen VALID campaign positions  
**Analysis-membership SHA-256:** `a2bf0c8f352f4386e74a500d97ea8f73e0c39d03bfe10ac0ebcf02470af9f70e`  
**Locked analysis extraction SHA-256:** `bf219d71162df708343f4be85bb258a083f5012e696c23619d0a46b7a2f2f265`

## Purpose

This record freezes the integrated WP10 scientific findings after completion of the predeclared P1–P5 analysis. It is the paper-facing bridge between the cryptographically frozen WP9 campaign and manuscript drafting.

This document does **not** replace the raw campaign evidence, the authoritative attempt ledger, the WP9 integrity freeze, or the retained local analysis outputs. It records the bounded conclusions and quantitative anchors that are permitted to propagate into the manuscript.

No new WP9 runtime, campaign seed consumption, campaign-data generation, raw-results mutation, imputation, weighted composite, or post-hoc replacement of observations by expectations is authorized or performed by this findings freeze.

## Frozen analysis authority

WP10 uses exactly the 720 VALID positions defined by the WP9 integrity freeze. The nine ledgered INVALID attempts, pre-runtime non-scientific abort evidence, and the quarantined never-ledgered interrupted attempt remain methods/provenance/limitations evidence and are not statistical-analysis members.

Execution provenance is retained rather than flattened:

| Execution commit | VALID observations |
|---|---:|
| `aae2239753119c92e7633db3b6c73aee94c7b6dd` | 1 |
| `97074d0cdc4261de02bc6f618e891a88f45f9cfc` | 9 |
| `7ed85d5cbeca8f903b3468bc6ccc1c56e29c2446` | 710 |

The execution-provenance equivalence review found no change to the frozen scientific core, treatment/policy logic, event simulation, timing horizon, primary metric generation, or frozen configuration across these execution commits. The apparent automated `shim_build_plan` failure was an audit-checker naming error: the actual function is `shim_plan`, and its AST SHA-256 is identical across all three commits:

`d933c537d745ab0554f46b326602f29f8877e1f8381bd60c28bfd04aed953749`

Accordingly, all 720 VALID observations remain in the primary analysis. A complete-block sensitivity using seeds `10002`–`10030` (29 seeds / 696 observations, all at final execution commit `7ed85d5...`) preserves all P5 Pareto-front memberships, pairwise Pareto relations, and metric directions.

## Analysis artifact identities

The following identities are retained as review anchors for the local WP10 analysis outputs:

- locked WP10 analysis extraction: `bf219d71162df708343f4be85bb258a083f5012e696c23619d0a46b7a2f2f265`
- WP10-E0-R1 output-manifest SHA-256: `3c4b141352c8ce9f2341cbc3acb2b6f5f0e7f97847fcc19f258ba1c2dc90eeb4`
- WP10-D2-R1 P4 output-manifest SHA-256: `b3239968b596edf1183f4ad6b93a34cf317a794ab86920a775d1e1e9045ad9ff`
- WP10-D2-R1 locked P4 table SHA-256: `f848a448cc75818d37a7827df9e8936ff7a4bf60075ca25b102e858df7f56af3`
- WP10-F-R3 P5 output-manifest SHA-256: `c31b357cb454ed96d60708f96b27e1993ef002b76a3cd36d90d36a437b3cbc9c`

The initial WP10-D2 provenance attempt and WP10-F-R1/R2 attempts are non-authoritative aborted analysis-script attempts. They produced no replacement scientific result. The retained authoritative P4 result is D2-R1; the retained authoritative P5 result is F-R3.

## Proposition findings freeze

| Proposition | Frozen finding | Manuscript status |
|---|---|---|
| P1 — mission-state dependence | Predeclared M01/M02/M03/M06 mission-state policy contrasts and interactions were exactly zero. Mission-state dependence was not demonstrated on the predeclared primary outcomes. | **Not supported on predeclared primary outcomes** |
| P2 — contact-delay effect | Modeled missed-contact delay strongly increased containment, verified-recovery, and ground/spacecraft divergence time under P6, while the autonomous P7 path remained approximately unchanged. All relevant P2 cells ultimately reached trusted recovery. | **Strongly supported for timing/divergence effects** |
| P3 — evidence requirement | Degraded evidence caused a strong recovery vulnerability for P7: full-evidence P7 recovered successfully, while degraded-evidence P7 failed recovery in all 30 repetitions. The narrower anticipated restoration-without-verification mechanism was not observed. | **Supported in a narrower evidence-dependent recovery form** |
| P4 — degraded-evidence policy/action effect | Degraded evidence changed actual effective-policy/action pathways and downstream outcomes. The evidence supports selection/consequence effects, not an objective post-hoc label of “incorrect action.” | **Supported with bounded semantics** |
| P5 — conditional mission-aware benefit | P7 could dominate, tie, or be dominated depending on the exact event/mission/contact/evidence condition. Five of nine groups placed P7 on the point-estimate Pareto front, but several were ties/delegation-equivalence cases. No universal policy winner exists. | **Conditionally supported** |

## P1 — mission-state dependence

P1 used the predeclared primary outcomes M01, M02, M03, and M06. The applicable P1 contrasts and interactions were exactly zero across the frozen campaign.

The manuscript must therefore state that the experiment **did not demonstrate mission-state dependence on the predeclared P1 primary endpoints**. M07 or other exploratory structure must not be used to rescue the proposition after the fact.

## P2 — modeled contact-delay effect

The contact condition is synthetic/modelled; it is not a measurement of real ground-station contact or operator response latency.

Primary RMST contrasts through the frozen 30 s horizon:

### M04 containment time

- P6, C1 − C0: `+10.0831 s`, 95% seed-block bootstrap CI `[9.8304, 10.3735]`
- P7, C1 − C0: `-0.0425 s`, 95% CI `[-0.1977, 0.0899]`
- interaction: `+10.1256 s`, 95% CI `[9.7859, 10.5176]`

### M05 verified-recovery time

- P6, C1 − C0: `+10.4246 s`, 95% CI `[9.6567, 11.3598]`
- P7, C1 − C0: `-0.1808 s`, 95% CI `[-0.7194, 0.2767]`
- interaction: `+10.6054 s`, 95% CI `[9.5343, 11.9023]`

### M07 ground/spacecraft divergence

- P6, C1 − C0: `+10.0676 s`, 95% CI `[9.8438, 10.3260]`
- P7, C1 − C0: `-0.0390 s`, 95% CI `[-0.1690, 0.0709]`
- interaction: `+10.1066 s`, 95% CI `[9.8135, 10.4499]`

Interpretation is bounded to the controlled synthetic contact model: the missed modeled contact window materially delays P6 recovery timing because P6 waits for modeled ground authorization before delegating to verified rollback. P7 does not wait on that authorization gate.

### P6/P5 terminology boundary

A16/A17 remain **P6 requested/effective policy** cases. P6 is the ground-authorized WAIT policy. After synthetic ground authorization it delegates recovery action to the P5 verified-rollback mechanism. These cells must not be relabeled as P5 in the manuscript.

## P3 — evidence-dependent recovery

The key retained E3/M4/C0 comparison is:

- A14, fixed P5 / T0: trusted recovery `30/30`
- A15, fixed P5 / T1: trusted recovery `30/30`
- A11, P7 / T0: trusted recovery `30/30`
- A13, P7 / T1: trusted recovery `0/30`; recovery failed `30/30`

For P7, degraded evidence therefore changes the recovery outcome from fully trusted recovery to complete recovery failure in this controlled condition. M07 also shows a large evidence-sensitive divergence effect for P7, whereas the fixed P5 path remains approximately unchanged.

The predeclared narrower “behavior restored but verification absent” mechanism was not observed in A13; the failure was stronger and terminated as recovery failure. The paper must distinguish the supported broader evidence-dependence claim from the absent narrower mechanism.

## P4 — degraded-evidence selection and consequences

The P4 semantic audit confirmed that the retained campaign contains actual effective-policy and selected-action metadata for all 240 P4 runs. Immutable ground truth was not used as a runtime correctness oracle.

Observed selection pathways were deterministic within each cell (`30/30`). Key degraded-evidence changes include:

### E1

Under P7, degraded evidence changes the path from P2 / `RESTRICT_HIGH_RISK_COMMANDS` to P4 / `ENTER_SAFE_MODE`.

Relative to full evidence, the degraded-evidence P7 cell shows:

- M02 mission-objective completion: `-0.5`
- M06 legitimate-command rejection: `+1.0`
- no M03 safety-invariant violation
- no mission-loss event

### E3

Under P7, degraded evidence explicitly enters the `evidence_insufficient` selection basis and changes the effective path from P5 verified rollback to P2 restriction.

Relative to full evidence:

- trusted recovery: `30/30 → 0/30`
- recovery failed: `0/30 → 30/30`
- M02 mission-objective completion: `-0.5`
- no M03 safety-invariant violation
- no mission-loss event

The supported claim is therefore that degraded evidence **changes actual policy/action selection and downstream mission/recovery consequences**. The data do not contain an independent objective “incorrect-policy-action” oracle, so the paper must not manufacture that label from acceptance-only expectations.

## P5 — condition-specific Pareto findings

P5 follows the frozen G01–G09 comparison groups in `docs/18-wp9a-final-campaign-design.md`. The primary Pareto dimensions are M01 unauthorized-effect completion, M02 mission-objective completion, M03 safety-invariant violations, M05 verified-recovery RMST, and M06 legitimate-command rejection. No weighted score or global policy rank is permitted.

### P7 point-estimate Pareto status

| Group | P7 cell | P7 effective policy | P7 on front | Frozen interpretation |
|---|---|---|---|---|
| G01 | A02 | P1 | Yes | empirical tie with A01/P1 |
| G02 | A04 | P2 | Yes | empirical ties with A03/P1 and A07/P2 |
| G03 | A06 | P2 | Yes | empirical tie with A05/P1 |
| G04 | A09 | P4 | No | dominated by A08/P2 |
| G05 | A11 | P5 | No | dominates A10/P2 and A16/P6; point-dominated by A14/P5 |
| G06 | A13 | P2 | No | tied with A12/P2; dominated by A15/P5 |
| G07 | A18 | P5 | Yes | unique front member; dominates A17/P6 |
| G08 | A21 | P1 | Yes | dominates A19/P0; ties A20/P1 |
| G09 | A24 | P4 | No | tied with A23/P4; dominated by A22/P0 |

P7 is on the point-estimate Pareto front in `5/9` groups and point-dominated in G04, G05, G06, and G09. The `5/9` count must not be presented as a success rate: G01–G03 are principally equivalence/delegation cases rather than evidence of incremental adaptive benefit.

### Bootstrap-supported P5 comparisons

Marginal seed-block bootstrap intervals support comparator dominance in:

- G04: A08/P2 over P7/A09
- G06: A15/P5 over P7/A13
- G09: A22/P0 over P7/A24

Marginal intervals support P7 dominance in:

- G05: P7/A11 over A10/P2
- G07: P7/A18 over A17/P6
- G08: P7/A21 over A19/P0

G05 P7/A11 is point-dominated by A14/P5 because M05 RMST is `3.9819393339 s` versus `3.8009359910 s`, with the other Pareto dimensions equal; however the corresponding marginal bootstrap classification is uncertain/tied rather than robust comparator dominance.

### P5 provenance sensitivity

The 29-seed final-execution-commit complete-block sensitivity (`10002`–`10030`, 696 observations) preserves:

- P7 Pareto-front membership in all `9/9` groups;
- every P7-versus-comparator point-estimate relation; and
- every primary-metric effect direction.

Thus the P5 conclusion is not driven by the ten VALID observations executed on the two earlier provenance commits.

## Integrated scientific interpretation

The combined result is not a universal-superiority claim. The controlled experiment supports a more precise conclusion:

> Mission-aware response produced condition-specific benefits rather than universal superiority. Context-sensitive selection improved mission/security outcomes in some conditions, was equivalent to fixed alternatives in others, and was dominated in several conditions. Contact delay and degraded evidence were particularly important discriminators of when adaptive or ground-dependent recovery paths succeeded or failed.

This conditional result is scientifically preferable to a forced single policy ranking because it preserves the original multidimensional mission/security trade-off design.

## Claim boundaries and limitations

The following boundaries are mandatory for manuscript use:

1. **Controlled academic software-in-the-loop environment.** The experiment is a NOS3/Fortytwo-based controlled simulation/test environment; it is not a test against an operational spacecraft.
2. **No RF interference/transmission claim.** No result should be described as real RF attack, interference, jamming, or spacecraft transmission behavior.
3. **No native spacecraft safe-mode claim.** `ENTER_SAFE_MODE` is an experimental response action in the controlled model, not evidence of a native flight-vehicle safe-mode implementation.
4. **Synthetic ground/contact timing.** C1 represents one modeled missed contact window; it is not real operator or ground-station timing data.
5. **Ground truth is not a runtime policy oracle.** Immutable ground truth is retained for analysis/validation separation and does not provide policy-visible runtime correctness information.
6. **No imputation of primary outcomes.** Censored M04/M05 outcomes remain right-censored through the frozen 30 s horizon.
7. **M03 structural zero.** No safety-invariant violations were observed; this is not proof that such violations are impossible. Report exact counts/upper bounds rather than a manufactured regression effect.
8. **P4 correctness boundary.** The data support actual selection/action and observed-consequence differences, not an objective post-hoc “incorrect action” label.
9. **P5 has no weighted composite.** Pareto conclusions are condition-specific and multidimensional; no overall score or universal winner may be added later for convenience.
10. **Execution provenance remains explicit.** Do not state that all 720 observations executed at the final `7ed85d5...` commit.

## Manuscript-ready proposition language

Use the following bounded wording as the default results framing:

- **P1:** “The predeclared primary outcomes did not demonstrate mission-state-dependent policy effects in the tested P1 block.”
- **P2:** “A modeled missed contact window materially delayed ground-authorized P6 containment, trusted recovery, and state convergence, whereas the autonomous P7 path was approximately invariant to the modeled contact condition.”
- **P3:** “Degraded policy-visible evidence produced a pronounced recovery vulnerability for the adaptive P7 path in the tested E3 condition, although the narrower anticipated restoration-without-verification mechanism was not observed.”
- **P4:** “Degraded evidence changed the actual selected policy/action pathway and downstream mission/recovery outcomes; the experiment does not provide an independent oracle for labeling those selected actions objectively correct or incorrect.”
- **P5:** “Mission-aware P7 exhibited condition-specific Pareto benefits rather than universal superiority, with dominance, equivalence, and disadvantage all observed across the frozen comparison groups.”

## Transition to manuscript integration

With P1–P5 now analyzed and integrated, WP10 transitions from statistical analysis to manuscript integration. The next repository-facing work should:

1. map this frozen findings register into Results subsections without changing proposition semantics;
2. update WP1–WP3 final-review language against the observed empirical record;
3. draft figures/tables from the locked analysis outputs with reproducible source identities;
4. write Discussion around the supported, unsupported, and bounded findings rather than only positive results;
5. preserve the controlled-environment and provenance limitations above; and
6. defer Zenodo DOI insertion until the WP11 archive package is uploaded and checksum-verified.

The raw `results/wp9/campaign` tree remains untouched and ignored by Git. This findings freeze is documentation/governance only.
