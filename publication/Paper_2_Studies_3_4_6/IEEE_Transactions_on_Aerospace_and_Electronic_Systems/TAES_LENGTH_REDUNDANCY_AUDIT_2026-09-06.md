# TAES Paper 2 Length and Redundancy Audit

**Audit date:** 2026-09-06  
**Target:** IEEE Transactions on Aerospace and Electronic Systems  
**Baseline manuscript commit:** `90bab7b563a360228602b18ab447d00613e1412f`  
**Baseline assembled SHA-256:** `6695737686171f7c5e235c1541504350a9f7af4724e554b290b4ca2389425f05`  
**Scientific rerun authorized or required:** No  
**Current status:** `ACTIVE_BASELINE_MEASUREMENT_AND_EDITORIAL_COMPRESSION_PLANNING`

## Purpose

This audit evaluates manuscript length and redundancy after the scientific, assembled-manuscript, and final IEEE bibliography audits have passed. The purpose is to improve TAES readability and reduce avoidable length without changing frozen Study 3, Study 4, or Study 6 results.

This is an editorial gate. It does not authorize:

- scientific reruns;
- population changes;
- endpoint changes;
- removal of null or conditional findings;
- pooled analysis;
- conversion of logical time to operational time;
- operational flight, safety, mission-availability, RF, CPU, energy, thermal, or certification claims;
- deletion of a limitation merely because it is inconvenient for length.

## Audit principle

The manuscript should not be shortened by deleting evidence. It should be shortened by assigning each idea a clear primary location and removing repeated explanation elsewhere.

The preferred hierarchy is:

1. Introduction states the problem, gap, RQs, contributions, and only the highest-level scope controls.
2. Related Work establishes prior art and novelty boundaries.
3. Section III defines the common abstraction and study separation without re-presenting the full methods of Studies 3, 4, and 6.
4. Sections IV through VI contain the study-specific methods, results, and only the local caveats needed to interpret those results.
5. Section VII synthesizes mechanisms rather than repeating each study narrative.
6. Section VIII is the authoritative home for comprehensive validity and aerospace interpretation boundaries.
7. Section IX states the principal findings and bounded systems conclusion without reproducing the Results sections.

## High-confidence redundancy findings

### 1. Introduction and Related Work

The Introduction currently gives a broad citation-by-citation survey of space cybersecurity, RATS, quorum systems, satellite trust architecture, in-toto, TUF, and SLSA. Section II then develops the same source groups in detail.

Editorial action candidate:

- retain sequential first-use citations in the Introduction;
- compress the literature survey to a shorter positioning paragraph;
- preserve the detailed novelty firewall in Section II.

### 2. Introduction and Section VIII limitation overlap

The Introduction includes separate paragraphs covering structural-zero interpretation, K4 non-operational meaning, provenance non-independence, Study-6 model boundaries, and prohibited operational extrapolation. Section VIII already provides the complete treatment of these limits.

Editorial action candidate:

- retain one compact scope paragraph in the Introduction;
- keep the detailed construct and external-validity controls in Section VIII.

### 3. Section III and Sections IV through VI

Section III currently re-describes substantial study-specific detail before the dedicated study sections repeat it. Examples include:

- the Study-3 timing horizon, onset grid, K0/K4 schedule, V0/V4/V5 treatments, and trajectory count;
- the Study-4 seven-producer 3/2/2 provenance allocation, two experimental blocks, and 4,608-observation construction;
- the Study-6 artifact states, six signals, two blocks, and 420-observation construction.

Editorial action candidate:

- preserve Table I;
- reduce each Study-3/4/6 realization subsection to the minimum needed to define how the common `Q_j(E_j)` / `T_j` abstraction maps to that study;
- leave full design detail in Sections IV, V, and VI.

This is expected to be one of the largest safe reductions.

### 4. Study-specific closing subsections and Section VII

Sections IV, V, and VI each end with a residual-boundary summary. Section VII then restates the same three boundaries before performing the actual synthesis.

Editorial action candidate:

- keep short study-specific closing statements;
- make Section VII start from Table V and cross-study contrasts rather than narrating each study again.

### 5. Study 4 and Study 6 prior-art subsections

Study 4 Section J and Study 6 Section J repeat prior-art distinctions already established in Section II.

Editorial action candidate:

- reduce each to a concise local cross-reference or one short paragraph explaining why the study should not be interpreted as the cited prior art;
- keep substantive prior-art discussion in Section II.

### 6. Table-adjacent prose

Tables II, III, IV, and V preserve results efficiently, but surrounding prose sometimes repeats values that are already visible in the table.

Editorial action candidate:

- keep prose for mechanisms, contrasts, nulls, and interpretation;
- avoid reciting every table value twice.

No table should be removed solely for length at this stage.

### 7. Section VIII as the authoritative limitation section

Section VIII is scientifically strong and should remain comprehensive. It already distinguishes:

- model exactness from external validity;
- Study-3 logical time from operational time;
- synthetic provenance domains from real independence;
- Study-6 Boolean assurance from a real supply-chain experiment;
- qualification availability from mission availability;
- same-repository reproducibility from external replication;
- conceptual use of standards from standards compliance;
- manuscript-level synthesis from an integrated experiment.

Editorial action candidate:

- preserve these controls in Section VIII;
- shorten repeated versions elsewhere rather than weakening Section VIII.

## Mandatory content preservation

The compression pass must preserve at least the following findings explicitly:

### Study 3

- persistent `V5/K0`: `B0` and `S1` 46/46, mean 122.5 logical seconds;
- persistent `V5/K4`: `B0` 46/46 mean 55.326, `S1` 46/46 mean 49.022;
- `B2` structural zeros in the reported frozen cells without universal-superiority wording;
- `V4` affected records do not qualify;
- truthful `V0/K4/B0` pre-onset cache boundary, 3/46 and mean 0.326 logical seconds;
- one-shot versus persistent `V5` temporal distinction;
- only Study 3 models contact.

### Study 4

- complete 18-rule threshold map remains available in Table III;
- first versus systematic failure distinction;
- provenance effects are conditional, including null/equal-threshold results;
- compromise and benign-unavailability populations remain separate;
- synthetic provenance is not demonstrated real independence;
- Study 4 is not a Byzantine-consensus experiment and contains no contact model.

### Study 6

- `G0` through `G5` residual incorrect-state counts and identities;
- `G3` and `G4` equal counts but different residual states;
- benign-loss counts 32/64, 48/64, 48/64, 56/64, 56/64, 63/64;
- `APPROVED_BAD_SOURCE` remains the composite-gate residual state;
- the residual is a frozen-model observability boundary, not a theorem or prevalence estimate;
- assurance-signal unavailability is not contact loss or mission availability.

### Cross-study

- no pooled population, success rate, confidence interval, p-value, common effect size, or global ranking;
- the three studies are not one integrated experiment;
- the synthesis is mechanism-based and qualitative;
- stronger composition closes selected modeled pathways but does not make visible evidence equivalent to hidden or objective truth.

## Measurement helper

`TAES_AUDIT_LENGTH_REDUNDANCY.py` performs a read-only baseline measurement of the canonical assembled manuscript. It reports:

- manuscript-body word count;
- reference-list word count;
- word count for Abstract and Sections I through IX;
- selected interpretation-boundary language counts;
- exact normalized long-sentence duplication across different sections.

The helper does not edit any manuscript file.

## Next decision gate

After baseline metrics are captured, the first editorial pass should prioritize Section III, the Introduction/Related-Work overlap, and Section VII repetition. The manuscript must then be reassembled and re-run through all existing scientific/citation guardrails before any edited draft is committed.

A lower word count by itself is not a pass condition. The pass condition is a shorter manuscript with unchanged scientific results, unchanged claim boundaries, and improved assignment of each idea to one primary section.
