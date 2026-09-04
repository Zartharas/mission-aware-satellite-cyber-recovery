#!/usr/bin/env python3
"""Build the JAIS compact export with target-specific archival references."""

from __future__ import annotations

from pathlib import Path

import build_jais_export as base
import build_jais_compact_export as compact
import jais_reference_profile as reference_profile

HERE = Path(__file__).resolve().parent
EXTRA_BIB = HERE / "jais_additional_references.bib"
_ORIGINAL_READ_TEXT = base.read_text


def _read_with_jais_references(path: Path) -> str:
    text = _ORIGINAL_READ_TEXT(path)
    if path == base.REFERENCES:
        text += "\n\n" + _ORIGINAL_READ_TEXT(EXTRA_BIB)
    return text


def main() -> int:
    # Apply target-specific editorial/reference choices without changing the
    # authoritative manuscript components or target-neutral bibliography.
    compact.profile = reference_profile
    base.read_text = _read_with_jais_references
    return compact.main()


if __name__ == "__main__":
    raise SystemExit(main())
