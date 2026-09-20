# Study 8E: External Contact-Trace Validation

**Experiment:** `S8E-ECTV-001`  
**Status:** `PROTOCOL_FREEZE_CANDIDATE__NO_EXTERNAL_DATA_ROWS_ACCESSED`

Study 8E is a separate extension of frozen Study 8. It is designed to test external contact-timing sensitivity without modifying the original deterministic 3,456-position population or the rejected Acta Astronautica submission package.

## Current authorized work

Authorized in this phase:

- prospective protocol design;
- source-documentation/schema review;
- candidate-source role definition;
- field mapping and claim-boundary definition;
- repository branch/PR preparation.

Not authorized in this phase:

- external dataset row download;
- external row analysis;
- extension runner implementation;
- canonical Study 8E execution;
- Study 8 modification;
- Acta package modification;
- publisher-facing manuscript revision based on unexecuted Study 8E results.

## Planned evidence layers

1. **SatNOGS Network**: primary external observation-opportunity timing source.
2. **ESA OPS-SAT-1 re-entry UHF telemetry**: secondary dependent reception-density/gap sensitivity source.
3. **LENS**: optional separately frozen LEO-network throughput/latency sensitivity layer.
4. **NASA HDTN**: optional future implementation harness after external-trace evidence is frozen.

## Design principle

The extension solves for the **minimum hypothetical uniform effective payload rate** needed for the frozen cryptographic transition bundle to complete within external observation-opportunity timing windows. It does not infer link capacity from SatNOGS transmitter baud and does not reinterpret the original Study 8 logical slots as physical time.

## Next gate

After review and explicit merge authorization:

1. merge the protocol freeze candidate;
2. perform source identity and schema-only validation;
3. select and freeze the exact SatNOGS trace-pair population using the predeclared deterministic rule;
4. materialize source artifacts and bind SHA-256 identities;
5. freeze an extension implementation on synthetic fixtures;
6. seek separate authorization before any canonical external-trace execution.
