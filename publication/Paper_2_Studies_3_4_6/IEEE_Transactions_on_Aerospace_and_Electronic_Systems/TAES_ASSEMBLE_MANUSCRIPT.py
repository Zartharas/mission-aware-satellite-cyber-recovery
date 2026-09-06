#!/usr/bin/env python3
"""Assemble the controlled TAES Paper-2 manuscript components in place.

This script does not fetch data, rerun studies, or alter frozen science. It only
combines already tracked manuscript-development components in the canonical
TAES publication directory, binds the controlled IEEE AI-use acknowledgment,
and binds approved figure assets into the component manifest.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "TAES_MANUSCRIPT_FULL_DRAFT.md"
MANIFEST = ROOT / "TAES_MANUSCRIPT_COMPONENT_SHA256.txt"

TITLE = (
    "Residual Trust Boundaries in Satellite Cyber Recovery: "
    "Temporal Evidence, Producer Composition, and Artifact Assurance"
)

COMPONENTS = [
    "TAES_ABSTRACT_KEYWORDS.md",
    "TAES_SECTION_I_INTRODUCTION.md",
    "TAES_MANUSCRIPT_SOURCE.md",
    "TAES_SECTION_IV_STUDY3.md",
    "TAES_SECTION_V_STUDY4.md",
    "TAES_SECTION_VI_STUDY6.md",
    "TAES_SECTION_VII_SYNTHESIS.md",
    "TAES_SECTION_VIII_VALIDITY.md",
    "TAES_SECTION_IX_CONCLUSION.md",
    "TAES_ACKNOWLEDGMENT_AI_DISCLOSURE.md",
]

FIGURE_FILES = [
    "TAES_FIGURE1_RESIDUAL_BOUNDARIES.pdf",
    "TAES_FIGURE1_RESIDUAL_BOUNDARIES.png",
]

SECTION_FILES = [
    "TAES_SECTION_I_INTRODUCTION.md",
    "TAES_SECTION_IV_STUDY3.md",
    "TAES_SECTION_V_STUDY4.md",
    "TAES_SECTION_VI_STUDY6.md",
    "TAES_SECTION_VII_SYNTHESIS.md",
    "TAES_SECTION_VIII_VALIDITY.md",
    "TAES_SECTION_IX_CONCLUSION.md",
]


def read(name: str) -> str:
    path = ROOT / name
    if not path.is_file():
        raise SystemExit(f"ERROR: missing manuscript component: {path}")
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def extract_section(text: str, heading: str, next_heading: str) -> str:
    """Extract Markdown section body using headings, not fragile note text."""
    start_marker = heading + "\n"
    next_marker = "\n" + next_heading
    start = text.find(start_marker)
    if start < 0:
        raise SystemExit(f"ERROR: manuscript heading missing: {heading}")
    start += len(start_marker)
    end = text.find(next_marker, start)
    if end < 0:
        raise SystemExit(f"ERROR: next manuscript heading missing: {next_heading}")
    return text[start:end].strip()


def normalize_section(text: str) -> str:
    """Normalize standalone section files under one top-level manuscript title."""
    lines = text.strip().splitlines()
    out: list[str] = []
    for line in lines:
        if re.match(r"^# (?:I|IV|V|VI|VII|VIII|IX)\.", line):
            out.append("#" + line)
        elif re.match(r"^## [A-Z]\.", line):
            out.append("#" + line)
        elif re.match(r"^### Table [IVX]+\.", line):
            out.append(f"**{line[4:]}**")
        else:
            out.append(line)
    return "\n".join(out).strip()


def acknowledgment_body() -> str:
    """Return the publisher-facing AI-use disclosure without its control note."""
    ack_doc = read("TAES_ACKNOWLEDGMENT_AI_DISCLOSURE.md")
    lines: list[str] = []
    for line in ack_doc.splitlines():
        stripped = line.strip()
        if stripped == "# Acknowledgment":
            continue
        if stripped.startswith("> Control note:"):
            continue
        lines.append(line)
    body = "\n".join(lines).strip()
    if not body:
        raise SystemExit("ERROR: AI-use acknowledgment body is empty")
    return body


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def citation_first_use_order(text: str) -> list[int]:
    """Return reference numbers in the order each is first cited before References."""
    body = text.split("\n## References", 1)[0]
    seen: list[int] = []
    token = re.compile(r"\[(\d+)\](?:-\[(\d+)\])?")
    for match in token.finditer(body):
        first = int(match.group(1))
        last = int(match.group(2)) if match.group(2) else first
        if last < first:
            raise SystemExit(
                f"ERROR: descending citation range detected: [{first}]-[{last}]"
            )
        for number in range(first, last + 1):
            if number not in seen:
                seen.append(number)
    return seen


def main() -> None:
    for name in COMPONENTS:
        read(name)

    for name in FIGURE_FILES:
        path = ROOT / name
        if not path.is_file():
            raise SystemExit(f"ERROR: missing approved figure asset: {path}")

    abstract_doc = read("TAES_ABSTRACT_KEYWORDS.md")
    abstract_block = extract_section(abstract_doc, "## Abstract", "## Index Terms")

    # Audit metadata may appear under the abstract during development. Exclude
    # it from the publisher-facing abstract without depending on its exact wording.
    abstract_lines = []
    for line in abstract_block.splitlines():
        if re.match(r"^\*\*.*word count.*\*\*", line.strip(), flags=re.IGNORECASE):
            continue
        abstract_lines.append(line)
    abstract = "\n".join(abstract_lines).strip()

    index_terms = extract_section(
        abstract_doc, "## Index Terms", "## Abstract claim controls"
    ).strip()

    abstract_words = re.findall(r"\b[\w'-]+\b", abstract)
    if not 150 <= len(abstract_words) <= 250:
        raise SystemExit(
            f"ERROR: abstract word count {len(abstract_words)} is outside IEEE 150-250 range"
        )

    section_i = normalize_section(read("TAES_SECTION_I_INTRODUCTION.md"))

    core = read("TAES_MANUSCRIPT_SOURCE.md")
    section_ii_start = core.find("## II. Related Work and Scientific Positioning")
    refs_start = core.find("## References Used in Sections II and III")
    if section_ii_start < 0 or refs_start < 0 or refs_start <= section_ii_start:
        raise SystemExit("ERROR: unable to identify Sections II-III and references in core source")
    sections_ii_iii = core[section_ii_start:refs_start].strip()
    references = core[refs_start:].strip().replace(
        "## References Used in Sections II and III", "## References", 1
    )

    later_sections = [normalize_section(read(name)) for name in SECTION_FILES[1:]]
    acknowledgment = acknowledgment_body()

    assembled_parts = [
        f"# {TITLE}",
        "## Abstract\n\n" + abstract,
        "**Index Terms:** " + index_terms,
        section_i,
        sections_ii_iii,
        *later_sections,
        "## Acknowledgment\n\n" + acknowledgment,
        references,
    ]

    assembled = "\n\n".join(part.strip() for part in assembled_parts if part.strip()) + "\n"

    if "—" in assembled:
        raise SystemExit("ERROR: em dash detected in assembled manuscript")

    # The three frozen populations must never be collapsed into a Paper-2 total.
    if "6,408" in assembled:
        raise SystemExit("ERROR: combined Paper-2 population total detected")

    # Current IEEE reference style writes numeric citation ranges out individually.
    if re.search(r"\[\d+\]\s*-\s*\[\d+\]", assembled):
        raise SystemExit("ERROR: dash-form numeric IEEE citation range detected")

    # Figure 1 is the approved qualitative replacement for the retired Table V.
    required_figure_markers = [
        "![Figure 1](TAES_FIGURE1_RESIDUAL_BOUNDARIES.png)",
        "**Fig. 1.** Parallel residual trust boundaries across the three separately frozen studies.",
        "Only Study 3 models contact.",
    ]
    for marker in required_figure_markers:
        if marker not in assembled:
            raise SystemExit(f"ERROR: required Figure 1 marker missing: {marker}")

    retired_table_v_markers = [
        "### Table V. Cross-study residual-boundary comparison",
        "**Table V. Cross-study residual-boundary comparison**",
        "| Layer | Study | What the gate can observe |",
    ]
    for marker in retired_table_v_markers:
        if marker in assembled:
            raise SystemExit(f"ERROR: retired qualitative Table V detected: {marker}")

    # Bind the required IEEE AI-generated-content disclosure and keep the
    # development-only control note out of the assembled manuscript.
    required_ai_markers = [
        "## Acknowledgment",
        "OpenAI ChatGPT (GPT-5.6 Sol)",
        "Abstract and Sections I-IX",
        "substantive drafting and editorial level",
        "It was not used to generate or modify the frozen experimental results.",
        "assumes responsibility for the final manuscript",
    ]
    for marker in required_ai_markers:
        if marker not in assembled:
            raise SystemExit(f"ERROR: required IEEE AI-disclosure marker missing: {marker}")
    if "Control note:" in assembled:
        raise SystemExit("ERROR: development-only AI-disclosure control note leaked into manuscript")

    # Guard only genuinely affirmative superiority claims. Explicit limitation
    # language such as "does not identify a globally best policy" is valid.
    affirmative_superiority_patterns = [
        r"\b(?:is|was|remains|represents|identifies|establishes)\s+(?:the\s+)?globally best\s+(?:policy|gate|quorum|rule)\b",
        r"\bwe\s+(?:identify|establish|show|demonstrate)\s+(?:a|the)\s+globally best\s+(?:policy|gate|quorum|rule)\b",
    ]
    for pattern in affirmative_superiority_patterns:
        if re.search(pattern, assembled, flags=re.IGNORECASE):
            raise SystemExit(
                "ERROR: affirmative global-superiority claim detected in assembled manuscript"
            )

    required_markers = [
        "## I. Introduction",
        "## II. Related Work and Scientific Positioning",
        "## III. Common Trust-Qualification Framework and Study Separation",
        "## IV. Temporal Evidence Qualification Under Intermittent Contact",
        "## V. Multi-Producer Qualification and Provenance-Domain Constraints",
        "## VI. Recovery-Artifact Assurance and Residual Incorrect States",
        "## VII. Cross-Study Residual Trust Boundaries",
        "## VIII. Validity, Aerospace Interpretation Boundaries, and Future Evaluation",
        "## IX. Conclusion",
        "## Acknowledgment",
        "## References",
    ]
    for marker in required_markers:
        if marker not in assembled:
            raise SystemExit(f"ERROR: required assembled section missing: {marker}")

    first_use = citation_first_use_order(assembled)
    if first_use:
        expected = list(range(1, max(first_use) + 1))
        if first_use != expected:
            raise SystemExit(
                "ERROR: IEEE reference numbers are not introduced in sequential first-use order: "
                f"observed={first_use}, expected={expected}"
            )

    OUTPUT.write_text(assembled, encoding="utf-8")

    manifest_lines = []
    for name in COMPONENTS:
        path = ROOT / name
        manifest_lines.append(f"{sha256(path)}  {name}")
    for name in FIGURE_FILES:
        path = ROOT / name
        manifest_lines.append(f"{sha256(path)}  {name}")
    manifest_lines.append(f"{sha256(OUTPUT)}  {OUTPUT.name}")
    MANIFEST.write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")

    print("TAES_MANUSCRIPT_ASSEMBLY=PASS")
    print(f"abstract_word_count={len(abstract_words)}")
    print(f"citation_first_use_order={','.join(str(n) for n in first_use)}")
    print("figure1_asset_binding=PASS")
    print("retired_table_v_check=PASS")
    print("ieee_ai_disclosure_binding=PASS")
    print(f"assembled_file={OUTPUT}")
    print(f"assembled_sha256={sha256(OUTPUT)}")
    print(f"component_manifest={MANIFEST}")
    for name in FIGURE_FILES:
        print(f"{name}_sha256={sha256(ROOT / name)}")
    print("NOTE: This is a development draft, not a frozen publisher-facing PDF.")


if __name__ == "__main__":
    main()
