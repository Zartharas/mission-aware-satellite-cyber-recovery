#!/usr/bin/env python3
"""Apply submission-facing prose normalization to the generated JAIS manuscript.

This is a venue-facing editorial layer only. It does not alter frozen numerical
results, statistical populations, treatment identities, or claim boundaries.
"""

from __future__ import annotations

from pathlib import Path

from docx import Document

HERE = Path(__file__).resolve().parent
GENERATED = HERE / "upload-packet" / "generated"
MARKDOWN = GENERATED / "JAIS_MANUSCRIPT.md"
DOCX = GENERATED / "JAIS_MANUSCRIPT.docx"

EM_DASH = "\u2014"

TARGETED_REPLACEMENTS = {
    "The narrower anticipated mechanism\u2014nominal behavioral restoration without sufficient verification\u2014was not observed in A13.":
        "The narrower anticipated mechanism, nominal behavioral restoration without sufficient verification, was not observed in A13.",
}


def normalize_text(text: str) -> str:
    for old, new in TARGETED_REPLACEMENTS.items():
        text = text.replace(old, new)
    text = text.replace(" \u2014 ", ": ")
    text = text.replace(EM_DASH, "-")
    return text


def iter_paragraphs(container):
    for paragraph in container.paragraphs:
        yield paragraph
    for table in container.tables:
        for row in table.rows:
            for cell in row.cells:
                yield from iter_paragraphs(cell)


def normalize_docx(path: Path) -> int:
    doc = Document(path)
    changed = 0
    for paragraph in iter_paragraphs(doc):
        if EM_DASH not in paragraph.text:
            continue
        replacement = normalize_text(paragraph.text)
        if paragraph.runs:
            paragraph.runs[0].text = replacement
            for run in paragraph.runs[1:]:
                run.text = ""
        else:
            paragraph.add_run(replacement)
        changed += 1

    doc.core_properties.author = "Aman Kumar Singh"
    doc.core_properties.last_modified_by = "Aman Kumar Singh"
    doc.save(path)
    return changed


def extract_docx_text(path: Path) -> str:
    doc = Document(path)
    return "\n".join(p.text for p in iter_paragraphs(doc))


def main() -> int:
    if not MARKDOWN.exists() or not DOCX.exists():
        raise SystemExit("Run the JAIS build and Word renderer before finalization")

    md_before = MARKDOWN.read_text(encoding="utf-8")
    md_after = normalize_text(md_before)
    MARKDOWN.write_text(md_after, encoding="utf-8")

    changed_paragraphs = normalize_docx(DOCX)
    docx_text = extract_docx_text(DOCX)

    if EM_DASH in md_after or EM_DASH in docx_text:
        raise SystemExit("Submission finalization failed: em dash remains in manuscript")

    print(f"markdown_em_dashes_removed={md_before.count(EM_DASH)}")
    print(f"docx_paragraphs_normalized={changed_paragraphs}")
    print("submission_punctuation_gate=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
