#!/usr/bin/env python3
"""Apply the controlled second TAES Paper-2 compression candidate.

This script edits manuscript prose only. It does not rerun, enlarge, or modify
Studies 3, 4, or 6, their frozen evidence, result files, protocols, or audits.

Pass 2 intentionally edits only Sections IV, V, VI, VIII, and IX. Sections I,
II, III, and VII remain byte-identical to the compliance-corrected canonical
source so the already-compressed framing and authoritative prior-art positioning
are not repeatedly squeezed.

The script is deterministic and guarded by the exact pre-pass SHA-256 values.
It assembles a local candidate and runs the existing length/redundancy audit.
It does not commit, push, build a publisher-facing PDF, or authorize submission.
"""

from __future__ import annotations

import hashlib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

FILES = {
    "iv": ROOT / "TAES_SECTION_IV_STUDY3.md",
    "v": ROOT / "TAES_SECTION_V_STUDY4.md",
    "vi": ROOT / "TAES_SECTION_VI_STUDY6.md",
    "viii": ROOT / "TAES_SECTION_VIII_VALIDITY.md",
    "ix": ROOT / "TAES_SECTION_IX_CONCLUSION.md",
}

EXPECTED_PRE_SHA256 = {
    "TAES_SECTION_IV_STUDY3.md": "e31836745677ca7c1aaecb665a6c18dc11201676f4dad351c7f7469e9ac9325e",
    "TAES_SECTION_V_STUDY4.md": "18543f9118200919d35d4171497352eb2c3785a042fdb5de56be5e5798cf1b97",
    "TAES_SECTION_VI_STUDY6.md": "6db7f547ab7a58c285ac9edae262785008398a6c199b297f28dcf002d1cf66bb",
    "TAES_SECTION_VIII_VALIDITY.md": "9b4a4b34cdd9a198230b2808122a94666c3f4d95435a9bfdd0d181a2f6a64c35",
    "TAES_SECTION_IX_CONCLUSION.md": "102e462bfc40ce0aea13446f3bf747abf0ab8cc3e12da8771d0a2ea6e69daccf",
}

UNTOUCHED = {
    "TAES_ABSTRACT_KEYWORDS.md": "79560ae13b065fe34a6e6fd224a047acdb7e089b70ef6fb7eab5ec6e57e174fd",
    "TAES_SECTION_I_INTRODUCTION.md": "4aa0f5d2f34fc718b12732cc92ec2a8a1c4176a4dc582c2b60a9c6e3f48135ff",
    "TAES_MANUSCRIPT_SOURCE.md": "7146b02da2dcd09f9ee89e6cc4dfa796f7cc2ba7dc9f86238c5ed08c475941a9",
    "TAES_SECTION_VII_SYNTHESIS.md": "e8da497e48e33dc1e2d7bff74e792fedcf070bf631e5de5d8348f72262d85ead",
    "TAES_ACKNOWLEDGMENT_AI_DISCLOSURE.md": "39dda9826bfc4373eb3a2d5691e622ad0cbc7f19f76c0e7e0df0d12dd8bdcef9",
    "TAES_FIGURE1_RESIDUAL_BOUNDARIES.pdf": "4872707261c8a8b6b747e76b9166b4ad7ae426e43d7bd9ffe272e4c5ea6f4ff8",
    "TAES_FIGURE1_RESIDUAL_BOUNDARIES.png": "7d22964bdae052b35b4680e1b09f3209f1c99bb1d157a0f995dcd2a6445e6698",
}

WORD_RE = re.compile(r"\b[\w'-]+\b")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def words(text: str) -> int:
    return len(WORD_RE.findall(text))


def require_sha(path: Path, expected: str) -> None:
    if not path.is_file():
        raise SystemExit(f"ERROR: missing required file: {path}")
    actual = sha256(path)
    if actual != expected:
        raise SystemExit(
            f"ERROR: pre-pass SHA mismatch for {path.name}: expected {expected}, got {actual}"
        )


IV = r'''# IV. Temporal Evidence Qualification Under Intermittent Contact

## A. Study Question and Design

Study 3 (`S3-K4E-001`) evaluates when runtime recovery evidence remains policy-qualified after research-only authorization has changed. It varies contact availability, evidence semantics, and whether an affected post-onset record occurs once or persists. The model is deterministic and uses logical time rather than wall-clock or flight time.

The horizon is 240 logical seconds in five-logical-second epochs, with five logical seconds of evidence validity. The onset grid contains 46 prespecified phases from 10 through 235 logical seconds in five-second increments. Hidden authorization is `true` before onset and `false` at and after onset; the post-onset security signal is `true`. Hidden authorization is never supplied to the selector.

`K0` provides continuous modeled contact from 0 through 240. `K4` provides synthetic windows `[25,35]`, `[75,90]`, `[145,165]`, and `[220,240]`. New records arrive only during modeled contact; otherwise the selector can use the latest received record subject to freshness. K4 is a deterministic contact treatment, not an orbital pass schedule or operational-access estimate.

The evidence treatments are:

1. `V0`: truthful evidence. A post-onset record reports authorization `false` with a valid signature.
2. `V4`: post-signature value manipulation. The signed post-onset value is changed from `false` to `true`, invalidating the signature.
3. `V5`: compromised trusted-producer evidence. The producer reports authorization `true` while hidden truth is `false`, and validly signs the false claim.

`V4` and `V5` are each evaluated as one-shot and persistent treatments; `V0` remains truthful. The frozen policy semantics are `S2_B0_FAIL_CLOSED`, `S2_B2_RISK_THRESHOLD`, and `S2_S1_EVIDENCE_AWARE`. The identifiers reuse frozen selector semantics, but no Study-2 result is imported. Thirty cells crossed with 46 onset phases yield 1,380 trajectories and 67,620 epoch states. The trajectory is the study unit; epochs within a trajectory are repeated model states.

## B. Endpoints and Origin Decomposition

Primary endpoints are `unsafe_permissive_epoch_rate`, `unsafe_qualified_epoch_rate`, `unsafe_qualified_exposure_s`, `unsafe_qualified_episode_count`, `protective_epoch_rate`, and `action_transition_count`. This paper emphasizes `unsafe_qualified`: the gate is policy-visible qualified while hidden authorization is false. `unsafe_permissive` is only a selector or gate-entry action metric, not completed recovery.

False-qualified epochs must map to one of two prespecified origins. `PRE_ONSET_CACHE` is a truthful record received before onset that remains policy-fresh afterward; `V5_AFFECTED_RECORD` is a validly signed false record from the compromised trusted producer. This separates ordinary freshness lag from adversarial semantic falsity. Because the frozen onset grid is complete, results are exact finite-grid summaries and paired phase differences, with no p-value gate, weighted policy score, or global policy rank.

## C. Persistent False-but-Valid Evidence Under Continuous Contact

Under persistent `V5/K0`, both `B0` and `S1` were unsafe-qualified in all 46 onset trajectories, with mean exposure 122.5 logical seconds. `B2` remained 0/46 with zero mean exposure in this frozen cell. The V5 records are validly signed; the mismatch exists because the trusted producer itself signs a claim that is false relative to hidden authorization. Signature validity therefore authenticates the modeled producer and record integrity without exposing producer-origin semantic falsity.

The `B2` zero is structural to the frozen policy and treatment grid, not evidence of universal immunity or global superiority.

## D. Persistent V5 Under the Frozen K4 Contact Schedule

Under persistent `V5/K4`, `B0` remained unsafe-qualified in 46/46 trajectories with mean exposure 55.326 logical seconds and a 55.0-logical-second increment over truthful `V0`. `S1` remained unsafe-qualified in 46/46 with mean exposure 49.022 logical seconds, equal to its V5-attributable increment. `B2` remained 0/46. The B0-S1 mean difference was approximately 6.304 logical seconds, so the frozen S1 contact-aware restriction reduced exposure relative to B0 but did not eliminate the V5 boundary.

### Table II. Selected Study-3 residual-boundary results

| Evidence / contact / policy | Unsafe-qualified trajectories | Mean unsafe-qualified exposure, logical s | Interpretation |
|---|---:|---:|---|
| Persistent `V5`, `K0`, `B0` | 46/46 | 122.500 | Sustained false qualification under continuous contact |
| Persistent `V5`, `K0`, `S1` | 46/46 | 122.500 | Same continuous-contact exposure in frozen grid |
| Persistent `V5`, `K0`, `B2` | 0/46 | 0 | Structural zero in frozen policy/treatment cell |
| Persistent `V5`, `K4`, `B0` | 46/46 | 55.326 | Reduced modeled exposure, not elimination |
| Persistent `V5`, `K4`, `S1` | 46/46 | 49.022 | Additional K4 restriction relative to B0, not immunity |
| Persistent `V5`, `K4`, `B2` | 0/46 | 0 | Structural zero in frozen policy/treatment cell |
| Truthful `V0`, `K4`, `B0` | 3/46 | 0.326 | Pre-onset cache boundary, not adversarial evidence |
| Truthful `V0`, `K4`, `S1` | 0/46 | 0 | No truthful-V0 false qualification in frozen K4 grid |
| Truthful `V0`, `K4`, `B2` | 0/46 | 0 | No truthful-V0 false qualification in frozen K4 grid |

K4 mechanically limits record reception under the registered cache semantics; the result does not establish that intermittent contact improves security. Table II values are logical model time, not spacecraft response time, communication latency, operator latency, or ground-contact duration.

## E. Post-Signature Manipulation and the Cryptographic Boundary

Under `V4`, post-signature modification invalidates the affected record's signature, and affected V4 records never qualify. Any B0/K4 false qualification in V4 cells comes instead from a previously received truthful record and is assigned to `PRE_ONSET_CACHE`, not to the manipulated record.

The V4-V5 contrast therefore supports two bounded claims: signature validation rejects the modeled post-signature alteration, while a valid signature alone does not establish semantic truth when the trusted producer signs the false claim. The experiment does not evaluate cryptanalysis, key extraction, or a real signing-system attack.

## F. Freshness and the Truthful Cache Boundary

Under truthful `V0/K4/B0`, 3/46 onset trajectories contained unsafe qualification, with mean exposure 0.326 logical seconds, all attributed to `PRE_ONSET_CACHE`. `S1` and `B2` had no truthful-V0 false qualification under K4. The result is schedule-, epoch-, freshness-, and policy-specific and is not an estimate of spacecraft cache staleness. It demonstrates that ordinary freshness lag can produce false qualification without being conflated with V5 producer-origin false evidence, consistent with RFC 9334's freshness limitation [5].

## G. One-Shot V5 and Temporal Persistence

One-shot `V5/K0` produced five logical seconds of mean unsafe-qualified exposure for both `B0` and `S1` across all 46 onset phases. Under K4, all 46 B0 and S1 trajectories eventually received the one-shot compromised record; S1 retained five logical seconds of V5 exposure, while B0 also contains the separately identified cache boundary. One-shot and persistent V5 are cryptographically the same false-but-valid producer claim; persistence determines whether the claim appears once or is renewed after later contact.

## H. Study-3 Residual Trust Boundary

Study 3 therefore separates two residual boundaries: brief truthful freshness lag and false but validly signed evidence from a compromised trusted producer. Contact-aware restrictions reduce selected K4 exposure but do not eliminate persistent V5 qualification for `B0` or `S1`. These are exact properties of the frozen grid, not estimates of compromise prevalence, unsafe-recovery probability, operational mission risk, or real spacecraft timing.
'''

V = r'''# V. Multi-Producer Qualification and Provenance-Domain Constraints

## A. Study Question and Exact Population

Study 4 (`S4-MPQ-001`) evaluates how absolute vote count and synthetic provenance-domain requirements change recovery qualification under two separate conditions: malicious producer compromise and benign producer unavailability.

Seven producers `P1`-`P7` are assigned to frozen domains `D1={P1,P2,P3}`, `D2={P4,P5}`, and `D3={P6,P7}`. These are synthetic independence classes, not demonstrated organizational, hardware, software, supply-chain, or operator independence. A rule `Qq_Dd` requires `q` qualifying claims and `d` represented domains, with `q=1..7` and `d=1..min(3,q)`, yielding 18 rules. The denominator is always the registered seven-producer set.

In the safety block, hidden authorization is false; all producers are available; compromised producers emit validly signed authorization-true claims and honest producers emit false. `unsafe_qualified` is true when the compromised subset satisfies the rule. In the benign availability block, hidden authorization is true; affected producers are unavailable; all available producers emit validly signed true claims; and `false_conservative` is true when the rule rejects because insufficient votes or domains remain.

Every producer subset is evaluated: 128 subsets per block per rule, for `18 x 2 x 128 = 4,608` exact observations. The two blocks are not combined and do not model simultaneous compromise plus benign loss.

## B. First and Systematic Failure Definitions

For each rule and block, the **first failure count** is the smallest affected-producer count for which at least one subset fails; the **systematic failure count** is the smallest count for which every subset fails. The distinction captures subset dependence introduced by provenance composition. Because all subsets are enumerated, these are finite combinatorial properties, not compromise, outage, or mission-availability probabilities.

## C. Exact Threshold Map

Table III gives the complete frozen map as `first/systematic` counts.

### Table III. Study-4 first and systematic failure thresholds

| Rule | Unsafe qualification, compromised producers | False-conservative rejection, unavailable producers |
|---|---:|---:|
| `Q1_D1` | 1/1 | 7/7 |
| `Q2_D1` | 2/2 | 6/6 |
| `Q2_D2` | 2/4 | 4/6 |
| `Q3_D1` | 3/3 | 5/5 |
| `Q3_D2` | 3/4 | 4/5 |
| `Q3_D3` | 3/6 | 2/5 |
| `Q4_D1` | 4/4 | 4/4 |
| `Q4_D2` | 4/4 | 4/4 |
| `Q4_D3` | 4/6 | 2/4 |
| `Q5_D1` | 5/5 | 3/3 |
| `Q5_D2` | 5/5 | 3/3 |
| `Q5_D3` | 5/6 | 2/3 |
| `Q6_D1` | 6/6 | 2/2 |
| `Q6_D2` | 6/6 | 2/2 |
| `Q6_D3` | 6/6 | 2/2 |
| `Q7_D1` | 7/7 | 1/1 |
| `Q7_D2` | 7/7 | 1/1 |
| `Q7_D3` | 7/7 | 1/1 |

Absolute vote count sets the basic compromise boundary while moving benign-loss tolerance in the opposite direction. Provenance can further delay systematic unsafe qualification for selected thresholds, but can also cause earlier false-conservative rejection.

## D. Absolute Vote Count Sets the Basic Compromise Boundary

With only one required domain, unsafe qualification follows the vote threshold directly: `Q1_D1` through `Q7_D1` require one through seven compromised producers. Benign tolerance moves oppositely: `Q1_D1` can tolerate six unavailable producers, `Q4_D1` fails at 4/4, and `Q7_D1` rejects after any single loss. This familiar quorum tradeoff is prior art [7], [8]; Study 4 contributes the exact mapping for the frozen recovery-evidence model and its provenance variants.

## E. Provenance Diversity Changes Systematic Failure Without Necessarily Changing First Failure

`Q3_D3` shows the clearest provenance effect. First unsafe failure remains at three compromised producers, as under `Q3_D1`, but a three-producer subset must span all three domains; systematic failure moves from 3 under `Q3_D1` to 6 under `Q3_D3`. The same pattern appears at `Q4_D3` (4/6) and `Q5_D3` (5/6). Reporting first and systematic counts together prevents a single threshold from hiding this subset dependence.

## F. Provenance Diversity Also Creates Earlier Benign Rejection for Selected Rules

The same structure can reduce benign qualification tolerance. `Q3_D1` fails at 5/5 unavailable producers, whereas `Q3_D3` first fails at two and becomes systematic at five because two losses can remove an entire domain. `Q4_D3` similarly changes benign failure from 4/4 under `Q4_D1` to 2/4, and `Q5_D3` first fails at two versus three under `Q5_D1`. These are qualification effects under the frozen denominator and domain assignment, not mission-availability measurements.

## G. Null and Equal-Threshold Results

Provenance is not monotonically beneficial. `Q4_D1` and `Q4_D2` are identical in both blocks at 4/4; `Q5_D1` and `Q5_D2` are identical at safety 5/5 and benign availability 3/3; all `Q6` variants are 6/6 and 2/2; and all `Q7` variants are 7/7 and 1/1. The effect of domain requirements is therefore conditional on vote threshold, domain allocation, and subset composition.

## H. The Q4 Boundary as a Symmetric Reference Case

`Q4_D1` is symmetric at 4/4 in both separately evaluated blocks, whereas `Q4_D3` preserves first unsafe failure at four, moves systematic unsafe failure to six, moves first benign failure to two, and leaves systematic benign failure at four. This compact case illustrates why vote count alone does not describe a provenance-constrained rule.

## I. High Vote Thresholds and the Loss-Tolerance Boundary

At high thresholds, compromise resistance increases while benign-loss tolerance tightens: `Q5_D1`, `Q6`, and `Q7` require five, six, and seven compromised producers respectively, but become false-conservative after three, two, and one unavailable producers. With no utility weights, operational probabilities, or mission costs, the grid does not define a globally best rule.

## J. Relationship to Distributed Trust Prior Art

Study 4 is a deterministic qualification model, not Byzantine consensus or distributed agreement: producers do not run an agreement protocol, and the model does not analyze leaders, forks, liveness, partitions, replicated state, or Byzantine broadcast. Quorum literature [7], [8] and satellite endorsement-quorum work [9] provide structural prior art; the contribution here is the frozen recovery-qualification threshold map.

## K. Study-4 Residual Trust Boundary

Absolute vote count sets the basic compromise boundary, while synthetic provenance constraints change which same-size subsets qualify, delaying systematic failure in selected cells and causing earlier benign rejection in others. The 128 subsets are model states rather than probabilities, the domains are labels rather than demonstrated real independence, and Study 4 contains no contact model. The result is a conditional qualification frontier, not a global policy ranking.
'''

VI = r'''# VI. Recovery-Artifact Assurance and Residual Incorrect States

## A. Study Question and Model Boundary

Study 6 (`S6-SCTR-001`) asks which objectively incorrect recovery artifacts remain qualified as assurance signals are composed, and what benign qualification cost appears when required signals are unavailable. It is an exact finite Boolean model, not a malware experiment, production build pipeline, real signing-key system, supply-chain compromise, or operational spacecraft recovery. SLSA, TUF, SPARTA, and related concepts motivate dimensions but do not establish compliance.

The research-only oracle `objective_baseline_correct` is never provided to a gate; each gate sees only its required policy-visible assurance signals.

## B. Artifact States and Assurance Signals

`CLEAN_APPROVED` is objectively correct with all six visible signals true. Five states are objectively incorrect:

1. `POST_RELEASE_TAMPER`: signature, digest, provenance, and reproduced-build signals false; review and approval true.
2. `TRUSTED_SIGNER_COMPROMISE`: signature valid; digest, provenance, and reproduced-build signals false; review true; approval false.
3. `TRUSTED_BUILDER_COMPROMISE`: signature, digest, provenance, review, and approval true; reproduced-build match false.
4. `SOURCE_REVIEW_BYPASS`: signature, digest, provenance, reproduced-build, and approval true; review attestation false.
5. `APPROVED_BAD_SOURCE`: all six gate-visible signals true while objective correctness is false.

The visible signals are `signature_valid`, `independent_target_digest_match`, `provenance_valid`, `independent_reproduced_build_match`, `source_review_attested`, and `release_approved`. "Independent" is part of the abstraction and does not demonstrate real organizational, hardware, network, or build-infrastructure independence.

## C. Assurance Gates and Exact Population

The six gates are:

- `G0_SIGNATURE_ONLY`: signature;
- `G1_SIGNATURE_TARGET_DIGEST`: signature + independent target digest;
- `G2_SIGNATURE_PROVENANCE`: signature + provenance;
- `G3_PROVENANCE_REPRODUCED_BUILD`: signature + provenance + reproduced-build match;
- `G4_PROVENANCE_SOURCE_REVIEW`: signature + provenance + source-review attestation;
- `G5_COMPOSITE`: all six visible signals.

Block A crosses six artifact states with six gates for 36 observations; `unsafe_qualified` means an objectively incorrect artifact qualifies. Block B crosses the correct `CLEAN_APPROVED` baseline with all 64 unavailable-signal subsets and six gates for 384 observations; `benign_availability_loss` means the correct baseline is rejected because required signals are missing. The total population is 420 exact observations. The blocks are separate and do not model artifact compromise plus signal loss simultaneously.

## D. Signature, Digest, and Provenance Boundaries

`G0` rejects only `POST_RELEASE_TAMPER` and qualifies the other four incorrect states, yielding 4/5. `G1` and `G2` each leave three incorrect states in this frozen set: `TRUSTED_BUILDER_COMPROMISE`, `SOURCE_REVIEW_BYPASS`, and `APPROVED_BAD_SOURCE`. Their equal counts and residual set do not establish operational equivalence between digest and provenance mechanisms. These finite ratios are state counts, not detection rates or attack-population estimates.

## E. Reproduced-Build and Source-Review Gates Are Complementary

`G3` leaves `SOURCE_REVIEW_BYPASS` and `APPROVED_BAD_SOURCE`, whereas `G4` leaves `TRUSTED_BUILDER_COMPROMISE` and `APPROVED_BAD_SOURCE`. Their equal 2/5 counts therefore conceal different residual trust assumptions: reproduced-build evidence closes the modeled builder pathway, while source-review evidence closes the review-bypass pathway.

## F. Composite Assurance Leaves the Approved-Bad-Source Boundary

`G5_COMPOSITE` leaves only `APPROVED_BAD_SOURCE`. All six gate-visible signals are true while research-only objective correctness is false, so the frozen gate has no visible basis for rejection. This is a structural observability boundary, not an information-theoretic impossibility theorem or evidence that additional semantic validation, formal verification, behavioral testing, runtime validation, or diverse implementations could not add information. The result is consistent with SLSA's recognized malicious-producer trust boundary [13]; the contribution here is the exact residual-state mapping of the recovery-artifact model.

## G. Exact Gate Frontier

Table IV gives the canonical residual-state and benign-loss frontier.

### Table IV. Study-6 residual incorrect states and benign assurance loss

| Gate | Required visible signals | Incorrect states still qualified | Unsafe count | Benign-loss subsets |
|---|---:|---|---:|---:|
| `G0_SIGNATURE_ONLY` | 1 | `APPROVED_BAD_SOURCE`; `SOURCE_REVIEW_BYPASS`; `TRUSTED_BUILDER_COMPROMISE`; `TRUSTED_SIGNER_COMPROMISE` | 4/5 | 32/64 |
| `G1_SIGNATURE_TARGET_DIGEST` | 2 | `APPROVED_BAD_SOURCE`; `SOURCE_REVIEW_BYPASS`; `TRUSTED_BUILDER_COMPROMISE` | 3/5 | 48/64 |
| `G2_SIGNATURE_PROVENANCE` | 2 | `APPROVED_BAD_SOURCE`; `SOURCE_REVIEW_BYPASS`; `TRUSTED_BUILDER_COMPROMISE` | 3/5 | 48/64 |
| `G3_PROVENANCE_REPRODUCED_BUILD` | 3 | `APPROVED_BAD_SOURCE`; `SOURCE_REVIEW_BYPASS` | 2/5 | 56/64 |
| `G4_PROVENANCE_SOURCE_REVIEW` | 3 | `APPROVED_BAD_SOURCE`; `TRUSTED_BUILDER_COMPROMISE` | 2/5 | 56/64 |
| `G5_COMPOSITE` | 6 | `APPROVED_BAD_SOURCE` | 1/5 | 63/64 |

For every gate, one missing required signal is sufficient to cause benign rejection in at least one subset. The denominators are finite model populations: `1/5` is not a 20 percent attack rate and `63/64` is not a 98.4 percent outage probability.

## H. Stronger Gates Increase Sensitivity to Benign Assurance Loss

Benign-loss counts rise from 32/64 for `G0`, to 48/64 for the two two-signal gates, 56/64 for the two three-signal gates, and 63/64 for `G5`. Thus stronger gates narrow the modeled incorrect-state set while increasing sensitivity to missing evidence. No operational probabilities, utility weights, or mission costs are assigned, and "availability" here is qualification availability under assurance-signal loss, not mission availability, spacecraft contact, network availability, or service uptime.

## I. Relationship to Provenance and Update-Security Prior Art

in-toto, TUF, SLSA, and SPARTA already provide or motivate provenance, signed metadata, target binding, controlled build processes, source assurance, and trusted recovery baselines [4], [10], [11], [12], [13]. Study 6 neither replaces nor validates those systems and claims no standards compliance. Its question is narrower: which prespecified incorrect artifacts remain observationally acceptable under each frozen combination of visible assurance signals?

## J. Study-6 Residual Trust Boundary

Composing assurance signals closes specific modeled pathways but leaves different residual assumptions depending on what is visible. The composite gate leaves only `APPROVED_BAD_SOURCE`, while stronger gates also increase benign signal-loss rejection. The result is a finite residual-correctness versus qualification-availability frontier, not a globally best gate.
'''

VIII = r'''# VIII. Validity, Aerospace Interpretation Boundaries, and Future Evaluation

## A. Internal and Construct Validity

The strongest claims are internal to three separately frozen deterministic models. Study 3 preserves policy-visible evidence versus hidden authorization and prespecified false-qualification origins; Study 4 exhausts every producer subset for every registered rule in separate compromise and benign-loss blocks; Study 6 exhausts prespecified artifact states and benign signal-loss subsets. Repository audits reported zero mismatches for their registered outputs.

The common residual-trust framework is a post hoc systems-level synthesis, not a prospectively tested treatment or integrated three-layer experiment. `unsafe_qualified`, Study-4 false-conservative rejection, and Study-6 benign availability loss are qualification constructs; none is equivalent to spacecraft physical safety, mission availability, or completed recovery.

## B. Study-3 Boundary Conditions

Study 3 characterizes one continuous regime and the registered synthetic K4 windows over a 240-logical-second horizon with five-second epochs and evidence validity. It does not establish behavior under other contact schedules, orbital geometry, latencies, evidence lifetimes, or mission-specific ground coverage. Logical seconds are model units, not processor, RF, ground-station, operator, or orbital time; the reported 122.5, 55.326, 49.022, 5, and 0.326 exposures remain model quantities.

The 46 onset phases exhaust the frozen grid rather than sample an operational distribution, and 67,620 epoch states are repeated states within 1,380 trajectory units. V5 assumes a trusted producer can validly sign a false claim but does not model how compromise occurs; V4 models post-signature alteration that invalidates the signature. Their contrast does not evaluate cryptographic strength or key-management security.

## C. Study-4 Boundary Conditions

Study 4 is conditional on seven producers, the 3/2/2 synthetic domain allocation, registered-producer denominator, and 18 rule definitions. Different membership, allocation, weighting, or denominator semantics can produce different thresholds. The domains do not demonstrate organizational, hardware, software, network, sensing-path, administrative, or supply-chain independence.

The compromise and benign-unavailability blocks are separate and exclude the joint condition. The model also excludes adaptive strategies, richer collusion behavior, network timing, Byzantine agreement, leader election, and sensor-estimation error. The 128 subsets per block are complete combinatorial model states, not compromise or outage probabilities, and first/systematic thresholds are not operational reliability limits.

## D. Study-6 Boundary Conditions

Study 6 is an abstract six-state, six-gate Boolean model, not an exhaustive software-supply-chain taxonomy. Counts `4/5`, `3/5`, `2/5`, and `1/5` are finite state counts rather than detection or false-negative rates. Modeled "independent" signals do not establish real organizational or infrastructure independence, and review/approval variables do not measure real process quality or adversarial resistance.

`APPROVED_BAD_SOURCE` deliberately has all six gate-visible signals true while objective correctness is false; it marks the frozen model's observability boundary, not a theorem about semantic correctness. All 64 benign signal-loss subsets use the correct baseline, so counts such as `63/64` are deterministic subset counts rather than service, contact, or outage probabilities.

## E. External Validity and Aerospace Generalization

Paper 2 does not operate an on-orbit spacecraft, ground station, RF link, flight processor, production key infrastructure, or real mission command path, and no operational spacecraft recovery is executed. The results do not establish flightworthiness, certification, mission-assurance compliance, operational attack prevalence, recovery success probability, or mission-level availability.

Only Study 3 models contact. Study-4 producer unavailability is not spacecraft-contact loss, and Study-6 assurance-signal unavailability is not contact loss or network outage. Generalization requires mapping the abstract producers, domains, timing semantics, gates, and failure states to a specific mission architecture and validating that mapping operationally.

## F. Statistical Interpretation

The studies evaluate complete finite populations specified by frozen protocols. Exact counts and thresholds therefore do not require sampling-based p-values, confidence intervals, or assumed-superpopulation inference, but exactness within a registered grid does not make results universal. Model choice, omitted operational variables, and external validity remain sources of uncertainty.

The populations are also incommensurate: trajectories in Study 3, rule-by-subset observations in Study 4, and artifact-state / assurance-unavailability observations in Study 6. Their arithmetic sum is not a meaningful sample size; no pooled `N`, success percentage, confidence interval, common effect, or global rank is defined.

## G. Reproducibility and Independence

Repository-bound independent audits reported zero Study-3 trajectory/origin mismatches, zero Study-4 observation/threshold mismatches under reconstruction, and zero Study-6 mismatches with frozen outputs. These controls support same-repository reproducibility, not external empirical replication. External replication requires an independent research group, environment, or evidence source beyond the present repository program.

## H. Standards and Framework Interpretation

RATS, SPARTA, SLSA, TUF, in-toto, and related sources position the modeled evidence dimensions; the studies do not implement every framework requirement and no compliance assessment was performed. Model variables named provenance, reproduced build, source review, or release approval therefore do not establish SLSA, TUF, SPARTA, or other standards compliance.

## I. Limits of the Cross-Study Synthesis

The synthesis compares residual mechanisms rather than causal transitions: Study 4 does not experimentally mitigate Study 3, Study 6 does not validate a downstream gate for either earlier study, and no data flow connects the frozen populations. The three layers are also not claimed to be complete; real recovery can depend on command authority, hardware roots, behavioral verification, physical-state estimation, network integrity, human authorization, fault management, and mission-phase constraints.

The layered interpretation is therefore an analytical decomposition of the three evaluated mechanisms, not a claim that every recovery architecture should contain exactly these layers or evaluate them in this order.

## J. Future Evaluation

Future prospective work could test orbital-contact schedules, variable evidence lifetimes, and hardware/software-in-the-loop timing for Study-3 mechanisms; alternative producer counts, empirically justified failure domains, dynamic membership, and joint compromise/loss for Study 4; and real build pipelines, independent assurance services, semantic validation, or joint artifact-compromise/evidence-loss scenarios for Study 6.

A separate integrated experiment could prospectively define joint interventions, units, and endpoints across runtime evidence, producer composition, and artifact assurance. Such extensions would broaden external validation without reopening the frozen Studies 3, 4, or 6 reported here.
'''

IX = r'''# IX. Conclusion

Paper 2 characterizes trusted cyber-recovery qualification through three separately frozen deterministic studies rather than one integrated experiment. Study 3 separates brief truthful pre-onset cache exposure from false but validly signed `V5` evidence issued by a compromised trusted producer; persistent V5 remains qualified for `B0` and `S1` across all 46 onset phases under both `K0` and synthetic `K4`, although K4 reduces modeled exposure. Affected `V4` post-signature-manipulated records have invalid signatures and do not qualify.

Study 4 shows that absolute vote count establishes the basic compromise boundary while synthetic provenance-domain requirements change which same-size subsets can satisfy it. Selected requirements delay systematic unsafe qualification but cause earlier benign false-conservative rejection, while other domain requirements have null threshold effects. Study 6 similarly shows that composed artifact-assurance signals close specific incorrect states: the six-signal gate leaves only `APPROVED_BAD_SOURCE`, while stronger gates increase rejection under benign assurance-signal loss.

Across the three studies, stronger trust composition moves or narrows modeled qualification boundaries without making policy-visible evidence equivalent to hidden or objective truth. Residual identity matters as much as aggregate count or duration. The results remain bounded to finite models: only Study 3 models contact, logical time is not operational spacecraft time, synthetic domains do not establish real independence, Study 6 is not a real supply-chain experiment, and no pooled population, global policy ranking, flight-safety claim, mission-availability claim, or operational recovery probability is inferred.
'''

NEW_CONTENT = {
    "iv": IV,
    "v": V,
    "vi": VI,
    "viii": VIII,
    "ix": IX,
}

REQUIRED_MARKERS = [
    "1,380",
    "67,620",
    "PRE_ONSET_CACHE",
    "V5_AFFECTED_RECORD",
    "122.5",
    "55.326",
    "49.022",
    "0.326",
    "4,608",
    "Q3_D3",
    "Q4_D3",
    "Q5_D3",
    "420 exact observations",
    "APPROVED_BAD_SOURCE",
    "32/64",
    "48/64",
    "56/64",
    "63/64",
    "not a globally best",
    "Only Study 3 models contact",
    "not external empirical replication",
    "not a claim that every recovery architecture",
]

FORBIDDEN = [
    "6,408",
    "global best policy",
    "mission availability improves",
    "operational attack rate",
]


def main() -> None:
    # Exact pre-pass state guard.
    for path in FILES.values():
        require_sha(path, EXPECTED_PRE_SHA256[path.name])
    for name, expected in UNTOUCHED.items():
        require_sha(ROOT / name, expected)

    before_words = {key: words(path.read_text(encoding="utf-8")) for key, path in FILES.items()}

    # Preflight the candidate text before writing anything.
    joined = "\n".join(NEW_CONTENT.values())
    if "—" in joined:
        raise SystemExit("ERROR: em dash detected in pass-2 candidate")
    for marker in REQUIRED_MARKERS:
        if marker not in joined:
            raise SystemExit(f"ERROR: protected pass-2 marker missing: {marker}")
    for marker in FORBIDDEN:
        if marker.lower() in joined.lower():
            raise SystemExit(f"ERROR: forbidden pass-2 marker detected: {marker}")

    for key, path in FILES.items():
        path.write_text(NEW_CONTENT[key].strip() + "\n", encoding="utf-8")

    # Verify untouched components did not drift.
    for name, expected in UNTOUCHED.items():
        require_sha(ROOT / name, expected)

    after_words = {key: words(path.read_text(encoding="utf-8")) for key, path in FILES.items()}
    before_total = sum(before_words.values())
    after_total = sum(after_words.values())
    reduction = before_total - after_total
    if reduction < 1200:
        raise SystemExit(f"ERROR: pass-2 reduction unexpectedly small: {reduction} words")
    if reduction > 2600:
        raise SystemExit(f"ERROR: pass-2 reduction exceeds controlled range: {reduction} words")

    assembler = ROOT / "TAES_ASSEMBLE_MANUSCRIPT.py"
    audit = ROOT / "TAES_AUDIT_LENGTH_REDUNDANCY.py"
    subprocess.run([sys.executable, str(assembler)], cwd=ROOT, check=True)
    subprocess.run([sys.executable, str(audit)], cwd=ROOT, check=True)

    full = (ROOT / "TAES_MANUSCRIPT_FULL_DRAFT.md").read_text(encoding="utf-8")
    for marker in REQUIRED_MARKERS:
        if marker not in full:
            raise SystemExit(f"ERROR: assembled protected marker missing: {marker}")

    print("TAES_COMPRESSION_PASS2=PASS_LOCAL_CANDIDATE_ONLY")
    print("science_files_changed=NONE")
    print("sections_changed=IV,V,VI,VIII,IX")
    print("sections_I_II_III_VII_changed=NO")
    print("abstract_changed=NO")
    print("references_changed=NO")
    print("figure1_changed=NO")
    print("ai_disclosure_changed=NO")
    print("study_rerun=NO")
    print(f"edited_sections_before_words={before_total}")
    print(f"edited_sections_after_words={after_total}")
    print(f"edited_sections_reduction_words={reduction}")
    for key in ("iv", "v", "vi", "viii", "ix"):
        print(f"section_{key}_words={before_words[key]}->{after_words[key]}")
    print(f"assembled_sha256={sha256(ROOT / 'TAES_MANUSCRIPT_FULL_DRAFT.md')}")
    print("candidate_status=UNTRACKED_REVIEW_REQUIRED")
    print("publisher_facing=NO")
    print("submission_effective=NO_PENDING_REMAINING_GATES")


if __name__ == "__main__":
    main()
