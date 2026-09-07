#!/usr/bin/env python3
"""Revision-2 read-only science-preservation audit wrapper for TAES Paper 2.

R1 produced a false negative because one Study-4 population marker spans a
Markdown inline-code closing delimiter. R2 preserves every R1 hash, row,
reference, branch-scope, claim-boundary, and non-pooling check, but textual
marker matching is performed against Markdown-visible text by ignoring only
backtick delimiters.

No manuscript, supplement, generated PDF, result, frozen study source, or
publisher-facing artifact is modified. Only the local audit output filename is
changed to an R2-specific file.
"""
from __future__ import annotations

from pathlib import Path

import TAES_AUDIT_SHORT_TRACK_SCIENCE_PRESERVATION_R1 as r1

ROOT = Path(__file__).resolve().parent
OUT_AUDIT_R2 = ROOT / "TAES_10P_R3_SHORT_TRACK_SCIENCE_PRESERVATION_R2_AUDIT.txt"


def _visible_markdown(text: str) -> str:
    # Ignore only Markdown inline/fenced code delimiters for textual marker
    # matching. Preserve all visible characters, whitespace, punctuation,
    # numbers, underscores, operators, and scientific values.
    return text.replace("`", "")


def require_r2(text: str, marker: str, label: str) -> None:
    if _visible_markdown(marker) not in _visible_markdown(text):
        raise SystemExit(
            f"ERROR: science-preservation visible marker missing [{label}]: {marker}"
        )


def main() -> None:
    r1.require = require_r2
    r1.OUT_AUDIT = OUT_AUDIT_R2
    print("TAES_SHORT_TRACK_SCIENCE_PRESERVATION_AUDIT_REVISION=2")
    print("r2_change=MARKDOWN_VISIBLE_TEXT_MARKER_MATCHING_ONLY")
    print("ignored_source_delimiter=BACKTICK_ONLY")
    print("r1_hash_checks=UNCHANGED")
    print("r1_complete_table_row_checks=UNCHANGED")
    print("r1_branch_scope_check=UNCHANGED")
    print("r1_claim_boundary_checks=UNCHANGED")
    print("science_files_changed=NONE")
    print("study_rerun=NO")
    r1.main()
    if not OUT_AUDIT_R2.is_file():
        raise SystemExit("ERROR: R2 science-preservation audit output missing after PASS")
    with OUT_AUDIT_R2.open("a", encoding="utf-8") as handle:
        handle.write("science_preservation_audit_revision=2\n")
        handle.write("r2_change=MARKDOWN_VISIBLE_TEXT_MARKER_MATCHING_ONLY\n")
        handle.write("ignored_source_delimiter=BACKTICK_ONLY\n")
        handle.write("r1_hash_checks=UNCHANGED\n")
        handle.write("r1_complete_table_row_checks=UNCHANGED\n")
        handle.write("r1_branch_scope_check=UNCHANGED\n")
        handle.write("r1_claim_boundary_checks=UNCHANGED\n")
        handle.write("science_files_changed=NONE\n")
        handle.write("study_rerun=NO\n")
    print("TAES_SHORT_TRACK_SCIENCE_PRESERVATION_R2=PASS")


if __name__ == "__main__":
    main()
