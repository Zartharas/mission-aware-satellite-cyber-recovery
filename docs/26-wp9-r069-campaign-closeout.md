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

## Retained INVALID attempts (9 total, individually reconciled by `failed_phase`)

**Correction to an earlier draft of this closeout:** an earlier version of this document described the 9 INVALID attempts using an informal two-signature model ("Signature A" / "Signature B") that only enumerated 5 of the 9 positions and omitted position 2 (`10001/A13`, the R-067-motivating case) entirely. That model was not re-derived from the individual per-attempt evidence files this closeout is now based on, and it undercounted. The table below is reconstructed directly from each attempt's `campaign-trial-invalid.json` and `source-harness-invalid.json` on disk (not from the ledger's terminal-summary fields alone, which only record `attempt_status`), and is authoritative over any prior narrative summary, including earlier commits of this file.

`audit_unledgered_campaign_artifacts` (`src/mission_recovery/wp9_r069_campaign_one_position_operator.py`) is a fail-closed gate that blocks any invocation while an unledgered run directory containing runtime/scientific evidence exists under `results/wp9/campaign/seed-*/*/*`. All 9 INVALID attempts below were ledgered through the normal R-069 append path, distinct from the quarantine case described in the next section, which was never ledgered at all.

| Global position | Seed | Cell | `failed_phase` | `runtime_execution_performed` | `campaign_data_generated` | `campaign_seed_consumed` | Source-harness `case_id` / `decision_id` | Run ID |
|---:|---:|---|---|:---:|:---:|:---:|---|---|
| 2 | 10001 | A13 | `MEASUREMENT_BINDING` | true | true | true | `Y01` / R-063 | `20260824T153114Z-wp9-r066-p0002-s10001-a13-4b0614290838440fab52354ca89cb15c` |
| 11 | 10001 | A08 | `MEASUREMENT_BINDING` | true | true | true | `X02` / R-061 | `20260825T132708Z-wp9-r069-p0011-s10001-a08-2be3b82d804e4dfabfa2383dc64b0e3a` |
| 120 | 10005 | A07 | `CFS_READINESS` | false | false | false | `X02` / R-061 | `20260826T015009Z-wp9-r069-p0120-s10005-a07-7148dafb23cd47a2a38a23087455e963` |
| 353 | 10015 | A05 | `FROZEN_ANALYSIS_HORIZON` | true | true | true | `X01` / R-061 | `20260827T040939Z-wp9-r069-p0353-s10015-a05-07072cce25d940e1829b9c4a247f0a17` |
| 404 | 10017 | A19 | `RUNTIME_HEALTH` | true | true | true | `V01` / R-057 | `20260827T172023Z-wp9-r069-p0404-s10017-a19-cc97f2c06d964f4bb91355b3805ff11e` |
| 407 | 10017 | A17 | `NOMINAL_RUNTIME_COMPLETION` | true | true | true | `Y05` / R-063 | `20260827T201857Z-wp9-r069-p0407-s10017-a17-47263c76c3014036957fd81a64727a29` |
| 582 | 10025 | A08 | `NOMINAL_RUNTIME_COMPLETION` | true | true | true | `X02` / R-061 | `20260828T163435Z-wp9-r069-p0582-s10025-a08-b6a6950a58cf45eb855a0ca04d850975` |
| 594 | 10025 | A18 | `CFS_READINESS` | false | false | false | `Y06` / R-063 | `20260828T215110Z-wp9-r069-p0594-s10025-a18-2c446e9bd04444a6a62b6d9b5c1c5702` |
| 627 | 10027 | A16 | `CFS_READINESS` | false | false | false | `Y04` / R-063 | `20260829T011001Z-wp9-r069-p0627-s10027-a16-ee3a470c142447aca85763c6b53a21c2` |

All 9 rows carry `attempt_status=INVALID`, `invalid_attempt_retained=true`, `classification=WP9_R066_FINAL_CAMPAIGN_INVALID_ATTEMPT`, `automatic_retry_performed=false`, `automatic_next_case_performed=false`, and — in the nested `source-harness-invalid.json` — `final_campaign_failure_claimed=false`: the source harness itself explicitly declines to characterize any of these as a final-campaign scientific failure claim. Every one cleared cleanly on the immediate next same-seed/cell retry with a fresh run ID, per the frozen design's retry rule; none of the 9 positions required a second retry. `invalid_attempt_count` held at exactly `9` from position `627` through campaign completion at position `720` — the final approximately 93 positions produced zero new INVALID attempts.

Grouped by `failed_phase` (5 distinct phases, not 2 informal signatures):

- **`CFS_READINESS` (3 occurrences: positions 120, 594, 627).** Pre-execution environment-readiness check failure. `runtime_execution_performed=false`, `campaign_data_generated=false`, no campaign-seed-consumption marker written. No NOS3/Docker runtime was ever started for these attempts.
- **`MEASUREMENT_BINDING` (2 occurrences: positions 2, 11).** Post-runtime instrumentation/measurement-capture failure. `runtime_execution_performed=true`, `campaign_data_generated=true`, `campaign_seed_consumed=true` — the underlying E1/E3 runtime and treatment completed, but the legacy source harness failed while binding/finalizing measurement output. Position 2 (`10001/A13`) is the case that motivated R-067's legacy finalization-summary compatibility fix. Position 11 (`10001/A08`) is a second, independent occurrence of the same `MEASUREMENT_BINDING` phase, on a different event route (E1 rather than E3) and a different repo commit (`97074d0c...`, already post-R-067) — it is not resolved by, and does not contradict, the R-067 fix; it establishes that `MEASUREMENT_BINDING` is a recurring failure phase in the legacy source-harness finalization path, not a single fixed defect.
- **`NOMINAL_RUNTIME_COMPLETION` (2 occurrences: positions 407, 582).** Runtime executed and campaign data was generated (`runtime_execution_performed=true`, `campaign_data_generated=true`, `campaign_seed_consumed=true`), but the source harness did not reach a clean completion state. Position 582 was independently confirmed at the time as a genuine Docker container termination (user-observed); position 407's specific proximate cause was not independently re-confirmed beyond this `failed_phase` label and should not be assumed identical to 582's without checking `source-harness.stderr.log` for that run.
- **`RUNTIME_HEALTH` (1 occurrence: position 404).** Runtime executed, data generated, seed consumed, but the runtime-health check itself failed.
- **`FROZEN_ANALYSIS_HORIZON` (1 occurrence: position 353).** Runtime executed, data generated, seed consumed, but the run violated the frozen analysis time horizon.

Distinct from all 9 ledgered INVALID rows above: three **pre-flight blocks** occurred during the campaign (before position `407`, after position `582`, and before the final push to position `660`), each caused by Docker daemon unavailability or a residual-container check. None of these produced a ledger entry or counted as a campaign attempt at all — they halted before `run-once` derived a frozen position, so they appear nowhere in `attempt-history.json`.


## Quarantined unledgered artifact — Signature C (retained out-of-band, never ledgered)

One additional, previously unobserved failure mode occurred and required deliberate remediation rather than routine retry:

- An operator-issued `Ctrl-C` interrupted a batch-runner invocation after `run-once` had already derived campaign position `660` (seed `10028`, cell `A05`) and begun real NOS3/Docker runtime execution, but before the harness completed its attempt cycle and before the atomic ledger append could run. This left an orphaned, unledgered run directory.
- The next invocation correctly fail-closed: `audit_unledgered_campaign_artifacts` raised `OperatorError: R-069 unledgered campaign artifact contains runtime/scientific evidence` for run ID `20260829T060252Z-wp9-r069-p0660-s10028-a05-d20db11ea75e4b05a49c85faca45d04b`. This is the intended fail-closed behavior (see `tests/test_wp9_r069_campaign_one_position_operator.py::test_unledgered_seed_commit_or_runtime_evidence_is_fail_closed`), not a defect.
- Read-only investigation confirmed: the harness's own internal preflight had failed (`NOMINAL_RUNTIME_PREFLIGHT_STATUS=FAIL`), the command/replay/recovery decision logs were empty, no seed-consumption marker existed, and no `executor-result.json` was ever written — the run never reached a final VALID/INVALID classification and the campaign seed was never consumed for that position.
- Per the frozen-design principle that unexpected results are never discarded, and per an explicit operator decision, the orphaned run directory was **quarantined, not deleted, and not fabricated into a ledger entry**: moved intact from `results/wp9/campaign/seed-10028/A05/<run_id>/` to `results/wp9/campaign/_quarantined-unledgered/seed-10028/A05/<run_id>/`, a path outside the audit's `seed-*/*/*` scan pattern, with a `QUARANTINE_NOTE.txt` documenting the full incident, evidence state, and classification alongside the preserved artifact.
- This action left the ledger completely unchanged (verified identical before and after: `attempt_count=668`, `valid_position_count=659`, `invalid_attempt_count=9`). Position `660` was then re-derived and executed cleanly on the next invocation as a fresh scientific attempt, and the campaign proceeded without incident to completion.
- **Wording precision:** `QUARANTINE_NOTE.txt` (quoted verbatim above, preserved unedited as the contemporaneous historical record) describes the re-derivation as treating position 660 "as if this interrupted attempt never started." That phrasing is scientifically imprecise and is not repeated as this closeout's own characterization: the interrupted attempt did start — real Docker containers were created and NOS3 runtime preparation began, as the evidence list above documents. What is accurate is narrower: the interrupted attempt never became a ledgered scientific attempt (VALID or INVALID) and never formally consumed the campaign seed, because `run-once`'s atomic ledger-append step never ran. The quarantine directory retains the partial evidence precisely so this distinction — real partial execution, but no formal attempt — remains checkable rather than erased.
- This incident does not have its own numbered decision record; it is documented here and in `results/wp9/campaign/_quarantined-unledgered/seed-10028/A05/<run_id>/QUARANTINE_NOTE.txt` as the durable record. A future campaign or replication encountering the same interrupted-mid-preflight condition should apply the same quarantine treatment (evidence retained, ledger untouched, position re-derived fresh) unless a subsequent decision record supersedes it.

## Scientific claim boundary (unchanged, still binding)

- Controlled NOS3 software-in-the-loop simulation only; no real spacecraft access.
- No RF interference/transmission claim.
- No native spacecraft safe-mode claim.
- No real ground-contact timing claim; no real human-operator timing claim. The C1 (missed-contact-window) condition's timing is synthetic/modeled only.
- Immutable ground truth never acted as a runtime policy oracle at any point in the campaign.
- Expected values remained acceptance-only criteria and were never substituted for raw measurement inputs.
- Trial-validity gate failures invalidated the 9 retained INVALID attempts above (`CFS_READINESS`, `MEASUREMENT_BINDING`, `NOMINAL_RUNTIME_COMPLETION`, `RUNTIME_HEALTH`, `FROZEN_ANALYSIS_HORIZON`); none of the 9 is recorded as a failure of the treatment/policy mechanism itself executing incorrectly — each source-harness record explicitly sets `final_campaign_failure_claimed=false`. One phase (`CFS_READINESS`) occurred before any runtime started; the other four (`MEASUREMENT_BINDING`, `NOMINAL_RUNTIME_COMPLETION`, `RUNTIME_HEALTH`, `FROZEN_ANALYSIS_HORIZON`) occurred after runtime execution and treatment completed, but before measurement/finalization validated cleanly. "Treatment-fidelity failure" should not be used as a blanket label for all 9 without this distinction — see the taxonomy above for which attempts did versus did not reach runtime execution.
- Unexpected but treatment-valid scientific outcomes were retained, never discarded.
- One runtime trial was executed per invocation throughout; no automatic retry and no automatic next-case execution occurred at any point.

## Data availability (open item — not yet resolved)

`results/wp9/campaign/attempt-history.json` and the 729 per-attempt trial directories referenced throughout this closeout are **not present in this GitHub repository**. `.gitignore` excludes `results/*` except `results/README.md`; `results/README.md` itself states the intended policy — "commit only: approved aggregate tables, figures, run manifests, checksums, documented exclusions, reproduction instructions" — but no `results/**` allowlist entry beyond the README currently exists in `.gitignore` to let a manifest or checksum file actually be committed. This is a gap between stated policy and enforced policy, not merely an absence of data.

Practical consequence: a person cloning this repository today cannot independently verify any of the counts in this closeout (729 ledger rows, 720 VALID, 9 INVALID, the `failed_phase` breakdown above, 30-per-cell balance, zero duplicate `(seed, cell)` pairs) without access to the raw `results/wp9/campaign/` tree, which lives only on the researcher's local machine at present.

For the record, independently computed on 2026-08-29:
- SHA-256 of `results/wp9/campaign/attempt-history.json`: `92893a2fd8746f410bffd4dca5101bc3f533ada2ff82f98681788cf0c24ce6fd`
- File size: 152,892 bytes; 729 JSON records.
- Final valid trial (position 720, seed 10030, cell A23) independently confirmed to have executed against repo commit `7ed85d5cbeca8f903b3468bc6ccc1c56e29c2446` (`immutable-ground/development-plan.json`, `repo_commit` field), matching the "final campaign execution baseline" recorded in `tracker/RESEARCH_TRACKER.md`.

**Unresolved, requires a researcher decision before this dataset is treated as publication-final:** where the frozen 729-row ledger, the 720-valid analysis dataset, and their checksums will permanently live for reproducibility (options include, but are not limited to, a versioned data-only archive with a DOI such as Zenodo, an institutional data repository, or a `.gitignore`-allowlisted manifest/checksum-only path inside this repository alongside the raw evidence held elsewhere). This closeout does not select one on the researcher's behalf.

## WP10 transition gate

No WP10 statistical analysis has been performed on this closeout. Before the retained 720-valid dataset is treated as final for analysis and manuscript drafting, the following read-only verification steps are recommended and remain outstanding:

1. Re-run the unledgered-artifact audit against the entire `results/wp9/campaign/` tree (not only the known Signature-C case) to confirm no other unledgered artifacts remain.
2. Spot-check a sample of retained trial-result payloads across multiple cells and seeds for internal consistency beyond ledger bookkeeping.
3. Re-review all 9 retained INVALID attempts (the `failed_phase` taxonomy above: `CFS_READINESS` ×3, `MEASUREMENT_BINDING` ×2, `NOMINAL_RUNTIME_COMPLETION` ×2, `RUNTIME_HEALTH` ×1, `FROZEN_ANALYSIS_HORIZON` ×1) for the manuscript's methods/limitations section, distinguishing pre-runtime readiness failures from post-runtime measurement/finalization failures.
4. Decide how the quarantined Signature-C evidence should be referenced, if at all, in the manuscript's methods or limitations section.
5. Consider whether the quarantined interrupted-mid-harness-preflight attempt (position 660) warrants a successor decision record formalizing the general handling policy, since it is a distinct failure mode from all 9 ledgered INVALID attempts above (it was never ledgered at all).

WP10 analysis should proceed only against the frozen, ledger-verified 720-valid dataset and the predeclared metrics/models in `docs/18-wp9a-final-campaign-design.md`.

**A16/A17 coding caution for WP10.** `docs/18-wp9a-final-campaign-design.md` (R-044) lists both A16 and A17 as `requested policy P6 → expected effective policy P6`. The validated runtime semantics are that P6 (`WAIT_FOR_GROUND_AUTHORIZATION`) is the initial decision policy, which *delegates* to P5 for the actual verified-rollback action once synthetic ground authorization becomes available (see `immutable-ground/p6-to-p5-handoff.json` present in relevant run directories, e.g. position 407). WP10 must code A16/A17 as P6-initiated trials with a recorded P5 delegation event, not simply relabel them as "P5 recovery" trials — collapsing that distinction would destroy the frozen `{P6,P7} × {C0,C1}` ground-dependent-vs-autonomous contrast that A16-A18 exist to identify.
