# WP9 R-069 Frozen Campaign Closeout

**Closeout date:** 2026-08-29
**Status:** Complete — 720/720 valid frozen positions retained
**Role:** Scientific provenance record for the completion of the WP9 frozen final campaign, transitioning to WP10 statistical analysis.

## Frozen implementation identity

- Canonical runtime/operator stack: R-064 through R-070 (see `tracker/RESEARCH_TRACKER.md` for the full per-decision history).
- Execution mechanism: `scripts/run_wp9_r069_campaign_one_position.sh run-once`, one frozen position per invocation, no automatic retry, no automatic next-position execution, per R-069.
- Ledger of record: `results/wp9/campaign/attempt-history.json` (atomic, append-only, authoritative over any prose/tracker/log narrative).

## Campaign completion result

Independently reconstructed from `results/wp9/campaign/attempt-history.json` on disk (not taken from runner terminal output alone):

- Total ledger records: `729`
- Valid frozen positions: `720` — target met (24 cells × 30 campaign seeds).
- Retained scientific INVALID attempts: `9`.
- `campaign_complete`: `true`, set atomically on the final ledger append (global order index `720`, campaign seed `10030`, cell `A23`).
- Distinct campaign seeds with valid entries: `30`, contiguous `10001`–`10030`, no gaps.
- Every one of the 24 frozen cells (A01–A24) has exactly `30` valid repetitions; none deviate.
- Unique (seed, cell) valid pairs: `720`, matching the required count exactly — zero duplicates, zero gaps.
- First ledger row: campaign seed `10001`, cell `A19`, run ID `20260824T145723Z-wp9-r066-p0001-s10001-a19-69fe370fe1d249e68ebf05671a630b9d`, `VALID`.
- Last ledger row: campaign seed `10030`, cell `A23`, run ID `20260829T110835Z-wp9-r069-p0720-s10030-a23-c1a79acf4d4c4d20acc961bc533e0f4b`, `VALID`.

This is a complete, gap-free, duplicate-free dataset matching the R-044/WP9-A frozen design and the WP9-C repetition-count selection of 30 valid repetitions per cell exactly.

### Terminal states observed across the campaign

`TRUSTED_RECOVERY_CONFIRMED`, `RECOVERY_FAILED`, `OPERATIONAL_BUT_UNVERIFIED`, `CONTAINED_NOT_RECOVERED`. No terminal-state category outside this predeclared set occurred at any point in the campaign.

### Evidence-completeness sanity check

`evidence_completeness_ratio` is a family-dependent scientific outcome metric, not a run-integrity signal. It held with zero false positives across the entire campaign:

- E1/E2/E3 trials: exactly `1.0`.
- E4 trials: exactly `0.6666666666666666` (2/3), by construction (`src/mission_recovery/wp8_observability_evidence.py`).

## Retained INVALID attempts (9 total) — two distinct ledgered failure signatures

`audit_unledgered_campaign_artifacts` (`src/mission_recovery/wp9_r069_campaign_one_position_operator.py`) is a fail-closed gate that blocks any invocation while an unledgered run directory containing runtime/scientific evidence exists under `results/wp9/campaign/seed-*/*/*`. All INVALID attempts below were ledgered through the normal R-069 append path, distinct from the quarantine case described in the next section.

- **Signature A — mid-run Docker termination.** Real runtime execution performed, real campaign data generated, `attempt_status=INVALID`. Occurred at campaign positions `404`, `407`, and `582` (position 582 confirmed as a genuine Docker container termination).
- **Signature B — pre-execution failure.** No runtime execution performed, no campaign data generated, no residual containers, `attempt_status=INVALID`. Occurred at campaign positions `594` and `627`. Both cleared cleanly on the first same-seed/cell retry with a fresh run ID, as required by the frozen design.
- `invalid_attempt_count` held at exactly `9` from position `627` through campaign completion at position `720` — the final approximately 93 positions produced zero new INVALID attempts.
- Distinct from both signatures above: three **pre-flight blocks** occurred (before position `407`, after position `582`, and before the final push to position `660`), each caused by Docker daemon unavailability or a residual-container check. None of these produced a ledger entry or counted as a campaign attempt — they halted before the frozen position was derived.

## Quarantined unledgered artifact — Signature C (retained out-of-band, never ledgered)

One additional, previously unobserved failure mode occurred and required deliberate remediation rather than routine retry:

- An operator-issued `Ctrl-C` interrupted a batch-runner invocation after `run-once` had already derived campaign position `660` (seed `10028`, cell `A05`) and begun real NOS3/Docker runtime execution, but before the harness completed its attempt cycle and before the atomic ledger append could run. This left an orphaned, unledgered run directory.
- The next invocation correctly fail-closed: `audit_unledgered_campaign_artifacts` raised `OperatorError: R-069 unledgered campaign artifact contains runtime/scientific evidence` for run ID `20260829T060252Z-wp9-r069-p0660-s10028-a05-d20db11ea75e4b05a49c85faca45d04b`. This is the intended fail-closed behavior (see `tests/test_wp9_r069_campaign_one_position_operator.py::test_unledgered_seed_commit_or_runtime_evidence_is_fail_closed`), not a defect.
- Read-only investigation confirmed: the harness's own internal preflight had failed (`NOMINAL_RUNTIME_PREFLIGHT_STATUS=FAIL`), the command/replay/recovery decision logs were empty, no seed-consumption marker existed, and no `executor-result.json` was ever written — the run never reached a final VALID/INVALID classification and the campaign seed was never consumed for that position.
- Per the frozen-design principle that unexpected results are never discarded, and per an explicit operator decision, the orphaned run directory was **quarantined, not deleted, and not fabricated into a ledger entry**: moved intact from `results/wp9/campaign/seed-10028/A05/<run_id>/` to `results/wp9/campaign/_quarantined-unledgered/seed-10028/A05/<run_id>/`, a path outside the audit's `seed-*/*/*` scan pattern, with a `QUARANTINE_NOTE.txt` documenting the full incident, evidence state, and classification alongside the preserved artifact.
- This action left the ledger completely unchanged (verified identical before and after: `attempt_count=668`, `valid_position_count=659`, `invalid_attempt_count=9`). Position `660` was then re-derived and executed cleanly on the next invocation as a brand-new, never-before-attempted position, and the campaign proceeded without incident to completion.
- This incident does not have its own numbered decision record; it is documented here and in `results/wp9/campaign/_quarantined-unledgered/seed-10028/A05/<run_id>/QUARANTINE_NOTE.txt` as the durable record. A future campaign or replication encountering the same interrupted-mid-preflight condition should apply the same quarantine treatment (evidence retained, ledger untouched, position re-derived fresh) unless a subsequent decision record supersedes it.

## Scientific claim boundary (unchanged, still binding)

- Controlled NOS3 software-in-the-loop simulation only; no real spacecraft access.
- No RF interference/transmission claim.
- No native spacecraft safe-mode claim.
- No real ground-contact timing claim; no real human-operator timing claim. The C1 (missed-contact-window) condition's timing is synthetic/modeled only.
- Immutable ground truth never acted as a runtime policy oracle at any point in the campaign.
- Expected values remained acceptance-only criteria and were never substituted for raw measurement inputs.
- Treatment-fidelity failures invalidated trials (Signatures A and B above); unexpected but treatment-valid scientific outcomes were retained, never discarded.
- One runtime trial was executed per invocation throughout; no automatic retry and no automatic next-case execution occurred at any point.

## WP10 transition gate

No WP10 statistical analysis has been performed on this closeout. Before the retained 720-valid dataset is treated as final for analysis and manuscript drafting, the following read-only verification steps are recommended and remain outstanding:

1. Re-run the unledgered-artifact audit against the entire `results/wp9/campaign/` tree (not only the known Signature-C case) to confirm no other unledgered artifacts remain.
2. Spot-check a sample of retained trial-result payloads across multiple cells and seeds for internal consistency beyond ledger bookkeeping.
3. Re-review all 9 retained INVALID attempts (Signatures A and B) for the manuscript's methods/limitations section.
4. Decide how the quarantined Signature-C evidence should be referenced, if at all, in the manuscript's methods or limitations section.
5. Consider whether Signature C warrants a successor decision record formalizing the general handling policy for an interrupted mid-harness-preflight attempt, since it is now a documented recurring failure category alongside Signatures A and B.

WP10 analysis should proceed only against the frozen, ledger-verified 720-valid dataset and the predeclared metrics/models in `docs/18-wp9a-final-campaign-design.md`.
