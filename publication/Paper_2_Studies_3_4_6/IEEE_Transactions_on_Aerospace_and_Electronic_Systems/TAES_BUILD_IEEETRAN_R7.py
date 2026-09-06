#!/usr/bin/env python3
"""Revision-7 development builder for TAES Paper 2.

Revision 7 is a narrowly scoped follow-up to the full R6 page-by-page visual
QA. R6 passed all pages except the Study-3 frozen-primary-endpoints sentence,
where local emergency stretch removed overflow but produced visibly uneven
spacing and left the terminal ``s`` of ``unsafe_qualified_exposure_s`` isolated
on a continuation line.

R7 preserves R5's proper common-framework math conversion and R6's three
visually acceptable Study-6 emergency-stretch blocks. It removes emergency
stretch from the Study-3 endpoint paragraph and formats only the endpoint-list
sentence as a compact ragged-right block. The exact endpoint characters and
punctuation are retained. The break opportunity immediately before the final
``s`` in ``unsafe_qualified_exposure_s`` is removed so that the suffix cannot be
isolated by itself.

No canonical Markdown prose, study result, citation, table, figure, scientific
claim, population, or TAES geometry value is changed. The generated artifacts
remain development-only pending another complete PDF visual QA.
"""

from __future__ import annotations

import re

import TAES_BUILD_IEEETRAN as base
import TAES_BUILD_IEEETRAN_R5 as r5

_REMOVED_LINEBREAK_HINTS = 0
_LOCALIZED_STUDY6_BLOCKS = 0
_ENDPOINT_BLOCKS = 0

_GATE_LIST_STRETCH = "0.60em"
_G1_STRETCH = "0.90em"
_ASSURANCE_STRETCH = "1.20em"


def _remove_r5_linebreak_hints(tex: str) -> str:
    global _REMOVED_LINEBREAK_HINTS
    marker = r"\linebreak[2]"
    _REMOVED_LINEBREAK_HINTS = tex.count(marker)
    if _REMOVED_LINEBREAK_HINTS != 11:
        raise SystemExit(
            "ERROR: revision-7 expected exactly 11 revision-5 linebreak hints; "
            f"found {_REMOVED_LINEBREAK_HINTS}"
        )
    return tex.replace(marker, "")


def _paragraph_parts(tex: str, marker: str, label: str) -> tuple[list[str], int]:
    parts = tex.split("\n\n")
    hits = [i for i, part in enumerate(parts) if marker in part]
    if len(hits) != 1:
        raise SystemExit(
            f"ERROR: revision-7 paragraph marker for {label} expected one hit; found {len(hits)}"
        )
    return parts, hits[0]


def _format_endpoint_sentence(tex: str) -> str:
    global _ENDPOINT_BLOCKS
    parts, idx = _paragraph_parts(
        tex,
        "The frozen primary endpoints are",
        "Study 3 frozen-primary-endpoints paragraph",
    )
    paragraph = parts[idx]

    split_marker = ". This paper emphasizes"
    if paragraph.count(split_marker) != 1:
        raise SystemExit(
            "ERROR: revision-7 endpoint paragraph sentence boundary missing or ambiguous"
        )
    first, tail = paragraph.split(split_marker, 1)
    first_sentence = first + "."
    remainder = "This paper emphasizes" + tail

    suffix_break = r"unsafe\_\allowbreak{}qualified\_\allowbreak{}exposure\_\allowbreak{}s"
    suffix_fixed = r"unsafe\_\allowbreak{}qualified\_\allowbreak{}exposure\_s"
    if first_sentence.count(suffix_break) != 1:
        raise SystemExit(
            "ERROR: revision-7 could not identify unsafe_qualified_exposure_s break pattern"
        )
    first_sentence = first_sentence.replace(suffix_break, suffix_fixed, 1)

    # The endpoint-list sentence alone is ragged right to avoid interword
    # stretching around long monospaced identifiers. The following explanatory
    # prose returns immediately to normal IEEEtran justification.
    parts[idx] = (
        "{\\raggedright\n"
        + first_sentence
        + "\n\\par}\n"
        + "\\noindent "
        + remainder
    )
    _ENDPOINT_BLOCKS += 1
    return "\n\n".join(parts)


def _wrap_unique_paragraph(tex: str, marker: str, label: str, stretch: str) -> str:
    global _LOCALIZED_STUDY6_BLOCKS
    parts, idx = _paragraph_parts(tex, marker, label)
    parts[idx] = (
        "{\\setlength{\\emergencystretch}{" + stretch + "}\n"
        + parts[idx]
        + "\n\\par}"
    )
    _LOCALIZED_STUDY6_BLOCKS += 1
    return "\n\n".join(parts)


def _wrap_unique_itemize(tex: str, marker: str, label: str, stretch: str) -> str:
    global _LOCALIZED_STUDY6_BLOCKS
    pattern = re.compile(r"\\begin\{itemize\}.*?\\end\{itemize\}", re.DOTALL)
    matches = list(pattern.finditer(tex))
    hits = [m for m in matches if marker in m.group(0)]
    if len(hits) != 1:
        raise SystemExit(
            f"ERROR: revision-7 itemize marker for {label} expected one hit; found {len(hits)}"
        )
    hit = hits[0]
    wrapped = (
        "{\\setlength{\\emergencystretch}{" + stretch + "}\n"
        + hit.group(0)
        + "\n}"
    )
    tex = tex[: hit.start()] + wrapped + tex[hit.end() :]
    _LOCALIZED_STUDY6_BLOCKS += 1
    return tex


def make_tex_r7(md: str) -> str:
    global _ENDPOINT_BLOCKS, _LOCALIZED_STUDY6_BLOCKS
    _ENDPOINT_BLOCKS = 0
    _LOCALIZED_STUDY6_BLOCKS = 0

    # Retain R5's 13 mathematical-notation corrections, but retire its
    # ineffective penalty-based linebreak experiment before applying R7.
    tex = r5.make_tex_r5(md)
    tex = _remove_r5_linebreak_hints(tex)

    if r"\sloppy" in tex:
        raise SystemExit("ERROR: revision-7 unexpectedly inherited \\sloppy")
    if r"\linebreak[2]" in tex:
        raise SystemExit("ERROR: revision-7 failed to retire revision-5 linebreak hints")

    tex = _format_endpoint_sentence(tex)

    # Preserve the three R6 Study-6 local stretch values that passed visual QA.
    tex = _wrap_unique_itemize(
        tex,
        r"G4\_\allowbreak{}PROVENANCE\_\allowbreak{}SOURCE\_\allowbreak{}REVIEW",
        "Study 6 gate-definition list",
        _GATE_LIST_STRETCH,
    )
    tex = _wrap_unique_paragraph(
        tex,
        "adds independent target-digest match",
        "Study 6 G1 target-digest paragraph",
        _G1_STRETCH,
    )
    tex = _wrap_unique_paragraph(
        tex,
        "The six assurance signals are also modeled Boolean variables.",
        "Study 6 assurance-signal limitations paragraph",
        _ASSURANCE_STRETCH,
    )

    if _ENDPOINT_BLOCKS != 1:
        raise SystemExit(
            f"ERROR: revision-7 expected one endpoint typography block; observed {_ENDPOINT_BLOCKS}"
        )
    if _LOCALIZED_STUDY6_BLOCKS != 3:
        raise SystemExit(
            "ERROR: revision-7 expected three preserved Study-6 stretch blocks; "
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

    print("TAES_IEEETRAN_R7_OVERFULL_CONTEXT_BEGIN")
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
    print("TAES_IEEETRAN_R7_OVERFULL_CONTEXT_END")


def main() -> None:
    base.make_tex = make_tex_r7
    base.main()
    print("TAES_IEEETRAN_BUILD_REVISION=7")
    print("r7_base=REVISION_5_MATH_WITH_R6_STUDY6_STRETCH_PRESERVED")
    print(f"removed_r5_linebreak_hints={_REMOVED_LINEBREAK_HINTS}")
    print(f"endpoint_raggedright_blocks={_ENDPOINT_BLOCKS}")
    print("endpoint_terminal_s_break=SUPPRESSED")
    print(f"preserved_study6_emergencystretch_blocks={_LOCALIZED_STUDY6_BLOCKS}")
    print(f"gate_list_emergencystretch={_GATE_LIST_STRETCH}")
    print(f"g1_emergencystretch={_G1_STRETCH}")
    print(f"assurance_emergencystretch={_ASSURANCE_STRETCH}")
    print("common_framework_math_typesetting=LATEX_MATH_INHERITED_FROM_R5")
    print("localized_sloppy_blocks=0")
    print("global_geometry_changed=NO")
    print("science_or_manuscript_source_changed=NO")
    print_overfull_context()


if __name__ == "__main__":
    main()
