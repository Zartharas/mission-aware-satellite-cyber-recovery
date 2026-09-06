# Study 8 - Contact-Aware Cryptographic Agility and Trusted Recovery

**Experiment:** `S8-PQC-ICR-001`  
**Manuscript title:** *Contact-Aware Cryptographic Agility for Trusted Post-Compromise Recovery in Intermittently Connected Space Systems*  
**Study type:** deterministic finite modeled contact/crypto-agility/recovery study  
**Frozen source-package status:** `PUBLICATION_PACKAGE_HASH_FROZEN_MERGED_TO_MAIN_POST_MERGE_VALIDATED`  
**Current publisher status:** `ACTA_SUBMITTED__WITH_EDITOR`  
**Acta manuscript ID:** `AA-D-26-02872`

Study 8 is a separately frozen companion study in this repository. It remains outside the Study-1/Study-2 journal manuscript and has its own frozen source publication package under [`../publication/study8/`](../publication/study8/README.md) plus a venue-specific submitted-state package under [`../publication/Paper_4_Study_8/Acta_Astronautica/`](../publication/Paper_4_Study_8/Acta_Astronautica/README_CURRENT.md).

## Scientific technical close

The exact Study-8 science was merged to `main` through PR `#89` as commit:

```text
63106778559c3127a7d6e8765d52939b73a3f35b
```

The required post-science-merge repository validation completed successfully:

```text
workflow: Validate research configurations
run:      33761681328
attempt:  1
result:   SUCCESS
```

Authoritative scientific closeout records:

- [`STUDY8_TECHNICAL_CLOSE.json`](STUDY8_TECHNICAL_CLOSE.json)
- [`docs/PHASE8_7_TECHNICAL_CLOSE.md`](docs/PHASE8_7_TECHNICAL_CLOSE.md)
- [`analysis/RESULTS_FREEZE_MANIFEST.json`](analysis/RESULTS_FREEZE_MANIFEST.json)
- [`analysis/RESULTS_FREEZE_SHA256SUMS.txt`](analysis/RESULTS_FREEZE_SHA256SUMS.txt)
- [`results/S8-PQC-ICR-001/independent_audit_summary.json`](results/S8-PQC-ICR-001/independent_audit_summary.json)

The Phase-8.7 technical-close record intentionally retains its historical status `TECHNICALLY_CLOSED_PUBLICATION_INTEGRATION_NOT_STARTED`. That status describes the technical-close gate at the time it was written; it is not the current publication state.

## Frozen companion publication package

The target-neutral companion-paper package was developed from frozen science only, adversarially reviewed, hash-frozen, and merged through PR `#92`.

```text
frozen package commit:   cbad15227bf99d1b7b19d95b0581196d78208f95
final reviewed head:     75c98356751087dd648684ade7cb973c166cbce0
publication PR:          #92
main merge commit:       87bcec000d278aeffef1222ce814098c93ada362
results-freeze CI:       33781901833 SUCCESS
repository-wide CI:      33781901724 SUCCESS
```

Frozen source-package records:

- [`../publication/study8/README.md`](../publication/study8/README.md)
- [`../publication/study8/PUBLICATION_DEVELOPMENT_STATUS.json`](../publication/study8/PUBLICATION_DEVELOPMENT_STATUS.json)
- [`../publication/study8/PUBLICATION_PACKAGE_FREEZE_MANIFEST.json`](../publication/study8/PUBLICATION_PACKAGE_FREEZE_MANIFEST.json)
- [`../publication/study8/SHA256SUMS.txt`](../publication/study8/SHA256SUMS.txt)
- [`../publication/study8/FINAL_ADVERSARIAL_REVIEW.md`](../publication/study8/FINAL_ADVERSARIAL_REVIEW.md)

The Phase-8.9 source freeze binds exactly 11 publication artifacts. Those frozen files remain unchanged.

## Acta Astronautica submission

The Acta-specific publisher package was built and editorially refrozen as `S8-ACTA-PKGFREEZE-002`. The exact submitted publisher-facing files came from repository commit:

```text
f5e9a1d4553737e534821bf647463abfd44fa0dd
```

The author explicitly authorized final submission, and the manuscript was submitted to **Acta Astronautica** on **2026-09-06**. Editorial Manager assigned:

```text
manuscript ID: AA-D-26-02872
article type:  Research paper
status:        With Editor
```

Current submitted-state authority:

- [`../publication/Paper_4_Study_8/Acta_Astronautica/README_CURRENT.md`](../publication/Paper_4_Study_8/Acta_Astronautica/README_CURRENT.md)
- [`../publication/Paper_4_Study_8/Acta_Astronautica/ACTA_SUBMISSION_STATUS.json`](../publication/Paper_4_Study_8/Acta_Astronautica/ACTA_SUBMISSION_STATUS.json)
- [`../publication/Paper_4_Study_8/Acta_Astronautica/SUBMISSION_CONFIRMED_2026-09-06.md`](../publication/Paper_4_Study_8/Acta_Astronautica/SUBMISSION_CONFIRMED_2026-09-06.md)

Historical `S8-ACTA-PKGFREEZE-002` preparation files retain their stage-local pre-submission wording by design. Do not rewrite those frozen records merely to make them look current.

## Frozen scientific record

The frozen factorial population contains exactly **3,456 modeled observations**.

Independent implementation-level reproduction:

- primary rows: **3,456**
- independent rows: **3,456**
- exact row matches: **3,456**
- mismatches: **0**

Frozen evidence identities:

- canonical observations SHA-256: `cfc65b6663be4e9f17a00ed102730f8642efcbbd844045acce032ff09a0bcabf`
- primary findings SHA-256: `26a8ac4d1039917323e75a294775dd14a2b563adb12a5d2fcdb47ce8f15c992e`
- independent findings SHA-256: `26a8ac4d1039917323e75a294775dd14a2b563adb12a5d2fcdb47ce8f15c992e`
- interpretation audit SHA-256: `620827f83fb566ff6ceae1b66c8f51f61ef8e5bbdabbb1c4b5a48b5187a82413`

The primary and independent findings files are byte-identical.

## Frozen primary finding

All four recovery policies have the same trusted-recovery success count over their equally weighted 864 positions:

| Policy | Trusted recovery |
|---|---:|
| `P0_HARD_CUTOVER` | `635/864` |
| `P1_STAGED_CUTOVER` | `635/864` |
| `P2_HYBRID_OVERLAP` | `635/864` |
| `P3_CONTACT_AWARE_STAGED` | `635/864` |

The prespecified primary contrast is therefore:

```text
P3 - P1 = 0/1 = 0.000000 percentage points
```

This negative primary result is frozen. No hypothesis rescue is authorized.

The frozen profile-level result is also retained:

- `PROFILE_512_44`: `1080/1152`
- `PROFILE_768_65`: `748/1152`
- `PROFILE_1024_87`: `712/1152`
- across all 1,152 matched non-profile positions, success is non-increasing as the modeled standardized cryptographic-object budget increases.

## Inference and claim boundaries

Study 8 is the complete deterministic finite population defined by the frozen design. It is not treated as a probabilistic sample. The frozen analysis therefore does not use sampling p-values, sampling confidence intervals, bootstrap inference, or permutation inference.

All reported timing quantities are **logical slot indices** and all cryptographic burdens are **standardized object-byte budgets**. The study does not measure or claim:

- spacecraft or flight-system latency;
- real RF-link performance;
- ground-station or operator timing;
- onboard ML-KEM/ML-DSA CPU or energy cost;
- operational CCSDS/PQC implementation performance;
- flightworthiness, certification, or production suitability.

Same-repository independently written reproduction is not external laboratory or independent-human replication.

## Study structure

### Frozen design

- [`STUDY8_PROTOCOL.json`](STUDY8_PROTOCOL.json)
- [`PHASE8_0_AMENDMENT_1.json`](PHASE8_0_AMENDMENT_1.json)
- [`STUDY8_CONTACT_MODEL.md`](STUDY8_CONTACT_MODEL.md)
- [`STUDY8_CRYPTO_OBJECT_BUDGETS.json`](STUDY8_CRYPTO_OBJECT_BUDGETS.json)
- [`STUDY8_CLAIM_BOUNDARY.md`](STUDY8_CLAIM_BOUNDARY.md)
- [`STUDY8_LITERATURE_REGISTER.md`](STUDY8_LITERATURE_REGISTER.md)

### Implementation and independent model

- [`src/contact_recovery_model.py`](src/contact_recovery_model.py)
- [`audit/independent_reference.py`](audit/independent_reference.py)
- [`PRE_RUNTIME_HASH_BINDING.json`](PRE_RUNTIME_HASH_BINDING.json)

### Canonical campaign evidence

- [`results/S8-PQC-ICR-001/canonical_observations.csv`](results/S8-PQC-ICR-001/canonical_observations.csv)
- [`results/S8-PQC-ICR-001/independent_reproduction.csv`](results/S8-PQC-ICR-001/independent_reproduction.csv)
- [`results/S8-PQC-ICR-001/independent_audit_summary.json`](results/S8-PQC-ICR-001/independent_audit_summary.json)
- [`results/S8-PQC-ICR-001/provenance.json`](results/S8-PQC-ICR-001/provenance.json)

### Statistical analysis and freeze

- [`analysis/PHASE8_5_STATISTICAL_ANALYSIS_PLAN.json`](analysis/PHASE8_5_STATISTICAL_ANALYSIS_PLAN.json)
- [`analysis/src/analyze_phase8.py`](analysis/src/analyze_phase8.py)
- [`analysis/audit/independent_statistical_reproduction.py`](analysis/audit/independent_statistical_reproduction.py)
- [`analysis/results/primary_findings.json`](analysis/results/primary_findings.json)
- [`analysis/results/independent_findings.json`](analysis/results/independent_findings.json)
- [`analysis/results/findings_audit.json`](analysis/results/findings_audit.json)
- [`analysis/results/interpretation_audit.json`](analysis/results/interpretation_audit.json)
- [`analysis/RESULTS_FREEZE_MANIFEST.json`](analysis/RESULTS_FREEZE_MANIFEST.json)

## Safe validation

Normal repository validation must not rerun the canonical campaign or rewrite statistical outputs. Use:

```bash
python scripts/audit_repository_release_gate.py
python study8/scripts/check_phase8_hash_binding.py
python study8/analysis/scripts/check_phase8_6_results_freeze.py
python study8/scripts/check_study8_technical_close.py
python publication/study8/scripts/check_publication_freeze.py
```

The historical campaign/analysis/freeze executors remain provenance. Their presence does not authorize re-execution.

## Next gate

Study 8 is now submitted and should remain frozen while Acta Astronautica editorial and peer review proceeds. Do not modify the submitted manuscript, publisher-facing files, canonical campaign, statistics, or frozen claim boundary unless the journal explicitly requests a revision.

For new publication development, proceed to the next unsent publication unit in [`../docs/PUBLICATION_PHASE_MAP.md`](../docs/PUBLICATION_PHASE_MAP.md), currently the Studies 3 + 4 + 6 synthesis.
