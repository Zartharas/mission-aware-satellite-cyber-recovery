#!/usr/bin/env python3
"""Build the peer-review supplementary PDF for the TAES Paper-2 short track.

The builder is bound to the exact generated supplementary Markdown and README,
the audited Figure-1 raster used as Supplementary Fig. S1, the visually approved
R8 eight-page main article, and the frozen 16-page R9 fallback.

It does not regenerate, rerun, enlarge, or modify Studies 3, 4, or 6. It creates
only development TeX/PDF/log/audit artifacts for the separate supplementary
material. The supplement is intentionally single-column for readable expanded
methods and complete finite tables; it is not appended to the main article.
"""

from __future__ import annotations

import hashlib
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent

SUPP_MD = ROOT / "TAES_10P_R3_SUPPLEMENTARY_MATERIAL.md"
SUPP_README = ROOT / "TAES_10P_R3_SUPPLEMENTARY_README.txt"
FIGURE_PNG = ROOT / "TAES_FIGURE1_RESIDUAL_BOUNDARIES.png"
MAIN_R8_PDF = ROOT / "TAES_10P_R3_MANUSCRIPT_IEEETRAN_R8_DEV.pdf"
FROZEN_R9_PDF = ROOT / "TAES_MANUSCRIPT.pdf"

OUT_TEX = ROOT / "TAES_10P_R3_SUPPLEMENTARY_MATERIAL_DEV.tex"
OUT_PDF = ROOT / "TAES_10P_R3_SUPPLEMENTARY_MATERIAL_DEV.pdf"
OUT_LOG = ROOT / "TAES_10P_R3_SUPPLEMENTARY_MATERIAL_DEV.log"
OUT_AUDIT = ROOT / "TAES_10P_R3_SUPPLEMENTARY_BUILD_AUDIT.txt"

EXPECTED_SUPP_MD = "e6313fca178f9de40a6b7c28468be6b20ae1fc7249c2e3c8e30ca5fbf0d7027c"
EXPECTED_README = "b7603d36ba2b9297b970dcad0138fbb9faadae4d8be946e4f05ebb6bdb6609c5"
EXPECTED_FIGURE_PNG = "7d22964bdae052b35b4680e1b09f3209f1c99bb1d157a0f995dcd2a6445e6698"
EXPECTED_MAIN_R8_PDF = "f34cd280371f73492f6ef746fd52279fb1ab01fa4ce8c38eedb8aa67a74f551b"
EXPECTED_FROZEN_R9_PDF = "a7624fa416ebe4ba4d0b9e46da25b5dcb4d85e23e63291f4bdf497d5ba6cb319"

TITLE = "Residual Trust Boundaries in Satellite Cyber Recovery: Temporal Evidence, Producer Composition, and Artifact Assurance"
AUTHOR = "Aman Kumar Singh"
AFFILIATION = "Independent Researcher, The Woodlands, Texas, United States"

REQUIRED_COMMANDS = ["pandoc", "latexmk", "pdfinfo", "pdffonts", "pdftotext"]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def require_file(path: Path, expected: str, label: str) -> None:
    if not path.is_file():
        raise SystemExit(f"ERROR: missing {label}: {path}")
    actual = sha256(path)
    if actual != expected:
        raise SystemExit(
            f"ERROR: {label} SHA-256 mismatch: expected={expected} actual={actual}"
        )


def require_commands() -> None:
    for command in REQUIRED_COMMANDS:
        if not shutil.which(command):
            raise SystemExit(f"ERROR: required command missing: {command}")


def run(args: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        args,
        cwd=str(cwd) if cwd else None,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if proc.returncode != 0:
        print(proc.stdout)
        raise SystemExit(f"ERROR: command failed ({proc.returncode}): {' '.join(args)}")
    return proc


def shift_headings_and_embed_figure(source: str) -> tuple[str, str]:
    source = source.replace("\r\n", "\n")
    lines = source.splitlines()
    if not lines:
        raise SystemExit("ERROR: empty supplementary Markdown")

    expected_title_line = f"# Supplementary Material for: {TITLE}"
    if lines[0].strip() != expected_title_line:
        raise SystemExit(
            "ERROR: unexpected supplementary H1: " + lines[0].strip()
        )

    body_lines: list[str] = []
    figure_hits = 0
    for line in lines[1:]:
        stripped = line.strip()
        if stripped == "![Supplementary Figure S1](TAES_FIGURE1_RESIDUAL_BOUNDARIES.png)":
            figure_hits += 1
            body_lines.extend([
                r"\begin{center}",
                r"\includegraphics[width=0.96\textwidth]{TAES_FIGURE1_RESIDUAL_BOUNDARIES.png}",
                r"\end{center}",
            ])
            continue

        match = re.match(r"^(#{2,6})(\s+.*)$", line)
        if match:
            hashes, rest = match.groups()
            line = "#" * (len(hashes) - 1) + rest
        body_lines.append(line)

    if figure_hits != 1:
        raise SystemExit(
            f"ERROR: expected one Supplementary Fig. S1 image marker; found {figure_hits}"
        )

    body = "\n".join(body_lines).lstrip() + "\n"
    return expected_title_line[2:], body


def make_breakable_texttt(tex: str) -> tuple[str, int]:
    pattern = re.compile(r"\\texttt\{((?:\\.|[^{}])*)\}")
    count = 0

    def repl(match: re.Match[str]) -> str:
        nonlocal count
        content = match.group(1)
        if r"\allowbreak{}" in content:
            return match.group(0)
        new = content.replace(r"\_", r"\_\allowbreak{}")
        new = re.sub(r"-(?!\\allowbreak\{\})", r"-\\allowbreak{}", new)
        if new != content:
            count += new.count(r"\allowbreak{}")
        return r"\texttt{" + new + "}"

    return pattern.sub(repl, tex), count


def pandoc_body(markdown_body: str) -> tuple[str, int]:
    with tempfile.TemporaryDirectory(prefix="taes_supp_") as tmp:
        tmp_path = Path(tmp)
        md_path = tmp_path / "body.md"
        md_path.write_text(markdown_body, encoding="utf-8")
        proc = run([
            "pandoc",
            str(md_path),
            "--from=gfm+raw_tex",
            "--to=latex",
            "--wrap=none",
        ], cwd=ROOT)
    tex, break_count = make_breakable_texttt(proc.stdout)
    return tex, break_count


def build_tex(source: str) -> tuple[str, int]:
    display_title, body_md = shift_headings_and_embed_figure(source)
    body_tex, break_count = pandoc_body(body_md)

    required_tex_markers = [
        "Appendix A",
        "Appendix B",
        "Appendix C",
        "Appendix D",
        "Appendix E",
        "Table S1",
        "Table S2",
        "Table S3",
        "Fig. S1",
        "S3-K4E-001",
        "S4-MPQ-001",
        "S6-SCTR-001",
    ]
    for marker in required_tex_markers:
        if marker not in body_tex:
            raise SystemExit(f"ERROR: expected supplement marker missing after Pandoc: {marker}")

    preamble = rf"""\documentclass[10pt]{{article}}
\usepackage[letterpaper,margin=0.78in]{{geometry}}
\usepackage[T1]{{fontenc}}
\usepackage[utf8]{{inputenc}}
\usepackage{{mathptmx}}
\usepackage{{microtype}}
\usepackage{{graphicx}}
\usepackage{{booktabs}}
\usepackage{{longtable}}
\usepackage{{array}}
\usepackage{{calc}}
\usepackage{{enumitem}}
\usepackage{{caption}}
\usepackage{{xurl}}
\usepackage[hidelinks]{{hyperref}}
\usepackage{{float}}
\setlength{{\parindent}}{{1em}}
\setlength{{\parskip}}{{0.22em}}
\setlength{{\emergencystretch}}{{1.5em}}
\setlength{{\LTleft}}{{0pt}}
\setlength{{\LTright}}{{0pt}}
\renewcommand{{\arraystretch}}{{1.08}}
\providecommand{{\tightlist}}{{%
  \setlength{{\itemsep}}{{0pt}}\setlength{{\parskip}}{{0pt}}}}
\begin{{document}}
\begin{{center}}
{{\Large\bfseries Supplementary Material\par}}
\vspace{{0.35em}}
{{\large\bfseries {display_title}\par}}
\vspace{{0.55em}}
{{\normalsize {AUTHOR}\par}}
{{\small {AFFILIATION}\par}}
\end{{center}}
\vspace{{0.4em}}
"""
    tex = preamble + body_tex + "\n\\end{document}\n"
    if r"\sloppy" in tex:
        raise SystemExit("ERROR: supplement TeX unexpectedly contains \\sloppy")
    return tex, break_count


def parse_pdfinfo(pdf: Path) -> tuple[int, str]:
    out = run(["pdfinfo", str(pdf)]).stdout
    pages_match = re.search(r"^Pages:\s+(\d+)", out, flags=re.MULTILINE)
    size_match = re.search(r"^Page size:\s+(.+)$", out, flags=re.MULTILINE)
    if not pages_match or not size_match:
        raise SystemExit("ERROR: unable to parse supplement pdfinfo")
    return int(pages_match.group(1)), size_match.group(1).strip()


def font_audit(pdf: Path) -> tuple[int, bool]:
    out = run(["pdffonts", str(pdf)]).stdout
    lines = [line for line in out.splitlines()[2:] if line.strip()]
    embedded = True
    for line in lines:
        parts = line.split()
        if len(parts) >= 6 and parts[-4].lower() != "yes":
            embedded = False
    return len(lines), embedded


def box_counts(log: str) -> dict[str, int]:
    return {
        "overfull_hbox": log.count("Overfull \\hbox"),
        "overfull_vbox": log.count("Overfull \\vbox"),
        "underfull_hbox": log.count("Underfull \\hbox"),
        "underfull_vbox": log.count("Underfull \\vbox"),
        "latex_warning": log.count("LaTeX Warning:"),
    }


def text_gate(pdf: Path) -> None:
    text = run(["pdftotext", str(pdf), "-"]).stdout
    markers = [
        "Supplementary Material",
        TITLE,
        "Supplementary Figure S1",
        "Fig. S1.",
        "Appendix A",
        "Appendix B",
        "Appendix C",
        "Appendix D",
        "Appendix E",
        "Table S1",
        "Table S2",
        "Table S3",
        "1,380 trajectories",
        "4,608 exact observations",
        "420 exact observations",
        "PRE_ONSET_CACHE",
        "APPROVED_BAD_SOURCE",
    ]
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise SystemExit("ERROR: supplement PDF text-gate missing: " + ", ".join(missing))


def main() -> None:
    require_commands()
    require_file(SUPP_MD, EXPECTED_SUPP_MD, "R3 supplementary Markdown")
    require_file(SUPP_README, EXPECTED_README, "R3 supplementary README")
    require_file(FIGURE_PNG, EXPECTED_FIGURE_PNG, "Supplementary Fig. S1 PNG")
    require_file(MAIN_R8_PDF, EXPECTED_MAIN_R8_PDF, "visually approved R8 main PDF")
    require_file(FROZEN_R9_PDF, EXPECTED_FROZEN_R9_PDF, "frozen R9 fallback PDF")

    source = SUPP_MD.read_text(encoding="utf-8").replace("\r\n", "\n")
    if "—" in source:
        raise SystemExit("ERROR: em dash detected in bound supplementary source")
    if "6,408" in source:
        raise SystemExit("ERROR: pooled Paper-2 population detected in supplement")

    tex, break_count = build_tex(source)
    OUT_TEX.write_text(tex, encoding="utf-8")

    run([
        "latexmk",
        "-pdf",
        "-interaction=nonstopmode",
        "-halt-on-error",
        "-file-line-error",
        OUT_TEX.name,
    ], cwd=ROOT)

    if not OUT_PDF.is_file() or not OUT_LOG.is_file():
        raise SystemExit("ERROR: supplement build did not create expected PDF/log")

    pages, page_size = parse_pdfinfo(OUT_PDF)
    log = OUT_LOG.read_text(encoding="utf-8", errors="replace")
    boxes = box_counts(log)
    font_count, all_fonts_embedded = font_audit(OUT_PDF)
    text_gate(OUT_PDF)

    audit_lines = [
        "TAES_10P_R3_SUPPLEMENTARY_BUILD=PASS_COMPILED_DEVELOPMENT_ONLY",
        f"supplement_source_sha256={EXPECTED_SUPP_MD}",
        f"supplement_readme_sha256={EXPECTED_README}",
        f"figure_s1_png_sha256={EXPECTED_FIGURE_PNG}",
        f"paired_main_r8_pdf_sha256={EXPECTED_MAIN_R8_PDF}",
        f"frozen_r9_fallback_pdf_sha256={EXPECTED_FROZEN_R9_PDF}",
        f"tex_sha256={sha256(OUT_TEX)}",
        f"pdf_sha256={sha256(OUT_PDF)}",
        f"log_sha256={sha256(OUT_LOG)}",
        f"pages={pages}",
        f"page_size={page_size}",
        f"overfull_hbox_count={boxes['overfull_hbox']}",
        f"overfull_vbox_count={boxes['overfull_vbox']}",
        f"underfull_hbox_count={boxes['underfull_hbox']}",
        f"underfull_vbox_count={boxes['underfull_vbox']}",
        f"latex_warning_count={boxes['latex_warning']}",
        f"font_count={font_count}",
        f"font_embedding_all_yes={'PASS' if all_fonts_embedded else 'FAIL'}",
        f"breakable_code_insertions={break_count}",
        "figure_s1_embedded=YES",
        "appendices_a_e_text_gate=PASS",
        "tables_s1_s2_s3_text_gate=PASS",
        "main_article_appended=NO",
        "main_article_page_count_changed=NO",
        "supplement_content_changed=NO",
        "science_files_changed=NONE",
        "study_rerun=NO",
        "publisher_facing=NO",
        "supplement_visual_qa_required=YES",
        "merge_to_main=NOT_AUTHORIZED_UNTIL_QA_PASS",
    ]
    OUT_AUDIT.write_text("\n".join(audit_lines) + "\n", encoding="utf-8")

    for line in audit_lines:
        print(line)

    print("SUPPLEMENT_OVERFULL_CONTEXT_BEGIN")
    pattern = re.compile(
        r"Overfull \\hbox \(([0-9.]+)pt too wide\) in paragraph at lines (\d+)--(\d+)"
    )
    matches = list(pattern.finditer(log))
    if not matches:
        print("NONE")
    else:
        tex_lines = tex.splitlines()
        for match in matches:
            width = match.group(1)
            start = int(match.group(2))
            end = int(match.group(3))
            print(f"overflow_pt={width} lines={start}--{end}")
            for number in range(max(1, start - 1), min(len(tex_lines), end + 1) + 1):
                value = tex_lines[number - 1].strip()
                if len(value) > 320:
                    value = value[:317] + "..."
                print(f"tex_{number}={value}")
    print("SUPPLEMENT_OVERFULL_CONTEXT_END")


if __name__ == "__main__":
    main()
