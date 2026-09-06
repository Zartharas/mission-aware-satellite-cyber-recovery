#!/usr/bin/env python3
"""Revision-2 development builder for TAES Paper 2.

This wrapper preserves the canonical manuscript, Tables I-IV, Figure 1, and all
frozen scientific content. It changes only LaTeX typesetting behavior for simple
inline code/identifier tokens: unbreakable ``\\texttt{...}`` identifiers are
rendered with the ``url`` package's native ``\\path{...}`` command so TeX may
break them at underscores and selected punctuation while preserving monospaced
styling and the exact visible identifier text.

The underlying deterministic build, geometry checks, font checks, hashes, page
count, and development-only controls remain those in TAES_BUILD_IEEETRAN.py.
"""

from __future__ import annotations

import re

import TAES_BUILD_IEEETRAN as base


_ORIGINAL_MAKE_TEX = base.make_tex
_REPLACEMENT_COUNT = 0

# Match simple Pandoc/table-generated texttt groups without nested braces.
_TEXTTT_RE = re.compile(r"\\texttt\{((?:\\[_-]|[^{}])*)\}")
_SAFE_CODE_RE = re.compile(r"^[A-Za-z0-9_./:;,\-+\[\]()=<> ]+$")


def _decode_simple_texttt(payload: str) -> str | None:
    decoded = payload.replace(r"\_", "_").replace(r"\-", "-")
    # Refuse to rewrite any token that still contains a TeX command or escape.
    if "\\" in decoded:
        return None
    if not _SAFE_CODE_RE.fullmatch(decoded):
        return None
    return decoded


def _make_breakable_code(tex: str) -> tuple[str, int]:
    count = 0

    def repl(match: re.Match[str]) -> str:
        nonlocal count
        decoded = _decode_simple_texttt(match.group(1))
        if decoded is None:
            return match.group(0)
        count += 1
        return r"\TAEScode{" + decoded + "}"

    return _TEXTTT_RE.sub(repl, tex), count


def make_tex_r2(md: str) -> str:
    global _REPLACEMENT_COUNT
    tex = _ORIGINAL_MAKE_TEX(md)
    tex, _REPLACEMENT_COUNT = _make_breakable_code(tex)

    anchor = r"\usepackage{url}"
    if tex.count(anchor) != 1:
        raise SystemExit("ERROR: revision-2 preamble anchor missing or ambiguous")

    controls = r"""\usepackage{url}
\urlstyle{tt}
\def\UrlBreaks{\do\_\do\-\do\/\do\.\do\:\do\;\do\,}
\newcommand{\TAEScode}[1]{\path{#1}}
"""
    tex = tex.replace(anchor, controls.rstrip(), 1)
    return tex


def print_overfull_hbox_context() -> None:
    if not base.OUT_LOG.is_file() or not base.OUT_TEX.is_file():
        return

    log = base.OUT_LOG.read_text(encoding="utf-8", errors="replace")
    tex_lines = base.OUT_TEX.read_text(encoding="utf-8", errors="replace").splitlines()
    pattern = re.compile(
        r"Overfull \\hbox \(([0-9.]+)pt too wide\) in paragraph at lines (\d+)--(\d+)"
    )
    matches = list(pattern.finditer(log))

    print("TAES_IEEETRAN_R2_OVERFULL_CONTEXT_BEGIN")
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
    print("TAES_IEEETRAN_R2_OVERFULL_CONTEXT_END")


def main() -> None:
    base.make_tex = make_tex_r2
    base.main()
    print("TAES_IEEETRAN_BUILD_REVISION=2")
    print(f"breakable_code_tokens={_REPLACEMENT_COUNT}")
    print("breakable_code_macro=URL_PACKAGE_PATH")
    print("science_or_manuscript_source_changed=NO")
    print_overfull_hbox_context()


if __name__ == "__main__":
    main()
