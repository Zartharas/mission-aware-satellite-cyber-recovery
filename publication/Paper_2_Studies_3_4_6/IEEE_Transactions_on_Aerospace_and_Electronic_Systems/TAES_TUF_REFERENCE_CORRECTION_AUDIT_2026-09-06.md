# TAES Paper 2 TUF Reference Correction Audit

**Audit date:** 2026-09-06  
**Target:** IEEE Transactions on Aerospace and Electronic Systems  
**Scope:** Bibliographic metadata for reference [11] only  
**Scientific-result changes authorized or required:** None  
**Verdict:** `CORRECTION_REQUIRED_BEFORE_FORMATTED_PDF_BUILD`

## 1. Reason for follow-up correction

The earlier bibliography audit relied on the public TUF website specification index, which still displayed v1.0.33 as its latest listed version during the September 6, 2026 review. A later authoritative-source cross-check found that the official `theupdateframework/specification` repository had subsequently released v1.0.34, v1.0.35, and v1.0.36, with v1.0.36 marked as the latest release.

The specification repository states that its `master` branch tracks the latest stable specification and that releases are tagged after updates to `master`. The v1.0.36 release record is therefore the stronger current authority for the stable-version identity even though the project website index is lagging.

## 2. Controlled correction

Reference [11] must change from:

`The Update Framework Specification, v1.0.33`

with the lagging website index URL to:

`The Update Framework Specification, v1.0.36`

using the official project release record:

https://github.com/theupdateframework/specification/releases/tag/v1.0.36

The v1.0.36 release is dated August 10, 2026 in the official release history.

## 3. Scientific impact

This is a bibliographic metadata correction only. It does not change:

- any Study 3, Study 4, or Study 6 result;
- the description of TUF mechanisms used as prior art;
- any endpoint, population, state, gate, threshold, or interpretation;
- the manuscript's novelty boundary;
- the reference numbering or first-use order.

Reference [11] remains the TUF source and retains the same in-text citation identity.

## 4. Historical record

The earlier bibliography audit is retained as historical evidence of what was reviewed at that stage. This follow-up audit supersedes only its TUF stable-version conclusion. Repository history must not be rewritten.

## 5. Gate effect

The formatted IEEEtran PDF must not be frozen from a manuscript that still cites TUF v1.0.33. The correction must be applied to the live manuscript source, the living literature ledger, and any rerunnable bibliography helper before reassembly and formatting.
