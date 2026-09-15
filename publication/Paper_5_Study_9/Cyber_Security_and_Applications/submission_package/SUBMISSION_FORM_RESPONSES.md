# Submission Form Responses

- **Journal:** Cyber Security and Applications
- **Article type:** Research Article
- **Title:** Recovery-State Semantic Interoperability and Decision Identifiability Across Public Space-Cyber Datasets
- **Author:** Aman Kumar Singh
- **Credential display:** MS, PhD
- **Authorship:** Single author
- **Corresponding author:** Aman Kumar Singh
- **Email:** asingh65430@ucumberlands.edu
- **ORCID:** 0009-0008-9752-3743
- **Affiliation:** Independent Researcher
- **City / region / country:** The Woodlands, Texas, United States
- **Full postal affiliation address:** **PENDING AUTHOR-SUPPLIED SUBMISSION ADDRESS**
- **Keywords:** satellite cybersecurity; semantic interoperability; cyber resilience; intrusion response; recovery state; decision identifiability
- **Highlights:** `CSA_HIGHLIGHTS_SUBMISSION.txt`
- **Funding:** This research did not receive any specific grant from funding agencies in the public, commercial, or not-for-profit sectors.
- **Competing interests:** Intended response: **I have nothing to declare**; official Elsevier declarations-tool Word document still required.
- **Graphical abstract:** Not included; encouraged but optional.
- **Cover letter:** `COVER_LETTER_DRAFT.md` included as an optional submission aid.
- **Submission exclusivity:** **PENDING FINAL AUTHOR RECONFIRMATION AT SUBMISSION GATE**

## Abstract

Public satellite cybersecurity datasets are commonly designed for intrusion detection, attack characterization, or testbed evaluation, but recovery decisions require additional semantics such as trust, freshness, epoch validity, contradiction state, evidence completeness, security signaling, and authorization. This study evaluates whether those semantics transfer across three independently sourced public space-cyber datasets: CuCD-ID v3, AegisSat, and UNSW-IoTSAT. A preregistered field-level rubric classified each required recovery-state variable as directly observable, deterministically derivable by a predeclared rule, ambiguous, or absent. Missing state was preserved as unknown; attack labels were not treated as operational truth. A frozen downstream selector was then evaluated over every admissible completion of unresolved state, with lossless native-state collapse and exact multiplicity weighting. Across all three datasets, direct recovery-state coverage was 0/8 and direct-or-derivable coverage was 0/8. The common unresolved set contained all eight required variables. Each dataset collapsed to one decision-equivalent native-state group while preserving 25,000, 137,965, and 404,798 source rows, respectively. For all four frozen recovery policies, the uniquely identifiable action fraction was 0. Depending on policy, two or three recovery actions remained reachable, and six to eight additional sidecar variables were required to guarantee a unique action. These results do not imply that the datasets lack useful security telemetry. They show that, under the frozen semantic contract, intrusion-oriented public space-cyber data do not by themselves establish the recovery-state semantics required for deterministic downstream recovery decisions. The findings motivate explicit recovery-state interfaces alongside security telemetry when datasets are intended to support response or resilience research.

## Data availability wording

The protocol, mapping records, analysis code, tests, accepted derived outputs, independent-audit outputs, and cryptographic artifact identities are publicly available at https://github.com/Zartharas/mission-aware-satellite-cyber-recovery. Third-party raw dataset bytes are not redistributed; source provenance and cryptographic identities are recorded in the repository.

## Generative AI wording

OpenAI ChatGPT was used to support manuscript drafting, language refinement, structural review, and consistency checking against the frozen Study 9 research records. The author reviewed and edited the resulting text, verified scientific claims against the frozen repository evidence, and assumes full responsibility for the manuscript.
