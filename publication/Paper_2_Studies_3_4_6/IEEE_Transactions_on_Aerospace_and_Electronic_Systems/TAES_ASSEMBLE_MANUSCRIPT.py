#!/usr/bin/env python3
"""Assemble the controlled TAES Paper-2 manuscript components in place.

This script does not fetch data, rerun studies, or alter frozen science. It only
combines already tracked manuscript-development components in the canonical
TAES publication directory.
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


def between(text: str, start: str, end: str) -> str:
    try:
        a = text.index(start) + len(start)
        b = text.index(end, a)
    except ValueError as exc:
        raise SystemExit(f"ERROR: assembly marker missing: {exc}") from exc
    return text[a:b].strip()


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


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    for name in COMPONENTS:
        read(name)

    abstract_doc = read("TAES_ABSTRACT_KEYWORDS.md")
    abstract = between(abstract_doc, "## Abstract\n\n", "\n\n**Word count:")
    index_terms = between(abstract_doc, "## Index Terms\n\n", "\n\n## Abstract claim controls")

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

    assembled_parts = [
        f"# {TITLE}",
        "## Abstract\n\n" + abstract,
        "**Index Terms:** " + index_terms,
        section_i,
        sections_ii_iii,
        *later_sections,
        references,
    ]

    assembled = "\n\n".join(part.strip() for part in assembled_parts if part.strip()) + "\n"

    if "—" in assembled:
        raise SystemExit("ERROR: em dash detected in assembled manuscript")

    # These guards target affirmative manuscript constructs. Limitation text is
    # allowed to mention terms such as "external replication" in order to state
    # explicitly that the present same-repository audits are not external replication.
    prohibited_exact = [
        "N = 6,408",
        "N=6,408",
        "globally best policy",
        "globally best gate",
    ]
    for phrase in prohibited_exact:
        if phrase in assembled:
            raise SystemExit(f"ERROR: prohibited exact manuscript phrase detected: {phrase}")

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
        "## References",
    ]
    for marker in required_markers:
        if marker not in assembled:
            raise SystemExit(f"ERROR: required assembled section missing: {marker}")

    OUTPUT.write_text(assembled, encoding="utf-8")

    manifest_lines = []
    for name in COMPONENTS:
        path = ROOT / name
        manifest_lines.append(f"{sha256(path)}  {name}")
    manifest_lines.append(f"{sha256(OUTPUT)}  {OUTPUT.name}")
    MANIFEST.write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")

    print("TAES_MANUSCRIPT_ASSEMBLY=PASS")
    print(f"abstract_word_count={len(abstract_words)}")
    print(f"assembled_file={OUTPUT}")
    print(f"assembled_sha256={sha256(OUTPUT)}")
    print(f"component_manifest={MANIFEST}")
    print("NOTE: This is a development draft, not a frozen publisher-facing PDF.")


if __name__ == "__main__":
    main()
