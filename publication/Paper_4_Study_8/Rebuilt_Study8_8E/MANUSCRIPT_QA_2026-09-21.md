# Rebuilt Paper 4 Manuscript QA — 2026-09-21

**Scope:** venue-neutral Study 8 + Study 8E integrated derivative  
**Status:** AUTOMATED_AND_EVIDENCE_QA_PASS__AUTHOR_REVIEW_PENDING

## Files reviewed

- MANUSCRIPT.md
- REFERENCES.bib
- CLAIM_LEDGER.csv
- LITERATURE_REFRESH_2026-09-21.md
- TABLE_1_TWO_STUDY_ARCHITECTURE.csv
- TABLE_5_STUDY8E_RESULTS.csv
- TABLE_6_CROSS_STUDY_SYNTHESIS.csv
- TRACE_TIMING_SUMMARY_RESULTS002.csv
- MANUSCRIPT_STATUS.json

## Structural checks

- Manuscript word count: approximately 6,870 words.
- Citation keys used in manuscript: 19.
- Bibliography keys available: 19.
- Missing bibliography keys: 0.
- Study 8 and Study 8E are presented as separate studies.
- No pooled Study 8 + Study 8E denominator is reported.
- No Study 8 logical slot is converted to seconds/hours.
- No Paper 5 dataset or semantic-interoperability result is imported.

## Frozen Study 8 anchors checked

- population = 3,456;
- each policy = 635/864 = 73.4954%;
- P3-P1 primary contrast = 0.000000 percentage points;
- profile success = 93.7500%, 64.9306%, 61.8056%;
- matched profile ordering = non-increasing success in 1,152/1,152 positions;
- regime/deadline values match frozen reader-facing tables;
- policy-state/resource values match the frozen tradeoff table.

## Frozen Study 8E anchors checked

- result authority = S8E-CANON-RESULTS-002-FREEZE-001;
- traces = 20;
- source rows = 476;
- eligible anchors = 454;
- cases = 65,376;
- finite = 17,640;
- non-finite = 47,736;
- finite fraction = 0.269824;
- finite modeled threshold min/median/max = 48 / 345 / 57,727 bit/s;
- 6 h finite fraction = 0.052863;
- 12 h finite fraction = 0.205947;
- 24 h finite fraction = 0.550661;
- A0/A1 finite fraction = 0.405286;
- A2/A3 finite fraction = 0.134361;
- each policy finite = 4,410/16,344;
- each profile finite = 5,880/21,792;
- P3/P1 both-finite equal-threshold count = 4,410;
- profile burden ordering preserved = 21,792/21,792;
- structural rollback/stale-epoch sums remain zero.

## Frozen timing extract

The derivative timing table is copied from the immutable corrected Results-002 artifact file:

- source file: TRACE_TIMING_SUMMARY.csv;
- frozen source SHA-256: c8f88d5255b56543b915e65e24b2fa24c1f7d513e8cd1e6cb76845d1880b8a2b;
- derivative rows: 20;
- manuscript reports only descriptive ranges read from that frozen summary.

No source-row re-selection or new endpoint computation was performed.

## Literature QA

Current literature refresh confirms:

- NIST CSWP 39upd1 supersedes the earlier CSWP 39 final and is used in the derivative bibliography;
- De Zuane et al. 2026 and Eichen et al. 2026 are labeled as arXiv preprints;
- the current SatNOGS Network API documentation is cited only for source/API semantics;
- no unsupported priority or "first" novelty claim is used.

## Claim-boundary checks

The manuscript does not claim:

- SatNOGS observation = authenticated/bidirectional command contact;
- transmitter baud = payload throughput;
- modeled bit/s = measured physical link capacity;
- Study 8 logical slots = physical elapsed time;
- Study 8E = external empirical replication;
- operational spacecraft/RF/CPU/energy/thermal/certification performance;
- one P0-P3 policy is generally superior;
- a lower-burden cryptographic profile should be selected because of these results.

## Cross-publication checks

No changed file is under:

- publication/Paper_5_Study_9/
- study9/

No manuscript reference to CuCD-ID, AegisSat, UNSW-IoTSAT, Paper-5 0/8 coverage, action-identifiability, or guaranteed sidecar-state results is present.

## Repository-scope checks

Branch changes do not modify:

- publication/Paper_4_Study_8/Acta_Astronautica/
- frozen study8/ scientific files;
- frozen Study 8E protocol/result/source/runner files;
- Paper 5 science or manuscript.

## Known remaining publication work

This QA pass does not mean the manuscript is submission-ready.

Still pending:

1. author review of the integrated narrative;
2. reader-facing figure generation;
3. optional tightening of prose after author review;
4. live venue assessment;
5. venue-specific formatting/length compliance;
6. venue-specific AI-disclosure check;
7. final reference-format audit for the selected journal;
8. separate package freeze;
9. separate final publisher-submission authorization.

## Decision

**PASS for integrated venue-neutral manuscript review.**

The next gate is author review / controlled manuscript refinement. Live venue assessment should occur only after the author accepts the scientific architecture and narrative.
