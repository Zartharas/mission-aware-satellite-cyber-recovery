# Computers & Security Submission Package

## Target

- **Journal:** Computers & Security (Elsevier)
- **Article type:** Full Length Article
- **Primary manuscript:** assembled from the authoritative components listed in `../../manuscript/MANUSCRIPT-ASSEMBLY.md`
- **Reproducibility-hardened code/data reference:** `main` commit `99892bd9bb0828bdb3d0a28caf40dbc18fcbc4dc`, tree `f17cd12011cff510aa0c4ce128938b4bf93b0288`
- **Author-attestation gate:** PASS as of 2026-08-31
- **Current state:** final submission-export gate; remaining checks are submission-day live-policy/portal checks and final export audits

This directory contains journal-specific submission material only. It does not replace the target-neutral manuscript components and must not become a second manually maintained copy of the full paper.

## Why this venue is a strong primary target

Computers & Security combines leading-edge information-security research with practical security relevance. The fit is strengthened by recent journal publications addressing space-sector attack-surface assessment, SatCom cybersecurity, satellite intrusion detection, and cyber-physical security testbeds.

Current fit references checked during submission preparation:

- Computers & Security journal description: https://shop.elsevier.com/journals/computers-and-security/0167-4048
- Space-organization attack-surface study, Computers & Security 164 (2026), 104848: https://doi.org/10.1016/j.cose.2026.104848
- SatCom user-segment cybersecurity study, Computers & Security 140 (2024), 103799: https://doi.org/10.1016/j.cose.2024.103799
- CANSat-IDS satellite intrusion-detection study, Computers & Security 146 (2024), 104033: https://doi.org/10.1016/j.cose.2024.104033
- SCASS cyber-physical security testbed, Computers & Security 151 (2025), 104315: https://doi.org/10.1016/j.cose.2025.104315

These works establish venue adjacency. They are included in the manuscript only when they substantively support positioning or comparison claims, not merely to manufacture journal fit.

## Integrated cybersecurity framing

The journal-upgrade material is now integrated into the conventional manuscript rather than maintained as auxiliary prose:

- **Section 2** — post-detection positioning; close-work differentiation; frozen SPARTA behavioral correspondence; NIST SP 800-61 Rev. 3 lifecycle positioning;
- **Section 3** — post-access adversary model; defender-knowledge model; TB0–TB5 trust boundaries; security/dependability properties; deterministic P7 semantics;
- **Section 5** — practical response/recovery implications; Study 1 evidence-treatment boundary; limitations; separately scoped Study 2/Study 3 program;
- `../../tables/table-r5-cybersecurity-positioning.csv` — conservative closest-work comparison;
- `../../tables/table-r6-security-property-mapping.csv` — security/dependability property map.

All manuscript citations now resolve through the single canonical bibliography `../../../references/references.bib`.

## Current journal-scope checks

Policy/scope snapshot checked in August 2026:

- Computers & Security emphasizes leading-edge security research with practical security value and excludes cryptology as a principal component. https://shop.elsevier.com/journals/computers-and-security/0167-4048
- The journal currently states a moratorium on submissions in which AI/ML is a significant scientific component. **This study does not use AI/ML as its response method:** P7 is a frozen deterministic rule-based selector. AI-assisted manuscript/reproducibility preparation is separately disclosed under Elsevier's publication-ethics policy and is not the experimental decision mechanism.
- Elsevier research highlights: 3–5 bullets, no more than 85 characters including spaces, submitted separately. https://www.elsevier.com/researcher/author/tools-and-resources/highlights
- Elsevier generative-AI journal policy requires appropriate disclosure of substantive manuscript-preparation use and research-process code assistance. https://www.elsevier.com/about/policies-and-standards/generative-ai-policies-for-journals
- Elsevier's general prior-publication policy does not treat an academic thesis as prior publication.
- Elsevier CRediT guidance supports explicit contributor-role statements.

The live Computers & Security Guide for Authors, Aims & Scope, and Editorial Manager fields must be rechecked on the actual submission date because publisher requirements can change.

## Files

- `title-page.md` — finalized author/correspondence metadata, CRediT statement, and author attestations
- `highlights.md` — five publisher-length-checked research highlights
- `concise-abstract-candidate.md` — shorter target-specific abstract candidate; the authoritative abstract remains in the manuscript until adopted
- `cover-letter.md` — target-specific editorial cover-letter draft with author confirmations closed
- `ai-declaration.md` — author-approved Elsevier disclosure plus Methods disclosure text for post-publication AI-assisted code reconstruction
- `submission-checklist.md` — author-attestation gate PASS; remaining submission-day checks and final export audits
- `venue-fit.md` — target rationale and backup-journal decision logic

## Author-attestation closeout

On 2026-08-31 the author explicitly confirmed the five outstanding factual items: no competing financial or non-financial interests; no acknowledgments to add; approval of the final CRediT roles; approval of the generative-AI declaration; and confirmation that the manuscript is not simultaneously under consideration elsewhere.

An institutional IRB/HRPP identifier remains conditional on a specific submission-system requirement. None is invented or inferred. The concise abstract candidate remains an export choice rather than a factual declaration.

## Scientific boundary

Every target-specific export must preserve the controls in `../../manuscript/MANUSCRIPT-ASSEMBLY.md`, including 720 VALID primary observations; P1 null preservation; modeled-contact wording; T1 as omission/reduction of policy-visible evidence rather than a stale/contradictory/forged-evidence factorial; no P4 correctness oracle; P7 as deterministic rule-based rather than AI/ML; condition-specific P5 interpretation without a global rank or success-rate framing; the 696-observation final-commit analysis as sensitivity only; and no operational spacecraft/RF/flight-readiness claim.

SPARTA mappings are frozen behavioral/experimental correspondences only, and the NIST SP 800-61 Rev. 3 mapping is lifecycle positioning rather than a compliance claim.
