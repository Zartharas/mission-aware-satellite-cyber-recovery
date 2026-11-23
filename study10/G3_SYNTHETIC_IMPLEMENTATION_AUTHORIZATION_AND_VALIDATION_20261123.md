# Study 10 (S10-RSEI-001) — G3 synthetic-only implementation and technical-oracle validation

**Record date:** 2026-11-23 UTC  
**Decision:** `G3_SYNTHETIC_ONLY_IMPLEMENTATION_AND_PARITY_AUTHORIZED; G4_06_NOT_AUTHORIZED; PR_MERGES_NOT_AUTHORIZED`

## Exact sole-author authorization

> I authorize G3 synthetic-only implementation and independent technical-oracle parity testing against the frozen 18-case specification and four Study 2 policies. I do not authorize real-source telemetry processing, G4-06, PR merges, or publication.

This authorization **supersedes the historical G3 NOT_AUTHORIZED status prospectively only**. The original frozen G2 Option B receipt (Git blob `38e5da5edc193b358012bc9c2c3180917d7419ac`), the original frozen Study 2 selector, Study 9 semantics, G1 fixture, and prior G3 readiness inventory are **not modified**. Neither GitHub code execution nor synthetic parity implies G4-06 approval.

## Exact source and implementation pins

- Source selector: `study2/src/study2_security/selectors.py`, SHA-256 `3bd5b607095807acf93a929d6d67c5cc1d2f592e5b0650c14032a7724e5f5505`; Git blob `6ac7d0767a719c6305a5a47555cc9d0cfc74fa23`.
- Source G1 synthetic specification: `study10/G1_SEMANTIC_CONTROL_SPEC_DRAFT_20261121.md`, Git blob `29c97ef13c8bc92b51f09a1b3ad033dba9371081`; actual pinned v3 positive fixture extracted dynamically by ID `S10_SYN_P0_V3_DRAFT`.
- Source G2 case manifest: `study10/G2_FREEZE_MANIFEST_CANDIDATE_20261121.json`, blob `a20ca25c439d97150c56eeec197cc891c83aa1ad`.
- Frozen G2 receipt: `study10/G2_PROTOCOL_FREEZE_RECEIPT_20261122.json`, blob `38e5da5edc193b358012bc9c2c3180917d7419ac`.
- Static pre-execution G3 inventory: `study10/G3_STATIC_SYNTHETIC_ORACLE_READINESS_INVENTORY_20261123.json`, blob `001dfbc88d642ba507dd7cd1868c99fe49cb3fed`.
- **New implementation:** `study10/g3_independent_oracle.py` and `study10/g3_synthetic_parity.py`, plus `study10/test_g3_synthetic_parity.py` and PR-only `.github/workflows/study10-g3-synthetic-parity.yml`. All are additive to a **draft/unmerged** branch.

## G3 test specification and method limits

1. **Independent technical oracle:** `g3_independent_oracle.py` does **not** import or call the production Study 2 selector. It expresses the four policy outputs as a separate four-row decision table. `g3_synthetic_parity.py` loads the hash-pinned production selector only in the **comparison harness**.
2. **Frozen synthetic case population:** exactly **18** cases, including `P0_BASE`, all sixteen other synthetic mutations and the cohort-mixing guard, matching both the pinned G1 mutation ledger and G2 manifest. The suite isolates the four time-only cases from the 1050 accepted-claim snapshot; no nonsensical retiming of the full accepted ledger.
3. **Exhaustive selector parity:** **256 complete Boolean states × four frozen primary policies = 1,024 comparisons**. The four `S2_ABL_*` policies are excluded. Six frozen G1 static expected-state examples are additional checks, not independent spacecraft trials.
4. **Strict observability:** `UNKNOWN` is never passed to the Boolean selector or silently mapped to false. `N_CRC`, `N_APID`, `N_TIME`, `N_LABEL`, and `N_COMMAND` cannot become operational decision evidence by lexical substitution. Fully specified synthetic failures remain distinct from unknown observability.
5. **Synthetic claims:** ten accepted current claim IDs and the exact ten required-value dictionary must match. Accepted-claim **value equality**, ledger inventory completeness, claim count, same-subject/key/epoch contradictory accepted values, synthetic trust membership, and time boundaries are controlled independently. `signature_valid=true` is **only an asserted synthetic interface premise**, never a demonstrated Ed25519 verification.
6. **Fail closed:** any frozen Git blob or selector hash mismatch, unknown case, omitted expected case, static-oracle difference, incomplete non-Boolean state or 1,024-state mismatch sets a non-success status. The report identifies failures without reading any original satellite dataset.
7. **Source access:** the new harness opens only a hardcoded list of five **tracked specification/code files**. It takes a repo path and optional report path, **no ESA/OPS-SAT/Hack-A-Sat telemetry input path**. It does not analyze raw datasets, make network calls, create a publication or merge code.

## Validation evidence and remaining integration checkpoint

In a local isolated test environment, using an exactly reconstructed and **SHA-256 verified** copy of the frozen Study 2 selector, the standalone oracle and harness passed **25 synthetic regression tests** and produced **0 disagreements in 1,024 exhaustive selector-oracle comparisons**. It also passed the test that deliberately replaces the production selector with a wrong always-proceed variant and verifies mismatches are detected. The local reconstructed G1 fixture exercises the same documented synthetic contract but is not the actual complete pinned GitHub Markdown file; these results are **not yet the pinned repository-wide integration result**.

For that final integration check, the GitHub PR workflow must run on the actual branch, whose G1 specification, manifest, G2 receipt and static inventory are verified by Git blob SHA-1 and the selector is verified by SHA-256. The repository-native tests cover the exact G1 source, all eighteen cases, six static expectations, unknown/known distinctions, synthetic ledger rules, and exhaustive parity. **Do not claim full G3 signoff until that actual pinned integration run is observed PASS and its evidence recorded.**

A separate conversation-downloadable, SHA-256-pinned standalone reproducibility bundle `Study10_G3_Synthetic_Parity_Bundle_V1.zip` was prepared with the fuller **25-test** local test suite and a Mac runner. Bundle SHA-256 `07dc5fcb6bba1ccc2812575da14f4cdeaad4ebfe452db3b494fb88eeb13148fc`. The ZIP is **not** committed to GitHub; the new code modules and repository-native integration test/CI are text files on this draft branch. No upload of datasets or Mac source paths occurs.

## Research-governance separation

| Gate | Status after implementation authorization |
| --- | --- |
| G3 synthetic implementation/parity | **AUTHORIZED**; full exact-G1 pinned integration PASS to be independently confirmed |
| R1 ESA v2 and OPS-SAT v2 rights | Conditional documentary eligibility; no third-party exception-free warranty |
| R1 ESA v1 comparator | Conditional, optional paired release sensitivity only |
| G4-05 | Current 9/9 dual-hash and 10/10 prospective notice checks PASS at earlier recorded timestamp; future execution-boundary recheck required |
| **G4-06** | **NOT AUTHORIZED** |
| PR merge | **NOT AUTHORIZED** |
| Real telemetry reading, derived source publication | **NOT AUTHORIZED** |

A synthetic-only PASS cannot establish cryptographic recovery assurance, real spacecraft security, field-level G4 semantic observability or any empirical numerator/denominator for the four primary source strata × eight recovery variables. No native spacecraft field has been classified or observed in this G3 step.

**Disposition:** `G3_SYNTHETIC_IMPLEMENTATION_COMMITTED_DRAFT; WAIT_FOR_PINNED_INTEGRATION_EVIDENCE; G4_06_BLOCKED`.
