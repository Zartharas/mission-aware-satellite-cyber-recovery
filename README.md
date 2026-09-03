<div align="center">

# Mission-Aware Satellite Cyber Response and Trusted Recovery

**Reproducible software-in-the-loop journal research on cyber response and trusted recovery under mission, contact, evidence, and bounded-compromise constraints.**

[![Study 1 Zenodo DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22181540.svg)](https://doi.org/10.5281/zenodo.22181540)
[![ORCID](https://img.shields.io/badge/ORCID-0009--0008--9752--3743-A6CE39?logo=orcid&logoColor=white)](https://orcid.org/0009-0008-9752-3743)
[![Research data](https://img.shields.io/badge/data-CC%20BY%204.0-blue)](LICENSE)
[![Code](https://img.shields.io/badge/code-MIT-green)](LICENSE)

[Study 1 dataset](https://doi.org/10.5281/zenodo.22181540) · [Manuscript](publication/README.md) · [Study 2](study2/README.md) · [Study 8](study8/README.md) · [Reproduce](docs/REPRODUCIBILITY_GUIDE.md) · [Security](SECURITY.md) · [Citation](CITATION.cff)

</div>

![Repository research workflow](docs/assets/repository-overview.svg)

## Research at a glance

This repository contains **two separately frozen empirical studies supporting the current journal article** plus a **separately frozen deterministic modeled companion study (Study 8)**. Their observations are never pooled into one statistical population.

| Item | Study 1 | Study 2 |
|---|---|---|
| Research role | Baseline comparative response/recovery study | Adversarial evidence-aware generalization study |
| Frozen design | 24 cells × 30 valid repetitions | 85 prespecified cells |
| Statistical population | **720 VALID observations** | **3,872 VALID observations** |
| Invalid-attempt handling | 9 retained INVALID attempts; one additional quarantined never-ledgered interruption | **0 INVALID attempts** |
| Main factors | cyber event, mission state, evidence condition, modeled contact | evidence mechanisms, adversary budget, contact regime, ambiguity controls, context ablations |
| Time basis | frozen 30-s Study-1 analysis horizon where applicable | deterministic logical SIL time; 240-logical-second RMST restriction |
| Public/source evidence | Zenodo v1.0.0, DOI `10.5281/zenodo.22181540` | Phase-6 evidence passed responsible-release review; DOI publication/checksum verification remain pre-submission gates |
| Statistical results | frozen WP10 record and reconstructed regression-tested reproduction package | canonical Phase-7 freeze with independent reproduction, **0 mismatches** |

### Study 8 — separately frozen companion study

Study 8 is a **separate companion study** and is not a third population in the existing Study-1/Study-2 journal article.

Study 8 (`S8-PQC-ICR-001`) evaluates trusted post-compromise recovery under finite logical contact budgets while varying cryptographic-transition policy, standardized ML-KEM/ML-DSA object-byte burden, contact regime, bounded modeled disruption, compromise-phase offset, and logical deadline.

- frozen factorial population: **3,456 modeled observations**;
- independent implementation-level reproduction: **3,456/3,456 exact row matches, 0 mismatches**;
- all four policies: `635/864` trusted-recovery success;
- prespecified primary contrast `P3 - P1`: `0/1` (`0.000000` percentage points);
- canonical observations SHA-256: `cfc65b6663be4e9f17a00ed102730f8642efcbbd844045acce032ff09a0bcabf`;
- primary/independent findings SHA-256: `26a8ac4d1039917323e75a294775dd14a2b563adb12a5d2fcdb47ce8f15c992e`;
- technical close: PR `#89`, `main` commit `63106778559c3127a7d6e8765d52939b73a3f35b`, post-merge CI run `33761681328` `SUCCESS`.

Study 8 is a **deterministic finite modeled study**, not an empirical spacecraft/RF performance experiment. Its publication integration has not started and must remain separate from the existing Study-1/Study-2 journal manuscript unless a later gate explicitly authorizes integration.

**Current repository state:** Study-1 science is frozen. Study-2 Phase 7 is `PRESPECIFIED_ANALYSIS_RESULTS_FROZEN_CANONICAL`; the two-study journal-manuscript integration is complete, while durable Study-2 DOI archiving/public checksum verification remain pre-submission work for that article. Study 8 is now `TECHNICALLY_CLOSED_PUBLICATION_INTEGRATION_NOT_STARTED` after exact-head results-freeze merge and successful post-merge validation. No new Study-1, Study-2, or Study-8 scientific execution is authorized by this current-state documentation.

Study-2 canonical result/provenance records:

- [`study2/docs/PHASE7_RESULTS_FREEZE.md`](study2/docs/PHASE7_RESULTS_FREEZE.md)
- [`study2/PHASE7_RESULTS_FREEZE.json`](study2/PHASE7_RESULTS_FREEZE.json)
- [`study2/PHASE7_PROVENANCE.json`](study2/PHASE7_PROVENANCE.json)
- [`study2/evidence/phase7/`](study2/evidence/phase7/)
- [`study2/release/phase6/`](study2/release/phase6/) — responsible-release review and DOI-deposit metadata

Study-8 current-state/freeze records:

- [`study8/README.md`](study8/README.md)
- [`study8/STUDY8_TECHNICAL_CLOSE.json`](study8/STUDY8_TECHNICAL_CLOSE.json)
- [`study8/docs/PHASE8_7_TECHNICAL_CLOSE.md`](study8/docs/PHASE8_7_TECHNICAL_CLOSE.md)
- [`study8/analysis/RESULTS_FREEZE_MANIFEST.json`](study8/analysis/RESULTS_FREEZE_MANIFEST.json)
- [`study8/results/S8-PQC-ICR-001/independent_audit_summary.json`](study8/results/S8-PQC-ICR-001/independent_audit_summary.json)

The Study-2 analysis covers 162 primary paired contrasts and 432 prespecified secondary contrasts. The exact Phase-7 results ZIP is durably retained in repository history at `study2/evidence/phase7/archive/`. The underlying 3,872-observation Phase-6 evidence remains a separately governed source artifact. Its responsible-release review is complete; the exact approved ZIP still requires a durable DOI-bearing public archive and post-publication checksum verification before the existing journal submission.

## Scientific interpretation boundaries

The repository intentionally preserves negative and conditional findings rather than promoting universal policy winners.

- Study 1 remains exactly 720 VALID observations; the 696-observation final-commit analysis remains sensitivity only.
- Study 2 remains exactly 3,872 VALID observations across 85 cells; it is not appended to or pooled with Study 1.
- Study-2 Block-C BENIGN/ADVERSARIAL contrasts are a **structural label-invariance control**, not empirical evidence about discrimination between genuinely different benign and adversarial causes.
- K4 is a separate intermittent/flapping-contact profile, not ordinal severity 4.
- A2/K2 is a coupled producer-compromise/contact-loss profile, not an unconfounded adversary-only effect.
- Logical SIL seconds are model time, not spacecraft, network, ground-station, or operator wall-clock latency.
- No weighted global policy score or global policy rank is supported.
- The evaluated selectors are deterministic rule-based mechanisms, not AI/ML scientific methods.
- Study 8 contains exactly 3,456 deterministic modeled positions; it is not a probabilistic sample and supports no sampling p-values or sampling confidence intervals.
- Study-8 `P3 - P1` trusted-recovery success is exactly zero in the frozen population; no policy-success superiority claim is supported.
- Study-8 logical slots and standardized cryptographic-object bytes are modeling quantities, not measured spacecraft/RF/PQC execution latency, CPU, energy, or flight performance.
- The work makes no operational spacecraft, real-RF, flightworthiness, or certification claim.

## Evidence and archive status

### Study 1

The exact public Study-1 research-data/reproducibility package is archived on Zenodo:

> **Singh, A. (2026). _Mission-Aware Satellite Cyber Response and Trusted Recovery Under Contact and Evidence Constraints — Research Data and Reproducibility Artifacts_ (Version 1.0.0) [Dataset]. Zenodo.**  
> <https://doi.org/10.5281/zenodo.22181540>

Version DOI: `10.5281/zenodo.22181540`  
Concept DOI: `10.5281/zenodo.22181539`

This DOI-bearing release is the **Study-1 evidence-of-record**. It must not be described as containing Study-2 or Study-8 source observations.

### Study 2

The Study-2 source campaign is identified by immutable hashes, including:

- Phase-6 artifact ZIP SHA-256: `195860bd44b38ccf170f02cb1cb392583217296d08640c99b18b52286403e133`
- observations SHA-256: `8dcc850c561d7e3c0bf7478263b534cae83cbbb55183c313e879dd7d61127854`
- attempt-ledger SHA-256: `755d6541263ac31589934200ea5071cdbcacae1ea197d044bbd3e6f7f7d1dbc5`
- trial-manifest SHA-256: `190612473717b7768ceccb4596a20d90cd7d532bf7581330ce94d609cb752e67`
- Phase-7 result ZIP SHA-256: `0136123a53d150437fefc8ace342af63b11d980cf8cab32ef7a4f03b78267417`

The exact Phase-6 source ZIP has passed responsible-release review with decision `APPROVED_FOR_PUBLIC_DURABLE_ARCHIVE_WITH_PROVENANCE_WRAPPER`; the review record and deposit metadata are retained under [`study2/release/phase6/`](study2/release/phase6/). No source-evidence record was changed by that review.

A DOI for the Study-2 source-evidence package is **not yet claimed here**. The remaining archive gate is to publish the exact approved ZIP to a new durable DOI-bearing Study-2 dataset record, verify the publicly served ZIP checksum, and then insert the actual DOI/archive identity into the journal package. The Study-1 DOI must not be reused for Study 2.

### Study 8

Study-8 canonical and statistical evidence is retained directly in Git with a frozen SHA-256 manifest:

- canonical observations SHA-256: `cfc65b6663be4e9f17a00ed102730f8642efcbbd844045acce032ff09a0bcabf`
- primary findings SHA-256: `26a8ac4d1039917323e75a294775dd14a2b563adb12a5d2fcdb47ce8f15c992e`
- independent findings SHA-256: `26a8ac4d1039917323e75a294775dd14a2b563adb12a5d2fcdb47ce8f15c992e`
- interpretation audit SHA-256: `620827f83fb566ff6ceae1b66c8f51f61ef8e5bbdabbb1c4b5a48b5187a82413`

The authoritative freeze is [`study8/analysis/RESULTS_FREEZE_MANIFEST.json`](study8/analysis/RESULTS_FREEZE_MANIFEST.json). No Study-8 DOI or publication release is claimed before a separate publication/release gate actually creates one.

## Publication package

Use [`publication/README.md`](publication/README.md) as the current **Study-1/Study-2 journal article** index. The authoritative journal source is componentized so those two frozen studies remain distinguishable:

- Study-1 Methods: `publication/manuscript/03-methods.md`
- Study-2 Methods extension: `publication/manuscript/03-study2-methods-extension.md`
- Study-1 Results: `publication/manuscript/04-results.md`
- Study-2 Results extension: `publication/manuscript/04-study2-results-extension.md`
- Cross-study Discussion: `publication/manuscript/05-discussion.md`
- Combined bounded Conclusion: `publication/manuscript/06-conclusion.md`

**Study 8 is not yet integrated into `publication/`.** Its future companion-paper package must be created under a separate publication gate from the frozen `study8/` evidence, without altering the existing two-study article or the frozen Study-8 science.

Historical Study-1 figures and tables remain frozen publication artifacts. Study-2 publication tables and claim traceability are maintained separately so later editing cannot silently rewrite Study-1 evidence.

## Repository map — recommended reading order

| Order | Location | Purpose |
|---:|---|---|
| 1 | [`publication/`](publication/README.md) | Current Study-1/Study-2 journal manuscript, displays, submission controls, and claim traceability |
| 2 | [`study2/`](study2/README.md) | Study-2 protocol, campaign, Phase-7 freeze, provenance, independent audit, and Phase-6 responsible-release record |
| 3 | [`study8/`](study8/README.md) | Study-8 design, canonical 3,456-position evidence, independent reproduction, statistical freeze, and technical close |
| 4 | [`analysis/`](analysis/README.md) | Study-1 WP10 statistical reconstruction validated against preserved reference outputs |
| 5 | [`docs/`](docs/) | Theory, methods, legal/ethical boundaries, historical work-package evidence, and release closeouts |
| 6 | [`configs/`](configs/) | Frozen Study-1 experiment designs, schemas, adapters, and toolchain locks |
| 7 | [`src/mission_recovery/`](src/mission_recovery/) | Study-1 research implementation and policy/runtime logic |
| 8 | [`tests/`](tests/) | Unit, contract, regression, and campaign-governance tests |
| 9 | [`scripts/`](scripts/) | Validation, testbed, runtime, campaign, and release tooling |
| 10 | [`tracker/`](tracker/) | Current research state plus historical work-package decisions |
| 11 | [`release/`](release/) | Study-1 responsible-release controls and Zenodo publication record |

Historical files intentionally retain stage-local wording when that wording is part of provenance. Current state is governed by this README, `tracker/RESEARCH_TRACKER.md`, `study2/PHASE7_PROVENANCE.json`, `study8/STUDY8_TECHNICAL_CLOSE.json`, and `publication/manuscript/MANUSCRIPT-ASSEMBLY.md` for the existing two-study article.

## Quick start: safe repository validation

The default validation path does **not** start NOS3, Docker campaign runtime, event injection, or the historical Study-8 canonical campaign:

```bash
git clone https://github.com/Zartharas/mission-aware-satellite-cyber-recovery.git
cd mission-aware-satellite-cyber-recovery

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt

python scripts/audit_repository_release_gate.py
python scripts/audit_bibliography_metadata.py
python scripts/validate_experiment_schema.py
python -m unittest discover -s tests -p 'test_*.py'
python study8/scripts/check_phase8_hash_binding.py
python study8/analysis/scripts/check_phase8_6_results_freeze.py
python study8/scripts/check_study8_technical_close.py
```

For Study-1 statistical reproduction, Study-2 result verification, and the frozen Study-8 verification boundary, see [`docs/REPRODUCIBILITY_GUIDE.md`](docs/REPRODUCIBILITY_GUIDE.md).

## Safety and scope

This repository is for controlled defensive research. The reported work:

- used researcher-controlled software simulation/modeling;
- did not access operational spacecraft or ground stations;
- did not use operational or stolen credentials;
- did not transmit, jam, spoof, or interfere with RF;
- did not use classified or proprietary mission telemetry;
- does not demonstrate flight certification or production autonomous recovery.

See [`SECURITY.md`](SECURITY.md), [`docs/05-legal-ethical-boundaries.md`](docs/05-legal-ethical-boundaries.md), and [`docs/13-laboratory-rules-of-engagement.md`](docs/13-laboratory-rules-of-engagement.md).

## Citation

`CITATION.cff` and Zenodo v1.0.0 currently identify the published **Study-1** evidence release. The Study-2 responsible-release review is complete, but a Study-2 DOI must be added only after the approved source package is actually published and its public checksum is verified. Study 8 has no DOI/publication identity yet; one must not be invented before a separate release/publication gate.

## Author

**Aman Singh** — Independent Researcher  
ORCID: <https://orcid.org/0009-0008-9752-3743>

This work was conducted independently and received no external funding.

## Licensing

This repository uses a split-license model; see [`LICENSE`](LICENSE) for the exact scope. Original code is MIT-licensed; original research documentation/data distributed by this project is CC BY 4.0 unless a file states otherwise. Third-party material remains under its own terms.

## Contributing and responsible disclosure

Contributions that improve reproducibility, documentation, validation, and defensive research quality are welcome. Read [`CONTRIBUTING.md`](CONTRIBUTING.md) before opening a pull request. Do not place credentials, proprietary telemetry, operational satellite details, or sensitive vulnerability information in a public issue. Follow [`SECURITY.md`](SECURITY.md) for responsible disclosure.
