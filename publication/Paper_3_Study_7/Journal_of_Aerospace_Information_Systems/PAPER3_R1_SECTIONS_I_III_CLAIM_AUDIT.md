# Paper 3 / Study 7 — R1 Sections I-III Scientific Claim Audit

**Audit date:** 2026-09-07  
**Audited draft:** `PAPER3_TECHNICAL_NOTE_DRAFT_R1_SECTIONS_I_III.md`  
**Status:** `PASS_WITH_EDITORIAL_CORRECTIONS__NO_SCIENTIFIC_RESULT_DEFECT`  
**Next controlled artifact:** corrected `R1A` Sections I-III draft  

This audit checks the first manuscript prose against the frozen Study-7 protocol/results, accepted workflow artifact, Study-2 antecedent records, and verified external sources. It does not authorize Sections IV-VI by itself.

## 1. Frozen Study-7 scientific facts

| Draft claim class | Authority | Audit |
|---|---|---|
| Study ID `S7-LSO-001` and deterministic finite ML-assurance design | `study7/STUDY7_PROTOCOL.json` | PASS |
| Eight visible inputs plus `independent_corroboration` | `study7/STUDY7_PROTOCOL.json` | PASS |
| Hidden authorization is adjudication-only and never policy-visible | protocol + `RESULTS_FREEZE.json` | PASS |
| Training prototypes: 10 for L0, 13 for L1 | protocol | PASS |
| Deterministic ERM / integer linear-threshold class / deterministic tie break | protocol + implementation | PASS |
| L0 model: `q=2, wa=1, ws=-1, threshold=12`, 0 training errors | `TRAINED_MODELS.json` + results freeze | PASS |
| L1 model: `q=2, wa=0, wc=1, ws=-1, threshold=12`, 0 training errors | `TRAINED_MODELS.json` + results freeze | PASS |
| Block A = 512, Block B = 512, Block C = 9, total = 1,033 | protocol + campaign freeze + results freeze | PASS |
| Objective definition described in Section III-A | `study7/src/learned_selector_model.py` | PASS |
| Accepted run `33689625480`, commit `f1530b0...` | results freeze / Actions metadata | PASS |
| Core output SHA-256 identities | results freeze + downloaded accepted artifact | PASS |
| Independent audit reconstructs objective/models/decisions with 0 mismatches | `study7/analysis/audit_independent.py` + accepted `INDEPENDENT_AUDIT.txt` | PASS |

The accepted artifact was downloaded read-only during this gate. Recomputed SHA-256 values for `observations.csv`, `policy_summary.csv`, `TRAINED_MODELS.json`, and `REPORT.json` exactly matched the frozen repository values. No scientific reexecution occurred.

## 2. Study-2 antecedent claims

The R1 description of the `V5` boundary is supported by the canonical Study-2 Phase-7 results freeze:

- a controlled producer can create policy-visible evidence that remains authenticated/current enough for the recovery gate;
- that evidence can be false relative to research-only adjudication truth;
- evidence-qualified recovery is therefore not equivalent to objectively correct recovery under the bounded compromise model.

**Audit:** PASS.

However, R1 reference [2] used a shorthand title that is not the exact Zenodo deposited title. The repository's deposit metadata gives the exact title:

**Mission-Aware Satellite Cyber Response and Trusted Recovery — Study 2 Phase-6 Source Evidence**

Creator: Aman Singh. Version DOI: `10.5281/zenodo.22289114`.

**Required correction:** use exact archive title/creator metadata in R1A.

## 3. External-source claims

### SPARTA CM0044

R1 uses SPARTA only to motivate the distinction between cyber-threat response and controlled recovery/reconstitution from a protected state.

**Audit:** PASS. The live SPARTA CM0044 page describes cyber-safe mode as a dedicated spacecraft state for cyber threats and a secure recovery baseline for reconstituting compromised functions.

### NASA learning-enabled component assurance memorandum

R1 states that assurance spans requirements/functional intent, model/data properties, implementation, integration, coverage, traceability, robustness/generalizability, and V&V rather than only model performance.

**Audit:** PASS. NASA NTRS document `20240006865` explicitly discusses these evidence classes and also states that it does not establish a complete or universally sufficient certification evidence set.

### OPS-SAT benchmark

R1 characterizes the paper as real satellite telemetry data/labels used to benchmark anomaly-detection methods.

**Audit:** PASS. The 2025 *Scientific Data* descriptor reports 2,123 annotated telemetry fragments from nine channels and benchmarks 30 supervised/unsupervised anomaly-detection algorithms.

### Transformer satellite telemetry paper

R1 characterizes it as a comparison of transformer architectures for satellite telemetry anomaly detection.

**Audit:** PASS. *Acta Astronautica* DOI `10.1016/j.actaastro.2025.09.035` explicitly presents and compares transformer methods on satellite telemetry anomaly detection.

### Validation-gated continual learning paper

R1 characterizes it as validation-gated continual learning for satellite telemetry under data drift/scarcity.

**Audit:** PASS. *Acta Astronautica* DOI `10.1016/j.actaastro.2026.07.065` supports this description.

R1 intentionally left author metadata incomplete. Live publisher/search metadata now identifies:

- Nils Kuhn;
- Bruno Sánchez Gómez;
- Natalia Moreno Blasco;
- Polona Caserman;
- Federico Antonello;
- *Acta Astronautica*, vol. 249, pp. 971-985 (2026).

**Required correction:** complete reference [6] in R1A.

## 4. Wording precision corrections

### Correction A — avoid unsupported extra qualifier

R1 Introduction says a recovery selector can receive information that is "timely, authenticated, and internally consistent" while false.

The Study-2 freeze directly supports authenticated/current enough for policy qualification and false relative to adjudication truth. "Internally consistent" is unnecessary and broader than the exact frozen wording.

**R1A correction:** use "authenticated and current enough for policy qualification" rather than adding internal-consistency language.

### Correction B — avoid general model-capacity assertion

R1 states that a more flexible model may reproduce a decision rule more accurately than a hand-written approximation.

That generic observation is not needed for the Study-7 claim and invites a model-performance interpretation that the protocol intentionally avoids.

**R1A correction:** state only the experiment-supported information-boundary proposition: exact fit to a visible decision boundary does not provide hidden information absent from the input.

### Correction C — independent audit versus external reproduction

R1 contribution language says the evidence is "independently reproduced."

The repository has an independently written auditor and exact recomputation with zero mismatches, but this is same-repository independent verification rather than external replication.

**R1A correction:** use "independently audited/recomputed with zero mismatches" and reserve "external replication" for genuinely external work.

### Correction D — novelty language

R1 says partial observability is long-established and mentions broad aerospace mechanisms. The core statement is reasonable, but a concise Technical Note does not need an uncited mini-survey to disclaim novelty.

**R1A correction:** simplify to "This note does not claim partial observability, corroboration, or redundancy as new general concepts" and keep the positive novelty statement application-specific.

## 5. Self-overlap / publication-independence audit

- No Paper-1 observation, table, figure, statistical estimate, or manuscript wording is copied into R1.
- Study-2 appears only as antecedent specification/motivation; its observations are explicitly excluded from the 1,033-observation Study-7 population.
- No Paper-2 Studies 3/4/6 evidence is imported.
- No Study-8 / Acta evidence is imported.
- Study 5 is absent from manuscript evidence.

**Audit:** PASS.

Paper 1 remains under review at JAIS and must be disclosed as related work at submission. This is a later submission-control obligation, not a reason to insert unpublished Paper-1 prose into the Technical Note.

## 6. Statistical / external-validity audit

R1 correctly states that:

- the 1,033 positions are a complete finite modeled population under the frozen design;
- counts are not operational spacecraft error probabilities;
- no confidence intervals, p-values, sampling inference, detector metrics, flight validation, certification, or global model ranking are claimed.

**Audit:** PASS.

## 7. Table-I audit

Table I is a direct condensation of the frozen protocol/model identities and introduces no new analysis.

**Audit:** PASS.

## 8. Audit disposition

**Scientific result integrity:** PASS.  
**Claim boundary:** PASS after four wording/metadata corrections above.  
**Self-overlap control:** PASS.  
**Reference integrity:** PASS after exact Study-2 title and reference-[6] completion.  
**Authorization to draft Results:** NOT YET; create and verify R1A first.

No frozen study or submitted-paper artifact was modified by this audit.