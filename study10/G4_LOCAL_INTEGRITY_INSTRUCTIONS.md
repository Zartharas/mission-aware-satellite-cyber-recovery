# Study 10 (S10-RSEI-001) — G4 local integrity-only verification

**Authorization:** Sole author approved *local MD5, SHA-256, and ESA archive integrity checks* for previously acquired ESA-ADB and OPS-SAT-AD files. This step does **not** authorize native semantic mapping, source-row research, telemetry publication, third-party upload, PR merging, or G4 scientific execution.

## Provenance and source selection

The script reads the frozen G2 source identity manifest **only after** verifying its SHA-256 (`2eb2cb1ec3a49de3ff61bd7bb1a4d186a45d6fddf7da98ec79d18f0dee9b4210`) and G2 receipt Git blob (`38e5da5edc193b358012bc9c2c3180917d7419ac`). Source MD5 hashes are the published Zenodo release identifiers; the expected SHA-256 values are **prior author-reported local hashes**, not an independently attested Zenodo SHA-256 source. Both must match to pass.

The expected local basenames are:

| Release | Expected filename | Research role |
|---|---|---|
| ESA-ADB v1 Mission 1/2/3 | `ESA-Mission1.zip`, `ESA-Mission2.zip`, `ESA-Mission3.zip` | Paired release only |
| ESA-ADB v2 Mission 1/2/3 | `ESA-Mission1 (1).zip`, `ESA-Mission2 (1).zip`, `ESA-Mission3 (1).zip` | Primary descriptive source strata |
| OPS-SAT-AD v2 | `dataset.csv`, `segments.csv`, `LICENSE` | Fourth primary descriptive stratum and data-specific MIT notice |

The validator does **not** open the separate Hack-A-Sat 4 ZIP or any other non-allowlisted file.

## Running offline on the computer that holds the nine files

Run from the repository checkout containing the **unchanged G2 frozen manifest and receipt** and the new G4 integrity script. The ESA and OPS paths can be separate folders. Example for a Mac where both sets are in `~/Downloads`:

```bash
cd /path/to/mission-aware-satellite-cyber-recovery

python3 study10/g4_local_integrity_check.py \
  --repo "$PWD" \
  --esa-dir "$HOME/Downloads" \
  --ops-dir "$HOME/Downloads" \
  --scratch-dir "$HOME/Downloads" \
  --report "$HOME/Downloads/Study10_G4_Local_Integrity_Only.json"
```

Run a **resource-limited full integrity audit** only on a local filesystem with adequate free storage and authorization to read these files. The ESA archives were previously reported to be **3.7–4.1 GB each**, and contain hundreds of nested channel ZIP files. This script verifies file size plus MD5 and SHA-256; then **streams all outer ZIP member contents to validate CRC and sizes**; for nested channel ZIP files it temporarily stages **one ZIP at a time** to a caller-specified local scratch directory, validates its member CRC and size, and automatically deletes the unnamed scratch file. It does not extract files into a named directory, parse data columns, retain source rows, or transmit data. It refuses path traversal, symlinks, encrypted members, duplicate member names, unsupported deeper ZIP nesting, size bombs and local storage limit violations. Check available disk space and avoid production/shared mounts.

No-scratch diagnostic mode, **not sufficient** for nested ZIP completeness:

```bash
python3 study10/g4_local_integrity_check.py \
  --repo "$PWD" --esa-dir "$HOME/Downloads" --ops-dir "$HOME/Downloads" \
  --outer-only --report "$HOME/Downloads/Study10_G4_Outer_Only.json"
```

The full pass result must be exactly `PASS_ALL_NINE_LOCAL_IDENTITY_AND_NESTED_INTEGRITY`. Exit 0 means all nine selected local files passed the requested archive level; exit 2 indicates a mismatch, corrupt archive, resource stop or precheck failure; exit 3 means missing files or incomplete nested checking. If a source is absent, **do not substitute a different release** or mark the intended source as verified. Request a reviewed filename mapping or new source identity decision instead.

The report contains **only filenames, DOI/release IDs, sizes, digests and summary-level integrity status** (no telemetry rows, absolute local paths or raw archive contents). Even this report should be reviewed before sharing and **must not be automatically uploaded to a public repo**. Sharing a redacted summary does not itself grant further research execution.

## Scope of archive verification

- Full outer ZIP member CRC check validates each outer member's decompressed bytes against the ZIP's CRC32, in addition to the independent *whole ZIP* SHA-256/MD5 check. **CRC32 is not cryptographic proof on its own**.
- Nested channel ZIP member CRC is checked at **one nested archive level**. A further nested `.zip` within the channel ZIP causes an explicit FAIL rather than an unsupported PASS.
- No semantic inference is made from the presence of fields, anomaly labels, timestamps, commands, signatures, or source metadata. Those remain separate G4 scientific work, not authorized here.
- The frozen G2 design and Option B hard source-rights gates remain intact. This integrity run **does not** close G4-01/02/03/04/06 or authorize G4-05/G4-06 final signoff without a reviewed real run record.

## Validation evidence

The separately committed unit tests use **only freshly generated synthetic ZIP/CSV bytes**. GitHub Actions may test the harness and check that a checkout with no dataset originals returns `INCOMPLETE_SOURCE_FILES_NOT_MOUNTED`, but cannot attest the author's nine source files. A real source-integrity PASS must come from running the script on those authorized local bytes and verifying its output.

## Deflate64 method-9 compatibility and rerun after previous archive failure

A previous author-local integrity report dated 2026-11-23 verified **all nine** full-file published MD5 values and author-pinned SHA-256 values. The three ESA v1 archives passed full outer and nested CRC, and all three OPS-SAT files passed their hashes. The **three ESA v2 archives** stopped at `NotImplementedError` because their `ESA-Mission{1,2,3}/channels.csv` entries use **Deflate64 ZIP method 9**, which the standard Python `zipfile` decoder cannot decompress. That observation is documented in the older pre-freeze intake. It is an unsupported-decompression check, not proof of altered source bytes; do not change the failed run or mark it as PASS.

The narrow correction runs **`/usr/bin/unzip -p` only on these three, exact allowlisted v2 `channels.csv` members**, streams decompressed bytes without printing them, and independently verifies the exact `ZipInfo.file_size` and expected `ZipInfo.CRC` against the output. It does not inspect CSV columns, stream any other ZIP member using an external tool, or skip CRC. The subprocess is invoked without a shell, with an output-size bound, time limit, and preserved input identity. If the system unzip utility is missing, unsupported, corrupt, times out or mismatches CRC, the audit **fails closed**. All nested archive checks remain as before. The helper uses only a local scratch directory and sends nothing over a network.

For an existing, previously cloned `S10_G4_integrity_checkout`, update only the detached worktree to the corrected exact Git commit (which will be provided after the fix passes exact-head CI), then rerun the original nine-file command but write to a **new report filename**, leaving the original failed report intact for audit. The nine originals must remain on the Mac and must not enter GitHub, CI, any AI connector, or an external service.

If this method-9-specific correction still encounters a failure, preserve the new JSON report and the *error code only* for review. Do not relabel it as PASS, bypass nested checks, change the frozen G2 source identities or execute G4 semantic research.
