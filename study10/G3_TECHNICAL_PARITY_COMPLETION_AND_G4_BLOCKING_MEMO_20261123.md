# Study 10 — G3 synthetic technical-oracle parity completed

**Date recorded:** 2026-11-23 UTC  
**Study:** S10-RSEI-001, standalone scientific paper (Paper 5).  
**Result:** `G3_SYNTHETIC_TECHNICAL_PARITY_PASS`.  
**Execution boundary:** `G4_06_NOT_AUTHORIZED; PR_MERGES_NOT_AUTHORIZED; PUBLICATION_NOT_AUTHORIZED`.

## Author decision and exact tested implementation

The sole author expressly authorized:

> I authorize G3 synthetic-only implementation and independent technical-oracle parity testing against the frozen 18-case specification and four Study 2 policies. I do not authorize real-source telemetry processing, G4-06, PR merges, or publication.

The newly implemented G3 is isolated to draft PR #252, exact tested head `6026ab85faeb8fa9815216cbd2443888404ff752`. The independent oracle (`study10/g3_independent_oracle.py`) uses an independently authored decision table and does **not** import the production selector. The comparison harness (`study10/g3_synthetic_parity.py`) imports the **exact content-pinned** frozen selector under a dedicated module name and validates the immutable G1 fixture/manifest/receipt/source code identities before evaluation. Only synthetic named claims, observed Boolean interfaces and counterfactual truth states are evaluated; **none** of the original nine ESA/OPS-SAT source files or Hack-A-Sat data is read.

The frozen Study 2 selector SHA-256 remains `3bd5b607095807acf93a929d6d67c5cc1d2f592e5b0650c14032a7724e5f5505`. The frozen G1 fixture Git blob is `29c97ef13c8bc92b51f09a1b3ad033dba9371081`; G2 receipt blob `38e5da5edc193b358012bc9c2c3180917d7419ac`; G3 pre-execution case inventory blob `001dfbc88d642ba507dd7cd1868c99fe49cb3fed`. The existing frozen records were **not modified**.

## Actual GitHub integration evidence

The read-only, PR-triggered workflow [Study 10 G3 synthetic-only oracle parity](https://github.com/Zartharas/mission-aware-satellite-cyber-recovery/actions/runs/45120125893) completed **successfully** on the exact PR #252 head.

| Verified execution item | GitHub CI result |
| --- | --- |
| GitHub Actions run / job | `45120125893` / `137511746401` |
| Repository-native integration regression tests | **22/22 PASS** using the actual pinned G1 fixture |
| Exact frozen G2/G1/Study2 integrity checks | **PASS**, validated in the runner before comparison |
| Frozen synthetic cases | **18/18 PASS**, including P0 and source-mixing rejection |
| Six static policy-state examples | **PASS**, four policy actions each |
| Complete Boolean combinations | **256/256 per policy** |
| Independent oracle / pinned production selector | **1,024/1,024 parity PASS**, zero mismatches |
| Incorrect-selector mutation test | **PASS**, intentionally wrong implementation detected |
| G4-06 and PR merge restrictions | CI assertion **PASS**, both false |
| Original telemetry | **None accessed** |

The CI runner reported `G3_SYNTHETIC_PARITY_PASS_NOT_G4_AUTHORIZED`, and the final job assertion printed `G3_SYNTHETIC_ONLY_PASS_NO_G4_06_NO_MERGE`. The ephemeral metadata-only CI report was hashed in the GitHub job logs as SHA-256 `401b6174cb733befc49250d3c22a3b943e7d1302b8fdb007a60af0522c844cff`. **The complete ephemeral report bytes were not uploaded to this chat or committed to GitHub**, so this digest is a CI-log observation rather than a secondary local independent rehash.

The prior isolated local engineering tests also passed 25/25 cases and a separate 1,024-comparison parity pass against a byte-identical frozen Study 2 selector. These local tests used a reconstructed G1 fixture, so the successful GitHub job using **the real exact G1 file** is the decisive integration checkpoint. The downloadable source/test-only reproducibility ZIP `Study10_G3_Synthetic_Parity_Bundle_V1.zip`, SHA-256 `07dc5fcb6bba1ccc2812575da14f4cdeaad4ebfe452db3b494fb88eeb13148fc`, is optional; **no Mac action is necessary** merely to confirm this already successful GitHub G3 integration.

## Coverage, uncertainty and nonclaims

- The G3 18-case result tests **synthetic state-interface correctness and fail-closed distinctions**: accepted-value equality versus key presence, known-false versus unknown, time boundary inclusivity, subject/key/epoch contradictions, synthetic accepted-claim ledger completeness, CRC versus signature evidence, identifier versus trust, offline labels versus operational guards, command status versus authorization availability, and dataset-replication guard rejection.
- The synthetic fixture's `signature_valid=true` is an explicitly **assumed interface input**, **not a real Ed25519 verification**. Passing synthetic tests does not demonstrate actual spacecraft cyber-recovery effectiveness, flight safety, source telemetry observability, or externally independent peer review.
- The four primary descriptive strata × eight recovery variables = **32 future classification slots** remain prospective; ESA v1 is optional paired sensitivity only, not a fifth independent stratum. No G4 RQ-E1/E2/E3 native-source observation, G5 row-level selector endpoint, or manuscript result is produced here.
- The existing approved R1 **source documentary eligibility is conditional**, not a declaration that unknown third-party rights are absent.
- The earlier G4-05 current local preflight of **9/9 frozen dual-hash identities and 10/10 prospective notices** remains valid **only at its recorded time**. If the sole author separately authorizes real-source scientific G4-06 later, that future execution boundary requires its own exact identity/notice recheck.
- Existing GitHub draft PRs remain **unmerged**. There was no original-source upload, public data redistribution, rights-holder outreach, or publication/submission.

## Gate disposition

| Gate | Result after actual G3 integration |
| --- | --- |
| G3 — synthetic technical implementation and oracle parity | **PASS** under the author's explicit G3-only execution authorization |
| G4-01 / G4-03 — ESA v2 / OPS-SAT v2 rights | R1 documentary eligibility conditional PASS, unchanged |
| G4-02 — optional ESA v1 rights | Conditional PASS **if used**, unchanged |
| G4-04 — Hack-A-Sat | Excluded |
| G4-05 — identity/notice plan | Point-in-time current PASS; recheck immediately before any later separately approved G4-06 work |
| **G4-06 — scientific original-source semantic analysis** | **NOT AUTHORIZED** |
| PR merges, original data release, manuscript submission | **NOT AUTHORIZED** |

**Final:** G3's specified synthetic technical parity prerequisite is completed and auditable. This is **not an authorization request or approval for G4-06**. No new Mac action, external validation, or another synthetic control run is warranted for this technical checkpoint. The original G2 freeze records and historical gate statuses are preserved; this is an additive post-freeze evidence record, not a retroactive rewrite.

*Research-reproducibility assessment, not independent human peer review, cryptographic flight attestation, or an operational safety claim.*
