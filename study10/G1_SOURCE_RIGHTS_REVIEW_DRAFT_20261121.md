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
| OPS-SAT-AD dataset | https://zenodo.org/records/12588359 | Public v1 Zenodo dataset with `dataset.csv` and `segments.csv`; displayed Rights section lacks an identifiable license value; record signals a newer version exists. | Confirm exact local-data deposit/release identity, the rights applicable to its data bytes and whether newer versions affect selection. | `DATA_RIGHTS_AND_RELEASE_CONFIRMATION_OPEN` |
| OPS-SAT-AD code | https://github.com/kplabs-pl/OPS-SAT-AD and https://www.nature.com/articles/s41597-025-05035-3 | GitHub and journal article identify MIT-licensed **code**; article describes a separately hosted data set. | Whether code's MIT LICENSE applies to deposited data or only repository content must be distinguished. | `CODE_LICENSE_IDENTIFIED` |
| Hack-A-Sat 4 | https://github.com/cromulencellc/hackasat-finals-2023/tree/2cb4b5a50ed2835d97b5f07ac4467ea210bcb7f1 | Public source repo at a pinned commit; README notes generally MIT terms with component-specific exceptions. | File-level rights for game data and nested proprietary/third-party components; no assumption that competition records are real-flight observations. | `SECONDARY_DATA_REUSE_SCOPE_OPEN` |
| NASA SMAP/MSL | https://doi.org/10.1145/3219819.3219845 | Literature context only. | Source package identity, license, population, and independence. | `DEFERRED_NOT_IN_PRIMARY` |

## 3. Platform guidance is not a dataset-specific license

Zenodo's license documentation says CC BY 4.0 is the default selection (https://help.zenodo.org/docs/deposit/describe-records/licenses/). Its permissions guidance says Zenodo does not own user-contributed content and reuse is governed by **each record's** published terms (https://support.zenodo.org/help/en-gb/2-content/21-can-i-get-permission-to-use-a-specific-record). Do **not** assign `CC-BY-4.0` to a dataset from these general statements. The National Library of Medicine catalog independently displays “Rights: No information provided; contact the repository owner” for ESA v2 (https://datasetcatalog.nlm.nih.gov/dataset?q=0002296812); this is corroborating *incomplete rights metadata*, not proof of absent copyright.

A 2026 third-party OPS-SAT study reports CC BY 4.0 for the Zenodo deposit (https://www.mdpi.com/1424-8220/26/19/6126). Treat this as a **secondary claim requiring a direct record/license or rights-holder confirmation**, not as a resolved rights grant.

## 4. Rights-holder clarification requests (not sent)

Send a clarification **only with separate explicit approval**. Preferred contact is the official dataset record's designated contact/depositor or an official institutional data steward. Request:
1. Exact license applicable to **ESA-ADB v1 DOI 10.5281/zenodo.12528696 and v2 DOI 10.5281/zenodo.15237121**, including any differing archive/file restrictions.
2. Whether download, on-device noncommercial academic analysis, publication of aggregate results, small metadata examples, and derived channel-level summaries are permissible, with attribution/citation requirements.
3. Whether redistributing original or transformed telemetry is forbidden or requires prior written consent, and whether project affiliation or export/security terms apply.
4. Whether the public Zenodo record's apparently blank Rights listing omits a deposit-specific license and where its authoritative text is available.

For OPS-SAT, confirm local `dataset.csv` and `segments.csv` match the exact Zenodo release or immutable Git commit before recording `SOURCE_IDENTITY_PINNED`. For Hack-A-Sat, inspect licenses covering the **specific five telemetry files** and archive contents separately from code dependencies.

## 5. Gate decision and conservative controls

- `G1_SOURCE_RIGHTS = OPEN`; `PREREGISTRATION_FREEZE = HOLD`.
- Repository may contain **original authored protocols, public metadata, reference URLs, and hashes**, not third-party datasets or repackaged telemetry.
- Do not extract or run source telemetry, execute a classifier, produce dataset-derived scientific endpoints, or claim an operationally safe recovery decision under this phase.
- Source rights must be evaluated per intended use; if unresolved, keep the source on a **candidate** list or document a transparent population exclusion/amendment **before** freezing and viewing outcomes.
- This is a research governance record, not a legal opinion.
