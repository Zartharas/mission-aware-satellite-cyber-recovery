# Rebuilt Paper 4 Manuscript Integration QA — 2026-09-21

**Status:** `INTEGRATED_DRAFT_QA_PASS_WITH_OPEN_PRESENTATION_ITEMS`

## Scope

This QA reviews the first venue-neutral rebuilt Paper 4 manuscript integrating Study 8 and Study 8E.

It does not authorize venue lock or publisher submission.

## Repository-scope audit

Changed files are limited to:

- the new `publication/Paper_4_Study_8/Rebuilt_Study8_8E/` derivative package;
- `docs/CURRENT_PUBLICATION_STATE.md`;
- `study8e/CURRENT_EXTENSION_STATE.md`;
- `study8e/HANDOFF_STATE_20260920.json`.

Confirmed untouched:

- rejected Acta Astronautica package;
- frozen Study 8 scientific source/results;
- frozen Study 8E scientific source/results;
- Paper 5 / Study 9 scientific and manuscript files.

## Frozen Study 8 checks

PASS:

- 3,456 complete deterministic positions retained.
- Each policy = 635/864 = 73.4954%.
- P3 minus P1 = 0.000000 percentage points.
- Profile success = 93.7500%, 64.9306%, 61.8056%.
- Contact-regime P1/P3 values = 79.1667%, 80.0926%, 76.8519%, 57.8704%.
- Logical D12/D24/D48 values preserved.
- Policy state/resource tradeoff values are drawn from the frozen table.
- No logical-slot to physical-time conversion is used.

## Frozen Study 8E checks

PASS:

- formal freeze: `S8E-CANON-RESULTS-002-FREEZE-001`;
- 20 trace pairs;
- 476 source rows;
- 476 merged windows;
- 454 eligible anchors;
- 65,376 canonical cases;
- 17,640 finite cases;
- 47,736 non-finite cases;
- finite fraction 245/908 = 0.269824;
- finite threshold minimum 48 modeled bps;
- finite threshold median 345 modeled bps;
- finite threshold maximum 57,727 modeled bps;
- 6 h fraction 0.052863;
- 12 h fraction 0.205947;
- 24 h fraction 0.550661;
- A0/A1 fraction 0.405286;
- A2/A3 fraction 0.134361;
- each policy finite 4,410/16,344;
- P3/P1 matched count 16,344;
- both finite 4,410;
- every both-finite P3/P1 rate difference = 0 bps;
- each profile finite 5,880/21,792;
- profile ordering preserved 21,792/21,792;
- profile ordering violations = 0;
- rollback/stale-epoch structural sums remain zero.

## Exact artifact verification

The immutable GitHub Actions Results-002 artifact was materialized from artifact ID `10613372166`.

Local SHA-256 verification against the formal freeze:

- `TRACE_TIMING_SUMMARY.csv`
  - observed: `c8f88d5255b56543b915e65e24b2fa24c1f7d513e8cd1e6cb76845d1880b8a2b`
  - expected: same
  - PASS

- `CANONICAL_FINDINGS.json`
  - observed: `9e2ac149d827ff6189983c1b576778d6f31b22dd7218232661a88ecef42e0773`
  - expected: same
  - PASS

- `RESULTS_HASH_MANIFEST.json`
  - observed: `02fbca01d1b45c0e254b9d12c349d4681d424b10805258a24013d17d9118d53f`
  - expected: same
  - PASS

The exact frozen 20-row trace timing summary is copied into the derivative package. No new timing endpoint was computed.

## Citation audit

PASS:

- 17 unique manuscript citation keys;
- all 17 resolve in the derivative bibliography;
- current NIST CSWP authority is `CSWP 39-upd1`;
- FIPS 203, FIPS 204, SP 800-227, IEEE 3536-2026, SatNOGS API documentation, Kim 2026, Ghosh/Nath 2026, De Zuane et al. 2026, GSMA PQ.07, and Eichen et al. are current-verified for the role assigned in the manuscript;
- Eichen et al. is explicitly identified as a preprint.

## Claim-boundary audit

PASS:

- Study 8 and Study 8E are explicitly non-pooled.
- Study 8 logical slots are explicitly nonphysical.
- D12/D24/D48 are explicitly not mapped to 6/12/24 h.
- SatNOGS observations are explicitly not treated as authenticated, bidirectional, or operational command contact.
- SatNOGS transmitter baud is not used as throughput.
- modeled bps is explicitly not measured link capacity.
- Study 8E is explicitly not described as external empirical replication.
- no policy is ranked as an overall winner.
- no smaller cryptographic profile is recommended as better security.
- no spacecraft CPU/RF/energy/thermal/certification performance claim is made.
- invalidated Results-001 is not used scientifically.
- known Results-002 stale metadata label is disclosed as non-scientific provenance.

## Paper 5 non-overlap audit

PASS:

The rebuilt manuscript does not import:

- CuCD-ID;
- AegisSat;
- UNSW-IoTSAT;
- Paper-5 semantic-coverage results;
- action-identifiability results;
- sidecar cardinalities;
- Study-2 B0/B1/B2/S1 selector outputs.

Paper 4 remains a cryptographic-transition feasibility / required-rate-burden paper.

## Current presentation items still open

These are not scientific defects.

1. Final reader-facing figures have specifications but are not yet rendered.
2. Venue-specific article structure, word/page limits, reference style, graphical abstract requirements, and supplementary-file conventions remain unknown until venue selection.
3. The working title is not locked.
4. The abstract may need length reduction after venue selection.
5. A final prose-level anti-overlap / anti-overclaim review should be repeated after figure insertion and any venue-specific condensation.

## QA decision

`PASS__VENUE_NEUTRAL_INTEGRATED_DRAFT_SCIENTIFICALLY_TRACEABLE__FINAL_PRESENTATION_QA_PENDING`

The next recommended gate is:

`AUTHOR_REVIEW__THEN_FINAL_FIGURE_TABLE_RENDERING_AND_VENUE_ASSESSMENT`

Publisher submission remains unauthorized.
