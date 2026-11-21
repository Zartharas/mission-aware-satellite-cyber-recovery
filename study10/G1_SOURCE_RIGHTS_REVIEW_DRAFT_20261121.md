# S10-RSEI-001 — G1 source rights and reuse assessment (REVIEW DRAFT)

**Date:** 2026-11-21. **Repository basis:** `5ee451c2a739cbca7dc948d49239d985c6b4cc07`.
**Status:** `G1_RIGHTS_REVIEW_PARTIAL_RIGHTS_NOT_RESOLVED`.
**Effect:** Records public-source evidence and decisions needed for protocol freezing; it does **not** grant any dataset license or authorize source-data access, execution, redistribution, manuscript revision, or submission.

## 1. Rights assessment method

Distinguish **(i)** public access; **(ii)** publication/code license; **(iii)** license of **dataset bytes**; **(iv)** permission for local academic analysis; and **(v)** permission to redistribute data or derived materials. An institutional name or an apparent Zenodo default license does not resolve (iii)–(v). Record **exact release-specific license wording or a documented rights-holder clarification** before treating a source's reuse as cleared. Preserve terms/attribution requirements, date, URL, version, and evidence snapshot. Confirm whether any telemetry security/export or mission-sensitive restriction also applies; do not infer blanket permission.

## 2. Source-by-source evidence and dispositions

| Source | Direct source checked | What is established | What remains unknown | G1 status |
|---|---|---|---|---|
| ESA-ADB v1.0 | https://zenodo.org/records/12528696 | Public Zenodo record for three real-flight mission datasets, DOI and archive MD5 identities; its rendered Rights section shows a License heading without an identifiable license value. | Dataset-specific license/permission scope for local analysis, derived outputs, redistribution and adaptations. | `RIGHTS_UNRESOLVED` |
| ESA-ADB v2 | https://zenodo.org/records/15237121 | Separate public v2 release, same mission family; displayed Rights section likewise lacks an identifiable license value. | Same rights questions; do **not** inherit v1 or generic ESA policy. | `RIGHTS_UNRESOLVED` |
| ESA-ADB code | https://github.com/kplabs-pl/ESA-ADB | GitHub identifies code repository license as MIT. | MIT repository code license is **not** proof that the separately hosted ESA telemetry ZIPs are MIT. | `CODE_LICENSE_IDENTIFIED_DATA_RIGHTS_UNRESOLVED` |
| OPS-SAT-AD dataset (v1 and v2) | https://zenodo.org/records/12588359 and https://zenodo.org/records/15108715 | The author-reported 2026-11-21 local checksum checker returned `PASS_ZENODO_V2_AND_PRIOR_INTAKE_SHA256`: both CSV MD5s exactly matched published **v2 record 15108715**, and both independently recorded earlier intake SHA-256 values matched. This is a **user-local verified** source identification, not an assistant-side rehash of the MacBook data. | Establish the applicability of the supplied v2 `LICENSE` to the Zenodo **data bytes** and the intended academic use/publication/redistribution; license gate remains open. | `V2_IDENTITY_PASS_RIGHTS_OPEN` |
| OPS-SAT-AD code | https://github.com/kplabs-pl/OPS-SAT-AD and https://www.nature.com/articles/s41597-025-05035-3 | GitHub and journal article identify MIT-licensed **code**; article describes a separately hosted data set. | Whether code's MIT LICENSE applies to deposited data or only repository content must be distinguished. | `CODE_LICENSE_IDENTIFIED` |
| Hack-A-Sat 4 | https://github.com/cromulencellc/hackasat-finals-2023/tree/2cb4b5a50ed2835d97b5f07ac4467ea210bcb7f1 | Public source repo pinned to a commit. README explicitly says repository files generally fall under MIT **unless stated otherwise**; its actual top-level license text is `.LICENSE` (MIT wording), despite README linking to a non-existent `LICENSE.md`. cFS, COSMOS and OSK have distinct licenses. | Confirm no path-specific notices/third-party restrictions affect the four telemetry CSVs or raw telemetry tar members before redistributing; game data are competition scoring input, not proven on-orbit observation. | `SECONDARY_DATA_REUSE_SCOPE_OPEN` |
| NASA SMAP/MSL | https://doi.org/10.1145/3219819.3219845 | Literature context only. | Source package identity, license, population, and independence. | `DEFERRED_NOT_IN_PRIMARY` |

### OPS-SAT dual-release identity (published checksums and author-reported local v2 PASS)

| Zenodo release | `dataset.csv` published MD5 | `segments.csv` published MD5 | Files in deposit |
|---|---|---|---|
| v1 / 12588359 | `c12fb83863afa4463dec07303a20bb14` | `1f4b6ffd0359efac96a6698ff557e0f9` | Two CSVs |
| v2 / 15108715 | `5246fdc5e4630a4cecbf7fb6bc8b795e` | `72f109630abb933a386106897a631188` | Two CSVs plus notebooks, `LICENSE` and `requirements.txt` |

**Local identity result supplied by the author (2026-11-21):** The MacBook run of `Paper5_OPSSAT_Zenodo_Release_Identity_Check_v2.py` reported `PASS_ZENODO_V2_AND_PRIOR_INTAKE_SHA256`, identifying **Zenodo v2 record 15108715**. `dataset.csv` matched the v2 MD5 `5246fdc5e4630a4cecbf7fb6bc8b795e` and the prior intake SHA-256 `b524177da6f516d5c9f63c7acbc385341f0ad42046ef20c1bed2d25e51b98f02`. `segments.csv` matched v2 MD5 `72f109630abb933a386106897a631188` and prior intake SHA-256 `d5201e9e751eb2a53a0ff7c11567dc4239f594ea4b479b2aa66fe67ddcbcb9ba`. Both reported prior SHA-256 comparisons were `True`. The script's SHA-256 was independently verified in the assistant container as `9f5b9476dafe5ed51977d4ac7d15c79e1384c44f5f9e79bf862452c37e3dc7b2`, matching the user's MacBook `shasum`. **Evidence boundary:** the local CSV bytes and generated JSON report were not uploaded or independently rehashed by the assistant. This establishes a reported local source-identity PASS; it does not determine data license, source-population independence, or valid recovery-state semantics. Any post-freeze population substitution would require a documented deviation.

## 3. Platform guidance is not a dataset-specific license

Zenodo's license documentation says CC BY 4.0 is the default selection (https://help.zenodo.org/docs/deposit/describe-records/licenses/). Its permissions guidance says Zenodo does not own user-contributed content and reuse is governed by **each record's** published terms (https://support.zenodo.org/help/en-gb/2-content/21-can-i-get-permission-to-use-a-specific-record). Do **not** assign `CC-BY-4.0` to a dataset from these general statements. The National Library of Medicine catalog independently displays “Rights: No information provided; contact the repository owner” for ESA v2 (https://datasetcatalog.nlm.nih.gov/dataset?q=0002296812); this is corroborating *incomplete rights metadata*, not proof of absent copyright.

A 2026 third-party OPS-SAT study reports CC BY 4.0 for the Zenodo deposit (https://www.mdpi.com/1424-8220/26/19/6126). Treat this as a **secondary claim requiring a direct record/license or rights-holder confirmation**, not as a resolved rights grant.

## 4. Rights-holder clarification requests (not sent)

Send a clarification **only with separate explicit approval**. Preferred contact is the official dataset record's designated contact/depositor or an official institutional data steward. Request:
1. Exact license applicable to **ESA-ADB v1 DOI 10.5281/zenodo.12528696 and v2 DOI 10.5281/zenodo.15237121**, including any differing archive/file restrictions.
2. Whether download, on-device noncommercial academic analysis, publication of aggregate results, small metadata examples, and derived channel-level summaries are permissible, with attribution/citation requirements.
3. Whether redistributing original or transformed telemetry is forbidden or requires prior written consent, and whether project affiliation or export/security terms apply.
4. Whether the public Zenodo record's apparently blank Rights listing omits a deposit-specific license and where its authoritative text is available.

For OPS-SAT, confirm local `dataset.csv` and `segments.csv` match the exact Zenodo release or immutable Git commit before recording `SOURCE_IDENTITY_PINNED`. For Hack-A-Sat, the canonical MIT text is in `.LICENSE` at pinned commit `2cb4b5a50ed2835d97b5f07ac4467ea210bcb7f1` (Git blob SHA-1 `a086eaa939d79549c4b16fea778b86c1f87ed389`); verify there are no overrides affecting the five telemetry paths or nested archive contents. This does not automatically establish rights to third-party embedded materials.

## 5. Gate decision and conservative controls

- `G1_SOURCE_RIGHTS = OPEN`; `PREREGISTRATION_FREEZE = HOLD`.
- Repository may contain **original authored protocols, public metadata, reference URLs, and hashes**, not third-party datasets or repackaged telemetry.
- Do not extract or run source telemetry, execute a classifier, produce dataset-derived scientific endpoints, or claim an operationally safe recovery decision under this phase.
- Source rights must be evaluated per intended use; if unresolved, keep the source on a **candidate** list or document a transparent population exclusion/amendment **before** freezing and viewing outcomes.
- This is a research governance record, not a legal opinion.
