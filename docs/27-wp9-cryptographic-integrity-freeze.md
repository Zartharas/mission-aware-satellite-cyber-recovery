# WP9 Cryptographic Integrity Freeze

**Freeze date:** 2026-08-29  
**Status:** Complete — publication-grade integrity freeze PASS  
**Source repository checkpoint:** `18596ea32c696b65bbdaf5676b1157d633ed59b5`  
**Role:** Durable repository-facing identity and provenance record for the completed WP9 frozen campaign before WP10 statistical analysis.

## Scope and authority

This record does not replace the raw campaign evidence or the authoritative local ledger. The execution authority remains `results/wp9/campaign/attempt-history.json`; this document records the independently verified identities needed to make the frozen state durable and citable without modifying `results/wp9/campaign/`.

The integrity-freeze procedure was read-only with respect to the campaign source tree. It did not execute WP9 runtime, consume a campaign seed, stage files, commit evidence, or push campaign results.

## Canonical campaign membership

The freeze independently reconciled:

- authoritative ledger records: `729`
- VALID frozen positions: `720`
- retained ledgered INVALID attempts: `9`
- global frozen positions: `1`–`720`
- valid design balance: `24` cells × `30` campaign seeds = `720` unique valid `(seed, cell)` pairs
- INVALID→VALID retry positions: `2`, `11`, `120`, `353`, `404`, `407`, `582`, `594`, `627`
- seed-consuming ledgered attempts: `726`
- pre-runtime `CFS_READINESS` INVALID attempts with no seed consumption: `3`
- normal-tree pre-runtime non-scientific unledgered runs: `1`
- quarantined interrupted never-ledgered runs: `1` (position `660`, seed `10028`, cell `A05`)

The corrected INVALID taxonomy is:

- `CFS_READINESS` ×3
- `MEASUREMENT_BINDING` ×2
- `NOMINAL_RUNTIME_COMPLETION` ×2
- `RUNTIME_HEALTH` ×1
- `FROZEN_ANALYSIS_HORIZON` ×1

All nine paired INVALID evidence records resolve `final_campaign_failure_claimed=false`.

## Cryptographic identities

### Authoritative ledger

- path: `results/wp9/campaign/attempt-history.json`
- bytes: `152892`
- SHA-256: `92893a2fd8746f410bffd4dca5101bc3f533ada2ff82f98681788cf0c24ce6fd`

### Complete local campaign tree

The complete source tree contained `17182` files and zero unclassified files at freeze time.

Deterministic tree identity:

`ad1e127b4431b6b334955129fcba82f76b18e5b43585395ac8c37300cac087b1`

Algorithm: SHA-256 over all campaign files in lexicographic repository-relative POSIX-path order, with each digest record encoded as:

`relative_path + NUL + lowercase_file_sha256 + LF`

Filesystem mtimes, ownership, inode numbers, and other mutable filesystem metadata are intentionally excluded.

### Frozen membership / manifest identities

- 729-ledger membership SHA-256: `979e52cfd23ea3f5e823dda58f0efc7573607bc51275883025727cb999b4c64e`
- 720-valid analysis membership SHA-256: `a2bf0c8f352f4386e74a500d97ea8f73e0c39d03bfe10ac0ebcf02470af9f70e`
- 9-INVALID classification SHA-256: `864a734488cabaef336cd128eb0264f1c69429f0923a408e3f261ac28a852681`
- complete local campaign-file manifest SHA-256: `4dd3f460874d01d99a70dcbc936257bbab3dd8ef637150a26df7303fcf25f0a1`
- ledgered-attempt file manifest SHA-256: `a7664f5958838e83c5199cc27863fcb12031014b2bcc7c1d56d7494b12f733cd`
- valid-attempt file manifest SHA-256: `bf5277c208f1be7f203b4a49ee5250f0189a6f0395952cd8146fde5f6a093b6d`
- invalid-attempt file manifest SHA-256: `d3a3f3891c6d9d6e49142725f3b9fd0dbf180adcb2f105f4bb5f2a8e03b65169`
- pre-runtime unledgered manifest SHA-256: `c7360fa401afd1b307dad4ec5cb4b7fe5f37e07a89d6fc664c37f86f0a3ef337`
- quarantine manifest SHA-256: `2e1626e26377e6199f9f352e8faf0586d0b2a9259162f2636ae818c4a89b1189`
- execution-commit membership SHA-256: `2952dff5a5d38f3c69ac76feab1718b4548aa1925d3aa4cec7bcffe079207a3e`
- execution-commit distribution SHA-256: `57b8c9265682310482c58eb5b722be55a23d93c4fd74bef3eca967022a532e52`
- freeze-index SHA-256: `6c287c3a7bd4bd9644cfa310b08060cd47f722eef2d4774b51962518e392976f`
- bundle-checksum-file SHA-256: `696bc615c1f227320aced30c1c88f4664f62def0cfbb454209e6068785e2d819`

## File-population partition

The complete `17182`-file tree reconciled exactly as:

- files under 729 ledgered attempt directories: `17170`
  - files under 720 VALID attempt directories: `16980`
  - files under 9 INVALID attempt directories: `190`
- normal-tree pre-runtime unledgered files: `2`
- quarantined interrupted-attempt files: `9`
- authoritative ledger file: `1`
- unclassified files: `0`

The normal-tree unledgered run is `20260824T135902Z-wp9-r066-p0001-s10001-a19-851b4bd92c8e43ea82c92994e41484b2`; it contains only `campaign-plan.json` and `r066-runtime-request.json`, no campaign seed-consumption marker, no canonical outcome, and no runtime-observation evidence.

The quarantined never-ledgered run is `20260829T060252Z-wp9-r069-p0660-s10028-a05-d20db11ea75e4b05a49c85faca45d04b`; it is retained outside canonical membership and has no seed-consumption marker or canonical VALID/INVALID outcome.

## Execution-repository provenance

A correction is required to any earlier wording implying that every campaign observation ran at one repository commit. Per-attempt `immutable-ground/campaign-plan.json` provenance shows **three** research-repository execution commits across the 729 ledgered attempts:

| Execution commit | Ledgered attempts | VALID | INVALID | Global-position range |
|---|---:|---:|---:|---:|
| `aae2239753119c92e7633db3b6c73aee94c7b6dd` | 2 | 1 | 1 | 1–2 |
| `97074d0cdc4261de02bc6f618e891a88f45f9cfc` | 10 | 9 | 1 | 2–11 |
| `7ed85d5cbeca8f903b3468bc6ccc1c56e29c2446` | 717 | 710 | 7 | 11–720 |

The overlap at positions `2` and `11` reflects INVALID→VALID retry boundaries that straddled plumbing/compatibility promotions; it is not duplicate valid membership.

All three commits resolve in Git history and are ancestors of source repository checkpoint `18596ea32c696b65bbdaf5676b1157d633ed59b5`.

The **final campaign execution baseline** is `7ed85d5cbeca8f903b3468bc6ccc1c56e29c2446`: the retained position-720 run independently records that SHA in `immutable-ground/campaign-plan.json`, `immutable-ground/development-plan.json`, and `immutable-ground/r066-runtime-request.json`.

Therefore publication wording must distinguish:

1. per-attempt execution provenance across the three historical ancestor commits;
2. the final campaign execution baseline (`7ed85d5...`); and
3. the later documentation checkpoint (`18596ea...`).

## Source immutability proof

After the first checksum-manifest pass, the freeze re-enumerated and re-hashed all `17182` source files. The second pass verified:

- identical source-file set;
- identical byte count for every file;
- identical SHA-256 for every file; and
- unchanged authoritative-ledger SHA-256.

The completed freeze bundle then passed its own checksum verification, including `FREEZE_INDEX.json`.

No campaign source file was created, modified, deleted, moved, staged, committed, or pushed by the freeze procedure.

## WP10 analysis boundary

WP10 analysis membership is exactly the 720 VALID runs identified by the frozen membership digest:

`a2bf0c8f352f4386e74a500d97ea8f73e0c39d03bfe10ac0ebcf02470af9f70e`

The 9 ledgered INVALID attempts, the two-file pre-runtime abort, and the quarantined position-660 interrupted run are not members of the 720-valid statistical analysis dataset. They remain provenance/methods/limitations evidence.

The A16/A17 P6→P5 handoff caution in `docs/26-wp9-r069-campaign-closeout.md` remains binding for WP10 coding.

## Archive decision

**Primary publication archive selected: Zenodo.**

Rationale: the intended release needs a persistent DOI, immutable/versioned research-object records, and a durable landing page independent of the GitHub source repository. As of the freeze date, Zenodo provides DOI assignment for published uploads, supports versioned records, and accepts up to 100 files / 50 GB per upload.

The archive deposit itself is **not yet performed** by this repository change. Before publication-final treatment:

1. package the frozen data/evidence and integrity bundle into no more than 100 archive objects without altering the logical source-tree identity;
2. verify the packaged total against Zenodo's 50 GB per-upload limit;
3. upload the data package plus this integrity bundle;
4. verify `BUNDLE_CHECKSUMS.sha256`, `FREEZE_INDEX.sha256`, and the packaged-data checksum after upload;
5. publish the Zenodo record and capture the version DOI and concept DOI; and
6. update this document and the manuscript Data Availability statement with the final DOI(s).

If the packaged dataset exceeds Zenodo's current per-record capacity, the fallback is an institutional research-data repository capable of preserving the full dataset; the Zenodo record should then preserve the integrity bundle and point to that primary data deposit rather than silently omitting evidence.

## Repository policy note

`results/README.md` permits committed run manifests and checksums, but `.gitignore` currently ignores all `results/*` content except `results/README.md`. This freeze does not weaken that raw-results boundary. The durable identities are recorded here under `docs/`; the raw campaign remains ignored and untouched.

A future sanitized artifact-release change may add a narrowly scoped allowlisted manifest/checksum path if WP11 determines that duplication inside the repository materially improves reproducibility.

## Transition state

- WP9 campaign execution: **Complete**
- WP9 authoritative integrity audit: **PASS**
- WP9 cryptographic integrity freeze: **PASS / Complete**
- WP10 statistical analysis: **Ready to start against the frozen 720-valid membership only**
- archive platform decision: **Zenodo selected**
- archive deposit / DOI: **Pending**
- raw campaign evidence mutation: **None**
