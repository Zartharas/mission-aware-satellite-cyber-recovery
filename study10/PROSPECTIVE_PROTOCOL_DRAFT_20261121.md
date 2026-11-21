# S10-RSEI-001 — Prospective external-applicability protocol (DRAFT)

**Working title:** Recovery-State Semantic Observability Across Public Real-Flight and Space-Cyberchallenge Records  
**Research relationship:** prospective extension to Paper 5, **not** a revision or continuation run of frozen Study 9 (`S9-RTSI-001`).  
**Prepared:** 2026-11-21 (UTC date); repository reference: `Zartharas/mission-aware-satellite-cyber-recovery`, `main` at `660683a6561274bdbeadc84a5000436e8c5d5d1f`.  
**Identifier:** `S10-RSEI-001` is **provisional**; a default-branch search found no `study10/` directory or `S10-` code-search hits. Reserved status on unexamined branches or other projects has **not** been established.  
**Status:** `DRAFT_FOR_REVIEW_NOT_PREREGISTERED_NOT_FROZEN`; **no source-level semantic adjudication, dataset-row analysis, selector execution, new results, or publisher submission authorized**.

## 1. Purpose and scientific boundary

Assess whether existing, public, independently acquired space telemetry and competition records provide **operationally interpretable inputs** for the eight-value recovery-state interface already defined in frozen Study 9. Evaluate which values, if any, are represented natively, are demonstrably derivable using rules locked in advance, remain ambiguous, or are absent. A subsequent *separately authorized* execution may assess bounded decision identifiability under the frozen Study 2 selector, but is **not** a validation of spacecraft recovery performance.

The term **external applicability** is deliberate. Independent external data can challenge an interface's applicability and transfer claims; it does not by itself validate recovery effectiveness, on-orbit authorization, cybersecurity attack detection, or generalization to all missions. If the future manuscript uses “external validation,” it must name the precise construct validated (e.g., field-mapping rubric stability, not operational recovery).

### Prior exposure / prospective integrity declaration

Before this draft, an intake had already inspected archive metadata, channel counts, selected schemas, OPS-SAT labels and split counts, and Hack-A-Sat file headers. This is **not fully blind preregistration**. The prior exposure and outcomes are explicitly listed in the provenance register. No new per-dataset eight-variable mapping matrix or selector-identifiability result is asserted here. Freeze the protocol **before** performing those adjudications, and report any outcome-informed modifications as deviations rather than rewriting this draft.

## 2. Cohort structure and independence

| Cohort | Version / units | Role | Dependence and restrictions |
|---|---|---|---|
| ESA Anomaly Dataset (ESA-ADB) v2 | Zenodo `10.5281/zenodo.15237121`; Mission1, Mission2, Mission3 each a separate mission stratum | **Candidate primary real-flight cohort** | Three missions are within one release/source family, not three independent consortium replications. Nested telemetry records not yet inspected. |
| OPS-SAT-AD | Ruszczak et al. (2025); 2,123 annotated segments from nine channels | **Candidate independent real-flight cohort** | Segment labels are anomaly annotations, not cyberattack or authorization truth. Multiple segments per channel are clustered. |
| ESA-ADB v1.0 | Zenodo `10.5281/zenodo.12528696`; matched to the same three ESA missions | **Matched version-sensitivity cohort only** | Never a fourth-to-sixth independent source or an independent replication of v2. |
| Hack-A-Sat 4 | `cromulencellc/hackasat-finals-2023` at commit `2cb4b5a50ed2835d97b5f07ac4467ea210bcb7f1`, `HAS4_FULL_GAME` | **Secondary, explicitly separate challenge-context cohort** | Competition scoring input; record-level provenance as actual on-orbit observation is unestablished. Never pool with real-flight sources. |
| NASA SMAP/MSL | Hundman et al., 2018 | **Deferred comparator; not currently in a primary cohort** | Requires a separately pinned artifact and provenance audit, with methodological concerns recorded before any inclusion. |

**Primary-source selection is provisional** until permissions, inner-archive structural metadata, schema meaning, observation granularity, and field visibility checks pass. A source with zero relevant decision fields must **remain included** once the population is frozen; poor semantic coverage is not an exclusion criterion.

## 3. Research questions (prospective; not results)

- **RQ-E1 — Semantic observability:** For each eligible source stratum, which of the eight recovery-state variables are `DIRECT`, `DERIVABLE_BY_PREDECLARED_RULE`, `AMBIGUOUS`, or `ABSENT`, and which classifications are operationally visible at decision time?
- **RQ-E2 — Source-type contrast:** How do the predeclared mapping classes differ among ESA flight missions, OPS-SAT telemetry segments, and independently reported Hack-A-Sat competition records, without treating them as exchangeable observation populations?
- **RQ-E3 — Release sensitivity:** Do any semantic classifications change between ESA v1 and v2 when the same mission and channel IDs are compared under the same rubric? How many changes are only source metadata additions or corrections?
- **RQ-E4 — Bounded decision interface (conditional gate):** Where an admissible native recovery-state assignment can be reconstructed under predeclared visibility/timing rules, what is the set of actions reachable under *every* admissible completion of unknown state using a separately integrity-pinned, frozen Study 2 selector? Where the operational decision point is unsupported, report `NOT_EVALUABLE` for operational-row claims instead of fabricating timing or authorization state.
- **RQ-E5 — Positive-control validity (synthetic only):** Can an independently specified synthetic fixture with explicit provenance and all eight known decision values be correctly mapped and processed by the evaluation harness, while negative controls (offline label, CRC, source ID, timestamps without validity windows, command presence) remain ineligible shortcuts?

**No directional hypotheses or anticipated coverage scores are asserted.** Null, zero, ambiguous, and not-evaluable findings are valid outcomes.

## 4. Fixed target interface and permitted mapping classes

The eight names and meanings come from the *existing frozen* `study9/RECOVERY_STATE_MAPPING_RUBRIC.json` and `study9/SEMANTIC_ADJUDICATION_FREEZE.json`; they must not be silently redefined here:

| Variable | Required meaning at decision point | Examples of invalid shortcuts |
|---|---|---|
| `signature_valid` | Cryptographic signature verification outcome under a known source public key | packet checksum or CCSDS CRC |
| `source_trusted` | Evidence source membership in verifier's trusted-source set | APID or source name alone |
| `fresh` | Evidence issue/validity interval contains the relevant decision time | telemetry timestamp alone |
| `epoch_valid` | Claimed evidence epoch equals expected epoch for its subject | sequence number or orbit epoch alone |
| `contradictory` | Accepted current same-subject, same-key, same-epoch claims contain competing values | divergent sensors without claim identity |
| `minimum_evidence_complete` | All ten frozen accepted recovery criteria are present | a complete packet or nonempty dataset |
| `security_signal` | Native operational guard/security signal visible to decision logic | offline anomaly/cyberchallenge label |
| `authorization_available` | Required authorization or authorized contact path exists at the decision point | telecommand presence or command log line |

Mapping classes use the **same definitions** as Study 9: `DIRECT`, `DERIVABLE_BY_PREDECLARED_RULE`, `AMBIGUOUS`, `ABSENT`. Evidence roles: `OPERATIONAL_NATIVE`, `OFFLINE_GROUND_TRUTH_ONLY`, `EXPERIMENT_METADATA_ONLY`, `DOCUMENTATION_ONLY`. The mapping rubric must be copied/reference-pinned with its SHA-256 at the future protocol freeze; any proposed exception or derivation is **new and separate**, explicitly justified and locked in this study. The frozen Study 9 derivation registry is empty; this draft does not add a derivation to it.

A `DIRECT`/derivable classification requires documented operational semantics, the required temporal context, source provenance, and unambiguous native field references. Correlations, flags without provenance, verbal similarity, and observed post-event correctness are insufficient. Missing values remain unknown; never impute a favorable, adverse, or preferred response.

## 5. Planned observational unit and analysis hierarchy

1. **Primary semantic mapping unit:** one `(source family, release, mission-or-OPS stratum, recovery variable)` tuple. ESA primary = three v2 mission strata; OPS-SAT = one source family with nine channels separately tracked. The primary denominator is **eight variables per stratum**, not telemetry rows or number of anomalous segments.
2. **Release sensitivity unit:** matched `(mission, channel ID, metadata attribute)` between ESA v1 and v2. Release matches are **paired**, not independent experiments. Explicitly distinguish metadata differences from changes to nested telemetry bytes.
3. **Secondary Hack-A-Sat unit:** the version-pinned dataset/interface, with separate CSV families and raw-telemetry archive; command and script logs cannot automatically establish cryptographic trust or operator authorization.
4. **Conditional operational unit:** if later permitted and decision-time semantics exist, a documented event/time-localized state with exact native field lineage. Each source needs a bespoke, frozen conversion rule before row-level processing; no post hoc joins or inferred decision times.
5. **Synthetic fixture unit:** deliberately constructed, marked `SYNTHETIC_ONLY`, independent of source-derived labels. It is a harness correctness control, never counted in empirical coverage.

Do not average source-family percentages into a single population estimate or treat time samples/segments/channels as independent trials.

## 6. Endpoints and estimands to freeze before execution

**Tier A: source-schema semantics, primary.** For each primary stratum and each of the eight variables, report mapping class, evidence role, exact field names, source-documentation citations, decision-time visibility, rationale, and uncertainty. Compute `DIRECT` count (0–8) and `DIRECT+DERIVABLE` count (0–8) only after an independently reviewed field-to-variable matrix has been frozen; fraction = count/8. Report the complete 8-element vector and unresolved count; never mask `AMBIGUOUS` as a “no” value.

**Tier B: matched metadata-release contrast, primary sensitivity.** Report channel matching counts; `(mission, channel)` categorical flags, unit metadata, exact paired-change counts, source-field meaning changes, and any resulting *prospectively defined* mapping-class transitions. Changed CRC and size are metadata signals, not independent proof of nested-file byte equivalence.

**Tier C: conditional bounded selector consequences, secondary and gated.** Only after a deterministic native-state projection and decision-time reference are explicitly frozen, enumerate the reachable action sets over all admissible assignments of unresolved variables for each of the four Study 9 primary-policy interfaces, **separately by policy**. A singleton set is *structural identifiability*, not correctness, safety, or recovery completion. A dataset lacking defensible decision-point reconstruction receives `NOT_EVALUABLE_FOR_OPERATIONAL_ACTION` and **no fabricated row-level rate**. An abstract “all-state-unknown” selector exercise, if later authorized, must be clearly labeled a mathematical sensitivity check, not dataset-native evidence.

**Tier D: engineered positive/negative controls, methodology verification only.** For preregistered synthetic 8-bit fixtures, compare the independent expected mapping and action enumeration with evaluator output. Failure indicates an implementation or contract fault. Synthetic fixture performance is never pooled with real source results.

Descriptive finite-population reporting only unless a pre-outcome amendment specifies a defensible sampling design and assumptions. No unregistered significance tests or population-level confidence intervals.

## 7. Controls, falsification, and audit strategy

Before **any** new semantic endpoint computation, lock the positive-control specification (known source/verification/decision-time values; at least one fully specified 8-value fixture; boundary cases for stale, wrong-epoch, contradictory and unavailable authorization states). Also lock negative-control rules for: label-to-security-signal laundering; CRC-to-signature inference; APID-to-trust inference; packet-time-to-freshness inference; CCSDS sequence-to-evidence-epoch inference; telecommand-to-authorization inference; and normal-segment-to-recovery-complete inference.

Use two independent reviewers or an independently implemented checker for the field classification and source-role schema where feasible. Capture disagreements **without looking at derived outcome summaries**, adjudicate from recorded sources, and preserve dissent/protocol deviations. Programmatic checks should verify source hashes, expected field names, record uniqueness, categorical encodings, and absence of cross-source pooling. At a future execution gate, independently reimplement the coverage arithmetic and bounded-action sets rather than relying on the canonical analyzer alone.

## 8. Known pre-outcome evidence and discrepancies (not findings of S10)

- **ESA archives:** six local source hash reports matched published Zenodo MD5 values; subsequent read-only directory inventory found no unsafe member paths. Reported local SHA-256s and structure are pinned in the companion register. The subsequent v1/v2 comparison detected only `ESA-Mission{1,2,3}/channels.csv` as differing *outer ZIP member metadata* in each mission; unchanged nested archive CRC/size **does not guarantee bytewise or semantic identity**.
- **ESA v2 `channels.csv`:** valid ZIP Deflate64 (compression method 9). macOS `unzip -p` returned CRC32/size-validated contents. Channel IDs remained 76/100/48 by mission; v2 added `Categorical` values with `YES` counts 0/10/44, exactly matching cleared `physical_unit_8` placeholders (0/10/44); all other common metadata fields were unchanged in the reported local comparison. This is **pre-study intake information**, not a newly computed semantic result.
- **OPS-SAT-AD:** `dataset.csv` contained 2,123 segments (1,689 nominal, 434 anomalous); 1,594 train and 529 test. The source paper's table text gives 1,494 train, inconsistent with component counts and uploaded CSV. The `segments.csv` text `label` was uniformly `anomaly` while integer `anomaly` distinguished 0 and 1. Do not treat the string as binary ground truth or either field as operational cyberattack recovery truth. The publisher issued a 2025 correction for figure ordering, **not documented as a correction of this count discrepancy**.
- **Hack-A-Sat 4:** four processed telemetry CSVs and the raw telemetry tarball matched the GitHub Git-blob identities in the locally reported inventory. An independent inspection of the user-supplied 16.4 MB GitHub source ZIP likewise matched all five SHA-1 blob IDs and SHA-256s. The release README explicitly excludes game-hosting infrastructure and certain emulation/cyber-payload code; dataset provenance is **competition scoring input**, not automatically flight observation.

## 9. Scope exclusions, rights, and operational safety

- No execution on a spacecraft, authorized command system, remote endpoint, flight hardware, control plane, or real mission network.
- No extraction of full ESA mission archives, bulk redistribution of telemetry, notebook execution, model training, injection, or attack simulation in this **draft-preparation** authorization.
- No reclassification of anomalies as attacks and no claim of flight-proven recovery or authorization.
- OPS-SAT-AD user-supplied license file is reported MIT; Hack-A-Sat top-level project indicates MIT generally but contains exceptions for cFS/COSMOS/OSK. **Per-file rights and reuse conditions must be checked before publishing derivatives**. ESA Zenodo records are public, but the precise reusable license terms and any payload-specific restrictions must be affirmatively confirmed prior to execution/public redistribution; access is not blanket permission to republish.
- NASA SMAP/MSL remains out of primary scope; do not add after outcome inspection. Source overlap between ESA dataset and OPS-SAT provider/curation should be examined even when missions differ; independence means separate acquisitions and missions, **not** guaranteed statistical independence.
- Original user data remain local; only hashes/metadata and licensed, non-sensitive documentation are proposed for Git versioning. Absolute home paths, private author information, and raw/third-party datasets stay out of repository commits.

## 10. Sequential authorization gates and stopping rules

| Gate | Condition | Current position |
|---|---|---|
| G0 — Source intake | Published identities, read-only archive metadata, licensed source descriptions | **PASS for identity/metadata as documented**; rights review open |
| G1 — Protocol review and population choice | Author approves this separate study's exact populations, units, endpoints, source rights, controls, exclusions, and reviewer/audit plan | **OPEN — this document is only a draft** |
| G2 — Preregistration/freeze | Time-stamped immutable protocol + source ledger hash, selector/rubric pin, schema preflight, no endpoint review | **CLOSED** |
| G3 — Implementation-only validation | Synthetic fixtures, negative controls, independent verification, strict no-source-data boundary | **CLOSED** |
| G4 — New real source semantic adjudication | Separate explicit approval after G2/G3; licensed access, independent field classifications | **CLOSED** |
| G5 — Conditional row-level/selector experiment | Separate explicit approval with decision-time evidence, resource budget, SHA-256-bound run manifest, and audit | **CLOSED** |
| G6 — Analysis/publication | Frozen, independently verified results; interpretation, originality, venue, and submission approval | **CLOSED** |

Stop and record an explicit deviation if any archive identity changes, rights remain unclear, an unsupported decision-time join is required, a positive control fails, a code/rubric hash changes, nested archive integrity fails, or another source is proposed after G2. No silent “fix” or favorable substitution. The original draft-preparation authorization permitted only local document drafting and validation. Subsequent explicit author authorization permits a dedicated GitHub documentation-review branch and draft pull request containing only this protocol and its two provenance-register files. A later explicit author authorization permits the documentation-only draft PR to be merged **after complete CI success and exact-scope review**, without freezing or approving the prospective protocol. It does not authorize scientific execution, dataset ingestion, model training, publisher upload, or changes to frozen Study 9 and the Paper 5 manuscript.

## 11. Review decisions still required to lock

1. Confirm `S10-RSEI-001` and new-study location; check all active branches and trackers at the chosen commit time.
2. Confirm ESA v2's three mission strata and OPS-SAT as the **primary** cohorts; decide whether Hack-A-Sat remains secondary-only.
3. Confirm exact decision-time eligibility and `NOT_EVALUABLE` policy before looking at row-level telemetry.
4. Verify source-specific license/reuse terms and whether all telemetry/derived outputs may be locally analyzed and published.
5. Freeze source manifest and accepted schema before setting the mapping matrix; independently review any proposed derivation registry (default empty).
6. Design and freeze synthetic positive and negative controls, including failure actions and independent verifier.
7. Only then consider a separate author authorization for implementation and later scientific execution. Preserve Study 9 and existing Paper 5 submission package unchanged.

**Documentation publication authorization (2026-11-21):** The author has separately approved review and merge of this *draft-only* documentation subject to CI and scope verification. This authorization does not approve cohorts, resolve ESA source licensing, lock semantic rules, freeze preregistration, or authorize any experiment. The documents retain their draft status after merge.

## 12. Evidence references and traceability

**Internal project (read-only):**
- `study9/STUDY9_PROTOCOL.json`
- `study9/RECOVERY_STATE_MAPPING_RUBRIC.json`
- `study9/SEMANTIC_ADJUDICATION_FREEZE.json`
- `study9/PRIMARY_POPULATION_FREEZE.json`
- `study9/results/RESULTS_FREEZE.json`
- `publication/Paper_5_Study_9/Cyber_Security_and_Applications/submission_package/SUBMISSION_PACKAGE_STATUS.json`

**Source records:**
- ESA-ADB v1.0: https://zenodo.org/records/12528696 (DOI `10.5281/zenodo.12528696`)
- ESA-ADB v2: https://zenodo.org/records/15237121 (DOI `10.5281/zenodo.15237121`)
- OPS-SAT-AD: Ruszczak et al., *Scientific Data* (2025), DOI https://doi.org/10.1038/s41597-025-05035-3; figure-order correction https://doi.org/10.1038/s41597-025-05751-w
- Hack-A-Sat 4: https://github.com/cromulencellc/hackasat-finals-2023/tree/2cb4b5a50ed2835d97b5f07ac4467ea210bcb7f1/game_data/HAS4_FULL_GAME
- NASA SMAP/MSL (deferred): Hundman et al., DOI https://doi.org/10.1145/3219819.3219845

**User-supplied local evidence:** `Paper5_OPSSAT_AD_ReadOnly_Intake_2026-11-21(1).md`, `Paper5_External_Dataset_Identity_Lock_2026-11-21.json`, `Paper5_External_Dataset_Metadata_Report_2026-11-21.json`; 2026-11-21 command outputs comparing ESA v1 and v2 outer-directory metadata and channel values; uploaded Hack-A-Sat repository ZIP. The companion machine-readable provenance register records which checks were local reports and which were independently repeated on the received ZIP.

**Drafting gate conclusion:** `DRAFT_FOR_REVIEW; DOCUMENTATION_ONLY_BRANCH_AUTHORIZED; NO_NEW_SCIENTIFIC_OUTCOME; NO_STUDY9_OR_MANUSCRIPT_CHANGE; NOT_PREREGISTERED`.