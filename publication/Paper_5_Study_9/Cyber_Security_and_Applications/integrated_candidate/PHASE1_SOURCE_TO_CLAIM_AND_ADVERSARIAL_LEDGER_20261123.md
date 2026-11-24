# Paper 5 Phase 1: closest-work source-to-claim and adversarial ledger

Date: 2026-11-23. Scope: Studies 9 and 10 only. Status: `MANUSCRIPT_ONLY_AND_SOURCE_CITATION`; NOT independent replication of outside papers. No new studies, dataset fields, or original-source releases.

## Exact manuscript target and claim boundaries

The new closest-method table `tab:priorcompare` is an **objective/estimand** comparison, not a quantitative head-to-head benchmark or proof that any named prior work lacks features we did not inspect. The source-evidence section `tab:stud10scope` is a bounded review of published release representations. The exact all-unknown result `C_d(g) = {0,1}^8` is conditional on the original zero-qualified-field mapping and frozen selector; it is not an empirical detector-quality or spacecraft recovery result.

| Citation key | Independently checked primary record | Supported source-level statement | What we MUST NOT claim |
|---|---|---|---|
| `nist2022ground` | [NIST IR 8401](https://csrc.nist.gov/pubs/ir/8401/final), DOI 10.6028/NIST.IR.8401; CSRC abstract and record | Applies CSF to satellite ground-segment command/control | That it performs (or fails) our exact eight-state dataset analysis |
| `mccarthy2023hsn` | [NIST IR 8441](https://csrc.nist.gov/pubs/ir/8441/final), DOI 10.6028/NIST.IR.8441; CSRC abstract | CSF profile covers interfaces in hybrid satellite networks with varying assurance | That it verifies our four downstream actions |
| `sahakian2021airss` | [Sandia AIRSS source record](https://www.sandia.gov/ccr/staff/srideep-musuvathy/), report SAND2021-11864 | Adaptive intrusion response for space systems is already a research objective | That the AIRSS modeling structure has been independently reproduced or fully compared |
| `akbar2023ontology`, `rodriguez2026harmonization` | Original entries retained in Paper 5 bibliography; prior DOI audit matched records | Ontology/label harmonization concern semantic comparability | That semantic interoperability as a concept is original here |
| `le2026trace` | [TRACE (Electronics 2026)](https://www.mdpi.com/2079-9292/15/15/3291), DOI 10.3390/electronics15153291; abstract, introduction, method description and contribution statements reviewed | Maps calibrated IDS outputs to action sets and release gates, with conformal/feasibility conditions; compares across IDS benchmarks | That action sets or uncertainty-aware release gating are original, or that TRACE lacks an uninspected operator authorization mode |
| `li2026rtef` | [RTEF-IDS (Mathematics 2026)](https://www.mdpi.com/2227-7390/14/17/3030), DOI 10.3390/math14173030; abstract, findings and supplement section reviewed | Differentiates evidence admission, feedback, history replacement and authorization; includes reproducibility artifact | That independent evidence governance is novel, or that RTEF replicates mission recovery |
| `guarino2026hybrid` | [FGCS 2026 publisher listing](https://www.sciencedirect.com/science/article/pii/S0167739X25006004) and [DBLP author record](https://dblp.org/pid/53/8957.html), DOI 10.1016/j.future.2025.108306 | Industrial CPS knowledge-based intrusion-response decision support has an active literature | That every implementation assumption, baseline or evaluation result has been inspected; complete publisher full-text inaccessible at review |
| `zhang2025uncertainty` | [Computers & Security 2025](https://www.sciencedirect.com/science/article/pii/S0167404824004589), DOI 10.1016/j.cose.2024.104153, publication metadata and accessible abstract | Examines cybersecurity decision-support uncertainty in security-control effectiveness and investment domain | That this study performs the same semantic source-admission test |
| `esaad2025v2`, `esaad2024v1`, `opssat2024v2`, `ruszczak2025opssatbenchmark` | Versioned Zenodo DOIs 10.5281/zenodo.15237121, 10.5281/zenodo.12528696, 10.5281/zenodo.15108715; Scientific Data DOI 10.1038/s41597-025-05035-3 | Public releases support telemetry/anomaly detection benchmark research and expose specified metadata schemas | That the whole spacecraft lacks recovery functions or that v1/v2 annotation differences imply telemetry conversions |

## Source-inventory provenance for source-scope table

Evidence is the previously rehashed Phase 1 schema report `Study10_G4_06_Schema_20261123T061027Z.json`, SHA-256 `36aca9592b52ad6da0c78039d6f3c41ea4a0b1e09473a2fb88bc426aced8ab8c`, and the original Tier A data package. The schema report has four ESA v2 metadata tables for M1 (`anomaly_types.csv`, `channels.csv`, `labels.csv`, `telecommands.csv`); five for M2 (those four plus `events.csv`); three for M3 (`anomaly_types.csv`, `channels.csv`, `labels.csv`). OPS-SAT `dataset.csv` has 23 published first-line header fields and `segments.csv` has 8. The nested ESA directory totals (224 channel + 821 telecommand ZIP members) came from an author-local outer-ZIP central-directory check; the report's expected digest was not independently validated against uploaded bytes. This is **not** a complete release payload audit.

## Adversarial outcome and unresolved risk

1. A reviewer can truthfully say that the all-unknown selector result is a deterministic truth-table consequence of the chosen eight-variable interface, with no source-dependent action diversity. The revised text now says exactly this.
2. TRACE and RTEF-IDS demonstrate that action sets, evidence contracts, and uncertainty-aware release are existing methodological areas. The new paper must NOT advertise any of those constructs as newly invented.
3. No inspected prior work is a matched replication of the exact Study 9/Study 10 question, but the accessible literature does not prove originality across all papers. Novelty survives only as a **narrow research arrangement and reproducible source-to-action evaluation**, not a new general theorem or deployed security technology.
4. NIST guidance and the industrial response study motivate security relevance, not empirical flight effectiveness.
5. The externally published Study 10 representations are narrow and not a probability sample of flight missions. Missingness is qualified at the documented schema level.

Phase 1 source-to-claim ledger outcome: `DOCUMENTED_WITH_LIMITATIONS`. Scientific-significance challenge remains `OPEN_EDITORIAL_JUDGMENT`. A full-text head-to-head review of the hybrid industrial CPS paper would strengthen confidence but is not required to describe its documented high-level objective. No scientific data, action policy, or original study result was changed.
