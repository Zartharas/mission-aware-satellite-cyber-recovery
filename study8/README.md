# Study 8 — Contact-Aware Cryptographic Agility and Trusted Recovery

**Experiment:** `S8-PQC-ICR-001`  
**Working title:** *Contact-Aware Cryptographic Agility for Trusted Post-Compromise Recovery in Intermittently Connected Space Systems*  
**Study type:** deterministic finite modeled contact/crypto-agility/recovery study  
**Technical status:** `TECHNICALLY_CLOSED_PUBLICATION_INTEGRATION_NOT_STARTED`

Study 8 is a separately frozen companion study in this repository. It is **not** part of the existing Study-1/Study-2 journal manuscript unless a later publication-integration gate explicitly authorizes that change.

## Current technical close

The exact Study-8 science was merged to `main` through PR `#89` as commit:

```text
63106778559c3127a7d6e8765d52939b73a3f35b
```

The required post-merge repository validation completed successfully:

```text
workflow: Validate research configurations
run:      33761681328
attempt:  1
result:   SUCCESS
```

Authoritative closeout records:

- [`STUDY8_TECHNICAL_CLOSE.json`](STUDY8_TECHNICAL_CLOSE.json)
- [`docs/PHASE8_7_TECHNICAL_CLOSE.md`](docs/PHASE8_7_TECHNICAL_CLOSE.md)
- [`analysis/RESULTS_FREEZE_MANIFEST.json`](analysis/RESULTS_FREEZE_MANIFEST.json)
- [`analysis/RESULTS_FREEZE_SHA256SUMS.txt`](analysis/RESULTS_FREEZE_SHA256SUMS.txt)
- [`results/S8-PQC-ICR-001/independent_audit_summary.json`](results/S8-PQC-ICR-001/independent_audit_summary.json)

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
python study8/scripts/check_phase8_hash_binding.py
python study8/analysis/scripts/check_phase8_6_results_freeze.py
python study8/scripts/check_study8_technical_close.py
```

The historical campaign/analysis runners remain provenance. Their presence does not authorize re-execution.

## Next gate

The next work is **publication integration only**: manuscript structure, tables/figures, literature positioning, venue selection, declarations/data availability, and submission packaging using the frozen Study-8 evidence above. New canonical execution or statistical re-execution is not authorized by this technical close.
