# Paper 5 (Studies 9 + 10): author-only final submission gate

> **Historical checkpoint, superseded for current technical readiness:** This file records an earlier, successfully built 23-page/15-reference candidate and older CI run IDs. It is preserved as evidence of the earlier gate, **not** a current manuscript readiness certificate. For the revised Phase 3 manuscript, use `PHASE3_HUMAN_REVIEW_AND_AUTHOR_PROOF_GATE_20261123.md` and the current PR head's latest two workflow runs. None of the author-only checkboxes below have been completed by subsequent editorial authorization. No journal submission or merge is approved.

**Recorded:** 2026-11-23  
**Stage:** `PRE_SUBMISSION_AUTHOR_CONFIRMATION_REQUIRED`  
**Status:** `HOLD_NOT_SUBMITTED_NOT_MERGED`  
**Repository:** `Zartharas/mission-aware-satellite-cyber-recovery`  
**Pull request:** https://github.com/Zartharas/mission-aware-satellite-cyber-recovery/pull/255

## What is verified already (not author attestation)

- [x] PR #255 has passed the dedicated exact-head LaTeX and Study 10 derived-evidence SHA-256 validation at commit `c56cd44de9875b8f7c723af8f81c8df84afcf679` (Actions run `45236633869`).
- [x] Repository-wide `Validate research configurations` finished SUCCESS (Actions run `45236633957`).
- [x] Latest reviewed manuscript PDF has 23 pages, zero overfull boxes and no unresolved references or citations in final `latexmk` output.
- [x] Bibliography contains 15 referenced items, highlights contain five items within 85 characters, and the abstract has approximately 255 words (limit 350). Six keywords remain within the journal's 3--6 range.
- [x] Study 10 derived-only archive is hash-checked: three JSON files, 32 Tier A slots, 16 Tier C reporting rows, and one aggregate ESA v1/v2 metadata comparison; original telemetry, nested pickles, source datasets and local paired-detail CSV were excluded.
- [x] Study 9 and Study 10 are disclosed as distinct prospectively governed studies combined in a **post-results** manuscript. The manuscript distinguishes Study 9's mathematical action-set endpoint from Study 10's operational non-evaluability.
- [x] Source release credits and rights qualifications are documented for ESA v2 DOI `10.5281/zenodo.15237121`, optional ESA v1 DOI `10.5281/zenodo.12528696`, and OPSSAT-AD v2 DOI `10.5281/zenodo.15108715`.
- [x] Manuscript includes funding, conflict-of-interest and AI-assistance statements **as proposed author text**, not independently certified facts.

## Required sole-author confirmations (NOT completed by assistant or by a general authorization to proceed)

- [ ] **Manuscript and title:** Read and approve the full 23-page integrated manuscript, its scientific limitations, post-results integration disclosure, all tables and sources, and the proposed title.
- [ ] **Author identity and correspondence:** Confirm preferred byline/credentials, single-author status, institution/independent-researcher designation, ORCID, the **current corresponding email appearing on the LaTeX title page**, and full postal contact address required by the journal. Do not change the email based on a different earlier manuscript without author approval.
- [ ] **Competing interests (2026 rules):** Assess all relevant employment, consultancy, stock ownership, honoraria, patents, grants, institutional relationships and other activities during the journal's relevant three-year period, including perceived conflicts. Complete the publisher's **Elsevier declarations tool** at https://declarations.elsevier.com/ and retain its **.doc/.docx output** for the portal. The preexisting paper's `no competing interests` sentence must not be construed as an independently verified clearance.
- [ ] **Funding and contributions:** Confirm the claimed no-grant/no-funding statement, author contribution roles and whether any sponsor or institutional authority must be disclosed.
- [ ] **Originality/exclusivity:** Confirm that neither this integrated paper nor substantially overlapping Study 9/Study 10 manuscript material is submitted to or being considered by another venue. Confirm permissions and any institutional approvals applicable to the research and intended publication.
- [ ] **AI-use disclosure:** Confirm the final factual statement describing ChatGPT's role and the author's source checking and editorial responsibility; keep this separate from the competing-interests Word document.
- [ ] **Rights and notices:** Review source-by-source R1 conditional eligibility, ESA v2's blank readable Zenodo Rights field, CC BY 3.0 IGO dataset-level provenance and possible file-specific exceptions, and OPSSAT-AD v2's MIT terms. Explicitly approve final intended publication use and notices without claiming blanket original-telemetry rights. Retain the no-endorsement and modification-description language.
- [ ] **Data availability / supplemental materials:** Decide whether to cite the draft PR's hashed derived-only JSON archive as a review artifact or prepare a stable, rights-reviewed release after separate approval. No original telemetry, raw dataset ZIP, unredacted channel identifiers, or paired-detail CSV may be published without a new, explicit rights and disclosure review.
- [ ] **Bibliography / editorial polish:** Personally check source-specific titles, authors, DOI resolution and content from the actual publications. The AegisSat proceedings reference produces a nonfatal BibTeX warning for absent page numbers; **do not invent a page range**.
- [ ] **Final approval:** Specifically approve a submission candidate after inspecting the final generated PDF and editable source package; any merging or submitting remains a separate deliberate action.

## Journal requirements checked 2026-11-23

Author instructions: https://www.keaipublishing.com/en/journals/cyber-security-and-applications/guide-for-authors/

- Research-article text remains editable, with `.tex` source and `references.bib`. The PDF is a review artifact, **not** a substitute for editable source.
- Abstract maximum: 350 words. Keywords: 3--6. Highlights: 3--5 items and maximum 85 characters each, uploaded as a separate editable highlights file.
- A separate Elsevier-generated competing-interest **Word** declaration is requested, even if there is nothing to declare; the full three-year relationships disclosure matters for manuscripts submitted after January 1, 2026.
- Generative AI use in manuscript preparation must be declared, and sources and claims reviewed by the author.
- Research data can be linked to stable datasets or an explicit availability limitation stated; the Study 10 review-branch outputs are **not yet a stable data deposit**.
- Open-access fee presently displayed as USD 800 excluding taxes, **fully waived for articles submitted before June 30, 2027**. This is a published policy as checked on 2026-11-23, not a quote or guaranteed future entitlement.
- Submission implies originality, consent of authors and relevant authorities, and no concurrent consideration of the same work elsewhere.

## Decision

`TECHNICAL_QA_PASS` / `AUTHOR_AND_PUBLISHER_SIGNOFF_PENDING` / `NO_GO_FOR_PORTAL_SUBMISSION`.

**No assistant assertion of author confirmation, independent legal clearance, PR merge, journal submission or publication has been made.** The latest broad user authorization is interpreted as permission to perform the pre-submission audit and prepare the author review gate, **not** as a declaration of facts or an instruction to submit.
