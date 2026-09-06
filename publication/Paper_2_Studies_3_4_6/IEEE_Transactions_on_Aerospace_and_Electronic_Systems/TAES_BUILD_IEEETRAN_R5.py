#!/usr/bin/env python3
"""Revision-5 development builder for TAES Paper 2.

Revision 5 responds to the page-by-page R4 visual audit. It deliberately starts
from revision 3 rather than revision 4, so the localized ``\\sloppy`` blocks are
not retained.

It makes two generated-LaTeX-only formatting corrections:

1. selected common-framework variables and four displayed logical expressions
   are rendered as mathematical notation instead of monospaced ASCII; and
2. the four R3 horizontal-overflow locations receive targeted invisible
   ``\\linebreak[2]`` incentives at natural separator points rather than relaxed
   paragraph justification.

No canonical Markdown prose is edited. No visible identifier characters are
removed or abbreviated. No table row, figure content, frozen result, citation,
limitation, population, or TAES geometry value is changed. Generated artifacts
remain development-only pending another full PDF visual QA.
"""

from __future__ import annotations

import re

import TAES_BUILD_IEEETRAN as base
import TAES_BUILD_IEEETRAN_R3 as r3

_MATH_CONVERSIONS = 0
_TARGETED_BREAKS = 0


def _replace_once(tex: str, old: str, new: str, label: str) -> str:
    global _MATH_CONVERSIONS
    count = tex.count(old)
    if count != 1:
        raise SystemExit(
            f"ERROR: revision-5 math marker for {label} expected one hit; found {count}"
        )
    _MATH_CONVERSIONS += 1
    return tex.replace(old, new, 1)


def _convert_common_framework_math(tex: str) -> str:
    global _MATH_CONVERSIONS
    _MATH_CONVERSIONS = 0

    replacements = [
        (
            r"For study \texttt{j}, let \texttt{E\_\allowbreak{}j} denote",
            r"For study \(j\), let \(E_j\) denote",
            "study j and E_j",
        ),
        (
            r"\texttt{Q\_j(E\_j)\ in\ \{0,1\}}",
            r"\[Q_j(E_j)\in\{0,1\}\]",
            "Q_j domain",
        ),
        (
            r"Let \texttt{T\_j\ in\ \{0,1\}} denote",
            r"Let \(T_j\in\{0,1\}\) denote",
            "T_j domain",
        ),
        (
            r"\texttt{T\_\allowbreak{}j} is used only for evaluation and is never supplied to \texttt{Q\_\allowbreak{}j}.",
            r"\(T_j\) is used only for evaluation and is never supplied to \(Q_j\).",
            "T_j Q_j prose",
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
        (
            r"\texttt{Q\_\allowbreak{}3}",
            r"\(Q_3\)",
            "Q_3",
        ),
        (
            r"\texttt{T\_\allowbreak{}3}",
            r"\(T_3\)",
            "T_3",
        ),
        (
            r"\texttt{Q\_\allowbreak{}4}",
            r"\(Q_4\)",
            "Q_4",
        ),
        (
            r"\texttt{T\_\allowbreak{}4}",
            r"\(T_4\)",
            "T_4",
        ),
        (
            r"\texttt{Q\_\allowbreak{}6}",
            r"\(Q_6\)",
            "Q_6",
        ),
        (
            r"\texttt{T\_\allowbreak{}6}",
            r"\(T_6\)",
            "T_6",
        ),
        (
            r"No pooled Paper-2 \texttt{N}, success rate",
            r"No pooled Paper-2 \(N\), success rate",
            "Paper-2 N",
        ),
    ]

    for old, new, label in replacements:
        tex = _replace_once(tex, old, new, label)
    return tex


def _paragraph_index(tex: str, marker: str, label: str) -> tuple[list[str], int]:
    parts = tex.split("\n\n")
    hits = [i for i, part in enumerate(parts) if marker in part]
    if len(hits) != 1:
        raise SystemExit(
            f"ERROR: revision-5 paragraph marker for {label} expected one hit; found {len(hits)}"
        )
    return parts, hits[0]


def _replace_in_unique_paragraph(
    tex: str,
    marker: str,
    replacements: list[tuple[str, str]],
    label: str,
) -> str:
    global _TARGETED_BREAKS
    parts, idx = _paragraph_index(tex, marker, label)
    paragraph = parts[idx]
    for old, new in replacements:
        count = paragraph.count(old)
        if count != 1:
            raise SystemExit(
                f"ERROR: revision-5 targeted-break marker in {label} expected one hit; found {count}: {old}"
            )
        paragraph = paragraph.replace(old, new, 1)
        _TARGETED_BREAKS += new.count(r"\linebreak[2]") - old.count(r"\linebreak[2]")
    parts[idx] = paragraph
    return "\n\n".join(parts)


def _target_endpoint_paragraph(tex: str) -> str:
    parts, idx = _paragraph_index(
        tex,
        "The frozen primary endpoints are",
        "Study 3 frozen-primary-endpoints paragraph",
    )
    paragraph = parts[idx]
    # Six endpoints are joined by four comma-only separators plus one final
    # comma-and separator. Encourage breaks only between endpoint tokens. The
    # endpoint strings, punctuation, and conjunction remain visibly unchanged.
    comma_sep = r"}, \texttt{"
    final_sep = r"}, and \texttt{"
    comma_hits = paragraph.count(comma_sep)
    final_hits = paragraph.count(final_sep)
    if comma_hits != 4 or final_hits != 1:
        raise SystemExit(
            "ERROR: revision-5 endpoint separator structure mismatch: "
            f"comma_only={comma_hits} final_and={final_hits}; expected 4 and 1"
        )
    paragraph = paragraph.replace(comma_sep, r"},\linebreak[2] \texttt{")
    paragraph = paragraph.replace(final_sep, r"},\linebreak[2] and \texttt{", 1)
    global _TARGETED_BREAKS
    _TARGETED_BREAKS += comma_hits + final_hits
    parts[idx] = paragraph
    return "\n\n".join(parts)


def _target_gate_itemize(tex: str) -> str:
    global _TARGETED_BREAKS
    pattern = re.compile(r"\\begin\{itemize\}.*?\\end\{itemize\}", re.DOTALL)
    matches = list(pattern.finditer(tex))
    marker = r"G4\_\allowbreak{}PROVENANCE\_\allowbreak{}SOURCE\_\allowbreak{}REVIEW"
    hits = [m for m in matches if marker in m.group(0)]
    if len(hits) != 1:
        raise SystemExit(
            f"ERROR: revision-5 Study-6 gate itemize expected one hit; found {len(hits)}"
        )
    hit = hits[0]
    block = hit.group(0)
    old = marker + r"}: signature, provenance, and source-review attestation;"
    new = marker + r"}:\linebreak[2] signature, provenance, and source-review attestation;"
    if block.count(old) != 1:
        raise SystemExit("ERROR: revision-5 G4 gate-definition insertion marker missing")
    block = block.replace(old, new, 1)
    _TARGETED_BREAKS += 1
    return tex[: hit.start()] + block + tex[hit.end() :]


def _target_g1_paragraph(tex: str) -> str:
    return _replace_in_unique_paragraph(
        tex,
        "adds independent target-digest match",
        [
            (
                r"reducing unsafe qualification to three states: \texttt{TRUSTED\_\allowbreak{}BUILDER\_\allowbreak{}COMPROMISE}",
                r"reducing unsafe qualification to three states:\linebreak[2] \texttt{TRUSTED\_\allowbreak{}BUILDER\_\allowbreak{}COMPROMISE}",
            ),
            (
                r"}, \texttt{SOURCE\_\allowbreak{}REVIEW\_\allowbreak{}BYPASS}",
                r"},\linebreak[2] \texttt{SOURCE\_\allowbreak{}REVIEW\_\allowbreak{}BYPASS}",
            ),
        ],
        "Study 6 G1 target-digest paragraph",
    )


def _target_assurance_signal_paragraph(tex: str) -> str:
    return _replace_in_unique_paragraph(
        tex,
        "The six assurance signals are also modeled Boolean variables.",
        [
            (
                r"variables. \texttt{independent\_\allowbreak{}target\_\allowbreak{}digest\_\allowbreak{}match}",
                r"variables.\linebreak[2] \texttt{independent\_\allowbreak{}target\_\allowbreak{}digest\_\allowbreak{}match}",
            ),
            (
                r" and \texttt{independent\_\allowbreak{}reproduced\_\allowbreak{}build\_\allowbreak{}match}",
                r" and\linebreak[2] \texttt{independent\_\allowbreak{}reproduced\_\allowbreak{}build\_\allowbreak{}match}",
            ),
            (
                r"independence. \texttt{source\_\allowbreak{}review\_\allowbreak{}attested}",
                r"independence.\linebreak[2] \texttt{source\_\allowbreak{}review\_\allowbreak{}attested}",
            ),
        ],
        "Study 6 assurance-signal limitations paragraph",
    )


def make_tex_r5(md: str) -> str:
    global _TARGETED_BREAKS
    _TARGETED_BREAKS = 0

    # Start from R3 intentionally. R4's localized \sloppy intervention is not
    # part of revision 5 because it failed page-by-page visual QA.
    tex = r3.make_tex_r3(md)
    if r"\sloppy" in tex:
        raise SystemExit("ERROR: revision-5 unexpectedly inherited \\sloppy")

    tex = _convert_common_framework_math(tex)
    tex = _target_endpoint_paragraph(tex)
    tex = _target_gate_itemize(tex)
    tex = _target_g1_paragraph(tex)
    tex = _target_assurance_signal_paragraph(tex)

    if _MATH_CONVERSIONS != 13:
        raise SystemExit(
            f"ERROR: revision-5 expected 13 math conversions; observed {_MATH_CONVERSIONS}"
        )
    if _TARGETED_BREAKS < 11:
        raise SystemExit(
            f"ERROR: revision-5 targeted-break count unexpectedly low: {_TARGETED_BREAKS}"
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

    print("TAES_IEEETRAN_R5_OVERFULL_CONTEXT_BEGIN")
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
    print("TAES_IEEETRAN_R5_OVERFULL_CONTEXT_END")


def main() -> None:
    base.make_tex = make_tex_r5
    base.main()
    print("TAES_IEEETRAN_BUILD_REVISION=5")
    print("r5_base=REVISION_3_NO_SLOPPY")
    print(f"common_framework_math_conversions={_MATH_CONVERSIONS}")
    print(f"targeted_linebreak_incentives={_TARGETED_BREAKS}")
    print("common_framework_math_typesetting=LATEX_MATH")
    print("localized_sloppy_blocks=0")
    print("global_geometry_changed=NO")
    print("science_or_manuscript_source_changed=NO")
    print_overfull_context()


if __name__ == "__main__":
    main()
