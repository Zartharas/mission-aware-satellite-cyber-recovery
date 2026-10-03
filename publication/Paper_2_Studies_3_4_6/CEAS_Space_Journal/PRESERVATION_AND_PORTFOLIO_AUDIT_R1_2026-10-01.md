# Paper 2 CEAS R1 — scientific preservation and portfolio audit (2026-10-01)

## Authority and edit boundary

- Source: merged R4 at main `4cd0c30a276b3c5a0494736b93a8d08dc1ed8df4`, exact manuscript git blob `069e319864b1f5c1ee201b31872e68572fea1923`.
- CEAS R1 new manuscript git blob: `a16fba122ad1b42a54c26bffee68ff05ad477b51`.
- Original canonical Figure-1 SVG remains at `../Post_Rejection_Rebuild/figures/PAPER2_R2_FIGURE1_RESIDUAL_BOUNDARIES.svg`, git blob `5f68ac156b4e27c7bfd99e006623196c250c94a1`, SHA-256 `adfdfaf833c8624bb405209be22ef6b2f002cdec53f081ce097f67e728eedffc`.
- Reproducible audit: `python scripts/audit_paper2_ceas_r1.py` reconstructs the **entire Methods/Results/Conclusion body** from R4 using only the documented text-only alterations and verifies that all reference text remains identical.

## Exact authorized R4 -> R1 changes

1. Replace R4 internal prevenue header with CEAS author-review source authority and sole-author metadata. Do not include private contact email.
2. Replace Abstract with a condensed, source-bound **220-word** version; original six index terms re-label to Keywords without changes.
3. Insert one Introduction bridge linking qualification observation sets to mission-specific engineering requirements while explicitly denying integration or learned-policy comparison.
4. Convert section headings from Roman to decimal, subsection letters to decimal, table captions/citations from Roman to Arabic, and Figure 1 references to Fig. 1; keep actual table bodies and all metrics unchanged.
5. Correct relative path in the CEAS child directory to embed **the same canonical SVG**, not a modified reproduction.
6. Adapt substantive AI drafting disclosure to Springer author accountability; add explicitly **non-final, author-confirmation-required** funding/conflicts/contributions/data/code/ethics declaration drafts.
7. Preserve all twenty original R4 reference entries byte-for-byte within the CEAS R1 References section. Journal-reference formatting remains a later controlled editorial step.

## Scientific claim firewall

| Material | CEAS R1 use | Prohibited claim or migration |
|---|---|---|
| Study 3 / S3-K4E-001 | 1,380 trajectories / 67,620 epoch states, exact temporal finding | No use of Paper-1 studies as new evidence |
| S3X / S3X-ETA-001 | 1,919 external ESA timing-proxy intervals, separately governed cases | Not an RF/contact outage measurement or Study-3 empirical replication |
| Study 4 / S4-MPQ-001 | 4,608 observations across 18 independent rule conditions | Not a Study-7E selector-topology experiment; no causal real-world independence claim |
| Study 6 / S6-SCTR-001 | 420 finite assurance observations; residual APPROVED_BAD_SOURCE | Not software certification or mission-safe flight test |
| S6X / S6X-EAP-001 | Two repetitions × 396 observations / eight builds, zero evaluator mismatch; functional RC0/RC2 research-only | Not a NASA cFS vulnerability, not a fourth Figure-1 panel; adjudication not among six gate signals |

Paper 1 / Studies 1+2 (JAIS submitted 2026-09-05), Paper 3 / Studies 7+7E (separate **unmerged PR #168**, IJCIP preparation), Paper 4 / Studies 8+8E (PQC transition and SatNOGS timing), and Paper 5 / Study 9 (semantic interoperability / **unmerged PR #117**) remain distinct; no figures, rows, result quantities or experimental populations imported. The earlier CEAS rejection on 2026-09-22 applied to **Paper 3's different Study-7 manuscript**, not this Paper-2 venue adaptation.

## Review boundaries

**Current manuscript state:** complete text-level CEAS R1 *candidate* for author review, NOT upload-ready. Title-page contact/ORCID confirmation, author-declaration confirmation, public data/code archival check, final journal bibliography formatting, editable publisher export, vector figure conversion and page-by-page PDF proof remain open.

**Governance:** no merge, no scientific execution, no R4/old Figure-1 change, no live publisher portal, no author email dispatch, no publisher submission, no GitHub visibility modification.
