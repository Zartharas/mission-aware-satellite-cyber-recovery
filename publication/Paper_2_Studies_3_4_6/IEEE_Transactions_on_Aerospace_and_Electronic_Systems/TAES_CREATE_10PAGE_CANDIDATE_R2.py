#!/usr/bin/env python3
"""Create a balanced short-form TAES Paper-2 candidate from the six-page R1 draft.

R2 restores reviewer-useful explanatory detail after R1 rendered to only six
IEEEtran pages. It preserves the frozen R9 manuscript/PDF, does not rerun any
study, and keeps the R1 supplementary material byte-identical under versioned
R2 output names.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

import TAES_CREATE_10PAGE_CANDIDATE as r1

ROOT = Path(__file__).resolve().parent
OUT_MAIN = ROOT / "TAES_10P_R2_MANUSCRIPT_DRAFT.md"
OUT_SUPP = ROOT / "TAES_10P_R2_SUPPLEMENTARY_MATERIAL.md"
OUT_README = ROOT / "TAES_10P_R2_SUPPLEMENTARY_README.txt"
OUT_AUDIT = ROOT / "TAES_10P_R2_CANDIDATE_AUDIT.txt"

EXPECTED_R1_MAIN = "5926d116acc877859545bd5e0e2829132894de5298d7ff3e3cd6123b4665cbd1"
EXPECTED_R1_SUPP = "e6313fca178f9de40a6b7c28468be6b20ae1fc7249c2e3c8e30ca5fbf0d7027c"
EXPECTED_R1_README = "b7603d36ba2b9297b970dcad0138fbb9faadae4d8be946e4f05ebb6bdb6609c5"

RESTORE_I = r'''The study questions remain separate. RQ1 asks how truthful evidence, invalid post-signature modification, and false but validly signed producer claims change false-qualification duration and recurrence across the frozen Study-3 contact and policy grid. RQ2 asks how absolute vote thresholds and synthetic provenance-domain requirements change first and systematic unsafe-qualification boundaries while separately changing false-conservative rejection under benign producer loss. RQ3 asks which prespecified incorrect artifacts remain qualified as Study-6 assurance requirements are composed and what benign qualification loss follows when required signals are unavailable. The systems-level synthesis then asks only how the residual trust assumption differs across those three independently measured layers.

Four bounded contributions follow from that structure. Study 3 separates ordinary freshness lag from producer-origin semantic falsity rather than collapsing both into one exposure count. Study 4 reports both first and systematic failure, preserving subset dependence and null provenance effects. Study 6 preserves the identity of surviving incorrect artifact states instead of reporting only aggregate counts. Finally, the synthesis makes the remaining trust assumption explicit at each layer without claiming that the three mechanisms were jointly tested or that one policy, quorum, or artifact gate is globally best.'''

RESTORE_II = r'''The distinction from prior work is mechanism-specific. RFC 9334 supplies a mature separation between evidence, appraisal, and relying-party decisions, and its freshness treatment motivates the difference between a record that is still policy-fresh and a hidden state that has already changed. It does not characterize how long the registered Study-3 policies remain falsely qualified across this particular onset, contact, persistence, and producer-semantics grid. Likewise, multi-Verifier RATS topologies coordinate appraisal across Verifiers, whereas Study 4 keeps appraisal centralized and varies the claims presented by modeled evidence producers.

Quorum theory establishes that threshold and failure-set structure matter, and Space Fabric shows that endorsement quorums can appear in a satellite trust architecture. Study 4 is narrower than consensus theory or a new quorum protocol: every subset of a fixed seven-producer population is enumerated so that first and systematic qualification failure can be distinguished for each registered vote/provenance rule. That distinction matters because a provenance requirement can leave first failure unchanged while changing the affected-producer count at which every same-size subset fails.

For artifact assurance, in-toto, TUF, and SLSA already establish provenance, signed update metadata, target binding, trusted roles, and source/build assurance concepts. Study 6 therefore does not present those controls as new. It treats selected assurance properties as visible Boolean signals and makes the residual incorrect-state set, rather than the existence of provenance or reproducible builds, the measured object.'''

RESTORE_III = r'''The realizations preserve important construct differences. In Study 3, the gate evaluates received records under signature, freshness, security-signal, policy, and contact semantics while hidden authorization truth remains research-only. In Study 4, the gate sees signed claims, a vote requirement, and a synthetic domain-count requirement; compromise status is used only to adjudicate the exhaustive safety block. In Study 6, the gate sees artifact-assurance signals while objective baseline correctness remains research-only. Producer unavailability in Study 4 and assurance-signal unavailability in Study 6 are therefore not alternate forms of spacecraft contact loss.

Unsafe qualification and false-conservative qualification also have bounded meanings. The former identifies a policy-qualified state when the corresponding hidden or objective adjudication is false. The latter identifies rejection in the separately defined benign-loss blocks even though hidden authorization or objective correctness supports qualification. Neither indicates that a recovery command executed, restored service, produced a physically safe state, or changed mission availability.

Because each study enumerates a registered finite population, exact counts and thresholds describe those grids without a sampling-based p-value gate. Exactness does not remove uncertainty about model choice or external validity, and the three units remain incommensurate. Their arithmetic sum has no scientific interpretation.'''

RESTORE_IV = r'''The frozen primary endpoint set includes unsafe-permissive epoch rate, unsafe-qualified epoch rate, unsafe-qualified exposure, unsafe-qualified episode count, protective epoch rate, and action-transition count. The article emphasizes unsafe qualification because it directly compares the policy-visible gate with hidden authorization. Unsafe permissiveness is only a selector or gate-entry action metric and must not be read as completed recovery.

K4 mechanically constrains when new records can be received under the registered cache and freshness semantics. Its lower mean V5 exposure relative to K0 therefore does not establish that intermittent connectivity improves security. Likewise, the V4 result shows only that the affected post-signature-modified record fails the registered signature check. It does not test cryptanalysis, key extraction, signing-service compromise, or operational spacecraft key management.

The onset grid is complete for the registered design, so the phase summaries are exact finite-grid results rather than estimates from a sampled operational distribution. One-shot `V5/K0` yields five logical seconds of mean V5 exposure for both `B0` and `S1` across all 46 phases. Under K4, `S1` retains five logical seconds while `B0` can also include the separately identified truthful cache boundary. One-shot and persistent V5 are cryptographically the same false-but-valid producer claim; persistence changes whether the false claim is renewed after later contact.'''

RESTORE_V = r'''The Q4 cells provide a compact reference for the two-sided tradeoff. `Q4_D1` is symmetric at 4/4 in the safety and benign-loss blocks, while `Q4_D3` preserves first unsafe failure at four, delays systematic unsafe failure to six, moves first benign failure to two, and leaves systematic benign failure at four. The domain constraint therefore changes which same-size subsets qualify even when the total-vote threshold is unchanged.

At higher vote thresholds, compromise resistance increases while benign-loss tolerance tightens. `Q5_D1`, `Q6`, and `Q7` require five, six, and seven compromised producers, respectively, but become false-conservative after three, two, and one unavailable producers. Without a probability model, mission-specific costs, or utility weights, those pairs cannot be collapsed into a preferred operating point.

The 128 subsets in each block form the complete power set of the seven registered producers. They are model states rather than random samples. A threshold such as 3/6 or 2/5 therefore reports a finite first/systematic boundary under the registered 3/2/2 allocation, not the probability of compromise, producer loss, or mission outage.

The model also stops well short of Byzantine consensus or distributed agreement. Producers do not elect leaders, maintain replicated state, resolve forks, run broadcast or agreement protocols, or model liveness under network partitions. Quorum and asymmetric-trust literature therefore provide structural prior art rather than an algorithm that Study 4 claims to improve. The measured object is the qualification threshold map under the fixed producer set and domain labels.'''

RESTORE_VI = r'''The five incorrect states encode different places where trust can fail. `POST_RELEASE_TAMPER` has invalid signature, digest, provenance, and reproduced-build signals. `TRUSTED_SIGNER_COMPROMISE` retains a valid signature while digest, provenance, and reproduced-build checks fail. `TRUSTED_BUILDER_COMPROMISE` retains signature, digest, provenance, review, and approval but fails reproduced-build match. `SOURCE_REVIEW_BYPASS` retains the other visible signals while source-review attestation is false. `APPROVED_BAD_SOURCE` is intentionally stronger: all six visible signals are true while objective correctness is false.

The gates expose different subsets of those signals. `G0` requires signature only; `G1` adds target-digest match; `G2` substitutes provenance for the digest requirement; `G3` requires signature, provenance, and reproduced-build match; `G4` requires signature, provenance, and source-review attestation; and `G5` requires all six visible signals. Thus equal aggregate counts can conceal different mechanisms: `G3` removes the modeled builder-compromise pathway but leaves `SOURCE_REVIEW_BYPASS`, whereas `G4` removes the review-bypass pathway but leaves `TRUSTED_BUILDER_COMPROMISE`.

For every gate, loss of one signal that the gate requires is sufficient to produce benign rejection in at least one unavailable-signal subset. The reported 32/64 through 63/64 progression is therefore a structural count over the complete subset space, not an operational outage frequency.

The assurance dimensions are intentionally related to established supply-chain mechanisms without claiming to implement them. in-toto motivates verifiable step metadata, TUF motivates authenticated target and role metadata, and SLSA motivates source/build assurance and explicit producer-trust boundaries. The Boolean gates neither replace nor validate those systems, and no compliance assessment was performed. The experiment asks only what the registered gate can distinguish when those broad assurance concepts are represented as visible signals.'''

RESTORE_VII = r'''Observability is the common constraint. Study 3 cannot directly observe that a trusted producer is semantically lying when the false claim remains fresh and correctly signed. Study 4 can apply vote and synthetic-domain structure to the claims it receives but does not observe an external compromise oracle. Study 6 cannot reject objective incorrectness when every signal required by the gate remains true. Changing the quantity or arrangement of visible evidence can narrow a residual set, but it cannot distinguish a mismatch that remains identical under the registered variables.

This interpretation is descriptive rather than prescriptive. A mission-specific recovery design would still need to map the abstract producers, provenance domains, timing semantics, assurance signals, and failure states to concrete components and then justify what real failure separation or trust property each variable represents.'''

RESTORE_VIII = r'''External validity remains the principal uncertainty. Study 3's 46 onset phases exhaust the registered grid but are not random draws from an orbital or operational distribution, and its 67,620 epoch states are repeated states within 1,380 trajectories rather than independent statistical units. Study 4 fixes seven producers, a 3/2/2 domain allocation, a registered-producer denominator, and separate compromise and benign-loss blocks; dynamic membership, weighted voting, different allocations, or joint compromise and loss could move the thresholds. Study 6 uses six prespecified artifact states and six Boolean gates rather than an exhaustive taxonomy of supply-chain failure.

The model vocabulary must also stay bounded. Study-4 provenance labels do not demonstrate independence of organizations, hardware roots, networks, software stacks, administrators, sensing paths, or suppliers. Study-6 signals named independent digest or independent reproduced build similarly do not prove real independence, while review and approval booleans do not measure process competence or adversarial resistance. References to RATS, SPARTA, SLSA, TUF, and in-toto position the abstractions against established concepts; no standards-compliance assessment was performed.

Reproducibility controls are repository-bound. Each frozen experiment has an independent same-repository reconstruction or audit with zero mismatches, supporting confidence that the manuscript projections match the registered outputs. They are not external empirical replication because the implementations, records, and audits remain within the same research program. External validation would require an independent group, environment, operational evidence source, or prospectively designed integrated experiment.

A future integrated experiment would be scientifically different from the present paper. It would need prospectively registered joint interventions, units, timing semantics, and endpoints connecting runtime evidence, producer composition, and artifact assurance in one architecture. Such a design could also introduce mission-specific contact schedules, empirically justified failure domains, production build services, hardware/software-in-the-loop timing, and joint compromise-plus-unavailability conditions. Those extensions should be frozen as new experiments rather than inferred by pooling or retrofitting the current three populations.'''


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text))


def insert_before(text: str, marker: str, addition: str, label: str) -> str:
    count = text.count(marker)
    if count != 1:
        raise SystemExit(f"ERROR: R2 insertion marker for {label} expected one hit; found {count}")
    return text.replace(marker, "\n\n" + addition.strip() + marker, 1)


def main() -> None:
    # Recreate the deterministic six-page R1 files first, then verify their exact
    # hashes before adding any restored text.
    r1.main()
    if sha256(r1.OUT_MAIN) != EXPECTED_R1_MAIN:
        raise SystemExit("ERROR: R1 short-main hash mismatch")
    if sha256(r1.OUT_SUPP) != EXPECTED_R1_SUPP:
        raise SystemExit("ERROR: R1 supplement hash mismatch")
    if sha256(r1.OUT_README) != EXPECTED_R1_README:
        raise SystemExit("ERROR: R1 supplementary README hash mismatch")

    main_text = r1.OUT_MAIN.read_text(encoding="utf-8")

    main_text = insert_before(
        main_text,
        "\n\nOnly Study 3 models contact",
        RESTORE_I,
        "Introduction research questions and contributions",
    )
    main_text = insert_before(
        main_text,
        "\n\n## III. Common Trust-Qualification Framework and Study Separation",
        RESTORE_II,
        "Related-work differentiation",
    )
    main_text = insert_before(
        main_text,
        "\n\n## IV. Temporal Evidence Qualification Under Intermittent Contact",
        RESTORE_III,
        "Common-framework construct detail",
    )
    main_text = insert_before(
        main_text,
        "\n\nExpanded endpoints and timing details appear in Supplementary Appendix A.",
        RESTORE_IV,
        "Study-3 endpoint and temporal interpretation",
    )
    main_text = insert_before(
        main_text,
        "\n\nStudy 4 is a qualification model, not Byzantine consensus or distributed agreement",
        RESTORE_V,
        "Study-4 selected threshold interpretation",
    )
    main_text = insert_before(
        main_text,
        "\n\n**Table III. Study-6 residual incorrect states and benign assurance loss**",
        RESTORE_VI,
        "Study-6 state and gate detail",
    )
    main_text = insert_before(
        main_text,
        "\n\nFor aerospace information systems, the practical questions are limited:",
        RESTORE_VII,
        "Cross-study observability interpretation",
    )
    main_text = insert_before(
        main_text,
        "\n\nFuture work can prospectively evaluate orbital-contact schedules",
        RESTORE_VIII,
        "Expanded external-validity and reproducibility detail",
    )

    if "—" in main_text:
        raise SystemExit("ERROR: em dash detected in R2 main article")
    if "6,408" in main_text:
        raise SystemExit("ERROR: pooled Paper-2 population detected in R2")

    required = [
        "RQ1 asks how truthful evidence",
        "PRE_ONSET_CACHE",
        "One-shot `V5/K0` yields five logical seconds",
        "`Q4_D3` preserves first unsafe failure at four",
        "Producers do not elect leaders",
        "`APPROVED_BAD_SOURCE` is intentionally stronger",
        "Observability is the common constraint",
        "not external empirical replication",
        "Only Study 3 models contact",
        "OpenAI ChatGPT (GPT-5.6 Sol)",
    ]
    for marker in required:
        if marker not in main_text:
            raise SystemExit(f"ERROR: protected R2 marker missing: {marker}")

    order = r1.first_use(main_text)
    if order != list(range(1, 14)):
        raise SystemExit(f"ERROR: citation first-use order is {order}, expected 1..13")

    main_words = word_count(main_text)
    if not 5400 <= main_words <= 5900:
        raise SystemExit(
            f"ERROR: R2 balanced-main word count outside controlled range: {main_words}"
        )

    OUT_MAIN.write_text(main_text, encoding="utf-8")
    OUT_SUPP.write_bytes(r1.OUT_SUPP.read_bytes())
    OUT_README.write_bytes(r1.OUT_README.read_bytes())

    if sha256(OUT_SUPP) != EXPECTED_R1_SUPP:
        raise SystemExit("ERROR: R2 supplement drifted from R1 supplement")
    if sha256(OUT_README) != EXPECTED_R1_README:
        raise SystemExit("ERROR: R2 README drifted from R1 README")

    audit = "\n".join([
        "TAES_10PAGE_BALANCED_CANDIDATE_R2=PASS_LOCAL_UNTRACKED_ONLY",
        f"r1_short_main_sha256={EXPECTED_R1_MAIN}",
        f"r2_main_words_including_references={main_words}",
        f"r2_main_sha256={sha256(OUT_MAIN)}",
        f"supplement_sha256={sha256(OUT_SUPP)}",
        f"readme_sha256={sha256(OUT_README)}",
        f"abstract_words={word_count(r1.extract_between(r1.read(r1.ABSTRACT_DOC), '## Abstract\\n', '\\n## Index Terms'))}",
        f"citation_first_use_order={','.join(str(n) for n in order)}",
        "restoration_goal=REVIEWER_USEFUL_DETAIL_NOT_PAGE_FILLER",
        "target_ieeetran_pages=8_TO_9_PREFERRED__10_MAXIMUM",
        "figure1_main_article=RETIRED_MOVED_TO_SUPPLEMENT",
        "study4_complete_18_rule_map=SUPPLEMENT_APPENDIX_B",
        "supplement_content_changed_from_r1=NO",
        "science_files_changed=NONE",
        "study_rerun=NO",
        "publisher_facing=NO",
        "merge_to_main=NOT_AUTHORIZED_UNTIL_QA_PASS",
    ]) + "\n"
    OUT_AUDIT.write_text(audit, encoding="utf-8")
    print(audit, end="")


if __name__ == "__main__":
    main()
