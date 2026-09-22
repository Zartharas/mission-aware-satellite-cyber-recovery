# Paper 4 IJSCCN R5 Source Preservation Audit

**Audit date:** 2026-09-22 UTC / 2026-09-21 America/Chicago  
**R5 source:** `publication/Paper_4_Study_8/IJSCCN/MANUSCRIPT_IJSCCN_R5.md`  
**Historical R4.x source:** `publication/Paper_4_Study_8/IJSCCN/MANUSCRIPT_IJSCCN.md`  
**Venue-neutral scientific source:** `publication/Paper_4_Study_8/Rebuilt_Study8_8E/MANUSCRIPT.md`  
**Claim ledger:** `publication/Paper_4_Study_8/Rebuilt_Study8_8E/CLAIM_LEDGER.csv`

## 1. Purpose

This audit verifies that the initial R5 source rebuild changes manuscript architecture and presentation without modifying the frozen scientific results, evidence boundaries, or Paper 4 / Paper 5 separation.

No scientific rerun or statistical reanalysis was performed.

## 2. Structural improvement scan

| Check | Historical R4.x | R5 source | Result |
| --- | ---: | ---: | --- |
| Approximate words | about 7,011 | about 5,736 | Reduced fragmentation and repetition |
| Visible headings | 71 | 28 | PASS |
| Markdown bullet lines | 69 | 0 | PASS |
| Abstract words | 213 previously recorded | 211 | PASS, journal limit 250 |
| Short-title characters | 63 | 63 | PASS, journal limit 70 |
| Em-dash characters | 9 previously recorded | 0 | PASS |
| Citation keys in R5 | not applicable to comparison | 19 | All resolve |
| Missing bibliography keys | not applicable | 0 | PASS |

The R5 source is a new file. The R4.x manuscript source remains unchanged for historical comparison and provenance.

## 3. Claim-ledger preservation

All 24 frozen claim-ledger classes are represented without prohibited overreach.

| Claim gate | R5 preservation check | Status |
| --- | --- | --- |
| P4-C01 | Study 8 complete deterministic population = 3,456 | PASS |
| P4-C02 | All four policies = 635/864 = 73.4954% | PASS |
| P4-C03 | P3 minus P1 = 0.000000 percentage points | PASS |
| P4-C04 | Profile success = 93.7500%, 64.9306%, 61.8056% | PASS |
| P4-C05 | 1,152 matched Study 8 positions preserve non-increasing object-burden success | PASS |
| P4-C06 | Equal full-cycle capacity = 65,536 bytes with different regime success | PASS |
| P4-C07 | D12/D24/D48 = 32.6389%, 87.8472%, 100% for P1/P3 | PASS |
| P4-C08 | Policy exposure/availability/overlap/resource tradeoffs retained without overall ranking | PASS |
| P4-C09 | Study 8E = 20 trace pairs, 476 source rows, 454 anchors, 65,376 cases | PASS |
| P4-C10 | Frozen observation-opportunity timing ranges retained | PASS |
| P4-C11 | 17,640 / 65,376 finite | PASS |
| P4-C12 | Finite threshold 48 to 57,727 modeled bit/s; median 345 | PASS |
| P4-C13 | Horizon fractions 5.2863%, 20.5947%, 55.0661% | PASS |
| P4-C14 | A0/A1 = 40.5286%; A2/A3 = 13.4361% | PASS |
| P4-C15 | Each policy = 4,410 finite and 11,934 non-finite | PASS |
| P4-C16 | All 4,410 both-finite P3/P1 differences = 0 bit/s | PASS |
| P4-C17 | Each profile = 5,880 / 21,792 finite | PASS |
| P4-C18 | Profile burden ordering preserved in 21,792 / 21,792 comparisons | PASS |
| P4-C19 | No P3 feasibility advantage on either study's respective endpoint | PASS |
| P4-C20 | Longer allowed recovery time expands the feasible set qualitatively only | PASS |
| P4-C21 | Fixed-capacity feasibility and solved-rate burden remain distinct estimands | PASS |
| P4-C22 | SatNOGS observations remain timing proxies only | PASS |
| P4-C23 | Modeled bit/s remains explicitly not measured throughput | PASS |
| P4-C24 | Paper 5 / Study 9 datasets, endpoints, and results remain excluded | PASS |

## 4. Corrected Study 8E authority checks

The R5 source retains:

- `S8E-SATNOGS-POP-002`;
- `S8E-SATNOGS-TRACE-002`;
- trace SHA-256 `6f80a44fa6cfa63a70df49de3ba447de3d59efe0632208180f26552f37b46a8e`;
- corrected runner `S8E-CANON-RUNNER-004`;
- corrected result freeze `S8E-CANON-RESULTS-002-FREEZE-001`;
- corrected canonical run 35536583594;
- artifact 10613372166;
- artifact ZIP SHA-256 `3e9c6c7899a9853682d29fa92ea37589c4684db49b16a0a289be054a3553bfee`;
- packaging-only stale Results-001 manifest-label discrepancy.

The invalidated Results-001 package is not used for scientific claims.

## 5. Strict-before-horizon bound check

R5 defines the corrected sufficient bound self-containedly:

- `B = sum(profile_object_bytes) + max(profile_object_bytes)`;
- `d_min` = shortest positive future observation-opportunity duration in exact seconds;
- `U_strict = floor(8B/d_min) + 1` integer bit/s.

The source explicitly states that this is a model-search sufficiency construction rather than measured physical capacity or SatNOGS throughput.

**Status:** PASS.

## 6. Study 8 logical-time boundary

The R5 source states that Study 8 slots are ordering units with no physical duration and prohibits conversion to seconds, minutes, orbital periods, or elapsed-time horizons.

**Status:** PASS.

## 7. Paper 4 / Paper 5 non-overlap scan

The R5 source contains zero occurrences of the protected Paper 5 dataset/result tokens checked in this audit:

- CuCD-ID;
- AegisSat;
- UNSW-IoTSAT;
- the Paper 5 0/8 semantic-coverage result;
- B0/B1/B2/S1 selector identifiers.

The R5 Introduction explicitly states that Paper 4 uses none of Paper 5's datasets, endpoints, or results.

**Status:** PASS.

## 8. Citation integrity

R5 contains 19 citation keys and all resolve in `REFERENCES.bib`.

The De Zuane record is the peer-reviewed IEEE LANMAN 2026 paper, DOI `10.1109/LANMAN69841.2026.11623493`.

A formal repository/data citation was added as `Singh_Paper4_Repository_2026`. No GitHub Release existed when checked during this audit, so the citation uses immutable repository commit:

`4ed95a53ade99ddabacbe7c542a3f29d988ecfd0`

This commit contains the frozen scientific evidence authorities used by the manuscript. The data-citation identity may be rebound to a later deliberately frozen archival release before final submission if such a release is separately authorized.

## 9. AI disclosure placement

R5 moves the substantive OpenAI ChatGPT / GPT-5.6 Sol disclosure into Methods and preserves the scientific boundary that AI did not generate or alter:

- Study 8 data;
- Study 8E data;
- protocols;
- canonical result files;
- evidence hashes;
- prespecified endpoints;
- corrected Results-002 findings.

**Status:** PASS.

## 10. Publisher-facing punctuation

The R5 manuscript source contains zero em-dash characters.

A separate builder defect remains open: the existing reference renderer converts LaTeX triple hyphens to an em dash. The R5 Word builder must be corrected before publisher-facing DOCX generation is accepted.

## 11. Remaining gates

The source-preservation gate covers scientific content only. The following remain open:

1. update the Word build pipeline to consume `MANUSCRIPT_IJSCCN_R5.md`;
2. insert References at the explicit R5 marker;
3. place Figure Legends after References;
4. put Table 1 and Table 2 on separate pages after References;
5. generate separate publication-quality figure files at journal-appropriate resolution;
6. eliminate reference-renderer em-dash generation;
7. build the public-safe R5 DOCX;
8. inspect every page and every figure visually;
9. inspect document metadata, comments, tracked changes, hidden text, and private-data leakage;
10. run final portal-instance checks before upload.

**R5 scientific source-preservation gate: PASS.**

**R5 DOCX visual/publisher gate: NOT YET PASSED.**

**Final Wiley submission: NOT AUTHORIZED.**
