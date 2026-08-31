# Cybersecurity Framing Upgrade — Journal Readiness

## Status

`IN_PROGRESS_JOURNAL_FRAMING_ONLY_NO_SCIENTIFIC_DATA_CHANGE`

This work package strengthens the current manuscript as a cybersecurity paper without reopening the frozen experiment or altering any historical statistical result.

## Motivation

Venue review against Computers & Security, IEEE Transactions on Dependable and Secure Computing, ACM Transactions on Privacy and Security, IEEE Transactions on Aerospace and Electronic Systems, and AIAA Journal of Aerospace Information Systems identified a consistent gap: the current study is strong in experimental governance, mixed-result reporting, and reproducibility, but its cybersecurity contribution should be made more explicit through a formal adversary model, trust boundaries, security-property mapping, closest-work differentiation, and mainstream incident-response positioning.

The upgrade therefore focuses on **interpretive and methodological clarity**, not new observations.

## Added manuscript modules

- `publication/manuscript/02a-cybersecurity-positioning-and-peer-comparison.md`
  - post-detection security positioning;
  - conservative closest-work comparison;
  - SPARTA behavioral alignment;
  - NIST SP 800-61 Rev. 3 lifecycle positioning;
  - bounded novelty statement.

- `publication/manuscript/03a-threat-trust-and-security-model.md`
  - post-access adversary model;
  - adversary exclusions;
  - defender-knowledge model;
  - TB0–TB5 trust boundaries;
  - integrity, availability, safety, recoverability, and evidence-assurance mappings;
  - explicit non-evaluated security properties.

- `publication/manuscript/05a-cybersecurity-implications-and-next-study.md`
  - practical security-dependency interpretation;
  - evidence-plane attack-surface implications;
  - NIST incident-response transferability;
  - separately scoped Study 2/Study 3 research extensions.

## Added publication tables

- `publication/tables/table-r5-cybersecurity-positioning.csv`
- `publication/tables/table-r6-security-property-mapping.csv`

Table R5 uses conservative `Not primary focus` language for external studies rather than claiming that unreported dimensions are absent from every implementation detail.

## Added references

`references/cybersecurity-upgrade.bib` contains only references introduced by this framing work package, including:

- NIST SP 800-61 Rev. 3;
- SPARTA command-replay, update-compromise, telemetry/evidence-degradation, and general technique pages;
- Computers & Security papers on CANSat-IDS, SatCom cybersecurity, space-organization attack-surface measurement, and the SCASS cyber-physical testbed.

The established `references/references.bib` remains unchanged during this phase to minimize unintended reference drift. Final export must merge/deduplicate both bibliography sources.

## Framework-use boundaries

### SPARTA

SPARTA mappings are used as **behavioral correspondence/adjacency** only. The experiment does not claim to reproduce full SPARTA attack chains, real initial-access methods, real credentials, RF delivery, compromised operators, or operational space assets.

### NIST SP 800-61 Rev. 3

The NIST mapping is a **lifecycle-positioning aid**, not a compliance claim. The experiment starts after event establishment and does not evaluate detection accuracy, SOC triage, staffing, legal reporting, attribution, or post-incident organizational lessons learned.

## Scientific immutability

This framing upgrade must not change:

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

## Next gates

1. Complete current cybersecurity framing modules and citation audit.
2. Verify no new sentence changes the frozen proposition-level scientific meaning.
3. Re-run repository CI on the final branch head.
4. Perform journal-specific editorial integration into conventional section numbering.
5. Do **not** create new campaign observations as part of Study 1.
6. Develop Study 2 as a separately frozen research design before any new runtime execution.
