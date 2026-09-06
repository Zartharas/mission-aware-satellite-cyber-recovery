# TAES IEEEtran Revision 3 Build Audit

**Audit date:** 2026-09-06  
**Build role:** Development-only two-column IEEEtran formatting audit  
**Canonical manuscript SHA-256:** `0381d6f60f5721ef2fb1ce3e0bce4e26133ad56cb2d123dfddfa24c2ab35f882`  
**Canonical Figure 1 PDF SHA-256:** `4872707261c8a8b6b747e76b9166b4ad7ae426e43d7bd9ffe272e4c5ea6f4ff8`  
**Canonical Figure 1 PNG SHA-256:** `7d22964bdae052b35b4680e1b09f3209f1c99bb1d157a0f995dcd2a6445e6698`

## Result

Revision 3 compiled successfully and remained development-only.

Observed build values supplied from the canonical Mac checkout:

- pages: `18`
- estimated pages beyond 10: `8`
- page size: `612 x 792 pts (letter)`
- text width: `7.100 in`
- column gap: `0.200 in`
- column width: `3.450 in`
- text height: `9.000 in`
- fonts reported: `9`
- all fonts embedded: `PASS`
- LaTeX warning count: `0`
- overfull hboxes: `7`
- overfull vboxes: `18`
- underfull hboxes: `26`
- underfull vboxes: `2`
- layout warning gate: `REVIEW_REQUIRED`

Generated artifact hashes:

- TEX: `393b28ffb36d3e5c776963694d8fe1166d1db4becc28e816b5f0c2d395f57534`
- PDF: `2a64d78dcc702ebdfcb1eb66df2c36c8e0d8b76de76e85a4eefa12106cfa5428`
- LOG: `dd206e41c81eaab5aa79655cd893595f4dae72a62bda66200d7a91b48767cfbb`
- build audit: `552c9c9e52713e5e361768e7d2dcfe89f6e10132511c24090ac8d534c6c6f89e`

## Revision 3 intervention

Revision 3 preserved the canonical Markdown manuscript and replaced the revision-2 URL-style identifier rendering with ordinary `\texttt{...}` plus explicit discretionary line-break opportunities after underscores and selected punctuation.

Reported revision controls:

- `breakable_code_tokens=300`
- `breakable_code_strategy=TEXTTT_EXPLICIT_DISCRETIONARY_BREAKS`
- `science_or_manuscript_source_changed=NO`

## Residual horizontal-overflow localization

The seven overfull hboxes were confined to four generated-TeX locations:

1. Study 3 frozen-primary-endpoints paragraph, with four reported overflow lines (`4.01677`, `24.26808`, `25.46812`, and `41.00798` pt);
2. Study 6 G4/G5 gate-definition list item (`5.10483` pt);
3. Study 6 G1 target-digest paragraph (`11.00798` pt);
4. Study 6 assurance-signal limitations paragraph (`14.89772` pt).

Because revision 3 already contained explicit identifier break opportunities, these residual overflows are treated as local paragraph-justification pressure rather than evidence that identifiers remain mechanically unbreakable.

## Page-count interpretation

The page count remained 18 after the earlier reduction from 24 to 7 horizontal overflows and again after revision 3. This makes 18 pages a more credible development estimate, but it is not yet a publisher-facing page count because:

- horizontal overflow remains unresolved;
- repeated vertical warnings remain unresolved or visually unclassified;
- the exact development PDF has not yet passed page-by-page visual QA.

No scientific compression or deletion is authorized by this audit.

## Next action

Revision 4 may alter only localized generated-TeX line-breaking behavior in the four residual problem blocks. It must not change manuscript source text, frozen identifiers, table rows, Figure 1, scientific content, or TAES geometry.

**Verdict:** `PASS_REVISION3_BUILD_PROVENANCE_RECORDED__FORMAT_GATE_REMAINS_OPEN`
