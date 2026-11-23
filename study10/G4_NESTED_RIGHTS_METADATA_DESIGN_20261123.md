# Study 10 — G4 nested ZIP rights-metadata inspector (development only)

**Status:** Synthetic-tested tooling proposal. The author authorized development on a new GitHub draft branch only, **not execution on the six original ESA archives**, PR merge, G4-06 source-semantic research, original telemetry upload, redistribution or scientific results.

## Provenance and bounds

- Parent review: draft PR #235 at `db1a468edadcf42d37abf49751bd7f08337fb780`.
- Previous local top-level report: `Study10_G4_License_Markers_Only.json`, author-reported SHA-256 `1b15ca458ce1f85ee4730e1b267dae4f023e60bf90689575b03930cd02fc00b5`. The assistant has **not rehashed** this report. The script requires the exact report bytes, SHA-256 and reported 6-archive / 2,124 outer member / 2,090 nested ZIP contract before scanning any original ESA archive.
- Frozen G2: `8ed6a2b16233b86bf91672f6f15605dcf906c5eb`; validated through existing repository `verify_local_manifest` and allowlist.
- Six ESA files only, from frozen G2; no OPS-SAT CSV inspection or Hack-A-Sat source use.

## What the tool does, and does not do

1. Opens only the six ESA outer ZIPs and checks their directory entries. It does **not** extract outer non-ZIP entries.
2. For an outer member named `.zip`, **decompresses that ZIP-container member** to an unnamed local temporary file, with per-archive, cumulative-size, count and wall-time limits. This necessarily reads **the bytes of the nested ZIP container**; it does not read telemetry members *inside* that nested ZIP.
3. Reads the nested ZIP's central-directory metadata only, counts rights-document marker **categories** such as `LICENSE` or `NOTICE`, counts deeper `.zip` names but does **not** descend again. It never reports original inner paths, filenames, labels, samples, telemetry content, or a clean-rights conclusion.
4. Fails closed on archive corruption, unsupported compression, malicious duplicates, symlinks, unavailable inputs, resource limits, mismatched metadata, or deeper nesting (the latter produces an explicitly incomplete aggregate result).
5. Outputs a locally created JSON with mode `0600`, refusing overwrite. **Do not upload any local source archive or resulting metadata to a public repository.** Review metadata before voluntarily sharing even summary results.

**Limits:** 512 MiB decompressed ZIP-container member, 32 GiB cumulative local spooling, 2,500 nested ZIP containers, 10,000 members per nested directory, and 30 minutes elapsed by default. Size/time parameters can be lowered or raised **only within** hard CLI caps (at most 1 GiB per nested container, 64 GiB cumulative, 2 hours). Limits are protective guards, not a prediction that the original ESA archives will fit.

**Research/legal boundary:** A successful directory scan only establishes that the specified metadata was inventoried. It cannot establish the absence of third-party rights, in-band license statements, export controls, restrictions within telemetry fields, or whether ESA v2 CC BY 3.0 IGO applies to every member. G4-01/02/03 and G4-05 final clearance remain unresolved; G4-04 optional secondary remains excluded; G4-06 remains blocked.

## Synthetic-only validation

```bash
python3 -m compileall -q study10/g4_nested_license_metadata_inventory.py study10/test_g4_nested_license_metadata_inventory.py
python3 -m unittest discover -s study10 -p 'test_g4_nested_license_metadata_inventory.py' -v
python3 study10/g4_readiness_guard.py --audit
```

GitHub Actions runs only the test-generated synthetic ZIP bytes and existing fail-closed G4 readiness checks. **It never runs this tool against original satellite archives.**

## Future local execution interface — NOT CURRENTLY AUTHORIZED

The CLI accepts `--repo`, `--esa-dir`, `--previous-report`, and `--report` as required arguments. No original-source execution instructions are provided here because author authorization for development is **not** permission for a subsequent source-content read. Before a real run, conduct a separate scoped approval and review the local scratch disk availability and limits. The original data remains only on the author's Mac.

**Provenance classifications:** The old report's SHA-256 is **author-supplied**, synthetic test results are **assistant-local**, and GitHub workflow checks (if completed) validate **the exact committed source**, not original ESA bytes.
