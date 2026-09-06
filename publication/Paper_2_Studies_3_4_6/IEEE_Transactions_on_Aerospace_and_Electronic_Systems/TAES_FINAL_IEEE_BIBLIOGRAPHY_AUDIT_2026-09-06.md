# TAES Paper 2 Final IEEE Bibliography Audit

**Audit date:** 2026-09-06  
**Target:** IEEE Transactions on Aerospace and Electronic Systems  
**Scope:** References used by the tracked assembled development manuscript  
**Scientific-result changes authorized or required:** None  
**Verdict:** `PASS_BIBLIOGRAPHICALLY__CONTROLLED_CITATION_EDITS_REQUIRED__REASSEMBLY_REQUIRED_AFTER_APPLY`

## 1. IEEE reference-style basis

The current IEEE Reference Guide for Authors, version 3.28.2025, was reviewed from IEEE Author Center. The controls relevant to this manuscript are:

- references cited in text use bracketed numeric identifiers;
- reference ranges are written out individually rather than as dash ranges;
- one reference number must identify one reference only;
- conference references should include conference metadata and page numbers where available;
- arXiv preprints use author, title, year, and arXiv identifier;
- websites include an accessed date and URL;
- all references require at least a year or accessed date.

Official IEEE source:
https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/create-the-text-of-your-article/ieee-editorial-style-manual/

IEEE Reference Guide:
https://journals.ieeeauthorcenter.ieee.org/wp-content/uploads/sites/7/IEEE_Reference_Guide.pdf

## 2. Bibliographic findings

### Finding A: combined SLSA reference

The current manuscript reference [12] combines two distinct SLSA webpages, `Source: Requirements for producing source` and `Threats & mitigations`.

IEEE explicitly requires one reference per number. The two SLSA pages must therefore be separated:

- [12] SLSA Source Requirements;
- [13] SLSA Threats & Mitigations.

The source-requirements claim remains attached to [12]. The intentionally malicious producer limitation is supported by the threat-model page and is moved to [13].

### Finding B: citation range syntax

The manuscript currently contains dash-form numeric reference ranges such as `[10]-[12]` and `[1]-[4]`.

Current IEEE guidance requires these to be written out individually. They will be converted to forms such as `[10], [11], [12]` and `[1], [2], [3], [4]` without changing the cited source set or substantive claim.

### Finding C: incomplete metadata

Several bibliography entries were intentionally concise during drafting. The final bibliography pass adds authoritative metadata where verified:

- SpaceSec 2026 event name, San Diego location, event date, and DOI for Thummala, Rice, and Falco;
- IEEE Aerospace Conference location and pages 1-20 for Curbo and Falco;
- pages 1393-1410 and Santa Clara conference location for in-toto;
- publication month for Byzantine quorum systems;
- issue no. 3 and May 2024 publication month for Asymmetric distributed trust;
- current accessed dates and URLs for SPARTA, TUF, and SLSA.

### Finding D: TUF stable version now visible

The earlier source ledger remained version-neutral because the official page did not expose a stable version in the prior retrieval. The official TUF specification page now identifies `v1.0.33` as the latest stable specification. The bibliography may therefore identify TUF v1.0.33 without inference.

## 3. Authoritative source verification

The following authoritative or primary sources were reviewed on 2026-09-06:

1. NDSS SpaceSec landing page and official paper for `Why is Space Cybersecurity Unique?`
2. arXiv record `2608.14532`
3. 2025 IEEE Aerospace Conference metadata and DOI `10.1109/AERO63441.2025.11068629`
4. The Aerospace Corporation SPARTA site
5. RFC Editor RFC 9334
6. IETF Datatracker `draft-ietf-rats-multi-verifier-00`
7. bibliographic record for Malkhi and Reiter, DOI `10.1007/s004460050050`
8. Springer version-of-record page for Alpos, Cachin, Tackmann, and Zanolini, DOI `10.1007/s00446-024-00469-1`, corroborated for issue 3 by indexed bibliographic metadata
9. arXiv record `2603.23745`
10. USENIX Security 2019 record for in-toto
11. official TUF specification page
12. SLSA v1.2 Source Requirements
13. SLSA v1.2 Threats & Mitigations

No citation was added merely to increase reference count. No source was promoted from preprint or Internet-Draft status to peer-reviewed status.

## 4. Controlled final reference identities

The controlled bibliography after this pass contains 13 references:

1. Thummala, Rice, and Falco, SpaceSec 2026.
2. Vanlyssel et al., arXiv:2608.14532.
3. Curbo and Falco, 2025 IEEE Aerospace Conference.
4. The Aerospace Corporation, SPARTA.
5. Birkholz et al., RFC 9334.
6. Deshpande et al., IETF multi-verifier Internet-Draft.
7. Malkhi and Reiter, Byzantine quorum systems.
8. Alpos et al., Asymmetric distributed trust.
9. Rezabek, Malkhi, and Yahalom, arXiv:2603.23745.
10. Torres-Arias et al., in-toto, USENIX Security 2019.
11. The Update Framework Specification v1.0.33.
12. SLSA v1.2 Source Requirements.
13. SLSA v1.2 Threats & Mitigations.

## 5. Claim-to-source preservation

The controlled renumbering preserves the scientific claim map:

- [12] supports SLSA source and process assurance requirements;
- [13] supports the specific statement that intentionally malicious producers are not directly mitigated by SLSA controls and require an independent basis of trust.

No Study 3, Study 4, or Study 6 numerical result, endpoint, population, interpretation boundary, or novelty statement is changed by this bibliography pass.

## 6. Reassembly requirement

Because the bibliography and in-text citation identifiers are manuscript components, applying this audit changes the assembled manuscript bytes. The previously tracked assembled SHA-256 remains a valid historical identity for the pre-bibliography draft but is superseded after controlled reassembly.

The updated manuscript must pass:

- abstract word-count guard;
- no-em-dash guard;
- no combined Paper-2 population guard;
- no affirmative global-superiority guard;
- no dash-form numeric reference-range guard;
- sequential IEEE first-use order `1,2,...,13`;
- component SHA-256 regeneration.

This bibliography audit does not authorize TAES formatting, PDF freeze, or portal submission.