# S6X Pre-Runtime Validator Defect Fix — 2026-09-26

**Status:** `TOOLING_DEFECT_IDENTIFIED_AND_CORRECTED__NO_SCIENTIFIC_EXECUTION`

## Trigger

The first local S6X pre-runtime run reached the pinned NASA cFS/LC source successfully, initialized the exact LC submodule commit, and passed the independent invariant-oracle unit tests.

The run then stopped with:

`baseline GT expression count is not exactly one`

## Root cause

The validator searched the entire pinned `lc_watch.c` file for this exact expression:

`EvalResult = (WPValue > CompareValue) ? LC_WATCH_TRUE : LC_WATCH_FALSE;`

At LC commit `a1c3a47ea1fa5c0d7751d6ff88848dc9bd8a6c7a`, that exact text occurs twice:

1. once in `LC_SignedCompare`;
2. once in `LC_UnsignedCompare`.

The corresponding `>=` expression also occurs twice.

Therefore the failure was caused by an over-broad validator uniqueness check. It was **not** a source-pin mismatch, not an upstream NASA defect, not a failed invariant, and not a scientific result.

## Correction

The validator now isolates the source region from:

`uint8 LC_SignedCompare(`

up to:

`uint8 LC_UnsignedCompare(`

and applies the exact-one GT and GE checks only inside that signed-comparison region.

A regression test reproduces the duplicate signed/unsigned expression pattern and verifies that only the signed region is adjudicated.

## Scientific state

- cFS source pin: unchanged;
- LC source pin: unchanged;
- fixture definition: unchanged;
- invariant truth table: unchanged;
- fixture patch: not applied;
- build: not executed;
- scientific execution: not performed;
- frozen Study 6: unchanged.
