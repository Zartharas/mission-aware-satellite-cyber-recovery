# Study-2 Phase-6 Responsible-Release Review

## Release decision

**Decision:** `APPROVED_FOR_PUBLIC_DURABLE_ARCHIVE_WITH_PROVENANCE_WRAPPER`

The exact frozen Study-2 Phase-6 source-evidence ZIP is suitable for public durable archiving as research data, provided it is preserved byte-for-byte and accompanied by provenance/safety documentation.

No source-evidence record was edited, regenerated, redacted, normalized, or re-zipped during this review.

## Frozen source identity

- experiment: `S2-AEATR-001`
- source artifact: `study2-phase6-evidence-24ed05f4d52611754ac91ad1a74c5bcf242245ac.zip`
- GitHub Actions artifact ID: `9816191406`
- workflow run: `33547420437`
- source ZIP SHA-256: `195860bd44b38ccf170f02cb1cb392583217296d08640c99b18b52286403e133`
- observations SHA-256: `8dcc850c561d7e3c0bf7478263b534cae83cbbb55183c313e879dd7d61127854`
- attempt-ledger SHA-256: `755d6541263ac31589934200ea5071cdbcacae1ea197d044bbd3e6f7f7d1dbc5`
- trial-manifest SHA-256: `190612473717b7768ceccb4596a20d90cd7d532bf7581330ce94d609cb752e67`

## Content reviewed

The source ZIP contains exactly five evidence files:

1. `attempt_ledger.jsonl`
2. `evidence_hashes.json`
3. `campaign_summary.json`
4. `observations.jsonl`
5. `runtime_bindings.json`

The archive contains no packet captures, RF recordings, operational spacecraft telemetry, production credentials, private certificates, real cryptographic keys, user home-directory paths, endpoint addresses, or proprietary mission data.

## Integrity findings

- 3,872 attempt-ledger rows were present.
- 3,872 observation rows were present.
- All 3,872 attempts were `VALID`; 0 were invalid.
- All 3,872 trial IDs were unique.
- All 3,872 run IDs were unique and followed the frozen campaign order.
- Ledger/observation identity mismatches: 0.
- Recomputed per-observation SHA-256 mismatches: 0.
- All file hashes recorded in `evidence_hashes.json` matched the extracted files.
- Cell count: 85.
- Frozen block membership matched exactly: Block A 18 cells/1,728 observations; Block B 20/640; Block C 18/576; Block D 20/640; Block E 9/288.
- Every observation identifies its time basis as `DETERMINISTIC_LOGICAL_SIL_TIME_NOT_WALL_CLOCK`.
- `oracle_was_selector_input` was false for all 3,872 observations.
- ZIP entry-path safety checks found no absolute paths, parent traversal, or backslash path abuse.

## Security and privacy findings

No release-sensitive occurrences were found for:

- passwords, passphrases, credentials, bearer material, API/access keys, private-key/PEM material, GitHub-token patterns, AWS access-key patterns, JWTs, cookies, or sessions;
- email addresses, URLs, IPv4 addresses, localhost/loopback references, or user-local absolute paths;
- human-subject data, operational spacecraft data, RF data, or proprietary mission telemetry.

The package contains SHA-256 digests, deterministic seeds, synthetic experiment/run/trial identifiers, and synthetic security-state labels. These are research provenance, not live secrets.

## Authorization provenance nuance

`runtime_bindings.json` records the Phase-6 campaign authorization as it existed when the source artifact was created: `active=true`, `consumed=false`. This is a historical pre-run provenance snapshot, not a current credential and not permission to rerun the campaign.

The canonical post-campaign repository state records the same authorization as `active=false`, `consumed=true`. No new Study-2 campaign is authorized by this release review.

## Responsible-research boundary

The data were generated in researcher-controlled software-in-the-loop conditions. They do not represent an operational spacecraft, ground station, RF link, production certificate infrastructure, real key theft, proprietary telemetry, or access to systems outside researcher control.

The archive must not be described as demonstrating operational exploitation, jamming, spoofing, flight readiness, certification, or production autonomous recovery.

## Licensing assessment

The source package consists of author-generated research data and provenance metadata. Under the repository license classification, original research data are intended for CC BY 4.0. The source ZIP does not embed third-party software source code; `runtime_bindings.json` records repository paths and SHA-256 identities only.

## Publication recommendation

Publish the exact source ZIP unchanged to a **new Study-2 dataset record** with the responsible-release documentation. Do not replace the frozen ZIP with a rewritten derivative as the evidence-of-record, and do not represent the existing Study-1 Zenodo record as containing Study-2 evidence.

After publication, independently verify the publicly served source ZIP SHA-256 against `195860bd44b38ccf170f02cb1cb392583217296d08640c99b18b52286403e133`, then insert the actual DOI/archive identity into the manuscript and target submission package.

**Responsible-release review status:** `PASS`
