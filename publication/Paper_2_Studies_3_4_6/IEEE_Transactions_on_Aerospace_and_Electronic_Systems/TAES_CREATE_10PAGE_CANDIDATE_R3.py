#!/usr/bin/env python3
"""Create balanced TAES Paper-2 short candidate R3.

R3 preserves every restored prose block from failed R2 and changes only the
Study-3 insertion anchor. R2 incorrectly required the existing sentence
`Expanded endpoints and timing details appear in Supplementary Appendix A.` to
start after a blank-line paragraph boundary. In the deterministic R1 candidate
it is the final sentence of the preceding paragraph.

R3 anchors on that exact sentence text, inserts the R2 Study-3 restoration as a
new paragraph before it, and preserves all frozen R9/R1 bindings. It does not
rerun Studies 3, 4, or 6 and does not modify publisher-facing files.
"""

from __future__ import annotations

import re
from pathlib import Path

import TAES_CREATE_10PAGE_CANDIDATE as r1
import TAES_CREATE_10PAGE_CANDIDATE_R2 as r2

ROOT = Path(__file__).resolve().parent
OUT_MAIN = ROOT / "TAES_10P_R3_MANUSCRIPT_DRAFT.md"
OUT_SUPP = ROOT / "TAES_10P_R3_SUPPLEMENTARY_MATERIAL.md"
OUT_README = ROOT / "TAES_10P_R3_SUPPLEMENTARY_README.txt"
OUT_AUDIT = ROOT / "TAES_10P_R3_CANDIDATE_AUDIT.txt"

EXPECTED_R1_MAIN = r2.EXPECTED_R1_MAIN
EXPECTED_R1_SUPP = r2.EXPECTED_R1_SUPP
EXPECTED_R1_README = r2.EXPECTED_R1_README


def sha256(path: Path) -> str:
    return r2.sha256(path)


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text))


def insert_before_sentence(text: str, marker: str, addition: str, label: str) -> str:
    count = text.count(marker)
    if count != 1:
        raise SystemExit(
            f"ERROR: R3 sentence insertion marker for {label} expected one hit; found {count}"
        )
    replacement = "\n\n" + addition.strip() + "\n\n" + marker
    return text.replace(marker, replacement, 1)


def main() -> None:
    # Recreate the deterministic R1 files and bind their exact identities.
    r1.main()
    if sha256(r1.OUT_MAIN) != EXPECTED_R1_MAIN:
        raise SystemExit("ERROR: R1 short-main hash mismatch")
    if sha256(r1.OUT_SUPP) != EXPECTED_R1_SUPP:
        raise SystemExit("ERROR: R1 supplement hash mismatch")
    if sha256(r1.OUT_README) != EXPECTED_R1_README:
        raise SystemExit("ERROR: R1 supplementary README hash mismatch")

    main_text = r1.OUT_MAIN.read_text(encoding="utf-8")

    # Seven R2 anchors were valid and are preserved unchanged.
    main_text = r2.insert_before(
        main_text,
        "\n\nOnly Study 3 models contact",
        r2.RESTORE_I,
        "Introduction research questions and contributions",
    )
    main_text = r2.insert_before(
        main_text,
        "\n\n## III. Common Trust-Qualification Framework and Study Separation",
        r2.RESTORE_II,
        "Related-work differentiation",
    )
    main_text = r2.insert_before(
        main_text,
        "\n\n## IV. Temporal Evidence Qualification Under Intermittent Contact",
        r2.RESTORE_III,
        "Common-framework construct detail",
    )

    # R3 correction: the supplementary-reference sentence is present inside the
    # existing Study-3 paragraph, not after a blank line. Anchor on the sentence
    # itself and create the paragraph boundaries explicitly.
    main_text = insert_before_sentence(
        main_text,
        "Expanded endpoints and timing details appear in Supplementary Appendix A.",
        r2.RESTORE_IV,
        "Study-3 endpoint and temporal interpretation",
    )

    main_text = r2.insert_before(
        main_text,
        "\n\nStudy 4 is a qualification model, not Byzantine consensus or distributed agreement",
        r2.RESTORE_V,
        "Study-4 selected threshold interpretation",
    )
    main_text = r2.insert_before(
        main_text,
        "\n\n**Table III. Study-6 residual incorrect states and benign assurance loss**",
        r2.RESTORE_VI,
        "Study-6 state and gate detail",
    )
    main_text = r2.insert_before(
        main_text,
        "\n\nFor aerospace information systems, the practical questions are limited:",
        r2.RESTORE_VII,
        "Cross-study observability interpretation",
    )
    main_text = r2.insert_before(
        main_text,
        "\n\nFuture work can prospectively evaluate orbital-contact schedules",
        r2.RESTORE_VIII,
        "Expanded external-validity and reproducibility detail",
    )

    if "—" in main_text:
        raise SystemExit("ERROR: em dash detected in R3 main article")
    if "6,408" in main_text:
        raise SystemExit("ERROR: pooled Paper-2 population detected in R3")

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
        "Expanded endpoints and timing details appear in Supplementary Appendix A.",
    ]
    for marker in required:
        if marker not in main_text:
            raise SystemExit(f"ERROR: protected R3 marker missing: {marker}")

    order = r1.first_use(main_text)
    if order != list(range(1, 14)):
        raise SystemExit(f"ERROR: citation first-use order is {order}, expected 1..13")

    main_words = word_count(main_text)
    if not 5400 <= main_words <= 5900:
        raise SystemExit(
            f"ERROR: R3 balanced-main word count outside controlled range: {main_words}"
        )

    OUT_MAIN.write_text(main_text, encoding="utf-8")
    OUT_SUPP.write_bytes(r1.OUT_SUPP.read_bytes())
    OUT_README.write_bytes(r1.OUT_README.read_bytes())

    if sha256(OUT_SUPP) != EXPECTED_R1_SUPP:
        raise SystemExit("ERROR: R3 supplement drifted from R1 supplement")
    if sha256(OUT_README) != EXPECTED_R1_README:
        raise SystemExit("ERROR: R3 README drifted from R1 README")

    abstract_doc = r1.read(r1.ABSTRACT_DOC)
    abstract = r1.extract_between(abstract_doc, "## Abstract\n", "\n## Index Terms")

    audit = "\n".join([
        "TAES_10PAGE_BALANCED_CANDIDATE_R3=PASS_LOCAL_UNTRACKED_ONLY",
        f"r1_short_main_sha256={EXPECTED_R1_MAIN}",
        f"r3_main_words_including_references={main_words}",
        f"r3_main_sha256={sha256(OUT_MAIN)}",
        f"supplement_sha256={sha256(OUT_SUPP)}",
        f"readme_sha256={sha256(OUT_README)}",
        f"abstract_words={word_count(abstract)}",
        f"citation_first_use_order={','.join(str(n) for n in order)}",
        "r3_change_from_failed_r2=STUDY3_INSERTION_ANCHOR_ONLY",
        "restored_prose_changed_from_r2=NO",
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
