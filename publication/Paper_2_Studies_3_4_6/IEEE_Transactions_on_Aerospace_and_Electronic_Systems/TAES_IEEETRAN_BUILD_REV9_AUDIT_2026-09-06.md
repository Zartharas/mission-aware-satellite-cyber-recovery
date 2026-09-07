# TAES IEEEtran Build Revision 9 Audit

**Audit date:** 2026-09-06  
**Venue:** IEEE Transactions on Aerospace and Electronic Systems  
**Build revision:** R9  
**Canonical manuscript tracking commit:** `710a72af05fb418a0d82a659198a677b9e2a8948`  
**Canonical manuscript SHA-256:** `802e6658e9e1325ec4f4a785c5da1b3856fbfadb950dadb6f6a57aec0acacd48`  
**Verdict:** `PASS_AUTOMATED_LAYOUT__VISUAL_QA_REQUIRED`

## 1. Purpose

Revision 9 is a generated-LaTeX-only typography correction applied to the canonically tracked Pass-2 R2 compressed manuscript. It addresses the single Study-3 primary-endpoints sentence that produced both horizontal overflows in R8.

No canonical Markdown prose, frozen study evidence, result, population, citation, table, figure, or TAES geometry value was changed.

## 2. R9 typography intervention

R9 preserves:

- revision-3 discretionary breaks inside simple monospaced identifiers;
- the 13 common-framework LaTeX math conversions;
- the three Study-6 localized emergency-stretch blocks that passed prior visual QA;
- zero use of `\sloppy`;
- the canonical Pass-2 R2 manuscript SHA.

R9 additionally formats only the six-endpoint list sentence as a local ragged-right block and suppresses the break immediately before the terminal `s` in `unsafe_qualified_exposure_s`. Normal IEEE justification resumes immediately in the following sentence.

## 3. Automated build result

- pages: 16
- estimated pages beyond 10: 6
- page size: 612 x 792 pt, US Letter
- text width: 7.100 in
- column gap: 0.200 in
- column width: 3.450 in
- text height: 9.000 in
- overfull hboxes: 0
- overfull vboxes: 16
- underfull hboxes: 28
- underfull vboxes: 1
- LaTeX warnings: 0
- fonts: 13
- all fonts embedded: PASS
- localized sloppy blocks: 0
- common-framework math conversions: 13
- endpoint ragged-right blocks: 1
- endpoint terminal-s break: SUPPRESSED
- preserved Study-6 emergency-stretch blocks: 3

The repeated approximately 4.77-pt vertical overfull condition is the same systematic geometry condition previously shown by full page-by-page visual QA not to cause clipping or margin intrusion. R9 still requires a new visual inspection because pagination changed from the previously approved 18-page R7 build to 16 pages.

## 4. Exact development-artifact hashes

- TeX SHA-256: `381e687bbdc1ccc409ed54bc189d2cfd31b846487bd7e2ae03cc105d0e720557`
- PDF SHA-256: `a7624fa416ebe4ba4d0b9e46da25b5dcb4d85e23e63291f4bdf497d5ba6cb319`
- log SHA-256: `5a85f848ccaf5274a8830624ef667b768f27dbe103e751597cd317a7b4e196d2`
- build-audit SHA-256: `c4c475d76bf90e548ee3e67621a6de36a02406cb5feac4960e3b6a04784001c6`

## 5. Editorial interpretation

The controlled Pass-2 R2 manuscript compression reduced the IEEEtran development layout from 18 pages to 16 pages. R9 removed the only horizontal-overflow blocker introduced by the compressed Study-3 endpoint sentence without further manuscript compression.

No additional length reduction is authorized or recommended before visual review of the exact 16-page R9 PDF. The next gate is full PDF visual QA, after which the 16-page endpoint can be accepted or a separate evidence-based decision can be made about whether one further page of editorial compression is scientifically worthwhile.

## 6. Submission state

- publisher-facing: NO
- PDF visual QA required: YES
- final author submission authorization: GRANTED on 2026-09-06
- effective portal submission authorization: PENDING remaining package gates
