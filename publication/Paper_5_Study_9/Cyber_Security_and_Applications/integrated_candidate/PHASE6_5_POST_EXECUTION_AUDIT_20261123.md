# Phase 6.5 — canonical report audit

CANONICAL_PASS / POST_RUN_TECHNICAL_AUDIT_PASS. One author-operated attempt; no rerun, source data access, protocol change, raw report upload, merge or submission.

Activation aa81959317a0c3fae6bfcfe9891175bf6ff07bfe; qualified payload 23e36944b03c6b45e2bf6c0eda0bdb480d03e3d5; preflight d2bcaf82e08b751f7e49332e489d96f749cbdd14. Activation blob c51d4cd4688077bc081adad23c9ba7ce033ade9c and authorization blob 8ab6997748e93870050f031d752aac5a7fc622dc match repository readback. Activation-head CI 45307596091, 45307596112, 45307596267 all success when checked after execution; connector did not provide completion timestamps, so their ordering relative to local start is not independently established. Preflight-head CI had previously passed. Attempt started 2026-11-24T01:52:06.141536+00:00; offline confirmation is operator-reported.

Uploaded exact bytes, independently SHA-256 hashed and strictly JSON parsed:
- attempt.json (611 bytes): e1e373dc9b22863990350dd9838c2535318d3850823e9f413209c5703b229a36
- report.json (34,862,894 bytes): dc230908147872314b10340b7e0f8819c54285edeb35e063f2007ae0532f7e45
- SHA256_MANIFEST.json (215 bytes): 6f7fd9a624fa9adeef5f4fb20d672d51d1ccd332c989177c54ef639f2e89fcfd

Report and manifest PASS; stage COMPLETE; canonical_execution true; failures empty. Hashes match terminal and internal manifest. Full report retained locally. Expected rows reconstructed as sorted indented UTF-8 JSON with final LF match frozen reference digest f73e09dba34de0fba45982f3a9d5ec24c7ae3ef99c0b2079c240c8066b08c4b2. 72 unique routing keys and case/family ordering match frozen routing manifest. Candidate outcomes and duplicate report sections agree. All eight ledger oracle objects equal actual diagnostics. All 17 metamorphic IDs and 25 observed signatures match frozen base signatures and multiplicity. All 12 per-family/method metric records and confusion counts recalculated from retained row signatures. Recorded transformations checked, not rerun.

## Mapping results
64 mapping endpoints: DIRECT 25, DERIVABLE 11, AMBIGUOUS 18, ABSENT 10; ADMIT true 13, false 10; UNKNOWN 29, UNKNOWN_MISSING 6, REJECT_INVALID 6. All 72 full outputs match expectations.

| Family | Method | Exact class | Exact admission/value | False admission | False rejection | Known false to unknown |
|---|---|---:|---:|---:|---:|---:|
| All 64 | candidate | 64 | 64 | 0/41 | 0/23 | 0/10 |
| All 64 | name-only | 35 | 36 | 11/41 | 7/23 | 2/10 |
| All 64 | always-unknown | 10 | 29 | 0/41 | 23/23 | 10/10 |
| Target 48 | candidate | 48 | 48 | 0/32 | 0/16 | 0 |
| Target 48 | name-only | 32 | 32 | 10/32 | 0/16 | 0 |
| Target 48 | always-unknown | 8 | 24 | 0/32 | 16/16 | 8 |
| Derivation 12 | candidate | 12 | 12 | 0/6 | 0/6 | 0 |
| Derivation 12 | name-only | 0 | 2 | 0/6 | 6/6 | 2 |
| Derivation 12 | always-unknown | 0 | 2 | 0/6 | 6/6 | 2 |
| Challenge mapping 4 | candidate | 4 | 4 | 0/3 | 0/1 | 0 |
| Challenge mapping 4 | name-only | 3 | 2 | 1/3 | 1/1 | 0 |
| Challenge mapping 4 | always-unknown | 2 | 3 | 0/3 | 1/1 | 0 |

All groups zero wrong admitted values and unknown-to-false transitions. Ledger C-03 duplicate all null; C-04 incomplete null except known contact true; C-05 missing M/Q false; C-06 M true Q false; C-07 required conflict C true M false; C-08 unrelated conflict C true M/Q true; C-09 rejected extra signature false M/Q true; C-11 authorization unavailable M/Q true.

## Post-run logical audit
Separate Python checker (no original candidate, selector or oracle imports) constructs complete-state bitsets using stated model conditions, adds each state's ternary projections to compatible observation masks, independently evaluates policy truth branches, obtains action images by intersecting label masks, enumerates increasing-size unknown-coordinate subsets and tests all refinements for multi-action cells. Compared exact completion counts, action sets and all tied minima for every unique endpoint; empties require null action/minimum fields. All 78,732 passed. Nested common nonempty slices: action inclusion and nonincreasing minimum size all passed. All-unknown archived F0 exact actions/minima matched. This is post-run analysis, not a second canonical experiment.

| Model | States | Feasible observations | Inconsistent observations | Evaluable endpoints | Inconsistent endpoints |
|---|---:|---:|---:|---:|---:|
| F0 | 256 | 6561 | 0 | 26244 | 0 |
| F1 | 192 | 5832 | 729 | 23328 | 2916 |
| F2 | 132 | 4662 | 1899 | 18648 | 7596 |
| Total | — | — | — | 68220 | 10512 |

| Policy | All-unknown action count (each model) | F0 minimum indices | F1 minimum indices | F2 minimum indices |
|---|---:|---|---|---|
| B0 | 2 | 0,1,2,3,4,5 | 0,1,2,3,5 | 5 |
| B1 | 2 | 0,1,2,3,4,5,6 | 0,1,2,3,5,6 | 5,6 |
| B2 | 3 | 0,1,2,3,4,5,6 | 0,1,2,3,5,6 | 5,6 |
| S1 | 3 | 0,1,2,3,4,5,6,7 | 0,1,2,3,5,6,7 | 5,6,7 |

Order S,T,F,E,C,M,G,A. Primary minima unique. Post-run descriptive counts: common feasible observations per policy F0/F1=5832, F1/F2=4662, F0/F2=4662. Strict minimum reduction B0/B1/B2/S1 respectively 288/192/288/288; 540/360/540/540; 558/372/558/558. Strict action-count reduction respectively 9/3/9/9; 270/90/270/270; 279/93/279/279. No population inference.

## Adversarial interpretation
Positive controls address all-negative discrimination but authored visible vocabulary and expectations are not blinded independent coding. F1/F2 logical outer approximations depend on named scope and whole-snapshot guarantees; establishing M and guarantees can itself require substantial evidence. Neither physical feasibility nor another independently justified recovery interface is tested. No real cryptographic verification, flight outcomes, original source replay, full RQ-E3 semantic transitions or optional Hack-A-Sat contrast. Original S9/S10 and G3 unchanged. Raw report not uploaded; final author attestations, rights review, fresh editorial review and publisher submission remain separate.
