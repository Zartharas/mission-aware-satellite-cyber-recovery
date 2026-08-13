# WP4 D-064 V6 Static-Verification PASS Governance — 2026-08-13

**Decision:** `D-063R2-C3B-I2D-D064-V6-SV1`  
**Source commit:** `967caf73fe73186f685df6296b58466062182f0c`  
**Source tree:** `811f6686c9ba304c2e4785ad964576bb4cce40e7`  
**Contract transition:** `0.4.21` → `0.4.22`  
**Source contract SHA-256:** `798bf3e93ab70118d70899b917ba3ae8a4b469d84d24f7f78ef041d5d18268b8` (174722 bytes)  
**Successor contract SHA-256:** `98756e1d56792355582e18e41ee11e8897da306aad18da98ee73c66776c4bad2` (188107 bytes)  
**State:** `STATIC_VERIFICATION_PASS_INDEPENDENT_REVIEW_PASS_D064_DECISION_ELIGIBLE_NOT_AUTHORIZED_RUNTIME_NOT_AUTHORIZED`

## Publication basis

The successor contract is byte-for-byte identical to the independently reviewed
`0.4.22` proposal:

- proposal preparation script SHA-256: `cf415d86cb1cd52574df4053260182d7bdfd1da994738db71867b35f79768991`
- proposed contract SHA-256: `98756e1d56792355582e18e41ee11e8897da306aad18da98ee73c66776c4bad2`
- proposal governance record SHA-256: `a5cd02a01d40792ef523a9e62e930a3ef9e1614dbefca7cdeba287610d0d9fad`
- proposal governance lock SHA-256: `8823dbb9db36d73f76d9e13b09bb5b713b67666ef9d41b1b36bd56e0ae3c146d`
- proposal contract diff SHA-256: `57f5c5ae813cc9e011edd5f7ea76d910a8da5dbf99ffc10c36712198fc349c6e`
- proposal manifest SHA-256: `37c6386312de3ea1ac744b6a685773c8403e1bdf5625994e4f6172f8fdca3966`
- independent proposal-review script SHA-256: `7689d59dd170662f79f7d58ca8cce95714808398c42a7d6e00e6599f3c588642`
- independent proposal-review result: **PASS**
- independent proposal-review findings: **0**
- independently reconstructed successor contract: **byte-identical PASS**
- independently regenerated contract diff: **PASS**
- residual active V5 runtime/execution authority: **absent**
- residual V6 runtime/execution authority: **absent**

No additional successor-contract mutation was made after that independent review.

## V6 accepted implementation and static evidence

- transaction-v4 SHA-256: `aa96c912a2311ee8c2edec2d5bbfbaf90f0387f78476f9fe80a83773c10c2d1d`
- receiver-v1 SHA-256: `64ecadbd0c8c8d69e5509bb7bbe9115bfe8ebc812961eaf77f8ec3331168726c`
- generator-v6 SHA-256: `2a2b7a5a1438831908af27b9c9cb6d4a0d4cd633ceb964c4f71a5df2a1beda83`
- verifier-v6 SHA-256: `23bc9cf4d8676882b39ac51979ac9de9f839f42bb819d24cdea416de9bb0d98d`
- accepted V6 candidate SHA-256: `185522b1e6a3b52a1e141f4ad82a994595895c407fa4d98bbf2685f9098c818f`
- accepted V6 candidate bytes: `82416`
- formal negative-suite item count: `36`
- formal stdout SHA-256: `a1c2a585e6e6e274b31b211b254fec2a25c372808cc6c29f8b8da4fa3a73dfc5`
- formal execution single-use sentinel SHA-256: `26948f8ce1af1dab69c38f94b9a9ab0c14d86783eab54c2871bd5ea0924f026c`
- independent formal-evidence review script SHA-256: `fe29dec0c0a6cafb449680a1754e4d5ffa58d066e3e29b3e2e6ec50c3710ca17`
- formal static verification: **PASS**
- independent formal-evidence review: **PASS / 0 findings**
- formal verifier rerun authorized: **false**

## V5 supersession

The prior V5 single-use authorization is retained as historical provenance but is
withdrawn as an active execution path because V6 supersedes the V5 architecture.

- historical V5 authorization granted: **true**
- V5 authorization consumed: **false**
- V5 execution attempts: **0**
- active V5 D-064 authorization: **false**
- active V5 execution authorization: **false**
- active V5 runtime authorization: **false**
- V5 superseded without consumption: **true**

This is supersession/withdrawal, not attempt consumption.

## V6 active governance state

- D-064 authorization-decision eligible: **true**
- D-064 authorized: **false**
- D-064 authorization consumed: **false**
- D-064 execution authorized: **false**
- D-064 execution attempts authorized: **0**
- D-064 execution attempts: **0**
- runtime authorized: **false**
- runtime attempts: **0**
- production candidate execution count: **0**
- production materialization count: **0**
- schema-1 production fallback allowed: **false**
- Execution #11 rerun authorized: **false**
- WP5 execution authorized: **false**

## Scientific interpretation

This governance publication records acceptance of the V6 implementation for a
future separately authorized bounded D-064 experiment. It is not runtime evidence
and does not establish a scientific outcome.

## Next research step

`SEPARATE_V6_D064_SINGLE_USE_AUTHORIZATION_AND_BOUNDED_RUNTIME_ATTEMPT_REQUIRED`

After publication of this governance state, the remaining WP4 research-critical
work is the bounded V6 D-064 observation, evidence analysis, and WP4 closeout.

No candidate execution, production materialization, Docker/NOS3/Fortytwo runtime,
event injection, command transmission, baseline execution, schema-1 fallback,
Execution #11 rerun, or WP5 activity is authorized by this record.
