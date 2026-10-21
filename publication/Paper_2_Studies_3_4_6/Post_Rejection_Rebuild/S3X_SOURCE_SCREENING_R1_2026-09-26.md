# S3X-ETA-001 Source Screening R1

**Status:** `SOURCE_SCREENING_COMPLETE__SOURCE_FREEZE_NOT_AUTHORIZED`  
**Screening date:** 2026-09-26  
**Scientific execution:** none

## Candidate source

ESA Anomaly Dataset.

Official ESA repository:
- https://github.com/esa/anomaly-dataset

Zenodo version records:
- v1 / DOI `10.5281/zenodo.12528696`, published 2024-06-25;
- v2 / DOI `10.5281/zenodo.15237121`, published 2025-04-17.

The repository's historical data register references v1. A newer v2 exists and has different archive checksums. Therefore S3X must not silently inherit the old v1 identity.

## Source structure established by official records

The ESA source describes real-life satellite telemetry from three ESA missions.

The v2 Zenodo record contains three mission archives totaling about 11.6 GB:
- `ESA-Mission1.zip` — about 3.8 GB;
- `ESA-Mission2.zip` — about 4.1 GB;
- `ESA-Mission3.zip` — about 3.7 GB.

The Mission-1 archive preview shows:
- `channels.csv`;
- `labels.csv`;
- `anomaly_types.csv`;
- a `channels/` directory with per-channel archives;
- a `telecommands/` directory with per-telecommand archives.

The official ESA-ADB code repository states that Missions 1 and 2 are the two missions selected for its published benchmark and provides dedicated preprocessing paths for each.

## Fit to S3X

**Potential fit:** high, but not yet proven.

The source is appropriate for checking empirical telemetry observation structure because it is real spacecraft telemetry and preserves per-mission/per-channel organization.

The source does **not** establish that every missing timestamp or discontinuity represents:
- RF contact loss;
- ground-station visibility loss;
- spacecraft unavailability;
- cyberattack;
- recovery latency.

Therefore S3X may use only empirically observed telemetry-availability structure unless source documentation provides a stronger causal interpretation.

## Version decision

Recommended candidate for a future source freeze: **v2**, because it is the newer ESA-published version.

However, before freezing v2:
1. verify the license directly for v2;
2. record exact archive/file hashes;
3. inspect actual per-channel file schema and timestamp representation;
4. determine whether missingness/gaps can be distinguished from expected sampling cadence and preprocessing;
5. define a deterministic gap-extraction rule before any recovery evaluation.

If these checks fail, S3X should stop rather than force the dataset into a contact model.

## Non-overlap control

Do not use Study-8E SatNOGS or OPS-SAT re-entry trace rows for S3X. This keeps Paper 2 independent from Paper 4.

OPSSAT-AD remains a possible literature/context source but is not the preferred S3X experimental source.

## Current decision

`CONDITIONAL_GO_FOR_LOCAL_METADATA_AND_SCHEMA_INSPECTION_AFTER_AUTHOR_APPROVAL`

No dataset download, source freeze, trace extraction, or scientific execution is authorized by this record.
