# Study 10 — prospective publication-source notices (draft, NOT yet inserted into a manuscript)

**Purpose:** Version-specific citation and attribution text for the standalone Paper 5 / Study 10 manuscript, **only if** separately authorized real-source research subsequently occurs and final source-rights review accepts the relevant source. This document **does not** attest dataset use, final license clearance, original-data publication, scientific findings, or actual publisher acceptance.

## 1. Version-specific reference list candidates

**ESA v2 — primary source, if later used**

De Canio, G., Kotowski, K., & Haskamp, C. (2025). *ESA Anomaly Dataset* (v2) [Data set]. European Space Agency. Zenodo. https://doi.org/10.5281/zenodo.15237121

**ESA v1 — conditional paired sensitivity only, if later used**

De Canio, G., Kotowski, K., & Haskamp, C. (2024). *ESA Anomaly Dataset* (Version 1.0) [Data set]. European Space Agency. Zenodo. https://doi.org/10.5281/zenodo.12528696

**OPS-SAT v2 — primary source, if later used**

Ruszczak, B. (2024). *OPSSAT-AD - anomaly detection dataset for satellite telemetry* (v2) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.15108715

**Metadata qualification:** The OPS-SAT Zenodo page renders the creator as “Bogdan, Ruszczak,” while its contributor data use “Ruszczak, Bogdan.” The normalized author used above is **provisional**, not a verified Zenodo citation export. Resolve that field before a journal-ready bibliography is declared.

**Associated OPS-SAT methods publication, if scientifically discussed**

Ruszczak, B., Kotowski, K., Evans, D., & Nalepa, J. (2025). *The OPS-SAT benchmark for detecting anomalies in satellite telemetry*. *Scientific Data*, 12, 710. https://doi.org/10.1038/s41597-025-05035-3 . The article includes an August 2025 correction, https://doi.org/10.1038/s41597-025-05751-w ; check publisher citation export and correction context at submission time.

**ESA methodology:** If benchmark design, annotations, or evaluation procedures are discussed, cite the applicable ESA benchmark methods publication in addition to the dataset DOI. Verify final bibliographic metadata independently; the dataset citation is not a substitute for method attribution.

## 2. Proposed release-specific attribution statements

**ESA attribution (conditional, after actual use and rights signoff)**

> The analysis draws on the European Space Agency's ESA Anomaly Dataset, version v2 (De Canio, Kotowski, and Haskamp, 2025; https://doi.org/10.5281/zenodo.15237121). The dataset's first-party project metadata identifies the Creative Commons Attribution 3.0 IGO license (https://creativecommons.org/licenses/by/3.0/igo/). This study is independent research and is not endorsed by the European Space Agency, its consortium partners, or the dataset contributors. The Methods section identifies any transformations undertaken by the author.

Do **not** claim that all contents were legally cleared solely by the repository metadata. When future methods contain changes or derivatives, describe which data or annotations were changed, at what level, and how the changes were applied. Do not imply original files were republished.

**ESA v1 conditional addendum (ONLY if paired sensitivity executed)**

> A separately identified, paired-release sensitivity analysis uses version 1.0 of the ESA Anomaly Dataset (De Canio, Kotowski, and Haskamp, 2024; https://doi.org/10.5281/zenodo.12528696). The two releases are treated as paired versions, not independent spacecraft or statistically independent replications.

**OPS-SAT v2 attribution (conditional, after actual use and rights signoff)**

> The study draws on version v2 of the OPSSAT-AD dataset (https://doi.org/10.5281/zenodo.15108715). Its versioned LICENSE identifies the MIT License for OPS-SAT Dataset, Copyright (c) 2024 KP Labs, applying to software, data and associated documentation. Original OPS-SAT telemetry files are not redistributed by this study.

If any licensed OPS-SAT code, data or substantial licensed material is copied into a publication supplement or repository, reproduce the **full** original versioned copyright/permission notice required by the license, not only the short acknowledgement. The authoritative 1.1 kB license is at https://zenodo.org/records/15108715/files/LICENSE?download=1 . Do **not** claim the full notice has been included until its inclusion is checked in that specific artifact.

## 3. Prospective data-availability wording

> The third-party datasets used in the study are available from their version-specific source archives on Zenodo [insert ONLY the DOIs actually used]. The authors do not redistribute the original satellite telemetry. Reproducibility scripts and non-raw, study-specific derived artifacts will be released, if permitted, following separate rights, operational-security, privacy and journal policy review.

**Before real source use:** do not insert this paragraph in a manuscript as a factual claim. Instead use planning-status documentation that clearly says **no source-semantic study results have been generated**.

## 4. Publication notice implementation checklist

- [ ] Rights record and original applicable dataset version DOI positively identified; license applicability to intended files approved by the sole author.
- [ ] ESA v2 blank Zenodo Rights value explicitly reconciled with exact linked first-party CC BY 3.0 IGO dataset metadata (and any rights-holder clarification deemed necessary).
- [ ] Conditional ESA v1 inclusion or exclusion documented without retroactively changing the primary protocol.
- [ ] OPS-SAT creator order checked against the **v2 citation export**.
- [ ] Dataset DOI cited in references for each source actually used; methods papers cited separately where used.
- [ ] ESA CC BY 3.0 IGO license link, creator credit, modification description and non-endorsement statement present when needed.
- [ ] OPS-SAT MIT copyright and permission notice copied in **full** if licensed material is copied or substantially redistributed; otherwise DOI/credit statements still included where study uses the source.
- [ ] All derivations and source-to-semantic transformations truthfully described; no scientific conclusions or data-use statements preempt the actual G4 results.
- [ ] No third-party raw telemetry, source snippets, command sequences, or potentially reconstructable sensitive outputs included without separate approval.
- [ ] Data availability, acknowledgements, figures, tables and supplements reviewed together for consistent license/provenance references.
- [ ] Final rights/source scope and notices signed off; G4-06 approved in a **separate** author decision; any PR merge independently authorized.

**Current checklist disposition: OPEN / NOT IMPLEMENTED IN MANUSCRIPT.** This is a review-ready template, not proof the study used ESA or OPS-SAT telemetry.
