#!/usr/bin/env python3
"""Revision-9 development builder for compressed TAES Paper 2.

Revision 9 follows the R8 pagination build. R8 reduced the manuscript from 18 to
16 IEEEtran pages but produced two overfull hboxes, both from the same compressed
Study-3 primary-endpoints sentence.

R9 changes generated LaTeX only. It inherits R8's canonical manuscript binding,
13 common-framework math conversions, R3 discretionary identifier breaks, and
three Study-6 localized emergency-stretch blocks. It then applies one localized
endpoint treatment that previously passed visual QA in R7:

1. only the first `Primary endpoints are ...` sentence is set ragged right;
2. normal IEEEtran justification resumes immediately for the following sentence;
3. the discretionary break immediately before the terminal `s` in
   `unsafe_qualified_exposure_s` is removed so that one character cannot be
   isolated on a continuation line.

No canonical Markdown prose, frozen result, citation, table, figure, population,
claim, or TAES geometry value is changed. Generated artifacts remain development
only pending fresh visual QA.
"""

from __future__ import annotations

import re

import TAES_BUILD_IEEETRAN as base
import TAES_BUILD_IEEETRAN_R8 as r8

_ENDPOINT_BLOCKS = 0


def _paragraph_parts(tex: str, marker: str, label: str) -> tuple[list[str], int]:
    parts = tex.split("\n\n")
    hits = [i for i, part in enumerate(parts) if marker in part]
    if len(hits) != 1:
        raise SystemExit(
            f"ERROR: revision-9 paragraph marker for {label} expected one hit; found {len(hits)}"
        )
    return parts, hits[0]


def _format_compressed_endpoint_sentence(tex: str) -> str:
    global _ENDPOINT_BLOCKS
    parts, idx = _paragraph_parts(
        tex,
        "Primary endpoints are",
        "compressed Study-3 primary-endpoints paragraph",
    )
    paragraph = parts[idx]

    split_marker = ". This paper emphasizes"
    if paragraph.count(split_marker) != 1:
        raise SystemExit(
            "ERROR: revision-9 endpoint paragraph sentence boundary missing or ambiguous"
        )

    first, tail = paragraph.split(split_marker, 1)
    first_sentence = first + "."
    remainder = "This paper emphasizes" + tail

    suffix_break = r"unsafe\_\allowbreak{}qualified\_\allowbreak{}exposure\_\allowbreak{}s"
    suffix_fixed = r"unsafe\_\allowbreak{}qualified\_\allowbreak{}exposure\_s"
    if first_sentence.count(suffix_break) != 1:
        raise SystemExit(
            "ERROR: revision-9 could not identify unsafe_qualified_exposure_s break pattern"
        )
    first_sentence = first_sentence.replace(suffix_break, suffix_fixed, 1)

    # Only the long endpoint-list sentence is ragged right. The explanatory
    # sentence returns immediately to ordinary IEEEtran justification.
    parts[idx] = (
        "{\\raggedright\n"
        + first_sentence
        + "\n\\par}\n"
        + "\\noindent "
        + remainder
    )
    _ENDPOINT_BLOCKS += 1
    return "\n\n".join(parts)


def make_tex_r9(md: str) -> str:
    global _ENDPOINT_BLOCKS
    _ENDPOINT_BLOCKS = 0

    tex = r8.make_tex_r8(md)
    tex = _format_compressed_endpoint_sentence(tex)

    if _ENDPOINT_BLOCKS != 1:
        raise SystemExit(
            f"ERROR: revision-9 expected one endpoint typography block; observed {_ENDPOINT_BLOCKS}"
        )
    if r"\sloppy" in tex:
        raise SystemExit("ERROR: revision-9 unexpectedly contains \\sloppy")
    if r"\linebreak[2]" in tex:
        raise SystemExit("ERROR: revision-9 unexpectedly contains retired linebreak hints")
    return tex


def print_overfull_context() -> None:
    if not base.OUT_LOG.is_file() or not base.OUT_TEX.is_file():
        return
    log = base.OUT_LOG.read_text(encoding="utf-8", errors="replace")
    tex_lines = base.OUT_TEX.read_text(encoding="utf-8", errors="replace").splitlines()
    pattern = re.compile(
        r"Overfull \\hbox \(([0-9.]+)pt too wide\) in paragraph at lines (\d+)--(\d+)"
    )
    matches = list(pattern.finditer(log))
    print("TAES_IEEETRAN_R9_OVERFULL_CONTEXT_BEGIN")
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
            lo = max(1, start - 1)
            hi = min(len(tex_lines), end + 1)
            print(f"overflow_pt={width} lines={start}--{end}")
            for number in range(lo, hi + 1):
                text = tex_lines[number - 1].strip()
                if len(text) > 260:
                    text = text[:257] + "..."
                print(f"tex_{number}={text}")
    print("TAES_IEEETRAN_R9_OVERFULL_CONTEXT_END")


def write_audit(result: dict[str, str | int | float | bool]) -> None:
    layout_clean = (
        result["overfull_hbox_count"] == 0
        and result["overfull_vbox_count"] == 0
        and result["font_embedding_all_yes"] is True
    )
    audit_lines = [
        "TAES_IEEETRAN_BUILD_AUDIT",
        f"canonical_manuscript_sha256={r8.EXPECTED_COMPRESSED_MANUSCRIPT}",
        f"canonical_manuscript_tracking_commit={r8.EXPECTED_MANUSCRIPT_TRACKING_COMMIT}",
        f"figure1_pdf_sha256={base.EXPECTED_FIG_PDF}",
        f"figure1_png_sha256={base.EXPECTED_FIG_PNG}",
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
        "author_submission_authorization=GRANTED_2026-09-06",
        "effective_submission_authorization=NO_PENDING_REMAINING_GATES",
    ]
    base.OUT_AUDIT.write_text("\n".join(audit_lines) + "\n", encoding="utf-8")


def main() -> None:
    r8.verify_manuscript_tracking_commit()
    base.EXPECTED_MANUSCRIPT = r8.EXPECTED_COMPRESSED_MANUSCRIPT
    base.make_tex = make_tex_r9

    result = base.build_and_audit()
    write_audit(result)

    layout_clean = (
        result["overfull_hbox_count"] == 0
        and result["overfull_vbox_count"] == 0
        and result["font_embedding_all_yes"] is True
    )

    print("TAES_IEEETRAN_BUILD=PASS_COMPILED_DEVELOPMENT_ONLY")
    print("TAES_IEEETRAN_BUILD_REVISION=9")
    print("r9_base=R8_COMPRESSED_WITH_LOCAL_ENDPOINT_TYPOGRAPHY_FIX")
    print(f"canonical_manuscript_sha256={r8.EXPECTED_COMPRESSED_MANUSCRIPT}")
    print(f"canonical_manuscript_tracking_commit={r8.EXPECTED_MANUSCRIPT_TRACKING_COMMIT}")
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
    print(f"common_framework_math_conversions={r8._MATH_CONVERSIONS}")
    print("common_framework_math_typesetting=LATEX_MATH")
    print(f"endpoint_raggedright_blocks={_ENDPOINT_BLOCKS}")
    print("endpoint_terminal_s_break=SUPPRESSED")
    print(f"preserved_study6_emergencystretch_blocks={r8._LOCALIZED_STUDY6_BLOCKS}")
    print(f"gate_list_emergencystretch={r8._GATE_LIST_STRETCH}")
    print(f"g1_emergencystretch={r8._G1_STRETCH}")
    print(f"assurance_emergencystretch={r8._ASSURANCE_STRETCH}")
    print("localized_sloppy_blocks=0")
    print("global_geometry_changed=NO")
    print("science_or_manuscript_source_changed=NO")
    print(f"tex={base.OUT_TEX}")
    print(f"tex_sha256={result['tex_sha256']}")
    print(f"pdf={base.OUT_PDF}")
    print(f"pdf_sha256={result['pdf_sha256']}")
    print(f"log={base.OUT_LOG}")
    print(f"audit={base.OUT_AUDIT}")
    print("publisher_facing=NO")
    print("pdf_visual_qa_required=YES")
    print("author_submission_authorization=GRANTED_2026-09-06")
    print("effective_submission_authorization=NO_PENDING_REMAINING_GATES")
    print_overfull_context()


if __name__ == "__main__":
    main()
