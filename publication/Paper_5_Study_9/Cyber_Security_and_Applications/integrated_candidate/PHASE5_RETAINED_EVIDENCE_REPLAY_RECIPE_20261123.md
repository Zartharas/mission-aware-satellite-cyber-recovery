# Paper 5 retained-evidence replay recipe (read-only)

## Immutable source locations
- Study 9 baseline and selector: `5ee451c2a739cbca7dc948d49239d985c6b4cc07` in the project repository.
- Study 10 G2 payload: `8ed6a2b16233b86bf91672f6f15605dcf906c5eb`; review the receipt in branch `study10/s10-rsei-001-g2-freeze-receipt-20261122` and verify its pinned payload before any future work.
- Study 10 G3 audit/code snapshot: `04317102b87eb63312ba4e1599f87a3971858d03` (resolved exact branch head).
- Derived-only PR archive: `e8e9bd7a6d60d32eb9a03e83b1eba59a010bb7c1`, path `publication/Paper_5_Study_9/Cyber_Security_and_Applications/integrated_candidate/study10_derived/`. This is a Git snapshot, not a DOI-backed deposited release.

## Verification using an existing clean clone
Read-only checks below do not run the frozen selectors or original telemetry experiments. Do not use a working tree containing unrelated local data. Fetching accesses GitHub, not source datasets.

```bash
set -euo pipefail
git fetch origin
git cat-file -t 5ee451c2a739cbca7dc948d49239d985c6b4cc07
git cat-file -t 8ed6a2b16233b86bf91672f6f15605dcf906c5eb
git cat-file -t 04317102b87eb63312ba4e1599f87a3971858d03
REF=e8e9bd7a6d60d32eb9a03e83b1eba59a010bb7c1
DIR=publication/Paper_5_Study_9/Cyber_Security_and_Applications/integrated_candidate/study10_derived
git show "$REF:$DIR/S10_G4_TierA_32Slot_PublishedSchema.json" | shasum -a 256
git show "$REF:$DIR/S10_G4_TierC_16_StratumPolicy_NonEvaluable.json" | shasum -a 256
git show "$REF:$DIR/S10_RQ_E3_ESA_V1V2_Aggregate_Metadata.json" | shasum -a 256
```

Compare digests respectively to `f727bc80823d9fe5a47d44c361b9aefcdadc6b5a144331f2857079ce91508d1c`, `93dd4f92810a33f0dbe13dd11f842f732a4ccc9fac322a762fcab557185623f6`, and `ba343e858b4d54256f8f4d8b118bb87a95a49a0d99baebc394ac5517c418ddc9`. If a Git object is absent locally, fetch its named source branch or exact reachable ref; stop if unavailable. See `study9/results/S9-RTSI-001_CANONICAL_RUN_20260914/output_sha256_manifest.json` for canonical Study 9 output pins. Check the manuscript's editorial validator against the 56 stored field labels and candidate/excluded field names; this is not semantic re-adjudication.

## Original-data reproduction is a separate activity

Identify CuCD-ID v3, AegisSat 2025 and UNSW-IoTSAT 2026 using the versioned canonical Study 9 artifact verification files and population freeze. Retrieve the exact approved releases only after source rights and hashes are checked. Study 10 source releases: ESA v2 DOI 10.5281/zenodo.15237121, ESA v1 DOI 10.5281/zenodo.12528696, OPS-SAT v2 DOI 10.5281/zenodo.15108715. Verify the original archive hashes against the frozen source records; do not deserialize untrusted nested pickles. Use the G2/G3 pinned method and check actual metadata inventory and field visibility. Original source replay and independent semantic adjudication require separate authorization. Author-reported ESA layout JSON and local paired-detail CSV remain unavailable here. Do not redistribute raw archives, channel IDs, original rows or private reports; conditional source-rights notices remain. A derived-only archival release requires explicit authorization and rights review.

This recipe was prepared and source paths inspected; the shell commands were not executed in the author's local clone. The static archived-result checks are recorded separately.
