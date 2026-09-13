# Study 9 Dataset Selection Register

**Study:** `S9-RTSI-001`  
**Phase:** 9.0 prospective design  
**Verification date:** 2026-09-13  
**Status:** `CANDIDATE_SCREEN_OPEN_NO_DATASET_INCLUDED`

## Purpose

This register records the candidate-source screen before any Study 9 dataset ingestion or row-level analysis. A candidate appears here because it is scientifically relevant enough to investigate. Appearance in this register does not mean that it has been included in the canonical Study 9 population.

The selection gate is deliberately stricter than Study 5. Study 9 must independently verify artifact identity, schema, legal terms, provenance, and population independence before a dataset is admitted.

## Inclusion gate

A dataset must satisfy every required gate in `STUDY9_PROTOCOL.json` before inclusion:

1. public and stably identifiable source artifact;
2. primary-source evidence of space or satellite cybersecurity relevance;
3. analyzable and documented data schema;
4. version, release, commit, DOI, or equivalent provenance that can be frozen;
5. legal usability for the intended academic analysis;
6. independent population provenance, or explicit modeling of shared provenance;
7. no need for unauthorized operational interaction or fabricated recovery state.

## Initial candidate screen

| Candidate | Primary source and provenance | Environment | Preliminary scientific relevance | Current gate state | Required pre-inclusion work |
| --- | --- | --- | --- | --- | --- |
| **CuCD-ID v3** | Mendeley Data DOI `10.17632/7n2d42pm3n.3`; Data in Brief DOI `10.1016/j.dib.2026.112598` | NOS3/cFS software-in-the-loop with OpenC3 COSMOS ground-side scenario generation | Public labelled CubeSat command and telemetry data with CCSDS-derived and engineered features; directly relevant to the question of whether IDS-oriented telemetry exposes recovery-decision state | `CANDIDATE_PRELIMINARY_PASS_ARTIFACT_REVERIFY_REQUIRED` | Independently fetch v3 for Study 9, record file list and hashes, freeze exact field names/types, verify dataset license from the dataset host, and do not reuse the frozen Study 5 manifest as Study 9 evidence |
| **AegisSat** | SpaceSec 2025 paper, *AegisSat: A Satellite Cybersecurity Testbed*; dataset DOI reported as `10.5281/zenodo.14960983` | Physical Earth-based CubeSat plus environmental emulator and attack manager; telemetry and labelled attack experiments | Offers materially different testbed provenance from CuCD-ID and may expose physical/system state absent from software-only data | `CANDIDATE_PENDING_DIRECT_ARTIFACT_VERIFICATION` | Resolve the current Zenodo record directly, verify license and artifact files, bind an exact dataset version, enumerate schema and experiment identifiers, and determine whether released files are sufficient for reproducible field-level mapping |
| **UNSW-IoTSAT** | Cyber Security and Applications DOI `10.1016/j.csa.2026.100133`; public source repository identified by the article as `Osama-Abdelhameed/UNSW-IoTSAT` | Hybrid cyber-physical smart-satellite testbed with CCSDS-oriented communications, IoT sensor data, RF-layer impairments, and attack scenarios | Provides a third independently developed public space-cyber source and directly demonstrates target-venue interest in satellite cybersecurity datasets | `CANDIDATE_PRELIMINARY_PASS_REPOSITORY_BINDING_REQUIRED` | Freeze a specific public repository commit or release, verify license and dataset artifacts, enumerate schema and labels, record file hashes, and confirm independence from the other included testbeds |

## Screened dependency risk

### LighTellite

LighTellite is not part of the initial independent-dataset candidate set because its 2026 study reports data collection using the AegisSat testbed. It may be relevant literature or a future dependent population, but it must not be counted as an additional independent testbed unless shared provenance is explicitly modeled.

Current disposition: `EXCLUDED_FROM_PRIMARY_INDEPENDENT_SCREEN_SHARED_AEGISSAT_PROVENANCE`.

## Selection rules that prevent post-result cherry-picking

- The primary dataset set must be frozen before any row-level Study 9 endpoint is computed.
- Failure of a candidate to pass provenance, schema, license, or accessibility checks is a valid exclusion and must be documented rather than repaired through undocumented substitution.
- A candidate may not be removed because its semantic coverage is poor, its results are null, or it weakens a preferred narrative.
- A new candidate may not be added after endpoint inspection merely to improve coverage or publication attractiveness.
- Negative and null mapping results remain valid Study 9 outcomes.

## Current decision

No dataset is included yet.

The next authorized design-stage task is direct artifact and schema verification only. Dataset download into this research repository, analysis-code creation, semantic mapping execution, and result generation remain unauthorized until a later explicit gate.
