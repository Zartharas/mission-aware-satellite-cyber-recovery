# TAES IEEEtran Development Build Failure 1 Audit

**Audit date:** 2026-09-06  
**Target:** IEEE Transactions on Aerospace and Electronic Systems  
**Canonical manuscript commit:** `a0567d9d8245ed1b543f4a55ddaa6563789977f2`  
**Canonical manuscript SHA-256:** `0381d6f60f5721ef2fb1ce3e0bce4e26133ad56cb2d123dfddfa24c2ab35f882`  
**Builder base commit:** `266c7e62c4b02e2c0431954067e5da497a500ada`  
**Scientific rerun or manuscript-content change required:** No

## Outcome

The first deterministic IEEEtran development build did not produce a PDF.

The failure occurred during PDFLaTeX font resolution after the generated TeX had already confirmed:

- IEEEtran 10-point journal mode;
- US Letter paper;
- text width `513.11743 pt` (7.10 in);
- column separation `14.45377 pt` (0.20 in);
- column width `249.33183 pt` (3.45 in);
- text height `650.43 pt` (9.00 in).

## Root cause

The generated manuscript uses `\texttt{...}` for controlled manuscript identifiers. Under the IEEEtran/Times font configuration, the typewriter family resolves to Courier. The BasicTeX installation did not contain Courier metric `pcrr7t.tfm`, and PDFLaTeX terminated with:

`Font OT1/pcr/m/n/10=pcrr7t ... Metric (TFM) file not found.`

The failure first surfaced at the manuscript identifier `APPROVED_BAD_SOURCE` but is a TeX environment dependency, not a problem with that scientific term.

CTAN identifies Courier as a TeX Live package named `courier`.

## Required remediation

Install the missing TeX Live Courier package through the existing TeX Live manager, verify that `kpsewhich pcrr7t.tfm` resolves, and rerun the unchanged deterministic builder.

No manual edit of the generated `.tex` file is authorized or needed.

## Provisional layout messages

The incomplete run emitted two `Overfull \vbox (4.77391pt too high)` messages and one `Underfull \vbox` message before the font failure. These are not accepted as final format-audit findings because the document did not compile to completion. They must be reassessed from the complete log after a successful build.

## Gate status

`BUILD_BLOCKED_BY_MISSING_TEX_FONT_DEPENDENCY__NO_PDF_CREATED__SCIENCE_UNCHANGED`

No publisher-facing file was created and no submission authorization is implied.
