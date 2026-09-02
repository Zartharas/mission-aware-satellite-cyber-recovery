# Computers & Security Submission Package

## Target

- **Journal:** Computers & Security (Elsevier)
- **Article type:** Full Length Article
- **Primary manuscript:** assembled from `../../manuscript/MANUSCRIPT-ASSEMBLY.md`
- **Scientific structure:** two separately frozen empirical studies; no pooled statistical population
- **Author-attestation gate:** PASS as of 2026-08-31
- **Journal integration:** completed in PR #72 / `6f9a1a5d26287120278913d453b26c78f267870f`
- **Study-2 Phase-6 responsible-release review:** PASS — `APPROVED_FOR_PUBLIC_DURABLE_ARCHIVE_WITH_PROVENANCE_WRAPPER`
- **Current state:** **Study-2 durable DOI archive / public checksum verification / DOI insertion gate; final export validation follows**

This directory contains target-specific submission material only. It does not replace the target-neutral manuscript and must not become a second manually maintained copy of the paper.

## Current scientific package

### Study 1

- 720 VALID observations across 24 frozen cells
- 9 retained INVALID attempts outside statistical membership
- frozen WP10 results and 696-observation sensitivity analysis
- public Study-1 evidence-of-record: Zenodo v1.0.0, DOI `10.5281/zenodo.22181540`
- deterministic P7 rule-based selector; no AI/ML response model

### Study 2

- 3,872 VALID observations, 0 INVALID attempts, 85 cells
- 162 primary paired contrasts and 432 prespecified secondary contrasts
- canonical Phase-7 result freeze and provenance under `../../../study2/`
- independent reproduction: 0 mismatches
- durable Phase-7 result ZIP in Git history
- exact Phase-6 source-evidence ZIP passed responsible-release review; the remaining archive gate is DOI publication plus independent public-checksum verification
- responsible-release record and deposit metadata: `../../../study2/release/phase6/`

The Study-1 Zenodo DOI must never be described as containing Study-2 source observations.

## Why this venue remains a strong primary target

Computers & Security combines leading-edge information-security research with practical security relevance. The paper centers on a concrete post-detection security problem: how response/recovery policies behave when authorization/contact is constrained and policy-visible evidence can be incomplete, stale, contradictory, manipulated, or compromised.

The satellite setting is substantive rather than decorative because command authority, intermittent contact, mission continuity, and trusted-state evidence interact directly with response/recovery behavior. At the same time, the research question remains legible to broader cyber-resilience and cyber-physical-systems readers.

Venue-adjacent Computers & Security work already cited in the manuscript includes space-sector attack-surface assessment, SatCom cybersecurity, satellite intrusion detection, cyber-physical security testbeds, and intrusion-response research. These publications establish venue adjacency; they are not used to imply that prior work lacks every dimension evaluated here.

## Current journal-scope and policy checks

Policy/scope snapshot rechecked on **2026-09-01**:

- Computers & Security continues to emphasize practical information-security research and excludes cryptology as a principal component.
- The current journal page still displays the AI/ML moratorium language for submissions in which AI/ML is a significant scientific component. Neither Study 1 nor Study 2 uses AI/ML as the response mechanism; the evaluated selectors are frozen deterministic rule-based policies.
- AI-assisted manuscript preparation and reproducibility/code-review work are publication-process disclosures, not scientific response mechanisms.
- Elsevier's current generative-AI journal policy requires substantive manuscript-preparation use to be disclosed and research-process/code assistance to be described in the appropriate Methods context. The repository retains a separate author-approved disclosure.
- General Elsevier highlights guidance uses 3–5 bullets with a maximum of 85 characters each; the current five highlights satisfy that constraint.

The live Computers & Security Guide for Authors, Aims & Scope, and Editorial Manager fields remain authoritative on the actual submission date.

## Integrated journal framing

The manuscript now uses a two-study structure:

- **Section 3 / Study 1:** original frozen post-access adversary model, defender-knowledge model, TB0–TB5 boundaries, design, P1–P5 methods, provenance, and reproducibility.
- **Study-2 Methods extension:** adversary classes A0–A3, evidence V0–V5, contact K0–K4, ambiguity controls, context ablations, frozen logical-time/RMST analysis, and independent audit boundary.
- **Section 4 / Study 1:** frozen P1–P5 results.
- **Study-2 Results extension:** frozen RQ1–RQ5 results.
- **Section 5:** cross-study cybersecurity interpretation and limitations.

Study-2 RQ3 is explicitly bounded as a **structural label-invariance/control result**. The BENIGN/ADVERSARIAL label does not alter hidden truth or generated policy-visible evidence within the frozen ambiguity families, so the 54 zero contrasts do not demonstrate empirical discrimination or non-discrimination between genuinely different causal mechanisms.

## Files

- `title-page.md` — author/correspondence metadata and CRediT statement
- `highlights.md` — five two-study, publisher-length-checked research highlights
- `concise-abstract-candidate.md` — target-specific two-study abstract candidate
- `cover-letter.md` — target-specific editorial cover letter
- `ai-declaration.md` — author-approved generative-AI/reproducibility disclosure
- `submission-checklist.md` — current archive, live-policy, and export gates
- `venue-fit.md` — updated target and backup-journal decision logic

## Scientific boundary

Every target-specific export must preserve the controls in `../../manuscript/MANUSCRIPT-ASSEMBLY.md`. In particular:

- Study 1 remains exactly 720 VALID observations.
- Study 2 remains exactly 3,872 VALID observations and is not pooled with Study 1.
- Study-1 P1 null and P3/P4/P5 boundaries remain unchanged.
- Study-2 V5 evidence qualification must not be equated with objective correctness.
- Study-2 RQ3 remains structural label-invariance only.
- K4 is not ordinal severity 4.
- A2/K2 is contact-coupled.
- secondary Study-2 n=32 blocks remain sensitivity/estimation evidence.
- no weighted global score, global policy rank, operational spacecraft/RF/real-link-latency, flightworthiness, or certification claim is supported.

## Gate to actual submission

The package is **not yet final-export ready**. The two-study journal integration, target-package reconciliation, local canonical audit, and Study-2 Phase-6 responsible-release review are complete. Before submission:

1. publish the exact approved Study-2 source-evidence ZIP to a new durable DOI-bearing archive;
2. independently verify the publicly served source ZIP SHA-256 and insert the actual Study-2 DOI/archive identity into Data Availability and submission materials;
3. recheck live Computers & Security scope, AI/ML wording, generative-AI policy, article type, portal fields, and file requirements;
4. run exact-export citation/DOI/frozen-claim/scope audits.

No missing DOI, portal field, or formatting preference may be resolved by inventing scientific or institutional information.
