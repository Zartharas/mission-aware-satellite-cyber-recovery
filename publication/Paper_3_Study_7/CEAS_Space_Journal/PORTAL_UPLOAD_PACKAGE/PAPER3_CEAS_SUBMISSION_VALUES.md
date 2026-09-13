# Paper 3 - CEAS Space Journal Submission Values

**Status:** `PORTAL_VALUES_PREPARED__FINAL_SUBMIT_NOT_AUTHORIZED`
**Journal:** CEAS Space Journal
**Article category:** Select `Original Paper` if that is the portal label; this corresponds to the journal guideline category `(Original) Research Article`. Do **not** select `Correspondence`, which is reserved for Short Communications.

## Manuscript identity

**Title**
Observability Limits of Learned Satellite Cyber-Recovery Decisions Under Compromised Evidence

**Abstract (197 words)**
Cyber-recovery decisions can remain unsafe even when the evidence presented to a decision policy is authenticated, current, and internally consistent, because a compromised evidence producer can supply a plausible but false state. This study evaluates whether a learned satellite cyber-recovery selector can overcome that observability boundary when it receives the same policy-visible inputs as a deterministic comparator, and what changes when a corroborating observable is added. A deterministic finite assurance experiment exhaustively evaluates 1,033 modeled observations: 512 observations over all 256 eight-feature visible states for a fixed comparator and a visible-only learned selector, 512 observations over all 512 nine-feature states for a corroboration-aware learner, and nine prespecified hidden-truth collision observations. The visible-only learner reproduces the complete visible decision boundary with zero errors, yet it proceeds unsafely when hidden authorization changes while its inputs remain unchanged. The corroboration-aware learner resolves the prespecified independent-disagreement collision, but it again proceeds unsafely when corroboration shares the false state; across its complete nine-feature lattice it has two objective-decision errors, one unsafe proceed and one false-conservative hold. The results show that model fit cannot substitute for decision-relevant observability and that corroboration shifts, rather than removes, the trust boundary of learned recovery logic.

**Keywords (6)**
1. Satellite cybersecurity
2. Cyber recovery
3. Machine learning assurance
4. Observability
5. Evidence integrity
6. Spacecraft autonomy

## Author

**Author:** Aman Kumar Singh
**Role:** Sole author; corresponding author
**Affiliation:** Independent Researcher
**City:** The Woodlands
**State:** Texas
**Country:** United States
**ORCID:** 0009-0008-9752-3743
**Corresponding-author email:** asingh65430@ucumberlands.edu

If the Springer account uses a different login email, keep the account login unchanged but use the corresponding-author email above where the manuscript-contact field is requested so the portal matches the manuscript title page.

## Funding

**Funding received?** No.

**Funding statement:**
No funding was received for conducting this study or preparing this manuscript.

## Competing interests

**Competing interests?** No.

**Statement:**
The author has no relevant financial or non-financial interests to disclose.

## Author contribution

Aman Kumar Singh is solely responsible for the conception and design of the study, implementation, experimental execution, analysis and verification, interpretation of results, manuscript preparation, and final approval of the submitted work.

## Ethics and consent

**Human participants / human data:** No.
**Animals / biological material:** No.
**Ethics approval:** Not applicable. This study did not involve human participants, human data, animals, or biological material.
**Consent to participate:** Not applicable.
**Consent for publication:** Not applicable.

## Data availability

The Study-7 protocol, canonical result records, policy summary, and separately implemented audit materials are publicly available in the mission-aware-satellite-cyber-recovery repository at https://github.com/Zartharas/mission-aware-satellite-cyber-recovery. The exact accepted Study-7 evidence is also preserved in a permanent Zenodo dataset deposit [9] (version DOI https://doi.org/10.5281/zenodo.22732060; concept DOI https://doi.org/10.5281/zenodo.22732059). The deposit preserves the accepted GitHub Actions artifact byte-for-byte and includes the exact observations, policy summary, trained-model parameters, execution report and provenance, implementation-independent repository audit output, and frozen protocol/results metadata. The accepted execution is identified by workflow run 33689625480 and commit f1530b0b2e81a5916adaf7ce808075156424dfb5; frozen SHA-256 identities are recorded in study7/results/RESULTS_FREEZE.json. No confidential, proprietary, or human-subject data are used.

## Code availability

The protocol, implementation, analysis code, and separately implemented audit code are available at https://github.com/Zartharas/mission-aware-satellite-cyber-recovery. The scientific implementation paths and accepted execution identity are recorded in the repository freeze files.

## Generative AI / LLM disclosure

**Was generative AI used beyond simple copy editing?** Yes.

**Methods disclosure already included in the manuscript:**
OpenAI ChatGPT, accessed through the ChatGPT web interface, was used during Study 7 development and manuscript preparation as an interactive research, coding, verification, and writing assistant. Before the results freeze, it assisted with protocol refinement, code and test drafting, repository and audit documentation, and verification-oriented review. After the results freeze, it assisted with manuscript structuring and drafting, literature-source discovery and verification, compliance checking, and language refinement. The author made and approved all research decisions, controlled the repository and experimental execution, reviewed and accepted code and test changes, verified the frozen outputs and numerical claims against the repository evidence, and reviewed and edited all AI-assisted text. ChatGPT was not an author and did not alter the accepted 1,033-observation population or frozen outputs after acceptance. All scientific claims and the submitted manuscript remain the sole responsibility of the author.

Author-confirmed provenance on 2026-09-12: ChatGPT web was the only generative-AI system used. Its role included pre-freeze study-development assistance and post-freeze manuscript assistance as described above. No Claude, Codex, or other generative-AI system was used for Study 7. Do not describe the repository audit as an independent human replication; it is a separately implemented, implementation-independent repository check.

## Originality and exclusivity

**Has this Paper-3 manuscript been published previously?** No.
**Is this Paper-3 manuscript currently under consideration elsewhere?** No.
**Is it part of a broader research program with related active manuscripts?** Yes. Disclose them in the cover letter; do not characterize them as prior submissions of this manuscript.

## Related-manuscript disclosure

Paper 3 is a separate Study-7 manuscript. It does not reuse the experimental populations, tables, figures, or numerical results of the following related manuscripts currently under consideration elsewhere. (1) AIAA Journal of Aerospace Information Systems manuscript 2026-09-I012066, “Satellite Cyber Response and Trusted Recovery Under Contact and Adversarial Evidence Constraints,” reports Studies 1 and 2. (2) IEEE Transactions on Aerospace and Electronic Systems manuscript “Residual Trust Boundaries in Satellite Cyber Recovery: Temporal Evidence, Producer Composition, and Artifact Assurance” reports Studies 3, 4, and 6. (3) Acta Astronautica manuscript AA-D-26-02872, “Contact-Aware Cryptographic Agility for Trusted Post-Compromise Recovery in Intermittently Connected Space Systems,” reports Study 8. (4) “Measuring Software Supply-Chain Assurance for Spacecraft Flight Software: A Controlled, Comparative Evaluation,” currently under review at the Journal of Space Safety Engineering, is based on the separate verifiable-spacecraft-lifecycle repository and evaluates S0-S5 software supply-chain assurance on spacecraft flight-software stacks. The present manuscript uses only Study 7 as new experimental evidence. Study-2 V5 is cited only as antecedent motivation through its public Zenodo archive. No manuscript listed above is a prior or concurrent submission of this Paper-3 manuscript.

## Suggested reviewers

Use the separately screened reviewer file. CEAS states that reviewer suggestions are welcome but optional, must be independent, and should preferably span different institutions and countries.

## Data archive control

The durable Study-7 archive is published on Zenodo as version 1.0.0. Version DOI: 10.5281/zenodo.22732060. Concept DOI: 10.5281/zenodo.22732059. The manuscript Data Availability statement and numbered reference list have been updated to cite the permanent dataset. The remaining controls are live-portal QA, proof review if generated, and explicit author authorization for the final Submit action.

## Dataset citation for portal/reference checks

Singh, A. (2026). *Mission-Aware Satellite Cyber Recovery - Study 7 Learned Selector Observability Evidence* (Version 1.0.0) [Dataset]. Zenodo. https://doi.org/10.5281/zenodo.22732060

**Version DOI:** `10.5281/zenodo.22732060`
**Concept DOI:** `10.5281/zenodo.22732059`
