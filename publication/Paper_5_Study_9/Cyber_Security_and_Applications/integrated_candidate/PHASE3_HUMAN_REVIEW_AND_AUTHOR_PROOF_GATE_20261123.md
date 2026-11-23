# Paper 5 Phase 3: human methods review and author PDF / publisher gate

**Prepared:** 2026-11-23  
**Status:** `PENDING_HUMAN_REVIEW_AND_AUTHOR_APPROVAL`; **not submitted; PR #255 must remain draft and unmerged.**  
**Authorizations:** Manuscript-only adversarial-remediation and preparation of human/visual review materials. No experiments, raw-source release, external manuscript transmission, journal upload or merge.  
**Supersedes for current readiness only:** The 2026-11-23 `FINAL_AUTHOR_SUBMISSION_GATE_20261123.md`'s *old* 23-page/15-reference snapshot and corresponding old CI run numbers. Its author attestations remain **unanswered**, not superseded or automatically approved.

## Research and source pins for human inspection

| Evidence class | Canonical source, scope and verification boundary |
|---|---|
| Study 9 frozen science | Repo `Zartharas/mission-aware-satellite-cyber-recovery`, baseline `5ee451c2a739cbca7dc948d49239d985c6b4cc07`; study9 protocol/mapping/policy freeze and accepted canonical results. Source populations 25,000, 137,965, 404,798. |
| Study 10 frozen design | G2 receipt on `study10/s10-rsei-001-g2-freeze-receipt-20261122`, pinned protocol payload `8ed6a2b16233b86bf91672f6f15605dcf906c5eb`. Internally frozen after some declared prior metadata exposure, **not** externally preregistered. Four primary ESA-v2/OPS-SAT strata; Hack-A-Sat secondary unpooled and unexecuted. |
| Study 10 synthetic methodology | `study10/s10-rsei-001-g3-post-parity-audit-g4-hold-20261123`: 18 synthetic cases, 22 tests and 1,024 exact oracle comparisons. Not real-flight recovery. |
| Study 10 derived-only observational evidence | `study10_derived/S10_G4_TierA_32Slot_PublishedSchema.json`; `S10_G4_TierC_16_StratumPolicy_NonEvaluable.json`; `S10_RQ_E3_ESA_V1V2_Aggregate_Metadata.json`; hashes/exclusions in `README_MANIFEST.json`. |
| Public inputs | ESA v2 DOI `10.5281/zenodo.15237121`, ESA v1 comparison DOI `10.5281/zenodo.12528696`, OPS-SAT-AD v2 DOI `10.5281/zenodo.15108715`. No original bytes republished. Rights and channel-detail exceptions remain under author control. |
| Integration and prior challenge | Exact Phase 2 assessed source commit `0dd962071b6adb16a9ad572046f9f90c59f922a7`; report added at `e171a2e7225c23539c56864cf7824ca90f9958b8`. See `PHASE2_ADVERSARIAL_REREVIEW_20261123.md`. |
| Revised manuscript and supplement | Use the **current PR head**, not the above historical commits, for author PDF approval; source is `CSA_S9_S10_INTEGRATED_CANDIDATE.tex`, `references.bib`, `PHASE2_FIELD_LEVEL_EVIDENCE_SUPPLEMENT.tex` and `PHASE2_FIELD_LEVEL_EVIDENCE_APPENDIX.tex`. |
| Exact checks | Phase 2 science input both workflows passed: `45265668348` LaTeX and `45265668356` repository. Review-document commit checks also passed: `45270778710` and `45270778729`. After Phase 3 manuscript edits, rerun / verify both latest workflows and record the revised PDF artifact IDs. |

## A. Human methods reviewer — questions, not claimed answers

A reviewer with relevant domain and mathematical-method expertise should be given a current candidate, source-linked field judgments and the frozen protocols **only through an author-approved confidential process**. Do not send unpublished work to anyone automatically. Do not falsely describe this AI-authored gate as external peer review.

- [ ] **Novelty:** Against TRACE, RTEF-IDS, AIRSS, CCSDS firewall, Stargate, SAFE and evidence-bound warrants, does this exact cross-product field-sufficiency audit add publishable knowledge? Identify its strongest *and* weakest original claim, with citations.
- [ ] **Construct validity:** Is the fixed eight-predicate mission recovery contract sufficiently motivated, or is its zero-coverage endpoint effectively predictable because detection datasets cannot expose operational trust/authorization evidence?
- [ ] **RQ1–RQ4:** Independently challenge each mapping class, the `Position_Anomaly` dataset-wide deviation, mathematical completion endpoint and 6/7/7/8 policy-specific sidecar minima.
- [ ] **RQ-E1–RQ-E5:** Confirm G2 primary four-stratum scope, note secondary Hack-A-Sat not executed, distinguish 54 paired metadata differences from actual semantic-class transitions, confirm 16 `NOT_EVALUABLE` outcomes have no operational recovery-rate denominator, and separate synthetic harness parity from field validation.
- [ ] **Threats to reproducibility:** Identify which exact source bytes, rights receipts, adjudicator decisions or tooling are missing from public source-to-result reproduction. Distinguish independently validated GitHub-derived results from author-only local report output.
- [ ] **Generalization and ethics:** Check for accidental independence claims, unsafe recommendations, overclaims of real flight recovery, questionable rights notices, and unqualified missing-field interpretations.
- [ ] **Recommendation:** Provide a written *accept for author revision / major revision / different venue / new preapproved study* appraisal and evidence, clearly naming reviewer and review date with permission. This checkbox must only be completed by the reviewer or author after receiving a real review.

**Human reviewer identity / date / conflicts / notes:** `PENDING`  
**Human external methods review:** `NOT_PERFORMED`

## B. Author visual proof of two current-head PDFs

Historical Phase 2 build yielded **31-page main PDF + 4-page separate S1 supplement**, zero overfull boxes, 123 underfull in main; this is **not** a guaranteed page count or log state for the revised manuscript. The bibliography after the editorial revision contains **24** source records (20 original + four source-verified closest-work additions), pending next exact-head LaTeX CI. Author must inspect artifacts built from the **latest** commit.

- [ ] Retrieve latest run from [PR #255](https://github.com/Zartharas/mission-aware-satellite-cyber-recovery/pull/255), Actions `Paper 5 integrated draft LaTeX validation`, and download its main + S1 PDF artifacts.
- [ ] Record **final SHA, workflow run IDs and actual page counts**; confirm no unresolved citations, overfull boxes, errors or missing figures after edits.
- [ ] Visually inspect **every main PDF page** at normal zoom: title/contact placeholders; abstract; nine-RQ table; closest-work table; diagram, caption and cross-references; ESA/OPS counts; appendix citations; bibliography legibility.
- [ ] Inspect all **four or updated number of S1 pages**: 24 S9 + 32 S10 mappings visible; tables not cropped; source-field names, exclusion judgments and evidence roles readable.
- [ ] Evaluate footnotes, page-break gaps, poor line breaks (especially any underfull warnings), typography and figure rendering. Log page numbers requiring edits, **not** just a technical pass.
- [ ] Verify all LaTeX figure disclosures, including the exact ChatGPT tool/model history for initial diagram drafting, and ensure no image asserts fabricated observed data.
- [ ] Approve or reject the typeset manuscript **with author name/date and exact final SHA**. The assistant must not check these boxes.

**Author PDF visual verification:** `NOT_PERFORMED`  
**Author title/affiliation/correspondence approval:** `NOT_RECORDED`

## C. Publisher / original research gate (author only)

The current [CSA Guide for Authors](https://www.keaipublishing.com/en/journals/cyber-security-and-applications/guide-for-authors/) and [Elsevier journal AI policy](https://www.elsevier.com/about/policies-and-standards/generative-ai-policies-for-journals) were checked on 2026-11-23. They require author accountability, AI text/image disclosures, and publisher forms; only the author can attest to personal information or competing interests.

- [ ] Confirm the exact current byline, independent researcher designation, ORCID, **full postal address** and corresponding email already in title-page source; do not infer or replace them.
- [ ] Recheck research originality/exclusivity, overlapping studies/papers and prior preprint disclosures. No current combined manuscript submitted elsewhere unless expressly disclosed.
- [ ] Independently verify the new four references and their scope: CCSDS 2026 full text was not available; SAFE published online 20 November 2026; Stargate was a 13 November arXiv preprint, not yet cited as a published proceedings paper; EBAW appeared 23 November 2026.
- [ ] Confirm OpenAI ChatGPT and figure/model-version accuracy; revise disclosure only from author-confirmed facts; independently edit and check AI-assisted wording/citation accuracy.
- [ ] Review funding, current employment and consultancies, perceived conflicts, intellectual property, relevant prior three-year relationships, and institutional disclosure duties; the previous sentence stating no competing interests is **proposed** and not a completed declaration.
- [ ] Use [Elsevier declarations tool](https://declarations.elsevier.com/) and supply its generated `.doc`/`.docx` file. Do not fake a form or an author attestation.
- [ ] Confirm specific ESA/OPS-SAT attribution, ESA v2 license limitations, release-specific source notices, no original-data republication; arrange stable supplementary release only if later separately authorized.
- [ ] Check all 3–5 highlights, 3–6 keywords, live journal requirements, sponsor/acknowledgment disclosures, supplement caption and upload plan.
- [ ] Provide specific approval for **final submission candidate at exact SHA**; the present permission to perform editorial work does not approve journal submission or merging.

**Status:** `AUTHOR_CONFIRMATION_PENDING` / `HUMAN_REVIEW_PENDING` / `PR_DRAFT_NO_SUBMISSION`.

## D. Stopping rule

Passing GitHub CI, presence of this checklist, current source citations, or success of a static validator **does not** certify scientific novelty, human review, license clearance, final PDF layout, model-version attribution or author attestations. Do not merge, upload to publisher, distribute raw data or run a new study without a separate explicit approval.
