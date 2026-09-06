#!/usr/bin/env python3
"""Revision-3 development builder for TAES Paper 2.

This wrapper preserves the canonical Markdown manuscript, Tables I-IV, Figure 1,
and every frozen scientific result. It changes only generated LaTeX typesetting
for simple inline code/identifier tokens. Instead of relying on URL parsing,
revision 3 keeps the original monospaced text and inserts explicit discretionary
line-break opportunities after underscores and selected punctuation.

No visible identifier characters are removed, abbreviated, or changed. The
underlying deterministic build, geometry checks, font checks, hashes, page count,
and development-only controls remain those in TAES_BUILD_IEEETRAN.py.
"""

from __future__ import annotations

import re

import TAES_BUILD_IEEETRAN as base


_ORIGINAL_MAKE_TEX = base.make_tex
_REPLACEMENT_COUNT = 0

_TEXTTT_RE = re.compile(r"\\texttt\{((?:\\[_-]|[^{}])*)\}")
_SAFE_CODE_RE = re.compile(r"^[A-Za-z0-9_./:;,\-+\[\]()=<> ]+$")
_BREAK_AFTER = {"_", "-", "/", ".", ":", ";", ","}


def _decode_simple_texttt(payload: str) -> str | None:
    decoded = payload.replace(r"\_", "_").replace(r"\-", "-")
    if "\\" in decoded:
        return None
    if not _SAFE_CODE_RE.fullmatch(decoded):
        return None
    return decoded


def _encode_breakable_texttt(decoded: str) -> str:
    pieces: list[str] = []
    for ch in decoded:
        if ch == "_":
            pieces.append(r"\_\allowbreak{}")
        elif ch in _BREAK_AFTER:
            pieces.append(ch + r"\allowbreak{}")
        else:
            pieces.append(ch)
    return r"\texttt{" + "".join(pieces) + "}"


def _make_breakable_code(tex: str) -> tuple[str, int]:
    count = 0

    def repl(match: re.Match[str]) -> str:
        nonlocal count
        decoded = _decode_simple_texttt(match.group(1))
        if decoded is None:
            return match.group(0)
        count += 1
        return _encode_breakable_texttt(decoded)

    return _TEXTTT_RE.sub(repl, tex), count


def make_tex_r3(md: str) -> str:
    global _REPLACEMENT_COUNT
    tex = _ORIGINAL_MAKE_TEX(md)
    tex, _REPLACEMENT_COUNT = _make_breakable_code(tex)
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

    print("TAES_IEEETRAN_R3_OVERFULL_CONTEXT_BEGIN")
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
    print("TAES_IEEETRAN_R3_OVERFULL_CONTEXT_END")


def main() -> None:
    base.make_tex = make_tex_r3
    base.main()
    print("TAES_IEEETRAN_BUILD_REVISION=3")
    print(f"breakable_code_tokens={_REPLACEMENT_COUNT}")
    print("breakable_code_strategy=TEXTTT_EXPLICIT_DISCRETIONARY_BREAKS")
    print("science_or_manuscript_source_changed=NO")
    print_overfull_hbox_context()


if __name__ == "__main__":
    main()
