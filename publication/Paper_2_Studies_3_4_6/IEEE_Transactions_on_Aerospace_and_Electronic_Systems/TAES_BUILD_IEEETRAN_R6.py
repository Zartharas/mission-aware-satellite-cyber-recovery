#!/usr/bin/env python3
"""Revision-6 development builder for TAES Paper 2.

Revision 6 preserves revision 5's corrected common-framework math rendering but
retires revision 5's ineffective ``\\linebreak[2]`` incentives. It applies only
modest, localized ``\\emergencystretch`` values to the four technical blocks
that still overflow under normal IEEEtran justification.

The intervention is generated-LaTeX-only. It does not edit the canonical
Markdown manuscript, abbreviate identifiers, change Tables I-IV or Figure 1,
change any frozen result or citation, or modify the TAES geometry. It does not
use ``\\sloppy``.
"""

from __future__ import annotations

import re

import TAES_BUILD_IEEETRAN as base
import TAES_BUILD_IEEETRAN_R5 as r5

_LOCALIZED_BLOCKS = 0
_REMOVED_LINEBREAK_HINTS = 0

# Chosen conservatively by residual-overflow severity from revision 5.
_ENDPOINT_STRETCH = "1.50em"
_GATE_LIST_STRETCH = "0.60em"
_G1_STRETCH = "0.90em"
_ASSURANCE_STRETCH = "1.20em"


def _remove_r5_linebreak_hints(tex: str) -> str:
    global _REMOVED_LINEBREAK_HINTS
    marker = r"\linebreak[2]"
    _REMOVED_LINEBREAK_HINTS = tex.count(marker)
    if _REMOVED_LINEBREAK_HINTS != 11:
        raise SystemExit(
            "ERROR: revision-6 expected exactly 11 revision-5 linebreak hints; "
            f"found {_REMOVED_LINEBREAK_HINTS}"
        )
    return tex.replace(marker, "")


def _wrap_unique_paragraph(tex: str, marker: str, label: str, stretch: str) -> str:
    global _LOCALIZED_BLOCKS
    parts = tex.split("\n\n")
    hits = [i for i, part in enumerate(parts) if marker in part]
    if len(hits) != 1:
        raise SystemExit(
            f"ERROR: revision-6 paragraph marker for {label} expected one hit; found {len(hits)}"
        )
    idx = hits[0]
    parts[idx] = (
        "{\\setlength{\\emergencystretch}{" + stretch + "}\n"
        + parts[idx]
        + "\n\\par}"
    )
    _LOCALIZED_BLOCKS += 1
    return "\n\n".join(parts)


def _wrap_unique_itemize(tex: str, marker: str, label: str, stretch: str) -> str:
    global _LOCALIZED_BLOCKS
    pattern = re.compile(r"\\begin\{itemize\}.*?\\end\{itemize\}", re.DOTALL)
    matches = list(pattern.finditer(tex))
    hits = [m for m in matches if marker in m.group(0)]
    if len(hits) != 1:
        raise SystemExit(
            f"ERROR: revision-6 itemize marker for {label} expected one hit; found {len(hits)}"
        )
    hit = hits[0]
    wrapped = (
        "{\\setlength{\\emergencystretch}{" + stretch + "}\n"
        + hit.group(0)
        + "\n}"
    )
    tex = tex[: hit.start()] + wrapped + tex[hit.end() :]
    _LOCALIZED_BLOCKS += 1
    return tex


def make_tex_r6(md: str) -> str:
    global _LOCALIZED_BLOCKS
    _LOCALIZED_BLOCKS = 0

    # Start from R5 to retain its 13 proper math conversions, then remove the
    # penalty-based linebreak experiment before applying localized stretch.
    tex = r5.make_tex_r5(md)
    tex = _remove_r5_linebreak_hints(tex)

    if r"\sloppy" in tex:
        raise SystemExit("ERROR: revision-6 unexpectedly inherited \\sloppy")
    if r"\linebreak[2]" in tex:
        raise SystemExit("ERROR: revision-6 failed to retire revision-5 linebreak hints")

    tex = _wrap_unique_paragraph(
        tex,
        "The frozen primary endpoints are",
        "Study 3 frozen primary endpoints",
        _ENDPOINT_STRETCH,
    )
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

    if _LOCALIZED_BLOCKS != 4:
        raise SystemExit(
            f"ERROR: revision-6 expected four localized stretch blocks; observed {_LOCALIZED_BLOCKS}"
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

    print("TAES_IEEETRAN_R6_OVERFULL_CONTEXT_BEGIN")
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
    print("TAES_IEEETRAN_R6_OVERFULL_CONTEXT_END")


def main() -> None:
    base.make_tex = make_tex_r6
    base.main()
    print("TAES_IEEETRAN_BUILD_REVISION=6")
    print("r6_base=REVISION_5_MATH_WITH_LINEBREAK_HINTS_RETIRED")
    print(f"removed_r5_linebreak_hints={_REMOVED_LINEBREAK_HINTS}")
    print(f"localized_emergencystretch_blocks={_LOCALIZED_BLOCKS}")
    print(f"endpoint_emergencystretch={_ENDPOINT_STRETCH}")
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
