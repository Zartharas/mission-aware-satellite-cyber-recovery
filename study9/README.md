# Study 9: Recovery-State Transfer and Semantic Interoperability

**Study ID:** `S9-RTSI-001`  
**Phase:** 9.0 prospective design  
**Status:** `PROSPECTIVE_DESIGN_OPEN_NO_ANALYSIS_AUTHORIZED`  
**Base main commit:** `49323c6f78d8a9ae14e09573a4b126b5bf0fda10`

## Purpose

Study 9 is a prospective, separate research line that examines whether public space-cyber datasets expose enough decision-relevant state to support a bounded mission-aware recovery interface without inventing or silently imputing missing security semantics.

The central question is not whether an intrusion detector transfers across datasets. The study instead asks whether heterogeneous security telemetry can be translated into a recovery-decision interface with explicit, reproducible semantics and, where it cannot, which additional state would be required to make the downstream decision identifiable.

## Publication strategy

The intended publication target is **Cyber Security and Applications**. This is a publication-strategy choice only. The scientific protocol, inclusion rules, endpoints, and interpretation boundaries must remain venue-neutral and may not be changed after observing results merely to improve journal fit.

No manuscript has been created and no submission is authorized by this phase.

## Relationship to frozen work

- Study 5 (`S5-CUCD-001`) remains frozen and unchanged.
- The submitted Paper 1, Paper 2, Paper 3, and Paper 4 publication lines remain frozen and unchanged.
- No frozen Study 5 observation, action count, or sufficiency result becomes a Study 9 observation.
- Study 5 may be cited later as motivation for the prospective question, but Study 9 must independently establish source provenance, dataset eligibility, schema evidence, and any new measurements.
- Study 9 may reference the frozen Study 2 recovery selector as a bounded downstream decision interface. Reuse of that interface does not authorize retrospective modification of Study 2.

## Candidate dataset screen

The initial candidate screen contains:

1. CuCD-ID v3
2. AegisSat
3. UNSW-IoTSAT

Candidate status is not inclusion. Every source must pass the preregistered selection gate and artifact-verification requirements before it enters the Study 9 population.

A derivative or follow-on dataset that shares a testbed or underlying experimental population with another candidate is not treated as an independent testbed population unless that dependence is modeled explicitly.

## Design artifacts

- `STUDY9_PROTOCOL.json`: prospective research questions, endpoints, inclusion rules, analysis boundaries, and stopping rules.
- `DATASET_SELECTION_REGISTER.md`: candidate-source screening and unresolved inclusion checks.
- `DATASET_SCHEMA_MANIFEST.json`: source and schema provenance register. No candidate is schema-locked yet.
- `RECOVERY_STATE_MAPPING_RUBRIC.json`: preregistered semantic classification rules.
- `CLAIM_BOUNDARY.md`: permitted and prohibited interpretations.
- `THREAT_MODEL.md`: bounded semantic and decision threat model.
- `LITERATURE_SOURCE_LEDGER.md`: design-stage literature and source provenance.

## Current authorization boundary

This branch is authorized only for prospective design and source-selection work.

The following remain false:

```text
dataset_ingestion_authorized=false
row_level_analysis_authorized=false
implementation_creation_authorized=false
canonical_execution_authorized=false
results_directory_authorized=false
manuscript_creation_authorized=false
submission_authorized=false
```

A later explicit authorization is required before downloading research datasets into the repository, creating analysis code, running a canonical experiment, creating a results population, or drafting a manuscript.
