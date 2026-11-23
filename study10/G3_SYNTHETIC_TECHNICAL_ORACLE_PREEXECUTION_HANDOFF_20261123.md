# Study 10 (S10-RSEI-001) — G3 synthetic technical-oracle pre-execution handoff

**Record date:** 2026-11-23 UTC.  
**Status:** `G3_STATIC_READINESS_REVIEW_COMPLETE; G3_EXECUTION_NOT_AUTHORIZED; G4_06_BLOCKED`.  
**Intent:** Prepare a next-phase scientific-readiness record from frozen sources **without executing** a selector, synthetic harness or original-data analysis. The sole author's latest “yes, I authorize” is treated as continuation/readiness preparation, not as a new explicit grant overriding the prior G4-06 execution prohibition or GitHub merge prohibition.

## Why G3 is the next required gate

The frozen G2 receipt, `study10/G2_PROTOCOL_FREEZE_RECEIPT_20261122.json` (Git blob `38e5da5edc193b358012bc9c2c3180917d7419ac`), records **G3 synthetic implementation NOT AUTHORIZED**, **G3 independent technical-oracle parity NOT EXECUTED**, and **G4 source-semantic adjudication BLOCKED**. Its normative protocol is `study10/G2_CANONICAL_PROTOCOL_CANDIDATE_20261121.md` (blob `12e5a76fa14f2c61d5fddcbe4d6b86f5d2923527`). It requires actual **standalone code implementation and parity** before any real-source G4 work. Technical independence means separate oracle implementation code, **not** an external human reviewer.

The newest verified G4-05 record, `study10/G4_05_CURRENT_PREFLIGHT_VERIFIED_LOCAL_EVIDENCE_METADATA_20261123.json` (Git blob `6501040b83f9c8657dc99201361618622de26c94`), reports a Mac-local **9/9 dual-hash** and **10/10 prospective-notice-plan** PASS at 2026-11-23 05:21:59 UTC. Its JSON SHA-256 `4a035980a8f10e60f5a645071761088e45e062827c4e974d3fca43a1d26f7bfc` was independently recomputed against the uploaded sanitized report. This is **not** G3 technical parity or a permanent execution-boundary recheck. Prospective source-rights eligibility under author-approved R1 remains conditional; G4-06 and PR merges remain unauthorised.

## Exact existing frozen G3 synthetic contract

- Frozen design source: `study10/G1_SEMANTIC_CONTROL_SPEC_DRAFT_20261121.md`, Git blob `29c97ef13c8bc92b51f09a1b3ad033dba9371081`, preserved by the frozen G2 protocol. Exact synthetic positive fixture: `S10_SYN_P0_V3_DRAFT` (**synthetic interface stub only**, not an actual Ed25519 verification).
- Ten accepted, current **synthetic** claims linked one-to-one to the ten frozen recovery criteria, with required-value **equality** (not just key presence) and a complete synthetic same-subject/key/epoch claim inventory.
- Frozen normalized Boolean order: `signature_valid, source_trusted, fresh, epoch_valid, contradictory, minimum_evidence_complete, security_signal, authorization_available`. P0 assumed values: `true, true, true, true, false, true, false, true`.
- Four primary Study 2 policies in order: `S2_B0_FAIL_CLOSED`, `S2_B1_FAIL_OPERATIONAL`, `S2_B2_RISK_THRESHOLD`, `S2_S1_EVIDENCE_AWARE`. Exclude all four `S2_ABL_*` ablations from primary results. The original selector is pinned by SHA-256 `3bd5b607095807acf93a929d6d67c5cc1d2f592e5b0650c14032a7724e5f5505` and Git blob `6ac7d0767a719c6305a47555cc9d0cfc74fa23`.
- The frozen manifest lists **18 exact synthetic cases including P0**, not 18 negative cases plus P0. Their exact IDs, source-stated mutations and expected interface/coverage boundaries are transcribed in the accompanying machine-readable inventory `study10/G3_STATIC_SYNTHETIC_ORACLE_READINESS_INVENTORY_20261123.json`.
- Freshness uses the synthetic verifier's **inclusive** predicate `issued_at_s <= now_s <= issued_at_s + valid_for_s`; isolated boundary cases at 1000/1100 pass, 999/1101 fail, but **do not pretend the P0 accepted-claim snapshot at 1050 is contemporaneous at each boundary**.
- Missing verifier, expected epoch, trust-set membership, native guard or authorization path yields an **UNKNOWN** observability result, not `false`, `DIRECT` or a valid Boolean selector input. Distinguish `known_false` from `unknown`. Source files with no supported decision time produce `NOT_EVALUABLE_FOR_OPERATIONAL_ACTION`.
- Positive synthetic selector inputs are not spacecraft evidence and produce no Tier A/B/C coverage denominator or operational recovery claim.

## P0 static exact-selector expectation — not a test result

The **pinned source text and previously frozen G1 static review** predict the following results for P0 only:

| Primary policy | Statically derived, unexecuted expected action |
| --- | --- |
| `S2_B0_FAIL_CLOSED` | `PROCEED_TO_RECOVERY_GATE` |
| `S2_B1_FAIL_OPERATIONAL` | `PRESERVE_LIMITED_OPERATION` |
| `S2_B2_RISK_THRESHOLD` | `PRESERVE_LIMITED_OPERATION` |
| `S2_S1_EVIDENCE_AWARE` | `PROCEED_TO_RECOVERY_GATE` |

These predictions are **static derivations**, not proof that the selector or an independently written oracle produces them. The same frozen G1 source includes five other sample Boolean state expectations (freshness invalid, contradiction present, signal with/without authorization) and an explicit plan for all 256 complete Boolean states per policy. None was executed in this checkpoint. Do not “correct” frozen policy outcomes using desired recovery-safety intuitions; parity must be measured against the exact selector behavior.

## Exact G3 next-phase acceptance criteria, to be approved separately

1. Record a separate, explicit **G3 synthetic-only implementation and parity** authorization. Do not interpret the current generic continuation approval as permission to run it.
2. Create an independently coded selector oracle (no importing/calling the production selector), pin independent source and environmental dependencies, and compare with the frozen selector on synthetic inputs.
3. Test the exact 18 P0/negative/mutation cases and all four primary policies, including policy-specific 256-complete-Boolean-state parity. Record errors/differences without silently discarding failing cases.
4. Verify the 10-criterion evidence ledger, expected-value comparator, inclusive time limits, trust/epoch/contradiction semantics and unknown-versus-false fail-closed boundary. No claim that asserted `signature_valid=true` is a real cryptographic signature validation.
5. Require **G3 PASS before new source-semantic G4**; any failure blocks G4 and calls for a prospective, independently approved method change without modifying frozen G2/G3. Preserve all failure evidence and original code pins.
6. Keep all original ESA/OPS/Hack telemetry paths inaccessible to G3 and forbid source-row reading, repository merges, uploads, publication and any source-specific inference.
7. At any future **separately approved** G4-06 execution boundary, rerun the narrow nine-file identity/notice preflight to avoid treating a historical current PASS as timeless.

**G4 remains blocked.** The sole-author R1 evidence approval and existing G4-05 current PASS are complete as separate governance controls; neither is being requested a second time. A G3 authorization, if later given, must be limited to **synthetic-only** independent-oracle implementation/test execution, not G4-06, merging or publishing.

## Disposition

`G3_STATIC_PREEXECUTION_HANDOFF_PREPARED; G3_SYNTHETIC_EXECUTION_NOT_AUTHORIZED; G4_06_NOT_AUTHORIZED; PR_MERGES_NOT_AUTHORIZED`.

Frozen G2/G3 files are not edited. No synthetic cases, selector function, real dataset, scientific endpoint or manuscript publication was executed in this readiness documentation. No repository branch was merged.
