#!/usr/bin/env python3
"""Revision-4 development builder for TAES Paper 2.

Revision 4 preserves the canonical Markdown manuscript, Tables I-IV, Figure 1,
all frozen study results, and the TAES geometry. It builds on revision 3's
explicit discretionary breaks inside monospaced identifiers, then applies
localized LaTeX ``\\sloppy`` line-breaking only to the four generated-TeX
blocks that remained overfull in revision 3:

1. the Study 3 frozen-primary-endpoints paragraph;
2. the Study 6 gate-definition itemize block containing G4/G5;
3. the Study 6 G1 target-digest paragraph; and
4. the Study 6 assurance-signal limitations paragraph.

No manuscript source text is changed. No identifier is abbreviated. No table
row, figure content, scientific result, limitation, citation, or geometry value
is changed. Generated files remain development-only pending separate PDF visual
QA.
"""

from __future__ import annotations

import re

import TAES_BUILD_IEEETRAN as base
import TAES_BUILD_IEEETRAN_R3 as r3

_LOCALIZED_BLOCKS = 0


def _wrap_unique_paragraph(tex: str, marker: str, label: str) -> str:
    global _LOCALIZED_BLOCKS
    parts = tex.split("\n\n")
    hits = [i for i, part in enumerate(parts) if marker in part]
    if len(hits) != 1:
        raise SystemExit(
            f"ERROR: revision-4 paragraph marker for {label} expected one hit; found {len(hits)}"
        )
    idx = hits[0]
    parts[idx] = "{\\sloppy\n" + parts[idx] + "\n\\par}"
    _LOCALIZED_BLOCKS += 1
    return "\n\n".join(parts)


def _wrap_unique_itemize(tex: str, marker: str, label: str) -> str:
    global _LOCALIZED_BLOCKS
    pattern = re.compile(r"\\begin\{itemize\}.*?\\end\{itemize\}", re.DOTALL)
    matches = list(pattern.finditer(tex))
    hits = [m for m in matches if marker in m.group(0)]
    if len(hits) != 1:
        raise SystemExit(
            f"ERROR: revision-4 itemize marker for {label} expected one hit; found {len(hits)}"
        )
    hit = hits[0]
    wrapped = "{\\sloppy\n" + hit.group(0) + "\n}"
    tex = tex[: hit.start()] + wrapped + tex[hit.end() :]
    _LOCALIZED_BLOCKS += 1
    return tex


def make_tex_r4(md: str) -> str:
    global _LOCALIZED_BLOCKS
    _LOCALIZED_BLOCKS = 0
    tex = r3.make_tex_r3(md)

    tex = _wrap_unique_paragraph(
        tex,
        "The frozen primary endpoints are",
        "Study 3 frozen primary endpoints",
    )
    tex = _wrap_unique_itemize(
        tex,
        "G4\\_\\allowbreak{}PROVENANCE\\_\\allowbreak{}SOURCE\\_\\allowbreak{}REVIEW",
        "Study 6 gate-definition list",
    )
    tex = _wrap_unique_paragraph(
        tex,
        "adds independent target-digest match",
        "Study 6 G1 target-digest paragraph",
    )
    tex = _wrap_unique_paragraph(
        tex,
        "The six assurance signals are also modeled Boolean variables.",
        "Study 6 assurance-signal limitations paragraph",
    )

    if _LOCALIZED_BLOCKS != 4:
        raise SystemExit(
            f"ERROR: revision-4 expected four localized line-breaking blocks; observed {_LOCALIZED_BLOCKS}"
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

    print("TAES_IEEETRAN_R4_OVERFULL_CONTEXT_BEGIN")
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
                if len(text) > 240:
                    text = text[:237] + "..."
                print(f"tex_{number}={text}")
    print("TAES_IEEETRAN_R4_OVERFULL_CONTEXT_END")


def main() -> None:
    base.make_tex = make_tex_r4
    base.main()
    print("TAES_IEEETRAN_BUILD_REVISION=4")
    print("breakable_code_strategy=R3_EXPLICIT_DISCRETIONARY_BREAKS_PLUS_LOCALIZED_SLOPPY")
    print(f"localized_sloppy_blocks={_LOCALIZED_BLOCKS}")
    print("global_geometry_changed=NO")
    print("science_or_manuscript_source_changed=NO")
    print_overfull_context()


if __name__ == "__main__":
    main()
