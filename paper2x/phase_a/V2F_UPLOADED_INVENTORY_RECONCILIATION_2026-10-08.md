# Paper 2 P2X — independent uploaded v2f inventory reconciliation

**Authority:** sole-author read-only scan on exact head `30cd02b9a5b61224893091c63b401dc49d554270`, closed by `aa5776a731e0e4a375b394123a892916871d3818`; workflow #1425 passed. This review uses the author's **uploaded original ZIP** only, not a second host scan.

## Verified evidence integrity

- Uploaded `v2f_full_source_inventory.jsonl` SHA-256: `edeba9101e56000a4ca1eb12f67105a05865627c5d39416db521991b6bf50e38`, matching the terminal-recorded hash.
- Uploaded `v2f_inventory_diagnostics.log` SHA-256: `f770806e11e3a452a37c8b6e4a8ca6fa0d35e0daa688d6237a58a286af043f88`, matching the terminal-recorded hash.
- One header, 50,617 entries and one terminal summary; zero invalid JSONL records or duplicate root-relative paths.
- Independently recomputed pre-summary digest: `e5fdf798b23b83026005fa03c534f3c02a5743641929da2760930062bc733eb9`, matching embedded summary.

## 20,089-file primary/repeat comparison

Both v2f source populations expose the same 24,742 relative entries (20,089 regular files, 4,642 directories, 11 symlinks); exactly **20,034 regular-file SHA-256 values match**, and **55 differ**. All 55 differences are in file digests, not relative path sets, file types, permissions, sizes, hardlink counts or symlink target values.

- 51 differing files: `.git/index` or `.git/modules/**/index` (Git index metadata).
- 4 differing files: `fsw/build/CMakeFiles/CMakeConfigureLog.yaml`, `fsw/build/amd64-nos3/default_cpu1/CMakeFiles/CMakeConfigureLog.yaml`, `gsw/build/CMakeFiles/CMakeConfigureLog.yaml`, and `sims/build/CMakeFiles/CMakeConfigureLog.yaml`.
- No qualified nine-output path is among the 55 differences.
- Differences are identified by path class; this uploaded report does not establish why Git or CMake emitted distinct bytes. **The source trees are not fully byte-identical**, and no variance is automatically excluded.

## Symlinks, FortyTwo and gap classification

Each source has 11 identical relative symlinks, confined to Yamcs examples/test paths. Their lexically resolved target paths appear as directories in the independent JSONL inventory. This is evidence of *lexical* containment and inventory presence, **not** physical runtime dereference or mount isolation. FortyTwo has 1,054 regular files, 79 directories, zero symlinks. The original inventory readback records the exact pinned FortyTwo executable hash as PASS; the uploaded JSONL reconfirms the recorded checksum/provenance, not a new read of the binary itself.

The source code-derived dependency matrix remains unresolved for cFS support libraries, runtime tables/configuration, dynamic loader dependencies, preflight path and IPC adaptations, and run-scoped writable derivations. The WP4 legacy materializer and historical exclusions are not promoted as v2f evidence.

## Decision

**INDEPENDENT UPLOADED JSONL REVIEW: COMPLETE.** Manifest integrity, scanned path coverage and 20,089-file primary/repeat comparison are independently evaluated. **55 hash variances remain**; treating the four CMake logs or 51 Git indexes as non-runtime without an exact-path policy is not yet authorized. The one-use host inventory authorization stays consumed.

**No** workspace copy, Docker/runtime launch, benign cFS NOOP, COSMOS, faults, scientific observations, final environment acceptance, or PR #215 merge is authorized. **Runtime dependency closure remains UNRESOLVED.**

Future work must classify the exact 55 variance paths, define and justify deterministic include/exclude and symlink semantics for a fresh runtime workspace, and separately authorize any materializer implementation or materialization activity.
