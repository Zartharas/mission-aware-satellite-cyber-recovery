# Phase-1 Theory Verification Audit

**Base commit:** `972a273f699cc1df39597f358e0fdb5369de342a`  
**Mode:** read-only audit of frozen repository artifacts  
**New scientific execution:** none

## Inputs

- `study3/STUDY3_PROTOCOL.json`
- `study3/results/canonical/cell_summary.csv`
- `study4/STUDY4_PROTOCOL.json`
- `study4/results/canonical/thresholds.csv`
- `study6/STUDY6_PROTOCOL.json`
- `study6/results/CANONICAL_GATE_SUMMARY.csv`

## Study 3 verification

- evidence lifetime = 5 logical seconds;
- K4 truthful-V0 / B0 false qualification occurs in 3 of 46 onset phases;
- mean exposure = `3 * 5 / 46 = 0.3260869565` logical seconds, matching the canonical summary;
- persistent V5 produces unsafe qualification in 46/46 K4 B0 and 46/46 K4 S1 trajectories;
- B2 remains 0/46 in those V5 cells.

Result: `PASS`.

## Study 4 verification

The closed-form formulas in `CROSS_STUDY_THEORY_DERIVATION_R1_2026-09-26.md` were checked against all 36 frozen threshold-summary rows.

- rows checked: 36;
- mismatches: 0.

Result: `PASS`.

## Study 6 verification

`CLEAN_APPROVED` and `APPROVED_BAD_SOURCE` have identical six-signal gate-visible evidence and opposite objective correctness. The canonical gate summary reports `APPROVED_BAD_SOURCE` as unsafe-qualified under all six gates.

The formula `2^6 - 2^(6-r)` reproduces benign-loss counts `32,48,56,63` for gates requiring `1,2,3,6` signals.

Result: `PASS`.

## Interpretation

This audit strengthens explanation and analytical generality of frozen results. It adds no observations, reruns no campaign, alters no endpoint, and is not external replication.
