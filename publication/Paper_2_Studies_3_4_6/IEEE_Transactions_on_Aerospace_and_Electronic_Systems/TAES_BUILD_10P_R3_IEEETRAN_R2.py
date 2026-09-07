#!/usr/bin/env python3
"""Revision-2 typography builder for the balanced eight-page TAES Paper-2 candidate.

R1 established the preferred eight-page pagination but left four horizontal
Overfull hboxes, all caused by long monospaced Study-6 identifiers. R2 preserves
the exact balanced-R3 Markdown source and all R1 science/layout behavior, then
applies the already validated TAES_BUILD_IEEETRAN_R3 discretionary-break
strategy to simple ``\\texttt{...}`` identifiers.

No visible identifier character is removed, abbreviated, or changed. No
manuscript prose, frozen result, reference, table value, supplement, geometry
setting, or publisher-facing R9 artifact is modified. ``\\sloppy`` is forbidden.
"""

from __future__ import annotations

import re
from pathlib import Path

import TAES_BUILD_10P_R3_IEEETRAN_R1 as prev
import TAES_BUILD_10P_IEEETRAN_R2 as short_math
import TAES_BUILD_IEEETRAN_R3 as breakable

ROOT = Path(__file__).resolve().parent
OUT_TEX = ROOT / "TAES_10P_R3_MANUSCRIPT_IEEETRAN_R2_DEV.tex"
OUT_PDF = ROOT / "TAES_10P_R3_MANUSCRIPT_IEEETRAN_R2_DEV.pdf"
OUT_LOG = ROOT / "TAES_10P_R3_MANUSCRIPT_IEEETRAN_R2_DEV.log"
OUT_AUDIT = ROOT / "TAES_10P_R3_IEEETRAN_R2_BUILD_AUDIT.txt"

_BREAKABLE_COUNT = 0


def make_tex_r2(md: str) -> str:
    global _BREAKABLE_COUNT

    # Preserve R1's three display-math conversions before adding discretionary
    # line-break opportunities to the remaining simple monospaced identifiers.
    prev.r1.convert_common_math = short_math.convert_common_math_r2
    tex = prev.r1.make_short_tex(md)
    tex, _BREAKABLE_COUNT = breakable._make_breakable_code(tex)

    if r"\sloppy" in tex:
        raise SystemExit("ERROR: balanced R3 R2 unexpectedly contains \\sloppy")
    if _BREAKABLE_COUNT < 1:
        raise SystemExit("ERROR: balanced R3 R2 found no breakable code tokens")
    return tex


def page_decision(pages: int) -> str:
    if pages <= 7:
        return "BELOW_BALANCED_TARGET_REVIEW_BEFORE_FREEZE"
    if pages in (8, 9):
        return "PREFERRED_BUFFER_TARGET"
    if pages == 10:
        return "ACCEPTABLE_NO_PRODUCTION_BUFFER"
    return "ABOVE_10_REVIEW_REQUIRED"


def write_audit(result: dict[str, str | int | float | bool]) -> None:
    pages = int(result["pages"])
    layout_horizontal = "PASS" if int(result["overfull_hbox_count"]) == 0 else "REVIEW_REQUIRED"
    lines = [
        "TAES_10P_R3_IEEETRAN_R2_BUILD_AUDIT",
        f"balanced_r3_manuscript_sha256={prev.EXPECTED_SHORT_MD}",
        f"frozen_r9_fallback_pdf_sha256={prev.EXPECTED_FROZEN_R9_PDF}",
        "balanced_r3_words_including_references=5625",
        f"tex_sha256={result['tex_sha256']}",
        f"pdf_sha256={result['pdf_sha256']}",
        f"log_sha256={result['log_sha256']}",
        f"pages={pages}",
        f"estimated_pages_over_10={result['estimated_pages_over_10']}",
        f"page_target_decision={page_decision(pages)}",
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
        f"horizontal_overflow_gate={layout_horizontal}",
        f"breakable_code_tokens={_BREAKABLE_COUNT}",
        "breakable_code_strategy=TEXTTT_EXPLICIT_DISCRETIONARY_BREAKS",
        "common_framework_display_math_conversions=3",
        "tables_rendered=I,II,III",
        "figure1_main_article=ABSENT_BY_SHORT_TRACK_DESIGN",
        "global_geometry_changed=NO",
        "localized_sloppy_blocks=0",
        "manuscript_source_changed=NO",
        "supplement_content_changed=NO",
        "science_files_changed=NONE",
        "study_rerun=NO",
        "publisher_facing=NO",
        "pdf_visual_qa_required=YES",
        "merge_to_main=NOT_AUTHORIZED_UNTIL_QA_PASS",
    ]
    OUT_AUDIT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def print_overfull_context() -> None:
    if not OUT_LOG.is_file() or not OUT_TEX.is_file():
        return
    log = OUT_LOG.read_text(encoding="utf-8", errors="replace")
    tex_lines = OUT_TEX.read_text(encoding="utf-8", errors="replace").splitlines()
    pattern = re.compile(
        r"Overfull \\hbox \(([0-9.]+)pt too wide\) in paragraph at lines (\d+)--(\d+)"
    )
    matches = list(pattern.finditer(log))
    print("TAES_10P_R3_R2_OVERFULL_CONTEXT_BEGIN")
    if not matches:
        print("NONE")
    else:
        seen: set[tuple[int, int, str]] = set()
        for match in matches:
            width = match.group(1)
            start = int(match.group(2))
            end = int(match.group(3))
            key = (start, end, width)
            if key in seen:
                continue
            seen.add(key)
            print(f"overflow_pt={width} lines={start}--{end}")
            lo = max(1, start - 1)
            hi = min(len(tex_lines), end + 1)
            for number in range(lo, hi + 1):
                text = tex_lines[number - 1].strip()
                if len(text) > 280:
                    text = text[:277] + "..."
                print(f"tex_{number}={text}")
    print("TAES_10P_R3_R2_OVERFULL_CONTEXT_END")


def main() -> None:
    prev.verify_r3_binding()

    # Rebind the validated short-paper build framework only to the R2 generated
    # artifact names. The source binding remains the exact balanced R3 Markdown.
    prev.r1.SHORT_MD = prev.SHORT_MD
    prev.r1.OUT_TEX = OUT_TEX
    prev.r1.OUT_PDF = OUT_PDF
    prev.r1.OUT_LOG = OUT_LOG
    prev.r1.OUT_AUDIT = OUT_AUDIT
    prev.r1.EXPECTED_SHORT_MD = prev.EXPECTED_SHORT_MD
    prev.r1.convert_common_math = short_math.convert_common_math_r2
    prev.r1.verify_short_binding = prev.verify_r3_binding

    prev.r1.base.MANUSCRIPT = prev.SHORT_MD
    prev.r1.base.OUT_TEX = OUT_TEX
    prev.r1.base.OUT_PDF = OUT_PDF
    prev.r1.base.OUT_LOG = OUT_LOG
    prev.r1.base.OUT_AUDIT = OUT_AUDIT
    prev.r1.base.EXPECTED_MANUSCRIPT = prev.EXPECTED_SHORT_MD
    prev.r1.base.TABLE_CAPTIONS = prev.r1.TABLE_CAPTIONS
    prev.r1.base.TABLE_SPECS = prev.r1.TABLE_SPECS
    prev.r1.base.TABLE_HEADER_KEYS = prev.r1.TABLE_HEADER_KEYS
    prev.r1.base.verify_bindings = prev.verify_r3_binding
    prev.r1.base.make_tex = make_tex_r2

    result = prev.r1.base.build_and_audit()
    write_audit(result)
    pages = int(result["pages"])

    print("TAES_10P_R3_IEEETRAN_BUILD=PASS_COMPILED_DEVELOPMENT_ONLY")
    print("TAES_10P_R3_IEEETRAN_BUILD_REVISION=2")
    print("r2_change=GENERATED_LATEX_BREAKABLE_MONOSPACED_IDENTIFIERS_ONLY")
    print(f"balanced_r3_manuscript_sha256={prev.EXPECTED_SHORT_MD}")
    print("balanced_r3_words_including_references=5625")
    print(f"pages={pages}")
    print(f"estimated_pages_over_10={result['estimated_pages_over_10']}")
    print(f"page_target_decision={page_decision(pages)}")
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
    print(f"breakable_code_tokens={_BREAKABLE_COUNT}")
    print("breakable_code_strategy=TEXTTT_EXPLICIT_DISCRETIONARY_BREAKS")
    print("localized_sloppy_blocks=0")
    print("global_geometry_changed=NO")
    print(f"tex={OUT_TEX}")
    print(f"tex_sha256={result['tex_sha256']}")
    print(f"pdf={OUT_PDF}")
    print(f"pdf_sha256={result['pdf_sha256']}")
    print(f"log={OUT_LOG}")
    print(f"audit={OUT_AUDIT}")
    print("frozen_r9_fallback_hash=PASS")
    print("manuscript_source_changed=NO")
    print("supplement_content_changed=NO")
    print("science_files_changed=NONE")
    print("study_rerun=NO")
    print("publisher_facing=NO")
    print("pdf_visual_qa_required=YES")
    print_overfull_context()


if __name__ == "__main__":
    main()
