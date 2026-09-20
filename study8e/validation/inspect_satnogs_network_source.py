#!/usr/bin/env python3
"""Inspect SatNOGS Network source code for observation API pagination/throttling.

This is source-code metadata inspection only. It does not access observation
records or compute Study 8E endpoints.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

PATTERNS = (
    re.compile(r"throttl", re.I),
    re.compile(r"cursor", re.I),
    re.compile(r"page_size", re.I),
    re.compile(r"pagination", re.I),
    re.compile(r"observations?.*rate", re.I),
    re.compile(r"rate.*observations?", re.I),
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    matches = []
    files_scanned = 0
    for path in sorted(args.source_root.rglob("*")):
        if not path.is_file() or path.suffix not in {".py", ".toml", ".ini", ".cfg", ".yaml", ".yml"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        files_scanned += 1
        lines = text.splitlines()
        for idx, line in enumerate(lines):
            if not any(p.search(line) for p in PATTERNS):
                continue
            start = max(0, idx - 2)
            end = min(len(lines), idx + 3)
            matches.append({
                "path": str(path.relative_to(args.source_root)),
                "line_number": idx + 1,
                "context": [
                    {"line_number": j + 1, "text": lines[j]}
                    for j in range(start, end)
                ],
            })

    git_head = ""
    head_file = args.source_root / ".git" / "HEAD"
    if head_file.is_file():
        git_head = head_file.read_text(encoding="utf-8").strip()

    report = {
        "schema": 1,
        "experiment_id": "S8E-ECTV-001",
        "stage": "SATNOGS_PUBLIC_SOURCE_PAGINATION_THROTTLE_AUDIT",
        "source_tag_requested": "1.134",
        "source_repository": "https://gitlab.com/librespacefoundation/satnogs/satnogs-network.git",
        "source_git_head_reference": git_head,
        "files_scanned": files_scanned,
        "match_count": len(matches),
        "matches": matches,
        "scope_boundary": {
            "observation_rows_accessed": False,
            "timing_endpoints_computed": False,
            "recovery_model_executed": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(report, indent=2, sort_keys=True) + "\n").encode()
    args.output.write_bytes(encoded)
    print(f"SatNOGS source configuration audit matches: {len(matches)}")
    print(f"Report SHA-256: {hashlib.sha256(encoded).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
