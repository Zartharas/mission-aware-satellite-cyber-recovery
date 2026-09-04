#!/usr/bin/env python3
"""Render the generated JAIS Markdown manuscript to an AIAA-style DOCX.

Requires python-docx. Run build_jais_export.py first or use --build.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

try:
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Inches, Pt
except ImportError as exc:
    raise SystemExit("python-docx is required to generate the JAIS Word manuscript") from exc

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "upload-packet" / "generated" / "JAIS_MANUSCRIPT.md"
OUTPUT = HERE / "upload-packet" / "generated" / "JAIS_MANUSCRIPT.docx"


def set_cell_text(cell, text: str) -> None:
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.0
    r = p.add_run(text.replace("\\|", "|"))
    r.font.name = "Times New Roman"
    r.font.size = Pt(8)


def add_page_number(paragraph) -> None:
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run()
    fld_char1 = OxmlElement("w:fldChar")
    fld_char1.set(qn("w:fldCharType"), "begin")
    instr_text = OxmlElement("w:instrText")
    instr_text.set(qn("xml:space"), "preserve")
    instr_text.text = " PAGE "
    fld_char2 = OxmlElement("w:fldChar")
    fld_char2.set(qn("w:fldCharType"), "end")
    run._r.append(fld_char1)
    run._r.append(instr_text)
    run._r.append(fld_char2)


def add_markdown_paragraph(doc: Document, text: str, style=None):
    p = doc.add_paragraph(style=style)
    p.paragraph_format.line_spacing = 2.0
    p.paragraph_format.space_after = Pt(0)

    # Minimal bold rendering for **...** spans.
    cursor = 0
    for m in re.finditer(r"\*\*(.+?)\*\*", text):
        if m.start() > cursor:
            p.add_run(text[cursor:m.start()])
        r = p.add_run(m.group(1))
        r.bold = True
        cursor = m.end()
    if cursor < len(text):
        p.add_run(text[cursor:])

    for r in p.runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(10)
    return p


def build_docx(source: Path, output: Path) -> None:
    text = source.read_text(encoding="utf-8")
    lines = text.splitlines()

    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)

    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(10)
    normal.paragraph_format.line_spacing = 2.0
    normal.paragraph_format.space_after = Pt(0)

    for style_name in ["Title", "Heading 1", "Heading 2", "Heading 3"]:
        style = styles[style_name]
        style.font.name = "Times New Roman"
        style.font.bold = True
        style.paragraph_format.space_before = Pt(8)
        style.paragraph_format.space_after = Pt(0)
        style.paragraph_format.line_spacing = 2.0
    styles["Title"].font.size = Pt(12)
    styles["Heading 1"].font.size = Pt(11)
    styles["Heading 2"].font.size = Pt(10)
    styles["Heading 3"].font.size = Pt(10)

    add_page_number(section.footer.paragraphs[0])

    i = 0
    first_heading = True
    while i < len(lines):
        line = lines[i].rstrip()
        if not line:
            i += 1
            continue

        if line.startswith("| "):
            block = []
            while i < len(lines) and lines[i].startswith("|"):
                block.append(lines[i])
                i += 1
            parsed = []
            for row in block:
                cells = [c.strip() for c in row.strip().strip("|").split("|")]
                parsed.append(cells)
            if len(parsed) >= 2 and all(re.fullmatch(r"-+", c.replace(":", "")) for c in parsed[1]):
                parsed.pop(1)
            if parsed:
                cols = max(len(r) for r in parsed)
                table = doc.add_table(rows=len(parsed), cols=cols)
                table.style = "Table Grid"
                for rr, row in enumerate(parsed):
                    for cc in range(cols):
                        set_cell_text(table.cell(rr, cc), row[cc] if cc < len(row) else "")
                        if rr == 0:
                            for run in table.cell(rr, cc).paragraphs[0].runs:
                                run.bold = True
                doc.add_paragraph()
            continue

        if line.startswith("# "):
            title = line[2:].strip()
            if first_heading:
                p = doc.add_paragraph(style="Title")
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                r = p.add_run(title)
                r.font.name = "Times New Roman"
                r.font.size = Pt(12)
                r.bold = True
                first_heading = False
            else:
                add_markdown_paragraph(doc, title, "Heading 1")
            i += 1
            continue
        if line.startswith("## "):
            add_markdown_paragraph(doc, line[3:].strip(), "Heading 2")
            i += 1
            continue
        if line.startswith("### "):
            add_markdown_paragraph(doc, line[4:].strip(), "Heading 3")
            i += 1
            continue

        if line.startswith("- "):
            p = add_markdown_paragraph(doc, line[2:].strip(), "List Bullet")
            p.paragraph_format.left_indent = Inches(0.25)
            i += 1
            continue

        if re.match(r"^\d+\.\s", line):
            p = add_markdown_paragraph(doc, re.sub(r"^\d+\.\s+", "", line), "List Number")
            p.paragraph_format.left_indent = Inches(0.25)
            i += 1
            continue

        # Accumulate normal paragraph lines until blank/structural marker.
        para = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r"^(#{1,3}\s|\|\s|-\s|\d+\.\s)", lines[i]):
            para.append(lines[i].strip())
            i += 1
        add_markdown_paragraph(doc, " ".join(para))

    doc.core_properties.title = "Satellite Cyber Response and Trusted Recovery Under Contact and Adversarial Evidence Constraints"
    doc.core_properties.subject = "AIAA Journal of Aerospace Information Systems submission manuscript"
    doc.core_properties.author = "Aman Kumar Singh"
    doc.core_properties.keywords = "satellite cybersecurity, mission-aware cybersecurity, cyber resilience, trusted recovery"

    output.parent.mkdir(parents=True, exist_ok=True)
    doc.save(output)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true", help="run build_jais_export.py first")
    args = ap.parse_args()

    if args.build or not SOURCE.exists():
        subprocess.run([sys.executable, str(HERE / "build_jais_export.py")], check=True)

    build_docx(SOURCE, OUTPUT)
    print(f"docx={OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
