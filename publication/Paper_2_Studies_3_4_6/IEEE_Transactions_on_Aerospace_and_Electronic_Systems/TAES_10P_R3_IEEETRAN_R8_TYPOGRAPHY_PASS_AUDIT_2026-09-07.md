# TAES 10-page short track: R8 typography pass audit

Date: 2026-09-07
Branch: `paper2/taes-10-page-compression`

## Status

`PASS_R8_TYPOGRAPHY_READY_FOR_FINAL_VISUAL_QA`

The unchanged R8 builder compiled successfully after restoring the existing MacTeX path `/Library/TeX/texbin` to the shell `PATH`. No TeX installation or manuscript-content change was required.

## Locked source identities

- Balanced R3 manuscript SHA-256: `7fa44eb55255bc7532a01728ab039b5e98fb3c719058f62440310e430b5f7909`
- Supplement SHA-256: `e6313fca178f9de40a6b7c28468be6b20ae1fc7249c2e3c8e30ca5fbf0d7027c`
- Frozen 16-page R9 fallback PDF SHA-256: `a7624fa416ebe4ba4d0b9e46da25b5dcb4d85e23e63291f4bdf497d5ba6cb319`

## R8 development build identities

- TeX SHA-256: `ac2ede2cae38ecf64f58b4b0f82f4c984f8320f171f780a8e2f83ba85652a93d`
- PDF SHA-256: `f34cd280371f73492f6ef746fd52279fb1ab01fa4ce8c38eedb8aa67a74f551b`
- Log SHA-256: `bd93e23365887312f541bdc27361788aa5536390ad58f569229599bb1fb1ede8`
- Build-audit SHA-256: `8f94db91f86175c1445304d81eff4981dc81bd4b6a7f2a9255ebb9b2907a2781`

## Mechanical layout result

- Pages: `8`
- Estimated pages over 10: `0`
- Page target decision: `PREFERRED_BUFFER_TARGET`
- Page size: US Letter, 612 x 792 pt
- Text width: 7.100 in
- Column separation: 0.200 in
- Column width: 3.450 in
- Text height: 9.000 in
- Overfull hboxes: `0`
- Overfull vboxes: `8`
- Underfull hboxes: `13`
- Underfull vboxes: `0`
- LaTeX warnings: `0`
- Fonts: `8`, all embedded

## Study-6 localized treatment

R8 replaces the visually inconsistent R7 localized `\raggedright` treatment with one localized, fully justified `\emergencystretch=2em` group on the first Study-6 state-definition paragraph only.

- Breakable code tokens: `166`
- Pre-existing `\raggedright` count: `4`
- Final `\raggedright` count: `4`
- Localized `\emergencystretch` blocks: `1`
- Value: `2em`
- Added localized `\raggedright` blocks: `0`
- Localized `\sloppy` blocks: `0`
- Forced `\linebreak` hints: `0`
- Global geometry changed: `NO`

## Scientific and package controls

- Manuscript source changed: `NO`
- Supplement content changed: `NO`
- Science files changed: `NONE`
- Study rerun: `NO`
- Publisher-facing artifact: `NO`
- Merge to main: `NOT AUTHORIZED UNTIL QA PASS`

## Next gate

The exact R8 PDF with SHA-256 `f34cd280371f73492f6ef746fd52279fb1ab01fa4ce8c38eedb8aa67a74f551b` is the candidate for final eight-page visual QA. Special attention should be given to the first Study-6 paragraph on page 5 to confirm that justification is visually consistent with surrounding IEEE body text.
