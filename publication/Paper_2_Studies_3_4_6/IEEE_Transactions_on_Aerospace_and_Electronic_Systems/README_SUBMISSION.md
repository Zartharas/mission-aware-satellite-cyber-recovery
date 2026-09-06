# Paper 2 (Studies 3, 4, and 6) - TAES Development and Submission Package

**Target venue:** IEEE Transactions on Aerospace and Electronic Systems (TAES)  
**Manuscript type:** Regular Paper  
**Primary Technical Area:** Aerospace Information Systems  
**Development status:** `VENUE_LOCKED__COMPONENT_COMPLETE_MANUSCRIPT_DRAFT__NOT_SUBMISSION_READY`  
**Venue lock date:** 2026-09-06  
**Submission status:** `NOT_SUBMITTED`

## Canonical package rule

This directory is the single canonical venue-specific development and future publisher-facing package for Paper 2. Paper 2 uses Studies 3, 4, and 6 only. Their frozen populations remain separate and must never be pooled into one statistical population.

All TAES development files, final manuscript files, supplementary files if any, checksums, portal records, and later submission-confirmation records must remain in this directory. Do not maintain a Downloads mirror, desktop copy, separate `PORTAL_UPLOAD` staging directory, or any other independently edited source of truth.

The local Git clone under the repository root is the working copy. Use `TAES_LOCAL_SYNC.sh` only to fast-forward the repository and verify this canonical directory in place. When final publisher-facing files are frozen, upload them directly from this directory.

No scientific rerun, enlargement, endpoint change, hidden correction, null-result removal, or post-hoc integrated experiment is authorized for venue fit.

## Core scientific populations

- Study 3 / `S3-K4E-001`: 1,380 deterministic trajectories.
- Study 4 / `S4-MPQ-001`: 4,608 exact rule-by-subset observations.
- Study 6 / `S6-SCTR-001`: 420 exact artifact-state and assurance-unavailability observations.
- Study 5 is deferred from the Paper-2 core and must not be presented as external validation of Studies 3, 4, or 6.
- There is no scientifically meaningful pooled Paper-2 `N = 6,408`.

## Working scientific identity

**Layered residual trust boundaries in satellite cyber-recovery qualification.**

Working title:

**Residual Trust Boundaries in Satellite Cyber Recovery: Temporal Evidence, Producer Quorums, and Artifact Assurance**

The three independently frozen layers are:

1. temporal evidence qualification under Study 3;
2. multi-producer quorum and synthetic provenance-domain qualification under Study 4;
3. recovery-artifact assurance qualification under Study 6.

The manuscript may synthesize these studies conceptually, but it must never claim that they constitute one integrated experiment or one jointly evaluated architecture.

## Current manuscript component set

The manuscript is component-complete at the development-draft level. It is not yet submission ready.

- `TAES_ABSTRACT_KEYWORDS.md`: abstract and index-term draft.
- `TAES_SECTION_I_INTRODUCTION.md`: Section I, Introduction.
- `TAES_MANUSCRIPT_SOURCE.md`: Section II, Related Work and Scientific Positioning, and Section III, Common Trust-Qualification Framework and Study Separation.
- `TAES_SECTION_IV_STUDY3.md`: Section IV, Temporal Evidence Qualification Under Intermittent Contact.
- `TAES_SECTION_V_STUDY4.md`: Section V, Multi-Producer Qualification and Provenance-Domain Constraints.
- `TAES_SECTION_VI_STUDY6.md`: Section VI, Recovery-Artifact Assurance and Residual Incorrect States.
- `TAES_SECTION_VII_SYNTHESIS.md`: Section VII, Cross-Study Residual Trust Boundaries.
- `TAES_SECTION_VIII_VALIDITY.md`: Section VIII, Validity, Aerospace Interpretation Boundaries, and Future Evaluation.
- `TAES_SECTION_IX_CONCLUSION.md`: Section IX, Conclusion.
- `TAES_LITERATURE_SOURCE_LEDGER.md`: durable literature, prior-art, and novelty-control ledger.

The next manuscript gate is **single-source assembly plus line-by-line scientific and citation audit**. Component completion does not authorize formatting, package freeze, or portal submission.

## TAES venue basis

TAES publishes original work on the organization, design, development, integration, and operation of complex aerospace and electronic systems. The selected primary Technical Area is Aerospace Information Systems because the current TAES description expressly includes aerospace systems and software engineering, verification and validation, safety and mission assurance, information technology, embedded and real-time computing, and distributed computing.

Secondary topical adjacency exists with:

- Avionics Systems, including cyber-physical security of space systems;
- Space Systems, including spacecraft, ground segment, operations, applications, and services;
- Fault-Tolerant Systems, including recovery, fault containment, robustness, and Byzantine fault tolerance.

The manuscript should remain assigned to Aerospace Information Systems unless the final emphasis changes materially or the TAES Editor-in-Chief reassigns it.

## Development and submission-control files

- `TAES_AIMS_SCOPE_REQUIREMENTS.md`
- `TAES_COMPLIANCE_CHECKLIST.md`
- `TAES_PORTAL_FIELD_MAP.md`
- `TAES_MANUSCRIPT_DEVELOPMENT.md`
- `TAES_ORIGINALITY_AI_SUPPLEMENTARY_CONTROL.md`
- `TAES_PACKAGE_STATUS.json`
- `UPLOAD_FILES.md`
- `TAES_LOCAL_SYNC.sh`

Future publisher-facing files will be added directly to this same directory only after manuscript assembly and quality control. At minimum, the initial TAES submission requires a manuscript PDF in the prescribed two-column format. Any supplementary material intended to accompany the article must also be supplied for peer review during initial submission.

## Official sources reviewed on 2026-09-06

- TAES main journal page: https://ieee-aess.org/publications/taes
- TAES Information for Authors: https://ieee-aess.org/publications/transactions-aes/author-information
- TAES Technical Area Descriptions: https://ieee-aess.org/publications/transactions-aes/technical-areas-editors/descriptions
- TAES AI guidance: https://ieee-aess.org/using-ai-generated-content-ieee-article-and-its-review
- IEEE Author Center, article structure: https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/create-the-text-of-your-article/structure-your-article/
- IEEE Author Center, templates: https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/authoring-tools-and-templates/
- IEEE Author Center, supplementary material: https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/prepare-supplementary-materials/
- IEEE Author Center, ethics and submission policy: https://journals.ieeeauthorcenter.ieee.org/become-an-ieee-journal-author/publishing-ethics/guidelines-and-policies/submission-and-peer-review-policies/
- IEEE Author Center new-author publication guide: https://newauthors.ieeeauthorcenter.ieee.org/publication/

The IEEE Xplore Recent Issue URL supplied by the author is retained as a venue-monitoring reference, but automated access was blocked during the prior venue review. Do not infer current-issue content from that access failure.

## Remaining mandatory gates

Before a TAES manuscript PDF can be frozen:

1. assemble the manuscript components into one canonical manuscript source;
2. perform a line-by-line scientific claim audit against frozen Study 3, 4, and 6 records;
3. perform a citation and prior-art audit;
4. perform terminology and style QA, including the no-em-dash rule;
5. format in the required TAES two-column manuscript style;
6. perform page-by-page PDF visual QA;
7. finalize the supplementary-material decision;
8. recheck the live Atypon ReX portal and lock portal values;
9. generate SHA-256 identities for frozen upload files;
10. obtain explicit final author submission authorization.

Venue lock and manuscript drafting do not authorize portal submission.
