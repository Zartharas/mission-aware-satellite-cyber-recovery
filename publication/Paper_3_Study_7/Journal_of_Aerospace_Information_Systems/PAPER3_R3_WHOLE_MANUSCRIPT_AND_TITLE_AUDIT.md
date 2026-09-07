# Paper 3 / Study 7 — R3 Whole-Manuscript and Title Audit

**Audit date:** 2026-09-07  
**Audited manuscript:** `PAPER3_TECHNICAL_NOTE_DRAFT_R3_FULL.md`  
**Status:** `PASS__SCIENTIFIC_BOUNDARY_INTACT__TITLE_LOCK_RECOMMENDED__SUBMISSION_NOT_AUTHORIZED`

## 1. Assembly provenance

R3 is an editorially compressed assembly of two previously audited components:

- `PAPER3_TECHNICAL_NOTE_DRAFT_R1A_SECTIONS_I_III.md` — verified PASS;
- `PAPER3_TECHNICAL_NOTE_DRAFT_R2A_SECTIONS_IV_VI.md` — verified PASS.

The compression removes repetition and detailed internal hash listings from the main prose. It does not add observations, recompute outcomes, change trained models, or alter the RQ.

## 2. Scientific evidence boundary

R3 uses Study 7 / `S7-LSO-001` as the sole new experimental evidence population.

Frozen population remains exactly:

- Block A: 512 observations;
- Block B: 512 observations;
- Block C: 9 observations;
- total: 1,033 observations.

No observation from Study 1, 2, 3, 4, 5, 6, or 8 is included in the R3 experimental population.

**Audit:** PASS.

## 3. Numerical result audit

R3 Table II matches frozen `study7/results/CANONICAL_POLICY_SUMMARY.csv` exactly:

| Block | Policy | N | Errors | Unsafe proceed | False conservative | Proceed |
|---|---|---:|---:|---:|---:|---:|
| A | D0 | 256 | 0 | 0 | 0 | 3 |
| A | L0 | 256 | 0 | 0 | 0 | 3 |
| B | L1 | 512 | 2 | 1 | 1 | 6 |
| C | D0 | 3 | 2 | 2 | 0 | 3 |
| C | L0 | 3 | 2 | 2 | 0 | 3 |
| C | L1 | 3 | 1 | 1 | 0 | 2 |

R3's descriptions of both Block-B error states and all three Block-C scenarios match the accepted hash-frozen `observations.csv` rows exactly.

**Audit:** PASS.

## 4. Model/protocol audit

R3 accurately preserves:

- eight policy-visible features;
- one corroboration feature;
- hidden authorization as adjudication-only;
- 10 L0 and 13 L1 training prototypes;
- deterministic ERM over bounded integer linear-threshold models;
- deterministic tie-breaking;
- L0 parameters `q=2, wa=1, ws=-1, t=12`;
- L1 parameters `q=2, wa=0, wc=1, ws=-1, t=12`;
- zero training errors for both learned models;
- no external ML library, RL, neural network, or adversarial perturbation optimizer.

**Audit:** PASS.

## 5. RQ answer and novelty audit

R3 answers the single locked RQ without expanding it into unsupported subclaims:

1. exact learning of the complete eight-feature visible boundary does not resolve a hidden-truth collision when the visible state is identical;
2. adding corroboration resolves the prespecified independent-disagreement case because the available information changes;
3. the protection disappears under correlated false corroboration;
4. the complete nine-feature lattice shows that making corroboration decision-relevant also creates one unsafe and one false-conservative disagreement state.

R3 explicitly does **not** claim:

- a new general theory of partial observability;
- generic novelty of redundancy/corroboration;
- ML superiority;
- certification sufficiency;
- operational spacecraft performance;
- detector performance;
- statistical inference from the deterministic lattice.

**Audit:** PASS.

## 6. External-validity audit

R3 states the principal limitations directly:

- simple deterministic linear-threshold learner;
- binary modeled inputs;
- no stochastic learning;
- no continuous/noisy evidence or distribution-shift experiment;
- no detector-performance experiment;
- no operational spacecraft/RF/flight/hardware/CPU/energy/latency claim;
- corroboration independence is a modeled assumption, not an empirical mission finding.

These limitations are consistent with the frozen protocol and earlier publication-boundary gate.

**Audit:** PASS.

## 7. Literature and reference audit

R3 uses six references, each for a bounded purpose:

1. SPARTA CM0044 — space cyber-recovery motivation only;
2. Study-2 Zenodo dataset DOI `10.5281/zenodo.22289114` — public antecedent/provenance only;
3. NASA NTRS `20240006865` — aerospace ML-assurance evidence context only;
4. OPS-SAT benchmark — satellite telemetry/anomaly-detection comparison literature;
5. Fejjari et al. transformer paper — satellite anomaly-detection comparison literature;
6. Kuhn et al. validation-gated continual-learning paper — satellite telemetry adaptation/performance comparison literature.

No source is used to claim that Study 7 is certified, externally validated, or operationally deployed.

**Audit:** PASS.

## 8. Related-publication / self-overlap audit

R3 does not copy manuscript prose, figures, tables, or experimental observations from Paper 1, Paper 2, or Roadmap Paper 4.

Study-2 `V5` appears only as prior specification lineage and is cited through the public dataset record. Paper 1 remains a separately submitted JAIS manuscript and must be disclosed as a related manuscript in the Paper-3 cover letter/submission process. That disclosure requirement remains mandatory even though Paper-1 prose is not copied into R3.

Paper 2's producer-composition/provenance results are not imported. Study 8's cryptographic-agility results are not imported. Study 5 remains excluded.

**Audit:** PASS.

## 9. Article-form audit

R3 remains structurally appropriate for a concise AIAA JAIS Technical Note:

- no abstract;
- one research question;
- six compact manuscript sections;
- two evidence tables;
- no unsupported performance plots;
- no literature-review padding;
- no combined Study-5 material;
- concise data/code availability statement.

A final exact word-count check should be performed when the AIAA template is instantiated because formatted tables, references, and publisher word-count conventions may differ from Markdown token/word counts. No scientific expansion is currently justified merely to increase length.

**Audit:** PASS.

## 10. Title review

Earlier working title:

**Evidence Observability Limits in Learned Satellite Cyber-Recovery Decisions**

R3 candidate:

**Observability Limits of Learned Satellite Cyber-Recovery Decisions Under Compromised Evidence**

The R3 candidate is preferred because:

- `Observability Limits` states the principal scientific boundary directly;
- `Learned` accurately identifies the ML component without promising broad AI theory;
- `Satellite Cyber-Recovery Decisions` identifies the application layer and distinguishes the paper from anomaly-detection work;
- `Under Compromised Evidence` states the adversarial condition without implying attack optimization or operational compromise data;
- it avoids the more awkward compound phrase `Evidence Observability Limits`;
- a live exact-title/discoverability search on 2026-09-07 found no obvious exact-title collision.

**Title recommendation:** LOCK the R3 title.

## 11. Whole-manuscript disposition

**Scientific claim integrity:** PASS.  
**Numerical integrity:** PASS.  
**Publication independence:** PASS.  
**Self-overlap controls:** PASS.  
**Reference/source control:** PASS.  
**Technical Note form:** PASS.  
**Title:** PASS for lock.  
**Publisher submission:** NOT AUTHORIZED.

Next controlled actions after title lock are: instantiate the journal-format manuscript source, perform exact reference formatting/author metadata QA, permanently archive the accepted Study-7 evidence bytes before Actions expiry, and conduct a final pre-submission scientific/ethics/related-manuscript audit before any publisher submission authorization.