#!/usr/bin/env python3
"""Create a local, untracked short-form TAES Paper-2 candidate and supplement.

This script is intentionally isolated from the frozen R9 package on main. It
verifies the R9 manuscript/PDF hashes, reads tracked manuscript components, and
creates only short-track development files in the publication directory.

It does not rerun or modify Studies 3, 4, or 6.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASELINE_MD = ROOT / "TAES_MANUSCRIPT_FULL_DRAFT.md"
BASELINE_PDF = ROOT / "TAES_MANUSCRIPT.pdf"
ABSTRACT_DOC = ROOT / "TAES_ABSTRACT_KEYWORDS.md"
CORE_SOURCE = ROOT / "TAES_MANUSCRIPT_SOURCE.md"
S3_SOURCE = ROOT / "TAES_SECTION_IV_STUDY3.md"
S4_SOURCE = ROOT / "TAES_SECTION_V_STUDY4.md"
S6_SOURCE = ROOT / "TAES_SECTION_VI_STUDY6.md"
VALIDITY_SOURCE = ROOT / "TAES_SECTION_VIII_VALIDITY.md"
FIGURE_PNG = ROOT / "TAES_FIGURE1_RESIDUAL_BOUNDARIES.png"

OUT_MAIN = ROOT / "TAES_10P_MANUSCRIPT_DRAFT.md"
OUT_SUPP = ROOT / "TAES_10P_SUPPLEMENTARY_MATERIAL.md"
OUT_README = ROOT / "TAES_10P_SUPPLEMENTARY_README.txt"
OUT_AUDIT = ROOT / "TAES_10P_CANDIDATE_AUDIT.txt"

EXPECTED_BASELINE_MD = "802e6658e9e1325ec4f4a785c5da1b3856fbfadb950dadb6f6a57aec0acacd48"
EXPECTED_BASELINE_PDF = "a7624fa416ebe4ba4d0b9e46da25b5dcb4d85e23e63291f4bdf497d5ba6cb319"
EXPECTED_FIGURE_PNG = "7d22964bdae052b35b4680e1b09f3209f1c99bb1d157a0f995dcd2a6445e6698"

TITLE = "Residual Trust Boundaries in Satellite Cyber Recovery: Temporal Evidence, Producer Composition, and Artifact Assurance"

SECTION_I = r'''## I. Introduction

Cyber recovery in satellite systems can require trust decisions under communication gaps, constrained postlaunch access, and mission-continuity pressure [1]. Before a policy permits a recovery path, it must decide whether runtime evidence, the producers supplying that evidence, and the recovery artifact are sufficiently trustworthy for the modeled decision.

The mechanisms themselves are established. Satellite research addresses internal trust boundaries and testable cyber-resilience requirements [2], [3], while SPARTA describes integrity-protected trusted recovery baselines [4]. RATS separates evidence from appraisal and treats freshness explicitly [5], with current work considering multi-Verifier composition [6]. Quorum research formalizes trust and failure assumptions [7], [8], and satellite trusted-execution work already uses endorsement quorums [9]. in-toto, TUF, and SLSA provide provenance, signed metadata, target binding, controlled build processes, and source-assurance concepts [10], [11], [12]; SLSA also states limits when the producer itself is malicious [13]. This paper does not claim novelty for those primitives.

The narrower question is what residual trust boundary remains when visible checks pass while a research-only authorization or correctness state differs. Three separately frozen deterministic studies address that question without pooling. Study 3 evaluates 1,380 temporal trajectories under continuous and synthetic intermittent contact and separates invalid post-signature alteration, truthful pre-onset cache lag, and false but validly signed evidence from a compromised trusted producer. Study 4 evaluates 4,608 exact rule-by-subset observations across 18 vote/provenance rules and distinguishes first from systematic unsafe qualification while separately measuring false-conservative rejection under benign producer loss. Study 6 evaluates 420 exact artifact-assurance observations and maps which prespecified incorrect states survive progressively composed gates together with benign assurance-signal loss.

The contribution is a bounded residual-boundary characterization across three qualification layers: temporal evidence, producer composition, and recovery-artifact assurance. The cross-study synthesis is qualitative only. Each study retains its own unit, interventions, endpoints, and population; no common effect, pooled success rate, end-to-end recovery probability, or global policy ranking is defined.

Only Study 3 models contact, and its logical time is not operational spacecraft time. Study 4 provenance domains are synthetic, and Study 6 is a finite Boolean assurance model rather than a real supply-chain experiment. Qualification is not recovery completion, and the studies do not measure flight safety, mission availability, RF performance, computing cost, or operational attack prevalence. Expanded finite-model and external-validity detail is provided in the peer-reviewed supplementary material.'''

SECTIONS_II_III = r'''## II. Related Work and Scientific Positioning

Space cybersecurity differs from continuously connected terrestrial systems because communication gaps, postlaunch inaccessibility, subsystem coupling, and mission-continuity constraints can limit how recovery evidence is refreshed or validated [1]. Flight-software studies further show that legitimate interfaces can preserve authority across internal trust boundaries [2], while secure-by-design work argues for testable resilience requirements rather than global security assertions [3]. SPARTA already treats integrity-protected and validated recovery baselines as part of cyber-safe recovery [4].

RATS provides the relevant evidence vocabulary: an Attester produces Evidence, a Verifier appraises it, and a Relying Party uses the resulting decision [5]. Freshness limits evidence age but does not guarantee instantaneous agreement with a state that changes immediately after evidence generation. Multi-Verifier RATS work addresses composition of appraisal across Verifiers [6], whereas Study 4 here composes claims from modeled evidence producers.

Byzantine and asymmetric quorum systems already formalize how trust assumptions and failure sets shape consistency and availability [7], [8], and Space Fabric applies endorsement quorums in a satellite-enhanced trusted-execution architecture [9]. Study 4 is not consensus or Byzantine agreement; it asks a narrower finite recovery-qualification question. Artifact provenance and update security are also established. in-toto provides verifiable supply-chain step metadata [10], TUF uses signed metadata, hashes, trusted roles, expiration, and thresholds [11], and SLSA defines source/build assurance requirements [12]. SLSA's threat model also recognizes that an intentionally malicious producer cannot be neutralized by process controls alone without an independent basis for trusting that producer [13].

The contribution is therefore not any individual signature, freshness, quorum, provenance, reproducible-build, review, or approval mechanism. It is the exact characterization of three separately frozen residual qualification boundaries: temporal evidence validity and producer semantics in Study 3, vote/provenance composition in Study 4, and artifact-assurance composition in Study 6. In the reviewed literature, we did not identify a directly matching spacecraft cyber-recovery study that reports these three perspectives as separate finite experiments and then synthesizes them without pooling. This is a literature-positioning statement, not a priority claim.

## III. Common Trust-Qualification Framework and Study Separation

For study `j`, let `E_j` denote policy-visible evidence and `Q_j(E_j) in {0,1}` the frozen qualification decision. Let `T_j in {0,1}` denote the research-only adjudication state, where `1` means that hidden authorization or objective artifact correctness supports qualification. `T_j` is never supplied to `Q_j`. The manuscript-level unsafe condition is

`U_j = 1[Q_j(E_j) = 1 and T_j = 0]`.

Where benign evidence loss is separately evaluated,

`C_j = 1[Q_j(E_j) = 0 and T_j = 1]`.

These expressions organize interpretation; they are not new experimental endpoints. Study 3 realizes the framework with signature/freshness/contact-dependent runtime evidence and hidden authorization truth; Study 4 with signed producer claims, vote/provenance requirements, and hidden authorization truth; and Study 6 with artifact-assurance signals and objective baseline correctness. Their frozen populations remain 1,380 trajectories, 4,608 rule-by-subset observations, and 420 artifact-state/assurance-unavailability observations, respectively.

Residual trust boundary denotes a modeled state in which visible evidence still satisfies qualification while research-only adjudication is false, together with any study-specific false-conservative boundary created by stronger evidence requirements. It is descriptive of the registered finite models, not an impossibility theorem. The three populations are not pooled, only Study 3 models intermittent contact, and qualification does not establish completed or safe spacecraft recovery. Same-repository independent audits reported zero mismatches and support reproducibility of the finite experiments, not external replication.'''

SECTION_IV = r'''## IV. Temporal Evidence Qualification Under Intermittent Contact

Study 3 (`S3-K4E-001`) uses a deterministic 240-logical-second horizon in five-second epochs with five logical seconds of evidence validity. Forty-six onset phases run from 10 through 235 logical seconds. `K0` provides continuous modeled contact; `K4` provides synthetic windows `[25,35]`, `[75,90]`, `[145,165]`, and `[220,240]`. K4 is not an orbital pass schedule.

`V0` is truthful evidence. `V4` changes a signed post-onset value from false to true after signing, invalidating the signature. `V5` represents a compromised trusted producer that validly signs authorization true while hidden authorization is false. `V4` and `V5` are evaluated as one-shot and persistent treatments under `B0` fail-closed, `B2` risk-threshold, and `S1` evidence-aware semantics. Thirty cells crossed with 46 onset phases yield 1,380 trajectories and 67,620 repeated epoch states; the trajectory is the study unit.

The principal outcome here is unsafe qualification: policy-visible evidence qualifies while hidden authorization is false. False-qualified epochs are attributed either to `PRE_ONSET_CACHE`, a truthful record received before onset that remains policy-fresh afterward, or `V5_AFFECTED_RECORD`, a false but validly signed record issued after compromise.

**Table I. Selected Study-3 residual-boundary results**

| Evidence / contact / policy | Unsafe-qualified trajectories | Mean exposure, logical s |
|---|---:|---:|
| Persistent `V5`, `K0`, `B0` or `S1` | 46/46 | 122.500 |
| Persistent `V5`, `K0`, `B2` | 0/46 | 0 |
| Persistent `V5`, `K4`, `B0` | 46/46 | 55.326 |
| Persistent `V5`, `K4`, `S1` | 46/46 | 49.022 |
| Persistent `V5`, `K4`, `B2` | 0/46 | 0 |
| Truthful `V0`, `K4`, `B0` | 3/46 | 0.326 |
| Truthful `V0`, `K4`, `S1` or `B2` | 0/46 | 0 |

Persistent `V5/K0` remains unsafe-qualified for every onset phase under `B0` and `S1`; `B2` is zero in that frozen cell. Under `V5/K4`, `B0` and `S1` again qualify in 46/46 trajectories, but modeled mean exposure falls to 55.326 and 49.022 logical seconds. The corresponding V5 increment is 55.0 logical seconds for `B0` and 49.022 for `S1`; the B0-S1 difference is approximately 6.304 logical seconds. These values are model time, not spacecraft response, communication, operator, or orbital-contact time. The `B2` zeros are structural properties of the registered grid, not universal immunity or a global ranking.

Affected `V4` records never qualify because the post-signature change invalidates their signatures. Any B0/K4 false qualification in V4 cells originates from a previously received truthful record and is labeled `PRE_ONSET_CACHE`. Under truthful `V0/K4/B0`, that cache boundary occurs in 3/46 trajectories with mean exposure 0.326 logical seconds; `S1` and `B2` have none. Thus signature validation rejects the modeled altered record but cannot expose semantic falsity when the trusted producer itself validly signs the false `V5` claim.

One-shot `V5/K0` produces five logical seconds of mean V5 exposure for `B0` and `S1` across all 46 onset phases; under K4, `S1` retains five logical seconds and `B0` additionally contains the separately identified cache boundary. Persistence therefore changes renewal and duration, not the cryptographic status of the false claim. Expanded endpoints and timing details appear in Supplementary Appendix A.'''

SECTION_V = r'''## V. Multi-Producer Qualification and Provenance-Domain Constraints

Study 4 (`S4-MPQ-001`) evaluates seven registered producers assigned to synthetic domains `D1={P1,P2,P3}`, `D2={P4,P5}`, and `D3={P6,P7}`. A rule `Qq_Dd` requires `q` qualifying claims and `d` represented domains, with `q=1..7` and `d=1..min(3,q)`, yielding 18 rules. The domains are model labels, not demonstrated organizational, hardware, software, or supply-chain independence.

Two exhaustive blocks are evaluated separately. In the safety block, hidden authorization is false and compromised producers emit validly signed true claims. In the benign-loss block, hidden authorization is true and affected producers are unavailable. Every producer subset is evaluated for every rule in both blocks: `18 x 2 x 128 = 4,608` exact observations. The blocks do not model simultaneous compromise and benign loss.

For each rule, first failure is the smallest affected-producer count for which at least one subset fails; systematic failure is the smallest count for which every subset fails. These are finite combinatorial thresholds, not compromise, outage, or mission-availability probabilities.

**Table II. Selected Study-4 first/systematic thresholds**

| Rule | Unsafe qualification: compromised producers | False-conservative rejection: unavailable producers |
|---|---:|---:|
| `Q1_D1` | 1/1 | 7/7 |
| `Q2_D2` | 2/4 | 4/6 |
| `Q3_D1` | 3/3 | 5/5 |
| `Q3_D3` | 3/6 | 2/5 |
| `Q4_D1` | 4/4 | 4/4 |
| `Q4_D3` | 4/6 | 2/4 |
| `Q5_D3` | 5/6 | 2/3 |
| all `Q6` variants | 6/6 | 2/2 |
| all `Q7` variants | 7/7 | 1/1 |

Absolute vote count sets the basic compromise boundary, while provenance changes which same-size subsets satisfy a rule. `Q3_D3` leaves first unsafe failure at three, as under `Q3_D1`, but moves systematic failure from three to six because a qualifying three-producer subset must span all three domains. Similar systematic-delay effects occur for `Q4_D3` (4/6) and `Q5_D3` (5/6).

That structure carries a benign cost. `Q3_D3` can reject after only two unavailable producers rather than five under `Q3_D1`; `Q4_D3` moves first benign failure from four to two; and `Q5_D3` first fails at two rather than three under `Q5_D1`. Provenance is therefore not monotonically beneficial.

Null and equal-threshold results are retained. `Q4_D1` and `Q4_D2` are identical at 4/4 in both blocks; `Q5_D1` and `Q5_D2` are identical at safety 5/5 and benign loss 3/3; all `Q6` variants are 6/6 and 2/2; and all `Q7` variants are 7/7 and 1/1. Without operational probabilities, mission costs, or utility weights, the grid does not identify a globally best rule.

Study 4 is a qualification model, not Byzantine consensus or distributed agreement [7], [8], [9]. Its residual boundary is subset composition under a fixed registered denominator and synthetic domain allocation. The complete 18-rule threshold map appears in Supplementary Appendix B; Study 4 contains no contact model.'''

SECTION_VI = r'''## VI. Recovery-Artifact Assurance and Residual Incorrect States

Study 6 (`S6-SCTR-001`) evaluates recovery-artifact qualification in an exact six-state, six-gate Boolean model. `CLEAN_APPROVED` is objectively correct; five prespecified states are objectively incorrect: `POST_RELEASE_TAMPER`, `TRUSTED_SIGNER_COMPROMISE`, `TRUSTED_BUILDER_COMPROMISE`, `SOURCE_REVIEW_BYPASS`, and `APPROVED_BAD_SOURCE`. The research-only oracle `objective_baseline_correct` is never supplied to a gate.

The six policy-visible signals are signature validity, independent target-digest match, provenance validity, independent reproduced-build match, source-review attestation, and release approval. Terms such as "independent" are names in the frozen abstraction and do not demonstrate real organizational or infrastructure independence. Gates `G0` through `G5` compose different subsets of these signals, from signature-only to all six.

The adversarial block crosses six states with six gates for 36 observations. A separate benign block crosses the objectively correct baseline with all 64 assurance-signal-unavailability subsets across the six gates for 384 observations. The frozen population is 420 exact observations; compromised-artifact and benign-signal-loss conditions are not combined.

**Table III. Study-6 residual incorrect states and benign assurance loss**

| Gate | Incorrect states still qualified | Unsafe count | Benign-loss subsets |
|---|---|---:|---:|
| `G0` signature only | `APPROVED_BAD_SOURCE`; `SOURCE_REVIEW_BYPASS`; `TRUSTED_BUILDER_COMPROMISE`; `TRUSTED_SIGNER_COMPROMISE` | 4/5 | 32/64 |
| `G1` signature + target digest | `APPROVED_BAD_SOURCE`; `SOURCE_REVIEW_BYPASS`; `TRUSTED_BUILDER_COMPROMISE` | 3/5 | 48/64 |
| `G2` signature + provenance | `APPROVED_BAD_SOURCE`; `SOURCE_REVIEW_BYPASS`; `TRUSTED_BUILDER_COMPROMISE` | 3/5 | 48/64 |
| `G3` provenance + reproduced build | `APPROVED_BAD_SOURCE`; `SOURCE_REVIEW_BYPASS` | 2/5 | 56/64 |
| `G4` provenance + source review | `APPROVED_BAD_SOURCE`; `TRUSTED_BUILDER_COMPROMISE` | 2/5 | 56/64 |
| `G5` six-signal composite | `APPROVED_BAD_SOURCE` | 1/5 | 63/64 |

Signature-only qualification leaves four of five prespecified incorrect states. `G1` and `G2` both leave three and, in this frozen state set, the same residual states; that aggregate equality does not establish operational equivalence between digest and provenance verification. `G3` and `G4` each leave two incorrect states but not the same two, showing why residual identity matters as much as count.

`G5` leaves only `APPROVED_BAD_SOURCE`, defined so that every gate-visible signal is true while objective correctness is false. This is a structural observability boundary of the registered model, not an impossibility theorem or a claim that semantic correctness can never be established. SLSA similarly recognizes that an intentionally malicious producer remains outside what process controls alone can guarantee [13].

Stronger gates also increase benign rejection from 32/64 unavailable-signal subsets under `G0` to 63/64 under `G5`. Those ratios are finite state/subset counts, not attack rates, false-negative rates, service-outage probabilities, or mission-availability estimates. Study 6 does not implement a real supply-chain compromise, production signing system, operational spacecraft recovery pipeline, or standards-compliance test. Expanded definitions appear in Supplementary Appendix C.'''

SECTION_VII = r'''## VII. Cross-Study Residual Trust Boundaries

Studies 3, 4, and 6 were designed, executed, and frozen separately. Their populations, mechanisms, and endpoints are not pooled, and no experimental data flow connects them. The synthesis compares only the residual qualification boundary left by policy-visible evidence.

Across the studies, integrity or additional evidence does not exhaust semantic trust. Study 3 rejects the affected post-signature-manipulated `V4` record but can still qualify false `V5` evidence that is freshly and validly signed by a compromised trusted producer. Study 6 similarly closes several integrity and process pathways while `APPROVED_BAD_SOURCE` remains qualified because every frozen gate-visible signal is true. A gate can discriminate only using properties represented in its observable variables and trust anchors.

Stronger composition moves rather than universally eliminates the boundary. In Study 4, provenance can delay systematic unsafe qualification while causing earlier benign rejection, and some provenance requirements have no threshold effect. In Study 6, stronger gates reduce residual incorrect states but increase benign assurance-loss sensitivity. Study 3 has different endpoints; its K4 restriction reduces selected modeled exposure while persistent V5 qualification remains for `B0` and `S1`.

Residual identity therefore matters. Study 3 distinguishes truthful cache lag from compromised-producer evidence, Study 4 distinguishes first from systematic failure because same-size subsets can differ, and Study 6 preserves which incorrect states remain rather than collapsing them into one count. This supports a layered observability interpretation, not a globally best policy, an integrated three-layer experiment, or a universal impossibility theorem.

For aerospace information systems, the practical questions are limited: separate integrity from semantic authority, justify what any claimed provenance domain means operationally, evaluate stronger evidence requirements together with benign evidence loss, and identify the highest-level trust assumption that remains outside each qualification gate.'''

SECTION_VIII = r'''## VIII. Validity, Aerospace Interpretation Boundaries, and Future Evaluation

The strongest claims are internal to three exact finite models. Study 3 exhausts its 46-phase registered grid, Study 4 exhausts all producer subsets for every rule in two separate blocks, and Study 6 exhausts its prespecified artifact states and assurance-unavailability subsets. Exactness within those grids does not imply universality. The units remain incommensurate and are not pooled: trajectories for Study 3, rule-by-subset observations for Study 4, and artifact-state/assurance-unavailability observations for Study 6. Sampling-based p-values, confidence intervals, pooled effect estimates, or a combined Paper-2 `N` are not used to generalize beyond those finite populations.

Study 3 uses one continuous-contact treatment and one synthetic K4 schedule over logical time. Its reported 122.5, 55.326, 49.022, 5, and 0.326 logical-second exposures are model quantities, not processor time, RF latency, operator delay, orbital time, or ground-contact duration. `V5` assumes a trusted producer can validly sign a false claim; `V4` models post-signature alteration. Neither treatment estimates compromise likelihood or cryptographic strength.

Study 4 is conditional on seven producers, a 3/2/2 synthetic domain allocation, a fixed registered denominator, and 18 rule definitions. Its 128 subsets per block are model states, not probabilities. The domains do not establish real organizational, hardware, network, administrative, or supply-chain independence, and the separate safety and benign-loss blocks do not model simultaneous compromise and unavailability. Study 4 is not Byzantine consensus and contains no contact model.

Study 6 is a prespecified Boolean assurance abstraction. Counts such as 4/5 and 1/5 are residual state counts, not detection rates or attack probabilities, and 63/64 is not an outage estimate. Signal names such as independent digest or reproduced build do not prove real independence. `APPROVED_BAD_SOURCE` identifies the registered gate's observability boundary but is not a theorem that semantic correctness cannot be established. The experiment does not implement a production build pipeline, real signing keys, malware, or standards compliance.

No study operates an on-orbit spacecraft, ground station, RF link, flight processor, production key infrastructure, or operational recovery command path. Qualification is not recovery completion and the results do not establish flightworthiness, certification, mission safety, mission availability, recovery success probability, or operational attack prevalence. Only Study 3 models contact; Study 4 producer unavailability and Study 6 assurance-signal unavailability must not be relabeled as contact loss.

Independent same-repository audits reported zero mismatches and support reproducibility of the frozen finite experiments, not external replication. The cross-study framework is a post hoc systems interpretation rather than a prospectively tested integrated architecture. Detailed construct boundaries, full finite maps, and expanded reproducibility notes are retained in Supplementary Appendices A-D.

Future work can prospectively evaluate orbital-contact schedules, hardware/software-in-the-loop timing, empirically justified producer failure domains, joint compromise/unavailability conditions, production build pipelines, independently operated assurance services, and a genuinely integrated recovery architecture. Such extensions would define new interventions and endpoints rather than reopen the frozen Studies 3, 4, or 6.'''

SECTION_IX = r'''## IX. Conclusion

Three separately frozen finite studies characterize residual trust boundaries in satellite cyber-recovery qualification. Study 3 distinguishes truthful cache lag, rejected post-signature alteration, and false but validly signed evidence from a compromised trusted producer. Study 4 shows that vote count sets the basic compromise boundary while synthetic provenance changes subset-dependent first/systematic failure and benign-loss tolerance, with both beneficial and null effects. Study 6 shows that composed artifact-assurance signals close specific incorrect states but leave `APPROVED_BAD_SOURCE` under the six-signal gate while increasing benign assurance-loss sensitivity.

Across the studies, stronger trust composition narrows modeled failure pathways without making policy-visible evidence equivalent to hidden or objective truth. The result is a layered observability interpretation, not a pooled experiment or global policy ranking. Only Study 3 models contact; logical time, synthetic provenance domains, and Boolean artifact states remain model abstractions rather than operational spacecraft measurements.'''

AI_ACK = '''OpenAI ChatGPT (GPT-5.6 Sol) was used at a substantive drafting and editorial level to assist with text in the Abstract and Sections I-IX, literature organization and bibliography formatting, preparation of the peer-reviewed supplementary material, and generation of publication-preparation scripts. It was not used to generate or modify the frozen experimental results. The author independently reviewed and verified the resulting text, citations, claims, calculations, and repository-bound evidence and assumes responsibility for the final manuscript and supplementary material.'''


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read(path: Path) -> str:
    if not path.is_file():
        raise SystemExit(f"ERROR: missing required file: {path}")
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def extract_between(text: str, start_marker: str, end_marker: str) -> str:
    start = text.find(start_marker)
    if start < 0:
        raise SystemExit(f"ERROR: start marker missing: {start_marker}")
    start += len(start_marker)
    end = text.find(end_marker, start)
    if end < 0:
        raise SystemExit(f"ERROR: end marker missing: {end_marker}")
    return text[start:end].strip()


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text))


def first_use(text: str) -> list[int]:
    body = text.split("\n## References", 1)[0]
    seen: list[int] = []
    for m in re.finditer(r"\[(\d+)\]", body):
        n = int(m.group(1))
        if n not in seen:
            seen.append(n)
    return seen


def supplement_section(path: Path, appendix: str, title: str, old_table: str | None, new_table: str | None) -> str:
    text = read(path).strip()
    lines = text.splitlines()
    if not lines or not lines[0].startswith("# "):
        raise SystemExit(f"ERROR: unexpected section format in {path.name}")
    lines[0] = f"## Appendix {appendix}. {title}"
    out: list[str] = []
    for line in lines:
        if line.startswith("## ") and not line.startswith("## Appendix"):
            line = "#" + line
        if old_table and new_table and line.startswith(f"### Table {old_table}."):
            rest = line[len(f"### Table {old_table}. "):]
            line = f"**Table {new_table}. {rest}**"
        out.append(line)
    return "\n".join(out).strip()


def main() -> None:
    if sha256(BASELINE_MD) != EXPECTED_BASELINE_MD:
        raise SystemExit("ERROR: frozen R9 canonical manuscript hash mismatch")
    if sha256(BASELINE_PDF) != EXPECTED_BASELINE_PDF:
        raise SystemExit("ERROR: frozen R9 publisher-facing PDF hash mismatch")
    if sha256(FIGURE_PNG) != EXPECTED_FIGURE_PNG:
        raise SystemExit("ERROR: Figure 1 PNG hash mismatch")

    abstract_doc = read(ABSTRACT_DOC)
    abstract_block = extract_between(abstract_doc, "## Abstract\n", "\n## Index Terms")
    abstract = "\n".join(
        line for line in abstract_block.splitlines()
        if not re.match(r"^\*\*.*word count.*\*\*", line.strip(), flags=re.IGNORECASE)
    ).strip()
    index_terms = extract_between(abstract_doc, "## Index Terms\n", "\n## Abstract claim controls").strip()

    core = read(CORE_SOURCE)
    refs_pos = core.find("## References Used in Sections II and III")
    if refs_pos < 0:
        raise SystemExit("ERROR: reference block missing from TAES_MANUSCRIPT_SOURCE.md")
    refs = core[refs_pos:].replace("## References Used in Sections II and III", "## References", 1).strip()

    main = "\n\n".join([
        f"# {TITLE}",
        "## Abstract\n\n" + abstract,
        "**Index Terms:** " + index_terms,
        SECTION_I,
        SECTIONS_II_III,
        SECTION_IV,
        SECTION_V,
        SECTION_VI,
        SECTION_VII,
        SECTION_VIII,
        SECTION_IX,
        "## Acknowledgment\n\n" + AI_ACK,
        refs,
    ]) + "\n"

    required_main = [
        "1,380 temporal trajectories",
        "4,608 exact rule-by-subset observations",
        "420 exact artifact-assurance observations",
        "PRE_ONSET_CACHE",
        "Affected `V4` records never qualify",
        "`B2` zeros are structural",
        "all `Q6` variants are 6/6 and 2/2",
        "all `Q7` variants are 7/7 and 1/1",
        "`G5` leaves only `APPROVED_BAD_SOURCE`",
        "Only Study 3 models contact",
        "qualification does not establish completed or safe spacecraft recovery",
        "not external replication",
        "OpenAI ChatGPT (GPT-5.6 Sol)",
    ]
    for marker in required_main:
        if marker not in main:
            raise SystemExit(f"ERROR: protected main-text marker missing: {marker}")

    if "—" in main:
        raise SystemExit("ERROR: em dash detected in short main article")
    if "6,408" in main:
        raise SystemExit("ERROR: pooled Paper-2 population detected")
    order = first_use(main)
    if order != list(range(1, 14)):
        raise SystemExit(f"ERROR: citation first-use order is {order}, expected 1..13")

    supp_parts = [
        f"# Supplementary Material for: {TITLE}",
        "This peer-reviewed supplementary document preserves expanded deterministic-model detail that was removed from the shortened main article for page control. It does not add, rerun, enlarge, or modify any frozen experiment. Main-text claims remain interpretable without this file; the appendices provide expanded methods, complete finite maps, and validity detail for review and reproducibility.",
        "## Supplementary Figure S1. Qualitative cross-study synthesis",
        "![Supplementary Figure S1](TAES_FIGURE1_RESIDUAL_BOUNDARIES.png)",
        "**Fig. S1.** Parallel residual trust boundaries across the three separately frozen studies. The panels summarize a qualitative manuscript-level synthesis only; no experimental data flow or integrated three-layer architecture connects Studies 3, 4, and 6. Only Study 3 models contact.",
        supplement_section(S3_SOURCE, "A", "Expanded Study-3 Design and Results", "II", "S1"),
        supplement_section(S4_SOURCE, "B", "Complete Study-4 Threshold Map", "III", "S2"),
        supplement_section(S6_SOURCE, "C", "Expanded Study-6 State and Gate Definitions", "IV", "S3"),
        supplement_section(VALIDITY_SOURCE, "D", "Expanded Validity and Aerospace Boundaries", None, None),
        "## Appendix E. Frozen-population and non-pooling control\n\nThe supplementary material preserves the same study separation as the main article. Study 3 contains 1,380 trajectories, Study 4 contains 4,608 exact rule-by-subset observations, and Study 6 contains 420 exact observations. These units are not pooled and no combined Paper-2 N, success rate, p-value, confidence interval, common effect, or global policy rank is defined.",
    ]
    supplement = "\n\n".join(supp_parts) + "\n"
    if "—" in supplement:
        raise SystemExit("ERROR: em dash detected in supplement")

    readme = f"""TAES Paper 2 Supplementary Material README\n\nMain article title:\n{TITLE}\n\nFiles in the intended supplementary package:\n1. TAES_10P_SUPPLEMENTARY_MATERIAL.pdf - peer-reviewed expanded methods, complete finite maps, and validity detail.\n2. TAES_FIGURE1_RESIDUAL_BOUNDARIES.pdf - vector source for Supplementary Fig. S1 if the portal accepts a separate figure asset; otherwise Fig. S1 is embedded in the supplementary PDF.\n\nPurpose:\nThe supplementary material preserves expanded detail relocated from the audited 16-page R9 manuscript to permit a shorter self-contained TAES Regular Paper. It does not add or alter experimental results.\n\nFrozen studies:\nStudy 3: S3-K4E-001\nStudy 4: S4-MPQ-001\nStudy 6: S6-SCTR-001\n\nThe main article must be reviewed together with this supplementary material during peer review.\n"""

    OUT_MAIN.write_text(main, encoding="utf-8")
    OUT_SUPP.write_text(supplement, encoding="utf-8")
    OUT_README.write_text(readme, encoding="utf-8")

    baseline_words = word_count(read(BASELINE_MD))
    main_words = word_count(main)
    refs_words = word_count(refs)
    supp_words = word_count(supplement)
    reduction = baseline_words - main_words

    audit = "\n".join([
        "TAES_10PAGE_CANDIDATE_GENERATION=PASS_LOCAL_UNTRACKED_ONLY",
        f"frozen_r9_manuscript_sha256={EXPECTED_BASELINE_MD}",
        f"frozen_r9_pdf_sha256={EXPECTED_BASELINE_PDF}",
        f"baseline_words_including_references={baseline_words}",
        f"short_main_words_including_references={main_words}",
        f"short_main_reduction_words={reduction}",
        f"references_words={refs_words}",
        f"supplement_words={supp_words}",
        f"abstract_words={word_count(abstract)}",
        f"citation_first_use_order={','.join(str(n) for n in order)}",
        f"short_main_sha256={sha256(OUT_MAIN)}",
        f"supplement_sha256={sha256(OUT_SUPP)}",
        f"readme_sha256={sha256(OUT_README)}",
        "figure1_main_article=RETIRED_MOVED_TO_SUPPLEMENT",
        "common_framework_table1_main_article=RETIRED_PROSE_RETAINED",
        "study4_complete_18_rule_map=SUPPLEMENT_APPENDIX_B",
        "science_files_changed=NONE",
        "study_rerun=NO",
        "publisher_facing=NO",
        "merge_to_main=NOT_AUTHORIZED_UNTIL_QA_PASS",
    ]) + "\n"
    OUT_AUDIT.write_text(audit, encoding="utf-8")
    print(audit, end="")


if __name__ == "__main__":
    main()
