# Live JAIS/AIAA Requirements Verification — 2026-09-04

This file records the current public AIAA requirements used to construct the Paper-1 JAIS Phase-1 package. It deliberately separates publicly verified requirements from ScholarOne-only fields that remain pending.

## 1. JAIS scope

**Official source:** AIAA, *Journal Scopes and Content*  
https://www.aiaa.org/publications/journals/Journal-Scopes-and-Content/

Current JAIS scope describes original archival research addressing aerospace-specific issues in aerospace computing, information, networks and communication systems. Relevant listed topics include aerospace systems and software engineering, verification and validation of embedded systems, autonomous systems, systems engineering, and safety and mission assurance.

**Paper-1 implication:** scope fit is credible when the manuscript is positioned as satellite cyber response/trusted recovery under aerospace-specific contact, authorization, mission-continuity, evidence, and software-recovery constraints.

## 2. Minimum manuscript presentation and abstract

**Official source:** AIAA, *Journal Author*  
https://www.aiaa.org/publications/journals/Journal-Author/

Current minimum journal-manuscript guidance states that manuscripts are in English using American spelling, 10-point type, double-spaced, and single-column. Full-length papers require a summary-type abstract of 100–200 words in one paragraph without numerical references, acronyms, or abbreviations.

**Paper-1 implication:** a separate JAIS abstract candidate is required; the existing 250-word Computers & Security abstract cannot be used unchanged.

## 3. Abstract detail

**Official source:** AIAA, *Preparation of an Abstract and Biography*  
https://www.aiaa.org/publications/journals/Journal-Author/Preparation-of-an-Abstract-and-Biography/

Current guidance requires a one-paragraph abstract between 100 and 200 words and recommends that it identify newly observed facts, conclusions, and methods/results as space permits.

**Paper-1 implication:** `jais-abstract.md` is maintained as a 189-word one-paragraph target-specific candidate.

## 4. Regular/Full Article length guideline

**Official source:** AIAA, *Journal Page Limits and Word Count Guidelines*  
https://www.aiaa.org/wp-content/uploads/2024/12/journalpagelimitsandwordcountguidelines_Sept_2024.pdf

Current published guideline for Regular/Full Articles is approximately 7–10 published pages or 10,000–12,000 words, with equivalent space from figures and tables counted. A standard single-column figure/table is approximately 200 equivalent words, a standard two-column figure/table approximately 450 words, and a large two-column table approximately 700 words. Editors retain discretion to request shorter or longer manuscripts.

**Paper-1 implication:** final compliance must be evaluated on the exact JAIS export, including figure/table equivalent space.

## 5. Reference style

**Official source:** AIAA, *Reference Style and Format*  
https://www.aiaa.org/publications/journals/reference-style-and-format/

Current AIAA requirements include numbered references cited in numerical order, use of original sources rather than secondary sources where possible, complete bibliographic information, and DOI URLs where available. The numbered reference list is intended for readily accessible published material.

**Paper-1 implication:** final JAIS export requires citation-order conversion plus a DOI/completeness/original-source audit.

## 6. ScholarOne submission information publicly confirmed

**Official source:** AIAA, *Submission of AIAA Conference Papers to Journals*  
https://www.aiaa.org/publications/journals/Submission-of-AIAA-Conference-Papers-to-Journals/

Current guidance for journal submission through ScholarOne states that authors follow system prompts, provide complete author/coauthor contact information, indicate that the paper is not classified and has not been submitted elsewhere, complete author verification before the submission is ready for review, supply suggested reviewer names/contact information as requested, and upload a double-spaced manuscript.

**Paper-1 implication:** the exact reviewer count and exact live field wording remain portal-only and must not be inferred.

## 7. Funding field

**Official source:** AIAA, *Journal Author*  
https://www.aiaa.org/publications/journals/Journal-Author/

Current guidance instructs authors to list funding sources and grant numbers in the ScholarOne submission field.

**Paper-1 value:** no external funding.

## 8. Artificial-intelligence policy

**Official source:** AIAA, *Ethical Standards for Publication of Aeronautics and Astronautics Research*  
https://www.aiaa.org/publications/Publish-with-AIAA/Ethical-Standards-for-Publication-of-Aeronautics-and-Astronautics-Research/

Current AIAA policy requires qualifying artificial-intelligence use in manuscript preparation to be disclosed upon submission in ScholarOne. When artificial intelligence is used in the writing process or permitted figure construction, authors must also provide a brief description in the technical paper. Authors remain fully responsible for the manuscript and may not list artificial intelligence as an author or cite an artificial-intelligence engine as an original source.

**Paper-1 implication:** retain a transparent in-manuscript disclosure and complete the exact live ScholarOne disclosure field. Artificial-intelligence assistance remains separate from the frozen deterministic experimental response mechanisms.

## 9. Public-release and copyright/clearance attestation

**Official source:** AIAA, *Copyright Clearance and Assignment*  
https://www.aiaa.org/publications/publish-with-aiaa/copyright-clearance-and-assignment/

AIAA states that during submission authors are presented with clearance and no-infringement forms. The clearance attestation distinguishes work that has been appropriately cleared for public release from work for which no classification/review is required.

**Paper-1 value:** the work is unclassified, uses no classified/proprietary mission telemetry, and requires no external company or government classification review for public release.

## 10. Posting/self-archiving policy

**Official source:** AIAA, *Publication Policies*  
https://www.aiaa.org/publications/Publish-with-AIAA/Publication-Policies/

Current AIAA policy permits authors to post draft manuscripts and research results before submission and defines allowed self-archiving/posting after submission, acceptance, and publication.

**Paper-1 implication:** existing public repository and research-archive materials do not by themselves prevent preparation of a JAIS submission; final accepted/published-version posting must follow the applicable AIAA copyright/self-archiving rules.

## 11. Supplemental material

**Official source:** AIAA, *Supplemental Materials for AIAA Journals*  
https://www.aiaa.org/publications/journals/Supplemental-Materials-for-Journals/

AIAA encourages relevant supplemental files such as datasets, extensive tables, and multimedia, while requiring the primary article to remain self-contained. Acceptance is based on the article itself.

**Paper-1 implication:** public Zenodo/GitHub evidence supports reproducibility but does not replace a self-contained manuscript.

## ScholarOne-only items still pending

The public sources above do not reliably expose the current production JAIS values for:

- exact article-type dropdown wording;
- exact suggested-reviewer count and required/optional status;
- excluded-reviewer workflow;
- subject classifications/taxonomy;
- exact conflict-of-interest field wording;
- exact ethics/institutional-review questions, if any;
- exact data/code availability fields, if any;
- exact prior-dissemination/related-manuscript fields;
- exact artificial-intelligence disclosure wording;
- exact upload-item designations/order;
- editor/special-issue selection fields;
- final submission preview/attestation sequence.

These remain intentionally unresolved until the live production JAIS ScholarOne workflow is inspected. No missing portal field is to be reconstructed from memory.

## Gate result

**JAIS/AIAA public scope and author-requirements verification:** PASS.  
**Exact production ScholarOne field lock:** PENDING.  
**Scientific changes authorized by this verification:** NONE.
