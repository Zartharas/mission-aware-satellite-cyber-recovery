#!/usr/bin/env python3
"""Build a development-only TAES/IEEEtran two-column PDF from the canonical Markdown manuscript.

The builder is deterministic with respect to tracked manuscript content and the
approved Figure 1 assets. It does not rerun studies or modify any frozen science.
Generated .tex/.pdf/.log/audit files are development artifacts and are not
publisher-facing until separate visual and format QA gates pass.
"""

from __future__ import annotations

import hashlib
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANUSCRIPT = ROOT / "TAES_MANUSCRIPT_FULL_DRAFT.md"
FIG_PDF = ROOT / "TAES_FIGURE1_RESIDUAL_BOUNDARIES.pdf"
FIG_PNG = ROOT / "TAES_FIGURE1_RESIDUAL_BOUNDARIES.png"
OUT_TEX = ROOT / "TAES_MANUSCRIPT_IEEETRAN_DEV.tex"
OUT_PDF = ROOT / "TAES_MANUSCRIPT_IEEETRAN_DEV.pdf"
OUT_LOG = ROOT / "TAES_MANUSCRIPT_IEEETRAN_DEV.log"
OUT_AUDIT = ROOT / "TAES_IEEETRAN_BUILD_AUDIT.txt"

EXPECTED_MANUSCRIPT = "0381d6f60f5721ef2fb1ce3e0bce4e26133ad56cb2d123dfddfa24c2ab35f882"
EXPECTED_FIG_PDF = "4872707261c8a8b6b747e76b9166b4ad7ae426e43d7bd9ffe272e4c5ea6f4ff8"
EXPECTED_FIG_PNG = "7d22964bdae052b35b4680e1b09f3209f1c99bb1d157a0f995dcd2a6445e6698"

TITLE = "Residual Trust Boundaries in Satellite Cyber Recovery: Temporal Evidence, Producer Composition, and Artifact Assurance"
AUTHOR = "Aman Kumar Singh"
AFFILIATION = "Independent Researcher, The Woodlands, Texas, United States"

TABLE_CAPTIONS = {
    "I": "Study-specific realizations",
    "II": "Selected Study-3 residual-boundary results",
    "III": "Study-4 first and systematic failure thresholds",
    "IV": "Study-6 residual incorrect states and benign assurance loss",
}

TABLE_SPECS = {
    "I": [
        r">{\raggedright\arraybackslash}p{0.90in}",
        r">{\raggedright\arraybackslash}p{0.95in}",
        r">{\raggedright\arraybackslash}p{1.00in}",
        r">{\raggedright\arraybackslash}p{2.10in}",
        r">{\centering\arraybackslash}p{0.65in}",
        r">{\raggedright\arraybackslash}p{0.90in}",
    ],
    "II": [
        r">{\raggedright\arraybackslash}p{1.50in}",
        r">{\centering\arraybackslash}p{0.90in}",
        r">{\centering\arraybackslash}p{0.95in}",
        r">{\raggedright\arraybackslash}p{3.15in}",
    ],
    "III": [
        r">{\raggedright\arraybackslash}p{1.10in}",
        r">{\centering\arraybackslash}p{2.70in}",
        r">{\centering\arraybackslash}p{2.70in}",
    ],
    "IV": [
        r">{\raggedright\arraybackslash}p{1.40in}",
        r">{\centering\arraybackslash}p{0.70in}",
        r">{\raggedright\arraybackslash}p{3.10in}",
        r">{\centering\arraybackslash}p{0.55in}",
        r">{\centering\arraybackslash}p{0.70in}",
    ],
}

TABLE_HEADER_KEYS = {
    "Study": "I",
    "Evidence / contact / policy": "II",
    "Rule": "III",
    "Gate": "IV",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def command_path(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise SystemExit(f"ERROR: required command missing: {name}")
    return path


def run(cmd: list[str], *, input_text: str | None = None, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        input=input_text,
        cwd=str(cwd) if cwd else None,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def pandoc_fragment(markdown: str) -> str:
    proc = run([command_path("pandoc"), "--from=gfm", "--to=latex", "--wrap=none"], input_text=markdown.strip() + "\n")
    if proc.returncode != 0:
        raise SystemExit("ERROR: pandoc fragment conversion failed:\n" + proc.stdout)
    return proc.stdout.strip()


def verify_bindings() -> None:
    checks = [
        (MANUSCRIPT, EXPECTED_MANUSCRIPT),
        (FIG_PDF, EXPECTED_FIG_PDF),
        (FIG_PNG, EXPECTED_FIG_PNG),
    ]
    for path, expected in checks:
        if not path.is_file():
            raise SystemExit(f"ERROR: required canonical input missing: {path}")
        actual = sha256(path)
        if actual != expected:
            raise SystemExit(
                f"ERROR: canonical input hash mismatch for {path.name}: expected={expected} actual={actual}"
            )


def extract_between(text: str, start_marker: str, end_marker: str) -> str:
    start = text.find(start_marker)
    if start < 0:
        raise SystemExit(f"ERROR: start marker missing: {start_marker}")
    start += len(start_marker)
    end = text.find(end_marker, start)
    if end < 0:
        raise SystemExit(f"ERROR: end marker missing: {end_marker}")
    return text[start:end].strip()


def markdown_table_cells(line: str) -> list[str]:
    stripped = line.strip()
    if not (stripped.startswith("|") and stripped.endswith("|")):
        raise ValueError("not a pipe-table row")
    return [cell.strip() for cell in stripped[1:-1].split("|")]


def is_table_separator(line: str) -> bool:
    try:
        cells = markdown_table_cells(line)
    except ValueError:
        return False
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in cells)


def latex_escape_plain(text: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(ch, ch) for ch in text)


def cell_to_latex(text: str) -> str:
    code_tokens: dict[str, str] = {}

    def save_code(match: re.Match[str]) -> str:
        token = f"@@CODE{len(code_tokens)}@@"
        code_tokens[token] = r"\texttt{" + latex_escape_plain(match.group(1)) + "}"
        return token

    work = re.sub(r"`([^`]+)`", save_code, text)
    bold_tokens: dict[str, str] = {}

    def save_bold(match: re.Match[str]) -> str:
        token = f"@@BOLD{len(bold_tokens)}@@"
        bold_tokens[token] = r"\textbf{" + latex_escape_plain(match.group(1)) + "}"
        return token

    work = re.sub(r"\*\*([^*]+)\*\*", save_bold, work)
    work = latex_escape_plain(work)
    for token, value in {**code_tokens, **bold_tokens}.items():
        work = work.replace(latex_escape_plain(token), value)
    return work


def render_table(roman: str, header: list[str], rows: list[list[str]]) -> str:
    spec = TABLE_SPECS[roman]
    if len(header) != len(spec):
        raise SystemExit(
            f"ERROR: Table {roman} column count mismatch: header={len(header)} expected={len(spec)}"
        )
    for row in rows:
        if len(row) != len(header):
            raise SystemExit(f"ERROR: Table {roman} row has {len(row)} columns; expected {len(header)}")

    lines = [
        r"\begin{table*}[!t]",
        r"\centering",
        rf"\caption{{{latex_escape_plain(TABLE_CAPTIONS[roman])}}}",
        rf"\label{{tab:taes-{roman.lower()}}}",
        r"\footnotesize",
        r"\setlength{\tabcolsep}{2pt}",
        r"\renewcommand{\arraystretch}{1.08}",
        r"\begin{tabular}{" + "".join(spec) + "}",
        r"\hline",
        " & ".join(r"\textbf{" + cell_to_latex(cell) + "}" for cell in header) + r" \\",
        r"\hline",
    ]
    for row in rows:
        lines.append(" & ".join(cell_to_latex(cell) for cell in row) + r" \\")
    lines.extend([r"\hline", r"\end{tabular}", r"\end{table*}"])
    return "\n".join(lines)


def extract_tables_and_figure(body_md: str) -> tuple[str, dict[str, str], str]:
    lines = body_md.splitlines()
    out: list[str] = []
    tables_rendered: dict[str, str] = {}
    figure_latex = ""
    pending_caption: tuple[str, str] | None = None
    i = 0

    while i < len(lines):
        line = lines[i]
        cap_match = re.match(r"^\*\*Table\s+([IVX]+)\.\s+(.+?)\*\*$", line.strip())
        if cap_match:
            pending_caption = (cap_match.group(1), cap_match.group(2))
            i += 1
            while i < len(lines) and not lines[i].strip():
                i += 1
            continue

        if line.strip() == "![Figure 1](TAES_FIGURE1_RESIDUAL_BOUNDARIES.png)":
            i += 1
            while i < len(lines) and not lines[i].strip():
                i += 1
            if i >= len(lines):
                raise SystemExit("ERROR: Figure 1 caption missing after image marker")
            fig_cap = lines[i].strip()
            match = re.match(r"^\*\*Fig\. 1\.\*\*\s*(.+)$", fig_cap)
            if not match:
                raise SystemExit("ERROR: Figure 1 caption format not recognized")
            caption = match.group(1).strip()
            figure_latex = "\n".join(
                [
                    r"\begin{figure*}[!t]",
                    r"\centering",
                    r"\includegraphics[width=\textwidth]{TAES_FIGURE1_RESIDUAL_BOUNDARIES.pdf}",
                    rf"\caption{{{latex_escape_plain(caption)}}}",
                    r"\label{fig:residual-boundaries}",
                    r"\end{figure*}",
                ]
            )
            out.extend(["", "TAESFIGUREONEPLACEHOLDER", ""])
            i += 1
            continue

        if line.strip().startswith("|") and i + 1 < len(lines) and is_table_separator(lines[i + 1]):
            header = markdown_table_cells(line)
            j = i + 2
            rows: list[list[str]] = []
            while j < len(lines) and lines[j].strip().startswith("|"):
                rows.append(markdown_table_cells(lines[j]))
                j += 1
            first = header[0]
            roman = TABLE_HEADER_KEYS.get(first)
            if not roman:
                raise SystemExit(f"ERROR: unrecognized manuscript table header: {first}")
            if pending_caption and pending_caption[0] != roman:
                raise SystemExit(
                    f"ERROR: pending caption Table {pending_caption[0]} does not match parsed Table {roman}"
                )
            if pending_caption:
                observed_caption = pending_caption[1]
                expected_caption = TABLE_CAPTIONS[roman]
                if observed_caption != expected_caption:
                    raise SystemExit(
                        f"ERROR: Table {roman} caption mismatch: expected={expected_caption!r} observed={observed_caption!r}"
                    )
            pending_caption = None
            if roman in tables_rendered:
                raise SystemExit(f"ERROR: duplicate Table {roman} parsed")
            tables_rendered[roman] = render_table(roman, header, rows)
            out.extend(["", f"TAESTABLE{roman}PLACEHOLDER", ""])
            i = j
            continue

        out.append(line)
        i += 1

    if pending_caption:
        raise SystemExit(f"ERROR: unmatched Table {pending_caption[0]} caption")
    if set(tables_rendered) != {"I", "II", "III", "IV"}:
        raise SystemExit(f"ERROR: expected Tables I-IV, parsed {sorted(tables_rendered)}")
    if not figure_latex:
        raise SystemExit("ERROR: Figure 1 was not parsed from canonical manuscript")

    return "\n".join(out), tables_rendered, figure_latex


def preprocess_headings(markdown: str) -> str:
    text = re.sub(r"^##\s+[IVX]+\.\s+(.+)$", r"# \1", markdown, flags=re.MULTILINE)
    text = re.sub(r"^###\s+[A-Z]\.\s+(.+)$", r"## \1", text, flags=re.MULTILINE)
    return text


def build_body_latex(body_md: str) -> str:
    stripped, tables, figure = extract_tables_and_figure(body_md)
    stripped = preprocess_headings(stripped)
    proc = run(
        [
            command_path("pandoc"),
            "--from=gfm",
            "--to=latex",
            "--wrap=none",
            "--top-level-division=section",
        ],
        input_text=stripped + "\n",
    )
    if proc.returncode != 0:
        raise SystemExit("ERROR: pandoc body conversion failed:\n" + proc.stdout)
    latex = proc.stdout
    for roman, rendered in tables.items():
        token = f"TAESTABLE{roman}PLACEHOLDER"
        if token not in latex:
            raise SystemExit(f"ERROR: Pandoc output lost Table {roman} placeholder")
        latex = latex.replace(token, rendered, 1)
    if "TAESFIGUREONEPLACEHOLDER" not in latex:
        raise SystemExit("ERROR: Pandoc output lost Figure 1 placeholder")
    latex = latex.replace("TAESFIGUREONEPLACEHOLDER", figure, 1)
    return latex.strip()


def build_references(refs_md: str) -> str:
    matches = list(re.finditer(r"(?ms)^\[(\d+)\]\s+(.*?)(?=^\[\d+\]\s+|\Z)", refs_md.strip() + "\n"))
    if [int(m.group(1)) for m in matches] != list(range(1, 14)):
        raise SystemExit("ERROR: expected exactly references [1] through [13]")
    lines = [r"\begin{thebibliography}{13}"]
    for match in matches:
        number = int(match.group(1))
        entry = " ".join(match.group(2).strip().split())
        converted = pandoc_fragment(entry)
        lines.append(rf"\bibitem{{ref{number}}} {converted}")
    lines.append(r"\end{thebibliography}")
    return "\n".join(lines)


def parse_manuscript(md: str) -> tuple[str, str, str, str, str]:
    if not md.startswith("# " + TITLE + "\n"):
        raise SystemExit("ERROR: canonical manuscript title mismatch")

    abstract = extract_between(md, "## Abstract\n", "\n**Index Terms:**")
    index_match = re.search(r"^\*\*Index Terms:\*\*\s*(.+)$", md, flags=re.MULTILINE)
    if not index_match:
        raise SystemExit("ERROR: Index Terms line missing")
    index_terms = index_match.group(1).strip()

    body_start = md.find("## I. Introduction")
    ack_start = md.find("## Acknowledgment")
    refs_start = md.find("## References")
    if min(body_start, ack_start, refs_start) < 0 or not (body_start < ack_start < refs_start):
        raise SystemExit("ERROR: manuscript section ordering for body/Acknowledgment/References is invalid")

    body = md[body_start:ack_start].strip()
    acknowledgment = md[ack_start + len("## Acknowledgment"):refs_start].strip()
    references = md[refs_start + len("## References"):].strip()

    return abstract, index_terms, body, acknowledgment, references


def make_tex(md: str) -> str:
    abstract_md, index_md, body_md, ack_md, refs_md = parse_manuscript(md)
    abstract_latex = pandoc_fragment(abstract_md)
    index_latex = pandoc_fragment(index_md)
    body_latex = build_body_latex(body_md)
    ack_latex = pandoc_fragment(ack_md)
    refs_latex = build_references(refs_md)

    return rf"""\documentclass[10pt,journal]{{IEEEtran}}
\usepackage{{graphicx}}
\usepackage{{array}}
\usepackage{{url}}
\setlength{{\textwidth}}{{7.10in}}
\setlength{{\columnsep}}{{0.20in}}
\setlength{{\oddsidemargin}}{{-0.30in}}
\setlength{{\evensidemargin}}{{-0.30in}}
\setlength{{\textheight}}{{9.00in}}
\setlength{{\topmargin}}{{0in}}
\setlength{{\headheight}}{{0in}}
\setlength{{\headsep}}{{0in}}
\setlength{{\footskip}}{{0.45in}}
\providecommand{{\tightlist}}{{\setlength{{\itemsep}}{{0pt}}\setlength{{\parskip}}{{0pt}}}}
\setlength{{\emergencystretch}}{{0pt}}

\title{{{latex_escape_plain(TITLE)}}}
\author{{{latex_escape_plain(AUTHOR)}\\\small {latex_escape_plain(AFFILIATION)}}}

\begin{{document}}
\typeout{{TAES_TEXTWIDTH_PT=\the\textwidth}}
\typeout{{TAES_COLUMNSEP_PT=\the\columnsep}}
\typeout{{TAES_COLUMNWIDTH_PT=\the\columnwidth}}
\typeout{{TAES_TEXTHEIGHT_PT=\the\textheight}}
\maketitle

\begin{{abstract}}
{abstract_latex}
\end{{abstract}}

\begin{{IEEEkeywords}}
{index_latex}
\end{{IEEEkeywords}}

{body_latex}

\section*{{Acknowledgment}}
{ack_latex}

{refs_latex}

\end{{document}}
"""


def parse_dimension(log_text: str, label: str) -> float:
    match = re.search(rf"{re.escape(label)}=([0-9.]+)pt", log_text)
    if not match:
        raise SystemExit(f"ERROR: TeX log missing dimension marker: {label}")
    return float(match.group(1))


def build_and_audit() -> dict[str, str | int | float | bool]:
    for name in ["pandoc", "latexmk", "pdflatex", "pdfinfo", "pdffonts", "kpsewhich"]:
        command_path(name)

    for tex_file in ["IEEEtran.cls", "graphicx.sty", "array.sty", "url.sty"]:
        proc = run([command_path("kpsewhich"), tex_file])
        if proc.returncode != 0 or not proc.stdout.strip():
            raise SystemExit(f"ERROR: required TeX file unresolved: {tex_file}")

    verify_bindings()
    md = MANUSCRIPT.read_text(encoding="utf-8").replace("\r\n", "\n")
    tex = make_tex(md)
    if "—" in tex:
        raise SystemExit("ERROR: em dash entered generated TeX")
    OUT_TEX.write_text(tex, encoding="utf-8")

    for path in [OUT_PDF, OUT_LOG, OUT_AUDIT]:
        if path.exists():
            path.unlink()

    with tempfile.TemporaryDirectory(prefix=".taes_ieeetran_build_", dir=ROOT) as tmp_name:
        tmp = Path(tmp_name)
        proc = run(
            [
                command_path("latexmk"),
                "-pdf",
                "-g",
                "-interaction=nonstopmode",
                "-halt-on-error",
                "-file-line-error",
                f"-outdir={tmp}",
                OUT_TEX.name,
            ],
            cwd=ROOT,
        )
        built_pdf = tmp / OUT_PDF.name
        built_log = tmp / OUT_LOG.name
        if built_log.is_file():
            shutil.copy2(built_log, OUT_LOG)
        if proc.returncode != 0 or not built_pdf.is_file():
            tail = "\n".join(proc.stdout.splitlines()[-80:])
            raise SystemExit("ERROR: IEEEtran development build failed:\n" + tail)
        shutil.copy2(built_pdf, OUT_PDF)

    log_text = OUT_LOG.read_text(encoding="utf-8", errors="replace")
    textwidth_pt = parse_dimension(log_text, "TAES_TEXTWIDTH_PT")
    columnsep_pt = parse_dimension(log_text, "TAES_COLUMNSEP_PT")
    columnwidth_pt = parse_dimension(log_text, "TAES_COLUMNWIDTH_PT")
    textheight_pt = parse_dimension(log_text, "TAES_TEXTHEIGHT_PT")

    expected = {
        "textwidth": 7.10 * 72.27,
        "columnsep": 0.20 * 72.27,
        "columnwidth": 3.45 * 72.27,
        "textheight": 9.00 * 72.27,
    }
    observed = {
        "textwidth": textwidth_pt,
        "columnsep": columnsep_pt,
        "columnwidth": columnwidth_pt,
        "textheight": textheight_pt,
    }
    for key in expected:
        if abs(expected[key] - observed[key]) > 0.20:
            raise SystemExit(
                f"ERROR: TAES geometry mismatch for {key}: expected_pt={expected[key]:.3f} observed_pt={observed[key]:.3f}"
            )

    pdfinfo = run([command_path("pdfinfo"), str(OUT_PDF)])
    if pdfinfo.returncode != 0:
        raise SystemExit("ERROR: pdfinfo failed:\n" + pdfinfo.stdout)
    pages_match = re.search(r"^Pages:\s+(\d+)", pdfinfo.stdout, flags=re.MULTILINE)
    size_match = re.search(r"^Page size:\s+(.+)$", pdfinfo.stdout, flags=re.MULTILINE)
    if not pages_match or not size_match:
        raise SystemExit("ERROR: unable to parse PDF page count or page size")
    pages = int(pages_match.group(1))
    page_size = size_match.group(1).strip()
    if "612 x 792 pts" not in page_size:
        raise SystemExit(f"ERROR: expected US Letter PDF, observed page size: {page_size}")

    pdffonts = run([command_path("pdffonts"), str(OUT_PDF)])
    if pdffonts.returncode != 0:
        raise SystemExit("ERROR: pdffonts failed:\n" + pdffonts.stdout)
    font_lines = [line for line in pdffonts.stdout.splitlines()[2:] if line.strip()]
    embedded = []
    for line in font_lines:
        parts = line.split()
        if len(parts) >= 7:
            embedded.append(parts[-5].lower() == "yes")
    font_embedding_all_yes = bool(embedded) and all(embedded)

    overfull_h = len(re.findall(r"Overfull \\hbox", log_text))
    overfull_v = len(re.findall(r"Overfull \\vbox", log_text))
    underfull_h = len(re.findall(r"Underfull \\hbox", log_text))
    underfull_v = len(re.findall(r"Underfull \\vbox", log_text))
    latex_warning_count = len(re.findall(r"LaTeX Warning:", log_text))

    return {
        "pages": pages,
        "page_size": page_size,
        "textwidth_pt": textwidth_pt,
        "columnsep_pt": columnsep_pt,
        "columnwidth_pt": columnwidth_pt,
        "textheight_pt": textheight_pt,
        "overfull_hbox_count": overfull_h,
        "overfull_vbox_count": overfull_v,
        "underfull_hbox_count": underfull_h,
        "underfull_vbox_count": underfull_v,
        "latex_warning_count": latex_warning_count,
        "font_count": len(font_lines),
        "font_embedding_all_yes": font_embedding_all_yes,
        "estimated_pages_over_10": max(0, pages - 10),
        "tex_sha256": sha256(OUT_TEX),
        "pdf_sha256": sha256(OUT_PDF),
        "log_sha256": sha256(OUT_LOG),
    }


def main() -> None:
    result = build_and_audit()
    layout_clean = (
        result["overfull_hbox_count"] == 0
        and result["overfull_vbox_count"] == 0
        and result["font_embedding_all_yes"] is True
    )

    audit_lines = [
        "TAES_IEEETRAN_BUILD_AUDIT",
        f"canonical_manuscript_sha256={EXPECTED_MANUSCRIPT}",
        f"figure1_pdf_sha256={EXPECTED_FIG_PDF}",
        f"figure1_png_sha256={EXPECTED_FIG_PNG}",
        f"tex_sha256={result['tex_sha256']}",
        f"pdf_sha256={result['pdf_sha256']}",
        f"log_sha256={result['log_sha256']}",
        f"pages={result['pages']}",
        f"estimated_pages_over_10={result['estimated_pages_over_10']}",
        f"page_size={result['page_size']}",
        f"textwidth_pt={result['textwidth_pt']:.3f}",
        f"columnsep_pt={result['columnsep_pt']:.3f}",
        f"columnwidth_pt={result['columnwidth_pt']:.3f}",
        f"textheight_pt={result['textheight_pt']:.3f}",
        f"overfull_hbox_count={result['overfull_hbox_count']}",
        f"overfull_vbox_count={result['overfull_vbox_count']}",
        f"underfull_hbox_count={result['underfull_hbox_count']}",
        f"underfull_vbox_count={result['underfull_vbox_count']}",
        f"latex_warning_count={result['latex_warning_count']}",
        f"font_count={result['font_count']}",
        f"font_embedding_all_yes={'PASS' if result['font_embedding_all_yes'] else 'FAIL'}",
        f"layout_warning_gate={'PASS' if layout_clean else 'REVIEW_REQUIRED'}",
        "publisher_facing=NO",
        "pdf_visual_qa_required=YES",
        "submission_authorized=NO",
    ]
    OUT_AUDIT.write_text("\n".join(audit_lines) + "\n", encoding="utf-8")

    print("TAES_IEEETRAN_BUILD=PASS_COMPILED_DEVELOPMENT_ONLY")
    print(f"pages={result['pages']}")
    print(f"estimated_pages_over_10={result['estimated_pages_over_10']}")
    print(f"page_size={result['page_size']}")
    print("geometry_check=PASS")
    print(f"textwidth_in={result['textwidth_pt'] / 72.27:.3f}")
    print(f"columnsep_in={result['columnsep_pt'] / 72.27:.3f}")
    print(f"columnwidth_in={result['columnwidth_pt'] / 72.27:.3f}")
    print(f"textheight_in={result['textheight_pt'] / 72.27:.3f}")
    print(f"overfull_hbox_count={result['overfull_hbox_count']}")
    print(f"overfull_vbox_count={result['overfull_vbox_count']}")
    print(f"underfull_hbox_count={result['underfull_hbox_count']}")
    print(f"underfull_vbox_count={result['underfull_vbox_count']}")
    print(f"latex_warning_count={result['latex_warning_count']}")
    print(f"font_count={result['font_count']}")
    print(f"font_embedding_all_yes={'PASS' if result['font_embedding_all_yes'] else 'FAIL'}")
    print(f"layout_warning_gate={'PASS' if layout_clean else 'REVIEW_REQUIRED'}")
    print(f"tex={OUT_TEX}")
    print(f"tex_sha256={result['tex_sha256']}")
    print(f"pdf={OUT_PDF}")
    print(f"pdf_sha256={result['pdf_sha256']}")
    print(f"log={OUT_LOG}")
    print(f"audit={OUT_AUDIT}")
    print("publisher_facing=NO")
    print("pdf_visual_qa_required=YES")
    print("submission_authorized=NO")


if __name__ == "__main__":
    main()
