# CEAS R5 reference verification ledger — 2026-10-09

Preserves the **original 20-entry** reference screen and its mapping to the **19-entry edited R5**. Evidence levels are explicitly listed; a resolved URL is **not** complete bibliographic verification. Original automated retraction screen reported zero results, but no independent current retraction check is claimed.

| Original | Current | Evidence/remaining caveat | Link |
|---:|---:|---|---|
| 1 | 1 | NDSS original proceedings, title/authors/DOI checked | https://www.ndss-symposium.org/ndss-paper/auto-draft-645/ |
| 2 | 2 | arXiv 2608.14532 indexed with five named authors; preprint | https://arxiv.org/abs/2608.14532 |
| 3 | 3 | Authors/title/2025 IEEE Aerospace Conference and DOI independently corroborated by author publication record, author-posted paper and proceedings table of contents; publisher-primary metadata/pagination check still required | https://curbo.space/publications/ |
| 4 | 4 | official SPARTA CM0044 item checked | https://sparta.aerospace.org/countermeasures/CM0044 |
| 5 | 5 | RFC Editor primary source, informational RFC 9334, DOI and author order verified | https://www.rfc-editor.org/info/rfc9334/ |
| 6 | removed | IETF Internet-Draft, May 5 2026; not finalized, publication reference removed | https://datatracker.ietf.org/doc/html/draft-ietf-rats-multi-verifier-00 |
| 7 | 6 | Author-hosted published journal PDF confirms Malkhi/Reiter, *Distributed Computing* 11, 203–213 (1998); DOI/title/issue independently corroborated by Reiter's publication list and Duke bibliographic record | https://doi.org/10.1007/s004460050050 |
| 8 | 7 | Springer publisher article independently rechecked: Alpos/Cachin/Tackmann/Zanolini, published online 28 May 2024, volume 37 pp. 247–277 (2024), DOI matches | https://link.springer.com/article/10.1007/s00446-024-00469-1 |
| 9 | 8 | arXiv 2603.23745 three authors verified via dblp; preprint | https://arxiv.org/abs/2603.23745 |
| 10 | 9 | USENIX primary: five authors, venue, 2019 pages 1393–1410 | https://www.usenix.org/conference/usenixsecurity19/presentation/torres-arias |
| 11 | 10 | TUF official v1.0.36 text identifies last-modified 5 Aug 2026; upstream specification GitHub Release v1.0.36 shows publication 10 Aug 2026; R5 reference uses release date, now corroborated | https://theupdateframework.github.io/specification/v1.0.36/ |
| 12 | 11 | SLSA v1.2 official source requirements | https://slsa.dev/spec/v1.2/source-requirements |
| 13 | 12 | SLSA v1.2 official Threats & mitigations page; heuristic title mismatch false alarm | https://slsa.dev/spec/v1.2/threats |
| 14 | 13 | ESA Zenodo v2 April 2025 DOI and authors verified; reuse/access check remains | https://zenodo.org/records/15237121 |
| 15 | 14 | arXiv preprint 2603.10388 verified; IEEE DOI and published pagination unresolved | https://arxiv.org/abs/2603.10388 |
| 16 | 15 | IEEE Xplore 27(1) pp 372–425, DOI verified | https://ieeexplore.ieee.org/abstract/document/10546924/authors |
| 17 | 16 | Aerospace 13(3) article 249 DOI verified via publisher | https://doi.org/10.3390/aerospace13030249 |
| 18 | 17 | NIST IR 8270 2023 authors/DOI verified | https://www.nist.gov/publications/introduction-cybersecurity-commercial-satellite-operations |
| 19 | 18 | SciTePress original conference vol 2 pages 133–140 DOI verified | https://www.scitepress.org/PublishedPapers/2025/131032/ |
| 20 | 19 | NASA Rev B primary PDF January 19 2024 verified | https://swehb.nasa.gov/spaces/SWEHBVD/pages/146540183/7.22+-+Space+Security+Best+Practices+Guide |

## Open gates

Confirm original [3] publisher-primary pagination and original [15] IEEE publisher bibliographic metadata; original [7] author/publisher-concordant reference and original [11] TUF version-release date now cross-checked; complete final 19-reference formatting and claim-support verification, including original [13] SLSA official content. Verify ESA data licensing and precise access for frozen and ignored artifacts. Preserve original R4 and TAES R10 unchanged. Do not record `bibliography_final_pass` until this work is completed.

## 2026-10-09 additional primary-source reconciliation (editorial only)

- **Current [6]** (original [7]): Author-hosted full published *Distributed Computing* paper (1998), and Michael Reiter's original publication record, confirm authors, title, 11(4), pages 203–213, and DOI 10.1007/s004460050050. This is a bibliographic cross-check only; Study-4 results and their trust assumptions are unchanged. Sources: https://users.ece.cmu.edu/~reiter/papers/1998/DC.pdf and https://reitermk.github.io/papers/byYear.html
- **Current [7]** (original [8]): Publisher record confirms 28 May 2024 online publication, volume 37, pages 247–277, and named authors. Source: https://link.springer.com/article/10.1007/s00446-024-00469-1
- **Current [10]** (original [11]): Versioned TUF official source header says last modified 5 August 2026, whereas upstream signed GitHub release v1.0.36 is dated 10 August 2026; the manuscript's **Aug. 10, 2026 release date is supported**. Sources: https://theupdateframework.github.io/specification/v1.0.36/ and https://github.com/theupdateframework/specification/releases
- **Current [3]** (original [3]): IEEE Aerospace Conference 2025 paper's authors/title/DOI independently corroborated by Curbo's publication list, author-posted full paper, ResearchGate DOI metadata and publisher proceedings table of contents. Still withhold full bibliographic completion until IEEE primary record/pagination are checked. Sources: https://curbo.space/publications/ , https://www.researchgate.net/publication/388733648_Testable_Cyber_Requirements_for_Space_Flight_Software , https://www.proceedings.com/content/081/081100webtoc.pdf

**Submission gate remains CLOSED:** these spot checks do not amount to all nineteen references' claim-to-source verification, retraction screening, DOI/style validation, source-license confirmation, or reviewer-access QA. Do not change original 20-entry screening counts or mark manual QA complete. No P2X reuse or study result mutation.
