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
| **UNSW-IoTSAT** | Cyber Security and Applications DOI `10.1016/j.csa.2026.100133`; public repository `Osama-Abdelhameed/UNSW-IoTSAT` bound to commit `48ccc99ebd182d886eb18d2b94e95baba5a2a89a`; author-linked SharePoint/OneDrive release package independently audited and byte-hash bound | Release package contains 404,798-row base, CCSDS-companion, and engineered CSVs plus JSON and schema documentation. `UNSW_IoTSAT.csv` is selected as the canonical native artifact; CCSDS preserves the 49 base fields semantically but its three added fields are label-conditioned derivatives. The JSON export is unterminated and the engineered CSV changes 139 original-field cells across 17 columns, so both are excluded from primary mapping | The pinned project repository contains an MIT `LICENSE`, displays an MIT license badge in the README, and directly links the public UNSW SharePoint dataset. Study 9 adopts MIT as an author-approved project-distribution licensing assumption for this release. The downloaded package contains no separate license file, so this is recorded as a governance interpretation rather than independently verified dataset-specific license text | Independently developed UNSW hybrid cyber-physical testbed; no evidence found that it is derived from CuCD-ID or AegisSat | `SELECTION_GATE_PASS_INCLUDED_PENDING_POPULATION_FREEZE` |

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

Direct retrieval of the Zenodo record returned an HTTP 429 rate-limit response during this verification, and the record was later reported unavailable during Zenodo maintenance. These fields remain explicitly pending rather than inferred.

Current disposition: `PROVISIONAL_SELECTION_PASS_PENDING_ZENODO_FILE_MANIFEST_AND_LICENSE_VERIFICATION`.

This is no longer a broad provenance/schema hold. It is a narrow deposited-artifact gate.

## UNSW-IoTSAT selection-pass rationale

The author-linked SharePoint/OneDrive release package was obtained and audited read-only. The downloaded package `OneDrive_2026-09-13.zip` is byte-bound by SHA-256:

`21f747325041e633df135aed2e12de4de518a5c4e62ded2270d7bbd0523c9d9d`

The package contains six artifacts. The canonical native Study 9 candidate is `UNSW_IoTSAT.csv`, which contains 404,798 rows × 49 columns and has SHA-256:

`06ef6681c90fbf4c43c0e8993cc2ccc803c21fa32ed30cbf54165b526c851521`

The 52-column `UNSW_IoTSAT_with_CCSDS_fields.csv` preserves all 49 base fields semantically across all 404,798 aligned rows. Its three added CCSDS fields are generated by the repository augmentation code using attack labels (`Attack_Type`, `Attack_Subtype`, and `Attack_Severity`) and therefore are **label-conditioned derivatives**. They may be retained as documentation/derived companion evidence but cannot count as `OPERATIONAL_NATIVE` recovery state in primary Study 9 endpoints.

Two release representations are excluded from primary mapping:

- `UNSW_IoTSAT.json` is an unterminated top-level JSON array. Its final non-whitespace byte is `}` rather than `]`.
- `UNSW_IoTSAT_With_Feature_Engineering.csv` preserves row count and column layout but changes 139 original base-field cells across 17 original columns after feature-engineering/coercion. It is therefore a derived artifact, not the canonical native representation.

A separate full-release reconciliation identified a systematic tail-field quality defect. Across all 404,798 base rows, `Vertical_Category` does not contain a documented category in 404,796 rows, and two rows have unparseable `Velocity_Up_ms`. The observed tail patterns are:

- 290,792 rows: numeric `Vertical_Category`, numeric `Horizontal_Speed_ms`, datetime-like `Reception_Time`, numeric `Data_Quality_Score`;
- 113,876 rows: numeric `Vertical_Category`, datetime-like `Horizontal_Speed_ms`, numeric `Reception_Time`, numeric `Data_Quality_Score`;
- 130 rows: all four fields numeric.

Repository source code provides a plausible implementation-level explanation: the receiver explicitly produces `stable` as a valid `Vertical_Category`, while the ground-station combiner removes literal `stable` values before row normalization. Study 9 does not repair, infer, or re-align affected values. Instead, the entire affected four-field block is preregistered as unusable for primary semantic mapping:

- `Vertical_Category`
- `Horizontal_Speed_ms`
- `Reception_Time`
- `Data_Quality_Score`

These exclusions are conservative artifact-quality controls and are not Study 9 endpoint results.

For Study 9 governance, the licensing gate is closed under an explicit project-distribution interpretation. At repository commit `48ccc99ebd182d886eb18d2b94e95baba5a2a89a`, the project root contains an MIT `LICENSE`; the README displays an MIT license badge and directly links the public UNSW SharePoint dataset. The release package was obtained through that author-provided public path. The downloaded package itself contains no standalone license file. On the author's direction for this independent research project, Study 9 therefore treats the dataset release as distributed under the MIT-licensed project context. This is documented as a research-governance assumption, not as independently verified dataset-specific legal advice or as a claim that a separate MIT license file was present in the data package. The eventual manuscript must cite the UNSW-IoTSAT article and source repository when the dataset is used.

Current disposition: `SELECTION_GATE_PASS_INCLUDED_PENDING_POPULATION_FREEZE`.

Detailed artifact hashes, defect counts, exclusion rules, provenance, and the licensing interpretation are preserved in `UNSW_IOTSAT_ARTIFACT_VERIFICATION.json`.

## Screened dependency risk

### LighTellite

LighTellite is not part of the initial independent-dataset candidate set because its 2026 study reports data collection using the AegisSat testbed. It may be relevant literature or a future dependent population, but it must not be counted as an additional independent testbed unless shared provenance is explicitly modeled.

Current disposition: `EXCLUDED_FROM_PRIMARY_INDEPENDENT_SCREEN_SHARED_AEGISSAT_PROVENANCE`.

## Selection rules that prevent post-result cherry-picking

- The primary dataset set must be frozen before any row-level Study 9 endpoint is computed.
- Failure of a candidate to pass provenance, schema, license, accessibility, or preregistered artifact-quality checks is a valid exclusion and must be documented rather than repaired through undocumented substitution.
- A candidate may not be removed because its semantic coverage is poor, its results are null, or it weakens a preferred narrative.
- A new candidate may not be added after endpoint inspection merely to improve coverage or publication attractiveness.
- Negative and null mapping results remain valid Study 9 outcomes.
- A HOLD, provisional, or technical-pass status may be cleared only by resolving the stated pre-analysis evidence deficiency, not by relaxing the inclusion criteria.
- Source defects are preserved as evidence. Study 9 does not silently repair, re-align, or impute affected source fields.

## Current decision

- **CuCD-ID v3:** selection gate passed; retained for the prospective primary population, pending final population freeze and independent byte-level verification before row analysis.
- **AegisSat:** provisional selection pass; correct GitHub repository and commit, DOI chain, implementation-derived persistence interface, and software license are bound; exact Zenodo deposited-file manifest, dataset license, file identities/checksums, and deposited-schema reconciliation remain pending.
- **UNSW-IoTSAT:** selection gate passed under the recorded MIT project-distribution governance interpretation, with canonical base-CSV binding and preregistered artifact/field exclusions; retained pending final population freeze.

The primary Study 9 dataset population is **not yet frozen**. Dataset ingestion into this research repository, implementation creation, semantic mapping execution, endpoint computation, results generation, manuscript creation, and submission remain unauthorized under `STUDY9_PROTOCOL.json`.
