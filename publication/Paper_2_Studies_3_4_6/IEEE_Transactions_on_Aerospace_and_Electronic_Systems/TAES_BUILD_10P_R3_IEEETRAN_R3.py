#!/usr/bin/env python3
"""Revision-3 typography builder for the balanced eight-page TAES Paper-2 candidate.

R2 reduced the horizontal overflow count from four to two by making simple
monospaced identifiers breakable. Both remaining hboxes occur in the same first
Study-6 state-definition paragraph. R3 preserves the exact balanced-R3 Markdown
source and all R2 behavior, then adds targeted generated-LaTeX line-break
incentives at natural separators in that one paragraph.

No visible manuscript character is removed, abbreviated, or changed. No
manuscript prose, frozen result, table value, supplement, geometry setting, or
publisher-facing R9 artifact is modified. ``\\sloppy`` remains forbidden.
"""

from __future__ import annotations

import re
from pathlib import Path

import TAES_BUILD_10P_R3_IEEETRAN_R1 as base_r3
import TAES_BUILD_10P_R3_IEEETRAN_R2 as prev
import TAES_BUILD_10P_IEEETRAN_R2 as short_math

ROOT = Path(__file__).resolve().parent
OUT_TEX = ROOT / "TAES_10P_R3_MANUSCRIPT_IEEETRAN_R3_DEV.tex"
OUT_PDF = ROOT / "TAES_10P_R3_MANUSCRIPT_IEEETRAN_R3_DEV.pdf"
OUT_LOG = ROOT / "TAES_10P_R3_MANUSCRIPT_IEEETRAN_R3_DEV.log"
OUT_AUDIT = ROOT / "TAES_10P_R3_IEEETRAN_R3_BUILD_AUDIT.txt"

_TARGET_HINTS = 0


def _study6_intro_with_hints(tex: str) -> str:
    global _TARGET_HINTS
    _TARGET_HINTS = 0

    parts = tex.split("\n\n")
    hits = [
        i for i, part in enumerate(parts)
        if "Study 6 (" in part
        and "five prespecified states are objectively incorrect" in part
        and "objective" in part
        and "baseline" in part
        and "correct" in part
    ]
    if len(hits) != 1:
        raise SystemExit(
            "ERROR: R3 Study-6 introductory paragraph expected one hit; "
            f"found {len(hits)}"
        )

    idx = hits[0]
    paragraph = parts[idx]

    replacements = [
        (
            r"\texttt{POST\_\allowbreak{}RELEASE\_\allowbreak{}TAMPER}, \texttt{TRUSTED\_\allowbreak{}SIGNER\_\allowbreak{}COMPROMISE}",
            r"\texttt{POST\_\allowbreak{}RELEASE\_\allowbreak{}TAMPER},\linebreak[2] \texttt{TRUSTED\_\allowbreak{}SIGNER\_\allowbreak{}COMPROMISE}",
            "after POST_RELEASE_TAMPER",
        ),
        (
            r"\texttt{TRUSTED\_\allowbreak{}SIGNER\_\allowbreak{}COMPROMISE}, \texttt{TRUSTED\_\allowbreak{}BUILDER\_\allowbreak{}COMPROMISE}",
            r"\texttt{TRUSTED\_\allowbreak{}SIGNER\_\allowbreak{}COMPROMISE},\linebreak[2] \texttt{TRUSTED\_\allowbreak{}BUILDER\_\allowbreak{}COMPROMISE}",
            "after TRUSTED_SIGNER_COMPROMISE",
        ),
        (
            r"\texttt{TRUSTED\_\allowbreak{}BUILDER\_\allowbreak{}COMPROMISE}, \texttt{SOURCE\_\allowbreak{}REVIEW\_\allowbreak{}BYPASS}",
            r"\texttt{TRUSTED\_\allowbreak{}BUILDER\_\allowbreak{}COMPROMISE},\linebreak[2] \texttt{SOURCE\_\allowbreak{}REVIEW\_\allowbreak{}BYPASS}",
            "after TRUSTED_BUILDER_COMPROMISE",
        ),
        (
            r"\texttt{SOURCE\_\allowbreak{}REVIEW\_\allowbreak{}BYPASS}, and \texttt{APPROVED\_\allowbreak{}BAD\_\allowbreak{}SOURCE}",
            r"\texttt{SOURCE\_\allowbreak{}REVIEW\_\allowbreak{}BYPASS},\linebreak[2] and \texttt{APPROVED\_\allowbreak{}BAD\_\allowbreak{}SOURCE}",
            "after SOURCE_REVIEW_BYPASS",
        ),
        (
            r"\texttt{APPROVED\_\allowbreak{}BAD\_\allowbreak{}SOURCE}. The research-only oracle",
            r"\texttt{APPROVED\_\allowbreak{}BAD\_\allowbreak{}SOURCE}.\linebreak[2] The research-only oracle",
            "before research-only oracle sentence",
        ),
    ]

    for old, new, label in replacements:
        count = paragraph.count(old)
        if count != 1:
            raise SystemExit(
                f"ERROR: R3 Study-6 linebreak marker {label} expected one hit; found {count}"
            )
        paragraph = paragraph.replace(old, new, 1)
        _TARGET_HINTS += 1

    parts[idx] = paragraph
    return "\n\n".join(parts)


def make_tex_r3(md: str) -> str:
    tex = prev.make_tex_r2(md)
    tex = _study6_intro_with_hints(tex)

    if _TARGET_HINTS != 5:
        raise SystemExit(
            f"ERROR: R3 expected five Study-6 linebreak hints; observed {_TARGET_HINTS}"
        )
    if r"\sloppy" in tex:
        raise SystemExit("ERROR: balanced R3 R3 unexpectedly contains \\sloppy")
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
        "TAES_10P_R3_IEEETRAN_R3_BUILD_AUDIT",
        f"balanced_r3_manuscript_sha256={base_r3.EXPECTED_SHORT_MD}",
        f"frozen_r9_fallback_pdf_sha256={base_r3.EXPECTED_FROZEN_R9_PDF}",
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
        f"breakable_code_tokens={prev._BREAKABLE_COUNT}",
        f"study6_separator_linebreak_hints={_TARGET_HINTS}",
        "linebreak_hint_strength=2",
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
    print("TAES_10P_R3_R3_OVERFULL_CONTEXT_BEGIN")
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
    print("TAES_10P_R3_R3_OVERFULL_CONTEXT_END")


def main() -> None:
    base_r3.verify_r3_binding()

    base_r3.r1.SHORT_MD = base_r3.SHORT_MD
    base_r3.r1.OUT_TEX = OUT_TEX
    base_r3.r1.OUT_PDF = OUT_PDF
    base_r3.r1.OUT_LOG = OUT_LOG
    base_r3.r1.OUT_AUDIT = OUT_AUDIT
    base_r3.r1.EXPECTED_SHORT_MD = base_r3.EXPECTED_SHORT_MD
    base_r3.r1.convert_common_math = short_math.convert_common_math_r2
    base_r3.r1.verify_short_binding = base_r3.verify_r3_binding

    base_r3.r1.base.MANUSCRIPT = base_r3.SHORT_MD
    base_r3.r1.base.OUT_TEX = OUT_TEX
    base_r3.r1.base.OUT_PDF = OUT_PDF
    base_r3.r1.base.OUT_LOG = OUT_LOG
    base_r3.r1.base.OUT_AUDIT = OUT_AUDIT
    base_r3.r1.base.EXPECTED_MANUSCRIPT = base_r3.EXPECTED_SHORT_MD
    base_r3.r1.base.TABLE_CAPTIONS = base_r3.r1.TABLE_CAPTIONS
    base_r3.r1.base.TABLE_SPECS = base_r3.r1.TABLE_SPECS
    base_r3.r1.base.TABLE_HEADER_KEYS = base_r3.r1.TABLE_HEADER_KEYS
    base_r3.r1.base.verify_bindings = base_r3.verify_r3_binding
    base_r3.r1.base.make_tex = make_tex_r3

    result = base_r3.r1.base.build_and_audit()
    write_audit(result)
    pages = int(result["pages"])

    print("TAES_10P_R3_IEEETRAN_BUILD=PASS_COMPILED_DEVELOPMENT_ONLY")
    print("TAES_10P_R3_IEEETRAN_BUILD_REVISION=3")
    print("r3_change=GENERATED_LATEX_STUDY6_SEPARATOR_LINEBREAK_HINTS_ONLY")
    print(f"balanced_r3_manuscript_sha256={base_r3.EXPECTED_SHORT_MD}")
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
    print(f"breakable_code_tokens={prev._BREAKABLE_COUNT}")
    print(f"study6_separator_linebreak_hints={_TARGET_HINTS}")
    print("linebreak_hint_strength=2")
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
