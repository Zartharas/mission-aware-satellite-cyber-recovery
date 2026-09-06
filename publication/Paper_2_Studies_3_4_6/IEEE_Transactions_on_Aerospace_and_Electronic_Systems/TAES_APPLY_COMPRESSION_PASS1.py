#!/usr/bin/env python3
"""Apply TAES Paper 2 editorial compression pass 1.

This helper edits only the Introduction, Section III, and Section VII. It does
not rerun studies, alter frozen numerical results, change the bibliography, or
modify Section VIII validity controls. The purpose is to remove duplicated
method, synthesis, and limitation prose while preserving all scientific claim
boundaries.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INTRO = ROOT / "TAES_SECTION_I_INTRODUCTION.md"
CORE = ROOT / "TAES_MANUSCRIPT_SOURCE.md"
SYNTH = ROOT / "TAES_SECTION_VII_SYNTHESIS.md"


def read(path: Path) -> str:
    if not path.is_file():
        raise SystemExit(f"ERROR: missing required file: {path}")
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def write(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def words(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text))


INTRO_NEW = r'''# I. Introduction

Cyber recovery in satellite systems can require trust decisions under communication gaps, constrained postlaunch access, and mission-continuity pressure [1]. Recovery is therefore not only a restoration problem but also a qualification problem: before a policy permits a recovery path, it must decide whether the available runtime evidence, the producers supplying that evidence, and the recovery artifact are sufficiently trustworthy for the modeled decision.

Prior work already establishes the main mechanisms used here. Satellite research examines internal trust boundaries and testable cyber-resilience requirements [2], [3], while SPARTA describes integrity-protected trusted recovery baselines [4]. RATS distinguishes evidence from appraisal and treats freshness as an explicit concern [5], with current work also considering multiple-Verifier composition [6]. Quorum systems formalize trust and failure assumptions [7], [8], and recent satellite trusted-execution work uses Byzantine-tolerant endorsement quorums [9]. Software-supply-chain systems provide provenance, signed metadata, hashes, controlled build processes, and source assurance [10], [11], [12], while SLSA also documents limits involving intentionally malicious producers [13]. This paper does not claim novelty for those mechanisms.

The narrower question is: **what residual trust boundary remains when a recovery-qualification policy can satisfy its visible checks while a relevant research-only authorization or correctness state differs?** Runtime evidence can be authentic and fresh but semantically false if a trusted producer is compromised. Multiple producers can reduce dependence on one source, but the boundary then depends on vote count, provenance assumptions, and producer availability. Artifact assurance can close several integrity and process failures while still depending on a higher-level assumption about approved source correctness.

Three separately frozen deterministic studies examine those boundaries without forming one integrated experiment or pooled population. Study 3 evaluates 1,380 temporal trajectories under continuous and synthetic intermittent contact. Study 4 evaluates 4,608 exact rule-by-subset observations across 18 vote and synthetic provenance-domain rules. Study 6 evaluates 420 exact observations across six artifact states, six assurance gates, and benign assurance-signal unavailability. Each study retains its own unit, interventions, endpoints, and model boundary.

The research questions are:

**RQ1:** Under the frozen continuous and intermittent-contact schedules, how do truthful evidence, post-signature modification, and false but validly signed claims from a compromised trusted producer affect the duration and recurrence of false recovery qualification across the Study-3 policy semantics?

**RQ2:** When recovery authorization is supported by multiple modeled evidence producers, how do absolute vote thresholds and synthetic provenance-domain requirements change the first and systematic failure boundaries for unsafe qualification under producer compromise and false-conservative qualification under benign producer loss?

**RQ3:** When the recovery artifact is subjected to progressively composed assurance requirements, which prespecified incorrect artifact states remain qualified, and what benign qualification loss results when required assurance signals become unavailable?

A systems-level synthesis then asks how these independently measured boundaries relate across temporal runtime evidence, producer composition, and recovery-artifact assurance. The synthesis is qualitative and mechanism based; it does not estimate a common treatment effect, pooled success rate, or end-to-end recovery probability.

The paper makes four bounded contributions:

1. **Temporal qualification boundary.** Study 3 separates a short truthful pre-onset cache boundary from false qualification caused by a compromised trusted producer that continues to generate fresh and validly signed false evidence, while the post-signature-manipulation control distinguishes semantic producer failure from invalidly signed alteration.
2. **Producer-composition boundary.** Study 4 provides an exhaustive first-versus-systematic failure map across 18 vote and provenance-domain rules, including conditional benefits, benign-loss costs, and null provenance effects.
3. **Artifact-assurance boundary.** Study 6 maps the incorrect artifact states that survive progressively composed assurance gates and the corresponding rejection of the objectively correct baseline under benign signal loss.
4. **Residual-boundary synthesis.** Across the three studies, stronger evidence composition closes or narrows specified failure pathways without automatically making policy-visible evidence equivalent to hidden or objective truth.

The interpretation remains model bounded. Only Study 3 models contact, and logical time is not operational spacecraft time. Study 4's provenance domains are synthetic, and Study 6 is a Boolean assurance model rather than a real supply-chain experiment. The studies do not measure flight safety, mission availability, RF performance, computing cost, or operational recovery probability; Section VIII states the complete validity and aerospace interpretation limits.

Section II positions the work against prior art. Section III defines the common qualification abstraction while preserving study separation. Sections IV through VI present the three studies, Section VII synthesizes their residual boundaries, Section VIII addresses validity and future evaluation, and Section IX concludes.'''


SECTION_III_NEW = r'''## III. Common Trust-Qualification Framework and Study Separation

### A. Policy-Visible Evidence and Research-Only Truth

The studies use different mechanisms but share one analytical structure. For study `j`, let `E_j` denote the policy-visible evidence and let

`Q_j(E_j) in {0,1}`

represent the frozen qualification decision. Let `T_j in {0,1}` denote the corresponding research-only adjudication state, where `1` means that hidden authorization or objective artifact correctness supports qualification. `T_j` is used only for evaluation and is never supplied to `Q_j`.

The generic unsafe-qualification condition is

`U_j = 1[Q_j(E_j) = 1 and T_j = 0]`.

Where a study separately evaluates benign evidence loss, the complementary false-conservative condition is

`C_j = 1[Q_j(E_j) = 0 and T_j = 1]`.

These expressions are manuscript-level abstractions, not new experimental endpoints. Each study retains its frozen unit, endpoint definitions, state space, and reporting rules. Here, **residual trust boundary** means the remaining modeled states in which visible evidence satisfies qualification while research-only adjudication is false, together with any study-specific boundary at which stronger visible-evidence requirements cause false-conservative rejection. The term is descriptive of the registered finite models, not a universal impossibility theorem.

### B. Study-Specific Realizations

Table I maps the shared abstraction to the three studies without merging them.

| Study | Qualification layer | Research-only adjudication | Principal policy-visible evidence | Frozen population | Contact model |
|---|---|---|---|---:|---|
| Study 3, `S3-K4E-001` | Temporal runtime evidence | Hidden authorization truth | Signature validity, trusted source semantics, freshness, epoch/contact-dependent record availability, security signal | 1,380 trajectories | Yes, K0 and synthetic K4 |
| Study 4, `S4-MPQ-001` | Producer composition | Hidden authorization truth | Signed producer claims, total-vote threshold, synthetic provenance-domain count | 4,608 exact rule-by-subset observations | No |
| Study 6, `S6-SCTR-001` | Recovery-artifact assurance | Objective baseline correctness | Signature, independent target digest, provenance, independent reproduced build, source-review attestation, release approval | 420 exact observations | No |

In Study 3, `Q_3` evaluates received evidence under frozen signature, freshness, policy, and contact semantics while `T_3` is hidden authorization truth. The design distinguishes truthful cache-origin false qualification from false but validly signed evidence generated by a compromised trusted producer. Full timing, treatment, and policy details are given in Section IV.

In Study 4, `Q_4` applies total-vote and synthetic provenance-domain requirements to seven signed producer claims, while `T_4` is hidden authorization truth. Producer compromise and benign producer unavailability are evaluated in separate exhaustive blocks. Full producer assignments and rule definitions are given in Section V.

In Study 6, `Q_6` composes visible artifact-assurance signals while `T_6` is objective baseline correctness. Incorrect artifact states and benign assurance-signal unavailability are evaluated separately. Full state, signal, and gate definitions are given in Section VI.

Only Study 3 directly models intermittent contact. Study 4 producer unavailability and Study 6 assurance-signal unavailability are distinct constructs and are not contact loss or mission availability.

### C. Exact Finite Populations and Non-Pooling

All three studies are deterministic finite experiments rather than random samples from an operational population. Their populations remain separate because their units, interventions, and outcomes differ: Study 3 uses trajectories, Study 4 uses rule-by-subset observations, and Study 6 uses artifact-state and assurance-unavailability observations. No pooled Paper-2 `N`, success rate, confidence interval, p-value, common effect size, or global policy ranking is defined.

Section VII therefore compares mechanisms and residual boundaries qualitatively rather than estimating a common treatment effect or end-to-end recovery probability.

### D. Qualification Is Not Recovery Completion

The modeled endpoint is qualification, not completed spacecraft recovery. A permissive or qualified gate does not establish that a recovery action executed successfully, restored mission capability, or produced a safe operational state. Likewise, Study 4's availability terminology refers to false-conservative qualification under benign producer loss, and Study 6's benign availability loss refers to rejection under missing assurance signals. Neither is mission availability. Section VIII provides the full construct and external-validity boundaries.

### E. Frozen Provenance and Reproducibility

Each study is bound to a frozen design and repository execution. Independent same-repository audits reported zero mismatches for Study 3 trajectories and origin rules, Study 4 reconstructed observations and thresholds, and Study 6 frozen outputs. These controls support reproducibility of the reported finite experiments; they are not external empirical replication.

### F. Cross-Study Interpretation Rule

The common synthesis is limited to observability. Stronger evidence composition can close specific modeled failure pathways, but qualification remains constrained by what the gate can observe and by trust assumptions that remain outside that observation set. Sections IV through VI establish those boundaries separately before Section VII compares them.'''


SYNTH_NEW = r'''# VII. Cross-Study Residual Trust Boundaries

## A. Scope of the Synthesis

Studies 3, 4, and 6 were designed, executed, and frozen separately. Their populations, mechanisms, and endpoints are not pooled. The synthesis compares only how policy-visible evidence leaves different residual qualification boundaries; it is a manuscript-level interpretation, not a prospectively tested integrated architecture or fourth experiment.

## B. Three Qualification Layers

Table V summarizes the three layers and their distinct residual mechanisms.

### Table V. Cross-study residual-boundary comparison

| Layer | Study | What the gate can observe | Research-only truth outside the gate | Principal residual boundary | Effect of stronger composition in frozen model |
|---|---|---|---|---|---|
| Temporal runtime evidence | Study 3 | Signature validity, freshness, received authorization evidence, contact-dependent record availability, security signal | Hidden authorization truth | Fresh valid evidence can remain false; truthful cache can briefly lag a state change | Contact-aware restriction reduces selected K4 exposure but does not eliminate persistent V5 qualification for B0/S1 |
| Producer composition | Study 4 | Signed claims, vote threshold, synthetic provenance-domain count | Hidden authorization truth | Some compromised subsets satisfy the rule while others of the same size do not | Provenance can delay systematic unsafe qualification but can also cause earlier false-conservative rejection |
| Recovery artifact | Study 6 | Signature, digest, provenance, reproduced-build, review, approval | Objective baseline correctness | All visible assurance signals can be true for `APPROVED_BAD_SOURCE` | Additional signals close specified modeled states while increasing sensitivity to benign assurance-signal loss |

The rows do not share a common measurement scale. Table V is therefore a qualitative mechanism comparison, not a basis for combining numeric outcomes.

## C. Integrity Does Not Exhaust Semantic Trust

Study 3 separates post-signature alteration from false content produced inside the modeled trust boundary. `V4` invalidates the affected signature and the manipulated record does not qualify. `V5` remains validly signed by the trusted producer and can remain qualified even when hidden authorization truth is false.

Study 6 exposes an analogous upstream boundary. Additional digest, provenance, reproduced-build, review, and approval signals close specific modeled incorrect states, yet `APPROVED_BAD_SOURCE` remains qualified because every frozen gate-visible signal is true while objective correctness is false.

The implication is bounded: integrity, freshness, provenance, and process evidence establish only the properties represented by those signals and their trust anchors. They do not automatically reveal a semantic mismatch that the gate cannot observe.

## D. Stronger Composition Moves the Boundary

Study 4 shows that additional provenance structure can delay systematic unsafe qualification without always changing first failure. For example, `Q3_D3` leaves first unsafe failure at three compromised producers but moves systematic failure from three under `Q3_D1` to six. The same constraint makes benign false-conservative rejection possible after two unavailable producers rather than five. Other provenance additions produce no threshold change, so diversity is not monotonically beneficial in the frozen model.

Study 6 shows a different frontier. Stronger gates reduce the prespecified incorrect states that remain qualified from four under signature-only checking to one under the six-signal composite gate, while benign-loss subsets increase from 32/64 to 63/64. Equal counts can still hide different residual mechanisms, as `G3` and `G4` each leave two incorrect states but not the same two.

Study 3 is not folded into that availability frontier because it has different endpoints. Its contact-aware restriction reduces selected K4 exposure while persistent `V5` qualification remains present for `B0` and `S1`. Across all three studies, stronger composition changes a boundary condition rather than establishing universal dominance.

## E. Residual Identity Matters

Aggregate count or duration is insufficient to identify the remaining trust assumption. Study 4 distinguishes first from systematic failure because same-size producer subsets can differ in provenance composition. Study 6 preserves residual state identity because gates with equal unsafe counts can fail on different artifact states. Study 3 preserves false-qualification origin because a truthful pre-onset cache and a compromised-producer record represent different mechanisms.

This is why the manuscript reports origin, subset structure, and surviving artifact states rather than collapsing the studies into one scalar trust score.

## F. Observability as the Common Constraint

The common principle is observability. Study 3 cannot directly observe that a trusted signer is semantically lying; Study 4 cannot observe a compromise oracle beyond the signed claims and structural provenance labels supplied to the rule; Study 6 cannot observe objective correctness when every required assurance signal remains true.

Within each frozen model, changing the arrangement or quantity of visible evidence can narrow the set of qualifying failures, but it cannot discriminate a mismatch that remains observationally identical under the gate's variables. This is a model-specific systems result, not a universal impossibility theorem.

## G. Aerospace Systems Implications

The experiments suggest four design questions for aerospace information systems. First, recovery requirements should distinguish evidence integrity from authority and semantic trust. Second, multi-source evidence should document what operational failure separation a claimed provenance domain represents. Third, stronger evidence requirements should be assessed together with the benign conditions under which required evidence can become unavailable. Fourth, artifact assurance should identify the highest-level trust assumption that remains outside the gate.

These implications are not prescriptive flight requirements. Mission-specific adoption would require mapping the abstract producers, provenance domains, timing semantics, gates, and failure states to an actual architecture and validating that mapping under operational conditions.

## H. Synthesis Result

Taken together, the studies support a layered residual-trust interpretation of satellite cyber-recovery qualification. Temporal evidence, producer composition, and artifact assurance each close some modeled failure pathways while leaving a different residual assumption outside direct observation. The synthesis therefore does not identify a globally best policy, producer-composition rule, or artifact gate. Its contribution is to make the remaining trust assumption explicit at each layer without pooling the three experiments.'''


def replace_section(text: str, start: str, end: str, replacement: str, label: str) -> str:
    s = text.find(start)
    e = text.find(end, s + len(start)) if s >= 0 else -1
    if s < 0 or e < 0 or e <= s:
        raise SystemExit(f"ERROR: unable to locate section markers for {label}")
    return text[:s] + replacement.rstrip() + "\n\n" + text[e:]


def verify_common(texts: list[str]) -> None:
    combined = "\n".join(texts)
    if "—" in combined:
        raise SystemExit("ERROR: em dash introduced by compression pass")
    if "6,408" in combined:
        raise SystemExit("ERROR: combined Paper-2 population total introduced")
    if re.search(r"\[\d+\]\s*-\s*\[\d+\]", combined):
        raise SystemExit("ERROR: dash-form numeric citation range introduced")

    required = [
        "**RQ1:**", "**RQ2:**", "**RQ3:**",
        "1,380", "4,608", "420",
        "Only Study 3 directly models intermittent contact",
        "No pooled Paper-2 `N`",
        "not a prospectively tested integrated architecture",
        "PRE_ONSET_CACHE",
        "V5",
        "Q3_D3",
        "G3", "G4", "APPROVED_BAD_SOURCE",
        "globally best policy",
    ]
    for marker in required:
        if marker not in combined:
            raise SystemExit(f"ERROR: required preservation marker missing: {marker}")

    intro = texts[0]
    first_use = []
    for match in re.finditer(r"\[(\d+)\]", intro):
        n = int(match.group(1))
        if n not in first_use:
            first_use.append(n)
    if first_use != list(range(1, 14)):
        raise SystemExit(
            f"ERROR: Introduction citation first-use order changed: {first_use}"
        )


def main() -> None:
    intro_old = read(INTRO)
    core_old = read(CORE)
    synth_old = read(SYNTH)

    # Refuse unexpected baselines rather than silently editing a drifted manuscript.
    baseline_markers = [
        (intro_old, "Several results constrain stronger interpretations and are intentionally retained."),
        (core_old, "#### 1) Study 3: temporal evidence qualification"),
        (core_old, "### F. Cross-Study Interpretation Rule"),
        (synth_old, "## C. Integrity and Authenticity Do Not Exhaust Semantic Trust"),
        (synth_old, "## G. Aerospace Systems Implications"),
    ]
    for text, marker in baseline_markers:
        if marker not in text:
            raise SystemExit(f"ERROR: expected compression baseline marker missing: {marker}")

    intro_new = INTRO_NEW
    core_new = replace_section(
        core_old,
        "## III. Common Trust-Qualification Framework and Study Separation",
        "## References Used in Sections II and III",
        SECTION_III_NEW,
        "Section III",
    )
    synth_new = SYNTH_NEW

    verify_common([intro_new, core_new, synth_new])

    before = {
        "I": words(intro_old),
        "III": words(core_old[core_old.find("## III."):core_old.find("## References Used in Sections II and III")]),
        "VII": words(synth_old),
    }
    after = {
        "I": words(intro_new),
        "III": words(SECTION_III_NEW),
        "VII": words(synth_new),
    }

    total_reduction = sum(before.values()) - sum(after.values())
    if total_reduction < 1200:
        raise SystemExit(f"ERROR: compression reduction too small: {total_reduction} words")
    if total_reduction > 2200:
        raise SystemExit(f"ERROR: compression reduction exceeds conservative pass bound: {total_reduction} words")

    write(INTRO, intro_new)
    write(CORE, core_new)
    write(SYNTH, synth_new)

    print("TAES_COMPRESSION_PASS1=PASS")
    print(f"section_I_before={before['I']}")
    print(f"section_I_after={after['I']}")
    print(f"section_III_before={before['III']}")
    print(f"section_III_after={after['III']}")
    print(f"section_VII_before={before['VII']}")
    print(f"section_VII_after={after['VII']}")
    print(f"targeted_word_reduction={total_reduction}")
    print("science_files_changed=NONE")
    print("section_VIII_changed=NO")
    print("NOTE: Re-run TAES_ASSEMBLE_MANUSCRIPT.py and TAES_AUDIT_LENGTH_REDUNDANCY.py before committing.")


if __name__ == "__main__":
    main()
