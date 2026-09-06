#!/usr/bin/env python3
"""Audit TAES Paper 2 manuscript length and cross-section redundancy.

This helper is read-only with respect to manuscript components. It reads the
canonical assembled development manuscript and prints section-level metrics and
high-confidence exact sentence repetition across different sections.

It does not edit manuscript text, rerun studies, or modify frozen evidence.
"""

from __future__ import annotations

import collections
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANUSCRIPT = ROOT / "TAES_MANUSCRIPT_FULL_DRAFT.md"

SECTION_ORDER = [
    "Abstract",
    "I. Introduction",
    "II. Related Work and Scientific Positioning",
    "III. Common Trust-Qualification Framework and Study Separation",
    "IV. Temporal Evidence Qualification Under Intermittent Contact",
    "V. Multi-Producer Qualification and Provenance-Domain Constraints",
    "VI. Recovery-Artifact Assurance and Residual Incorrect States",
    "VII. Cross-Study Residual Trust Boundaries",
    "VIII. Validity, Aerospace Interpretation Boundaries, and Future Evaluation",
    "IX. Conclusion",
    "References",
]

WORD_RE = re.compile(r"\b[\w'-]+\b")
SECTION_RE = re.compile(
    r"^## (Abstract|I\. Introduction|II\. Related Work and Scientific Positioning|"
    r"III\. Common Trust-Qualification Framework and Study Separation|"
    r"IV\. Temporal Evidence Qualification Under Intermittent Contact|"
    r"V\. Multi-Producer Qualification and Provenance-Domain Constraints|"
    r"VI\. Recovery-Artifact Assurance and Residual Incorrect States|"
    r"VII\. Cross-Study Residual Trust Boundaries|"
    r"VIII\. Validity, Aerospace Interpretation Boundaries, and Future Evaluation|"
    r"IX\. Conclusion|References)\s*$",
    flags=re.MULTILINE,
)


def words(text: str) -> int:
    return len(WORD_RE.findall(text))


def split_sections(text: str) -> dict[str, str]:
    matches = list(SECTION_RE.finditer(text))
    sections: dict[str, str] = {}
    for i, match in enumerate(matches):
        name = match.group(1)
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        sections[name] = text[start:end].strip()
    missing = [name for name in SECTION_ORDER if name not in sections]
    if missing:
        raise SystemExit(f"ERROR: missing sections: {missing}")
    return sections


def strip_tables_and_headings(text: str) -> str:
    out = []
    for line in text.splitlines():
        if line.startswith("#"):
            continue
        if line.startswith("|"):
            continue
        if re.match(r"^\*\*Table\s+[IVX]+\.", line):
            continue
        out.append(line)
    return "\n".join(out)


def sentence_candidates(text: str) -> list[str]:
    body = strip_tables_and_headings(text)
    chunks = re.split(r"(?<=[.!?])\s+(?=[A-Z`])", body)
    result = []
    for chunk in chunks:
        sentence = " ".join(chunk.split()).strip()
        if words(sentence) >= 12:
            result.append(sentence)
    return result


def normalized_sentence(sentence: str) -> str:
    text = sentence.lower()
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\[[0-9]+\]", "", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def main() -> None:
    if not MANUSCRIPT.is_file():
        raise SystemExit(f"ERROR: missing assembled manuscript: {MANUSCRIPT}")

    text = MANUSCRIPT.read_text(encoding="utf-8").replace("\r\n", "\n")
    sections = split_sections(text)

    manuscript_body_words = sum(words(sections[name]) for name in SECTION_ORDER[:-1])
    references_words = words(sections["References"])

    print("TAES_LENGTH_REDUNDANCY_AUDIT=PASS")
    print(f"manuscript_body_words_including_abstract={manuscript_body_words}")
    print(f"references_words={references_words}")
    print(f"total_words_including_references={manuscript_body_words + references_words}")
    print("SECTION_WORD_COUNTS_BEGIN")
    for name in SECTION_ORDER:
        print(f"{name}\t{words(sections[name])}")
    print("SECTION_WORD_COUNTS_END")

    # High-value boundary/caveat language indicators. Counts are descriptive,
    # not targets. They help identify where interpretation controls may repeat.
    indicators = {
        "does_not": r"\bdoes not\b",
        "do_not": r"\bdo not\b",
        "not_operational": r"\bnot operational\b",
        "mission_availability": r"\bmission availability\b",
        "not_a_probability": r"\bnot (?:an? )?(?:operational )?probabilit(?:y|ies)\b",
        "not_integrated_experiment": r"\bnot (?:an? )?(?:prospectively tested )?integrated (?:experiment|architecture)\b",
        "not_global": r"\bnot (?:a|the) global(?:ly)?\b",
        "finite_model": r"\bfinite (?:model|models|grid|population|populations|state|states|subset space)\b",
        "research_only": r"\bresearch-only\b",
    }
    print("BOUNDARY_LANGUAGE_COUNTS_BEGIN")
    body_lower = "\n".join(sections[name] for name in SECTION_ORDER[:-1]).lower()
    for label, pattern in indicators.items():
        print(f"{label}\t{len(re.findall(pattern, body_lower, flags=re.IGNORECASE))}")
    print("BOUNDARY_LANGUAGE_COUNTS_END")

    # Report only exact normalized sentence repetitions that occur in different
    # sections. This deliberately avoids fuzzy matching that could overstate
    # redundancy in technical prose.
    occurrence: dict[str, list[tuple[str, str]]] = collections.defaultdict(list)
    for section_name in SECTION_ORDER[:-1]:
        for sentence in sentence_candidates(sections[section_name]):
            occurrence[normalized_sentence(sentence)].append((section_name, sentence))

    duplicates = []
    for norm, items in occurrence.items():
        unique_sections = {section for section, _ in items}
        if len(unique_sections) >= 2 and len(norm.split()) >= 12:
            duplicates.append((len(norm.split()), norm, items))
    duplicates.sort(reverse=True)

    print("CROSS_SECTION_EXACT_SENTENCE_DUPLICATES_BEGIN")
    if not duplicates:
        print("NONE")
    else:
        for _, _, items in duplicates[:20]:
            sections_seen = []
            for section, _ in items:
                if section not in sections_seen:
                    sections_seen.append(section)
            print("sections=" + " | ".join(sections_seen))
            print("sentence=" + items[0][1])
    print("CROSS_SECTION_EXACT_SENTENCE_DUPLICATES_END")

    print("NOTE: This audit is descriptive. It does not authorize deletion of scientific results or mandatory limitations.")


if __name__ == "__main__":
    main()
