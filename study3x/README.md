# Study 3 Extension Workspace — S3X-ETA-001

**State:** `LOCAL_SOURCE_VERIFICATION_AND_FREEZE_AUTHORIZED__NO_TRACE_EXTRACTION__NO_RECOVERY_EXECUTION`  
**Authorization date:** 2026-09-26  
**Branch base:** `a2b6f2e02c4075d2e9cd1976888dae38464a11c1`

This workspace exists only for the separately identified Paper-2 extension `S3X-ETA-001`.

The frozen Study-3 population `S3-K4E-001` is not modified, rerun, or enlarged by this workspace.

## Authorized in this phase

- verify the exact ESA Anomaly Dataset v2 Mission-1 and Mission-2 archive bytes locally;
- compute local SHA-256 values after the published Zenodo MD5 checks pass;
- inspect the extracted source schema and timestamp cadence with the read-only inspector;
- create a source-identity freeze record if and only if every source-verification gate passes.

## Not authorized

- defining or freezing an empirical gap-extraction threshold before schema evidence is reviewed;
- extracting a scientific S3X trace population;
- replaying Study-3 recovery policies;
- generating S3X scientific results;
- appending S3X rows to the 1,380 frozen Study-3 trajectories;
- manuscript R11/R12 claims based on S3X;
- venue submission.

Large external source archives and extracted datasets must remain local and untracked.

## Current gate

`AWAITING_LOCAL_ESA_V2_ARCHIVE_BYTES_AND_SCHEMA_REPORTS`
