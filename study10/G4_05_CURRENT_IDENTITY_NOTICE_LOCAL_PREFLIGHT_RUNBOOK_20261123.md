# Study 10 — approved G4-05 current local identity and prospective-notice preflight

**Date:** 2026-11-23 UTC.  
**Approval:** Author replied **“yes, I approve”** to performing the remaining applicable G4-05 source-identity and notice preflight, expressly carrying forward **no G4-06** and **no PR merges**.  
**Status:** `PREFLIGHT_PACKAGE_TESTED; ORIGINAL_NINE_SOURCE_LOCAL_CHECK_PENDING`. Do not call the G4-05 gate fully cleared from this documentary artifact.

## 1. Reuse exact frozen evidence; no rescan of ZIP members or telemetry

The frozen G2 receipt has Git blob SHA-1 `38e5da5edc193b358012bc9c2c3180917d7419ac` and the frozen G2 manifest SHA-256 is `2eb2cb1ec3a49de3ff61bd7bb1a4d186a45d6fddf7da98ec79d18f0dee9b4210`. No frozen G2/G3 files are modified. The original nine sources have source-specific published MD5s and previously author-reported SHA-256s frozen in the manifest:

- Six ESA archive bytes, Missions 1–3 in both v1 and v2; exact original local filenames are reconstructed from `study10/g4_local_integrity_check.py`, pinned Git blob `f5d76faf5cbfc37a1391bbd7a287bea6ee23a158`.
- Two OPS-SAT v2 CSV files, `dataset.csv` and `segments.csv`, and the accompanying exact v2 `LICENSE` file.
- **No Hack-A-Sat** sources; excluded by frozen design.

The approved prospective R1 rights evidence record Git blob is `812fd538b0fa5e8970996a8224c424d8dc8b7342`, and the sole-author limited-use attestation is Git blob `92d0bfc3d6b52d2e0d78169577c8e4a433bafd54`. The draft, version-specific prospective notice text is Git blob `f475c5591457ecfbf731e932e43e65bd99b17cf9`. Exact local Git blob identity of each record is checked by the preflight script.

**Already achieved:** R1 documentary eligibility `EVIDENCE_PASS_CONDITIONAL` for ESA v2 and OPS-SAT v2, `EVIDENCE_PASS_CONDITIONAL_IF_USED` for ESA v1. Existing V2/V3 bounded notice scans cover **26/26 leading CSV preambles**, not full member terms. There is no reason to repeat those nested ZIP scans.

**Current check purpose:** a *new* read-only comparison of the nine local files' **whole-file MD5 and SHA-256 digests** against frozen G2, plus a strictly pinned, documentary prospective notice-plan check. CSV contents are never parsed or exported. ZIP members are not extracted/decompressed. Output is an aggregate/failure-code JSON with no original source bytes, source paths, or observed hashes.

## 2. Local package validated independently on synthetic fixtures

Download the conversation attachment `Study10_G4_05_Current_Identity_Notice_Preflight_Bundle.zip`, SHA-256:

`a4694ff9acd3c99f63850361fcc653ec940ce2a08e6ba59c8b836153896fcdf3`.

Four package files and its internal `SHA256SUMS.txt` are included. Testing from the prepared local package: **15/15 synthetic regression tests PASS**, Python syntax PASS, Bash syntax PASS, ZIP CRC/integrity PASS. Synthetic tests do **not** verify the author's real archived files. The ZIP is a **chat-delivered, hash-pinned standalone local artifact**; its Python source and test source are not committed by this documentary PR. It is separately auditable by its SHA-256. Do not confuse a successful synthetic test with a real-source PASS.

The launcher itself has no network or Git operation, and refuses any mismatched, unclean repository checkout, existing report or tampered package. Its script reads the nine source files as opaque byte streams with a 4 MiB buffer. A readable regular file is required; symlinks and nonregular/special files are refused (including FIFO). The run may read more than 23 GiB of local storage, depending on original archive sizes, and enforces a 3600-second wall-clock cap. No raw-data upload occurs.

## 3. Safe Mac execution (author-controlled)

Create a **separate** repository checkout at exact **draft PR #248** head `dfce2b9a620cd93911b0729462664b3b6b4560ea`. Do **not** merge any PR and do not touch existing pinned checkouts:

```bash
gh repo clone Zartharas/mission-aware-satellite-cyber-recovery "$HOME/Downloads/S10_G4_05_pinned_checkout" || exit 1
cd "$HOME/Downloads/S10_G4_05_pinned_checkout" || exit 1
git fetch origin study10/s10-rsei-001-g4-r1-author-approval-20261123 || exit 1
git checkout --detach dfce2b9a620cd93911b0729462664b3b6b4560ea || exit 1
```

This clone/fetch is **read-only remote access** performed by the author on the Mac, not by the launched validator. If the checkout already exists, **do not** re-clone into it or replace its files. Check the exact HEAD and clean status manually.

After saving the verified bundle to `~/Downloads`, from the Mac:

```bash
cd "$HOME/Downloads" || exit 1
ZIP="$HOME/Downloads/Study10_G4_05_Current_Identity_Notice_Preflight_Bundle.zip"
printf '%s  %s\n' \
  'a4694ff9acd3c99f63850361fcc653ec940ce2a08e6ba59c8b836153896fcdf3' \
  "$ZIP" | shasum -a 256 -c - || exit 1
unzip -n "$ZIP" -d "$HOME/Downloads" || exit 1
bash "$HOME/Downloads/study10_g4_05_preflight_v1/Study10_G4_05_Local_Run.sh"
```

Expected report: `~/Downloads/Study10_G4_05_Identity_Notice_Current_Preflight.json`. The runner creates this report only when no prior path exists, permissions `0600`. It never overwrites or uploads the report or data. A report status `G4_05_CURRENT_CHECK_PASS_NOT_EXECUTION_AUTHORIZED` means nine source digests and the **prospective notice plan** match their pinned documents **at this specific run time**. Error states `G4_05_FAIL_CLOSED` or `G4_05_ERROR_FAIL_CLOSED` require investigation, not a downgrade/waiver.

The author should share **only the sanitized terminal source-count/status lines, failure codes (if any), and report SHA-256**, not raw telemetry ZIPs or CSVs.

## 4. Explicit unresolved matters and future execution boundary

- **Actual Mac source check is pending.** Repository document/commit checks and synthetic tests do not establish the current local nine-source identity.
- **G4-05 remains partial** pending those real local results. Even a PASS now does not establish the **future** identity state immediately before a separately approved scientific execution; repeat a narrowly scoped dual-hash check at that execution boundary if and only if separately authorized.
- The notice-plan check verifies that the appropriate release DOIs, ESA **CC BY 3.0 IGO** credit/license/changes/non-endorsement, OPS-SAT **data-inclusive MIT** license/copyright/full-notice obligations, no-raw-data redistribution, and prospective-methods limitations are documented. It does **not** verify actual manuscript implementation or replace an eventual journal review.
- OPS-SAT v2's official creator-order citation discrepancy remains provisional; final bibliography requires a version-specific authoritative citation check, but this is not a reason to invent a new file license restriction.
- No source-semantic adjudication, no G3 parity execution, no selector policy change, no independent spacecraft replication claim, no original data release and **no PR merge** are part of this preflight.
- **G4-06 remains NOT AUTHORIZED**, as repeatedly directed by the author. The prospective design remains **four descriptive primary strata × eight frozen variables = 32 classifications**, with ESA v1 only optional paired sensitivity.

**Disposition:** `APPROVED_G4_05_READ_ONLY_PREFLIGHT_PREPARED; USER_MAC_NINE_SOURCE_RUN_NOT_YET_VERIFIED; NO_G4_06_EXECUTION`.
