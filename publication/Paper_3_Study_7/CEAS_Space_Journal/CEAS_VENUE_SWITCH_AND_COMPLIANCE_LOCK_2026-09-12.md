# Paper 3 / Study 7 — CEAS Venue Switch and Compliance Lock

**Lock date:** 2026-09-12  
**Status:** `PASS__CEAS_SPACE_JOURNAL_PRIMARY_TARGET__ORIGINAL_RESEARCH_ARTICLE`  
**Branch:** `publication/paper3-study7-ceas-submission`  
**Base manuscript:** audited Paper-3 R3 from the prior JAIS development track  
**Study:** `S7-LSO-001`

## 1. Venue decision

The primary target for Paper 3 is now:

**CEAS Space Journal**  
**Article type:** `(Original) Research Article`

This supersedes the earlier JAIS Technical Note target for Paper-3 development. The JAIS development directory is retained unchanged as historical provenance; no submitted JAIS artifact is modified.

The scientific reason for the switch is venue diversification plus an unusually direct scope match. CEAS Space Journal explicitly lists both **cybersecurity for space systems** and **artificial intelligence in space** among its disciplines of interest, alongside mission design and space systems, operations, avionics, small satellites, and related technologies.

Official scope checked 2026-09-12:

https://link.springer.com/journal/12567/aims-and-scope

## 2. Article type

Use **Original Research Article**, not Short Communication.

The journal states that Original Research Articles should contain original research of high scientific quality and significant new experimental, numerical and/or theoretical content. Short Communications are about 2,500 words, are submitted as “Correspondence,” and are intended for work that needs immediate publication under strict length limits.

Study 7 needs enough space to preserve the finite design, adversarial-evidence boundary, exact state-space results, limitations, reproducibility controls, related-work separation, and declarations without suppressing methodological detail.

Official instructions checked 2026-09-12:

https://link.springer.com/journal/12567/submission-guidelines

## 3. Mandatory submission-source format

Primary source file:

- editable Microsoft Word `.docx` manuscript.

For a `.docx` submission the journal also asks authors to submit a **PDF version of the manuscript as supplementary material**.

Formatting controls:

- normal plain font, e.g. 10-point Times Roman;
- automatic page numbering;
- decimal heading system;
- no more than three heading levels;
- Word table function for tables;
- Equation Editor/MathType for equations where required;
- abbreviations defined at first use and then used consistently.

The CEAS version will therefore convert the prior Roman/A/B heading scheme to decimal headings.

## 4. Title page requirements

The manuscript title page must include:

- concise informative title;
- author name;
- affiliation, city, state/country where applicable;
- clear corresponding-author designation;
- active corresponding email;
- ORCID if available.

The current sole-author development identity is retained unless the author explicitly changes it.

## 5. Abstract and keywords

Mandatory abstract:

- **150–250 words**;
- no undefined abbreviations;
- no unspecified references.

Mandatory keywords:

- **4–6** indexing terms.

Paper-3 target keywords:

1. satellite cybersecurity;
2. cyber recovery;
3. artificial intelligence in space;
4. machine learning assurance;
5. observability;
6. evidence integrity.

These are development values and remain subject to final metadata QA.

## 6. Reference style

Use numbered citations in square brackets and a consecutively numbered reference list.

Where available, DOI values should be written as full DOI links (`https://doi.org/...`).

The CEAS manuscript must include only cited works that are published or accepted for publication. Unpublished related manuscripts are handled through cover-letter/submission disclosure rather than being silently represented as published literature.

## 7. Tables and figures

Tables:

- Arabic numbering;
- cited in consecutive order;
- descriptive captions;
- table footnotes beneath the table body.

Figures:

- Arabic numbering;
- captions in the manuscript text;
- figures placed in the body where practical;
- preferred vector format EPS; MS Office graphics are also acceptable;
- embedded fonts in vector artwork;
- RGB for color;
- accessibility-compatible captions/contrast.

No unsupported performance graphic will be added merely for presentation. The existing scientific display boundary remains in force.

## 8. AI-use policy lock

The journal states that LLMs such as ChatGPT do not meet authorship criteria and that LLM use should be documented in the **Methods section** unless use was limited to simple AI-assisted copy editing.

Paper 3 used AI beyond copy editing during manuscript development, including structure, drafting support, source discovery, compliance review, and language revision. Therefore **AI-use disclosure is mandatory**.

Springer Nature's current manuscript-preparation policy classifies AI-assisted outlining, section drafting from author input, framing suggestions, reference-management support, and verifiable-source visual assistance as uses that require human verification, transparency, and author accountability. It explicitly does not permit AI to replace authorship or independently generate scientific claims/results without oversight.

Official policy checked 2026-09-12:

https://www.springernature.com/gp/policies/editorial-policies/ai-manuscript-preparation

### Paper-3 disclosure requirement

The CEAS manuscript must contain a Methods-subsection disclosure that accurately states:

- the AI system used;
- the purpose and extent of assistance;
- that the author defined and controlled the research question, study design, frozen evidence boundary, scientific interpretation, and final claims;
- that numerical results were verified against the frozen accepted evidence;
- that references were checked against primary/publisher records;
- that AI did not generate or alter the frozen Study-7 observations;
- that the author takes full responsibility for the manuscript.

The wording must remain accurate to actual provenance and should not claim that AI was used only for copy editing.

## 9. Statements and Declarations

The journal requires relevant declarations and warns that incomplete submissions may be returned.

Paper 3 should include a **Statements and Declarations** section before the References containing, as applicable:

- Funding;
- Competing interests;
- Author contributions;
- Data availability;
- Code availability;
- Ethics approval / consent where applicable.

Development defaults, subject to final author confirmation:

### Funding

`No funding was received for conducting this study or preparing this manuscript.`

### Competing interests

`The author has no relevant financial or non-financial interests to disclose.`

### Author contributions

A sole-author contribution statement will be included and reconciled against the actual Study-7 provenance before submission.

### Ethics / consent

No human participants, human data requiring consent, or animal subjects are part of Study 7. Use `Not applicable` only where the manuscript/submission interface requires an explicit field.

## 10. Data and code availability

All original research articles require a Data Availability Statement.

The journal strongly encourages public repository deposition and recommends citation of public datasets with persistent identifiers such as DOIs.

Paper 3 currently has:

- public repository: `https://github.com/Zartharas/mission-aware-satellite-cyber-recovery`;
- frozen protocol/results in the repository;
- accepted Study-7 execution provenance and hashes;
- a GitHub Actions evidence artifact that is not a sufficient long-term archival endpoint because it expires.

**Pre-submission requirement:** permanently archive the exact accepted Study-7 evidence bytes in a durable repository, preferably Zenodo, without rerunning or modifying the experiment, then cite the resulting persistent identifier in the Data Availability Statement and References.

## 11. Publication ethics / related manuscripts

Submission implies that the manuscript is not under consideration elsewhere.

Paper 3 is not submitted to another venue.

Because the broader research program has related active manuscripts, the CEAS cover letter and submission workflow must provide transparent related-work disclosure where required.

Relevant active lines include:

- Paper 1 / Studies 1+2 at AIAA JAIS;
- Paper 2 / Studies 3+4+6 at IEEE TAES;
- Study 8 / Roadmap Paper 4 at Acta Astronautica;
- the separately scoped spacecraft software supply-chain assurance manuscript at Journal of Space Safety Engineering, based on the distinct `verifiable-spacecraft-lifecycle` repository.

The disclosure should state that none of those manuscripts uses Study 7's 1,033-observation experimental population as its new experimental evidence.

The corresponding-author guidance specifically calls for transparency regarding reused material and unpublished related material in a cover letter.

## 12. Closest-prior-work outcome

A dedicated audit on this branch found Paper 3 scientifically distinct from the closest CEAS Space Journal neighbors.

Required citations:

- Wanninger, knowledge-based satellite FDIR — cite as adjacent recovery/FDIR implementation;
- Tappe et al., supervised AI anomaly-detection/diagnosis/reconfiguration toolchain — cite as the closest AI fault-management/reconfiguration neighbor.

Kübler et al.'s in-orbit optical AI system is scientifically tangential and should not be cited solely because it appears in the target journal.

See:

`CEAS_CLOSEST_PRIOR_WORK_AND_NOVELTY_AUDIT_2026-09-12.md`

## 13. Submission-package sequence

Before portal submission:

1. create CEAS-compliant R1 manuscript source from the audited R3 science;
2. add 150–250-word abstract and 4–6 keywords;
3. convert headings to decimal style;
4. add Wanninger and Tappe citations with explicit novelty separation;
5. add AI-use disclosure in Methods;
6. add Statements and Declarations;
7. complete permanent Study-7 data archive and update Data Availability;
8. generate `.docx` and matching PDF;
9. perform scientific-claim, reference, formatting, and related-work audits;
10. prepare cover letter and submission-interface values;
11. prepare independent reviewer suggestions if useful;
12. obtain explicit final author authorization before pressing the publisher submission action.

## 14. Gate disposition

**GO — CEAS Space Journal / Original Research Article.**

**NO-GO — any new scientific execution, enlargement of the frozen Study-7 population, unsupported operational claims, or publisher submission before final package QA and explicit final authorization.**
