# Study 10 — post-G3 parity audit and pre-G4-06 decision boundary

**Study:** S10-RSEI-001 (Paper 5). **Audit date:** 2026-11-23 UTC.  
**Status:** `G3_SYNTHETIC_PARITY_RECONFIRMED_FROM_CI_LOGS; G4_06_NO_GO_NOT_AUTHORIZED`.  
**Scope of latest author response:** “yes, I authorize” after review of G3 technical completion, which permits continued read-only validation and preparation. It does **not** specifically reverse the earlier explicit refusal of G4-06 original-data execution, GitHub merges, or publication. No new author execution grant is inferred.

## 1. Source of truth: GitHub CI evidence, not a reported claim

Draft PR #252, exact tested head `6026ab85faeb8fa9815216cbd2443888404ff752`, contains the synthetic implementation; draft PR #253, head `1028098b14b90fd7aaba793a54ffa914162b7576`, is its additive evidence record.

The G3 GitHub Actions workflow run [#45120125893](https://github.com/Zartharas/mission-aware-satellite-cyber-recovery/actions/runs/45120125893), job **#137511746401** (“Frozen synthetic control and independent oracle checks”), was independently retrieved again through the connected GitHub service. It reports **completed/success**. All seven job steps completed successfully.

The **original CI job logs** were retrieved, and explicitly report:

| CI observation | Verified log content |
| --- | --- |
| Exact repository-native unit tests | `Ran 22 tests ... OK` |
| Frozen synthetic cases | `cases_passed=18`, `cases_total=18` |
| Complete Boolean selector/oracle parity | `exhaustive_comparisons=1024`, `mismatches=0` |
| Four primary policies / 256 states each | Pinned harness implementation and the logged 1024 check |
| Mutation/negative-control detection | `test_deliberately_incorrect_selector_is_detected ... ok` |
| CI stop flags | `G4_06_authorized=false`; `PR_merge_authorized=false` |
| End-of-job assertion | `G3_SYNTHETIC_ONLY_PASS_NO_G4_06_NO_MERGE` |
| Ephemeral metadata-only report SHA-256 from logs | `401b6174cb733befc49250d3c22a3b943e7d1302b8fdb007a60af0522c844cff` |

The report's SHA-256 is **verified as a literal CI-log output**. The ephemeral JSON file was **not independently received or rehashed** here; report-byte verification is not claimed. The prior independent local source bundle likewise does not replace the successful original-G1 GitHub integration check.

## 2. Adversarial review of the execution boundary and artifacts

The exact five-file PR #252 diff was reviewed: `study10/g3_independent_oracle.py`, `study10/g3_synthetic_parity.py`, `study10/test_g3_synthetic_parity.py`, one GitHub Actions workflow, and a method/authorization memo. PR #253 adds **two evidence documents only**. Neither PR is merged.

The independent oracle's source is a standalone four-policy decision table **without importing Study 2**. The comparison harness loads the pinned production selector solely for parity checking and enforces:
- **Five Git blob-pinned allowlisted repository inputs**, including the G1 fixture, G2 manifest and receipt, G3 case inventory and frozen selector.
- **Selector SHA-256** `3bd5b607095807acf93a929d6d67c5cc1d2f592e5b0650c14032a7724e5f5505`, in addition to its blob SHA-1 `6ac7d0767a719c6305a5a47555cc9d0cfc74fa23`.
- **Exactly 18 frozen cases including baseline P0**, not 18 negative cases plus P0; six static action examples, plus exhaustive four-policy parity on 256 complete Boolean states.
- **Missing versus known-false** distinctions, accepted-value equality over ten criteria, inclusive synthetic time boundaries, complete accepted-claim contradiction semantics, protection against false source independence, and rejected invalid/unknown Boolean selector inputs.
- A fail-closed, metadata-only report with `G4_06_authorized=false`, `PR_merge_authorized=false`, `original_telemetry_processed=false`.

The workflow runs on scoped pull requests with **`permissions: contents: read`**, pinned checkout action and disabled persistent checkout credentials; it has no deployment, publishing, merge or source-data access step. Review of code and job logs supports **synthetic-only scope**. This review is *not* a formal security proof, third-party rights-holder confirmation, independent human peer review or spacecraft recovery validation.

**Methodological caution:** The synthetic `signature_valid=true` is a test-interface assumption, **not an actual Ed25519 verification**. The parity result means the standalone oracle agrees with the frozen policy selector on its complete Boolean input domain; agreement does **not** validate the original policy's external safety, source-data observability, or the validity of any operational decision.

## 3. G3 technical go / G4-06 operational no-go

| Gate | Audited outcome | Implication |
| --- | --- | --- |
| **G3 synthetic implementation + independent technical-oracle parity** | **Technical PASS** | Meets the frozen G3 synthetic parity prerequisite at exact tested implementation commit |
| G4-01 — ESA v2 source rights | Prospective R1 documentary `PASS_CONDITIONAL` | No universal exception-free statement |
| G4-02 — ESA v1 source rights | `PASS_CONDITIONAL_IF_USED` | Optional paired v1/v2 release sensitivity only |
| G4-03 — OPS-SAT v2 source rights | Prospective R1 documentary `PASS_CONDITIONAL` | Data-inclusive MIT and provenance/notice limits retained |
| G4-04 — Hack-A-Sat | **Excluded** | Not a fifth stratum |
| G4-05 — source identity/notice preflight | **Current, point-in-time PASS** (9/9 dual hashes, 10/10 notice plan) | New source/notice identity check at any future separately approved execution boundary |
| **G4-06 — original-source semantic adjudication / execution** | **NO-GO: NOT AUTHORIZED** | No ESA/OPS telemetry content may be accessed for scientific classification |
| GitHub PR merges / paper publication | **NOT AUTHORIZED** | Keep all PRs draft and unmerged |

The frozen G2 receipt `study10/G2_PROTOCOL_FREEZE_RECEIPT_20261122.json` (blob `38e5da5edc193b358012bc9c2c3180917d7419ac`) records the historical G3/G4 holds at freeze time. Those original records are **unchanged**. The explicit author G3-only approval and subsequent technical evidence are **post-freeze additive**, not a retroactive mutation of that receipt.

## 4. Future G4 preparation without G4 access

The allowed *next preparation step*, if useful, is a documentation-only G4-06 execution-boundary checklist: rights/R1 provenance, fresh source identities and notices, exact eight-variable semantic rubric, no preselected favorable outcome, expected possibility of `ABSENT`/`AMBIGUOUS`, and stop on missing defensible decision time or newly conflicting file-specific terms. No G4 science runbook or mapping task may actually **open or parse** an ESA/OPS-SAT file until the sole author explicitly authorizes **G4-06**, and then only after the required contemporaneous local integrity/notice checks.

Retain four descriptive primary strata × eight recovery-state variables = **32 predeclared classification slots**. ESA v1 is conditional paired sensitivity and must never be counted as an independent fifth stratum. G3 synthetic action tables do **not** provide empirical spacecraft recovery percentages or safety outcomes.

**No new tests or source reads were performed for this audit.** The existing successful G3 integration is sufficient for the pinned code version; do not rerun tests only to inflate an evidence count. A material future code or synthetic-contract change would require a new appropriately scoped parity validation.

**Final:** `G3_TECHNICAL_AUDIT_PASS; G4_06_SOURCE_ANALYSIS_NOT_AUTHORIZED; PR_MERGES_NOT_AUTHORIZED; PUBLICATION_NOT_AUTHORIZED`.

Companion machine-readable record: `study10/G3_POST_PARITY_INDEPENDENT_CI_LOG_AUDIT_AND_G4_06_GATE_20261123.json`.
