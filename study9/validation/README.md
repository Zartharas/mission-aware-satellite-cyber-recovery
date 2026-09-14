# Study 9 Pre-Freeze Dataset Validation

This directory contains the pre-analysis integrity and reproducibility gate for Study 9 (`S9-RTSI-001`). Its purpose is to verify that the exact candidate dataset bytes, schemas, and preregistered exclusion policies are stable across the author's native macOS environment and a clean Linux/Python container before the Study 9 population is frozen.

This stage is intentionally **not scientific endpoint execution**. It does not perform recovery-state semantic mapping, invoke the frozen Study 2 selector, compute action identifiability, infer missing state, train a detector, or use attack labels as operational truth.

## Files

- `pre_freeze_dataset_validator.py` - standard-library-only deterministic validator for CuCD-ID v3, AegisSat, and UNSW-IoTSAT.
- `Dockerfile` - minimal Python 3.12 Linux environment containing exactly the same validator.
- `run_pre_freeze_validation.sh` - runs native validation, runs Docker validation with no network and read-only input mounts, compares deterministic outputs, and creates a compact evidence bundle.
- `README.md` - this governance and execution guide.

## Frozen input identities checked by this stage

### CuCD-ID v3

Source provenance:

- Dataset DOI: `10.17632/7n2d42pm3n.3`
- Article DOI: `10.1016/j.dib.2026.112598`
- Dataset license: CC BY 4.0

Expected downloaded package SHA-256:

`da3d95886feae0bc913a9e5beec1368571f51c80ecc811e40f6cc29edf33f2f0`

Canonical native artifact:

`Data/Raw/consolidated_dataset_raw.csv`

Expected SHA-256:

`2a6bb7bc9856099eef468dfe7df0043718a57c6ce84328e26b1883fa560c6ca2`

Expected dimensions: 25,000 rows x 31 columns.

`Data/Augmented/noised_dataset.csv` remains a derived/augmented companion and cannot replace the raw CSV as operational-native evidence. `Label` remains `OFFLINE_GROUND_TRUTH_ONLY`.

### AegisSat

Source provenance:

- Zenodo DOI: `10.5281/zenodo.14960983`
- Zenodo dataset license: CC BY 4.0
- Repository commit: `24c00de5ee729b91805724cbf82068562e7a4b6d`

Canonical artifact:

`AegisSat-AD.csv`

Expected MD5:

`f5b53ba9d080fe1795def09bdecd7cb9`

Expected SHA-256:

`dcbaa9bb23c6492087d5dd6a5e0729e42fa84a2d43f5370bca967276426e487e`

Expected dimensions: 137,965 rows x 176 columns.

The fields `attacks.cpuhightarget.duration` and `attacks.cpuhightarget.target` remain offline ground-truth/experiment metadata. They cannot create `security_signal` or another primary recovery-state variable.

### UNSW-IoTSAT

Expected downloaded package SHA-256:

`21f747325041e633df135aed2e12de4de518a5c4e62ded2270d7bbd0523c9d9d`

Canonical native artifact:

`UNSW_IoTSAT.csv`

Expected SHA-256:

`06ef6681c90fbf4c43c0e8993cc2ccc803c21fa32ed30cbf54165b526c851521`

Expected dimensions: 404,798 rows x 49 columns.

Preregistered artifact/field boundaries remain unchanged:

- `UNSW_IoTSAT.json` remains excluded because the release serialization is unterminated.
- `UNSW_IoTSAT_With_Feature_Engineering.csv` remains excluded from primary semantic mapping because it is a derived artifact whose original-field values are not semantically identical to the base release.
- `Vertical_Category`, `Horizontal_Speed_ms`, `Reception_Time`, and `Data_Quality_Score` remain wholly excluded from primary semantic mapping.
- `CCSDS_MC_Frame_Count`, `CCSDS_Packet_Sequence_Count`, and `CCSDS_APID` in the CCSDS companion remain label-conditioned derivatives and cannot count as operational-native evidence.

## Execution

From the repository root:

```bash
chmod +x study9/validation/run_pre_freeze_validation.sh

study9/validation/run_pre_freeze_validation.sh \
  --cucd "$HOME/Downloads/CubeSat Cybersecurity Dataset for Intrusion Detect.zip" \
  --aegissat "$HOME/Downloads/AegisSat-AD.csv" \
  --unsw "$HOME/Downloads/OneDrive_2026-09-13.zip"
```

An explicit output directory may be supplied with `--output`. If omitted, the runner creates a timestamped directory under `~/Downloads`.

The native validator reads the three source files without opening them for writing. The Docker validation mounts each source file `readonly`, runs with `--network none`, and uses a read-only container filesystem except for `/tmp` and the dedicated output mount.

The Docker build may need network access once to obtain the declared base image if it is not already present. The actual dataset validation container is run with networking disabled.

## Passing criteria

The gate passes only if all of the following are true:

1. Top-level source artifact hashes match the preregistered values.
2. Canonical file/member hashes match the independently verified values.
3. Expected rows, columns, and row widths match for each CSV.
4. CuCD-ID raw/augmented numeric-integrity checks remain clean and the raw five-class counts remain 5,000 each.
5. AegisSat retains the expected run/provenance, command, and attack-annotation fields.
6. UNSW-IoTSAT retains the exact six-file release identity, known malformed-JSON boundary, canonical base CSV, excluded artifacts/fields, and label-conditioned CCSDS companion fields.
7. Native and Docker `validation_core.json` files are byte-identical.

Environment-specific data such as OS version, Python executable, and generation time are stored only in `validation_report.json`. They are deliberately excluded from `validation_core.json`, allowing the scientific input validation result itself to be compared byte-for-byte across environments.

## Outputs

A successful run creates:

- `native/validation_core.json`
- `native/validation_report.json`
- `docker/validation_core.json`
- `docker/validation_report.json`
- `cross_environment_comparison.json`
- `EVIDENCE_BUNDLE.json`
- `<output-directory>_evidence.zip`

The evidence ZIP contains only compact validation reports. It does not contain dataset bytes.

## Governance boundary

A successful pre-freeze validation does **not** itself freeze the Study 9 population and does not authorize semantic mapping or endpoint computation. Population freeze remains a separate governance action. After a successful run, preserve the evidence bundle and review it before any population-freeze commit.

The existing `STUDY9_PROTOCOL.json` scientific-analysis authorization flags are intentionally unchanged by this validation infrastructure. This directory is a source-integrity/reproducibility control, not the Study 9 endpoint implementation.
