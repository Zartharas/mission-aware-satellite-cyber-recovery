# TAES Paper 2 short-track R7 typography PASS audit

Date: 2026-09-06
Branch: `paper2/taes-10-page-compression`

## Status

`PASS_FINAL_SHORT_TRACK_TYPOGRAPHY__VISUAL_QA_PENDING`

## Bound source and protected artifacts

- Balanced R3 manuscript SHA-256: `7fa44eb55255bc7532a01728ab039b5e98fb3c719058f62440310e430b5f7909`
- Supplement SHA-256: `e6313fca178f9de40a6b7c28468be6b20ae1fc7249c2e3c8e30ca5fbf0d7027c`
- Frozen R9 16-page fallback PDF SHA-256: `a7624fa416ebe4ba4d0b9e46da25b5dcb4d85e23e63291f4bdf497d5ba6cb319`
- Balanced R3 words including references: `5625`

## R7 build result

- Pages: `8`
- Estimated pages over 10: `0`
- Page-target decision: `PREFERRED_BUFFER_TARGET`
- Page size: `612 x 792 pts (letter)`
- Text width: `7.100 in`
- Column gap: `0.200 in`
- Column width: `3.450 in`
- Text height: `9.000 in`
- Overfull hboxes: `0`
- Overfull vboxes: `8`
- Underfull hboxes: `8`
- Underfull vboxes: `0`
- LaTeX warnings: `0`
- Font count: `8`
- All fonts embedded: `PASS`
- Horizontal overflow gate: `PASS`

## R7 generated-LaTeX-only typography controls

- Breakable monospaced identifiers: `166`
- Pre-existing `\raggedright` count: `4`
- Final `\raggedright` count: `5`
- Added localized `\raggedright` blocks: `1`
- Added scope: first Study-6 state-definition paragraph only
- Guard: structural wrapper plus one `\raggedright` delta
- Localized `\sloppy` blocks: `0`
- Forced `\linebreak[2]` or `\linebreak[4]` hints: `0`
- Global geometry changed: `NO`
- Manuscript source changed: `NO`
- Supplement content changed: `NO`
- Science files changed: `NONE`
- Study rerun: `NO`
- Publisher-facing: `NO`

## Development artifact identities

- TeX SHA-256: `648dcd1e0af0468ed555a2bc2f19306fe755f30d7eefc303072058ebb08e636d`
- PDF SHA-256: `0c0cebd98723b0e501d7ea7f2c405e7504b217d1a4655e9bacfbadd7cd18e905`
- Log SHA-256: `38cad18dfdbdab7027c664018f1c8e52f708650495d56b6e9888c48453605ba7`
- Build-audit SHA-256: `7f262920350128d8ad966d3fbcf66dd075fecbc6ecdce337d0fa449fcc3cda4c`

## Decision

Typography work is complete. No further manuscript, content, or generated-LaTeX changes are authorized unless visual QA identifies a concrete defect. The exact development PDF with SHA-256 `0c0cebd98723b0e501d7ea7f2c405e7504b217d1a4655e9bacfbadd7cd18e905` is the sole candidate for the next full eight-page visual-QA gate.

The short-track package remains unmerged and non-publisher-facing until visual QA, supplementary-PDF build/QA, scientific-preservation proof, and package-freeze gates pass.
