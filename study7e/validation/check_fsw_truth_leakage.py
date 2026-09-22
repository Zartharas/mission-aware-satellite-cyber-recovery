#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FSW_ROOT = ROOT / "study7e/fsw"

FORBIDDEN_TOKENS = (
    "true_authorization",
    "true_health_ready",
    "objective_action",
    "fault_profile",
    "domain_alias_map",
)

# Topology identity is forbidden as a policy/runtime input. The generic English
# word may legitimately appear in documentation, so source matching is scoped
# to identifier-like forms rather than prose README files.
FORBIDDEN_PATTERNS = (
    re.compile(r"\btopology_id\b"),
    re.compile(r"\bscenario_topology\b"),
    re.compile(r"\bexpected_affected_paths\b"),
    re.compile(r"\bexpected_propagation\b"),
)


def main() -> int:
    if not FSW_ROOT.is_dir():
        raise SystemExit("study7e/fsw is missing")

    checked = 0
    violations: list[str] = []
    for path in sorted(FSW_ROOT.rglob("*")):
        if not path.is_file() or path.suffix not in {".c", ".h", ".py"}:
            continue
        checked += 1
        text = path.read_text(encoding="utf-8", errors="strict")
        rel = path.relative_to(ROOT)

        for token in FORBIDDEN_TOKENS:
            if token in text:
                violations.append(f"{rel}: forbidden research-truth token {token!r}")

        for pattern in FORBIDDEN_PATTERNS:
            if pattern.search(text):
                violations.append(f"{rel}: forbidden research-topology pattern {pattern.pattern!r}")

    if violations:
        for violation in violations:
            print(f"[FAIL] {violation}")
        print(f"study7e_fsw_truth_leakage=FAIL violations={len(violations)}")
        return 1

    print("study7e_fsw_truth_leakage=PASS")
    print(f"source_files_checked={checked}")
    print("research_truth_visible_to_fsw=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
