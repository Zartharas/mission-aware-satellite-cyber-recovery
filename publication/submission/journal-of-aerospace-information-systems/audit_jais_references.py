#!/usr/bin/env python3
"""Audit the generated JAIS numbered references against AIAA reference rules."""

from __future__ import annotations

import csv
import json
import sys
from collections import OrderedDict
from pathlib import Path

import build_jais_export as base

HERE = Path(__file__).resolve().parent
GENERATED = HERE / "upload-packet" / "generated"
EXTRA_BIB = HERE / "jais_additional_references.bib"

# Reviewed durable published sources without a DOI.
ALLOWED_NO_DOI = {
    "geletko2019nos3": "published Journal of Small Satellites article",
    "sparta_fact_sheet_2025": "published Aerospace Corporation institutional fact sheet",
}

# These target-neutral web references must not survive into the JAIS numbered list.
DISALLOWED_FORMAL_KEYS = {
    "chunawala2026satelliteir",
    "nasa_nos3",
    "nasa_cfs",
    "sparta_cybersafe",
    "sparta_malicious_valid_gs",
    "sparta_replay_command_packets",
    "sparta_onorbit_update",
    "sparta_compromise_boot_memory",
    "sparta_telemetry_downlink_modes",
}


def merged_bib() -> dict[str, dict[str, str]]:
    text = base.read_text(base.REFERENCES) + "\n\n" + base.read_text(EXTRA_BIB)
    return base.parse_bibtex(text)


def required_fields(entry: dict[str, str]) -> list[str]:
    et = entry.get("ENTRYTYPE", "")
    if et == "article":
        return ["author", "title", "journal", "volume", "year", "pages"]
    if et == "inproceedings":
        return ["author", "title", "booktitle", "publisher", "address", "year", "pages", "doi"]
    if et == "techreport":
        return ["author", "title", "institution", "number", "year", "doi"]
    if et == "dataset":
        return ["author", "title", "publisher", "year", "doi"]
    return ["author", "title", "year"]


def main() -> int:
    ref_map = GENERATED / "JAIS_REFERENCE_MAP.csv"
    manuscript_path = GENERATED / "JAIS_MANUSCRIPT.md"
    if not ref_map.exists() or not manuscript_path.exists():
        raise SystemExit("Run build_jais_final_export.py before the reference audit")

    rows = list(csv.DictReader(ref_map.open(encoding="utf-8")))
    manuscript = manuscript_path.read_text(encoding="utf-8")
    bib = merged_bib()

    checks = OrderedDict()
    checks["reference_map_nonempty"] = bool(rows)
    checks["numbers_consecutive"] = [int(r["number"]) for r in rows] == list(range(1, len(rows) + 1))
    checks["no_disallowed_dynamic_web_refs"] = not any(r["bibtex_key"] in DISALLOWED_FORMAL_KEYS for r in rows)
    checks["no_et_al_in_reference_list"] = "et al." not in manuscript.split("# References", 1)[-1].lower()

    problems: list[str] = []
    classifications: list[dict[str, str]] = []

    for row in rows:
        key = row["bibtex_key"]
        entry = bib.get(key)
        if entry is None:
            problems.append(f"{key}: missing from merged bibliography")
            continue

        missing = [field for field in required_fields(entry) if not entry.get(field)]
        if missing:
            problems.append(f"{key}: missing required field(s): {', '.join(missing)}")

        author = entry.get("author", "")
        if " and others" in author.lower() or author.lower().endswith("others"):
            problems.append(f"{key}: abbreviated author list contains 'others'")

        doi = entry.get("doi", "").strip()
        url = entry.get("url", "").strip()
        if doi:
            persistence = "DOI"
            expected = f"https://doi.org/{doi}"
            if expected not in manuscript:
                problems.append(f"{key}: DOI URL missing from generated reference list")
        elif key in ALLOWED_NO_DOI:
            persistence = ALLOWED_NO_DOI[key]
            if not url:
                problems.append(f"{key}: reviewed no-DOI source lacks a public URL")
        else:
            persistence = "UNREVIEWED_NO_DOI"
            problems.append(f"{key}: no DOI and not an approved durable no-DOI publication")

        classifications.append({
            "number": row["number"],
            "key": key,
            "entry_type": entry.get("ENTRYTYPE", ""),
            "persistence": persistence,
            "doi": doi,
            "url": url,
        })

    checks["all_cited_entries_complete"] = not any("missing required field" in p for p in problems)
    checks["all_author_lists_explicit"] = not any("author list" in p for p in problems)
    checks["all_references_persistent_or_reviewed"] = not any("UNREVIEWED_NO_DOI" in p or "no DOI and" in p for p in problems)
    checks["all_doi_urls_rendered"] = not any("DOI URL missing" in p for p in problems)

    result = {
        "reference_count": len(rows),
        "checks": checks,
        "problems": problems,
        "classifications": classifications,
        "reference_gate_pass": all(checks.values()) and not problems,
    }

    (GENERATED / "JAIS_REFERENCE_AUDIT.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# JAIS AIAA Reference Audit",
        "",
        f"- Numbered references: {len(rows)}",
        f"- Gate: {'PASS' if result['reference_gate_pass'] else 'FAIL'}",
        "",
        "## Checks",
        "",
    ]
    for name, passed in checks.items():
        lines.append(f"- [{'x' if passed else ' '}] {name}")
    lines.extend(["", "## Persistence classification", ""])
    for item in classifications:
        lines.append(f"- [{item['number']}] `{item['key']}` — {item['persistence']}")
    if problems:
        lines.extend(["", "## Problems", ""])
        lines.extend(f"- {p}" for p in problems)
    lines.extend([
        "",
        "AIAA target-specific overrides are layered on the target-neutral bibliography; the research-source bibliography is not rewritten by this audit.",
    ])
    (GENERATED / "JAIS_REFERENCE_AUDIT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"reference_count={len(rows)}")
    print(f"reference_gate_pass={result['reference_gate_pass']}")
    if problems:
        for problem in problems:
            print(f"problem={problem}")
    return 0 if result["reference_gate_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
