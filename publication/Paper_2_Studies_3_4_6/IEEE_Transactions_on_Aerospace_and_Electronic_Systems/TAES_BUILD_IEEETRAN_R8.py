#!/usr/bin/env python3
"""Revision-8 development builder for compressed TAES Paper 2.

Revision 8 is the first IEEEtran build bound to the canonically tracked Pass-2
R2 manuscript at commit 710a72af05fb418a0d82a659198a677b9e2a8948 and SHA-256
802e6658e9e1325ec4f4a785c5da1b3856fbfadb950dadb6f6a57aec0acacd48.

The compressed manuscript changed Sections IV, V, and IX only. R8 therefore
retains generated-LaTeX treatments that remain structurally applicable:

1. revision-3 discretionary breaks inside simple monospaced identifiers;
2. revision-5's 13 common-framework math conversions; and
3. the three Study-6 localized emergency-stretch blocks that passed the R7
   visual QA.

The R7 Study-3 endpoint ragged-right workaround is intentionally retired because
the compressed Section IV no longer contains the old endpoint sentence and must
be typeset naturally before any new intervention is considered.

No canonical Markdown prose, frozen study evidence, result, citation, table,
figure, population, or TAES geometry value is changed. Generated artifacts remain
development-only and require a fresh visual QA before publisher-facing freeze.
"""

from __future__ import annotations

import re
import subprocess

import TAES_BUILD_IEEETRAN as base
import TAES_BUILD_IEEETRAN_R3 as r3
import TAES_BUILD_IEEETRAN_R5 as r5
import TAES_BUILD_IEEETRAN_R7 as r7

EXPECTED_COMPRESSED_MANUSCRIPT = "802e6658e9e1325ec4f4a785c5da1b3856fbfadb950dadb6f6a57aec0acacd48"
EXPECTED_MANUSCRIPT_TRACKING_COMMIT = "710a72af05fb418a0d82a659198a677b9e2a8948"

_GATE_LIST_STRETCH = "0.60em"
_G1_STRETCH = "0.90em"
_ASSURANCE_STRETCH = "1.20em"
_LOCALIZED_STUDY6_BLOCKS = 0
_MATH_CONVERSIONS = 0


def verify_manuscript_tracking_commit() -> None:
    rel = base.MANUSCRIPT.relative_to(base.ROOT).as_posix()
    proc = subprocess.run(
        ["git", "log", "-1", "--format=%H", "--", rel],
        cwd=base.ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if proc.returncode != 0:
        raise SystemExit("ERROR: unable to resolve manuscript tracking commit:\n" + proc.stdout)
    observed = proc.stdout.strip()
    if observed != EXPECTED_MANUSCRIPT_TRACKING_COMMIT:
        raise SystemExit(
            "ERROR: compressed manuscript tracking commit mismatch: "
            f"expected={EXPECTED_MANUSCRIPT_TRACKING_COMMIT} observed={observed}"
        )


def make_tex_r8(md: str) -> str:
    global _LOCALIZED_STUDY6_BLOCKS, _MATH_CONVERSIONS
    _LOCALIZED_STUDY6_BLOCKS = 0

    # Start from R3 only. R5's targeted linebreak experiment and R7's retired
    # Study-3 endpoint block are deliberately not inherited.
    tex = r3.make_tex_r3(md)
    tex = r5._convert_common_framework_math(tex)
    _MATH_CONVERSIONS = r5._MATH_CONVERSIONS

    if _MATH_CONVERSIONS != 13:
        raise SystemExit(
            f"ERROR: revision-8 expected 13 common-framework math conversions; observed {_MATH_CONVERSIONS}"
        )
    if r"\sloppy" in tex:
        raise SystemExit("ERROR: revision-8 unexpectedly inherited \\sloppy")
    if r"\linebreak[2]" in tex:
        raise SystemExit("ERROR: revision-8 unexpectedly inherited revision-5 linebreak hints")

    # The compressed Section IV no longer needs or matches R7's endpoint block.
    if "The frozen primary endpoints are" in tex:
        raise SystemExit("ERROR: revision-8 unexpectedly contains retired Study-3 endpoint sentence")

    # Preserve only the three R6/R7 Study-6 local treatments that already passed
    # visual QA and whose manuscript source remained byte-identical in Pass-2 R2.
    r7._LOCALIZED_STUDY6_BLOCKS = 0
    tex = r7._wrap_unique_itemize(
        tex,
        r"G4\_\allowbreak{}PROVENANCE\_\allowbreak{}SOURCE\_\allowbreak{}REVIEW",
        "Study 6 gate-definition list",
        _GATE_LIST_STRETCH,
    )
    tex = r7._wrap_unique_paragraph(
        tex,
        "adds independent target-digest match",
        "Study 6 G1 target-digest paragraph",
        _G1_STRETCH,
    )
    tex = r7._wrap_unique_paragraph(
        tex,
        "The six assurance signals are also modeled Boolean variables.",
        "Study 6 assurance-signal limitations paragraph",
        _ASSURANCE_STRETCH,
    )
    _LOCALIZED_STUDY6_BLOCKS = r7._LOCALIZED_STUDY6_BLOCKS
    if _LOCALIZED_STUDY6_BLOCKS != 3:
        raise SystemExit(
            "ERROR: revision-8 expected three preserved Study-6 stretch blocks; "
            f"observed {_LOCALIZED_STUDY6_BLOCKS}"
        )
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
    print("TAES_IEEETRAN_R8_OVERFULL_CONTEXT_BEGIN")
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
    print("TAES_IEEETRAN_R8_OVERFULL_CONTEXT_END")


def write_audit(result: dict[str, str | int | float | bool]) -> None:
    layout_clean = (
        result["overfull_hbox_count"] == 0
        and result["overfull_vbox_count"] == 0
        and result["font_embedding_all_yes"] is True
    )
    audit_lines = [
        "TAES_IEEETRAN_BUILD_AUDIT",
        f"canonical_manuscript_sha256={EXPECTED_COMPRESSED_MANUSCRIPT}",
        f"canonical_manuscript_tracking_commit={EXPECTED_MANUSCRIPT_TRACKING_COMMIT}",
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
    verify_manuscript_tracking_commit()
    base.EXPECTED_MANUSCRIPT = EXPECTED_COMPRESSED_MANUSCRIPT
    base.make_tex = make_tex_r8

    result = base.build_and_audit()
    write_audit(result)

    layout_clean = (
        result["overfull_hbox_count"] == 0
        and result["overfull_vbox_count"] == 0
        and result["font_embedding_all_yes"] is True
    )

    print("TAES_IEEETRAN_BUILD=PASS_COMPILED_DEVELOPMENT_ONLY")
    print("TAES_IEEETRAN_BUILD_REVISION=8")
    print("r8_input=CANONICAL_PASS2_R2_COMPRESSED_MANUSCRIPT")
    print(f"canonical_manuscript_sha256={EXPECTED_COMPRESSED_MANUSCRIPT}")
    print(f"canonical_manuscript_tracking_commit={EXPECTED_MANUSCRIPT_TRACKING_COMMIT}")
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
    print(f"common_framework_math_conversions={_MATH_CONVERSIONS}")
    print("common_framework_math_typesetting=LATEX_MATH")
    print("retired_study3_endpoint_raggedright_blocks=1")
    print(f"preserved_study6_emergencystretch_blocks={_LOCALIZED_STUDY6_BLOCKS}")
    print(f"gate_list_emergencystretch={_GATE_LIST_STRETCH}")
    print(f"g1_emergencystretch={_G1_STRETCH}")
    print(f"assurance_emergencystretch={_ASSURANCE_STRETCH}")
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
