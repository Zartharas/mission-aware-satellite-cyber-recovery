# Study 9 Dataset Selection Register

**Study:** `S9-RTSI-001`  
**Phase:** 9.0 prospective design  
**Verification date:** 2026-09-13  
**Status:** `SOURCE_VERIFICATION_RECORDED_POPULATION_NOT_YET_FROZEN`

## Purpose

This register records the candidate-source screen before any Study 9 dataset ingestion or row-level analysis. A candidate appears here because it is scientifically relevant enough to investigate. Selection status is based on artifact identity, schema evidence, legal terms, provenance, accessibility, and source-population independence rather than on any Study 9 endpoint result.

The selection gate is deliberately stricter than Study 5. Study 9 must independently verify source evidence rather than importing the frozen Study 5 manifest as new Study 9 evidence.

## Inclusion gate

A dataset must satisfy every required gate in `STUDY9_PROTOCOL.json` before it enters the frozen primary Study 9 population:

1. public and stably identifiable source artifact;
2. primary-source evidence of space or satellite cybersecurity relevance;
3. analyzable and documented data schema;
4. version, release, commit, DOI, or equivalent provenance that can be frozen;
5. legal usability for the intended academic analysis;
6. independent population provenance, or explicit modeling of shared provenance;
7. no need for unauthorized operational interaction or fabricated recovery state.

A source may pass the selection gate before its bytes are ingested into this repository. Byte-level hash verification is still required before row-level analysis of that source.

## Direct-source verification disposition

| Candidate | Verified provenance | Verified schema/access evidence | Legal/access state | Independence assessment | Current disposition |
| --- | --- | --- | --- | --- | --- |
| **CuCD-ID v3** | Mendeley Data DOI `10.17632/7n2d42pm3n.3`, published 2026-02-10; Data in Brief DOI `10.1016/j.dib.2026.112598` | Primary article documents raw `Data/Raw/consolidated_dataset_raw.csv` as 25,000 rows × 31 columns and augmented `Data/Augmented/noised_dataset.csv` as 22,465 rows × 23 columns, with field-level schema described in the article; published SHA-256 values are recorded in `DATASET_SCHEMA_MANIFEST.json` | Dataset host reports **CC BY 4.0** and public Mendeley access | Independent NOS3/cFS software-in-the-loop population relative to the other screened testbeds | `SELECTION_GATE_PASS_INCLUDED_PENDING_POPULATION_FREEZE_AND_BYTE_HASH_VERIFICATION` |
| **AegisSat** | SpaceSec 2025 paper *AegisSat: A Satellite Cybersecurity Testbed*; correct public repository `texydo/satellite_security_testbed`; repository bound to commit `24c00de5ee729b91805724cbf82068562e7a4b6d`; repository identifies Zenodo DOI `10.5281/zenodo.14960983` | Repository implementation exposes the MongoDB persistence interface used for runs, including `run_id`, `TLE File Name`, `TLE`, `Epoch_Time`, `UTC_time`, optional `cosmos_data`, `command`, `pi_metrics`, `satState`, and optional `attacks`; COSMOS telemetry is persisted as packet-keyed field dictionaries. Primary paper documents the physical CubeSat/environment-emulator setting, 1 Hz telemetry, commands, attacks, and hundreds of experiments | Repository software is MIT licensed. Direct Zenodo record retrieval was rate-limited during verification, so the deposited dataset license, exact file manifest, file sizes, and checksums remain unverified and are not inferred from the repository license | Scientifically distinct physical/emulation provenance; no evidence found that it is derived from CuCD-ID or UNSW-IoTSAT | `PROVISIONAL_SELECTION_PASS_PENDING_ZENODO_FILE_MANIFEST_AND_LICENSE_VERIFICATION` |
| **UNSW-IoTSAT** | Cyber Security and Applications DOI `10.1016/j.csa.2026.100133`; public repository `Osama-Abdelhameed/UNSW-IoTSAT`; repository `main` bound during verification to commit `48ccc99ebd182d886eb18d2b94e95baba5a2a89a` | Repository feature documentation reports 404,798 records, 109 main-release features plus 3 CCSDS companion features, and explicit `MEASURED`, `SIMULATED`, `COMPUTED`, and `LABEL` origins | Repository software/documentation is MIT licensed, but the separately hosted dataset link redirected to a Microsoft/UNSW sign-in flow during verification; dataset-specific license and anonymous artifact access therefore remain unresolved | Independently developed UNSW hybrid cyber-physical testbed; no evidence found that it is derived from CuCD-ID or AegisSat | `HOLD_PENDING_PUBLIC_DATASET_ARTIFACT_AND_DATASET_LICENSE_VERIFICATION` |

## CuCD-ID v3 selection rationale

CuCD-ID v3 clears the source-selection gate because its versioned DOI, public host, dataset license, testbed provenance, table dimensions, schema documentation, and published artifact hashes are available from the dataset host and primary Data in Brief article.

The two primary tabular artifacts are reported by the primary article as:

- `Data/Raw/consolidated_dataset_raw.csv`: 25,000 rows × 31 columns; published SHA-256 `2a6bb7bc9856099eef468dfe7df0043718a57c6ce84328e26b1883fa560c6ca2`.
- `Data/Augmented/noised_dataset.csv`: 22,465 rows × 23 columns; published SHA-256 `656fc2f23544469d8cbdca631747debc8dae7164621a2cd6740a5928cfae3c68`.

These hashes are **source-reported values**, not Study 9 byte-level recomputations. Study 9 must independently verify downloaded bytes against them before any row-level analysis. The frozen Study 5 copy of the same values is not treated as Study 9 evidence.

Current disposition: `SELECTION_GATE_PASS_INCLUDED_PENDING_POPULATION_FREEZE_AND_BYTE_HASH_VERIFICATION`.

## AegisSat provisional-pass rationale

AegisSat now has a verified research-to-repository provenance chain. The SpaceSec 2025 work is associated with the public repository `texydo/satellite_security_testbed`, and that repository identifies Zenodo DOI `10.5281/zenodo.14960983`. The repository state observed during verification is bound to:

`24c00de5ee729b91805724cbf82068562e7a4b6d`

The repository `LICENSE` is MIT. That establishes software/repository licensing only; Study 9 does not assume it also licenses every deposited Zenodo dataset artifact.

The implementation provides reproducible evidence for the run-persistence interface. `ManagerClass.py` writes MongoDB documents containing core run provenance (`run_id`, TLE identity/content, epoch and UTC time), satellite state, and optional COSMOS telemetry, command, Raspberry Pi metrics, and attacks. COSMOS telemetry is normalized into packet-keyed dictionaries before persistence. These implementation-derived fields are schema evidence for the generating testbed, not a claim that every deposited Zenodo file has already been inspected or that the deposited dataset schema is fully locked.

The remaining pre-inclusion work is therefore narrow and artifact-specific:

- verify the exact Zenodo deposited-file manifest;
- verify the dataset license from the Zenodo record;
- record deposited file sizes and checksums or equivalent immutable identities;
- bind the exact deposited dataset version used for Study 9;
- reconcile the deposited dataset's actual field schema with the implementation-derived persistence interface before mapping.

Direct retrieval of the Zenodo record returned an HTTP 429 rate-limit response during this verification, so these fields remain explicitly pending rather than inferred.

Current disposition: `PROVISIONAL_SELECTION_PASS_PENDING_ZENODO_FILE_MANIFEST_AND_LICENSE_VERIFICATION`.

This is no longer a broad provenance/schema hold. It is a narrow deposited-artifact gate.

## UNSW-IoTSAT hold rationale

UNSW-IoTSAT has strong schema documentation. The repository explicitly distinguishes measured, simulated, computed, and label-derived variables, which is valuable for Study 9 because attack labels can be kept outside the primary operational recovery-state mapping.

The repository state observed during verification is bound to:

`48ccc99ebd182d886eb18d2b94e95baba5a2a89a`

The repository `LICENSE` is MIT. That license is evidence for the repository software/documentation and is **not assumed to license the separately hosted dataset bytes**.

The dataset link exposed from the public repository redirected to a Microsoft/UNSW authentication flow during this verification. The primary article describes the dataset as publicly available, but Study 9 requires directly reproducible artifact access and dataset-specific legal terms before inclusion.

Before inclusion, Study 9 must resolve:

- anonymous or otherwise reproducibly public access to the released dataset artifact;
- dataset-specific license or rights statement;
- immutable dataset version/file identity;
- released file inventory and hashes.

Current disposition: `HOLD_PENDING_PUBLIC_DATASET_ARTIFACT_AND_DATASET_LICENSE_VERIFICATION`.

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
- A HOLD or provisional status may be cleared only by resolving the stated pre-analysis evidence deficiency, not by relaxing the inclusion criteria.

## Current decision

- **CuCD-ID v3:** selection gate passed; retained for the prospective primary population, pending final population freeze and independent byte-level verification before row analysis.
- **AegisSat:** provisional selection pass; correct GitHub repository and commit, DOI chain, implementation-derived persistence interface, and software license are bound; exact Zenodo deposited-file manifest, dataset license, file identities/checksums, and deposited-schema reconciliation remain pending.
- **UNSW-IoTSAT:** hold pending reproducibly public dataset artifact access and dataset-specific license verification.

The primary Study 9 dataset population is **not yet frozen**. Dataset ingestion into this research repository, implementation creation, semantic mapping execution, endpoint computation, results generation, manuscript creation, and submission remain unauthorized under `STUDY9_PROTOCOL.json`.
