# Study 2 Design Candidate — Secure Response Under Partial and Adversarial Observation

> **Historical/superseded planning record.** This document preserves the pre-freeze design-candidate thinking and must not be read as the current Study-2 status. Study 2 was subsequently prospectively frozen, executed as a 3,872-VALID / 85-cell campaign, analyzed in Phase 7, independently reproduced with 0 mismatches, and canonically closed. Current authority is `study2/PHASE7_RESULTS_FREEZE.json`, `study2/PHASE7_PROVENANCE.json`, and `study2/docs/PHASE7_RESULTS_FREEZE.md`. The historical candidate text below is retained for provenance.

## Historical status at time of this document

`DESIGN_ONLY_NOT_RUNTIME_AUTHORIZED_NOT_FROZEN`

This document defines a candidate follow-on study motivated by the limitations of Study 1 and by the scope expectations of higher-bar security/dependability venues. It does **not** authorize runtime execution, consume campaign seeds, alter the Study 1 population, or modify the Study 1 Zenodo record.

## Primary research positioning

**Primary venue class:** IEEE Transactions on Dependable and Secure Computing (TDSC)  
**Strong alternative:** ACM Transactions on Privacy and Security (TOPS)  
**Engineering-validation follow-on:** IEEE Transactions on Aerospace and Electronic Systems (TAES) / AIAA Journal of Aerospace Information Systems (JAIS)

The intended contribution is broader than the Study 1 question of how specific frozen response policies behaved in one satellite SIL campaign. Study 2 asks a more general systems-security question:

> **Under partial, stale, contradictory, or adversarially manipulated observation and intermittent connectivity, when can a cyber-response policy preserve security, availability, safety, and evidence-qualified recoverability?**

The satellite testbed remains the empirical case study, but the security/dependability model should be applicable to other intermittently connected cyber-physical systems.

## Design principles inherited from Study 1

Study 2 should retain the governance strengths that made Study 1 reproducible:

- estimand-driven frozen cells rather than a blind full factorial;
- predeclared hypotheses/primary outcomes;
- fixed campaign seeds and blocked analysis;
- explicit trial-validity rules;
- retained INVALID attempts;
- no hidden automatic retries;
- separate immutable ground truth and policy-visible evidence;
- explicit right-censoring where time-to-event outcomes apply;
- effect estimates/confidence intervals rather than p-value hunting;
- public raw-evidence archive after freeze;
- executable analysis code preserved **before** final publication;
- no post-hoc weighted global policy score.

## General state and policy model

Let the underlying system state be represented as:

`S = {mission, security, evidence, connectivity, authorization, recovery, fault}`

The response policy receives only an observation:

`O ⊂ S`

where `O` may be incomplete, stale, contradictory, or adversarially manipulated.

A response policy maps observation to action:

`π(O) → a`

The design evaluates whether the resulting path satisfies or trades among bounded properties:

`G = {integrity, safety, availability, commandability, bounded containment, bounded recovery, evidence-qualified trust restoration}`.

No policy is assumed optimal by construction.

## Research questions

### RQ1 — Evidence integrity

How do qualitatively different evidence failures affect response selection, containment, mission availability, and trusted recovery?

Candidate evidence states:

- **V0 — complete/current:** all required policy-visible evidence present and current;
- **V1 — omission:** one required evidence source absent;
- **V2 — staleness:** evidence present but outside a frozen freshness threshold;
- **V3 — contradiction:** two independently represented evidence sources disagree;
- **V4 — manipulation:** one untrusted policy-visible value is deliberately falsified within frozen treatment rules.

The primary scientific objective is to distinguish **absence**, **age**, **conflict**, and **deception** rather than treating all degraded evidence as one binary T1 condition.

### RQ2 — Connectivity and authorization dependence

How does increasing or intermittent contact unavailability alter containment/recovery performance for policies with different authorization dependencies?

Candidate modeled contact regimes:

- **K0 — immediate contact**;
- **K1 — short outage**;
- **K2 — medium outage**;
- **K3 — extended outage**;
- **K4 — intermittent/flapping contact**.

Durations must be frozen after feasibility testing and should be expressed as modeled contact conditions, not orbital or RF measurements unless a later orbital-access model is explicitly added.

Primary estimands should test whether delay is approximately linear, thresholded, saturating, or policy-specific rather than merely repeating the Study 1 C1-minus-C0 contrast.

### RQ3 — Fault/attack ambiguity

Can response policies preserve security and availability when similar observations can arise from benign fault or adversarial action?

Candidate matched symptom pairs:

- telemetry/evidence unavailable because of a simulated benign publisher/process fault versus deliberate evidence suppression;
- inconsistent software/configuration state because of a simulated benign update failure versus compromised update context;
- contact unavailable because of modeled benign schedule/access loss versus deliberate authorization/evidence-path disruption.

The experiment should not require the policy to infer attacker intent perfectly. The key outcome is whether response behavior remains bounded and recoverable when **cause is ambiguous**.

### RQ4 — Context ablation

Which context dimensions actually contribute useful mission-aware response information?

Candidate selector variants:

- **π-full:** event + mission + evidence + contact context;
- **π-no-mission:** mission state removed from policy-visible inputs;
- **π-no-evidence:** evidence-quality context removed;
- **π-no-contact:** contact context removed;
- **π-security-only:** only the cyber-event/security state retained.

This directly follows from Study 1, where mission state was null on P1 primary endpoints while evidence/contact materially affected other outcomes. Study 2 must treat this as a new hypothesis rather than rewriting the Study 1 null result.

### RQ5 — Stronger policy baselines

Does contextual response add value beyond reasonable non-adaptive baselines?

Candidate baselines:

- **fixed security control** selected for the scenario class;
- **ground-authorized recovery**;
- **fail-closed:** choose the most conservative security action under evidence insufficiency;
- **fail-operational:** preserve mission/command availability unless frozen compromise evidence exceeds a threshold;
- **risk-threshold:** choose among actions using a preregistered deterministic evidence/security threshold.

An optimization-based policy may be considered later, but Study 2 should not introduce ML/AI solely for novelty.

## Candidate estimand blocks

The final design should share cells where factor identities are exactly compatible. A candidate structure is:

### Block A — evidence mechanism

- compromised-update context;
- one fixed mission state;
- immediate modeled contact;
- evidence states V0–V4;
- policies: fixed rollback, π-full, fail-closed, risk-threshold.

Nominal size before overlap: `5 evidence × 4 policies = 20 cells`.

### Block B — contact/authorization curve

- compromised-update context;
- full/current evidence;
- contact regimes K0–K4;
- policies: ground-authorized recovery, π-full, risk-threshold.

Nominal size before overlap: `5 contact × 3 policies = 15 cells`.

### Block C — benign-fault/adversarial ambiguity

- three matched symptom families;
- cause: benign fault versus adversarial treatment;
- selected policies: π-full, fail-closed, fail-operational.

Nominal size before overlap: `3 symptom families × 2 causes × 3 policies = 18 cells`.

### Block D — selector ablation

- four representative contexts selected **before** outcome generation to cover unauthorized-command, update/recovery, replay, and evidence-loss scenarios;
- selector variants: π-full, π-no-mission, π-no-evidence, π-no-contact, π-security-only.

Nominal size: `4 contexts × 5 variants = 20 cells`.

Because several full-evidence/full-selector conditions can be shared, the expected unique design is approximately **60–70 cells**, not the unshared 73-cell total above. Exact membership must be resolved and frozen before runtime.

## Replication and expected scale

The number of seed blocks should be selected by a **pre-runtime precision/power analysis**, not by copying the Study 1 value automatically. A practical planning range is 24–30 independent reproducible seed blocks.

At approximately 64 unique cells:

- 24 seeds → 1,536 VALID target observations;
- 30 seeds → 1,920 VALID target observations.

This scale is large enough to improve breadth while remaining interpretable and auditable. A blind full factorial producing tens of thousands of correlated observations is explicitly discouraged.

## Candidate primary outcomes

Study 2 should preserve the useful Study 1 dimensions but may refine their operationalization before freeze:

- unauthorized-effect completion / residual unauthorized control;
- mission-objective completion;
- safety-invariant violations;
- time to containment;
- time to evidence-qualified trusted recovery;
- legitimate-command rejection / command availability;
- ground/spacecraft state divergence;
- evidence completeness/freshness/conflict status;
- recovery terminal state.

Potential **new** outcomes that may be justified before freeze:

- response-selection stability under evidence perturbation;
- false-conservative response rate under benign fault;
- unsafe-permissive response rate under adversarial evidence loss, provided a frozen correctness/acceptability oracle is defined prospectively;
- response overhead (CPU/memory/latency) if measured under a controlled implementation-performance block.

Unlike Study 1 P4, a future “correctness” endpoint may be used only if an independent acceptability oracle is defined **before** data generation and is not available to the runtime policy.

## Statistical-analysis direction

Candidate analysis methods, subject to pre-registration and simulation-based verification:

- blocked generalized linear/mixed models for binary/proportion outcomes where non-degenerate;
- RMST or other prespecified survival estimands for censored containment/recovery outcomes;
- hierarchical or interaction models for evidence mechanism × policy and contact regime × policy;
- ordered trend/contrast tests for contact-duration regimes where scientifically justified;
- paired seed-block bootstrap for complex multi-objective contrasts;
- separate point-estimate Pareto analysis and uncertainty classification without an arbitrary weighted global score;
- complete-block sensitivity if runtime-version provenance changes.

No method should be selected after observing final outcomes solely to produce significance.

## Formal-assurance work package before empirical freeze

Study 2 should add a formal model of the response/recovery state machine using TLA+, nuXmv, PRISM, or another justified framework.

Candidate properties:

1. unauthorized state cannot transition directly to `TRUSTED_RECOVERY_CONFIRMED`;
2. trusted recovery requires the frozen evidence prerequisites;
3. authorization-gated actions cannot execute before authorization;
4. evidence-insufficient paths cannot bypass the declared fallback;
5. every terminating response path reaches an allowed terminal state;
6. recovery state cannot be declared trusted while modeled residual unauthorized state remains;
7. a policy-visible evidence change cannot alter immutable experiment ground truth;
8. runtime policy cannot read the post-run correctness/adjudication oracle.

The formal model must describe the **implemented** state machine rather than an idealized architecture that the code does not follow.

## HIL / aerospace-validation extension

A later validation block can increase TAES/JAIS compatibility without interacting with operational spacecraft or RF.

Candidate HIL setup:

- cFS running on a flight-like single-board computer;
- simulated sensors/actuators and dynamics;
- software-only command/telemetry link;
- no operational credentials;
- no RF transmission/interference;
- no real ground-station access.

Candidate HIL measures:

- CPU utilization;
- memory footprint;
- command-processing latency;
- policy-evaluation overhead;
- telemetry/evidence bandwidth;
- recovery timing.

A 12–18-cell representative subset with approximately 10 repetitions per cell could test implementation transfer after the SIL analysis is frozen. HIL results should be reported as engineering validation, not flight qualification.

## Legal and responsible-research boundary

Study 2 must remain entirely researcher-controlled and synthetic/emulated. It must not:

- target operational spacecraft or ground systems;
- transmit/jam/spoof RF;
- use non-public credentials;
- intercept communications;
- exploit third-party infrastructure;
- use classified/proprietary mission data;
- provide an operational attack recipe beyond what is necessary for reproducible defensive research.

## Freeze gates before any runtime execution

Runtime execution is prohibited until all of the following are complete:

1. final RQs and propositions/estimands;
2. exact cell matrix;
3. seed-block count justified by precision/power analysis;
4. frozen adversary and defender-knowledge model;
5. exact evidence and contact treatment definitions;
6. exact policy/baseline implementations;
7. trial-validity and INVALID rules;
8. primary/secondary outcome applicability rules;
9. analysis plan and censoring rules;
10. formal-model properties and implementation traceability;
11. campaign ledger/retry semantics;
12. safety/responsible-research review;
13. source commit and configuration hashes;
14. explicit runtime authorization.

## Separation from Study 1

Study 1 remains immutable at 720 VALID observations. This historical design candidate was superseded by the separately frozen Study-2 protocol, campaign, and Phase-7 result/provenance records. No Study-2 observation was inserted into Study 1 or used to retroactively change Study-1 proposition outcomes.
