# Paper 2 Phase 7D — Phase-6 Float-Serialization Contract Correction

**Status:** `CORRECTION PREPARED — NOT EFFECTIVE — NO SCIENTIFIC RESULTS`

## Failure boundary

The first authorized Phase-7 real replay stopped during Run 1 before any case generation.

Verified before the failure:

- authorized `main` commit: `1396a82657ff0613b9a1abb0b645e1daa172eb27`;
- frozen interval CSV SHA-256: `cfa4fa3d88cb525237cbfe347fabe8485021351f3b639bdb58f79c575d8a51bc`;
- Phase-7 bound-code identity: PASS.

The runtime then stopped in `parse_interval_row` with:

`ValueError: frozen P99_X10 threshold relationship is inconsistent`

No 34,542-case population was generated, independent validation did not begin, and no scientific result was frozen or used.

## Root cause

Phase 6 computed:

`threshold = p99 * 10.0`

using Python binary floating-point. The interval CSV then serialized `cadence_p99_seconds` and `threshold_seconds` independently with `csv.DictWriter`.

Its independent validator correctly re-parses those canonical strings as floats and checks them against independently recomputed binary-float values.

Phase-7 candidate 001 introduced a stronger condition that Phase 6 never specified:

`Decimal(threshold_string) == Decimal(cadence_string) * 10`

That condition can fail for a correct binary-float pair. Example:

- cadence string: `0.07`
- Phase-6 float threshold string: `0.7000000000000001`
- `float("0.7000000000000001") == float("0.07") * 10.0` → true
- exact decimal `0.7000000000000001 == 0.07 * 10` → false

Therefore the failure is an implementation validation-contract mismatch, not a frozen-data failure and not a P99_X10 rule failure.

## Corrected contract

Candidate 002 preserves the original Phase-6 numerical semantics:

`float(threshold_seconds) == float(cadence_p99_seconds) * 10.0`

and:

`float(delta_seconds) > float(threshold_seconds)`

No tolerance or epsilon is introduced.

The Phase-7 normalized hiatus remains deterministic exact rational arithmetic over the canonical CSV decimal tokens:

`g_i = DecimalToken(delta_seconds) / DecimalToken(cadence_p99_seconds)`

This correction does not alter:

- P99_X10;
- the strict `>` operator;
- the frozen 1,919 interval identities;
- the frozen CSV SHA;
- the 34,542 prospective case grid;
- any Study-3 policy semantics.

## Provenance-preserving v2 stack

The original candidate/auth/runtime files remain unchanged.

Corrected files are versioned separately:

- `S3X_PHASE7_IMPLEMENTATION_FREEZE_CANDIDATE_002.json`
- `S3X_PHASE7_RUNTIME_AUTH_002.json`
- `study3x/src/recovery_replay_v2.py`
- `study3x/audit/reference_replay_v2.py`
- `study3x/runtime/run_phase7_replay_v2.py`
- `study3x/audit/validate_phase7_replay_v2.py`
- `study3x/validation/run_local_phase7_replay_v2.sh`

The old authorization remains historical evidence of the stopped attempt; it is not silently rewritten.

## Current gate

The corrected stack is not effective on this feature branch.

No corrected real replay is authorized until a separate author-reviewed merge and successful post-merge CI.

After that, a separate explicit post-merge author instruction is still required before the corrected real replay can run.

`AUTHOR_REVIEW_AFTER_PHASE7D_CORRECTION_PR_AND_PREMERGE_CI_BEFORE_MERGE`
