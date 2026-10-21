# S3X-ETA-001 Protocol Draft R1

**Working title:** Empirical Telemetry-Availability Validation of Temporal Recovery-Evidence Qualification  
**Status:** `PROTOCOL_DRAFT__NO_IMPLEMENTATION__NO_EXECUTION_AUTHORIZED`

## Research purpose

Test whether the qualitative Study-3 distinction between bounded truthful-cache exposure and refreshable false-but-valid evidence remains under empirically observed satellite telemetry availability patterns.

## External source candidate

ESA Anomaly Dataset — DOI `10.5281/zenodo.12528696`.

Only timing/availability structure is eligible for use. Anomaly labels must not be interpreted as cyberattacks.

## Prospective design requirements

Before execution:

1. bind exact source version, file identities, license, and local SHA-256 values;
2. define eligible telemetry channels/time series;
3. define timestamp normalization and duplicate handling;
4. define a deterministic observation-gap extraction rule;
5. freeze all derived availability traces before recovery evaluation;
6. preserve frozen Study-3 policy/evidence semantics as read-only dependencies or separately audited extension copies;
7. define extension-specific units/endpoints;
8. perform independent trace-extraction audit.

## Candidate endpoints

- unsafe-qualified exposure under truthful cached evidence;
- unsafe-qualified exposure under one-shot and refreshable false-but-valid evidence;
- episode count;
- fraction of empirical availability traces exhibiting any unsafe qualification;
- matched continuously available control difference under the extension semantics.

## Interpretation controls

- empirical telemetry gap != RF contact loss;
- telemetry anomaly != cyberattack;
- observed gap duration != spacecraft recovery latency;
- S3X observations are not appended to the 1,380 Study-3 trajectories;
- no operational-frequency claim without a source/sampling design that supports it.

## Go/no-go gate

Execution requires a separate author-approved source freeze and final protocol after inspecting the actual ESA dataset structure.
