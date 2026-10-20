# Paper 3 — IJCIP R3 manual source and citation-order audit (2026-10-20)

**Authoritative source:** Study 7/7E manuscript in draft PR #223; no change to scientific results or hypotheses. Review of 24 references, ordered by first in-text citation. The original reference IDs are preserved in the mapping below.

## DOI/title validation

A scholarly identifier batch screening of 24 entries returned 16 machine matches, 1 ambiguous and 7 not found. **Those verdicts must not be treated as a 16/24 bibliography pass rate**: the service uses fuzzy work matching when no DOI is provided, and wrongly associated some institutional/agency titles with unrelated publications. We therefore separate identifier-backed scholarly claims from primary-agency URLs.

- DOI/identifier-backed title screening showed no identified title/DOI mismatch and no retraction flag in the screened set. This is database screening, not exhaustive publisher metadata verification.
- Scholarly items [2], [4]–[7], [14]–[21] include DOI, arXiv, or NASA/publisher source identifiers; title matching was checked where available. The arXiv record remains labeled a preprint. (These are *old* R3 indices; use mapping below for the publication numbering.)
- [3] NASA learning-enabled assurance report was manually located at https://ntrs.nasa.gov/citations/20240006865.
- [8] PMLR safety-certification paper was manually located at https://proceedings.mlr.press/v267/jing25b.html.
- [1] SPARTA countermeasure CM0044 was independently located from SPARTA's own current countermeasure index/search, https://sparta.aerospace.org/countermeasures/CM0044.
- [9]–[13] were checked against their exact NASA Software Catalog landing pages: GSC-18719-1, GSC-18128-1, GSC-18476-1, GSC-16917-1, GSC-17737-1. Their NASA catalog titles can have longer version qualifiers; do not infer all NASA software releases equal the pinned Study 7E runtime.
- [22] 2021 Space Priorities Framework original White House URL currently returned HTTP 404. **Corrected only its reference URL** to the US Government Publishing Office preserved bibliographic record https://www.govinfo.gov/app/details/GOVPUB-PREX23-PURL-gpo193490. Historical policy (2021) is cited as historical context, not as a statement of current presidential policy.
- [23] CISA official Communications Systems text was available in search indexing, confirming satellite listed among communications infrastructure and the identified infrastructure dependencies; direct live fetch gave 403. Link preserved without claiming HTTP retrieval success.
- [24] Office of Space Commerce historical SPD-5 article was directly accessible at https://space.commerce.gov/president-signs-space-cybersecurity-policy-directive/.

**Unresolved source QA:** a final human metadata/format pass should check author spellings, journal LTWA abbreviations and vol/pages against each publisher; check the current SPARTA revision date against the historically cited application; verify any public-code/dataset rights before release. We do not assert every institutional URL passed direct HTTP testing.

## Citation-order correction

All 24 bibliography entries were cited, but previously occurred in the nonsequential in-text order `1,22,23,24,2,4,5,6,3,7,8,14,15,16,17,18,19,20,21,9,10,11,12,13`. This is corrected deterministically across prose, numeric ranges and the numbered bibliography. Text-only renumbering is not a new citation/source or a new empirical result. Two numeric ranges were preserved as ranges.

| Original R3 reference | Publication reference | Item / source identity |
|---:|---:|---|
| 1 | 1 | Space Attack Research and Tactic Analysis (SPARTA), "Cyber-safe Mode," Counter |
| 22 | 2 | Executive Office of the President, *United States Space Priorities Framework*, |
| 23 | 3 | Cybersecurity and Infrastructure Security Agency, "Communications Systems," In |
| 24 | 4 | U.S |
| 2 | 5 | A |
| 4 | 6 | B |
| 5 | 7 | A |
| 6 | 8 | N |
| 3 | 9 | A |
| 7 | 10 | H |
| 8 | 11 | H |
| 14 | 12 | J |
| 15 | 13 | R |
| 16 | 14 | J |
| 17 | 15 | S |
| 18 | 16 | F |
| 19 | 17 | M |
| 20 | 18 | O |
| 21 | 19 | D |
| 9 | 20 | NASA Goddard Space Flight Center, "Core Flight System (cFS)," NASA Software Ca |
| 10 | 21 | NASA Goddard Space Flight Center, "Core Flight Executive Version 6.7," NASA So |
| 11 | 22 | NASA Goddard Space Flight Center, "Health and Safety (HS)," NASA Software Cata |
| 12 | 23 | NASA Goddard Space Flight Center, "Software Bus Network (SBN)," NASA Software  |
| 13 | 24 | NASA, "NASA Operational Simulator for Small Satellites (NOS3)," NASA Software  |

The following are mandatory release checks: exactly 24 unique reference items; every bibliography item cited; first appearance 1–24; valid reference ranges; no invented DOI; unmodified quoted scientific text and frozen endpoint tables; only one changed URL (government archive substitution).

## Submission readiness status

The manuscript is **scientifically frozen**, and the citation-order/link correction is prepared on the draft PR. It remains **NOT FINAL SUBMISSION READY** until IJCIP's inaccessible journal-specific Guide and portal are confirmed, the vector figures are visually inspected, an editable DOCX/LaTeX source is generated and independently checked, the author reconfirms metadata and declarations, and source/figure artifact checksum QA is completed. No publishing/merging is authorized by this record.
