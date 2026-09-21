# Study 8E Current Extension State

**Experiment:** `S8E-ECTV-001`  
**Current-state date:** 2026-09-20  
**Status:** `CORRECTED_CANONICAL_RESULTS_FORMALLY_FROZEN__PAPER4_LIVE_VENUE_ASSESSMENT_R1_COMPLETE__VENUE_LOCK_PENDING`

This file is the primary current-state handoff for Study 8E. Historical protocol, freeze, invalidation, authorization, activation, and execution records remain authoritative for the facts that were true when they were created.

## Current authoritative evidence chain

1. Parent Study 8 `S8-PQC-ICR-001` remains frozen and unchanged.
2. Rejected Acta package `S8-ACTA-PKGFREEZE-002` remains immutable historical provenance.
3. `S8-SATNOGS-POP-001` is historical and invalidated. The qualification filter used stale generated API parameter `satellite__norad_cat_id`.
4. Corrected population `S8E-SATNOGS-POP-002` contains 20 qualifying `norad_cat_id × ground_station` pairs under the frozen 50-request stopping rule.
5. `S8E-SATNOGS-TRACE-002` is the frozen first-page projection of those 20 pairs:
   - 476 observation rows;
   - five persisted fields: `id`, `start`, `end`, `ground_station`, `norad_cat_id`;
   - JSONL SHA-256 `6f80a44fa6cfa63a70df49de3ba447de3d59efe0632208180f26552f37b46a8e`.
6. `S8E-IMPLFREEZE-001` freezes the external continuous-time transition model after synthetic validation.
7. `S8E-CANON-EXEC-001` freezes the real-trace canonical execution protocol.
8. `S8E-CANON-RUNNER-004` is the corrected canonical runner. It repairs the strict-before-horizon sufficient-bound defect and adds an independent bound audit.
9. First canonical result package `S8E-CANON-RESULTS-001` is invalidated before scientific freeze.
10. Corrected canonical execution under `S8E-CANON-GOLIVE-002` completed successfully as GitHub Actions run `35536583594`.
11. Corrected result package `S8E-CANON-RESULTS-002` has been independently audited and hash-bound in `CANONICAL_RESULTS_002_AUDIT_HANDOFF.json`.
12. Formal result freeze `S8E-CANON-RESULTS-002-FREEZE-001` binds the immutable corrected artifact and exact hashes without rewriting the Actions artifact. Manuscript integration was later separately authorized and executed only in the venue-neutral derivative workspace; the frozen result package remains unchanged.
13. Paper-4 architecture/originality gate `publication/Paper_4_Study_8/PAPER4_STUDY8_8E_ARCHITECTURE_AND_NONOVERLAP_GATE_2026-09-20.md` locks Study 8 + Study 8E as one rebuilt Paper 4 while preserving separate populations and Paper-5 independence.
14. Rebuilt-manuscript integration plan `publication/Paper_4_Study_8/REBUILT_STUDY8_8E_MANUSCRIPT_INTEGRATION_PLAN_2026-09-20.md` defines the title direction, study/RQ placement, claim ledger, section architecture, figures/tables, cross-study synthesis rules, and Paper-5 non-overlap controls.
15. Venue-neutral manuscript integration was explicitly authorized and executed in `publication/Paper_4_Study_8/Rebuilt_Study8_8E/`. Study 8 and Study 8E remain separate, unpooled evidence populations.

## Corrected canonical execution

- workflow run: `35536583594`
- execution head: `d49d4ba43c451564f697188ca88deb463895792d`
- artifact ID: `10613372166`
- artifact name: `study8e-canonical-results-002`
- artifact ZIP SHA-256: `3e9c6c7899a9853682d29fa92ea37589c4684db49b16a0a289be054a3553bfee`
- runner tests: 10/10 PASS
- execution passes: 2
- deterministic scientific outputs: byte-identical
- independent case mismatches: 0
- repository drift: none

## Corrected canonical findings

Population:

- traces: 20
- source rows: 476
- eligible anchors: 454
- cases per anchor: 144
- canonical cases: 65,376

Finite minimum-rate feasibility:

- finite thresholds: 17,640 / 65,376 = 245/908 = 0.269824
- non-finite thresholds: 47,736 / 65,376
- finite threshold range: 48 to 57,727 modeled bps
- finite threshold median: 345 modeled bps

By elapsed-time horizon:

- 6 h: 1,152 / 21,792 = 12/227 = 0.052863
- 12 h: 4,488 / 21,792 = 187/908 = 0.205947
- 24 h: 12,000 / 21,792 = 125/227 = 0.550661

By disruption:

- A0: 6,624 / 16,344 finite = 92/227 = 0.405286
- A1: 6,624 / 16,344 finite = 92/227 = 0.405286
- A2: 2,196 / 16,344 finite = 61/454 = 0.134361
- A3: 2,196 / 16,344 finite = 61/454 = 0.134361

Policy/profile findings:

- each of P0, P1, P2, P3 has 4,410 / 16,344 finite cases;
- each of the three frozen cryptographic profiles has 5,880 / 21,792 finite cases;
- P3 vs P1 matched comparisons: 16,344;
- P3/P1 both finite: 4,410;
- P3/P1 both non-finite: 11,934;
- every both-finite P3/P1 minimum-rate difference is exactly 0 bps;
- profile burden ordering preserved: 21,792 / 21,792;
- profile burden ordering violations: 0;
- rollback invocation sums: 0;
- stale epoch acceptance sums: 0.

These are finite-population modeled results for the frozen extension only. They are not physical link-capacity measurements.

## Historical invalidated canonical result

Workflow run `35529423881` produced the first deterministic result package, but post-run adversarial review found a strict-bound defect:

- defective upper bound: `ceil(8B/d_min)`
- corrected upper bound: `floor(8B/d_min) + 1`
- known misclassified cases: 24
- invalidated profile-ordering violations: 4

The invalidated artifact remains historical evidence and must never be used for scientific claims.

## Package metadata note

The corrected artifact has one non-scientific metadata inconsistency:

- `CANONICAL_FINDINGS.json` correctly reports `results_id = S8E-CANON-RESULTS-002`;
- `RESULTS_HASH_MANIFEST.json` retains the stale label `results_id = S8E-CANON-RESULTS-001`.

The hashes inside the manifest correspond to the corrected result files. The immutable Actions artifact is not rewritten. `CANONICAL_RESULTS_002_AUDIT_HANDOFF.json` records the pre-freeze audit, and `CANONICAL_RESULTS_002_FREEZE.json` is the formal authority binding the corrected artifact to `S8E-CANON-RESULTS-002`. The stale label is accepted as a documented non-scientific packaging metadata defect and does not authorize a rerun.

## Claim boundary

Frozen scientific content that may be used only after separate manuscript-integration authorization:

- observation-opportunity timing descriptors for TRACE-002;
- finite/non-finite modeled recovery-threshold counts;
- exact minimum hypothetical uniform effective payload-rate thresholds;
- matched P3/P1 threshold comparisons;
- matched profile-burden ordering;
- modeled state-cost fields and terminal states.

Still prohibited:

- SatNOGS observation equals authenticated/bidirectional command contact;
- transmitter baud equals usable recovery throughput;
- modeled bps equals measured physical link capacity;
- TLE epoch equals cryptographic epoch;
- station/satellite identity equals cryptographic trust;
- original Study 8 logical slots converted to seconds;
- pooling Study 8 and Study 8E populations;
- calling the Study 8E result external replication;
- spacecraft CPU, RF, energy, thermal, flight-memory, ground-station processing, certification, or operational availability claims without new evidence;
- recommending lower-burden cryptography as preferable security.

## Current gate

**Formal corrected-result freeze is complete under `S8E-CANON-RESULTS-002-FREEZE-001`.**

The freeze itself does not authorize manuscript integration, but a later explicit author authorization did authorize venue-neutral manuscript integration. Scientific reanalysis, TRACE-002 reexecution, venue lock, and publisher submission remain unauthorized.

Author/scientific review R1 is complete and passed under `publication/Paper_4_Study_8/Rebuilt_Study8_8E/AUTHOR_SCIENTIFIC_REVIEW_R1_2026-09-21.md` with controlled language refinements only and no scientific change.

Live venue assessment R1 is complete under `publication/Paper_4_Study_8/Rebuilt_Study8_8E/LIVE_VENUE_ASSESSMENT_R1_2026-09-21.md`. IJSCCN is the preferred candidate; Computer Networks is the strongest fallback; International Journal of Information Security is the security-oriented fallback. No venue is locked.

Next controlled sequence:

1. obtain explicit author venue-lock decision;
2. record the selected venue without modifying frozen Study 8/8E science;
3. prepare any venue-specific submission package only after venue lock;
4. require separate explicit final authorization before publisher submission.

Do not rerun TRACE-002 merely to change the stale metadata label unless a new explicit scientific-execution authorization is granted.
