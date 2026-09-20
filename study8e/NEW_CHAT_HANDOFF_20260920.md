# Study 8E New-Chat Handoff - 2026-09-20

Use this file to resume Study 8E / Paper 4 work in a fresh ChatGPT session.

## Repository

- repository: `Zartharas/mission-aware-satellite-cyber-recovery`
- repository path used locally by the author: `/Users/zarthras/Documents/Development Projects/Satellite-Cybersecurity-Research/mission-aware-satellite-cyber-recovery`
- Study 8E experiment: `S8E-ECTV-001`
- parent frozen Study 8: `S8-PQC-ICR-001`
- current authoritative Study 8E state: `study8e/CURRENT_EXTENSION_STATE.md`
- corrected-result audit handoff: `study8e/CANONICAL_RESULTS_002_AUDIT_HANDOFF.json`

Always read the repository current state before relying on chat memory.

## Scientific governance

- User is the sole independent author.
- Do not add coauthors.
- Repository records override chat memory.
- Frozen Study 8 and the rejected Acta package are immutable.
- Do not silently repair source data.
- Do not silently change protocol rules after endpoint inspection.
- Preserve negative/null findings.
- No publisher submission without explicit final author authorization.
- Every new scientific execution requires explicit authorization.
- Same-repository independent implementation is reproducibility, not external empirical replication.

## Original Study 8

Original Study 8 is a complete deterministic population of 3,456 positions:

- 3 crypto profiles
- 4 policies
- 4 contact regimes
- 4 disruptions
- 6 compromise offsets
- 3 logical deadlines

Frozen primary Study 8 result remains:

`P3 - P1 = 0/1 = 0.000000 percentage points`

The Acta Astronautica editorial rejection does not invalidate Study 8 science and identified no specific methodological defect.

## Study 8E purpose

Study 8E is a separate post-rejection evidence extension. It tests how frozen Study 8 transition semantics behave under a prospectively frozen public SatNOGS observation-opportunity timing population.

SatNOGS semantics must remain narrow:

- `start/end` are observation-opportunity timing proxies;
- observation does not prove operational/authenticated/bidirectional command contact;
- transmitter baud is not modeled or measured usable recovery throughput;
- `hypothetical_uniform_effective_payload_rate_bps` is solved as a model threshold;
- original Study 8 logical slots are never converted to seconds.

## Corrected source/population history

### POP-001 invalidation

`S8E-SATNOGS-POP-001` is invalid.

Root cause:

- generated API documentation exposed stale `satellite__norad_cat_id`;
- live SatNOGS Network 1.134 uses `norad_cat_id`;
- old qualification calls therefore filtered station but did not correctly prove satellite-station pair activity.

No timing/recovery endpoint had been computed when POP-001 was invalidated.

### POP-002

`S8E-SATNOGS-POP-002` is the corrected frozen population:

- ten frozen June seed windows;
- 149 candidate pairs;
- corrected `norad_cat_id + ground_station` filter;
- >=20 observation threshold;
- SHA-256 rank;
- max two selected per NORAD ID;
- max two selected per station;
- hard request cap 50;
- 40 candidate pairs evaluated;
- 20 below threshold;
- 5 skipped by entity caps;
- 20 selected;
- target 32 not reached;
- stopping rule prohibits tuning to force 32.

### TRACE-002

`S8E-SATNOGS-TRACE-002`:

- 20 selected pairs;
- 476 frozen first-page observations;
- JSONL SHA-256 `6f80a44fa6cfa63a70df49de3ba447de3d59efe0632208180f26552f37b46a8e`;
- source artifact workflow run `35493369936`;
- source artifact ID `10600470520`;
- source artifact ZIP SHA-256 `5e06da499540842bc826188977cd66216bf4348e115a16db00c2dd9d8ee0855f`.

Do not follow additional cursor pages without a new prospective protocol/authorization.

## Implementation and canonical protocol

- extension implementation freeze: `S8E-IMPLFREEZE-001`
- canonical protocol: `S8E-CANON-EXEC-001`
- corrected canonical runner: `S8E-CANON-RUNNER-004`

Canonical factor grid per eligible anchor:

- horizons: 6 h, 12 h, 24 h
- profiles: 3
- policies: P0, P1, P2, P3
- disruptions: A0, A1, A2, A3
- cases per eligible anchor: 144

Success requires `TRUST_RESTORED` strictly before the horizon.

Correct sufficient upper bound:

`U_strict = floor(8 * B / d_min) + 1`

where:

- `B = sum(profile transition-object bytes) + largest transition-object bytes`;
- `d_min` is the shortest positive future-window duration.

The separate independent bound auditor must agree exactly.

## Canonical execution history

### Pre-execution failed run

Run `35525450194` failed at runner compilation before scientific execution.

No scientific endpoint was computed.

### Results 001 - invalidated

Run `35529423881` technically succeeded and was deterministic, but the old bound used `ceil(8B/d_min)`.

Post-run adversarial audit found 24 exact-divisibility boundary cases incorrectly classified as non-finite.

Record:

`study8e/CANONICAL_RESULTS_001_INVALIDATION.json`

Never use results 001 scientifically.

### Results 002 - corrected and audited

Corrected execution authorization:

`S8E-CANON-GOLIVE-002`

Corrected activation:

`S8E-CANON-ACTIVATE-002`

Corrected workflow run:

`35536583594`

Execution head:

`d49d4ba43c451564f697188ca88deb463895792d`

Artifact:

- ID `10613372166`
- name `study8e-canonical-results-002`
- ZIP SHA-256 `3e9c6c7899a9853682d29fa92ea37589c4684db49b16a0a289be054a3553bfee`

Validation:

- 10/10 runner tests PASS
- execution pass 1 PASS
- execution pass 2 PASS
- byte-identical scientific outputs
- independent case mismatches = 0
- repository drift = none

Corrected findings:

- 20 traces
- 476 source rows
- 454 eligible anchors
- 65,376 canonical cases
- 17,640 finite thresholds
- 47,736 non-finite thresholds
- finite fraction = 245/908 = 0.269824
- finite threshold min = 48 modeled bps
- median = 345 modeled bps
- max = 57,727 modeled bps

By horizon:

- 6 h: 1,152/21,792 finite = 0.052863
- 12 h: 4,488/21,792 finite = 0.205947
- 24 h: 12,000/21,792 finite = 0.550661

By disruption:

- A0: 6,624/16,344 finite = 0.405286
- A1: 6,624/16,344 finite = 0.405286
- A2: 2,196/16,344 finite = 0.134361
- A3: 2,196/16,344 finite = 0.134361

Policies:

- each policy finite = 4,410/16,344
- feasibility classification is identical across P0-P3

P3 vs P1:

- matched comparisons = 16,344
- both finite = 4,410
- both non-finite = 11,934
- all 4,410 both-finite minimum-rate differences = exactly 0 bps
- P3 lower threshold = 0
- P3 higher threshold = 0

Profiles:

- each profile finite = 5,880/21,792
- matched burden-ordering checks = 21,792
- ordering preserved = 21,792
- ordering violations = 0

Structural modeled safety fields:

- rollback invoked sums = 0
- stale epoch acceptance sums = 0

## Corrected result hashes

- `ANCHOR_MANIFEST.csv`: `e45561d4dc30cace106a0f1e3be2f3801967ecc798d4b7db2c9a52d1ed8c93a9`
- `CANONICAL_CASE_RESULTS.csv`: `be0ea2b4da2228bf270ab8ef51bb8625a633346ac6e0b3ebd5fa2134496583fd`
- `CANONICAL_FINDINGS.json`: `9e2ac149d827ff6189983c1b576778d6f31b22dd7218232661a88ecef42e0773`
- `INDEPENDENT_AUDIT.json`: `8a66ff3c9c5f3070a6f1effcb0e21a21243ea6bbd747a1b4baf09406c37181fd`
- `P3_P1_CONTRASTS.csv`: `3053b42cf30591bb56c23dc5f0b83244dec34ea933943900a4b2a3f25e93d559`
- `PROFILE_ORDERING_CHECKS.csv`: `eab36d1511c182e299288e6d23a1cde0fae285ed97d3c382dbdb2a2e868e50f0`
- `TRACE_TIMING_GAPS.csv`: `9cad90c5d5984c87d82bca0495e77c7343a7a3ce5742ddbe93ee57541080bfc2`
- `TRACE_TIMING_SUMMARY.csv`: `c8f88d5255b56543b915e65e24b2fa24c1f7d513e8cd1e6cb76845d1880b8a2b`
- `TRACE_TIMING_WINDOWS.csv`: `59c6a3beaa9831a58174dcd0776ef8c404fcd37783b307044d2f9ee9dcad0c0d`

## Metadata inconsistency in results 002

Do not miss this.

Inside the immutable corrected artifact:

- `CANONICAL_FINDINGS.json` says `results_id = S8E-CANON-RESULTS-002`.
- `RESULTS_HASH_MANIFEST.json` still says `results_id = S8E-CANON-RESULTS-001`.

This is a packaging metadata defect only. It does not change the scientific rows/hashes.

Do not rewrite the historical Actions artifact.

Repository authority:

`study8e/CANONICAL_RESULTS_002_AUDIT_HANDOFF.json`

The next chat must decide whether formal result freeze can accept the documented metadata discrepancy or whether a separately authorized metadata-corrected reexecution is warranted. Do not rerun by default.

## Current explicit gate

**Formal result freeze is still pending.**

Do not:

- merge/copy canonical result files into the repository as frozen science without explicit approval;
- integrate results into the manuscript yet;
- change the Study 8 / Study 8E paper architecture yet;
- submit to a publisher;
- rerun TRACE-002 merely to clean metadata.

Next recommended action:

1. review current repository state and `CANONICAL_RESULTS_002_AUDIT_HANDOFF.json`;
2. make a formal result-freeze decision;
3. if frozen, decide manuscript architecture:
   - revised Study 8 paper with Study 8E external-timing validation section, or
   - separate companion paper;
4. only then perform manuscript integration and live venue assessment.

## Repository authority order for the next chat

For Study 8E questions, prefer:

1. `study8e/CURRENT_EXTENSION_STATE.md`
2. `study8e/CANONICAL_RESULTS_002_AUDIT_HANDOFF.json`
3. `study8e/CANONICAL_EXECUTION_GO_LIVE_002_CLOSEOUT.json`
4. `study8e/CANONICAL_RUNNER_FREEZE_004.json`
5. `study8e/CANONICAL_BOUND_DEFECT_001.json`
6. `study8e/CANONICAL_RESULTS_001_INVALIDATION.json`
7. `study8e/CANONICAL_EXECUTION_PROTOCOL_001.json`
8. `study8e/SATNOGS_TRACE_ARTIFACT_FREEZE_002.json`
9. `study8e/SATNOGS_POPULATION_FREEZE_002.json`
10. `study8e/IMPLEMENTATION_FREEZE_001.json`

Historical POP-001, results 001, earlier runner freezes, rejected Acta files, and superseded PRs remain provenance only.
