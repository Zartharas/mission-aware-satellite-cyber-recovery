# Rebuilt Paper 4 — Study 8 + Study 8E Manuscript Integration Plan

**Plan date:** 2026-09-20  
**Plan status:** `READY_FOR_AUTHOR_REVIEW__MANUSCRIPT_EDITING_NOT_EXECUTED`  
**Architecture authority:** `publication/Paper_4_Study_8/PAPER4_STUDY8_8E_ARCHITECTURE_AND_NONOVERLAP_GATE_2026-09-20.md`  
**Source main commit:** `391a76ae46a2c91592a9eafded5fcca8ef0f90cb`  
**Scientific components:** Study 8 / `S8-PQC-ICR-001` + Study 8E / `S8E-ECTV-001`

## 1. Purpose

This plan defines how to rebuild Paper 4 as one two-study manuscript after the Acta Astronautica editorial rejection.

The author has already selected:

> **Study 8 + Study 8E -> rebuilt Paper 4**

This plan does not edit the manuscript. It defines the scientific story, title direction, research-question placement, section architecture, claim-to-evidence ledger, figure/table plan, cross-study synthesis rules, non-overlap controls, and execution sequence that must govern later manuscript integration.

The exact rejected Acta package remains immutable provenance.

## 2. Definition of success

A successful rebuilt manuscript must satisfy all of the following:

1. preserve the complete frozen Study 8 record and its negative primary policy result;
2. preserve the complete frozen corrected Study 8E record;
3. present Study 8 and Study 8E as separate finite evidence populations;
4. never pool their rows, denominators, endpoints, or timescales;
5. use Study 8E to strengthen external timing relevance without calling it an external empirical replication;
6. distinguish fixed-capacity success in Study 8 from minimum modeled rate thresholds in Study 8E;
7. make the strongest systems contribution visible earlier than the rejected manuscript did;
8. keep Paper 5 / Study 9's semantic-interoperability and action-identifiability lane outside Paper 4;
9. avoid physical-link, flight, RF, CPU, energy, certification, or operational availability claims not supported by the frozen evidence;
10. leave venue lock and publisher submission for later explicit gates.

## 3. Frozen evidence authorities

### 3.1 Study 8

Primary authorities:

- `study8/STUDY8_PROTOCOL.json`
- `study8/STUDY8_CLAIM_BOUNDARY.md`
- `study8/STUDY8_TECHNICAL_CLOSE.json`
- `study8/analysis/docs/PHASE8_6_RESULTS_FREEZE.md`
- `publication/study8/manuscript/manuscript.md`
- `publication/study8/tables/table-s8-1-design.csv`
- `publication/study8/tables/table-s8-2-primary-profile.csv`
- `publication/study8/tables/table-s8-3-p3-vs-p1-strata.csv`
- `publication/study8/tables/table-s8-4-policy-tradeoffs.csv`

Frozen Study 8 population:

- 3 cryptographic profiles;
- 4 policies;
- 4 synthetic logical contact regimes;
- 4 disruption schedules;
- 6 compromise offsets;
- 3 logical deadlines;
- 3,456 complete deterministic positions.

Frozen primary result:

- each policy: `635/864 = 73.4954%`;
- P3 minus P1: `0.000000` percentage points;
- exact null in every prespecified regime, profile, disruption, and deadline stratum.

### 3.2 Study 8E

Primary authorities:

- `study8e/STUDY8E_PROTOCOL.json`
- `study8e/CANONICAL_RESULTS_002_AUDIT_HANDOFF.json`
- `study8e/CANONICAL_RESULTS_002_FREEZE.json`
- `study8e/CURRENT_EXTENSION_STATE.md`

Formal corrected freeze:

`S8E-CANON-RESULTS-002-FREEZE-001`

Frozen Study 8E population and results:

- 20 selected satellite-station trace pairs;
- 476 frozen SatNOGS source rows;
- 454 eligible anchors;
- 65,376 canonical cases;
- 17,640 finite minimum-rate thresholds;
- 47,736 non-finite cases;
- finite fraction `245/908 = 0.269824`;
- finite modeled threshold range: 48 to 57,727 bps;
- finite modeled threshold median: 345 bps;
- 16,344 P3/P1 matched comparisons;
- 4,410 both-finite P3/P1 comparisons, all with exactly 0 bps threshold difference;
- 21,792 profile-burden ordering checks, all preserved.

The immutable corrected artifact's known stale `results_id` label in `RESULTS_HASH_MANIFEST.json` remains a documented non-scientific metadata defect. It must not be silently repaired or used to justify a rerun.

## 4. Scientific center of the rebuilt manuscript

The rejected manuscript was centered primarily on the Study 8 contact-aware policy comparison.

The rebuilt manuscript should instead center on the broader systems question:

> **What constrains trusted post-compromise post-quantum cryptographic recovery when communication opportunity is intermittent, and which structural findings remain when the analysis moves from a controlled logical contact budget to independently sourced public observation-opportunity timing?**

This is a manuscript-level organizing question, not a replacement for either frozen study protocol.

The scientific thesis should be:

> **Trusted post-compromise cryptographic recovery is jointly constrained by transition-object burden, the temporal structure of communication opportunity, and the available recovery horizon. A contact-aware pre-commit guard does not create capacity: the Study 8 P3-versus-P1 success null remains exact in the controlled finite model, and Study 8E likewise finds no P3/P1 minimum-rate advantage under the frozen external observation-opportunity timing population. The two evidence layers differ in estimand—fixed-capacity success versus minimum modeled rate—so their results must be synthesized structurally rather than pooled.**

## 5. Recommended title direction

No title is locked by this plan.

### Preferred working title

**Post-Quantum Trusted Recovery Under Intermittent Connectivity: Feasibility Across Modeled Contact Budgets and Public Observation-Opportunity Timing**

Why this is preferred:

- foregrounds the actual systems contribution rather than P3;
- accommodates both Study 8 and Study 8E;
- does not call SatNOGS observations operational command contacts;
- avoids implying that Study 8 logical slots were converted to physical time;
- makes feasibility, not policy superiority, the center.

### Alternative 1

**Post-Compromise Post-Quantum Recovery in Satellite Systems: Deterministic Contact-Budget Feasibility and External Observation-Timing Evaluation**

### Alternative 2

**Cryptographic Recovery Under Intermittent Satellite Connectivity: From Controlled Contact Budgets to Public Observation-Opportunity Timing**

Avoid:

- leading the title with “contact-aware”;
- “real-world validation”;
- “operational validation”;
- “external replication”;
- “measured throughput”;
- any wording that equates SatNOGS observation windows with authenticated command availability.

## 6. Contribution structure

The rebuilt Introduction should state four contributions.

### Contribution 1 — controlled post-compromise transition model

An exhaustive deterministic model couples:

- exact standardized ML-KEM / ML-DSA object sizes;
- a frozen cryptographic recovery state machine;
- four transition policies;
- finite logical contact opportunities;
- deadlines;
- bounded non-cryptanalytic disruptions.

This is Study 8 evidence only.

### Contribution 2 — fixed-capacity feasibility versus state-cost separation

Study 8 shows that:

- all four policies have identical primary recovery success;
- standardized object burden materially changes the fixed-capacity feasible set;
- equal full-cycle capacity does not imply equal deadline-constrained success when capacity is differently distributed in logical time;
- policy semantics redistribute predecessor exposure, control unavailability, overlap, transfer use, attempts, and terminal failure classification even when primary success is unchanged.

### Contribution 3 — separately frozen external timing extension

Study 8E applies the frozen transition object requirements and policy semantics to prospectively governed public SatNOGS observation-opportunity timing and solves the minimum hypothetical uniform effective payload rate needed for trust restoration.

This extension adds timing evidence without:

- rewriting Study 8;
- pooling populations;
- assuming observation = operational command contact;
- using transmitter baud as throughput;
- converting Study 8 logical slots into seconds.

### Contribution 4 — cross-study structural synthesis

The two separately governed studies support a bounded synthesis:

- P3 has no feasibility advantage over P1 in either evidence layer under the respective frozen endpoint;
- more available time expands the feasible set in both studies, but the numerical horizons and endpoints are not directly comparable;
- cryptographic-object burden reduces fixed-capacity success in Study 8, while Study 8E shows identical finite/non-finite classification across profiles but preserves required-rate burden ordering in every matched profile comparison;
- therefore **fixed-capacity feasibility** and **required-rate burden** are distinct but complementary ways to characterize recovery constraints.

## 7. Research-question placement

### 7.1 Manuscript-level framing question

Use the organizing question in Section 4 as the narrative umbrella only. Do not call it a new preregistered endpoint.

### 7.2 Study 8 question — reproduce exactly

In the Study 8 section, reproduce the frozen question exactly:

> **How do cryptographic-transition strategies change the ability to restore trusted control within finite intermittent-contact budgets after credential or cryptographic-state compromise?**

### 7.3 Study 8E research questions — preserve exactly

The Study 8E section must retain the four frozen RQs.

**RQ1**

> What observation-opportunity duration, inter-opportunity-gap, window-count, and gap-variability structure is observed in prospectively selected public satellite observation traces under a frozen source-selection rule?

**RQ2**

> For the frozen Study 8 cryptographic transition-object bundles replayed over externally observed observation-opportunity windows, what minimum hypothetical uniform effective payload rate is required to reach TRUST_RESTORED within each extension-only elapsed-time horizon?

**RQ3**

> Under the same externally observed observation-opportunity timing traces and transition-object requirements, do the four frozen Study 8 policy semantics change the minimum-rate feasibility threshold or primarily redistribute transition-state costs and terminal failure classifications?

**RQ4**

> Which qualitative Study 8 findings remain directionally consistent, differ, or become non-identifiable when synthetic contact timing is replaced by external contact timing, without pooling the two evidence populations?

RQ4 is the formal bridge into the cross-study synthesis section.

## 8. Recommended manuscript architecture

### 1. Introduction

Purpose:

- establish the long-lived satellite cryptographic-transition problem;
- explain why intermittent opportunity matters after compromise;
- distinguish algorithm benchmarking from recovery-state transition feasibility;
- explain the need for both a controlled model and an external timing layer;
- state the manuscript-level framing question;
- list the four contributions;
- state clearly that the negative/null policy result is retained.

Do not put repository hashes in the Introduction.

### 2. Related Work and Standards Context

Use compact categories:

1. post-quantum cryptography for satellite / NTN systems;
2. quantum-safe authentication, handshakes, and key management under constrained communications;
3. crypto agility and migration;
4. satellite cybersecurity, post-compromise recovery, and intermittent connectivity;
5. public observation networks as timing evidence, carefully separated from operational command links.

End with a closest-work paragraph:

> The gap is not “PQC for satellites” or “PQC objects are larger.” The gap is the interaction between standardized cryptographic transition burden, trusted post-compromise state progression, intermittent opportunity timing, and bounded recovery horizons, evaluated first under a controlled finite contact model and then under separately frozen public observation-opportunity timing.

A fresh literature verification should occur during later manuscript integration. This plan does not lock a literature corpus.

### 3. Shared Cryptographic-Recovery Framework

This section prevents duplicated methods across the two studies.

#### 3.1 Recovery state machine

Show:

`COMPROMISED -> RECOVERY_AUTHORITY_ESTABLISHED -> SUCCESSOR_CRYPTO_PROFILE_SELECTED -> SUCCESSOR_KEY_MATERIAL_STAGED -> TRANSITION_PROOF_ACCEPTED -> NEW_EPOCH_COMMITTED -> OLD_EPOCH_REVOKED -> TRUST_RESTORED`

#### 3.2 Cryptographic object bundles

Retain the seven required objects and exact profile budgets:

- 12,560 bytes;
- 17,460 bytes;
- 24,236 bytes.

State once that these are standardized cryptographic-object bytes only.

#### 3.3 Transition policies

Define P0-P3 once.

Emphasize that P3 is P1 staged semantics plus a deterministic nominal pre-commit capacity guard.

#### 3.4 Shared adversary and trust boundaries

State what the model permits and prohibits.

Do not imply cryptanalytic break, implementation compromise, or operational spacecraft validation.

### 4. Study 1 — Controlled Logical-Contact Experiment (Study 8)

#### 4.1 Frozen finite design

Report:

`3 × 4 × 4 × 4 × 6 × 3 = 3,456`

Explain the four 48-slot regimes and equal 65,536-byte full-cycle capacity.

State explicitly:

> Study 8 logical slots are ordering units and have no physical duration.

#### 4.2 Endpoint and exact finite-population analysis

Primary endpoint:

`trusted_recovery_before_deadline_without_stale_or_compromised_epoch_acceptance`

Primary contrast:

P3 minus P1.

Explain complete finite-population reporting once.

#### 4.3 Study 8 results

Order the results as:

1. primary P3/P1 null;
2. fixed-capacity cryptographic-object feasibility;
3. contact timing and deadline;
4. policy state/availability tradeoffs;
5. invariant checks.

Do not let the null result dominate the entire manuscript, but keep it clearly identified as prespecified and primary.

### 5. Study 2 — External Observation-Opportunity Timing Extension (Study 8E)

#### 5.1 Prospective source and population governance

Describe:

- SatNOGS as the primary external observation-opportunity timing source;
- frozen June 2026 source window;
- deterministic candidate ranking and entity caps;
- corrected `norad_cat_id + ground_station` qualification;
- 20 selected trace pairs;
- 476 retained source rows;
- 454 eligible anchors.

The POP-001 parameter defect may be disclosed briefly in reproducibility/provenance, not made a central scientific result.

#### 5.2 Observation-opportunity mapping

State precisely:

- `start/end` define timing windows;
- overlapping/abutting windows within one trace are merged for timing arithmetic;
- windows are timing proxies only;
- no cross-station or cross-satellite primary merging;
- no source-metadata capacity inference;
- no same-window reuse after the compromise anchor.

#### 5.3 Extension endpoint

Define:

`hypothetical_uniform_effective_payload_rate_bps`

as:

> a modeled constant net payload bit rate available only during accepted observation-opportunity windows, solved as a threshold parameter and not measured from SatNOGS.

Primary horizons:

- 6 h;
- 12 h;
- 24 h.

Success still requires `TRUST_RESTORED` strictly before the horizon.

#### 5.4 Study 8E results

Report in this order:

1. frozen trace/timing description from `TRACE_TIMING_SUMMARY.csv` and related frozen timing outputs;
2. overall finite/non-finite rate-threshold feasibility;
3. horizon dependence;
4. disruption dependence;
5. policy threshold comparison;
6. profile burden ordering;
7. structural safety fields.

Timing-descriptor values must be taken directly from the frozen Study 8E result artifact during manuscript integration. Do not invent or recompute them manually for this plan.

### 6. Cross-Study Synthesis

This section is essential and must never present a pooled denominator.

Use four synthesis questions.

#### 6.1 Does contact-aware staging increase feasibility?

**Study 8:** no success advantage; P3-P1 = 0.000000 percentage points.

**Study 8E:** no rate-threshold advantage; every both-finite P3/P1 comparison has exactly 0 bps difference.

Permitted synthesis:

> Across both frozen evidence layers, the added P3 pre-commit guard does not increase the respective feasibility endpoint because it does not create communication capacity or reduce the transition-object bundle.

Do not call this replication.

#### 6.2 How does cryptographic-object burden appear under different estimands?

**Study 8, fixed modeled contact capacity:**

- PROFILE_512_44: 93.7500% success;
- PROFILE_768_65: 64.9306%;
- PROFILE_1024_87: 61.8056%;
- non-increasing success in all 1,152 matched non-profile positions.

**Study 8E, solved minimum-rate endpoint:**

- each profile has the same finite/non-finite classification count: 5,880/21,792;
- profile burden ordering is preserved in 21,792/21,792 matched comparisons.

Permitted synthesis:

> Larger standardized transition bundles reduce success when capacity is fixed, while under a solved-rate endpoint they increase the required communication burden without changing whether a finite threshold exists in the frozen external timing cases.

This distinction is one of the strongest reasons to publish the studies together.

#### 6.3 What does additional recovery time change?

**Study 8:**

- D12: 32.6389% per policy;
- D24: 87.8472%;
- D48: 100%.

**Study 8E:**

- 6 h finite: 5.2863%;
- 12 h finite: 20.5947%;
- 24 h finite: 55.0661%.

Permitted synthesis:

> Longer allowed recovery time expands the feasible set in both studies.

Prohibited:

- mapping D12/D24/D48 logical slots to 6/12/24 hours;
- comparing the percentages as if they estimate the same endpoint;
- calculating a pooled or cross-study effect size.

#### 6.4 What do disruption patterns show?

Study 8 retains its exact fixed-capacity success strata.

Study 8E finds:

- A0 and A1: 40.5286% finite;
- A2 and A3: 13.4361% finite.

Permitted synthesis:

> Timing-sensitive disruption can materially restrict recovery opportunity, but the magnitude is endpoint- and model-specific.

Do not claim causal real-world attack prevalence or operational disruption rates.

### 7. Discussion

Organize around mechanisms, not around a list of percentages.

#### 7.1 Capacity cannot be created by a guard

P3 can block or classify a transition differently but cannot:

- add contact windows;
- increase capacity;
- shrink the object bundle.

This explains the exact P3/P1 null structure without dismissing policy-state differences.

#### 7.2 Fixed-capacity feasibility versus required-rate burden

This should be the central conceptual discussion.

Study 8 asks:

> Can the transition finish under a fixed modeled opportunity budget?

Study 8E asks:

> What modeled rate would be required for it to finish under the frozen external timing windows?

These are complementary, not interchangeable, endpoints.

#### 7.3 Timing distribution matters

Study 8 shows that equal complete-cycle byte capacity can produce different deadline success when capacity arrives at different logical times.

Study 8E tests the same broad concern using separately sourced observation-opportunity timing.

Do not claim that Study 8E establishes operational command availability.

#### 7.4 Policy semantics still matter without policy superiority

Use Study 8 policy tradeoffs and Study 8E state-cost outputs only where frozen evidence supports them.

Do not turn state-cost differences into an overall policy ranking.

#### 7.5 Systems implication

Bounded implication:

> Cryptographic migration planning for intermittently connected systems should account for transition-object burden, when usable opportunity becomes available, and the recovery horizon, rather than treating algorithm selection or aggregate capacity alone as sufficient.

Do not convert this into a deployment recommendation for a particular ML-KEM/ML-DSA pair.

### 8. Limitations and External-Validity Boundary

Consolidate limitations here.

Must include:

- Study 8 uses synthetic logical contact and no slot-to-seconds mapping;
- Study 8E uses public observation-opportunity timing, not authenticated bidirectional command contact;
- modeled rate is not measured throughput;
- transmitter baud is not used as recovery throughput;
- no spacecraft CPU, memory, RF, energy, thermal, framing, certificate, or operational mission measurements;
- no external laboratory replication;
- no inferential generalization beyond the frozen finite populations;
- Study 8E trace selection is bounded by its frozen stopping rule and first-page acquisition rule;
- the Results-002 metadata-label discrepancy is non-scientific and documented;
- no policy-superiority conclusion is supported.

### 9. Reproducibility and Data Availability

Keep the reader-facing section concise.

Include:

- repository;
- Study 8 identifiers and frozen result authority;
- Study 8E population/trace/result freeze IDs;
- exact corrected workflow/artifact identity where useful;
- note that detailed hashes and audit lineage are in repository governance records.

Do not overload the main Results text with commit hashes.

### 10. Conclusion

The conclusion should contain three points only:

1. fixed contact capacity, timing, and transition burden jointly constrain modeled recovery;
2. P3 does not improve the frozen feasibility endpoint over P1 in either evidence layer;
3. external observation-opportunity timing strengthens the timing relevance of the systems argument without converting the evidence into operational command-contact or throughput measurements.

## 9. Claim-to-evidence ledger

| ID | Proposed manuscript claim | Evidence authority | Status / boundary |
| --- | --- | --- | --- |
| C1 | All four Study 8 policies succeed in 635/864 positions | Study 8 frozen findings / table-s8-2 | Exact |
| C2 | Study 8 P3-P1 primary difference is 0.000000 percentage points | Study 8 frozen findings / table-s8-3 | Exact |
| C3 | Study 8 profile success is 93.7500%, 64.9306%, 61.8056% | table-s8-2 | Exact |
| C4 | Study 8 success is non-increasing with larger object burden in all 1,152 matched non-profile positions | Study 8 frozen analysis | Exact finite-population statement |
| C5 | Equal 65,536-byte full-cycle capacity does not yield equal Study 8 regime success | Study 8 protocol + table-s8-3 | Logical model only |
| C6 | Study 8 policies redistribute exposure, availability, overlap, transfer, attempts, and terminal failure classes | table-s8-4 | No overall policy ranking |
| C7 | Study 8E population contains 20 trace pairs, 476 rows, 454 eligible anchors, 65,376 cases | Results-002 freeze | Exact |
| C8 | Study 8E finite thresholds are 17,640/65,376 = 0.269824 | Results-002 freeze | Exact |
| C9 | Study 8E finite threshold range is 48-57,727 modeled bps; median 345 | Results-002 freeze | Modeled rate only |
| C10 | Study 8E finite fraction rises from 0.052863 to 0.205947 to 0.550661 over 6/12/24 h | Results-002 audit/freeze | Exact; extension-only horizons |
| C11 | Study 8E A0/A1 finite fraction = 0.405286 and A2/A3 = 0.134361 | Results-002 audit | Exact |
| C12 | Each Study 8E policy has 4,410/16,344 finite cases | Results-002 audit | Exact |
| C13 | Every both-finite Study 8E P3/P1 threshold difference is 0 bps | Results-002 freeze | Exact |
| C14 | Each Study 8E profile has 5,880/21,792 finite cases | Results-002 audit | Exact |
| C15 | Profile burden ordering is preserved in 21,792/21,792 Study 8E matched checks | Results-002 freeze | Exact |
| C16 | Study 8E rollback/stale-epoch acceptance structural sums are zero in frozen outputs | Results-002 audit | Modeled structural field only |
| C17 | P3 shows no advantage on the respective feasibility endpoint in either study | C2 + C13 | Cross-study structural synthesis; not replication |
| C18 | More allowed recovery time expands the feasible set in both studies | Study 8 deadline strata + Study 8E horizon strata | Qualitative synthesis only |
| C19 | Object burden affects fixed-capacity success in Study 8 and required-rate burden in Study 8E | C3/C4 + C14/C15 | Distinct estimands; no pooling |
| C20 | Study 8E strengthens external timing relevance of Paper 4 | Study 8E frozen source/timing design | Must not say operational validation or empirical replication |

Any proposed claim not represented here or directly traceable to a frozen authority must be added to the ledger before it enters manuscript prose.

## 10. Figure plan

No figure is authorized to introduce a new scientific endpoint.

### Figure 1 — Shared trusted-recovery state machine

New presentation figure derived only from frozen protocol semantics.

Show:

- state progression;
- seven required objects;
- predecessor/successor acceptance transitions for P0-P3.

Purpose: make the mechanism understandable before results.

### Figure 2 — Two evidence layers, explicitly non-convertible

A schematic with two panels:

**A. Study 8:** 48-slot logical contact schedules with fixed byte budgets.

**B. Study 8E:** external observation-opportunity windows on elapsed time with solved modeled rate.

Place a visible separator:

> **No slot-to-seconds conversion; no pooled population.**

Purpose: prevent readers from assuming Study 8E is a physical calibration of Study 8.

### Figure 3 — Study 8 fixed-capacity feasibility

Reuse/redesign frozen Study 8 profile and contact-regime result graphics.

Possible two-panel figure:

- profile success;
- regime success.

Values must remain exactly frozen.

### Figure 4 — Study 8E timing and threshold result

Use only frozen Results-002 files.

Possible panels:

- frozen observation-opportunity timing summary;
- finite/non-finite fraction by horizon;
- finite threshold distribution or summary.

Exact plotting choices must be based on the frozen artifact, not newly derived source rows.

### Figure 5 — Cross-study burden/feasibility synthesis

Prefer a conceptual or matched-endpoint figure rather than pooled quantitative plotting.

Show:

- Study 8: fixed capacity -> larger bundle -> lower fixed-capacity success;
- Study 8E: solved rate -> finite classification unchanged by profile, but rate burden ordering preserved.

Do not place incompatible percentages on a common y-axis.

## 11. Table plan

### Table 1 — Two-study evidence architecture

Columns:

- study;
- population;
- time representation;
- capacity/rate treatment;
- primary endpoint;
- permitted interpretation.

This table should explicitly show that there is no pooled sample size.

### Table 2 — Shared profiles and policy semantics

Merge the most useful frozen Study 8 design information into one compact reader-facing table.

### Table 3 — Study 8 fixed-capacity results

Retain:

- policy success;
- profile success;
- selected contact/deadline strata.

Do not overfill with provenance hashes.

### Table 4 — Study 8 policy state-cost tradeoffs

Use the existing frozen tradeoff table, possibly shortened for readability.

### Table 5 — Study 8E frozen results

Include:

- population counts;
- overall finite threshold fraction;
- threshold min/median/max;
- horizon finite fractions;
- disruption finite fractions;
- policy equality;
- profile ordering.

### Table 6 — Cross-study synthesis

Columns:

- scientific dimension;
- Study 8 finding;
- Study 8E finding;
- permitted synthesis;
- prohibited inference.

This table is preferable to any pooled meta-analysis.

## 12. Abstract blueprint

The rebuilt abstract should use four short components.

### Problem

Long-lived satellite systems may need to replace compromised cryptographic state under intermittent communication opportunity while post-quantum transition objects impose nontrivial transfer burden.

### Methods

State that the paper contains two separately governed finite studies:

- Study 8: 3,456-position controlled deterministic logical-contact experiment;
- Study 8E: prospectively frozen public SatNOGS observation-opportunity timing extension with 65,376 canonical cases.

Explicitly state that populations are not pooled.

### Principal findings

Include no more than four numerical messages:

1. Study 8 P3-P1 = 0.000000 percentage points;
2. Study 8 profile success range 93.7500% to 61.8056%;
3. Study 8E overall finite threshold fraction 26.9824% with modeled finite thresholds 48-57,727 bps;
4. Study 8E P3/P1 both-finite threshold differences are all 0 bps and profile burden ordering is preserved in all 21,792 matched checks.

Optional substitution: use the Study 8E horizon gradient instead of one of the four if the target journal values temporal interpretation.

### Interpretation

Conclude that:

- a guard does not create communication capacity;
- object burden and timing/horizon drive feasibility;
- external observation timing strengthens timing relevance but does not constitute measured operational link performance.

Do not put commit hashes, artifact IDs, or metadata-defect details in the abstract.

## 13. Paper 5 / Study 9 non-overlap controls

The existing non-overlap gate remains mandatory.

Rebuilt Paper 4 must not import as its experimental evidence:

- CuCD-ID;
- AegisSat;
- UNSW-IoTSAT;
- 0/8 semantic-coverage findings;
- action-identifiability results;
- guaranteed sidecar cardinalities;
- Study-2 B0/B1/B2/S1 selector outputs.

Paper 4 may use generic terms such as trust, recovery, state, authorization, or evidence where scientifically necessary, but it must not drift into the Paper-5 question:

> whether public cybersecurity datasets expose sufficient semantic state to identify a recovery action.

Paper 4's question remains:

> whether a defined cryptographic transition can complete under constrained opportunity and what modeled communication burden is required.

## 14. Reader-facing terminology rules

### Preferred

- modeled trusted recovery;
- logical contact;
- observation-opportunity timing;
- hypothetical uniform effective payload rate;
- standardized cryptographic-object burden;
- fixed-capacity feasibility;
- minimum-rate threshold;
- separately frozen evidence populations;
- directional/structural consistency.

### Avoid unless explicitly qualified

- real contact;
- actual throughput;
- operational recovery rate;
- validated spacecraft recovery;
- external replication;
- physical contact capacity;
- satellite link rate;
- real-world success probability.

## 15. Manuscript execution sequence after separate authorization

No step below is executed by this plan.

### Phase A — create derivative source

Create a new venue-neutral derivative directory, recommended:

`publication/Paper_4_Study_8/Rebuilt_Study8_8E/`

Do not edit:

- rejected Acta files;
- frozen `publication/study8/` source package;
- frozen Study 8/8E science.

### Phase B — establish manuscript skeleton

Create:

- manuscript source;
- claim ledger;
- figure/table source directory;
- bibliography working copy;
- manuscript status record.

### Phase C — integrate shared framework and Study 8

Reuse validated Study 8 prose selectively, but reorganize around the new feasibility thesis.

Do not merely append Study 8E to the rejected paper.

### Phase D — integrate Study 8E

Draft Study 8E methods/results directly from frozen authorities.

All timing-descriptor values must be extracted from frozen Results-002 artifacts.

### Phase E — write cross-study synthesis

Use Section 6 rules above.

Every sentence that compares the studies must be checked for:

- no pooled denominator;
- no slot/hour conversion;
- no endpoint equivalence claim;
- no replication language.

### Phase F — literature refresh

Perform a fresh current literature audit covering:

- satellite/NTN PQC;
- crypto agility;
- constrained PQ authentication/key management;
- intermittent connectivity / DTN where relevant;
- SatNOGS/public observation timing context;
- closest post-compromise recovery work.

Literature may strengthen framing but may not alter frozen scientific outcomes.

### Phase G — figures/tables

Generate reader-facing figures from frozen design/results only.

No new endpoint or post-hoc subgroup analysis without separate scientific authorization.

### Phase H — manuscript QA

Validate:

- exact numbers against frozen authorities;
- citations;
- no cross-paper evidence leakage;
- no invalidated Results-001 values;
- no stale result-ID used as scientific identity;
- no operational overclaim;
- no unsupported “first” claim;
- no title/abstract language that equates SatNOGS observation with command contact.

### Phase I — venue audit

Only after the venue-neutral rebuilt manuscript is scientifically coherent:

- perform live scope/requirements review;
- shortlist venues;
- assess word/page/figure constraints;
- select venue under separate author approval.

### Phase J — submission package

Separate authorization required.

## 16. Validation checklist for later manuscript integration

Before any rebuilt manuscript can be considered review-ready:

- [ ] Study 8 primary null exactly preserved.
- [ ] Study 8 profile values exactly preserved.
- [ ] Study 8 contact/deadline values exactly preserved.
- [ ] Study 8 tradeoff values exactly preserved.
- [ ] Study 8E uses Results-002 only.
- [ ] Results-001 never used scientifically.
- [ ] Results-002 metadata discrepancy disclosed in provenance where needed.
- [ ] 20 trace pairs / 476 rows / 454 anchors / 65,376 cases exact.
- [ ] 17,640 finite / 47,736 non-finite exact.
- [ ] 48 / 345 / 57,727 modeled bps exact.
- [ ] 6/12/24 h fractions exact.
- [ ] A0/A1/A2/A3 fractions exact.
- [ ] P3/P1 threshold differences exact.
- [ ] 21,792/21,792 burden ordering exact.
- [ ] No pooled Study 8 + Study 8E denominator.
- [ ] No logical-slot to hour/second conversion.
- [ ] No SatNOGS baud used as throughput.
- [ ] No SatNOGS observation described as authenticated command contact.
- [ ] No Paper-5 datasets/results imported.
- [ ] No operational spacecraft/RF/CPU/energy/certification claim.
- [ ] No policy-superiority claim.
- [ ] Rejected Acta package remains unchanged.

## 17. Gate decision

### PLAN READY

`REBUILT_PAPER4_MANUSCRIPT_INTEGRATION_PLAN_READY`

The architecture, scientific story, research-question placement, section plan, claim ledger, figure/table plan, cross-study synthesis rules, and Paper-5 non-overlap controls are sufficiently defined to proceed to manuscript integration.

### Not authorized by this record

- manuscript prose editing;
- creation of a venue-specific package;
- venue lock;
- new scientific analysis;
- rerunning Study 8 or TRACE-002;
- modifying frozen Study 8 or Study 8E results;
- publisher submission.

## 18. Next explicit gate

`EXPLICIT_REBUILT_PAPER4_MANUSCRIPT_INTEGRATION_EXECUTION_AUTHORIZATION`

If authorized, the next controlled work should create the venue-neutral derivative manuscript directory and execute the integration plan while preserving the rejected Acta package and both frozen scientific records.

Publisher submission remains a later, separate explicit authorization.
