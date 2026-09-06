# TAES Aims, Scope, and Submission Requirements Review

**Review date:** 2026-09-06  
**Target:** IEEE Transactions on Aerospace and Electronic Systems (TAES)  
**Paper:** Paper 2, Studies 3 + 4 + 6  
**Current decision:** `FIT_CONFIRMED__REGULAR_PAPER__AEROSPACE_INFORMATION_SYSTEMS`

## 1. Journal aims and scope

TAES focuses on the organization, design, development, integration, and operation of complex systems for space, air, ocean, and ground environments. The journal explicitly includes spacecraft, command and control, avionics, telemetry, defense, transportation, intelligent and fault-tolerant systems, large-scale systems, and systems-of-systems.

TAES describes its purpose as publishing high-quality systems-related scientific findings that improve the foundations on which systems are conceived, designed, and physically realized. It expects a novel contribution with strong scientific underpinning, clear development, and good English.

### Paper-2 fit

Paper 2 is in scope when framed as an aerospace information-systems and trusted-recovery qualification study, not as a generic cybersecurity paper. The manuscript must keep the aerospace system application explicit in the research problem, system assumptions, implications, and limitations.

The strongest scope alignment is:

- satellite cyber recovery as the aerospace application;
- software and information-system trust qualification;
- verification and validation through exact finite modeled populations and independent audit;
- safety and mission-assurance relevance at the qualification boundary;
- distributed evidence composition and recovery-artifact assurance;
- constrained decision making under intermittent contact in Study 3.

The manuscript must not imply operational spacecraft validation, flight certification, RF performance, or measured mission availability.

## 2. Technical Area selection

### Primary: Aerospace Information Systems

The current TAES Technical Area description includes:

- aerospace systems and software engineering;
- requirements engineering, design, verification and validation, maintenance and evolution;
- model-based systems engineering and development;
- safety and mission assurance;
- formal methods;
- information technology;
- embedded and real-time computing;
- distributed and cloud computing;
- algorithms and artificial intelligence.

Paper 2 is best matched to this area because its central contribution is the modeling, verification, and residual-boundary analysis of software-visible trust evidence used to qualify satellite cyber recovery.

### Secondary adjacency

**Avionics Systems:** explicitly includes cyber-physical security of avionics, CNS/ATM, and space systems.

**Space Systems:** includes spacecraft, ground segment, missions, operations, applications, and services. This becomes a stronger choice only if the final manuscript emphasizes system/service architecture more than software/evidence qualification.

**Fault-Tolerant Systems:** includes roll-forward and roll-back recovery, fault containment, robustness, fault-tolerant design, Byzantine fault tolerance, and availability. It is relevant background but not the primary focus because Study 4 is not a Byzantine-consensus experiment and the paper does not estimate conventional reliability quantities.

## 3. Contribution type

**Required manuscript type for this project: Regular Paper.**

TAES defines Regular Papers as well-rounded treatments of a problem area. The title, abstract, and introduction should communicate the essence of the manuscript to the broadest possible audience and place the contribution in context with related work.

A Correspondence Item is not appropriate because Paper 2 contains three separately frozen studies and a cross-study synthesis rather than one or two concise points.

## 4. Initial submission format

TAES currently requires the initial Regular Paper manuscript as a PDF in a two-column, single-spaced format with:

- 10-point font;
- single line spacing;
- 1 inch / 25 mm top and bottom margins;
- 0.7 inch / 18 mm left and right margins;
- 3.45 inch / 88 mm column width;
- 0.2 inch / 5 mm space between columns.

The TAES site links an official LaTeX template and also permits use of IEEE Author Center templates. The final PDF must be produced from a controlled source file and visually reviewed before submission.

There is no formal manuscript page limit. However:

- unnecessarily long manuscripts may receive unfavorable reviews;
- accepted Regular Papers incur a mandatory overlength charge of USD 200 per printed page beyond 10 pages;
- the most accurate pre-submission page estimate is the TAES two-column version.

The development target should therefore be a technically complete manuscript near 10 printed pages when feasible, without deleting required scientific boundaries merely to avoid charges.

## 5. Abstract, title, and index terms

IEEE Author Center guidance requires the abstract to be:

- one paragraph;
- 150 to 250 words;
- self-contained;
- free of references, footnotes, undefined abbreviations, and mathematical equations;
- explicit about the research, conclusions, and implications.

IEEE recommends 3 to 5 keywords or phrases. TAES additionally recommends avoiding words such as "new" or "novel" in the title and abstract. Search-relevant technical terms should be used instead.

For Paper 2, do not place mathematical symbols or unexplained study IDs in the title or abstract.

## 6. Originality and prior work

TAES publishes only original material within its scope and does not allow concurrent multiple submission.

The manuscript must:

- cite any relevant previously published work by the author;
- clearly state how the current article differs from prior work when prior work forms a basis for the submission;
- disclose if a substantially similar manuscript was previously reviewed and rejected by another journal;
- provide prior editorial correspondence if the portal requests it for a previously rejected version.

Paper 1, Studies 1 + 2, is currently submitted to AIAA JAIS and is not prior published work. It must not be imported into Paper 2 as new evidence. Paper 2 uses Studies 3, 4, and 6 only and must preserve a clean scientific distinction from Paper 1.

## 7. Authorship and ORCID

TAES follows IEEE authorship requirements. Each author must have made a significant intellectual contribution, contributed to drafting or intellectual revision, and approve the final accepted version.

IEEE requires ORCID for all authors submitting to its journals. The sole-author working configuration for Paper 2 should retain the existing ORCID only after author identity details are reverified before portal submission.

## 8. Review model and prescreening

TAES uses single-anonymous peer review. At least two independent reviewers review published articles.

Before formal review, TAES performs three levels of prescreening:

1. Editor-in-Chief;
2. Senior Editor;
3. Associate Editor.

The prescreening risk for Paper 2 is not lack of data volume. It is whether the paper reads as a coherent aerospace systems contribution rather than three disconnected abstract models. The Introduction, common framework, and cross-study synthesis must therefore make the system-level scientific contribution explicit without claiming an integrated experiment.

## 9. Revisions

If TAES issues Major Revision or Minor Revision:

- submit a revised two-column manuscript;
- provide a separate Response to Reviewers file;
- respond point by point to every editor/reviewer issue;
- highlight or color all manuscript changes.

Major Revisions may be returned to one or more original reviewers. Minor Revisions may be handled by the Associate Editor.

## 10. Supplementary materials and reproducibility

TAES permits supplementary material including:

- multimedia;
- images;
- data sets;
- code;
- accompanying PDF documents.

TAES encourages authors to submit files necessary to recreate results. Any supplementary material intended to accompany the article must be submitted for peer review during the original article submission and referenced in the manuscript. A README should describe the material.

For Paper 2, the public repository is the primary reproducibility record. A frozen supplementary snapshot may be prepared later if it materially helps peer review, but it must not silently create a fourth statistical population or alter the frozen Study 3, 4, or 6 evidence.

## 11. AI-generated content

Current IEEE/AESS guidance permits AI-generated content but requires disclosure in the Acknowledgments section when AI generated article content. The disclosure must:

- identify the AI system used;
- identify the article sections in which AI-generated content was used;
- briefly explain the level of use.

Editing and grammar-only assistance is generally outside the mandatory scope but disclosure is recommended.

Because ChatGPT is being used materially for manuscript organization and drafting after the scientific results were frozen, the TAES manuscript should carry an explicit AI-use disclosure rather than relying on the editing-only exception.

## 12. Open access and fees

TAES is a hybrid journal. The current TAES journal page lists the IEEE hybrid open-access article processing charge as USD 2,800. This does not replace or waive overlength page charges.

Open access is not required for initial submission. The choice should be revisited if the paper is accepted because IEEE fees and institutional arrangements can change.

## 13. Final-production rules

After a manuscript is recommended for publication, TAES supplies instructions for the Final Submission Package. Differences between the accepted manuscript and final package must follow the accepting editor's instructions. Changes to title, authorship, or references after acceptance require explicit Editor-in-Chief approval and are described as extremely rare.

This means title, author list, references, figures, tables, data availability, and AI disclosure should be stabilized before final acceptance whenever possible.

## 14. Official sources

Reviewed on 2026-09-06:

- https://ieee-aess.org/publications/taes
- https://ieee-aess.org/publications/transactions-aes/author-information
- https://ieee-aess.org/publications/transactions-aes/technical-areas-editors/descriptions
- https://ieee-aess.org/using-ai-generated-content-ieee-article-and-its-review
- https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/create-the-text-of-your-article/structure-your-article/
- https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/authoring-tools-and-templates/
- https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/prepare-supplementary-materials/
- https://journals.ieeeauthorcenter.ieee.org/become-an-ieee-journal-author/publishing-ethics/ethical-requirements/
- https://journals.ieeeauthorcenter.ieee.org/become-an-ieee-journal-author/publishing-ethics/guidelines-and-policies/submission-and-peer-review-policies/
- https://journals.ieeeauthorcenter.ieee.org/submit-your-article-for-peer-review/checklist-for-submitting-your-article-for-peer-review/
- https://newauthors.ieeeauthorcenter.ieee.org/publication/

The IEEE Xplore current-issue page provided by the author was not machine-accessible during this audit. Current issue content should be checked manually in the browser before final submission if we want a last-minute topical/terminology comparison.
