# Research Tracker

Last updated: 2026-09-03

## Current focus

**The repository contains two separately frozen empirical studies supporting the existing journal research article plus a separately frozen deterministic modeled companion study, Study 8 (`S8-PQC-ICR-001`). Study-1 science remains frozen at 720 VALID observations. Study-2 Phase 7 remains `PRESPECIFIED_ANALYSIS_RESULTS_FROZEN_CANONICAL`. Study 8 is now `TECHNICALLY_CLOSED_PUBLICATION_INTEGRATION_NOT_STARTED` after a frozen 3,456-position canonical campaign, independent reproduction with 0 mismatches, prespecified statistical analysis, independent statistical reproduction, SHA-256 results freeze, exact-head merge through PR #89, and successful post-merge `main` CI. No new Study-1, Study-2, or Study-8 scientific execution is authorized by this tracker.**

The existing `publication/` directory remains the **Study-1/Study-2 journal-article package**. Study 8 is a separate companion-paper research stream and must not be silently inserted into that manuscript. A later explicit publication-integration gate is required before Study-8 manuscript or submission work begins.

This is a **journal/research publication workflow**, not a dissertation-revision workflow. The prior dissertation relationship remains a disclosure/prior-dissemination consideration only.

## Current canonical repository state

### Existing Study-1/Study-2 journal article

- Study-2 Phase-7 results merge: `49c62cbed3fb8fc318e44d696faba1854ed6c21a`
- Study-2 Phase-7 canonical closeout main commit: `2bd3fb34ca709127e45ea9bffa8f516846d6c4b5`
- journal integration PR: `#72`
- journal integration merge commit: `6f9a1a5d26287120278913d453b26c78f267870f`
- post-integration current-state closeout PR: `#73`
- local clean-worktree audit isolation PR: `#74`
- current journal assembly authority: `publication/manuscript/MANUSCRIPT-ASSEMBLY.md`
- current Study-2 freeze authority: `study2/PHASE7_RESULTS_FREEZE.json`
- current Study-2 provenance authority: `study2/PHASE7_PROVENANCE.json`
- current Study-2 Phase-6 release-review record: `study2/release/phase6/`

### Study 8 companion study

- experiment ID: `S8-PQC-ICR-001`
- results-freeze PR: `#89`
- final validated PR head: `1356b73d1edc01c8618c9290460f4fbf22c458df`
- canonical science/results merge commit on `main`: `63106778559c3127a7d6e8765d52939b73a3f35b`
- post-merge repository validation run: `33761681328` — attempt `1` — `SUCCESS`
- current Study-8 technical-close authority: `study8/STUDY8_TECHNICAL_CLOSE.json`
- current Study-8 human closeout: `study8/docs/PHASE8_7_TECHNICAL_CLOSE.md`
- current Study-8 results-freeze authority: `study8/analysis/RESULTS_FREEZE_MANIFEST.json`
- current Study-8 checksum authority: `study8/analysis/RESULTS_FREEZE_SHA256SUMS.txt`

Historical work-package and phase documents may retain stage-local status wording because they are provenance. They must not be read as the current repository state when a later canonical closeout exists.

## Study 1 — frozen scientific record

Study 1 remains unchanged:

- frozen design: 24 cells × 30 valid repetitions;
- statistical population: **720 VALID observations**;
- retained INVALID attempts: **9** outside statistical membership;
- one additional interrupted never-ledgered attempt retained/quarantined outside membership;
- 696-observation final-commit complete-block analysis: sensitivity only;
- no additional Study-1 runtime is required or authorized.

### Study-1 immutable identities

- 720-valid analysis-membership SHA-256: `a2bf0c8f352f4386e74a500d97ea8f73e0c39d03bfe10ac0ebcf02470af9f70e`
- authoritative attempt-history ledger SHA-256: `92893a2fd8746f410bffd4dca5101bc3f533ada2ff82f98681788cf0c24ce6fd`
- deterministic campaign-tree SHA-256: `ad1e127b4431b6b334955129fcba82f76b18e5b43585395ac8c37300cac087b1`
- Study-1 reproducibility-hardened code snapshot: `99892bd9bb0828bdb3d0a28caf40dbc18fcbc4dc`
- Zenodo version DOI: `10.5281/zenodo.22181540`
- Zenodo concept DOI: `10.5281/zenodo.22181539`

The Zenodo v1.0.0 record is the **Study-1 evidence-of-record** and must not be described as containing Study-2 or Study-8 observations.

### Study-1 principal journal boundaries

- P1 remains unsupported on the predeclared M01/M02/M03/M06 outcomes.
- C1 is modeled/synthetic contact, not real ground-contact timing.
- T1 is omission/reduction of selected policy-visible evidence, not a stale/contradictory/forged-evidence factorial.
- P7 is a frozen deterministic rule-based selector, not AI/ML.
- the 696-observation final-commit analysis is sensitivity only.
- no weighted global P5 score or universal policy ranking is supported.
- no operational spacecraft, RF, operator-timing, flightworthiness, or certification claim is supported.

Historical Study-1 campaign/provenance details remain in `docs/26-wp9-r069-campaign-closeout.md`, `docs/27-wp9-cryptographic-integrity-freeze.md`, and the WP10 evidence/audit documents. The tracker no longer duplicates all per-position incident detail because those immutable records remain authoritative.

## Study 2 — canonical Phase-7 closeout

Experiment ID: `S2-AEATR-001`

Study-2 campaign and analysis are complete:

- **3,872 VALID observations**;
- **0 INVALID attempts**;
- **85 cells**;
- 162 primary paired contrasts;
- 432 prespecified secondary contrasts;
- independent reproduction mismatches: **0**;
- status: `PRESPECIFIED_ANALYSIS_RESULTS_FROZEN_CANONICAL`.

### Study-2 immutable identities

- Phase-6 artifact ID: `9816191406`
- Phase-6 artifact ZIP SHA-256: `195860bd44b38ccf170f02cb1cb392583217296d08640c99b18b52286403e133`
- observations SHA-256: `8dcc850c561d7e3c0bf7478263b534cae83cbbb55183c313e879dd7d61127854`
- attempt-ledger SHA-256: `755d6541263ac31589934200ea5071cdbcacae1ea197d044bbd3e6f7f7d1dbc5`
- trial-manifest SHA-256: `190612473717b7768ceccb4596a20d90cd7d532bf7581330ce94d609cb752e67`
- Phase-7 analysis-implementation main commit: `18207460fc5d419ad6a940f00db2df8610a5e5a0`
- Phase-7 analyzer SHA-256: `351039f0d6d79eb605c7dc027a5427da862b0f544815f862a85bc997df56c8bd`
- Phase-7 result ZIP SHA-256: `0136123a53d150437fefc8ace342af63b11d980cf8cab32ef7a4f03b78267417`
- independent auditor SHA-256: `3e738e2c27d621073a8c1bba49044df3fc83d099abdd244894537f4c4b22142d`

The exact Phase-7 result ZIP is durably retained in repository history under `study2/evidence/phase7/archive/`.

### Study-2 principal frozen findings/boundaries

**RQ1 — evidence mechanisms and bounded compromise**

- V1 omission, V2 stale/replay, V3 contradiction, and V4 post-signature manipulation changed B0/S1 behavior relative to V0 and reduced adjudicated unsafe-permissive rate by 1.0 under the frozen Block-A prerequisites.
- Under V5, B0/S1 reached evidence-qualified recovery while adjudicated unsafe-permissive remained 1.0. Policy-visible authenticated/current evidence therefore cannot be equated with objective correctness under the bounded producer-compromise model.
- B0 and S1 had identical primary endpoint estimates within Block A; comparisons against B2 are endpoint-specific trade-offs, not a global rank.

**RQ2 — contact/authorization**

- S1 evidence-qualified recovery occurred at 10/25/65/185/30 logical SIL seconds for K0/K1/K2/K3/K4 with unsafe-permissive rate 0.
- B0 produced an unsafe-permissive increase of +1.0 versus K0 at each non-K0 contact profile.
- K4 is an intermittent/flapping profile and is not ordinal severity 4.
- logical SIL seconds are not real spacecraft/network/operator latency.

**RQ3 — ambiguity control**

- all 54 C-family BENIGN/ADVERSARIAL contrasts were zero;
- 0/54 Holm-adjusted contrasts were rejected;
- the frozen cause label does **not** change hidden truth or generated policy-visible evidence within each ambiguity family;
- therefore this is a **structural label-invariance/control result**, not empirical evidence of discrimination or non-discrimination between genuinely different benign and adversarial causal mechanisms.

**RQ4 — context ablations**

- specific mission/contact/security-context ablations changed specific endpoints;
- these n=32 blocks are secondary sensitivity/estimation evidence, not small-effect confirmatory evidence;
- the results do not identify a universal dominant context variable.

**RQ5 — adversary-budget stress**

- A3/K0 produced residual unauthorized state in all evaluated policies while B0/S1 could still reach evidence-qualified recovery;
- A2/K2 is a **coupled producer-compromise/contact-loss profile** and cannot be reported as an unconfounded adversary-only effect.

No weighted global policy score or global policy rank is supported by Study 2.

## Study-2 archive state

The Phase-7 **result** artifact is durably retained in Git history. The underlying Phase-6 **source-evidence** artifact is hash-bound, and its original GitHub Actions retention is temporary.

The exact source ZIP has now passed responsible-release review. The recorded decision is:

`APPROVED_FOR_PUBLIC_DURABLE_ARCHIVE_WITH_PROVENANCE_WRAPPER`

The review verified 3,872 ledger rows against 3,872 observations; 0 ledger/observation identity mismatches; 0 recomputed observation-hash mismatches; 0 recorded file-hash mismatches; exact 85-cell/block membership; and no identified credentials, tokens, private keys, email addresses, URLs, IPv4 addresses, local absolute paths, operational spacecraft/RF/proprietary mission data, human-subject data, or unsafe ZIP paths. The review performed no campaign runtime and changed no frozen science or source-evidence record. Repository documentation is retained under `study2/release/phase6/`.

**Remaining pre-submission archive gate for the existing journal article:** publish the exact approved source ZIP to a new durable DOI-bearing archive, verify the publicly served ZIP checksum, and insert the actual DOI/archive identity into the journal Data Availability statement and target package. Do not invent a DOI and do not reuse the Study-1 Zenodo DOI.

## Study 8 — canonical technical close

Experiment ID: `S8-PQC-ICR-001`

Study 8 is a deterministic finite modeled contact/crypto-agility/recovery study. It is not pooled with Study 1 or Study 2 and is not currently part of the existing two-study journal manuscript.

### Study-8 canonical population and audit

- frozen population: **3,456 modeled observations**;
- primary canonical rows: **3,456**;
- independent implementation-level recomputation rows: **3,456**;
- exact row matches: **3,456**;
- row mismatches: **0**.

### Study-8 immutable identities

- canonical observations SHA-256: `cfc65b6663be4e9f17a00ed102730f8642efcbbd844045acce032ff09a0bcabf`
- primary findings SHA-256: `26a8ac4d1039917323e75a294775dd14a2b563adb12a5d2fcdb47ce8f15c992e`
- independent findings SHA-256: `26a8ac4d1039917323e75a294775dd14a2b563adb12a5d2fcdb47ce8f15c992e`
- interpretation audit SHA-256: `620827f83fb566ff6ceae1b66c8f51f61ef8e5bbdabbb1c4b5a48b5187a82413`
- results-freeze manifest: `study8/analysis/RESULTS_FREEZE_MANIFEST.json`
- results-freeze checksums: `study8/analysis/RESULTS_FREEZE_SHA256SUMS.txt`

### Study-8 frozen findings

Primary trusted-recovery success is exactly tied across all four policies:

- `P0_HARD_CUTOVER`: `635/864`
- `P1_STAGED_CUTOVER`: `635/864`
- `P2_HYBRID_OVERLAP`: `635/864`
- `P3_CONTACT_AWARE_STAGED`: `635/864`

The prespecified primary contrast is:

`P3 - P1 = 0/1 = 0.000000 percentage points`

This negative primary result is frozen. No hypothesis rescue or policy-success superiority claim is supported.

Profile-level success is:

- `PROFILE_512_44`: `1080/1152`
- `PROFILE_768_65`: `748/1152`
- `PROFILE_1024_87`: `712/1152`

Across all 1,152 matched non-profile positions, trusted-recovery success is non-increasing as the modeled standardized cryptographic-object budget increases.

### Study-8 inference and claim boundaries

- the 3,456 positions are the complete deterministic finite factorial population, not a probabilistic sample;
- no sampling p-values, sampling confidence intervals, bootstrap inference, or permutation inference are supported;
- logical slots are model indices, not spacecraft/network/operator wall-clock time;
- standardized ML-KEM/ML-DSA object bytes are modeled cryptographic-object burdens, not measured onboard PQC execution cost;
- no operational spacecraft, RF-link, ground-station, energy, flightworthiness, certification, or production claim is supported.

### Study-8 technical-close provenance

- final results-freeze PR: `#89`
- exact validated head: `1356b73d1edc01c8618c9290460f4fbf22c458df`
- squash merge commit on `main`: `63106778559c3127a7d6e8765d52939b73a3f35b`
- post-merge repository validation: run `33761681328`, attempt `1`, `SUCCESS`
- status: `TECHNICALLY_CLOSED_PUBLICATION_INTEGRATION_NOT_STARTED`

The Phase-8.6 results-freeze manifest remains immutable and therefore still contains its historical pre-merge `results_merge_authorized=false`. The later Phase-8.7 merge authorization is preserved by PR #89 review/merge provenance and the merge commit; the frozen Phase-8.6 file is intentionally not rewritten.

## Current journal-manuscript state

The existing two-study journal manuscript integration is complete and merged in PR #72:

- `publication/manuscript/03-methods.md` — Study 1
- `publication/manuscript/03-study2-methods-extension.md` — Study 2
- `publication/manuscript/04-results.md` — Study 1
- `publication/manuscript/04-study2-results-extension.md` — Study 2
- `publication/manuscript/05-discussion.md` — cross-study synthesis
- `publication/manuscript/06-conclusion.md` — combined bounded conclusion
- `publication/manuscript/study2-claim-traceability.csv` — Study-2 claim boundary register
- `publication/tables/table-r7-study2-prespecified-findings.csv` — Study-2 findings summary
- `publication/tables/table-s2-study2-secondary-holm.csv` — Study-2 secondary-family multiplicity summary

The Study-1 and Study-2 populations must remain separate throughout that manuscript. Study 8 is **not yet integrated into `publication/`** and will require a separate companion-paper publication gate.

## Historical Study-1 work packages

The original WP0–WP11 program remains historically closed:

| ID | Work package | Historical status | Current interpretation |
|---|---|---|---|
| WP0 | Research workspace | Complete | retained infrastructure/provenance |
| WP1 | Literature and novelty | Complete — empirically reconciled | Study-1 framing retained; two-study novelty is integrated in the current journal manuscript |
| WP2 | Theoretical/conceptual model | Complete — empirically reconciled | Study-1 Mission Aware framing remains bounded |
| WP3 | Threat and mission model | Complete — empirically reconciled | Study-1 claim boundaries retained |
| WP4 | Testbed selection/architecture | Complete | historical Study-1 environment retained |
| WP5 | Deterministic event library | Complete | historical Study-1 event implementation retained |
| WP6 | Response-policy implementation | Complete | historical Study-1 policy implementation retained |
| WP7 | Trusted-recovery implementation | Complete | historical Study-1 recovery implementation retained |
| WP8 | Pilot | Complete | historical pilot record retained |
| WP9 | Frozen Study-1 campaign | Complete | 720/720 valid; integrity freeze PASS |
| WP10 | Study-1 analysis/manuscript | Complete | historical Study-1 analysis closed; current two-study article integration is outside this historical WP numbering |
| WP11 | Study-1 responsible artifact release | Complete | Zenodo v1.0.0 published |

No `WP12` is created for the historical Study-1 program. Study 8 uses its own explicit `Phase 8.x` records under `study8/`; those records are a separate research stream and do not reopen or renumber the closed Study-1 work packages.

## Current exact action

Completed for the existing Study-1/Study-2 article:

1. stale-current-state cleanup across README/publication/submission/reproducibility surfaces;
2. release-gate hardening for the two-study journal state and Study-2 frozen identities;
3. full repository CI on the exact journal-integration head;
4. reviewer/CI correction of identified stale or misleading wording without changing frozen statistics;
5. journal-integration merge to `main` as PR #72 / `6f9a1a5d26287120278913d453b26c78f267870f`;
6. post-integration status closeout through PR #73;
7. local release-gate isolation through PR #74 and local exact-commit clean-worktree validation at `6bb0051628ec64ebd09a85435f88a6a0d2cfc382`, including 611 research tests, frozen WP10 reproduction, and zero drift;
8. responsible-release review of the exact Study-2 Phase-6 source-evidence ZIP, disposition `APPROVED_FOR_PUBLIC_DURABLE_ARCHIVE_WITH_PROVENANCE_WRAPPER`, with no campaign execution or frozen-science modification.

Completed for Study 8:

9. Phase 8.0 standards/literature review, protocol/contact/population lock, and adversarial design review;
10. Phase 8.1 primary implementation plus independently written reference implementation, with design amendment before runtime;
11. Phase 8.2 pre-runtime CI, non-canonical fixture parity, and SHA-256 implementation binding;
12. Phase 8.3 exact-head pre-runtime merge and successful post-merge CI;
13. Phase 8.4 single-use canonical execution of exactly 3,456 observations plus 3,456 independent recomputations with 0 mismatches;
14. Phase 8.5 prespecified finite-population statistical analysis plus independent statistical reproduction and interpretation audit;
15. Phase 8.6 12-file SHA-256 results freeze preserving the negative primary finding;
16. Phase 8.7 final review, exact-head PR #89 merge to `63106778559c3127a7d6e8765d52939b73a3f35b`, and successful post-merge run `33761681328`;
17. current-state Study-8 repository indexing/technical-close synchronization before publication work.

### Next actions — separate gates

**Existing Study-1/Study-2 journal article:**

18. publish the exact approved Study-2 source-evidence package to a new durable DOI-bearing archive;
19. independently verify the publicly served source ZIP SHA-256 against `195860bd44b38ccf170f02cb1cb392583217296d08640c99b18b52286403e133`;
20. insert the actual DOI/checksums into Data Availability and target materials;
21. proceed to final Computers & Security live-portal checks and exact-export claim/citation/DOI/scope audit.

**Study-8 companion paper:**

22. only after repository synchronization is complete, open a separate publication-integration gate;
23. build a dedicated Study-8 manuscript/package from the frozen science without changing or rerunning it;
24. perform literature/venue/current-guideline verification, tables/figures, claim traceability, data/code availability, and submission-package review as publication work rather than new experimental science.

## Scientific and responsible-research boundaries

Preserve throughout publication and future work:

- controlled defensive software simulation/modeling only;
- no real spacecraft access;
- no RF transmission/interference claim;
- no real ground-contact, network, or operator timing claim;
- immutable research truth never acts as a runtime policy oracle;
- unexpected treatment-valid outcomes remain evidence rather than being removed for presentation;
- no post-hoc seed replacement, outcome-dependent exclusion, or new campaign execution to improve journal or companion-paper results;
- no weighted global score or global policy rank;
- Study-1 and Study-2 frozen populations remain separate;
- Study 8 remains a separate deterministic finite modeled population and is not pooled with either empirical study;
- Study-8 negative primary policy result remains frozen;
- Study-8 standardized cryptographic-object byte effects must not be restated as measured onboard PQC CPU/energy/RF performance;
- any new experimental execution is a new replication/validation study with its own frozen identity.
