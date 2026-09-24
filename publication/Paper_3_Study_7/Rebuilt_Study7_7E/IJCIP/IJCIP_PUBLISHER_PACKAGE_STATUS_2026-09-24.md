# Paper 3 — IJCIP Publisher-Facing Package Status

**Package ID:** `PAPER3-S7-S7E-IJCIP-PUBLISHER-PACKAGE-001`  
**Date:** 2026-09-24  
**Basis manuscript:** `PAPER3_IJCIP_MANUSCRIPT_R3.md`  
**Basis branch head:** `f5c5bac572fcbb0e3f3439d4cb072a2d244e15e3`  
**Repository CI:** `Validate research configurations` run `36007175600` = **SUCCESS**  
**State:** `PACKAGE_RENDERED_AND_VERIFIED__PR168_UNMERGED__SUBMISSION_NOT_AUTHORIZED`

## Generated publisher-facing files

The following files were generated outside repository history for upload preparation:

- `PAPER3_IJCIP_MANUSCRIPT_R3.docx`
- `PAPER3_IJCIP_MANUSCRIPT_R3.pdf`
- `PAPER3_IJCIP_TITLE_PAGE.docx`
- `PAPER3_IJCIP_HIGHLIGHTS.docx`
- `PAPER3_IJCIP_COVER_LETTER.docx`

A ZIP package containing the upload-ready files and checksum manifest was also produced:

- `PAPER3_IJCIP_SUBMISSION_PACKAGE.zip`

## Render and content verification

DOCX visual QA:

- manuscript pages rendered: 18;
- title page: 1;
- highlights: 1;
- cover letter: 1;
- all rendered pages inspected for clipping, overlap, table breakage, missing glyphs, and footer/header issues;
- result: **PASS**.

PDF preflight:

- pages: 18;
- encrypted: false;
- openable: true;
- scanned-only: false;
- XFA: false;
- independent PDF render: 18 pages;
- result: **PASS**.

Content invariants confirmed in the publisher DOCX:

- Study 7 population = 1,033;
- Study 7E held-out population = 196 scenarios / 784 decisions;
- aggregate D0/L0/D1/L1 counts retained;
- D0/L0 disagreement = 67/196;
- D1/L1 disagreement = 72/196;
- F12 adverse-transfer finding retained;
- C0 all-HOLD zero-error control retained;
- no global policy ranking;
- AI disclosure present;
- six keywords;
- five highlights, each <=85 characters.

## SHA-256

```text
ffcafd58e44f49ff163507bf275c32b184c77fb2e6530c0cf3348bb9e72a8fda  PAPER3_IJCIP_COVER_LETTER.docx
dea4a1b2cfb08940837a5e7fa399144da6a430d3414d36dc7740d0628841b4ae  PAPER3_IJCIP_HIGHLIGHTS.docx
1affb34d08093289b82ece8afdde0e4ac37d8002fbbf3b09dd5a2684267f12d3  PAPER3_IJCIP_MANUSCRIPT_R3.docx
6cb63d7cee0cd656d58744c0d2c12a4c75a085c353dbfb40aa707929af290932  PAPER3_IJCIP_MANUSCRIPT_R3.pdf
13c3a6720ed328dc923857408a86d6b77cd75684a7957100726d12dcfc13c978  PAPER3_IJCIP_TITLE_PAGE.docx
```

## Governance

This package-generation phase does **not** authorize:

- PR #168 merge;
- opening or completing a publisher submission on the author's behalf;
- pressing final Submit;
- changing frozen Study 7 or Study 7E science.

The remaining gate is the live IJCIP submission-portal field check and explicit author submission authorization.
