# 3. Methods

## 3.1 Study design

The study used theory-informed design-science research with controlled software-in-the-loop experimentation. A trial was one fully specified combination of cyber event, mission state, evidence condition, contact condition, requested response policy, recovery behavior, and reproducible campaign seed. The final campaign was estimand-driven rather than a full factorial: combinations were retained when they identified a predeclared proposition, supplied a condition-matched policy comparator, or provided a same-campaign untreated reference.

The final design contained 24 frozen cells (A01–A24). Thirty campaign seeds (`10001`–`10030`) were applied to every cell, yielding a target of 720 VALID observations. Cell order was deterministic/reproducible within the frozen campaign plan, and one frozen position was executed per operator invocation. INVALID attempts did not advance the position and required a fresh-run-ID retry of the same seed/cell. No automatic retry or automatic next-position execution was allowed.

The experiment tested five propositions: mission-state dependence (P1), contact-delay effects (P2), evidence requirements for trusted recovery (P3), reduced-evidence effects on response selection/consequences (P4), and condition-specific mission-aware policy benefit (P5). Primary outcomes were predeclared and retained separately; no primary weighted composite replaced them.

## 3.2 Experimental environment and safety boundary

Experiments were conducted in a controlled NOS3/Fortytwo and cFS-based software-in-the-loop environment on researcher-controlled computing infrastructure. The testbed represented a ground command path, authorization state, modeled contact availability, flight-software command ingest, mission state, telemetry/evidence generation, response-policy execution, and recovery validation.

All cyber events, identities, commands, update artifacts, telemetry/evidence degradation, and contact conditions were synthetic or software-emulated. The study did not access an operational satellite or ground station, use operational credentials, transmit or interfere with RF, intercept non-public communications, or use classified/proprietary mission data. The immutable experiment-control and ground-truth records were outside the simulated adversary boundary and were never available to the runtime response policy as an oracle.

The experiment distinguished immutable experiment ground truth from policy-visible state and recovery evidence. In Study 1, the T1 treatment specifically reduced/suppressed selected policy-visible evidence fields according to the frozen event adapter; it was not a separate experiment in stale, contradictory, or forged observations. Those qualitatively different evidence-failure mechanisms are reserved for follow-on research.

### 3.2.1 Post-access adversary model

The experiment uses a **post-access adversary model**. Reconnaissance, exploit development, credential theft, RF interception, and the process by which an adversary initially reaches a command, update, or telemetry path are outside scope. Each event family instead begins from a frozen cyber-relevant state whose effect on response/recovery behavior can be measured reproducibly.

Depending on the frozen event family, the modeled adversary is represented as able to:

- submit an unauthorized but syntactically valid laboratory command through the simulated command path (E1);
- cause a previously authorized laboratory command to be replayed (E2);
- place the simulated spacecraft in a compromised synthetic software/update context (E3); or
- reduce/suppress selected policy-visible telemetry/evidence fields used for response selection or recovery assessment (E4/T1).

These are capability abstractions rather than claims of compromise of a specific satellite, real ground station, RF link, cryptographic key, software supplier, or operator account. The SPARTA identifiers reported in Section 2 are the identifiers frozen in the event catalog and are used only as behavioral/experimental correspondence.

### 3.2.2 Adversary exclusions and immutable research boundary

The simulated adversary cannot modify the frozen experiment plan, campaign seed, event/cell identity, response-policy implementation, trial-validity rules, analysis-membership rules, authoritative attempt-history ledger, or immutable experiment ground truth. These controls belong to the researcher-controlled experiment plane and are outside the simulated adversary boundary.

The runtime response policy also cannot access post-run outcome labels or the final trusted-recovery adjudication as an oracle. This separation is central to P3/P4: a policy can act with reduced evidence even while the experiment controller retains the true underlying state for later validity and outcome analysis.

The experiment does not evaluate confidentiality loss, data exfiltration, cryptanalytic strength, key extraction, RF jamming/spoofing resistance, physical counterspace attack, insider behavior, or human social engineering.

### 3.2.3 Defender-knowledge model

The defender is represented through two distinct knowledge domains:

1. **Runtime policy-visible state.** The response policy can use only the event, mission, evidence, contact, authorization, and other context explicitly exposed by the frozen policy interface. Under T1, selected evidence fields can be absent according to the frozen event definition.
2. **Experiment/analysis ground truth.** The controller retains immutable treatment identity, expected treatment/fidelity conditions, run provenance, and outcome evidence required to determine trial validity and terminal state. This information is not exposed to P7 as a correctness oracle.

This architecture creates the core information-security problem studied by P3/P4: response decisions are made under bounded observation, while trustworthy recovery is adjudicated only when sufficient current evidence exists.

### 3.2.4 Trust boundaries

For cybersecurity interpretation, the implemented experiment is partitioned into six trust boundaries:

- **TB0 — research control plane:** frozen campaign plan, run/cell identity, campaign seed, immutable ground truth, ledger rules, analysis-membership controls, and integrity-freeze material. TB0 is trusted for experimental validity and is not part of the simulated operational response system.
- **TB1 — ground authorization and command origin:** synthetic ground-side command/authorization state. P6 depends on this boundary; C1 delays authorization availability but does not model real operators, antenna scheduling, or ground-network performance.
- **TB2 — spacecraft command and execution path:** command ingest/execution in the cFS/NOS3/Fortytwo environment. E1/E2 challenge authorization/freshness assumptions of this path; the study measures modeled command consequences rather than protocol or cryptographic strength.
- **TB3 — policy-visible evidence/telemetry plane:** evidence/state exposed to the selector. Study 1 can reduce selected evidence fields across this boundary. The boundary is therefore treated as degradable rather than implicitly trustworthy.
- **TB4 — response/recovery mechanism:** fixed response mechanisms, ground-authorized behavior, rollback behavior, the modeled safe-mode action, and the deterministic rule-based P7 selector.
- **TB5 — recovery evidence adjudication:** post-action evidence used to classify trusted recovery. TB5 is an analysis/assurance boundary and is not a source of privileged runtime guidance to P7.

### 3.2.5 Security and dependability properties

The experiment evaluates multiple properties rather than a single security score. Table R6 provides the full mapping.

- **Integrity:** M01, software/configuration and authorization evidence, and post-response state agreement/divergence (M07).
- **Availability and mission continuity:** M02, M04, M05, M06, and M07.
- **Safety:** M03 frozen safety-invariant violations.
- **Recoverability/cyber resilience:** M05, recovery terminal state, restored authorized command path, and the requirement for current evidence before trusted recovery.
- **Evidence assurance:** the controlled evidence condition, M08 evidence completeness, and the applicable recovery-evidence criteria.

Confidentiality, exfiltration, cryptographic strength, RF security, and human/operator response are explicitly not evaluated.

### 3.2.6 Incident-response lifecycle mapping

NIST SP 800-61 Rev. 3 positions incident response inside broader cybersecurity risk management [@nist80061r3]. The experiment covers only the bounded response/recovery segment:

`modeled event established → response selection → containment → recovery/reconstitution → evidence-qualified recovery validation → mission/security consequence measurement`.

The study does not evaluate detector precision/recall, SOC triage, incident declaration, escalation staffing, forensic attribution, legal reporting, or organizational lessons learned. The mapping is explanatory rather than a claim of NIST compliance.

## 3.3 Frozen factors and final campaign cells

The final campaign used four event families:

- **E1:** unauthorized valid command;
- **E2:** replay of an authorized laboratory command;
- **E3:** compromised synthetic software/update context;
- **E4:** policy-visible telemetry/evidence degradation.

The final matrix used mission states M0 (nominal), M2 (low-power/eclipse context), and M4 (software-update/recovery context) as required by the proposition blocks. Contact condition C0 represented immediate modeled contact and C1 represented one synthetic/modelled missed-contact window. Evidence condition T0 provided the frozen full-evidence condition, while T1 reduced/suppressed policy-visible evidence according to the event adapter.

The 24 cells were:

| Cell | Event | Mission | Contact | Evidence | Requested policy | Effective policy in frozen design |
|---|---|---|---|---|---|---|
| A01 | E1 | M0 | C0 | T0 | P1 | P1 |
| A02 | E1 | M0 | C0 | T0 | P7 | P1 |
| A03 | E1 | M2 | C0 | T0 | P1 | P1 |
| A04 | E1 | M2 | C0 | T0 | P7 | P2 |
| A05 | E1 | M4 | C0 | T0 | P1 | P1 |
| A06 | E1 | M4 | C0 | T0 | P7 | P2 |
| A07 | E1 | M2 | C0 | T0 | P2 | P2 |
| A08 | E1 | M2 | C0 | T1 | P2 | P2 |
| A09 | E1 | M2 | C0 | T1 | P7 | P4 |
| A10 | E3 | M4 | C0 | T0 | P2 | P2 |
| A11 | E3 | M4 | C0 | T0 | P7 | P5 |
| A12 | E3 | M4 | C0 | T1 | P2 | P2 |
| A13 | E3 | M4 | C0 | T1 | P7 | P2 |
| A14 | E3 | M4 | C0 | T0 | P5 | P5 |
| A15 | E3 | M4 | C0 | T1 | P5 | P5 |
| A16 | E3 | M4 | C0 | T0 | P6 | P6 |
| A17 | E3 | M4 | C1 | T0 | P6 | P6 |
| A18 | E3 | M4 | C1 | T0 | P7 | P5 |
| A19 | E2 | M0 | C0 | T0 | P0 | P0 |
| A20 | E2 | M0 | C0 | T0 | P1 | P1 |
| A21 | E2 | M0 | C0 | T0 | P7 | P1 |
| A22 | E4 | M2 | C0 | T0 | P0 | P0 |
| A23 | E4 | M2 | C0 | T0 | P4 | P4 |
| A24 | E4 | M2 | C0 | T0 | P7 | P4 |

The final design retained complete low-dimensional blocks for the proposition interactions rather than using a broad aliased fractional factorial. P1 used policy `{P1,P7}` × mission `{M0,M2,M4}`. P2 used policy `{P6,P7}` × contact `{C0,C1}` under E3/M4/T0. P3 used policy `{P5,P7}` × evidence `{T0,T1}` under E3/M4/C0. P4 used event `{E1,E3}` × policy `{P2,P7}` × evidence `{T0,T1}`. Cells were shared across propositions when factor identities were exactly compatible.

## 3.4 Response policies and P6 authorization semantics

The policy family included observation-only, fixed containment/recovery mechanisms, a ground-authorized response, and the mission-aware selector. Relevant policies in the final matrix were P0 observe only, P1 identity/source isolation, P2 selective command restriction, P4 modeled safe-mode transition, P5 verified rollback, P6 wait for ground authorization, and P7 mission-aware selection.

P7 was a **frozen deterministic rule-based selector**, not a learned model or AI/ML method. It selected an effective policy from frozen policy-visible event, mission, evidence, and contact context. It did not read immutable ground truth. The P7 decision logic was frozen before the final campaign.

P6 requires special semantic treatment. A16/A17 are requested/effective **P6** cases. P6 represents a ground-authorized WAIT state: under C0 current synthetic authorization is available at the response boundary; under C1 one modeled contact window is missed before authorization becomes available. After authorization, P6 delegates the verified-rollback recovery action/mechanism associated with P5. The analysis therefore does not relabel A16/A17 as P5 policy cases.

`ENTER_SAFE_MODE` was an experimental software action in the controlled testbed. It is not a claim that a native spacecraft safe-mode implementation was entered or validated.

## 3.5 Trusted-recovery definition and outcomes

A run was classified `TRUSTED_RECOVERY_CONFIRMED` only when all applicable frozen recovery criteria passed, including approved software/configuration identity, integrity evidence, authorization/signature evidence, current measured-state/attestation evidence, restored authorized command path, ground/spacecraft state agreement, required telemetry restoration, health checks, absence of modeled residual unauthorized state, and a complete recovery record.

Other frozen terminal states included `OPERATIONAL_BUT_UNVERIFIED`, `CONTAINED_NOT_RECOVERED`, `RECOVERY_FAILED`, `MISSION_LOSS`, and `RUN_INVALID` as applicable to the analysis/validity rules.

The retained primary or proposition-facing metrics were:

- **M01:** unauthorized-effect completion;
- **M02:** mission-objective completion ratio;
- **M03:** count of distinct frozen safety-invariant violations;
- **M04:** time to modeled containment;
- **M05:** time to verified trusted recovery;
- **M06:** legitimate-command rejection rate from rejected/attempted counts;
- **M07:** modeled ground/spacecraft state-divergence duration;
- **M08:** evidence-completeness checklist ratio.

P5 used exactly M01, M02, M03, M05, and M06 as its primary multi-objective dimensions. M07 and M08 were not added to the P5 primary vector after seeing the data.

For M04 and M05, the frozen analysis horizon was 30 s. An unobserved event was right-censored rather than imputed. In the locked 720-run extraction, M05 contained 180 observed verified-recovery events and 540 right-censored observations. The event indicator and analysis-time field were stored separately so an administrative analysis time of 30 s was not mistaken for an observed recovery.

## 3.6 Trial validity, invalid-attempt retention, and campaign completion

A trial could enter the statistical dataset only after treatment/runtime, measurement, analysis-horizon, and evidence-validity checks passed. Infrastructure or measurement failures were classified `INVALID` under frozen rules and were retained rather than silently discarded.

The authoritative campaign ledger contains 729 records: 720 VALID observations and 9 retained INVALID attempts. The nine INVALID attempts occurred at five failed phases: `CFS_READINESS` (3), `MEASUREMENT_BINDING` (2), `NOMINAL_RUNTIME_COMPLETION` (2), `RUNTIME_HEALTH` (1), and `FROZEN_ANALYSIS_HORIZON` (1). Three CFS-readiness failures stopped before runtime and did not consume a campaign seed; other INVALID attempts had crossed later execution boundaries as recorded in their retained evidence. All nine were retried only as the same seed/cell with a fresh run ID and did not count toward the 720 VALID analysis positions.

One additional interrupted position-660 run created partial runtime/preflight evidence before a ledger classification could be completed. It was preserved in a quarantined unledgered area, never fabricated into the ledger, and the position was re-derived and later executed cleanly. Pre-runtime non-scientific abort evidence was likewise retained outside the analysis population.

The final VALID dataset was balanced and complete: every A01–A24 cell contained exactly 30 VALID repetitions; all seeds `10001`–`10030` were represented; and there were 720 unique valid `(seed, cell)` pairs with no gaps or duplicates.

## 3.7 Analysis population and frozen extraction

WP10 statistical analysis used exactly the 720 VALID membership frozen after campaign closeout. INVALID attempts and non-analysis unledgered/quarantined evidence were available for Methods, provenance, and limitations but were not statistical members.

The locked analysis extraction preserved raw/frozen endpoint variables, factor identities, requested/effective policy, and M05 event/censor representation. Expected values used during treatment/fidelity validation were acceptance criteria only and were never substituted for observed primary metrics.

## 3.8 Statistical analysis

Analysis followed the endpoint applicability rules frozen before the final campaign and adapted to observed structural degeneracy without manufacturing model estimates. Seed was treated as the reproducible blocking/resampling unit. Results emphasize effect estimates, exact counts where appropriate, and confidence intervals rather than p-values.

### P1 — mission-state dependence

P1 used the complete E1 `{P1,P7} × {M0,M2,M4}` block. M01 and M06 were evaluated from exact cell counts/risk-difference contrasts; M02 used blocked/descriptive cell contrasts; and structurally zero M03 was reported using exact counts/bounds rather than forcing a count regression. Policy-by-state contrasts/interactions were retained on the predeclared primary outcomes. M07 was not introduced to rescue the P1 result.

### P2 — modeled contact-delay effect

P2 compared P6 and P7 across C0/C1 under E3/M4/T0. M04 and M05 used restricted mean survival time (RMST) through `τ = 30 s`, retaining right-censoring and using seed-block bootstrap intervals. M07 used a paired/seed-blocked duration contrast with bootstrap uncertainty. The primary reported quantities were the P6 C1−C0 effect, P7 C1−C0 effect, and their difference-in-differences interaction.

### P3 — evidence requirement for trusted recovery

P3 compared P5 and P7 under T0/T1 in E3/M4/C0. Terminal-state distributions and trusted-recovery counts were reported directly when the outcome structure was deterministic/degenerate. Supporting divergence/evidence analyses were retained without replacing the terminal-state conclusion. The analysis separately assessed the predeclared narrower possibility of nominal restoration without verification rather than assuming that mechanism from an evidence failure.

### P4 — reduced-evidence selection and consequence

P4 used actual execution metadata for `effective_policy_id`, selected action, and selection basis. Selection was not inferred from expected policy or immutable ground truth. The analysis traced `event × evidence × requested policy → actual effective policy/action → observed consequences` across the frozen P4 cells. Because the experiment did not contain an independent objective correctness oracle, P4 was interpreted as selection/consequence evidence rather than as a post-hoc “incorrect action” classification.

### P5 — condition-specific Pareto comparison

P5 used nine frozen condition groups (G01–G09): G01 A01/A02; G02 A03/A04/A07; G03 A05/A06; G04 A08/A09; G05 A10/A11/A14/A16; G06 A12/A13/A15; G07 A17/A18; G08 A19/A20/A21; and G09 A22/A23/A24.

For each cell, lower values were preferred for M01, M03, M05 RMST, and M06; higher values were preferred for M02. A cell dominated another when it was no worse on all five dimensions and strictly better on at least one. Point-estimate Pareto-front membership was reported separately from uncertainty.

For matched P7-versus-comparator contrasts, 20,000 paired campaign-seed bootstrap replicates were used to obtain marginal percentile 95% intervals. Benefit directions were standardized so positive values favored P7. The retained interval classifications distinguish marginal support for P7 dominance, comparator dominance, trade-off, or uncertain/tied relations. These are marginal intervals rather than simultaneous Pareto-confidence regions; no simultaneous 95% dominance claim is made.

No p-values, primary weighted score, or global policy ranking were computed for P5.

## 3.9 Execution-provenance audit and sensitivity analysis

Per-run immutable campaign plans identified three research-repository execution commits among the 720 VALID observations: 1 VALID run at `aae2239753119c92e7633db3b6c73aee94c7b6dd`, 9 at `97074d0cdc4261de02bc6f618e891a88f45f9cfc`, and 710 at `7ed85d5cbeca8f903b3468bc6ccc1c56e29c2446`.

A dedicated provenance review compared the runtime executor and frozen scientific core across these commits. It found no change to treatment/policy logic, event simulation, timing horizon, primary metric generation, or frozen configuration, while identifying versioned changes in runtime orchestration, finalization compatibility, fidelity validation, and invalid-result handling. The 720 VALID observations were therefore retained as analytically exchangeable with explicit versioned provenance.

As a sensitivity analysis, P5 was repeated on the 29 complete seed blocks (`10002`–`10030`) for which all 24 cells executed at the final commit C, yielding 696 observations. This sensitivity did not replace the primary population. It tested whether P7 front membership, pairwise Pareto relation, or primary-metric direction changed when the earlier execution commits were removed as complete blocks.

## 3.10 Reproducibility and integrity controls

The campaign recorded immutable plans, random seeds, run IDs, factor identities, source-harness derivation, runtime requests, treatment/fidelity checks, raw measurement inputs, canonical outcomes, and cleanup state. The authoritative attempt-history ledger was append-only under the campaign operator and enforced exact-next-position, duplicate-valid prevention, same-seed/cell retry after INVALID, fresh run IDs, and no hidden automatic reruns.

After campaign completion, a read-only integrity freeze reconciled all 729 ledger rows, 720 VALID memberships, nine INVALID classifications, seed-consumption boundaries, unledgered evidence partitions, per-attempt execution commits, and the complete local campaign tree. The authoritative ledger SHA-256 is `92893a2fd8746f410bffd4dca5101bc3f533ada2ff82f98681788cf0c24ce6fd`; the 720-valid analysis-membership SHA-256 is `a2bf0c8f352f4386e74a500d97ea8f73e0c39d03bfe10ac0ebcf02470af9f70e`; and the deterministic complete campaign-tree SHA-256 is `ad1e127b4431b6b334955129fcba82f76b18e5b43585395ac8c37300cac087b1`.

Raw campaign evidence remains outside GitHub and is publicly archived as the DOI-bearing Zenodo v1.0.0 evidence-of-record (version DOI `10.5281/zenodo.22181540`; concept DOI `10.5281/zenodo.22181539`). The archive contains the frozen raw campaign, integrity-freeze material, publication/provenance artifacts, release documentation, manifest, and checksums. After the campaign and Zenodo v1.0.0 publication, but before journal submission, an executable statistical reproduction implementation was reconstructed under `analysis/` because the original WP10 analysis source was not preserved. That reconstructed implementation starts from the frozen derived analysis inputs and is regression-validated against the preserved authoritative WP10 outputs; it is not represented as the original analysis source and does not alter the archived v1.0.0 files or the frozen statistical population.

OpenAI ChatGPT was used **after the campaign and historical WP10 findings were frozen** to assist with reconstructing, reviewing, and testing that public reproducibility implementation from preserved derived inputs, outputs, and provenance records. This AI-assisted reconstruction did not generate experimental observations, consume campaign seeds, change statistical membership, or modify frozen WP9/Zenodo evidence. The implementation was human-reviewed and regression-tested against preserved reference artifacts; the AI assistance is disclosed because it formed part of reproducibility-code reconstruction after Zenodo publication and before journal submission, not because AI/ML was part of the Study 1 response mechanism.

## 3.11 Responsible-research boundary

The study used public/research software, synthetic events, synthetic identities, isolated networking, and software-emulated impairments. No human participants were included in this experiment. No operational satellite/ground-station testing, live RF transmission/interference, stolen credentials, proprietary telemetry, or classified/export-controlled mission data were used.
