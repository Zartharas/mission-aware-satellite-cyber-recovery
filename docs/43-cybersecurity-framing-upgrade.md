# Cybersecurity Framing Upgrade — Journal Readiness

## Status

`COMPLETE_INTEGRATED_JOURNAL_FRAMING_NO_SCIENTIFIC_DATA_CHANGE`

This work package strengthens the current manuscript as a cybersecurity paper without reopening the frozen experiment or altering any historical statistical result.

## Motivation

Venue review against Computers & Security, IEEE Transactions on Dependable and Secure Computing, ACM Transactions on Privacy and Security, IEEE Transactions on Aerospace and Electronic Systems, and AIAA Journal of Aerospace Information Systems identified a consistent gap: Study 1 is strong in experimental governance, mixed-result reporting, and reproducibility, but its cybersecurity contribution needed more explicit adversary assumptions, trust boundaries, security-property mapping, closest-work differentiation, and mainstream incident-response positioning.

The upgrade therefore changed **interpretive and methodological clarity**, not observations or proposition-level results.

## Integrated manuscript changes

The temporary drafting modules were integrated into the conventional manuscript and then removed to avoid duplicate prose drift:

- **Section 2 — Background and Related Work** now includes post-detection security positioning, conservative closest-work comparison, frozen SPARTA behavioral correspondence, NIST SP 800-61 Rev. 3 lifecycle positioning, and the bounded novelty statement.
- **Section 3 — Methods** now includes the post-access adversary model, adversary exclusions, defender-knowledge model, TB0–TB5 trust boundaries, security/dependability-property mappings, explicit non-evaluated properties, and the incident-response mapping.
- **Section 5 — Discussion** now includes practical security-dependency interpretation, the precise Study 1 evidence-treatment boundary, NIST transferability, limitations, and the separately scoped Study 2/Study 3 research program.

## Publication displays

- `publication/tables/table-r5-cybersecurity-positioning.csv`
- `publication/tables/table-r6-security-property-mapping.csv`

Table R5 uses conservative `Not primary focus` language for external studies rather than claiming that unreported dimensions are absent from every implementation detail. Table R6 explicitly separates evaluated security/dependability properties from confidentiality, RF security, and human/operator performance, which were not evaluated.

## Canonical bibliography

All cybersecurity-upgrade references have been merged and deduplicated into `references/references.bib`, including:

- NIST SP 800-61 Rev. 3;
- the SPARTA technique identifiers already frozen in `configs/wp5_event_catalog.json`;
- Computers & Security papers on CANSat-IDS, SatCom cybersecurity, space-organization attack-surface measurement, and SCASS.

The temporary split bibliography was removed after the canonical bibliography was updated.

## Framework-use boundaries

### SPARTA

The publication follows the event identifiers already frozen in Study 1:

- E1 → `IA-0007.02` Malicious Commanding via Valid GS;
- E2 → `EX-0001.01` Replay — Command Packets;
- E3 → `IA-0007.01` Compromise On-Orbit Update and `EX-0004` Compromise Boot Memory;
- E4 → `DE-0003.06` Telemetry Downlink Modes.

These are **behavioral/experimental correspondences**. The experiment does not claim to reproduce full SPARTA attack chains, real initial access, real credentials, RF delivery, compromised operators, or operational space assets.

### NIST SP 800-61 Rev. 3

The NIST mapping is a **lifecycle-positioning aid**, not a compliance claim. The experiment starts after modeled event establishment and does not evaluate detector accuracy, SOC triage, staffing, legal reporting, attribution, or organizational lessons learned.

### Evidence treatment

Study 1 T1 is implemented as omission/reduction of selected policy-visible evidence fields. The paper does not relabel Study 1 as an experiment in separately controlled staleness, contradiction, or forged/manipulated evidence. Those mechanisms are reserved for Study 2.

### AI/ML scope

P7 is a frozen deterministic rule-based selector. It is not a learned, generative-AI, or other ML response mechanism. AI-assisted manuscript and post-publication reproducibility-code preparation is addressed separately through publisher disclosure and does not change the experimental method.

## Scientific immutability verified by construction

The framing work did not intentionally change:

- 720 VALID primary observations;
- 24 frozen cells × 30 seeds;
- 9 retained INVALID attempts;
- P1 null interpretation;
- P2 modeled-contact interpretation;
- P3 narrower-mechanism null result;
- P4 no-correctness-oracle boundary;
- P5 condition-specific Pareto result and no global rank;
- 1/9/710 execution provenance;
- 696-observation final-C sensitivity interpretation;
- raw campaign evidence;
- Zenodo v1.0.0.

## Follow-on research separation

- `docs/44-study2-secure-response-generalization-design.md` is design-only and not runtime-authorized. It covers evidence failure mechanisms, contact regimes, fault/attack ambiguity, selector ablation, stronger baselines, and formal assurance.
- `docs/46-formal-assurance-traceability-candidate.md` ties candidate formal properties to the implemented Study 1 code and is preparation for future work, not a claim that Study 1 has already been formally verified.
- Study 3 engineering/HIL extensions remain separate from Study 1 and must use a new frozen design and provenance record.

## Closeout gates

Before PR merge, the final branch head must pass repository CI, the canonical bibliography and peer-comparison claims must be checked, and the final PR diff must remain outside frozen campaign/scientific-source paths. Those are repository-release gates, not reasons to reopen Study 1.
