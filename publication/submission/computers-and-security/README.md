# Computers & Security Submission Package

## Target

- **Journal:** Computers & Security (Elsevier)
- **Article type:** Full Length Article
- **Primary manuscript:** assembled from `../../manuscript/MANUSCRIPT-ASSEMBLY.md`
- **Scientific structure:** two separately frozen empirical studies; no pooled statistical population
- **Author-attestation gate:** PASS as of 2026-08-31
- **Journal integration:** completed in PR #72 / `6f9a1a5d26287120278913d453b26c78f267870f`
- **Study-2 Phase-6 responsible-release review:** PASS — `APPROVED_FOR_PUBLIC_DURABLE_ARCHIVE_WITH_PROVENANCE_WRAPPER`
- **Study-2 public archive:** Zenodo v1.0.0 — version DOI `10.5281/zenodo.22289114`, concept DOI `10.5281/zenodo.22289113`, public ZIP SHA-256 verified
- **Publication Phase 1:** STARTED — first live-policy verification recorded 2026-09-04
- **Current state:** **live scope/policy pass completed with portal/export checks still pending before submission**

This directory contains target-specific submission material only. It does not replace the target-neutral manuscript and must not become a second manually maintained copy of the paper.

The current live-policy record is `LIVE_POLICY_VERIFICATION_2026-09-04.md`.

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
- exact Phase-6 source-evidence ZIP passed responsible-release review
- public source-evidence archive: Zenodo v1.0.0, version DOI `10.5281/zenodo.22289114`, concept DOI `10.5281/zenodo.22289113`
- public ZIP SHA-256 independently verified as `195860bd44b38ccf170f02cb1cb392583217296d08640c99b18b52286403e133`
- publication-verification authority: `../../../study2/release/phase6/ZENODO_PUBLICATION_VERIFICATION.json`

The Study-1 Zenodo DOI must never be described as containing Study-2 source observations.

## Why this venue remains a strong primary target

Computers & Security combines leading-edge information-security research with practical security relevance. The paper centers on a concrete post-detection security problem: how response/recovery policies behave when authorization/contact is constrained and policy-visible evidence can be incomplete, stale, contradictory, manipulated, or compromised.

The satellite setting is substantive rather than decorative because command authority, intermittent contact, mission continuity, and trusted-state evidence interact directly with response/recovery behavior. At the same time, the research question remains legible to broader cyber-resilience and cyber-physical-systems readers.

Venue-adjacent Computers & Security work already cited in the manuscript includes space-sector attack-surface assessment, SatCom cybersecurity, satellite intrusion detection, cyber-physical security testbeds, and intrusion-response research. These publications establish venue adjacency; they are not used to imply that prior work lacks every dimension evaluated here.

## Current journal-scope and policy checks

First Publication-Phase-1 live-policy pass completed on **2026-09-04** and recorded in `LIVE_POLICY_VERIFICATION_2026-09-04.md`:

- Computers & Security continues to emphasize practical information-security research and excludes cryptology when it is a principal component.
- The current journal page still displays the AI/ML moratorium language for submissions in which AI/ML is a significant scientific component. Neither Study 1 nor Study 2 uses AI/ML as the response mechanism; the evaluated selectors are frozen deterministic rule-based policies.
- Current 2026 Computers & Security articles continue to use the `Full Length Article` label; exact Editorial Manager article-type taxonomy remains a live-portal check.
- AI-assisted manuscript preparation and reproducibility/code-review work are publication-process/research-process disclosures, not scientific response mechanisms.
- Elsevier's current generative-AI journal policy requires substantive manuscript-preparation use to be disclosed and research-process/code assistance to be described in the appropriate methodology context. The repository retains an author-approved disclosure and Methods/reproducibility boundaries.
- Current Elsevier highlights guidance uses 3–5 bullets with a maximum of 85 characters each and generally places highlights at the final-files stage; the current five highlights satisfy the length constraint. Journal-specific portal behavior remains to be confirmed.
- Elsevier's general prior-publication policy does not treat an academic thesis/dissertation as prior publication. The ProQuest/dissertation relationship remains transparently disclosed, and any Computers & Security-specific exception still requires live-guide confirmation.
- Current Elsevier Your Paper Your Way guidance supports flexible initial formatting when essential manuscript elements are present. Exact Computers & Security guide/portal requirements remain authoritative for the final export.

The live Computers & Security Guide for Authors and Editorial Manager fields remain authoritative on the actual submission date. Exact portal metadata/file requirements have not been inferred or invented.

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
- `LIVE_POLICY_VERIFICATION_2026-09-04.md` — first Publication-Phase-1 live policy/scope verification record

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

The Study-2 archive blocker is now closed and Publication Phase 1 is active. The first live scope/policy pass is complete. The current gate is **exact journal-guide/portal confirmation plus exact final-export validation**.

Before actual submission:

1. confirm the exact current Computers & Security Guide-for-Authors requirements and live Editorial Manager fields/file behavior;
2. reconcile the exact article type, abstract choice/limit, highlights stage, data/code statements, competing-interest workflow, and any reviewer/IRB metadata fields without inventing information;
3. run exact-export citation/DOI/reference, frozen-claim, and scope-fit audits;
4. record the final submission repository snapshot only after those exact-export checks pass.

Actual publisher submission remains a separate explicit authorization gate.
