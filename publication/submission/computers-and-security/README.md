# Computers & Security Submission Package

## Target

- **Journal:** Computers & Security (Elsevier)
- **Article type:** Full Length Article
- **Primary manuscript:** assembled from the authoritative components listed in `../../manuscript/MANUSCRIPT-ASSEMBLY.md`
- **Submission-preparation snapshot:** reproducibility-hardened `main` commit `99892bd9bb0828bdb3d0a28caf40dbc18fcbc4dc`, tree `f17cd12011cff510aa0c4ce128938b4bf93b0288`

This directory contains journal-specific submission material only. It does not replace the target-neutral manuscript components and must not become a second manually maintained copy of the full paper.

## Why this venue is a strong primary target

Computers & Security explicitly combines leading-edge security research with practical security guidance. The fit is strengthened by recent journal publications directly addressing space-sector attack-surface assessment and SatCom cybersecurity, satellite intrusion detection, and cyber-physical security testbeds.

Current fit references checked during submission preparation:

- Computers & Security journal description: https://shop.elsevier.com/journals/computers-and-security/0167-4048
- Space-organization attack-surface study, Computers & Security 164 (2026), 104848: https://doi.org/10.1016/j.cose.2026.104848
- SatCom user-segment cybersecurity study, Computers & Security 140 (2024), 103799: https://doi.org/10.1016/j.cose.2024.103799
- CANSat-IDS satellite intrusion-detection study, Computers & Security 146 (2024), 104033: https://doi.org/10.1016/j.cose.2024.104033
- SCASS open-source cyber-physical security testbed, Computers & Security 151 (2025), 104315: https://doi.org/10.1016/j.cose.2025.104315
- Intrusion-response systems for cyber-physical systems, Computers & Security 124 (2023), 102984: https://doi.org/10.1016/j.cose.2022.102984

These papers establish venue adjacency; they are not cited merely to manufacture journal fit and should enter the manuscript bibliography only when they substantively support a manuscript claim.

## Cybersecurity framing upgrade

The manuscript now includes journal-upgrade modules that make the cybersecurity contribution explicit without changing any frozen observations or historical statistical results:

- `../../manuscript/02a-cybersecurity-positioning-and-peer-comparison.md` — post-detection positioning, closest-work differentiation, SPARTA behavioral mapping, and NIST SP 800-61 Rev. 3 lifecycle mapping;
- `../../manuscript/03a-threat-trust-and-security-model.md` — post-access adversary model, defender knowledge, TB0–TB5 trust boundaries, and security/dependability properties;
- `../../manuscript/05a-cybersecurity-implications-and-next-study.md` — practical security implications and a separately scoped higher-bar follow-on research program;
- `../../tables/table-r5-cybersecurity-positioning.csv` — conservative closest-work comparison;
- `../../tables/table-r6-security-property-mapping.csv` — integrity, availability, safety, recoverability, evidence assurance, and explicit non-evaluated properties.

The additional bibliography is held in `../../../references/cybersecurity-upgrade.bib` and must be merged/deduplicated with the established bibliography during final export.

## Current publisher-policy checks

Policy snapshot checked in August 2026:

- Elsevier research highlights: 3–5 bullets, no more than 85 characters including spaces, submitted separately. https://www.elsevier.com/researcher/author/tools-and-resources/highlights
- Elsevier generative-AI journal policy: substantive manuscript-preparation use requires a separate declaration; research-process use, including AI-assisted code development, should be described in Methods. https://www.elsevier.com/about/policies-and-standards/generative-ai-policies-for-journals
- Elsevier prior-publication policy does not treat an academic thesis as prior publication. https://www.elsevier.com/connect/clarification-of-our-policy-on-prior-publication
- Elsevier CRediT guidance supports explicit contributor-role statements. https://www.elsevier.com/researcher/author/policies-and-guidelines/credit-author-statement

The live Computers & Security Guide for Authors and Editorial Manager fields must be rechecked immediately before final export and submission because portal requirements can change.

## Files

- `title-page.md` — author/correspondence metadata and CRediT draft
- `highlights.md` — five publisher-length-checked research highlights
- `concise-abstract-candidate.md` — shorter target-specific abstract candidate; the authoritative abstract remains in the manuscript until adopted
- `cover-letter.md` — target-specific editorial cover-letter draft
- `ai-declaration.md` — Elsevier disclosure draft plus Methods disclosure text for post-publication AI-assisted code reconstruction
- `submission-checklist.md` — resolved items, blockers, and final portal checks
- `venue-fit.md` — target rationale and backup-journal decision logic

## Scientific boundary

Every target-specific export must preserve the manuscript controls in `../../manuscript/MANUSCRIPT-ASSEMBLY.md`: 720 VALID primary observations, P1 null preservation, modeled-contact wording, evidence-qualified P3/P4 interpretation, no P4 correctness oracle, condition-specific P5 interpretation without a global rank or success-rate framing, the 696-observation final-commit analysis as sensitivity only, and no operational spacecraft/RF/flight-readiness claim.

The new SPARTA mappings are behavioral correspondences only, and the NIST SP 800-61 Rev. 3 mapping is lifecycle positioning rather than a compliance claim.
