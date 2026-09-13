# Study 9 Literature and Source Ledger

**Study:** `S9-RTSI-001`  
**Phase:** 9.0 prospective design  
**Verification date:** 2026-09-13  
**Status:** `DESIGN_LITERATURE_VERIFIED_NOVELTY_NOT_FROZEN`

## Purpose

This ledger records literature used to justify the prospective Study 9 question and to constrain its claims. It is not a manuscript bibliography and it does not establish novelty by itself.

The candidate contribution is narrower than satellite intrusion detection, dataset creation, cross-dataset machine-learning transfer, or mission-aware recovery individually. The prospective question is whether independently generated public space-cyber datasets expose a reproducible recovery-state interface, how unresolved semantics affect downstream action identifiability, and what minimal additional state would remove that ambiguity.

## Intended venue guidance

### Cyber Security and Applications: Guide for Authors

- Publisher: KeAi / Elsevier.
- Current guide: https://www.keaipublishing.com/en/journals/cyber-security-and-applications/guide-for-authors/
- Verified 2026-09-13.
- Relevant article types currently include Research Article and Short Communication.
- The journal currently requires declaration of generative AI use in manuscript preparation when applicable and requires human oversight and responsibility for accuracy.
- Design use: supports the current publication strategy and later submission-compliance planning only.
- Boundary: author instructions are not scientific evidence and must not influence endpoint selection after results are known.

## Candidate public space-cyber datasets

### CuCD-ID v3

- Yasamin Fayyaz et al., *CubeSat cybersecurity dataset for intrusion detection (CuCD-ID): Labelled NOS3/cFS telemetry (raw + augmented) with COSMOS reproduction scripts*.
- Data in Brief 65 (2026), 112598.
- Article DOI: `10.1016/j.dib.2026.112598`.
- Dataset DOI: `10.17632/7n2d42pm3n.3`.
- Dataset host comparison page verified 2026-09-13: https://data.mendeley.com/datasets/compare/7n2d42pm3n
- Primary article: https://www.sciencedirect.com/science/article/pii/S2352340926001514
- Design relevance: public intrusion-detection-oriented CubeSat command and telemetry data generated in NOS3/cFS with CCSDS-derived fields and engineered traffic/system features.
- Published population characteristics include a 25,000-row raw table with 31 columns and a 22,465-row augmented table with 23 columns across five scenarios.
- Dataset host reports CC BY 4.0 for version 3.
- Boundary: Study 9 must independently bind and hash selected v3 artifacts rather than treating the frozen Study 5 manifest as new Study 9 evidence.

### AegisSat

- Roee Idan et al., *AegisSat: A Satellite Cybersecurity Testbed*.
- Workshop on the Security of Space and Satellite Systems, SpaceSec 2025, co-located with NDSS Symposium.
- Primary paper: https://www.ndss-symposium.org/wp-content/uploads/spacesec25-final69.pdf
- NDSS record: https://www.ndss-symposium.org/ndss-paper/auto-draft-619/
- Dataset DOI reported by bibliographic metadata: `10.5281/zenodo.14960983`.
- Design relevance: physically instantiated Earth-based CubeSat plus environment emulator and controlled attack manager, with telemetry and labelled attack data from hundreds of experiments reported by the primary paper.
- Boundary: direct Zenodo artifact identity, version, license, files, and field schema still require verification before inclusion.

### UNSW-IoTSAT

- Osama Abdelhameed, Benjamin Turnbull, Nickolaos Koroniotis, *UNSW-IoTSAT: A hybrid testbed-derived dataset for enabling cybersecurity research in the smart satellite domain*.
- Cyber Security and Applications 4 (2026), article 100133.
- DOI: `10.1016/j.csa.2026.100133`.
- Primary article: https://www.sciencedirect.com/science/article/pii/S277291842600010X
- Public repository identified by the article: https://github.com/Osama-Abdelhameed/UNSW-IoTSAT
- Design relevance: hybrid cyber-physical satellite environment with CCSDS-oriented communication, IoT sensor data, RF-layer impairments, and more than 404,000 labelled normal/attack records according to the article.
- Venue relevance: the intended Study 9 journal has already published this satellite-cybersecurity dataset article, which supports topical fit but does not guarantee suitability or acceptance of Study 9.
- Boundary: a specific repository commit or release, license, file inventory, hashes, and field schema must be frozen before inclusion.

### LighTellite provenance caution

- SpaceSec 2026 paper: *LighTellite: Reinforcement Learning-Based ...*.
- Source: https://www.ndss-symposium.org/wp-content/uploads/spacesec26-13.pdf
- The paper states that its dataset was collected using the AegisSat testbed.
- Design consequence: LighTellite is not counted as an independent primary testbed population in the initial Study 9 screen unless shared provenance is explicitly modeled.

## Cross-dataset and distribution-shift literature

### WILDS

- Pang Wei Koh et al., *WILDS: A Benchmark of in-the-Wild Distribution Shifts*, ICML 2021, PMLR 139:5637-5664.
- Source: https://proceedings.mlr.press/v139/koh21a.html
- Design relevance: establishes that strong in-distribution performance does not imply robust out-of-distribution performance and that real-world distribution shifts require explicit evaluation.
- Boundary: Study 9 is not a WILDS-style predictive benchmark and does not claim machine-learning distributional robustness.

### Rule-based label harmonization for cross-dataset IoT IDS

- *A rule-based label harmonization framework for cross-dataset IoT intrusion detection*.
- Internet of Things 39 (2026), 102030.
- DOI: `10.1016/j.iot.2026.102030`.
- Design relevance: demonstrates the importance of explicit feature/label harmonization across heterogeneous security datasets and reports severe degradation in conventional cross-dataset ML evaluation before harmonization.
- Novelty consequence: dataset interoperability and semantic harmonization are active research topics. Study 9 cannot claim novelty merely for mapping heterogeneous datasets into a common interface.

### Cross-network NIDS transferability

- Francesco Cerasuolo, Giampaolo Bovenzi, Antonio Pescapè, *Cross-network transferability of AI-based network intrusion detection systems in heterogeneous Internet of Things environments*.
- Computer Networks 286 (2026), 112434.
- DOI: `10.1016/j.comnet.2026.112434`.
- Design relevance: evaluates eight heterogeneous IoT environments and reports that transferability varies with attack semantics and dataset characteristics.
- Boundary: this is model-transfer research. Study 9 instead isolates semantic sufficiency of a downstream recovery interface and must not relabel that question as classifier transferability.

## Intrusion response and cyber-resiliency foundations

### Intrusion response systems for cyber-physical systems

- *Intrusion response systems for cyber-physical systems: A comprehensive survey*.
- Computers & Security 124 (2023), 102984.
- DOI: `10.1016/j.cose.2022.102984`.
- Design relevance: distinguishes intrusion response decision-making from detection alone and reviews response architectures and decision approaches for cyber-physical systems.
- Design consequence: an IDS-oriented record cannot be assumed to contain all information needed for safe or justified response selection.

### NIST SP 800-160 Vol. 2 Rev. 1

- Ron Ross et al., *Developing Cyber-Resilient Systems: A Systems Security Engineering Approach*.
- NIST SP 800-160 Vol. 2 Rev. 1, December 2021.
- DOI: `10.6028/NIST.SP.800-160v2r1`.
- Source: https://csrc.nist.gov/pubs/sp/800/160/v2/r1/final
- Design relevance: frames cyber resiliency around the ability to anticipate, withstand, recover from, and adapt to adverse conditions while reducing mission/business risk.
- Boundary: NIST does not validate the Study 9 selector, dataset mappings, or any Study 9 outcome.

## Candidate gap statement

The verified literature shows substantial prior work on:

- satellite cybersecurity testbeds and public attack-labelled datasets;
- intrusion detection and learned-model evaluation;
- cross-dataset feature/label harmonization;
- cross-network model transfer and distribution shift;
- cyber-physical intrusion response and mission-aware cyber resiliency.

The prospective Study 9 gap is therefore limited to the following conjunction:

> A preregistered, field-level semantic interoperability study across independently generated public space-cyber datasets that preserves missing decision state, quantifies downstream recovery-action identifiability over all admissible completions, and derives the minimal additional recovery-state interface needed to eliminate decision ambiguity without using attack labels as operational truth.

This is a **candidate gap statement**, not a frozen novelty claim. It must remain qualified until source artifacts are verified, schemas are frozen, and a dedicated pre-analysis novelty/adversarial review is completed.

## Prohibited novelty statements

Study 9 must not claim to be:

- the first public satellite cybersecurity dataset study;
- the first cross-dataset cybersecurity study;
- the first dataset-harmonization framework;
- the first cross-network transferability study;
- the first satellite intrusion-response study;
- the first mission-aware cyber-resiliency study;
- the first demonstration that missing state can affect a security decision.

Any later novelty statement must be narrower and supported by the final pre-analysis literature review.
