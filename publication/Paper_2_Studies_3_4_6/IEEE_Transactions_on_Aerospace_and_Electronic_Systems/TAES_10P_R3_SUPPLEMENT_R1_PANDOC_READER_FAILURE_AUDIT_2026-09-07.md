# TAES Paper 2 Short Track: Supplement R1 Pandoc Reader Failure Audit

Date: 2026-09-07
Branch: `paper2/taes-10-page-compression`

## Result

`FAIL_TOOLCHAIN_COMPATIBILITY_BEFORE_LATEX`

The first supplementary-PDF builder, `TAES_BUILD_10P_SUPPLEMENT_R1.py`, stopped before TeX materialization or LaTeX compilation because the installed Pandoc rejected the requested reader specification:

```text
The extension 'raw_tex' is not supported for gfm.
Use --list-extensions=gfm to list supported extensions.
ERROR: command failed (23): pandoc ... --from=gfm+raw_tex --to=latex --wrap=none
```

## Scope of failure

The failure occurred inside `pandoc_body()` before `OUT_TEX.write_text(...)`. Therefore no R1 supplementary TeX, PDF, log, or build-audit artifact was produced by this attempt.

The failure is a Pandoc reader-option incompatibility only. It does not indicate a defect in the supplementary Markdown, the frozen study results, the R8 main article, the supplementary Figure S1 asset, or the R9 fallback.

## Protected identities observed after failure

- R8 main article PDF SHA-256: `f34cd280371f73492f6ef746fd52279fb1ab01fa4ce8c38eedb8aa67a74f551b`
- R3 supplementary Markdown SHA-256: `e6313fca178f9de40a6b7c28468be6b20ae1fc7249c2e3c8e30ca5fbf0d7027c`
- R3 supplementary README SHA-256: `b7603d36ba2b9297b970dcad0138fbb9faadae4d8be946e4f05ebb6bdb6609c5`
- Supplementary Fig. S1 PNG expected SHA-256: `7d22964bdae052b35b4680e1b09f3209f1c99bb1d157a0f995dcd2a6445e6698`
- frozen 16-page R9 fallback PDF SHA-256: `a7624fa416ebe4ba4d0b9e46da25b5dcb4d85e23e63291f4bdf497d5ba6cb319`

The paired R8 main article remained 8 pages, US Letter.

## Corrective strategy

Do not change the supplementary Markdown or switch its Markdown dialect merely to satisfy the raw-TeX extension request. The R2 builder should retain the `gfm` reader, temporarily replace only the generated raw-LaTeX Fig. S1 include block with a neutral placeholder, convert the Markdown with `--from=gfm`, then replace exactly one placeholder in the generated LaTeX with the exact Fig. S1 include block.

This correction is build-pipeline-only and preserves GFM pipe-table behavior.

## Scientific controls

- supplement content changed: `NO`
- main article changed: `NO`
- science files changed: `NONE`
- study rerun: `NO`
- publisher-facing package changed: `NO`
- merge to `main`: `NOT_AUTHORIZED_UNTIL_QA_PASS`
