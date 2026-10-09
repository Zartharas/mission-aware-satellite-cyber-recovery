# Paper 2 — CEAS Space Journal definitive new-chat handoff
**As-of:** 2026-10-09. **Scope:** publication manuscript preparation; not journal submission.  
**Authority:** private repository `Zartharas/mission-aware-satellite-cyber-recovery`, check live `main` and both active PRs before proceeding.

## Verified GitHub checkpoint BEFORE this handoff commit

- Live `main` at verification: `4cd0c30a276b3c5a0494736b93a8d08dc1ed8df4`. Verify again in the new chat; do not assume it has stayed fixed.
- **Publication:** draft, open, unmerged [PR #216](https://github.com/Zartharas/mission-aware-satellite-cyber-recovery/pull/216); branch `publication/paper2-r5-readiness-20261008`; exact pre-handoff head `723b1ce374c339c54e52d648f95dba67c97f6224`. Workflow **#1434**, run ID **37938128591**, *SUCCESS* on this exact head.
- **Optional P2X/NOS3:** draft, open, unmerged [PR #215](https://github.com/Zartharas/mission-aware-satellite-cyber-recovery/pull/215); branch `research/paper2x-nos3-phase-a-20261003`; exact head `0a5ab758a4b7f0002c3407d269efc7bb4cb22499`; workflow **#1428**, run ID **37819118655**, *SUCCESS*. Its 55 hash differences (51 Git indexes, four CMake logs) remain *conditional proposed omissions only*; exclusions applied **0**; workspace materialization, nominal runtime, COSMOS, faults and merge not authorized.
- **Historical independent core:** Frozen Studies **3, 4 and 6**; separately bounded extensions **S3X** (ESA timing proxies) and **S6X** (controlled executable cFS/LC fixture). Do not pool populations. No on-orbit or operational spacecraft recovery claim. P2X is **not** part of R4/R5 study claims and is not a mandatory gate for an editorial submission.
- **Rejection history:** TAES manuscript `TAES-2026-4182` originally submitted 2026-09-07, editorial prescreen rejected 2026-09-26 *without external peer review*. It criticized contribution narrowness, aerospace importance/relevance, convoluted prose, unclear gap, limitations-heavy framing, and activity rather than findings. Do not characterize this as a scientific-integrity or reviewer rejection.
- The accepted historical **R4 manuscript Git blob** is `069e319864b1f5c1ee201b31872e68572fea1923`; do not edit its file or the old TAES R10 submission.

## Publication branch authoritative paths

All relative to `publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/` unless noted:

| Record | Path |
|---|---|
| CEAS R5 complete draft | `PAPER2_CEAS_MANUSCRIPT_R5_2026-10-09.md` |
| Title page draft | `PAPER2_CEAS_TITLE_PAGE_DRAFT_2026-10-09.md` |
| CEAS-specific cover letter, **unsent** | `PAPER2_CEAS_COVER_LETTER_DRAFT_2026-10-09.md` |
| CEAS compliance and submission HOLD gate | `PAPER2_CEAS_JOURNAL_COMPLIANCE_GATE_2026-10-09.json` |
| Submission readiness checklist | `PAPER2_CEAS_SUBMISSION_READINESS_2026-10-09.md` |
| 20-reference review, machine record | `PAPER2_CEAS_REFERENCE_INTEGRITY_SCREEN_2026-10-09.json` |
| 20-reference review, narrative | `PAPER2_CEAS_REFERENCE_INTEGRITY_SCREEN_2026-10-09.md` |
| Prior R5 readiness/abstract candidate | `PAPER2_R5_PUBLICATION_READINESS_AND_ABSTRACT_CANDIDATE_2026-10-08.md` |
| CEAS editorial static audit | `scripts/audit_paper2_ceas_r5.py` |
| Draft local DOCX/PDF builder | `scripts/build_paper2_ceas_package.py` |
| Historical R4 guard, includes CEAS whitelist | `scripts/audit_paper2_r4_prevenue_figure_insertion.py` |
| This handoff | `PAPER2_CEAS_NEW_CHAT_HANDOFF_2026-10-09.md` |
| Machine continuation | `PAPER2_CEAS_CONTINUATION_STATUS_2026-10-09.json` |

**CEAS venue**: [CEAS Space Journal](https://link.springer.com/journal/12567), [official submission guidelines](https://link.springer.com/journal/12567/submission-guidelines), Original Research Article. Springer Nature. Single-blind review, hybrid publication. Format guidance captured in the compliance JSON. **CEAS-specific derivative is prepared; the actual portal submission remains separately unauthorized.**

R5 currently contains a **228-word abstract**, **six keywords**, **five Arabic-numbered tables**, **one Figure 1** based on unchanged canonical vector figure, and **20 references**. The manuscript has unresolved bracketed author-confirmation placeholders and remains a DRAFT. Check the live file and compliance gate before treating these as unchanged.

Reference screen: **14 matched**, **one automated generic-title mismatch [13]** (official SLSA source is not fabricated), **five not indexed** [4], [6], [11], [12], [20], zero retractions reported by the automated screen. The screen does not finish manual bibliography accuracy. **[6]** is an IETF multi-verifier *Internet-Draft*, not a finalized standard; author/editor must settle whether it can stay in the CEAS reference list or use a claim-preserving alternative. The source links in the reference screen are not universal DOI verification.

### Submission blockers to resolve in priority order

1. **Finish claim, contribution, and typography QA.** Lead with aerospace mission qualification engineering implications (not new spacecraft observations). Re-audit S3X/S6X claims against frozen status/claim-source records, all five tables and Figure 1. No cross-study pooling or science rewriting.
2. **Complete reference-level review.** Check every one of 20 author/title/date/DOI or official document version; resolve [6] as a genuine draft. Keep a traceable ledger of manual evidence and any corrections.
3. **Verify declarations with the sole author.** Legal display name, independent affiliation, corresponding email, financial/nonfinancial competing interests, any funding/support, source permissions, data/code availability/reviewer access, and author-contribution/ethics wording. Do **not** invent assertions from other papers. A private GitHub repository is not automatically a public dataset.
4. **Render preview DOCX + PDF and visually audit every page.** `python3 scripts/build_paper2_ceas_package.py --check` is a source-only static test. Only when CI for the latest PR head is SUCCESS and local Pandoc, CairoSVG and LibreOffice are available, a scoped draft-preview may generate `--draft-preview --out-dir <new-path-outside-repo>`. It does *not* make a clean publisher package by itself. Confirm tables, page flow, figure quality, reference links and no unfilled placeholders. Save checksums and preview evidence.
5. **Finish CEAS-specific portal field map, originality/prior-prescreen responses, data-sharing declaration, cover letter, signed-off title page and upload manifest.** Verify all actual CEAS portal-required fields against official guidance/current live UI; do not infer. Obtain explicit author's **final submission authorization** before portal actions. No PR merge without independent author approval.
6. Optionally continue P2X in **separate** PR #215 only when it materially supports a future independent validation study. It must not block R5 editorial preparation or be presented as existing recovery evidence.

## Next-chat starter prompt (copy verbatim)

> Continue **Paper 2 — CEAS Space Journal submission preparation** from the authoritative private GitHub repository `Zartharas/mission-aware-satellite-cyber-recovery`. **Start by reading live `main`, PR #216 and PR #215, and the handoff `publication/Paper_2_Studies_3_4_6/Post_Rejection_Rebuild/PAPER2_CEAS_NEW_CHAT_HANDOFF_2026-10-09.md` plus the adjacent continuation-status JSON.** Verify exact branch head and latest exact-head `Validate research configurations` CI before acting. At handoff creation, publication PR #216 was draft/unmerged at `723b1ce374c339c54e52d648f95dba67c97f6224` with workflow #1434 run `37938128591` SUCCESS; a separate handoff commit was subsequently made and must have its own CI checked. PR #215 was draft/unmerged at `0a5ab758a4b7f0002c3407d269efc7bb4cb22499` with #1428 SUCCESS. Use the live heads over historical expectations.
>
> The target is **CEAS Space Journal (Springer Nature), Original Research Article**. Produce the best evidence-based, venue-compliant Paper 2 submission package from **R5**, while preserving the historical R4 Git blob `069e319864b1f5c1ee201b31872e68572fea1923`, the rejected TAES R10, frozen Studies 3/4/6, and separate S3X/S6X evidence. Sole author is **Aman Kumar Singh**, independent researcher; final corresponding email, affiliation wording, funding, conflicts and reviewer-access data/code statements need verification. R5 has a 228-word abstract, six keywords, one figure, five tables, 20 refs and current declaration placeholders. 20-reference screen returned 14 matches, one misresolved SLSA title [13], five nonindexed, and an unresolved provisional IETF Internet-Draft [6]. Do not misreport unverified references as checked.
>
> Work efficiently with batched GitHub reads and bounded commits, keep a continuously accurate runbook/claim/source gate and validate exact-head CI after updates. Next: complete reference-level checking, scientific/figure/table QA, verify author declarations and data/code-access decisions, render local or available draft DOCX/PDF and inspect full pages, then finish CEAS portal requirements, editable manuscript, title page, cover letter, and submission checklist. Update PR #216 and preserve draft/no-merge status until I authorize merge. **Do not submit to a journal portal without my explicit final submission instruction.** P2X PR #215 is optional independent validation and must not be merged, executed or convolved with Paper 2 claims without separate authorization. If an external artifact cannot be rendered or a declaration cannot be confirmed, record the exact HOLD and proceed with other verifiable tasks; never fabricate completion. Avoid repeated CI polling, unnecessary experiments, or re-reading full files without purpose.
