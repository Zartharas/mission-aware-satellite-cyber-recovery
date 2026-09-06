# TAES IEEEtran Development Build Revision 2 Audit

**Audit date:** 2026-09-06  
**Status:** `PASS_COMPILED_DEVELOPMENT_ONLY__HORIZONTAL_OVERFLOW_REDUCED__REVISION_3_REQUIRED`  
**Publisher-facing:** No  
**Submission authorized:** No

## Canonical input bindings

- Canonical manuscript SHA-256: `0381d6f60f5721ef2fb1ce3e0bce4e26133ad56cb2d123dfddfa24c2ab35f882`
- Figure 1 PDF SHA-256: `4872707261c8a8b6b747e76b9166b4ad7ae426e43d7bd9ffe272e4c5ea6f4ff8`
- Figure 1 PNG SHA-256: `7d22964bdae052b35b4680e1b09f3209f1c99bb1d157a0f995dcd2a6445e6698`
- Scientific or manuscript source changed by revision-2 typesetting: No

## Revision-2 deterministic build result

The local canonical checkout completed the revision-2 development build successfully after Courier support had been installed in the TeX Live environment.

Reported build values:

- `TAES_IEEETRAN_BUILD=PASS_COMPILED_DEVELOPMENT_ONLY`
- `TAES_IEEETRAN_BUILD_REVISION=2`
- `breakable_code_tokens=300`
- `breakable_code_macro=URL_PACKAGE_PATH`
- pages: 18
- estimated pages beyond 10: 8
- page size: 612 x 792 pt, US Letter
- text width: 7.100 in
- column separation: 0.200 in
- column width: 3.450 in
- text height: 9.000 in
- all PDF fonts embedded: PASS
- LaTeX warnings: 0
- overfull hboxes: 7
- overfull vboxes: 18
- underfull hboxes: 26
- underfull vboxes: 2
- layout gate: `REVIEW_REQUIRED`

Generated-artifact hashes reported by the local run:

- TeX SHA-256: `7bd71976ffb54fc41150f412f15e7445c93c352f6971abb291dac69b6038aa45`
- PDF SHA-256: `55249a6a7e1b9b98d4edaf3497e80f09bf6f3d5924de7945ec18a188db4cfa15`
- log SHA-256: `7e616eab2bcdc7725d9932ea4744b5ab6114951dfc5fc2d3f6d5e9f081c1c3d9`
- build-audit SHA-256: `f2302ffbcba398bce48efdcb5d7a5210253df39a3d39d277668696847a565d49`

The generated artifacts remained untracked and development-only.

## Horizontal-overflow result

Revision 2 reduced overfull hboxes from 24 in the first complete build to 7 without editing the manuscript source. The remaining hboxes were concentrated in four manuscript locations:

1. Study 3 endpoint-list paragraph containing multiple long endpoint identifiers. Four overfull boxes were reported there, up to 41.00798 pt.
2. Study 6 gate-definition bullet containing `G4_PROVENANCE_SOURCE_REVIEW`, 5.10483 pt.
3. Study 6 paragraph beginning with `G1_SIGNATURE_TARGET_DIGEST`, 11.00798 pt.
4. Study 6 assurance-signal paragraph containing `independent_target_digest_match` and `independent_reproduced_build_match`, 14.89772 pt.

This concentration supports treating the residual problem as identifier line-breaking mechanics rather than a scientific-content defect.

## Vertical warnings

Eighteen overfull vbox messages remained, almost all approximately 4.77391 pt. These occur with the mandated 9.000 in text height and IEEEtran's reported approximate 54-line column grid. They are not yet interpreted as publisher-facing clipping or a margin violation because page-level visual QA has not been performed on an attached exact PDF.

The 9.000 in TAES text height must not be changed merely to suppress these warnings without a separate geometry and page-level visual review.

## Page-count interpretation

The 18-page count remained unchanged from the first complete build. This is a real development-format observation, but it is not yet treated as the stable final page count because the remaining horizontal overflows have not been eliminated and the development PDF has not passed page-level visual QA.

No scientific content should be removed solely on the basis of the revision-2 page count. Mechanical layout defects must be addressed first, followed by a fresh page-count and visual audit.

## Next action

Use `TAES_BUILD_IEEETRAN_R3.py`, which preserves the exact visible code/identifier text while inserting explicit discretionary break opportunities after underscores and selected punctuation. Revision 3 must be evaluated before any substantive page-length editing is considered.
