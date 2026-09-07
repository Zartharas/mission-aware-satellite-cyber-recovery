#!/usr/bin/env python3
"""Revision-4 typography builder for the balanced eight-page TAES Paper-2 candidate.

R3 preserved eight-page pagination but its five weak ``\\linebreak[2]`` hints did
not clear the two remaining overfull hboxes in the first Study-6 state-definition
paragraph. R4 deliberately starts from the cleaner R2 generated-LaTeX state and
adds exactly two strong line-break controls at natural visible separators:

after ``TRUSTED_BUILDER_COMPROMISE,`` and after ``APPROVED_BAD_SOURCE.``.

No visible manuscript character is removed, abbreviated, reordered, or changed.
No Markdown source, frozen result, reference, table value, supplement, geometry,
or publisher-facing R9 artifact is modified. ``\\sloppy`` is forbidden.
"""

from __future__ import annotations

import re
from pathlib import Path

import TAES_BUILD_10P_R3_IEEETRAN_R2 as r2

ROOT = Path(__file__).resolve().parent
OUT_TEX = ROOT / "TAES_10P_R3_MANUSCRIPT_IEEETRAN_R4_DEV.tex"
OUT_PDF = ROOT / "TAES_10P_R3_MANUSCRIPT_IEEETRAN_R4_DEV.pdf"
OUT_LOG = ROOT / "TAES_10P_R3_MANUSCRIPT_IEEETRAN_R4_DEV.log"
OUT_AUDIT = ROOT / "TAES_10P_R3_IEEETRAN_R4_BUILD_AUDIT.txt"

_STRONG_BREAKS = 0

_TARGET_1 = (
    r"\texttt{TRUSTED\_\allowbreak{}BUILDER\_\allowbreak{}COMPROMISE}, "
    r"\texttt{SOURCE\_\allowbreak{}REVIEW\_\allowbreak{}BYPASS}"
)
_REPLACEMENT_1 = (
    r"\texttt{TRUSTED\_\allowbreak{}BUILDER\_\allowbreak{}COMPROMISE},\linebreak[4] "
    r"\texttt{SOURCE\_\allowbreak{}REVIEW\_\allowbreak{}BYPASS}"
)

_TARGET_2 = (
    r"\texttt{APPROVED\_\allowbreak{}BAD\_\allowbreak{}SOURCE}. "
    r"The research-only oracle"
)
_REPLACEMENT_2 = (
    r"\texttt{APPROVED\_\allowbreak{}BAD\_\allowbreak{}SOURCE}.\linebreak[4] "
    r"The research-only oracle"
)


def _replace_once(tex: str, old: str, new: str, label: str) -> str:
    global _STRONG_BREAKS
    hits = tex.count(old)
    if hits != 1:
        raise SystemExit(
            f"ERROR: R4 strong-break marker for {label} expected one hit; found {hits}"
        )
    tex = tex.replace(old, new, 1)
    _STRONG_BREAKS += 1
    return tex


def make_tex_r4(md: str) -> str:
    global _STRONG_BREAKS
    _STRONG_BREAKS = 0

    # Start from R2: exact balanced Markdown, three common-framework math
    # conversions, and the previously validated breakable-code strategy.
    tex = r2.make_tex_r2(md)
    tex = _replace_once(
        tex,
        _TARGET_1,
        _REPLACEMENT_1,
        "after TRUSTED_BUILDER_COMPROMISE comma",
    )
    tex = _replace_once(
        tex,
        _TARGET_2,
        _REPLACEMENT_2,
        "after APPROVED_BAD_SOURCE sentence",
    )

    if _STRONG_BREAKS != 2:
        raise SystemExit(f"ERROR: expected exactly two R4 strong breaks; observed {_STRONG_BREAKS}")
    if r"\linebreak[2]" in tex:
        raise SystemExit("ERROR: R4 unexpectedly retained R3 weak linebreak hints")
    if r"\sloppy" in tex:
        raise SystemExit("ERROR: R4 unexpectedly contains \\sloppy")
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
    horizontal = "PASS" if int(result["overfull_hbox_count"]) == 0 else "REVIEW_REQUIRED"
    lines = [
        "TAES_10P_R3_IEEETRAN_R4_BUILD_AUDIT",
        f"balanced_r3_manuscript_sha256={r2.prev.EXPECTED_SHORT_MD}",
        f"frozen_r9_fallback_pdf_sha256={r2.prev.EXPECTED_FROZEN_R9_PDF}",
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
        f"horizontal_overflow_gate={horizontal}",
        f"breakable_code_tokens={r2._BREAKABLE_COUNT}",
        f"study6_strong_linebreaks={_STRONG_BREAKS}",
        "strong_linebreak_strength=4",
        "strong_linebreak_locations=AFTER_TRUSTED_BUILDER_COMPROMISE_COMMA__AFTER_APPROVED_BAD_SOURCE_SENTENCE",
        "weak_r3_linebreak_hints_retained=NO",
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
    print("TAES_10P_R3_R4_OVERFULL_CONTEXT_BEGIN")
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
                if len(text) > 300:
                    text = text[:297] + "..."
                print(f"tex_{number}={text}")
    print("TAES_10P_R3_R4_OVERFULL_CONTEXT_END")


def main() -> None:
    r2.prev.verify_r3_binding()

    # Rebind the shared audited build framework to R4 development outputs only.
    r2.prev.r1.SHORT_MD = r2.prev.SHORT_MD
    r2.prev.r1.OUT_TEX = OUT_TEX
    r2.prev.r1.OUT_PDF = OUT_PDF
    r2.prev.r1.OUT_LOG = OUT_LOG
    r2.prev.r1.OUT_AUDIT = OUT_AUDIT
    r2.prev.r1.EXPECTED_SHORT_MD = r2.prev.EXPECTED_SHORT_MD
    r2.prev.r1.verify_short_binding = r2.prev.verify_r3_binding

    base = r2.prev.r1.base
    base.MANUSCRIPT = r2.prev.SHORT_MD
    base.OUT_TEX = OUT_TEX
    base.OUT_PDF = OUT_PDF
    base.OUT_LOG = OUT_LOG
    base.OUT_AUDIT = OUT_AUDIT
    base.EXPECTED_MANUSCRIPT = r2.prev.EXPECTED_SHORT_MD
    base.TABLE_CAPTIONS = r2.prev.r1.TABLE_CAPTIONS
    base.TABLE_SPECS = r2.prev.r1.TABLE_SPECS
    base.TABLE_HEADER_KEYS = r2.prev.r1.TABLE_HEADER_KEYS
    base.verify_bindings = r2.prev.verify_r3_binding
    base.make_tex = make_tex_r4

    result = base.build_and_audit()
    write_audit(result)
    pages = int(result["pages"])

    print("TAES_10P_R3_IEEETRAN_BUILD=PASS_COMPILED_DEVELOPMENT_ONLY")
    print("TAES_10P_R3_IEEETRAN_BUILD_REVISION=4")
    print("r4_change=GENERATED_LATEX_TWO_STRONG_STUDY6_BREAKS_ONLY")
    print(f"balanced_r3_manuscript_sha256={r2.prev.EXPECTED_SHORT_MD}")
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
    print(f"breakable_code_tokens={r2._BREAKABLE_COUNT}")
    print(f"study6_strong_linebreaks={_STRONG_BREAKS}")
    print("strong_linebreak_strength=4")
    print("weak_r3_linebreak_hints_retained=NO")
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
