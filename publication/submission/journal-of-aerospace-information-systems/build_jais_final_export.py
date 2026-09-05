#!/usr/bin/env python3
"""Build the JAIS compact export with archival references and JAIS display tables."""

from __future__ import annotations

import csv
from pathlib import Path

import build_jais_export as base
import build_jais_compact_export as compact
import jais_aiaa_reference as aiaa_reference
import jais_reference_profile as reference_profile

HERE = Path(__file__).resolve().parent
EXTRA_BIB = HERE / "jais_additional_references.bib"
_ORIGINAL_READ_TEXT = base.read_text
_ORIGINAL_CSV_TO_MARKDOWN = base.csv_to_markdown


def _read_with_jais_references(path: Path) -> str:
    text = _ORIGINAL_READ_TEXT(path)
    if path == base.REFERENCES:
        text += "\n\n" + _ORIGINAL_READ_TEXT(EXTRA_BIB)
    return text


def _md_table(headers: list[str], rows: list[list[str]]) -> str:
    def esc(value: str) -> str:
        return str(value).replace("|", "\\|").replace("\n", " ").strip()

    lines = [
        "| " + " | ".join(esc(x) for x in headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(esc(x) for x in row) + " |")
    return "\n".join(lines)


def _read_csv_dicts(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _human_policy(text: str) -> str:
    replacements = {
        "S2_B0_FAIL_CLOSED": "B0 fail-closed",
        "S2_B1_FAIL_OPERATIONAL": "B1 fail-operational",
        "S2_B2_RISK_THRESHOLD": "B2 risk-threshold",
        "S2_S1_EVIDENCE_AWARE": "S1 evidence-aware",
        "C_FAULT_ATTACK_AMBIGUITY": "fault/attack ambiguity control",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def _jais_csv_to_markdown(path: Path, number: int, caption: str) -> str:
    """Render wide frozen CSVs as compact JAIS-facing tables.

    This changes only the display shape. Every value is derived from the frozen
    manuscript-facing CSVs; the source tables and numerical Results are untouched.
    """
    name = path.name

    if name == "table-r3-p3-p4-evidence-pathways.csv":
        rows = []
        for d in _read_csv_dicts(path):
            action = d["selected_action_or_basis"].replace("_", " ").replace(" -> ", "; then ")
            case = f"{d['cell']} ({d['event_family']}, {d['evidence_condition']})"
            policy_path = f"{d['requested_policy']}→{d['effective_policy']}; {action}"
            outcomes = (
                f"M02={d['M02_mission_completion']}; "
                f"trusted recovery={d['M05_trusted_recovery_count']}/30; "
                f"recovery failed={d['recovery_failed_count']}/30; "
                f"M06={d['M06_legitimate_rejection_rate']}"
            )
            rows.append([case, policy_path, outcomes, d["interpretive_note"]])
        body = _md_table(
            ["Case", "Policy path / action", "Frozen outcomes", "Interpretation"],
            rows,
        )
        return f"**Table {number}. {caption}.**\n\n{body}"

    if name == "table-r4-p5-pareto-status.csv":
        category = {
            "TIE_EQUIVALENCE": "Tie/equivalence",
            "COMPARATOR_SUPPORTED_DISADVANTAGE": "Comparator-supported disadvantage",
            "MIXED": "Mixed",
            "P7_SUPPORTED_BENEFIT": "P7-supported benefit",
        }
        rows = []
        for d in _read_csv_dicts(path):
            case = f"{d['group']} / {d['p7_cell']} / {d['p7_effective_policy']}"
            front = "yes" if d["p7_on_point_front"].lower() == "true" else "no"
            relation = f"Front={front}; {d['point_estimate_relation_summary']}"
            rows.append([
                case,
                relation,
                d["marginal_interval_summary"],
                category.get(d["display_category"], d["display_category"]),
            ])
        body = _md_table(
            ["Group / P7", "Point-estimate relation", "Marginal-interval interpretation", "Category"],
            rows,
        )
        return f"**Table {number}. {caption}.**\n\n{body}"

    if name == "table-r7-study2-prespecified-findings.csv":
        rows = []
        for d in _read_csv_dicts(path):
            rq = f"{d['research_question']}: {d['contrast_or_profile']}"
            rows.append([
                rq,
                _human_policy(d["policy_or_scope"]),
                _human_policy(d["frozen_finding"]),
                d["journal_interpretation_boundary"],
            ])
        body = _md_table(
            ["RQ / contrast", "Policy / scope", "Frozen finding", "Interpretation boundary"],
            rows,
        )
        return f"**Table {number}. {caption}.**\n\n{body}"

    return _ORIGINAL_CSV_TO_MARKDOWN(path, number, caption)


def main() -> int:
    # Apply target-specific editorial/reference/display choices without changing
    # authoritative manuscript components, frozen tables, or target-neutral bibliography.
    compact.profile = reference_profile
    base.read_text = _read_with_jais_references
    base.format_reference = aiaa_reference.format_reference
    base.csv_to_markdown = _jais_csv_to_markdown
    return compact.main()


if __name__ == "__main__":
    raise SystemExit(main())
