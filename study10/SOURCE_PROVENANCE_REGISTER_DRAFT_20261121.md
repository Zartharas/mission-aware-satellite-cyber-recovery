# S10-RSEI-001 — Source provenance register (DRAFT)

**Status:** `DRAFT_FOR_REVIEW_NOT_FROZEN` · **Date:** 2026-11-21 · **Repo reference:** `main` at `660683a6561274bdbeadc84a5000436e8c5d5d1f`.  
**Evidence boundary:** data identities and metadata only; no new recovery-state semantic classifications, no telemetry-row experiment, no manuscript changes, and no publication submission.

## 1. Source inclusion and roles

| Family | Bound source | Role | Independence / restriction |
|---|---|---|---|
| ESA-ADB v2 | 10.5281/zenodo.15237121 | Primary candidate | Three mission strata, shared release/source family |
| OPS-SAT-AD | 10.1038/s41597-025-05035-3 | Primary candidate | Independent mission; segments clustered in nine channels |
| ESA-ADB v1 | 10.5281/zenodo.12528696 | Matched sensitivity | Not independent of v2 |
| Hack-A-Sat 4 | Git commit `2cb4b5a5…` | Separate secondary | Competition scoring inputs; no per-record flight validation |
| NASA SMAP/MSL | 10.1145/3219819.3219845 | Deferred | No pinned input population or verified license |

## 2. ESA archives — published MD5 + user-reported SHA-256

The checksums below are **from the author’s local checker outputs**; the assistant did not independently hash the multi-gigabyte ESA downloads. Each file MD5 matched its *published* Zenodo release identity at intake. The later metadata-only inventory explicitly did **not** rehash them.

| Mission | Release | Local basename | Published MD5 | Local SHA-256 (reported) | ZIP members |
|---|---|---|---|---|---:|
| 1 | v1 | `ESA-Mission1.zip` | `80750189d171f5f398fb3d96c49df12b` | `8c81edb1e81af9084f38a3cc06fa06dbea73b504c99ce1b0fb92bda996b801a7` | 780 |
| 1 | v2 | `ESA-Mission1 (1).zip` | `9770ad12ed730238f37c42d5c27ab436` | `ba28f761b1deab4dbba4728793bff139fea39dbf9cf0d9c559d619ffe75d5a72` | 780 |
| 2 | v1 | `ESA-Mission2.zip` | `0b7505b7f0731ca037ee889ca2a520ce` | `843c3b5e0042178bfee650fcf7f16413ce8083dcfa5db53e6d37e0811dfb138d` | 230 |
| 2 | v2 | `ESA-Mission2 (1).zip` | `bfc72012691427d9327eb41f726ce45e` | `e8a89be1917b6754a10bd323441e87a82c8cf2e84ed162442c2dcf72ecc346d5` | 230 |
| 3 | v1 | `ESA-Mission3.zip` | `34b8a8857e2242fb1f00b368b7421595` | `4ed219e4d07c8a277b5c32d06f9a8a9ebc61fc231450bf21ce92079d25182b27` | 52 |
| 3 | v2 | `ESA-Mission3 (1).zip` | `d63943f09c81378acd9fc5e565ecc66e` | `f426c4bb9857299c586e3c50f35ddb58b469a3e5565f586d4095bcb6cf532404` | 52 |

Official records: https://zenodo.org/records/12528696 (v1.0) and https://zenodo.org/records/15237121 (v2). Public availability **does not by itself establish a data-republication license**; resolve rights before execution/distribution.

## 3. ESA channel-metadata reconciliation (reported Mac checks)

| Mission | Stable channel IDs | v2 Categorical YES | v2 Categorical NO | `physical_unit_8` cleared | Exact set alignment |
|---|---:|---:|---:|---:|---|
| 1 | 76 | 0 | 76 | 0 | PASS |
| 2 | 100 | 10 | 90 | 10 | PASS |
| 3 | 48 | 44 | 4 | 44 | PASS |

**Totals:** 224 channel IDs; 54 new categorical YES flags, exactly 54 corresponding cleared unit placeholders; no changed other shared fields; no added/removed channels. Only the three outer ZIP `channels.csv` entries differed by CRC32/size. Deflate64 (method 9) v2 files were read via local macOS `unzip -p` and CRC32/size validated. Nested ZIP payloads were **not cryptographically compared**.

## 4. OPS-SAT-AD intake anchors

User-provided source inspection: **2,123 segments**, **303,493 raw samples**, **nine channels**, **1,689 nominal**, **434 anomalous**, **1,594 train** and **529 test**. Training total in the source article text says 1,494, inconsistent with constituent counts and uploaded CSV; preserve the discrepancy. `segments.csv` text `label` is uniformly `anomaly`; the numeric `anomaly` field varies and remains offline anomaly truth, not cyberattack or recovery authorization.

| Source member | SHA-256 recorded during previous intake |
|---|---|
| `dataset.csv` | `b524177da6f516d5c9f63c7acbc385341f0ad42046ef20c1bed2d25e51b98f02` |
| `segments.csv` | `d5201e9e751eb2a53a0ff7c11567dc4239f594ea4b479b2aa66fe67ddcbcb9ba` |
| `dataset_generator.ipynb` | `409047fc42fbc415b7b16c85e24773127d1266e5034ae5be47b69d5323b120e2` |
| `modeling_examples.ipynb` | `224f8a73561c25e421f1eb72b84a850118002eecf278642c690e8b4fce2d4faa` |
| `LICENSE` | `76d2ff9834ed2bb1356d9f7eb303c289817374bb1d5bbe5af86817e73e0f47d2` |
| `requirements.txt` | `fd06761596b7271f90cb7183ced57b96884d02ae74195b71dbe26b683a19aaaf` |

Publisher article: https://doi.org/10.1038/s41597-025-05035-3; figure-order correction: https://doi.org/10.1038/s41597-025-05751-w. Uploaded license stated MIT; review rights of each actual source bundle before reproducing content.

## 5. Hack-A-Sat 4 provenance — independent check of received ZIP

Upstream: https://github.com/cromulencellc/hackasat-finals-2023 at commit `2cb4b5a50ed2835d97b5f07ac4467ea210bcb7f1`. The complete user-uploaded repository ZIP has SHA-256 `5a9ea0ffe6382739c3d03166935ac9b10aba5fd77878ac2cb2602f48ef34a8e5` (16,395,491 bytes). The ZIP hash refers to the **received conversation attachment**, not a separately rehashed MacBook download.

| File in `game_data/HAS4_FULL_GAME/` | Git blob SHA-1 | SHA-256 verified in received ZIP |
|---|---|---|
| `processed_tlm/2023_08_10_00_00_00.0_GPS_GEODETIC.csv` | `ad8e34ba9dead45208c28affff9cb6f0681a038f` | `cd0ab92d244bc10db728cfa0f6e62662ef316779b7e0fd689d3dfaa3275d2faf` |
| `processed_tlm/2023_08_10_00_00_00.0_SCRIPT_KIDDIE.csv` | `6fa02c57f8044535a9839d03c829eaf40f585989` | `f3c355869f52c29caed2538f734d1a28a8bab67fa65404cc8f43db2d1956d495` |
| `processed_tlm/2023_08_10_00_00_00.0_SCRIPT_STATUS.csv` | `03f356d745e1f7ea08faf9376743d507df2499bc` | `8f90a749dec3e1fe95ec340b59f75c37268c76008666af69626a61e536009eda` |
| `processed_tlm/2023_08_10_00_00_00.0_SPAP_METADATA.csv` | `d7e700b93451e709d21d53e0e224513e2a31aee9` | `71a2199819178eba11e5c445679c524cd621c8b69e243c8a59de808a18843c11` |
| `raw_tlm/raw_tlm.tar.gz` | `e9eab4cfbbfb92480f7687472afe9ae8ef64ec08` | `3ca4ebbd4cee7ef4591d35017c3f8dd2607adb0806203e32a398c7f9aab4c8af` |

All five file identities matched both the user’s reported check and this independent read-only verification of the uploaded repository ZIP. The tarball has 231 entries by prior local header inspection (230 regular files and one directory), without extraction. Game data are described by the source as **competition scoring inputs**, not record-level proven flight telemetry. README licensing is generally MIT with exceptions; confirm specific code/data license headers before reuse.

## 6. Provenance uncertainty and lock conditions

- `VERIFIED_PUBLIC`: ESA DOI/MD5 records; OPS-SAT publication DOI; upstream Hack-A-Sat commit and Git blob IDs.
- `USER_LOCAL_VERIFIED`: ESA full-archive hashes and metadata comparisons; OPS-SAT counts and source-file hashes.
- `INDEPENDENT_ATTACHMENT_VERIFIED`: five Hack-A-Sat file identities inside the received ZIP.
- `NOT_VERIFIED`: full ESA nested-payload SHA-256 equivalence, any new eight-variable mapping, row-level command authorization, effective ESA reuse license, NASA archive identity, source independence as a statistical property.
- **No raw ESA/OPS datasets have been copied to the project repository.** Do not publish raw third-party data, user home paths, or hidden credentials.

## 7. Required next gates

Approve this provisional study ID and cohort membership; resolve source rights; freeze this register and the protocol with content hashes; lock all semantic mappings and synthetic controls; authorize subsequent implementation and data access **separately**. Frozen Study 9 and the current Paper 5 submission package remain unchanged.