# WP11 Responsible Release Preparation Closeout

**Date:** 2026-08-30
**Status:** `COMPLETE_RELEASE_PREPARATION_ARCHIVE_PUBLICATION_PENDING`
**Repository merge commit:** `eb3be7aaaed9e60c54843d9a7b9ace1a0fa5812e`
**Repository tree:** `ea01c0ad638255409f8ac39bef53dd5bf9ef4ee8`
**Archive target:** Zenodo
**Zenodo upload performed:** `false`
**Zenodo publication performed:** `false`
**DOI assigned:** `false`

## Scope

WP11 responsible release preparation is complete for the exact local
six-object candidate generated from the reviewed and merged WP11 repository
state.

This closeout records local preparation, deterministic packaging, independent
audit, responsible-release review, and publication disposition. It does not
claim that a Zenodo record has been created, uploaded, published, or assigned
a DOI.

Actual archive publication remains a separate authenticated external action.

## Reviewed repository state

WP11 release tooling and governance were merged through PR #52.

- reviewed feature head:
  `60175dfb291ed4aca0a45bfc3d5ac329c9d02928`
- merge commit:
  `eb3be7aaaed9e60c54843d9a7b9ace1a0fa5812e`
- merged tree:
  `ea01c0ad638255409f8ac39bef53dd5bf9ef4ee8`
- reviewed WP11 PR scope:
  exactly 7 added files
- Codex findings:
  6 substantive findings identified, fixed, regression-tested, replied to,
  and resolved
- final additional Codex review:
  unavailable because the code-review usage quota was reached; no automated
  PASS was claimed for that unavailable review

The scientific campaign and WP10 manuscript claims were not changed by WP11.

## Exact release candidate

Candidate directory name:

`WP11_RELEASE_CANDIDATE_eb3be7a`

The candidate contains exactly six top-level regular files.

| Object | SHA-256 |
|---|---|
| `01-wp9-campaign-raw.tar.gz` | `c6d559b1c213e6f076a2cee2c1b79a88ba6838afc9a15754f045a1f6587d15bf` |
| `02-wp9-integrity-freeze.tar.gz` | `3256091e0857da00e36c4fe254c6dd28ade5a71a8a80c63156ac7d48ed627b94` |
| `03-publication-and-provenance.tar.gz` | `83a1096907454b45612fd8a825017d35172115ae3c4b0e4db2b6a44e5144d27b` |
| `README_RELEASE.txt` | `9868fc35e860c1979a219485f4e6780bf7f0b9b806108baa1a76967283130745` |
| `RELEASE_CHECKSUMS.sha256` | `c0697caded6768b3a30c555e3cc13a628792b9b69a0d3504bc2508c981f27613` |
| `RELEASE_MANIFEST.json` | `4c91b03c6682f74c39446b95cbcf5b29635f855897fd1ae68fa467d264253e04` |

Candidate total:

- top-level objects: `6`
- total bytes: `11162927`
- raw campaign archive source files: `17182`
- integrity-freeze archive source files: `16`
- publication/provenance archive source files: `68`

## Frozen scientific identities preserved

Packaging and all subsequent reviews preserved:

- authoritative ledger SHA-256:
  `92893a2fd8746f410bffd4dca5101bc3f533ada2ff82f98681788cf0c24ce6fd`
- deterministic campaign-tree SHA-256:
  `ad1e127b4431b6b334955129fcba82f76b18e5b43585395ac8c37300cac087b1`
- valid-analysis membership SHA-256:
  `a2bf0c8f352f4386e74a500d97ea8f73e0c39d03bfe10ac0ebcf02470af9f70e`
- integrity-freeze checksum-file SHA-256:
  `696bc615c1f227320aced30c1c88f4664f62def0cfbb454209e6068785e2d819`
- ledger records:
  `729 = 720 VALID + 9 INVALID`
- campaign source files:
  `17182`

No campaign runtime was performed and no frozen campaign evidence was
modified during WP11.

## Automated release audit

Local audit report SHA-256:

`bdd8c7edf075c3662f9c1e6c6741682900d00c399740cb6eb66882427a86355a`

Audit status:

`PASS`

The independent audit verified:

- exact six-object release set;
- complete release checksum target set;
- manifest/archive metadata identity;
- recomputed raw campaign archive identity;
- reconstructed authoritative ledger identity;
- integrity-freeze archive identity;
- zero unsafe archive members;
- zero duplicate archive members;
- zero sensitive filename candidates;
- zero high-confidence secret candidates;
- zero forbidden publication/provenance paths;
- Zenodo default file-count gate PASS;
- Zenodo default size gate PASS;
- candidate unchanged by audit.

## Manual responsible-release evidence

Manual review evidence SHA-256:

`c330add5a4d9295c820bd90054942f55d904d8cc9e3867218ba844dd658fa94b`

Targeted manual review SHA-256:

`5ebe145bc59c53131df0d746456b04b8810644ab697f072e9f64af34623a6ca7`

The targeted review covered all `739` members initially omitted from the
manual text-suffix scan.

Results:

- all 739 were text-like;
- high-confidence secret findings: `0`;
- email-bearing members: `0`;
- human-subject-bearing members: `0`;
- operational-term-bearing members: `0`;
- globally routable IPv4 addresses: `0`;
- unresolved copyright/license/proprietary markers in those 739 members: `0`.

Observed network values were limited to the non-public/non-routable
laboratory values:

- `0.0.0.0`
- `127.0.0.1`
- `172.19.0.22`
- `172.19.0.24`
- `172.19.0.26`

`0.0.0.0` is an unspecified/non-routable address.

## Rights, privacy, and misuse decision

Completed review record SHA-256:

`bf872b6ac9c153a65e709b959cba5ebe548fd5313e467bf40d7d02068acfc047`

Access decision:

`PUBLIC_FILES`

Final responsible-release decision:

`APPROVED_FOR_PUBLICATION`

This approval applies only to the exact six-object candidate identified
above.

Any byte change to the candidate invalidates the audit/review binding and
requires a fresh audit and responsible-release review.

The approval does not automatically select or accept a Zenodo license.
Archive metadata and rights/license selections must be explicitly reviewed
against the actual uploaded artifact classes before publication.

## Scientific and operational boundaries retained

The release retains the frozen WP10 scientific boundaries, including:

- 720 VALID analysis observations;
- 9 retained INVALID provenance attempts;
- P1 null result preserved;
- P2 modeled-contact wording preserved;
- A16/A17 retained as P6;
- M05 right-censoring retained;
- P3 narrower anticipated mechanism absent;
- P4 has no objective correctness oracle;
- `ENTER_SAFE_MODE` remains experimental only;
- M03 structural zero is not generalized as universal safety;
- P5 `5/9` is not represented as a success rate;
- no weighted P5 score/global ranking;
- no simultaneous 95% Pareto-dominance claim;
- execution provenance remains `1 / 9 / 710`;
- final-commit analysis remains a 696-observation sensitivity analysis;
- no operational spacecraft, ground-station, RF, or operator-timing claim.

## WP11 closure decision

WP11 responsible artifact **release preparation** is complete.

The following are explicitly outside this closeout and remain pending
separate authorization/execution:

1. final Zenodo metadata completion;
2. explicit archive rights/license selection;
3. authenticated Zenodo draft/deposit creation;
4. optional DOI reservation;
5. candidate upload;
6. post-upload checksum verification;
7. Zenodo publication;
8. final version/concept DOI capture;
9. manuscript Data Availability update with the actual DOI;
10. optional repository publication tag/release.

Until those actions occur:

- `zenodo_upload_performed=false`
- `zenodo_publication_performed=false`
- `doi_assigned=false`

No statement may claim that the raw campaign is publicly available at a DOI
until the archive publication actually completes.
