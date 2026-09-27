# Paper 2 New-Chat Handoff — 2026-09-27

## Scope

This record is the authoritative handoff for continuing the Paper-2 post-rejection rebuild in a new ChatGPT session.

Paper 2 title:

**Residual Trust Boundaries in Satellite Cyber Recovery: Temporal Evidence, Producer Composition, and Artifact Assurance**

Author: Aman Kumar Singh, sole independent author/corresponding author.

Paper 2 remains limited to frozen Studies 3, 4, and 6 as its original evidence foundation. Study 5 is not part of Paper 2. Studies 1/2/7/7E/8/8E/9 remain separate publication/research streams.

The TAES R10 submission, manuscript ID `TAES-2026-4182`, was rejected at editorial pre-screen before external peer review. The rejected package remains immutable provenance.

## Rebuild theory

Core principle:

> A recovery decision cannot infer a trust property that is absent from the evidence it can observe.

Working central research question:

> Which trust failures remain invisible to a satellite cyber-recovery decision when it relies on fresh evidence, multiple trusted producers, and an approved recovery artifact?

No R11/R12 manuscript rewrite has been authorized yet.

## Frozen original studies

- Study 3 `S3-K4E-001`: 1,380 temporal trajectories and 67,620 epochs.
- Study 4 `S4-MPQ-001`: 4,608 exact observations across 18 vote/provenance-domain rules.
- Study 6 `S6-SCTR-001`: 420 exact observations.

Do not modify, rerun, enlarge, pool, or substitute the frozen Studies 3, 4, or 6.

## S3X extension identity

Extension id: `S3X-ETA-001`.

Public source: ESA Anomaly Dataset v2.

Frozen source record: `S3X-ESA-V2-SOURCE-FREEZE-001`.

Source archive SHA-256:

- Mission 1: `ba28f761b1deab4dbba4728793bff139fea39dbf9cf0d9c559d619ffe75d5a72`
- Mission 2: `e8a89be1917b6754a10bd323441e87a82c8cf2e84ed162442c2dcf72ecc346d5`

Source-freeze SHA-256:

`dd1d71dc074588c12cae24c3718ed758fabd36c41b22755f57ccf98964db9f27`

Schema report SHA-256:

- Mission 1: `696ad9bfa90ff37e2c22bb7eb0c1778af4225a09b02038130698d402b53aaa0a`
- Mission 2: `25533581a3585a8b3056081e1e47f4907d7664103aad5527e374510c0ffba62e`

Channels:

- Mission 1: 76
- Mission 2: 100
- total: 176

Cadence-review SHA-256:

`7355988e25401d6808019f78723eb7356e1646936be41664ce270667cf454b48`

## Phase 5 / 5A sensitivity evidence

Phase 5 evaluated exactly eight diagnostic rules:

- `P99_X1`
- `P99_X2`
- `P99_X3`
- `P99_X5`
- `P99_X10`
- `MAX_P99_MEDIAN_X2`
- `MAX_P99_MEDIAN_X3`
- `MAX_P99_MEDIAN_X5`

The R1 sensitivity CSV had an output-field naming collision: cadence fields and exceedance-distribution fields reused generic names. The threshold calculations were not invalidated. Phase 5A corrected the output schema and reran the identical read-only analysis.

Corrected R2 evidence:

- `S3X_GAP_SENSITIVITY_002.csv`
  - SHA-256 `f690dd230b2897dd74ec880be0de9c207cbb3c975fb4f7740bb18b49df55b88e`
- `S3X_DELTA_FREQUENCIES_002.csv`
  - SHA-256 `1399dde74c0cad144e4be4b5c0af201030eaf9ae70621c8b5b70ff9a52b78349`
- `S3X_GAP_SENSITIVITY_SUMMARY_002.json`
  - SHA-256 `c57fb506c08f03f69f3bed7326355bc97a318f7b6b5015c7745cc3e956865cc6`

R2 dimensions:

- channels: 176
- candidate rules: 8
- sensitivity rows: 1,408

## Phase 5B pre-freeze validation

Local validation record:

`S3X_P99_X10_PREFREEZE_VALIDATION_001.json`

SHA-256:

`cdf9894a6bf1f3dbe9dadb11ec1484b0c540118b05d108d7a38ed33af5930be0`

Validation result:

- candidate: `P99_X10`
- channels: 176
- total exceedances: 1,919
- channels with exceedances: 171
- zero-exceedance channels: 5
- canonical 176-channel projection SHA-256:
  `f15338f1790f60d83d2c849542f6d6e3b21a8c49f7d413cdc5098e35952294d1`

Zero-exceedance channels:

- `ESA-Mission2/channel_66.zip`
- `ESA-Mission2/channel_67.zip`
- `ESA-Mission2/channel_68.zip`
- `ESA-Mission2/channel_69.zip`
- `ESA-Mission2/channel_100.zip`

The Phase-5B local run left the Git worktree clean.

## Phase 5C frozen gap rule

Freeze id:

`S3X-P99X10-GAP-RULE-FREEZE-001`

Machine-readable authority:

`study3x/config/S3X_GAP_RULE_FREEZE_001.json`

Frozen rule:

`P99_X10`

Exact formula:

`threshold_seconds = 10 * channel-specific cadence_p99_seconds`

Exact comparison:

`positive inter-sample delta > threshold_seconds`

The comparison is strict greater-than. Equality is not an exceedance.

Selection characterization:

`DATA_INFORMED_SELECTION_FROM_PRESPECIFIED_PHASE5_CANDIDATE_FAMILY`

Do not describe P99_X10 as having been prespecified as the final rule before cadence inspection. It was selected after the read-only eight-rule sensitivity analysis and separate pre-freeze validation.

No cadence-class-specific multiplier was introduced.

## Phase 5C merge/CI provenance

PR `#180`:

- pre-merge head: `a85b1cefa50d55adc1c61ee581cf6a3ad2279ddd`
- pre-merge CI: run id `36298410362`, run number `1226`, success
- merge commit: `ac5b2e1cedafbcc2c15da41f5c0b254256850afc`
- post-merge CI: run id `36299292647`, run number `1227`, success
- `main` immediately after Phase-5C merge: `ac5b2e1cedafbcc2c15da41f5c0b254256850afc`

Phase 5C is technically complete and the frozen rule is active repository state.

## Interpretation firewall

A `P99_X10` exceedance is only an extreme telemetry inter-sample interval diagnostic.

Do not claim that a detected interval is, by itself:

- RF contact loss;
- ground-station visibility loss;
- spacecraft outage;
- cyberattack truth;
- onboard recovery latency;
- operational command availability.

## Current gates

Current authorized state:

- source identity frozen: YES
- gap rule selected: YES
- gap rule frozen: YES
- timestamp-level trace extraction: NO
- trace population frozen: NO
- recovery-policy execution: NO
- S3X scientific execution: NO
- S4X execution: NO
- S6X build/scientific campaign: NO
- manuscript R11/R12 rewrite: NO
- new venue lock: NO
- publisher submission: NO

The frozen P99_X10 rule may not be retuned after timestamp-level locations are inspected. Any future rule change requires a separately authorized versioned protocol.

## Next phase

Next gate:

`AUTHOR_REVIEW_BEFORE_PHASE6_TIMESTAMP_LEVEL_TRACE_EXTRACTION_DESIGN`

The next chat should begin with **Phase 6 design only** unless the author explicitly authorizes execution.

Recommended Phase 6 objective:

Design a deterministic timestamp-level extraction protocol that:

1. reads the already frozen ESA-v2 source bytes;
2. uses only the frozen `P99_X10` rule;
3. recomputes each channel P99 using the frozen method;
4. emits timestamp-level intervals only where `delta > 10 * P99`;
5. preserves mission/channel/source-hash provenance;
6. includes deterministic ordering and stable identifiers;
7. validates aggregate extraction counts against the already bound 1,919 exceedances;
8. does not reinterpret gaps as RF outages, attacks, recovery latency, or command availability;
9. does not execute Study-3 recovery policies;
10. does not freeze the extracted trace population until a separate author review;
11. does not create scientific results or manuscript claims.

Before any Phase-6 execution, create a versioned protocol/design record, fail-closed tests/audit, and a separate PR. Run CI, obtain author authorization, merge, and verify post-merge CI before local extraction.

## S6X state

S6X pre-runtime validation has already passed against pinned NASA cFS/LC source identities. No cFS/LC build, fixture application, signing, independent rebuild, provenance observation generation, or scientific campaign has been authorized.

Keep S6X on hold while Phase 6 S3X design is being considered unless the author explicitly changes priorities.

## Other non-negotiable separation controls

- no Study 5 import into Paper 2;
- no Study 7/7E, 8/8E, or 9 import;
- no pooling across frozen studies/extensions;
- do not merge historical branch `paper2/taes-10-page-compression`;
- historical archive SHA-256 for that branch remains `ef1c6f5a224a0a0816a5f02285055fb43eb0e5cebcb4be4c0156ab35524741c4`.

## New-chat operating instructions

At the start of the next chat:

1. inspect current GitHub `main` and the Phase-5C freeze/status records;
2. verify the latest release-gate CI is green;
3. treat this handoff as provenance, but prefer live repository state if later commits exist;
4. do not rerun or change frozen Studies 3/4/6;
5. do not change P99_X10 unless a separately authorized versioned change protocol is created;
6. proceed incrementally with explicit author authorization at each execution/freeze gate;
7. keep all generated large ESA artifacts local/ignored unless a specific repository-safe aggregate record is intentionally committed.
