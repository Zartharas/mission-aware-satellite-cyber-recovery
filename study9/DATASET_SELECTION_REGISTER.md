# Study 9 Dataset Selection Register

**Study:** `S9-RTSI-001`<br>
**Phase:** 9.0 prospective design<br>
**Verification date:** 2026-09-13<br>
**Status:** `PRIMARY_POPULATION_FROZEN_SEMANTIC_ADJUDICATION_NOT_YET_FROZEN`

## Purpose

This register records the Study 9 source-selection process and the frozen primary source population before any semantic mapping or Study 9 endpoint computation. Selection and freeze decisions are based on artifact identity, schema evidence, legal terms, provenance, accessibility, source-population independence, and pre-analysis reproducibility checks rather than on any Study 9 result.

The selection gate is deliberately stricter than Study 5. Study 9 independently verifies source evidence and does not import the frozen Study 5 manifest as new Study 9 evidence.

## Inclusion gate

A dataset must satisfy every required gate in `STUDY9_PROTOCOL.json` before it enters the frozen primary Study 9 population:

1. public and stably identifiable source artifact;
2. primary-source evidence of space or satellite cybersecurity relevance;
3. analyzable and documented data schema;
4. version, release, commit, DOI, or equivalent provenance that can be frozen;
5. legal usability for the intended academic analysis;
6. independent population provenance, or explicit modeling of shared provenance;
7. no need for unauthorized operational interaction or fabricated recovery state;
8. byte-level identity and pre-analysis integrity validation completed before row-level analysis.

## Pre-freeze reproducibility gate

The three selected source populations were validated with the same standard-library validator on native macOS and in a Linux Docker container before the population freeze. The Docker validation used read-only dataset mounts, a read-only container root filesystem, and no runtime network access.

Canonical evidence:

- validation record: `study9/PRE_FREEZE_VALIDATION_EVIDENCE.json`
- uploaded evidence bundle: `Study9_PreFreeze_Validation_20260913_211741_evidence.zip`
- evidence bundle SHA-256: `10869b324f754d24630b02de770e5095ebf46a9009b9b3f5cb1f846adcc9328f`
- deterministic validation-core SHA-256: `bbcfe1c8f3605b252c9bf5bfd55c32f7fbd024e61b3d9bcee2f973707e7e8cf5`
- native and Docker deterministic cores byte-identical: **yes**
- CuCD-ID v3 checks: **19/19 PASS**
- AegisSat checks: **8/8 PASS**
- UNSW-IoTSAT checks: **27/27 PASS**
- total: **54/54 PASS**

This gate did not modify dataset bytes, impute missing state, use attack labels as operational state, execute the recovery selector, perform semantic mapping, compute Study 9 endpoints, or freeze the population by itself.

## Frozen primary population

The primary source population is frozen in `study9/PRIMARY_POPULATION_FREEZE.json` as exactly these three separate finite populations:

| Candidate | Verified provenance | Canonical primary artifact | Independence assessment | Frozen disposition |
| --- | --- | --- | --- | --- |
| **CuCD-ID v3** | Mendeley Data DOI `10.17632/7n2d42pm3n.3`, Version 3, published 2026-02-10; Data in Brief DOI `10.1016/j.dib.2026.112598`; downloaded Version 3 package independently audited and byte-hash bound | `Data/Raw/consolidated_dataset_raw.csv`, 25,000 rows × 31 columns, SHA-256 `2a6bb7bc9856099eef468dfe7df0043718a57c6ce84328e26b1883fa560c6ca2` | Independent NOS3/cFS software-in-the-loop population relative to the other frozen testbeds | `PRIMARY_POPULATION_FROZEN_INCLUDED` |
| **AegisSat** | SpaceSec 2025 paper *AegisSat: A Satellite Cybersecurity Testbed*; repository `texydo/satellite_security_testbed` at commit `24c00de5ee729b91805724cbf82068562e7a4b6d`; Zenodo DOI `10.5281/zenodo.14960983` | `AegisSat-AD.csv`, 137,965 rows × 176 columns, SHA-256 `dcbaa9bb23c6492087d5dd6a5e0729e42fa84a2d43f5370bca967276426e487e`, MD5 `f5b53ba9d080fe1795def09bdecd7cb9` | Scientifically distinct physical/emulation provenance; no evidence that it is derived from CuCD-ID or UNSW-IoTSAT | `PRIMARY_POPULATION_FROZEN_INCLUDED` |
| **UNSW-IoTSAT** | Cyber Security and Applications DOI `10.1016/j.csa.2026.100133`; repository `Osama-Abdelhameed/UNSW-IoTSAT` at commit `48ccc99ebd182d886eb18d2b94e95baba5a2a89a`; author-linked public release package byte-hash bound | `UNSW-IoTSAT dataset/UNSW_IoTSAT.csv`, 404,798 rows × 49 columns, SHA-256 `06ef6681c90fbf4c43c0e8993cc2ccc803c21fa32ed30cbf54165b526c851521` | Independently developed UNSW hybrid cyber-physical testbed; no evidence that it is derived from CuCD-ID or AegisSat | `PRIMARY_POPULATION_FROZEN_INCLUDED` |

The three datasets remain separate finite populations. They are not pooled into one empirical population for inferential claims.

## CuCD-ID v3 frozen-source rationale

CuCD-ID v3 has a verified article-to-Mendeley-to-byte chain. The exact downloaded Version 3 package is byte-bound by SHA-256:

`da3d95886feae0bc913a9e5beec1368571f51c80ecc811e40f6cc29edf33f2f0`

The two tabular artifacts independently verify as:

- `Data/Raw/consolidated_dataset_raw.csv`: 25,000 rows × 31 columns; SHA-256 `2a6bb7bc9856099eef468dfe7df0043718a57c6ce84328e26b1883fa560c6ca2`; exact match to the published Version 3 checksum.
- `Data/Augmented/noised_dataset.csv`: 22,465 rows × 23 columns; SHA-256 `656fc2f23544469d8cbdca631747debc8dae7164621a2cd6740a5928cfae3c68`; exact match to the published Version 3 checksum.

Both CSVs have zero row-width mismatches, zero blank values, zero nonnumeric values, and zero NaN/Inf values. The raw artifact contains exactly 5,000 rows for each of the five integer labels in `label_schema.json`.

For Study 9, `consolidated_dataset_raw.csv` is the canonical native data artifact. `noised_dataset.csv` remains a deterministic derived/augmented companion and cannot replace the native raw artifact for primary operational-state mapping. `Label` remains `OFFLINE_GROUND_TRUTH_ONLY` and cannot create `security_signal` or any other operational recovery-state variable.

Two package defects remain preserved rather than repaired: the source checksum helper can skip verification because the checksum file contains bare digests while the parser expects digest-plus-path entries, and the root README refers to `/Code/Scripts/` while the actual scenario directory is `Code/Cosmos_Scripts/`. Study 9 relies on independent byte recomputation and does not modify the source package.

Detailed evidence remains in `CUCD_ID_V3_ARTIFACT_VERIFICATION.json`.

## AegisSat frozen-source rationale

AegisSat has a verified research-to-repository-to-Zenodo chain. The pinned repository state is:

`24c00de5ee729b91805724cbf82068562e7a4b6d`

The Zenodo deposit contains one CSV:

- `AegisSat-AD.csv`
- 190,028,590 bytes
- 137,965 rows × 176 columns
- zero row-width mismatches
- Zenodo MD5 `f5b53ba9d080fe1795def09bdecd7cb9`
- Study 9 SHA-256 `dcbaa9bb23c6492087d5dd6a5e0729e42fa84a2d43f5370bca967276426e487e`

The CSV reconciles with the verified persistence interface through run/TLE provenance, `Epoch_Time`, `UTC_Time`, flattened `cosmos_data`, `command`, and attack fields. Optional persistence concepts such as `pi_metrics` and `satState` are not inferred when absent as standalone export columns.

The attack fields `attacks.cpuhightarget.duration` and `attacks.cpuhightarget.target` remain `OFFLINE_GROUND_TRUTH_OR_EXPERIMENT_METADATA_ONLY` and cannot create `security_signal` or another operational recovery-state variable.

Detailed evidence remains in `AEGISSAT_ARTIFACT_VERIFICATION.json`.

## UNSW-IoTSAT frozen-source rationale

The author-linked SharePoint/OneDrive release package is byte-bound by SHA-256:

`21f747325041e633df135aed2e12de4de518a5c4e62ded2270d7bbd0523c9d9d`

The canonical native artifact is `UNSW_IoTSAT.csv`, which contains 404,798 rows × 49 columns and has SHA-256:

`06ef6681c90fbf4c43c0e8993cc2ccc803c21fa32ed30cbf54165b526c851521`

The 52-column CCSDS companion preserves the 49 base fields semantically, but its three added CCSDS fields are generated using attack labels and therefore cannot count as `OPERATIONAL_NATIVE` recovery state.

Two release representations remain excluded from primary mapping:

- `UNSW_IoTSAT.json` because its top-level JSON array is unterminated;
- `UNSW_IoTSAT_With_Feature_Engineering.csv` because it is derived and modifies 139 original-field cells across 17 original columns.

The four-field tail block remains excluded wholesale from primary semantic mapping without row-local salvage or repair:

- `Vertical_Category`
- `Horizontal_Speed_ms`
- `Reception_Time`
- `Data_Quality_Score`

The license gate remains governed by the recorded MIT project-distribution interpretation: the pinned project repository contains an MIT license and directly links the public dataset, but no separate dataset-specific license file was found in the downloaded package. This remains a research-governance interpretation, not legal advice.

Detailed evidence remains in `UNSW_IOTSAT_ARTIFACT_VERIFICATION.json`.

## Screened dependency risk

### LighTellite

LighTellite is not part of the frozen independent primary population because its 2026 study reports data collection using the AegisSat testbed. It may remain relevant literature or a future dependent population, but it cannot be counted as another independent testbed unless shared provenance is explicitly modeled through a documented protocol deviation.

Current disposition: `EXCLUDED_FROM_PRIMARY_INDEPENDENT_SCREEN_SHARED_AEGISSAT_PROVENANCE`.

## Post-freeze rules that prevent result-driven membership changes

- The primary population is frozen before semantic mapping and before any row-level Study 9 endpoint is computed.
- A frozen member may not be removed because semantic coverage is poor, results are null, or it weakens a preferred narrative.
- A new primary population may not be added after endpoint inspection merely to improve coverage or publication attractiveness.
- Any later population change requires a documented protocol deviation and must not rewrite the frozen primary-population record retroactively.
- Negative and null mapping results remain valid Study 9 outcomes.
- Source defects remain preserved as evidence. Study 9 does not silently repair, re-align, or impute affected source fields.

## Current decision

- **CuCD-ID v3:** `PRIMARY_POPULATION_FROZEN_INCLUDED`.
- **AegisSat:** `PRIMARY_POPULATION_FROZEN_INCLUDED`.
- **UNSW-IoTSAT:** `PRIMARY_POPULATION_FROZEN_INCLUDED`.

The Study 9 primary source population is now frozen. Artifact identities are locked, but field-to-recovery-state semantic adjudication is **not yet frozen**. Dataset ingestion into this research repository, implementation creation, semantic mapping execution, endpoint computation, results generation, manuscript creation, and submission remain unauthorized under `STUDY9_PROTOCOL.json`.

The next required gate is to freeze the exact field-to-recovery-state adjudication and any permitted deterministic derivation rules before any semantic mapping or endpoint computation.
