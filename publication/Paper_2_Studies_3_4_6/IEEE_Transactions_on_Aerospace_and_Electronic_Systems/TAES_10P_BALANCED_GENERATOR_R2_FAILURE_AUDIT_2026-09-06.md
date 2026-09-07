# TAES Paper 2 Balanced Short-Track Generator R2 Failure Audit

Date: 2026-09-06
Branch: `paper2/taes-10-page-compression`

## Result

`FAIL_SAFE__STRING_ANCHOR_MISMATCH__NO_R2_CANDIDATE_WRITTEN`

The balanced short-track R2 generator recreated and verified the deterministic six-page R1 development candidate, then stopped before writing any R2 output because the Study-3 restoration anchor expected the sentence `Expanded endpoints and timing details appear in Supplementary Appendix A.` to begin after a blank-line paragraph boundary. In the deterministic R1 source, that sentence is the final sentence of the preceding paragraph, so the registered anchor with a leading `\n\n` had zero matches.

## Scientific and package impact

- Frozen R9 canonical manuscript changed: **NO**.
- Frozen 16-page publisher-facing PDF changed: **NO**.
- Frozen R9 PDF SHA-256 remained `a7624fa416ebe4ba4d0b9e46da25b5dcb4d85e23e63291f4bdf497d5ba6cb319`.
- R1 short-main source changed: **NO**.
- R1 short-main SHA-256 remained `5926d116acc877859545bd5e0e2829132894de5298d7ff3e3cd6123b4665cbd1`.
- R1 supplementary material changed: **NO**.
- R1 supplementary SHA-256 remained `e6313fca178f9de40a6b7c28468be6b20ae1fc7249c2e3c8e30ca5fbf0d7027c`.
- Study 3, Study 4, or Study 6 rerun: **NO**.
- Partial balanced candidate written: **NO**.
- Publisher-facing status: **NO**.

## Root cause

The failed R2 anchor was:

```text
\n\nExpanded endpoints and timing details appear in Supplementary Appendix A.
```

The deterministic R1 candidate instead contains that text as the final sentence of the existing Study-3 paragraph. The sentence itself is present; only the assumed paragraph-boundary prefix is absent.

The remaining seven restoration anchors were reviewed against the deterministic R1 template and remain structurally valid.

## Corrective action

Preserve R2 as failed history. Create a new R3 generator that keeps all R2 restored prose unchanged and changes only the Study-3 insertion logic so it anchors on the exact sentence text without requiring a pre-existing blank-line boundary. The corrected insertion will place the restored Study-3 detail in its own paragraph before the existing supplementary-reference sentence.

No merge to `main`, publisher-facing freeze, or portal continuation is authorized until the balanced candidate compiles and completes scientific and visual QA.
