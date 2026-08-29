# WP10-G2 Empirical Reconciliation of WP1, WP2, and WP3

**Date:** 2026-08-29  
**Status:** Post-results reconciliation locked for manuscript integration  
**Upstream findings authority:** `docs/28-wp10-integrated-findings-freeze.md`  
**Claim control:** `docs/30-wp10-g1-claim-to-evidence-matrix.md`  
**Results architecture:** `docs/31-wp10-g1-results-architecture.md`

## Purpose

This document reconciles the pre-experiment literature/novelty framing (WP1), theoretical/conceptual model (WP2), and threat/mission model (WP3) against the frozen WP10 empirical findings. It is a post-results interpretive overlay; it does not rewrite the historical preregistration-like design record in `docs/01`, `docs/07`, `docs/08`–`docs/12`, or the frozen WP9 design.

The reconciliation follows one rule: **null, adverse, or narrower-than-expected findings change the manuscript interpretation rather than being explained away or replaced by post-hoc endpoints.**

No new runtime, data generation, endpoint, model fit, weighted score, p-value, or valid-run exclusion is introduced here.

## Executive reconciliation

| Work package | Pre-results expectation | Frozen empirical result | Reconciled manuscript position |
|---|---|---|---|
| WP1 — literature/novelty | A controlled satellite response-policy experiment would expose mission-state, contact, evidence, and recovery trade-offs. | Contact and evidence strongly discriminate outcomes; mission-state dependence was not demonstrated on P1 primary endpoints; P7 benefit is conditional rather than universal. | Novelty rests on the **comparative experimental method and conditional multi-objective evidence**, not on proving every proposed contextual factor matters. |
| WP2 — theory/concept | Mission Aware + FDIR/resilience + trusted-evidence framing would explain response value across mission context. | P1 mission-state interaction is null; P2 contact timing, P3/P4 evidence dependence, and P5 conditional trade-offs are supported. | The framework remains a **design and interpretation lens**, but the experiment does not validate a general mission-state-dependence claim. |
| WP3 — threat/mission model | Adversarial events, contact constraints, degraded evidence, safety/trust invariants, and recovery criteria would expose harmful or ineffective response choices. | Evidence degradation changes actual P7 selection and recovery outcomes; modeled contact delays P6; M03 is structural zero; no independent “incorrect action” oracle exists. | Threat/mission framing is retained with tighter semantics: **selection/consequence**, modeled contact, experimental safe-mode action, and bounded invariant claims. |

# WP1 — Literature and novelty reconciliation

## What survives unchanged

The original WP1 reviewer challenge was correct that the paper cannot claim novelty for:

- Mission Aware cybersecurity itself;
- state-aware spacecraft FDIR;
- safe mode or cyber-safe mode;
- autonomous recovery;
- satellite cybersecurity testbeds;
- NOS3/cFS event injection;
- anomaly detection;
- general cyber-resilience engineering.

The retained contribution is still a comparative experiment rather than a new general theory or a new flight architecture.

## What must change after the empirical results

### 1. Mission-state dependence is no longer part of the positive novelty claim

WP1 originally treated mission-state-dependent policy effects as one expected differentiator. P1 produced exactly zero predeclared M01/M02/M03/M06 policy-by-state contrasts/interactions in the applicable block.

Therefore the manuscript may say that the experiment **varied mission state as a controlled spacecraft context**, but it must not imply that the study demonstrated mission-state-dependent cyber-response effects.

The null result is itself part of the experimental contribution: a spacecraft-specific factor that appeared theoretically important did not affect the predeclared P1 endpoints in the tested design.

### 2. Contact constraint is empirically important, but only as modeled timing

P2 strongly supports a contact-dependent timing effect for ground-authorized P6. The effect is approximately +10 s on containment, verified recovery, and state-divergence RMST/duration contrasts under the single modeled missed-contact condition, while P7 is approximately unchanged.

The novelty claim may therefore include **intermittent-contact-aware comparative evaluation**, but not real operator latency, real ground-station performance, or RF-link behavior.

### 3. Evidence quality is a stronger empirical discriminator than originally expected

P3/P4 show that degraded policy-visible evidence materially changes P7 recovery and action-selection pathways in the tested E3/E1 conditions. This strengthens the trusted-evidence portion of the contribution.

However, the paper must distinguish:

- actual evidence-dependent selection/consequence differences, which are observed; from
- objective “wrong” or “unsafe” action labels, which are not available as an independent oracle.

### 4. P5 matches the defensible novelty hypothesis

The strongest original WP1 hypothesis was that mission-aware response could improve the security–mission Pareto frontier without dominating every baseline. The frozen result is consistent with that bounded prediction:

- P7 is on the point-estimate Pareto front in 5/9 groups;
- several front memberships are ties/delegation equivalence rather than incremental benefit;
- P7 is point-dominated in G04, G05, G06, and G09;
- bootstrap-supported P7 advantages and comparator advantages both occur.

This is better framed as **condition-specific comparative evidence** than as an adaptive-policy performance claim.

## Reconciled novelty statement

Use this as the default manuscript novelty statement pending journal-specific editing:

> We present a reproducible software-in-the-loop experimental method for comparing fixed, ground-authorized, recovery, and mission-aware satellite cyber-response policies under frozen event, mission-state, evidence, and contact conditions. The study evaluates security containment, mission completion, safety-invariant outcomes, legitimate-command rejection, and verified trusted recovery separately, and reports conditions in which adaptive response is beneficial, equivalent, or worse than simpler alternatives.

This statement intentionally does **not** claim that mission awareness, autonomy, safe mode, trusted recovery, or satellite cyber testbeds are individually new.

## WP1 falsification criteria — post-results disposition

| Original criterion | Empirical disposition | Manuscript consequence |
|---|---|---|
| Mission-aware policy does not materially differ from a static baseline | Partly falsified as a universal expectation: P7 ties several static/delegated alternatives, but also differs materially in G04–G09 comparisons. | Report conditional differentiation, not universal advantage. |
| Results depend on one arbitrary weighting scheme | Not triggered. No P5 weighted score was computed. | Preserve separate endpoints/Pareto analysis. |
| Trusted-recovery evidence does not change conclusions | Not triggered. P3/P4 evidence condition materially changes P7 recovery/selection. | Trusted-evidence contribution retained. |
| Contact delay and mission state do not alter policy outcomes | Mixed: contact delay matters strongly; mission-state dependence is not demonstrated on P1 primary endpoints. | Split the claim; do not bundle contact and mission state into one positive statement. |
| Same conclusions arise without spacecraft-specific constraints | Not established by this experiment. | Treat spacecraft specificity as a bounded design context, not proof of uniqueness. |
| Results cannot be reproduced from pinned snapshots/seeds | Not triggered. Frozen membership, provenance, checksums, and seed-block sensitivity are retained. | Reproducibility contribution retained. |

# WP2 — Theoretical and conceptual reconciliation

## Mission Aware lens

Mission Aware remains the primary systems-theoretic lens for connecting mission requirements, system functions, attack paths, and unacceptable losses. The experiment used that lens to structure mission objectives, invariants, controlled contexts, and policy trade-offs.

**Important boundary:** P1 does not empirically validate a general proposition that cyber-response value is mission-state dependent. The framework remains useful even though this particular prediction was unsupported on the predeclared P1 outcomes.

In the manuscript, Mission Aware should therefore be described as a **design/analysis lens**, not a theory “confirmed” by the experiment.

## FDIR and resilience lens

The FDIR/resilience lens is supported as operational vocabulary rather than a novel contribution. P2 shows a clear distinction between ground-authorized waiting and autonomous recovery timing under modeled contact loss. P3/P4 show why nominal operation or a selected recovery action is insufficient without current trust evidence.

The manuscript should distinguish cyber-originated evidence/authorization problems from ordinary non-adversarial spacecraft fault management.

## Governance/evidence lens

The evidence lens becomes more central after the results:

- trusted recovery is an evidence-qualified terminal state, not merely behavioral restoration;
- M05 uses an explicit event/censor indicator and 30 s administrative horizon;
- degraded evidence changes P7 selection/recovery in the tested conditions;
- immutable experiment ground truth is never a runtime policy oracle.

NIST CSF/RMF should remain governance/evidence structures, not causal explanations for the observed effects.

## Construct reconciliation

### Mission continuity
Retain. Operationalized primarily through frozen mission-objective completion and command-rejection outcomes. Do not imply that all real mission functions are represented.

### Cyber containment
Retain. Report event-specific modeled unauthorized-effect termination/completion and containment timing only.

### Trusted recovery
Retain and strengthen. The empirical program demonstrates why trusted recovery must be tied to current evidence and terminal-state criteria rather than nominal behavior alone.

### Mission-aware response
Retain as the definition of P7’s context-sensitive selection mechanism. Do not redefine “mission-aware” to mean empirically superior.

### Recovery confidence
Use cautiously. The study operationalizes evidence completeness/freshness and verified terminal states, but does not estimate a universal scalar “confidence” score.

## Proposition reconciliation

- **P1:** unsupported on predeclared primary outcomes; do not rescue with M07.
- **P2:** strongly supported for modeled contact-delay timing/divergence effects.
- **P3:** supported in the broader evidence-dependent recovery form; the narrower restoration-without-verification mechanism was absent.
- **P4:** supported for degraded-evidence selection/action and downstream consequences; objective correctness labeling is not supported.
- **P5:** conditionally supported; no universal policy winner.

# WP3 — Threat and mission model reconciliation

## Threat-model elements confirmed by the campaign

The red-team requirement to separate immutable ground truth, spacecraft/ground observed state, policy-visible state, and recovery evidence was scientifically necessary and remains a central validity control. P4 analysis confirmed actual policy-visible selection pathways without using ground truth as a policy oracle.

The following modeled concerns produced discriminating evidence:

- degraded/suppressed policy-visible evidence;
- compromised-update recovery context;
- ground/spacecraft state divergence;
- one modeled missed-contact window;
- ground-authorized versus autonomous response timing;
- conservative evidence-insufficient behavior.

## Threat-model elements requiring narrower wording

### Contact condition
C1 is a **controlled modeled contact condition**, not necessarily an adversary-caused link attack. The pre-experiment threat model allowed an adversary to “cause contact or data delay,” but the manuscript must describe the retained C1 experiment according to the implemented frozen design: one synthetic/modelled missed-contact window.

### Safe mode
`ENTER_SAFE_MODE` is an experimental response action. It cannot be presented as a native spacecraft safe-mode implementation or as operational evidence that a real vehicle entered safe mode.

### Incorrect/unsafe action
The pre-experiment P4 traceability listed “incorrect policy action.” The final campaign contains actual effective-policy/action metadata and consequences but no independent objective correctness oracle. Manuscript terminology must use **selection/action pathway**, **evidence-insufficient fallback**, and **observed consequence**, not post-hoc “incorrect action.”

### Safety invariants
M03 is zero across all 720 VALID runs. This supports the statement that no frozen safety-invariant violations were observed. It does not demonstrate that the policies are inherently safe or formally verified.

### Mission loss
No mission loss occurred in the P4 cells. Negative mission consequences are instead visible through mission-objective completion, legitimate-command rejection, recovery failure, and timing/divergence outcomes.

## Specific invariant/construct dispositions

- **SI-7 minimum observability:** empirically exercised. In A13, degraded evidence causes the P7 selection basis to enter `evidence_insufficient` in 30/30 repetitions and changes the effective path from P5 rollback to P2 restriction.
- **SI-8 immutable ground truth:** retained as an experimental validity boundary, not a runtime control available to P7.
- **Ground/spacecraft convergence:** empirically relevant through M07 and P2 contact-delay effects.
- **Verified recovery image / trust evidence:** relevant to the E3/P5 recovery pathway and P3 evidence distinction.
- **Energy/survivability invariants:** no M03 violations were observed; do not infer broad spacecraft survivability assurance.

## P6/P5 reconciliation

The early Gate 1 policy list predates the bounded P6 extension. Final manuscript semantics follow the frozen WP9/WP10 authority:

- A16/A17 are requested/effective **P6** cases;
- P6 is ground-authorized WAIT;
- after modeled ground authorization, P6 delegates the verified rollback action/mechanism associated with P5;
- A16/A17 must never be relabeled as P5 policy cases.

## Weighted-score reconciliation

`docs/10-frozen-study-boundaries.md` historically allowed a weighted composite only as a possible secondary sensitivity analysis. The later frozen P5 contract and completed WP10-F-R3 analysis supersede that optional path for manuscript reporting:

- no weighted P5 score was computed;
- no global policy ranking was computed;
- all primary outcomes remain separate;
- P5 is reported through condition-specific Pareto relations and marginal seed-block bootstrap intervals.

The historical Gate 1 wording remains untouched as part of the design record; this reconciliation is the post-results manuscript authority.

# Research-question reconciliation

| Research question | Empirical answer boundary |
|---|---|
| RQ1 — response effectiveness | Response effectiveness is condition-specific. P7 can dominate, tie, or be dominated; no universal winner is supported. |
| RQ2 — mission-state cost | Mission-state dependence was not demonstrated on P1 predeclared primary endpoints. Mission costs are observed in condition-specific P4/P5 comparisons, but they must not be relabeled as a P1 mission-state effect. |
| RQ3 — contact delay | Strongly supported as a modeled timing/divergence effect for ground-authorized P6 relative to autonomous P7. |
| RQ4 — harmful automation | Supported conditionally through P4/P5 cases where adaptive P7 incurs mission/rejection/recovery disadvantages; no safety-invariant violation or mission-loss claim is needed. |
| RQ5 — trusted-state evidence | Supported in the broader evidence-dependent recovery/selection sense; the narrower nominal-restoration-without-verification mechanism was not observed. |

# Manuscript-level contribution hierarchy after reconciliation

## Primary contribution

A reproducible controlled software-in-the-loop **comparative evaluation method and outcome dataset** for satellite cyber response and trusted recovery under frozen contact/evidence/mission/event contexts.

## Secondary contribution

Empirical evidence that modeled contact constraints and degraded policy-visible evidence can materially change recovery timing, policy selection, and recovery terminal outcomes.

## Conditional contribution

Evidence that mission-aware selection can improve, match, or underperform simpler policies depending on condition; no universal policy superiority.

## Supporting contribution

A version-pinned, integrity-frozen experimental workflow with explicit invalid-attempt retention, execution-provenance accounting, right-censoring, and sensitivity analysis.

# G2 disposition

- WP1 literature/novelty: **empirically reconciled; publication-era refresh recorded separately in `docs/33-wp10-g2-publication-era-literature-refresh.md`**.
- WP2 theoretical/conceptual model: **empirically reconciled; P1 null explicitly retained**.
- WP3 threat/mission model: **empirically reconciled; claim/semantic corrections locked**.
- Historical pre-experiment documents remain unchanged.
- Next phase: **WP10-G3 publication tables and figures**, generated only from already frozen estimands/results.