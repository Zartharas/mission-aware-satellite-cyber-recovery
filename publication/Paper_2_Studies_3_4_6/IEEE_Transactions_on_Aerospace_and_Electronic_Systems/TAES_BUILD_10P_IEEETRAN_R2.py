#!/usr/bin/env python3
"""Revision-2 IEEEtran pagination builder for the short TAES Paper-2 candidate.

R1 stopped before compilation because its three common-framework display-math
recognizers did not match the Pandoc LaTeX emitted by the installed toolchain.
Pandoc represents spaces inside code spans as ``\\ `` and square brackets as
``{[}`` / ``{]}``. R2 preserves the exact short-manuscript binding and all R1
layout/table behavior, changing only recognition of those three generated-LaTeX
math tokens.

No manuscript prose, supplement, frozen study, result, table value, reference,
or publisher-facing R9 artifact is modified.
"""

from __future__ import annotations

import TAES_BUILD_10P_IEEETRAN_R1 as r1


def convert_common_math_r2(tex: str) -> tuple[str, int]:
    replacements = [
        (
            r"\texttt{Q\_j(E\_j)\ in\ \{0,1\}}",
            r"\[Q_j(E_j)\in\{0,1\}\]",
            "Q_j domain",
        ),
        (
            r"\texttt{U\_j\ =\ 1{[}Q\_j(E\_j)\ =\ 1\ and\ T\_j\ =\ 0{]}}.",
            r"\[U_j = 1[Q_j(E_j)=1 \land T_j=0].\]",
            "U_j expression",
        ),
        (
            r"\texttt{C\_j\ =\ 1{[}Q\_j(E\_j)\ =\ 0\ and\ T\_j\ =\ 1{]}}.",
            r"\[C_j = 1[Q_j(E_j)=0 \land T_j=1].\]",
            "C_j expression",
        ),
    ]

    count = 0
    for old, new, label in replacements:
        hits = tex.count(old)
        if hits != 1:
            raise SystemExit(
                f"ERROR: R2 math marker for {label} expected one hit; found {hits}: {old}"
            )
        tex = tex.replace(old, new, 1)
        count += 1
    return tex, count


def page_decision(pages: int) -> str:
    if pages <= 8:
        return "BELOW_TARGET_REVIEW_RESTORE_USEFUL_DETAIL"
    if pages == 9:
        return "PREFERRED_BUFFER_TARGET"
    if pages == 10:
        return "ACCEPTABLE_NO_PRODUCTION_BUFFER"
    return "ABOVE_10_ADDITIONAL_COMPRESSION_REQUIRED"


def main() -> None:
    # Patch only the generated-LaTeX recognizer used by R1's make_short_tex.
    r1.convert_common_math = convert_common_math_r2
    r1.verify_short_binding()

    # Rebind the shared base builder only to isolated short-track paths/inputs.
    r1.base.MANUSCRIPT = r1.SHORT_MD
    r1.base.OUT_TEX = r1.OUT_TEX
    r1.base.OUT_PDF = r1.OUT_PDF
    r1.base.OUT_LOG = r1.OUT_LOG
    r1.base.OUT_AUDIT = r1.OUT_AUDIT
    r1.base.EXPECTED_MANUSCRIPT = r1.EXPECTED_SHORT_MD
    r1.base.TABLE_CAPTIONS = r1.TABLE_CAPTIONS
    r1.base.TABLE_SPECS = r1.TABLE_SPECS
    r1.base.TABLE_HEADER_KEYS = r1.TABLE_HEADER_KEYS
    r1.base.verify_bindings = r1.verify_short_binding
    r1.base.make_tex = r1.make_short_tex

    result = r1.base.build_and_audit()
    r1.write_short_audit(result)
    decision = page_decision(int(result["pages"]))

    print("TAES_10P_IEEETRAN_BUILD=PASS_COMPILED_DEVELOPMENT_ONLY")
    print("TAES_10P_IEEETRAN_BUILD_REVISION=2")
    print("r2_change=GENERATED_LATEX_COMMON_MATH_TOKEN_RECOGNITION_ONLY")
    print(f"short_manuscript_sha256={r1.EXPECTED_SHORT_MD}")
    print(f"pages={result['pages']}")
    print(f"estimated_pages_over_10={result['estimated_pages_over_10']}")
    print(f"page_target_decision={decision}")
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
    print("common_framework_display_math_conversions=3")
    print("tables_rendered=I,II,III")
    print("figure1_main_article=ABSENT_BY_SHORT_TRACK_DESIGN")
    print(f"tex={r1.OUT_TEX}")
    print(f"tex_sha256={result['tex_sha256']}")
    print(f"pdf={r1.OUT_PDF}")
    print(f"pdf_sha256={result['pdf_sha256']}")
    print(f"log={r1.OUT_LOG}")
    print(f"audit={r1.OUT_AUDIT}")
    print("science_files_changed=NONE")
    print("publisher_facing=NO")
    print("pdf_visual_qa_required=YES")


if __name__ == "__main__":
    main()
