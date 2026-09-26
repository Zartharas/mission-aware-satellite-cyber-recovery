# S3X-ETA-001 Metadata and Schema Inspection R2

**Status:** `METADATA_SCHEMA_INSPECTION_COMPLETE__SOURCE_FREEZE_CANDIDATE_PREPARED__NO_RECOVERY_EXECUTION`  
**Authorization:** explicit author authorization on 2026-09-26  
**Scientific execution:** none

## Authoritative source identity

Candidate dataset: **ESA Anomaly Dataset v2**.

- Zenodo DOI: `10.5281/zenodo.15237121`
- publication date: 2025-04-17
- publisher: European Space Agency
- official source repository: `https://github.com/esa/anomaly-dataset`
- official repository license: **CC BY 3.0 IGO**

Zenodo v2 exposes three outer archives:

| Archive | Approx. size | Zenodo MD5 |
|---|---:|---|
| `ESA-Mission1.zip` | 3.8 GB | `9770ad12ed730238f37c42d5c27ab436` |
| `ESA-Mission2.zip` | 4.1 GB | `bfc72012691427d9327eb41f726ce45e` |
| `ESA-Mission3.zip` | 3.7 GB | `d63943f09c81378acd9fc5e565ecc66e` |

The v2 bytes differ from the older v1 record already referenced elsewhere in the repository. S3X therefore must use a new, explicit source identity and must never inherit v1 checksums.

## Mission-1 archive structure established from the Zenodo v2 preview

The Mission-1 archive contains:

- `anomaly_types.csv`
- `channels.csv`
- `labels.csv`
- `channels/` with **76** per-channel ZIP files
- `telecommands/` with per-telecommand ZIP files

The archive preview establishes structure and member sizes. It does not expose the complete content of every channel archive through the repository workflow used for this inspection.

## Consumer schema established from the official ESA-ADB preprocessing code

The official `kplabs-pl/ESA-ADB` preprocessing code reads the source as follows.

### Common annotation metadata

`labels.csv` is parsed with at least:

- `ID`
- `Channel`
- `StartTime`
- `EndTime`

`anomaly_types.csv` is joined by `ID` and supplies at least:

- `ID`
- `Category`

The preprocessing distinguishes `Anomaly`, `Rare Event`, and, for Mission 1, other annotated intervals treated as a gap label. S3X will **not** interpret any of these classes as cyberattack truth.

### Telecommand metadata

`telecommands.csv` is expected to contain at least:

- `Telecommand`
- `Priority`

The official preprocessing uses only telecommands with priority at least 3 for its benchmark construction. S3X does not currently need telecommand semantics.

### Channel archives

The official code enumerates `channels/*.zip` and loads each directly with `pandas.read_pickle`.

For channel `channel_N`:

- the table has a datetime-like index;
- the value column is named `channel_N`;
- the code renames that value column to `value`;
- Mission 1 benchmark preprocessing uses a 30-second resampling rule;
- Mission 2 benchmark preprocessing uses an 18-second resampling rule.

These benchmark resampling intervals are evidence about the official preprocessing pipeline. They are **not** assumed to be the native sampling cadence of every raw channel.

## Candidate S3X scope

Source-freeze candidate scope:

- **include Mission 1 and Mission 2**
- **exclude Mission 3 from S3X R1**

Rationale: Missions 1 and 2 are the missions for which the official ESA-ADB repository provides explicit benchmark preprocessing paths. Using both permits cross-mission sensitivity to different telemetry sampling structures without inventing a Mission-3 preprocessing contract.

This is a scientific-scope choice, not observation-count inflation.

## What is still required before a source freeze

The 7.9-GB Mission-1/Mission-2 archive bytes are not stored in this repository and were not downloaded into this GitHub-connected workspace.

Before a final S3X source freeze:

1. download the exact v2 Mission-1 and Mission-2 archives from Zenodo;
2. verify the Zenodo MD5 values above;
3. compute and record local SHA-256 for both outer archives;
4. extract read-only copies;
5. run `scripts/inspect_s3x_esa_schema.py`;
6. record CSV headers and row counts;
7. inspect every selected channel's index type, monotonicity, duplicates, first/last timestamp, sample count, and positive inter-sample delta distribution;
8. identify whether any apparent gaps are distinguishable from expected/native channel cadence;
9. freeze a deterministic gap rule **before** any recovery-policy replay.

## Gap-extraction rule remains intentionally unfrozen

No multiplier such as `delta > 2x median`, `3x median`, or a fixed-seconds threshold is accepted yet.

The local schema report must first establish whether per-channel cadence is sufficiently stable to support a defensible gap rule.

If it is not, S3X must stop or use a different externally documented availability construct.

## Interpretation firewall

S3X may describe derived intervals only as **empirical telemetry-availability gaps** unless the source documentation proves a stronger interpretation.

S3X must not equate such intervals with:

- RF contact windows;
- ground-station visibility;
- spacecraft outage;
- cyberattack;
- onboard recovery latency;
- operational command availability.

## Current gate

`SOURCE_FREEZE_CANDIDATE_PREPARED__LOCAL_ARCHIVE_HASH_AND_SCHEMA_REPORT_REQUIRED__NO_SCIENTIFIC_EXECUTION`
