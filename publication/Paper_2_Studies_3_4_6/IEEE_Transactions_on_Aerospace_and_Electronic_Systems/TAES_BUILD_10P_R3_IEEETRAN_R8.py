#!/usr/bin/env python3
"""Revision-8 typography builder for the balanced eight-page TAES Paper-2 candidate.

R7 cleared all horizontal overflow but visual QA found that its one localized
``\\raggedright`` Study-6 paragraph was visibly inconsistent with the otherwise
fully justified IEEE body text. R8 starts again from the validated R2
breakable-identifier TeX and applies only a localized ``\\emergencystretch=2em``
group to the unique first Study-6 state-definition paragraph.

The paragraph therefore remains justified. No visible manuscript character,
canonical Markdown prose, frozen result, table value, reference, supplement,
geometry setting, or publisher-facing R9 artifact is changed. ``\\sloppy`` and
forced ``\\linebreak`` hints are forbidden, and R8 must not add any new
``\\raggedright`` command.
"""

from __future__ import annotations

import re
from pathlib import Path

import TAES_BUILD_10P_R3_IEEETRAN_R1 as core
import TAES_BUILD_10P_R3_IEEETRAN_R2 as typo2

ROOT = Path(__file__).resolve().parent
OUT_TEX = ROOT / "TAES_10P_R3_MANUSCRIPT_IEEETRAN_R8_DEV.tex"
OUT_PDF = ROOT / "TAES_10P_R3_MANUSCRIPT_IEEETRAN_R8_DEV.pdf"
OUT_LOG = ROOT / "TAES_10P_R3_MANUSCRIPT_IEEETRAN_R8_DEV.log"
OUT_AUDIT = ROOT / "TAES_10P_R3_IEEETRAN_R8_BUILD_AUDIT.txt"

_LOCALIZED_EMERGENCYSTRETCH_BLOCKS = 0
_PREEXISTING_RAGGEDRIGHT_COUNT = 0
_FINAL_RAGGEDRIGHT_COUNT = 0

_STUDY6_WRAPPER_PREFIX = "\\begingroup\\emergencystretch=2em\\relax\nStudy 6 ("


def _localize_study6_first_paragraph(tex: str) -> str:
    global _LOCALIZED_EMERGENCYSTRETCH_BLOCKS
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
            "ERROR: R8 expected exactly one first Study-6 state-definition paragraph; "
            f"found {len(hits)}"
        )
    idx = hits[0]
    paragraph = parts[idx]
    if r"\sloppy" in paragraph or r"\raggedright" in paragraph or r"\emergencystretch" in paragraph:
        raise SystemExit("ERROR: R8 target paragraph already contains local layout treatment")
    parts[idx] = "\\begingroup\\emergencystretch=2em\\relax\n" + paragraph + "\\par\\endgroup"
    _LOCALIZED_EMERGENCYSTRETCH_BLOCKS = 1
    return "\n\n".join(parts)


def make_tex_r8(md: str) -> str:
    global _PREEXISTING_RAGGEDRIGHT_COUNT, _FINAL_RAGGEDRIGHT_COUNT

    tex = typo2.make_tex_r2(md)
    _PREEXISTING_RAGGEDRIGHT_COUNT = tex.count(r"\raggedright")

    tex = _localize_study6_first_paragraph(tex)
    _FINAL_RAGGEDRIGHT_COUNT = tex.count(r"\raggedright")

    if r"\sloppy" in tex:
        raise SystemExit("ERROR: R8 unexpectedly contains \\sloppy")
    if re.search(r"\\linebreak\[[24]\]", tex):
        raise SystemExit("ERROR: R8 unexpectedly contains a forced linebreak hint")
    if _FINAL_RAGGEDRIGHT_COUNT != _PREEXISTING_RAGGEDRIGHT_COUNT:
        raise SystemExit(
            "ERROR: R8 must not add raggedright commands: "
            f"before={_PREEXISTING_RAGGEDRIGHT_COUNT} after={_FINAL_RAGGEDRIGHT_COUNT}"
        )

    wrapper_hits = tex.count(_STUDY6_WRAPPER_PREFIX)
    if wrapper_hits != 1:
        raise SystemExit(
            "ERROR: R8 expected exactly one structural Study-6 emergencystretch wrapper; "
            f"found {wrapper_hits}"
        )
    if _LOCALIZED_EMERGENCYSTRETCH_BLOCKS != 1:
        raise SystemExit(
            "ERROR: R8 emergencystretch block counter is not one: "
            f"{_LOCALIZED_EMERGENCYSTRETCH_BLOCKS}"
        )
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
    hboxes = int(result["overfull_hbox_count"])
    lines = [
        "TAES_10P_R3_IEEETRAN_R8_BUILD_AUDIT",
        f"balanced_r3_manuscript_sha256={core.EXPECTED_SHORT_MD}",
        f"frozen_r9_fallback_pdf_sha256={core.EXPECTED_FROZEN_R9_PDF}",
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
        f"overfull_hbox_count={hboxes}",
        f"overfull_vbox_count={result['overfull_vbox_count']}",
        f"underfull_hbox_count={result['underfull_hbox_count']}",
        f"underfull_vbox_count={result['underfull_vbox_count']}",
        f"latex_warning_count={result['latex_warning_count']}",
        f"font_count={result['font_count']}",
        f"font_embedding_all_yes={'PASS' if result['font_embedding_all_yes'] else 'FAIL'}",
        f"horizontal_overflow_gate={'PASS' if hboxes == 0 else 'REVIEW_REQUIRED'}",
        f"breakable_code_tokens={typo2._BREAKABLE_COUNT}",
        "breakable_code_strategy=TEXTTT_EXPLICIT_DISCRETIONARY_BREAKS",
        f"preexisting_raggedright_count={_PREEXISTING_RAGGEDRIGHT_COUNT}",
        f"final_raggedright_count={_FINAL_RAGGEDRIGHT_COUNT}",
        f"localized_emergencystretch_blocks={_LOCALIZED_EMERGENCYSTRETCH_BLOCKS}",
        "localized_emergencystretch_scope=FIRST_STUDY6_STATE_DEFINITION_PARAGRAPH_ONLY",
        "localized_emergencystretch_value=2em",
        "localized_raggedright_blocks_added=0",
        "localized_sloppy_blocks=0",
        "forced_linebreak_hints=0",
        "common_framework_display_math_conversions=3",
        "tables_rendered=I,II,III",
        "figure1_main_article=ABSENT_BY_SHORT_TRACK_DESIGN",
        "global_geometry_changed=NO",
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
    print("TAES_10P_R3_R8_OVERFULL_CONTEXT_BEGIN")
    if not matches:
        print("NONE")
    else:
        for match in matches:
            width = match.group(1)
            start = int(match.group(2))
            end = int(match.group(3))
            print(f"overflow_pt={width} lines={start}--{end}")
            lo = max(1, start - 1)
            hi = min(len(tex_lines), end + 1)
            for number in range(lo, hi + 1):
                text = tex_lines[number - 1].strip()
                if len(text) > 280:
                    text = text[:277] + "..."
                print(f"tex_{number}={text}")
    print("TAES_10P_R3_R8_OVERFULL_CONTEXT_END")


def main() -> None:
    core.verify_r3_binding()

    core.r1.SHORT_MD = core.SHORT_MD
    core.r1.OUT_TEX = OUT_TEX
    core.r1.OUT_PDF = OUT_PDF
    core.r1.OUT_LOG = OUT_LOG
    core.r1.OUT_AUDIT = OUT_AUDIT
    core.r1.EXPECTED_SHORT_MD = core.EXPECTED_SHORT_MD
    core.r1.verify_short_binding = core.verify_r3_binding

    core.r1.base.MANUSCRIPT = core.SHORT_MD
    core.r1.base.OUT_TEX = OUT_TEX
    core.r1.base.OUT_PDF = OUT_PDF
    core.r1.base.OUT_LOG = OUT_LOG
    core.r1.base.OUT_AUDIT = OUT_AUDIT
    core.r1.base.EXPECTED_MANUSCRIPT = core.EXPECTED_SHORT_MD
    core.r1.base.TABLE_CAPTIONS = core.r1.TABLE_CAPTIONS
    core.r1.base.TABLE_SPECS = core.r1.TABLE_SPECS
    core.r1.base.TABLE_HEADER_KEYS = core.r1.TABLE_HEADER_KEYS
    core.r1.base.verify_bindings = core.verify_r3_binding
    core.r1.base.make_tex = make_tex_r8

    result = core.r1.base.build_and_audit()
    write_audit(result)
    pages = int(result["pages"])

    print("TAES_10P_R3_IEEETRAN_BUILD=PASS_COMPILED_DEVELOPMENT_ONLY")
    print("TAES_10P_R3_IEEETRAN_BUILD_REVISION=8")
    print("r8_change=R7_RAGGEDRIGHT_REPLACED_BY_LOCAL_JUSTIFIED_EMERGENCYSTRETCH")
    print(f"balanced_r3_manuscript_sha256={core.EXPECTED_SHORT_MD}")
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
    print(f"breakable_code_tokens={typo2._BREAKABLE_COUNT}")
    print(f"preexisting_raggedright_count={_PREEXISTING_RAGGEDRIGHT_COUNT}")
    print(f"final_raggedright_count={_FINAL_RAGGEDRIGHT_COUNT}")
    print(f"localized_emergencystretch_blocks={_LOCALIZED_EMERGENCYSTRETCH_BLOCKS}")
    print("localized_emergencystretch_scope=FIRST_STUDY6_STATE_DEFINITION_PARAGRAPH_ONLY")
    print("localized_emergencystretch_value=2em")
    print("localized_raggedright_blocks_added=0")
    print("localized_sloppy_blocks=0")
    print("forced_linebreak_hints=0")
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
