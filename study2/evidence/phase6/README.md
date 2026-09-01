# Study 2 Phase 6 evidence freeze

This directory records the immutable identity and execution bindings of the completed Study-2 Phase-6 campaign. It does not contain or report statistical interpretation of the Study-2 outcomes.

## Authoritative execution

- Experiment: `S2-AEATR-001`
- Authorization: `S2-AEATR-001-PHASE6-AUTH-001`
- Authorized main commit: `24ed05f4d52611754ac91ad1a74c5bcf242245ac`
- Campaign workflow run: `33547420437`
- Campaign job: `99988273536`
- Run attempt: `1`
- Result: `3872 VALID / 0 INVALID`
- Frozen trial-manifest SHA-256: `190612473717b7768ceccb4596a20d90cd7d532bf7581330ce94d609cb752e67`

## Authoritative raw artifact

The raw campaign package was uploaded by the frozen workflow as GitHub Actions artifact ID `9816191406`, named:

`study2-phase6-evidence-24ed05f4d52611754ac91ad1a74c5bcf242245ac`

Artifact ZIP SHA-256:

`195860bd44b38ccf170f02cb1cb392583217296d08640c99b18b52286403e133`

The Actions copy is configured for 90-day retention and is scheduled to expire at `2026-11-30T19:05:03Z`. A separately downloaded copy was independently hash-verified during closeout. Preserve that exact ZIP in the long-term research archive before the Actions retention date. Do not regenerate campaign data to replace an expired or lost artifact.

## File identities

- `observations.jsonl`: `8dcc850c561d7e3c0bf7478263b534cae83cbbb55183c313e879dd7d61127854`
- `attempt_ledger.jsonl`: `755d6541263ac31589934200ea5071cdbcacae1ea197d044bbd3e6f7f7d1dbc5`
- `runtime_bindings.json`: `4d8d1a4db3c9594946eab06a72c2bb71f1dbb13860bdbd01598ca4694ce4f31a`
- `campaign_summary.json`: `247bdf2e57a1d0c4b7aaf9e9811d1abf331bcd1cd655dddf3e5c2b5b2da82f99`
- `evidence_hashes.json`: `a1a53153356db3434e7ac427225f2a9b620bbec74c3436e2c87a8cbf0b0ffa50`

The repository retains the exact campaign summary, evidence-hash manifest, runtime bindings, and Phase-6 provenance. The raw observations and attempt ledger remain in the hash-identified authoritative ZIP rather than being copied into repository history.

## Independent closeout checks

The downloaded artifact was independently checked after the workflow completed:

- ZIP digest matched GitHub artifact metadata.
- All five file digests matched the workflow output and `evidence_hashes.json`.
- Observation rows: 3,872.
- Attempt-ledger rows: 3,872.
- VALID observations: 3,872.
- INVALID attempts: 0.
- Run IDs and trial IDs were unique and exactly ordered.
- Observation and ledger `(trial_id, cell_id, seed)` identities matched row-for-row.
- Every cell used its exact prospectively frozen campaign seed membership.
- Block replication counts matched the frozen design: A=18x96, B=20x32, C=18x32, D=20x32, E=9x32.
- `oracle_was_selector_input` was false for all observations.
- Automatic retry and automatic next-trial behavior remained disabled at the single-trial runtime boundary.

## Closeout boundary

The campaign authorization is consumed during Phase-6 closeout. A consumed authorization must not execute the campaign again. Any future analysis must operate on the frozen evidence identified above and must not regenerate or substitute Study-2 campaign observations.
