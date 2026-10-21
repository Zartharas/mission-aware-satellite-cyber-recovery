# Paper 4 Study 8 + Study 8E Architecture and Cross-Publication Non-Overlap Gate

**Gate date:** 2026-09-20  
**Gate status:** `PASS__PAPER4_STUDY8_PLUS_STUDY8E_ARCHITECTURE_LOCKED__PAPER5_NON_OVERLAP_CONFIRMED__MANUSCRIPT_INTEGRATION_NOT_YET_EXECUTED`  
**Scoped branch:** `paper4/study8-8e-architecture-nonoverlap-gate`  
**Base main commit:** `1a7748fc1d3ef441b55fb4034351724e2d7dd37f`

## 1. Purpose and author decision

The author explicitly selected the following publication architecture:

> **Study 8 + Study 8E -> rebuilt Paper 4**

This record formalizes that choice before any Paper-4 manuscript integration. It also establishes a hard self-overlap boundary between rebuilt Paper 4 and Paper 5 / Study 9.

The objective is to strengthen Paper 4 for a new venue by combining two separately frozen evidence layers in one manuscript:

1. **Study 8 / `S8-PQC-ICR-001`** — the controlled deterministic cryptographic-transition/contact-budget experiment; and
2. **Study 8E / `S8E-ECTV-001`** — the separately governed external observation-opportunity timing extension.

The two study populations remain scientifically separate. This architecture does **not** pool their observations or reinterpret Study 8E as an empirical replication of Study 8.

## 2. Governance effect

This is a publication-architecture and originality-control record only.

It does **not**:

- modify frozen Study 8 science;
- modify frozen Study 8E science;
- rerun TRACE-002;
- rewrite any GitHub Actions result artifact;
- modify Paper 5 / Study 9 science or manuscript;
- modify the rejected Acta Astronautica package;
- authorize publisher submission;
- authorize scientific reanalysis.

The exact rejected Acta package remains immutable historical provenance.

## 3. Rebuilt Paper 4 scientific lane

### 3.1 Study 8 role

Study 8 asks:

> How do cryptographic-transition strategies change the ability to restore trusted control within finite intermittent-contact budgets after credential or cryptographic-state compromise?

Its scientific mechanism is the frozen cryptographic transition state machine and its P0-P3 policies using standardized ML-KEM / ML-DSA object-size budgets.

Its evidence includes:

- 3,456 deterministic finite modeled positions;
- synthetic deterministic contact schedules;
- four recovery policies P0-P3;
- three frozen cryptographic profiles;
- four disruption schedules;
- exact modeled transition-object byte burdens;
- terminal recovery/failure states;
- frozen primary result `P3 - P1 = 0/1 = 0.000000 percentage points`.

### 3.2 Study 8E role

Study 8E asks whether the frozen Study-8 transition semantics remain feasible or structurally consistent when synthetic timing is replaced by prospectively governed external observation-opportunity timing.

Its frozen corrected evidence includes:

- formal result freeze: `S8E-CANON-RESULTS-002-FREEZE-001`;
- `S8E-SATNOGS-POP-002`;
- `S8E-SATNOGS-TRACE-002`;
- 20 satellite-station trace pairs;
- 476 frozen SatNOGS observation rows;
- 454 eligible anchors;
- 65,376 canonical cases;
- 17,640 finite modeled minimum-rate cases;
- 47,736 non-finite cases;
- finite modeled thresholds from 48 to 57,727 bps;
- 16,344 matched P3/P1 comparisons;
- zero P3/P1 threshold differences whenever both cases are finite;
- 21,792/21,792 preserved cryptographic-profile burden orderings;
- zero profile-ordering violations.

Study 8E uses SatNOGS timing only as an **observation-opportunity timing proxy**. It does not establish authenticated command contact, measured payload throughput, operational spacecraft availability, or physical link capacity.

### 3.3 Combined Paper-4 contribution

The rebuilt Paper 4 may present a two-layer argument:

> Study 8 establishes the controlled deterministic cryptographic-transition behavior under frozen intermittent-contact assumptions; Study 8E independently evaluates the corresponding recovery burden and feasibility against prospectively governed public observation-opportunity timing without pooling the two populations or converting Study-8 logical slots to physical time.

The combined paper is therefore centered on:

**cryptographic-transition feasibility and communication burden under intermittent contact, strengthened by an external timing sensitivity layer.**

## 4. Paper 5 protected scientific lane

Paper 5 / Study 9 is:

- **Experiment:** `S9-RTSI-001`
- **Study 9 protocol title:** *Recovery-State Transfer and Semantic Interoperability Across Public Space-Cyber Datasets*
- **Paper 5 manuscript title:** *Recovery-State Semantic Interoperability and Decision Identifiability Across Public Space-Cyber Datasets*
- **Target manuscript line:** Cyber Security and Applications

Its scientific question is different:

> Do independently sourced public space-cyber datasets expose enough semantically valid recovery state to identify a downstream recovery action without imputing unavailable state?

Its evidence population is:

- CuCD-ID v3;
- AegisSat 2025;
- UNSW-IoTSAT 2026.

Its principal endpoints are:

- recovery-state mapping classes;
- direct and direct-or-derivable semantic coverage;
- row-level reachable action-set size;
- unique-action identifiability;
- guaranteed minimal sidecar state;
- common versus dataset-specific missing semantics.

Its frozen findings include:

- 0/8 direct coverage for all three datasets;
- 0/8 direct-or-derivable coverage for all three datasets;
- zero uniquely identifiable action fraction across all 12 dataset-policy strata;
- guaranteed sidecar cardinalities of 6, 7, 7, and 8 for the four frozen Study-2 downstream policies.

Paper 5 does **not** evaluate cryptographic transition-object burden, SatNOGS observation timing, P0-P3 transition policies, ML-KEM/ML-DSA recovery bundles, or minimum effective payload-rate thresholds.

## 5. Paper 4 versus Paper 5 non-overlap determination

| Dimension | Rebuilt Paper 4 — Studies 8 + 8E | Paper 5 — Study 9 |
| --- | --- | --- |
| Primary question | Can a defined cryptographic recovery transition complete under finite intermittent contact, and what modeled communication burden is required? | Does existing public cyber data expose enough semantic state to identify a recovery action? |
| Experimental mechanism | Cryptographic transition state machine | Semantic state projection into a frozen downstream selector |
| Evidence populations | Study-8 finite modeled contact population + frozen SatNOGS observation timing | CuCD-ID, AegisSat, UNSW-IoTSAT |
| Policy family | P0, P1, P2, P3 | Study-2 B0, B1, B2, S1 |
| Cryptographic object burden | Primary scientific quantity | Not an endpoint |
| Minimum modeled rate | Study-8E primary quantity | Not an endpoint |
| Semantic recovery-state coverage | Not an endpoint | Primary endpoint |
| Unique action identifiability | Not an endpoint | Primary endpoint |
| Minimal sidecar state | Not an endpoint | Primary endpoint |
| SatNOGS timing | External timing evidence | Not used |
| Public cyber-dataset semantic mapping | Not used | Core method |

**Determination:** `SCIENTIFIC_OVERLAP_LOW__PUBLICATION_INDEPENDENCE_CONFIRMED`

The two papers share a broader satellite cyber-recovery program and some terminology, but they do not share the same research question, experimental population, intervention/mechanism, primary endpoints, policy family, or canonical result set.

## 6. Hard self-overlap controls for rebuilt Paper 4

A rebuilt Paper 4 must **not**:

1. use CuCD-ID, AegisSat, or UNSW-IoTSAT as Paper-4 experimental evidence;
2. report Paper-5 semantic-coverage results as Paper-4 findings;
3. import the Paper-5 0/8 coverage result;
4. import Paper-5 action-identifiability fractions;
5. import Paper-5 guaranteed-sidecar cardinalities 6/7/7/8;
6. treat the frozen Study-2 B0/B1/B2/S1 selectors as the Paper-4 recovery mechanism;
7. claim novelty for semantic interoperability, cross-dataset recovery-state mapping, or minimal-sidecar derivation;
8. reuse Paper-5 tables, figures, result rows, or quantitative evidence as if generated by Studies 8 or 8E;
9. pool any Paper-5 dataset rows with Study 8 or Study 8E;
10. describe Study 8E as validating whether public cybersecurity datasets expose recovery-state semantics.

Paper 4 may cite Paper-5 concepts or future publication output only as related work where scientifically necessary and with explicit attribution.

## 7. Reciprocal protection of Paper 5

Paper 5 must remain outside the Paper-4 cryptographic-transition lane.

Paper 5 must not silently import as its own evidence:

- Study-8 P0-P3 transition-policy results;
- Study-8 cryptographic object-size budgets;
- Study-8 3,456-position population;
- Study-8E SatNOGS trace population;
- Study-8E 65,376 cases;
- Study-8E minimum modeled payload-rate thresholds;
- Study-8E horizon/disruption feasibility results;
- Study-8E P3/P1 threshold contrasts.

Cross-paper citation is permitted; experimental evidence reuse is not.

## 8. Separation from Papers 1-3

The rebuilt Paper 4 remains publication-independent from the submitted Papers 1-3.

- **Paper 1 / Studies 1+2:** deterministic mission-aware response/recovery under contact and adversarial evidence constraints.
- **Paper 2 / Studies 3+4+6:** temporal evidence persistence, producer/provenance composition, and recovery-artifact assurance.
- **Paper 3 / Study 7:** learned-selector observability and hidden-truth information limits.
- **Rebuilt Paper 4 / Studies 8+8E:** cryptographic transition burden and trusted post-compromise recovery feasibility under intermittent contact with an external timing layer.
- **Paper 5 / Study 9:** semantic interoperability and downstream decision identifiability across public datasets.

Earlier studies may be cited as antecedent work or architectural lineage, but their frozen observations must not be silently reused as Paper-4 experimental evidence.

## 9. Study 8 / Study 8E integration boundary

Integration into one manuscript does not erase the scientific separation between the studies.

The rebuilt Paper 4 must:

- identify Study 8 and Study 8E as separate studies;
- report their populations separately;
- avoid a pooled sample/case count;
- avoid pooled inferential statistics;
- preserve the original Study-8 negative/null policy result;
- preserve Study-8E finite/non-finite findings exactly;
- preserve the Study-8E metadata-discrepancy note;
- preserve the distinction between logical Study-8 contact slots and physical elapsed-time horizons in Study 8E;
- avoid calling Study 8E an external empirical replication;
- distinguish modeled effective payload rate from measured physical throughput.

## 10. Gate decision

### GO

`GO__REBUILD_PAPER4_AS_STUDY8_PLUS_STUDY8E_TWO_STUDY_MANUSCRIPT`

Rationale:

- Study 8 and Study 8E form a coherent mechanism-to-external-timing evidence chain;
- Study 8E directly strengthens the external-timing relevance of the original Paper-4 argument;
- Study 8E remains separately frozen, so scientific provenance is preserved;
- Paper 5 remains independently publishable because its question, data, method, endpoints, and results are materially different;
- Papers 1-3 retain separate scientific lanes and frozen evidence populations.

### NO-GO

- `NO_GO__SPLIT_STUDY8E_INTO_SEPARATE_PAPER_BY_DEFAULT`
- `NO_GO__POOL_STUDY8_AND_STUDY8E_POPULATIONS`
- `NO_GO__IMPORT_PAPER5_SEMANTIC_INTEROPERABILITY_RESULTS_INTO_PAPER4`
- `NO_GO__REUSE_PAPER5_DATASETS_AS_PAPER4_EVIDENCE`
- `NO_GO__ALTER_FROZEN_STUDY8_OR_STUDY8E_RESULTS_FOR_VENUE_FIT`
- `NO_GO__MODIFY_REJECTED_ACTA_PACKAGE`

## 11. Next gate

The architecture decision is now fixed.

The next controlled gate is a **rebuilt Paper-4 manuscript integration plan**, which should:

1. define the revised Paper-4 title and contribution statement;
2. define explicit Study-8 and Study-8E research-question placement;
3. map each manuscript claim to one frozen evidence source;
4. design separate methods/results subsections for Study 8 and Study 8E;
5. define the cross-study synthesis without statistical pooling;
6. update the literature-positioning strategy;
7. retain this Paper-4/Paper-5 non-overlap gate as a hard drafting constraint;
8. perform live venue assessment only after the rebuilt manuscript architecture is stable.

Actual manuscript editing and publisher submission remain separate controlled actions.

## Canonical authorities used

### Paper 4 / Study 8

- `study8/STUDY8_PROTOCOL.json`
- `study8/STUDY8_CLAIM_BOUNDARY.md`
- `study8/STUDY8_TECHNICAL_CLOSE.json`
- `publication/Paper_4_Study_8/Acta_Astronautica/ACTA_SUBMISSION_STATUS.json`

### Study 8E

- `study8e/STUDY8E_PROTOCOL.json`
- `study8e/CURRENT_EXTENSION_STATE.md`
- `study8e/CANONICAL_RESULTS_002_AUDIT_HANDOFF.json`
- `study8e/CANONICAL_RESULTS_002_FREEZE.json`

### Paper 5 / Study 9

- `study9/STUDY9_PROTOCOL.json`
- `study9/results/RESULTS_FREEZE.json`
- `publication/Paper_5_Study_9/Cyber_Security_and_Applications/MANUSCRIPT_EVIDENCE_NOVELTY_AUDIT.md`
- `publication/Paper_5_Study_9/Cyber_Security_and_Applications/MANUSCRIPT_CREATION_STATUS.json`

### Cross-publication state

- `docs/CURRENT_PUBLICATION_STATE.md`
- `docs/PAPER3_STUDY7_PUBLICATION_BOUNDARY_AND_ORIGINALITY_GATE_2026-09-07.md`

Historical records remain provenance and are not rewritten by this gate.
