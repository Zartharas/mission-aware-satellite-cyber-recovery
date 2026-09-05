#!/usr/bin/env python3
"""Build the compact JAIS Paper-1 export from frozen source + editorial profile.

The authoritative numerical Results remain sourced from publication/manuscript.
JAIS-specific Introduction, Background, Methods, Discussion, and Conclusion are
reproducible editorial condensations in jais_editorial_profile.py.
"""

from __future__ import annotations

import csv
import json
import re
import sys
from collections import OrderedDict

import jais_editorial_profile as profile
import build_jais_export as base


# Five frozen manuscript-facing tables are retained as the principal displays.
# No separate figures are included in this compact initial-submission export.
DISPLAY_EQUIVALENT_WORDS = sum(base.TABLE_EQUIVALENT_WORDS.values())


def strip_markdown_tables(text: str) -> str:
    """Remove Markdown table rows for AIAA text-word counting.

    AIAA instructs Word authors to count manuscript text and then add equivalent
    space for tables/figures. Counting table-cell words and adding table-space
    equivalents would double-count those displays.
    """
    return "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("|"))


def compact_results() -> str:
    # Frozen numerical Results are not rewritten by the editorial profile.
    s1 = base.apply_editorial_transform(base.read_text(base.MANUSCRIPT / "04-results.md")).strip()
    s2 = base.apply_editorial_transform(base.read_text(base.MANUSCRIPT / "04-study2-results-extension.md")).strip()

    # The standalone synopsis repeats the individual result subsections and the
    # Discussion; remove it without changing any numerical result statement.
    s1 = re.sub(
        r"\n## 4\.8 Results synopsis\n.*?\Z",
        "",
        s1,
        flags=re.S,
    ).strip()

    # Move the full secondary multiplicity-count table to the repository record;
    # retain its interpretation and the fact that Holm adjustment was applied.
    s2 = re.sub(
        r"\n### 4\.9\.6 Secondary multiplicity summary\n.*?(?=\n### 4\.9\.7 Study-2 result boundary)",
        "\n### 4.9.6 Secondary multiplicity summary\n\nThe prespecified secondary contrast families used within-family and within-endpoint Holm adjustment. The complete family-level rejection counts are retained in the frozen Study-2 statistical record and public repository; they are not converted into a global policy score or rank.\n",
        s2,
        flags=re.S,
    )
    return s1 + "\n\n" + s2


def compact_endmatter() -> str:
    # Keep submission-relevant declarations concise; archive checksums/provenance
    # remain in the public repository and Zenodo records.
    return """# 7. Declarations, Data Availability, and Reproducibility

## 7.1 Ethics and responsible-research boundary

The reported studies used no human participants and collected no human-subject data. All identities, commands, mission states, evidence conditions, adversary states, and contact conditions were synthetic or software-emulated on researcher-controlled infrastructure. The research did not access an operational spacecraft or ground station, use operational or stolen credentials, transmit or interfere with radio-frequency systems, intercept non-public communications, or use classified or proprietary mission telemetry. Producer-compromise conditions used frozen research keys and software-generated evidence and do not represent compromise of a real mission organization.

## 7.2 Data and code availability

Study 1 is publicly archived on Zenodo as Version 1.0.0, version DOI 10.5281/zenodo.22181540 and concept DOI 10.5281/zenodo.22181539. Its primary statistical population remains exactly 720 VALID observations; nine INVALID attempts are retained as provenance outside statistical membership.

Study 2 is separately archived on Zenodo as Version 1.0.0, version DOI 10.5281/zenodo.22289114 and concept DOI 10.5281/zenodo.22289113. Its frozen population remains exactly 3,872 VALID observations across 85 cells with zero INVALID attempts. The publicly served Study-2 source-evidence archive was independently re-downloaded and its checksum matched the frozen source-evidence identity.

The public research repository is https://github.com/Zartharas/mission-aware-satellite-cyber-recovery. Study-1 reproducibility retains a separately reconstructed statistical implementation because the original executable analysis source was not preserved; the reconstruction begins from frozen derived inputs and regression-validates against preserved authoritative outputs. For Study 2, a separate implementation recomputed all frozen result families with zero mismatches. The two study populations remain separate and are not pooled.

## 7.3 Funding

This research was conducted independently and received no external funding.

## 7.4 Competing interests

The author declares no competing financial or non-financial interests.

## 7.5 Author contribution

Aman Kumar Singh: Conceptualization; Methodology; Software; Validation; Formal analysis; Investigation; Resources; Data curation; Writing - original draft; Writing - review and editing; Visualization; Project administration.

## 7.6 Artificial-intelligence disclosure

During preparation of this journal work, the author used OpenAI ChatGPT to assist with manuscript organization, source checking, editorial refinement, consistency review, reproducibility documentation, repository and audit workflow support, and preparation of journal-submission materials. The author reviewed and edited all resulting content, checked scientific quantities and source claims against the frozen research record and cited sources, and takes full responsibility for the manuscript. For Study 1, this assistance occurred after the experimental campaign and historical statistical findings were frozen and after the evidence package had been archived. For Study 2, the assistance occurred after the campaign evidence and prospective analysis implementation were frozen. It did not generate or replace observations, alter seeds or exclusions, change either frozen statistical population, modify the frozen Study-2 analyzer, or provide input to the evaluated deterministic response policies.
"""


def build() -> tuple[str, list[str], list[str]]:
    abstract = base.extract_abstract()
    keywords = base.extract_keywords()
    bib = base.parse_bibtex(base.read_text(base.REFERENCES))

    body_parts = [
        profile.INTRODUCTION.strip(),
        profile.BACKGROUND.strip(),
        profile.METHODS.strip(),
        compact_results().strip(),
        profile.DISCUSSION.strip(),
        profile.CONCLUSION.strip(),
        compact_endmatter().strip(),
    ]
    body = "\n\n".join(body_parts)
    body, citation_order, missing = base.replace_citations(body, bib)

    front = f"""# {base.TITLE}

**Aman Kumar Singh, MS, DSc**  
Independent Researcher, The Woodlands, Texas, United States  
Corresponding author: asingh65430@ucumberlands.edu  
ORCID: 0009-0008-9752-3743

## Abstract

{abstract}

**Keywords:** {keywords}
"""

    tables_md = ["# Main Tables"]
    for number, (filename, caption) in enumerate(base.MAIN_TABLES.items(), start=1):
        tables_md.append(base.csv_to_markdown(base.TABLES / filename, number, caption))

    refs = ["# References"]
    for number, key in enumerate(citation_order, start=1):
        refs.append(f"[{number}] {base.format_reference(bib[key])}")

    manuscript = (
        front.strip() + "\n\n" + body.strip() + "\n\n" +
        "\n\n".join(tables_md) + "\n\n" + "\n\n".join(refs) + "\n"
    )
    return manuscript, citation_order, missing


def audit(manuscript: str, citation_order: list[str], missing: list[str]) -> dict:
    abstract = base.extract_abstract()
    text_without_tables = strip_markdown_tables(manuscript)
    text_words = base.word_count(text_without_tables)
    equivalent_words = text_words + DISPLAY_EQUIVALENT_WORDS

    checks = OrderedDict()
    checks["title_max_12_words"] = len(base.TITLE.split()) <= 12
    checks["abstract_100_200_words"] = 100 <= len(abstract.split()) <= 200
    checks["abstract_single_paragraph"] = "\n" not in abstract.strip()
    checks["abstract_third_person"] = not re.search(r"\b(we|our|I|my)\b", abstract, re.I)
    checks["abstract_no_citation_marker"] = "[@" not in abstract and not re.search(r"\[\d", abstract)
    checks["no_unconverted_pandoc_citations"] = "[@" not in manuscript
    checks["all_citation_keys_resolved"] = not missing
    checks["study1_population_preserved"] = "720 VALID" in manuscript and "24" in manuscript
    checks["study2_population_preserved"] = "3,872" in manuscript and "85" in manuscript
    checks["study2_zero_invalid_preserved"] = "zero INVALID attempts" in manuscript
    checks["study_populations_not_pooled"] = "not pooled" in manuscript.lower()
    checks["study1_p1_null_boundary_present"] = "did not demonstrate mission-state dependence" in manuscript
    checks["block_c_structural_boundary_present"] = "structural label-invariance" in manuscript.lower()
    checks["k4_nonordinal_boundary_present"] = "K4" in manuscript and "intermittent/flapping" in manuscript
    checks["a2_k2_coupled_boundary_present"] = "A2/K2" in manuscript and "coupled" in manuscript
    checks["logical_time_boundary_present"] = "logical software" in manuscript.lower() or "logical software-model" in manuscript.lower()
    checks["no_weighted_global_rank"] = "No weighted global" in manuscript or "no weighted global" in manuscript
    checks["no_study8_import"] = "Study 8" not in manuscript and "study8" not in manuscript.lower()
    checks["no_c_and_s_target_residue"] = "primary target remains Computers & Security" not in manuscript
    checks["aiaa_equivalent_word_guideline"] = equivalent_words <= 12000

    return {
        "title": base.TITLE,
        "title_words": len(base.TITLE.split()),
        "abstract_words": len(abstract.split()),
        "text_words_excluding_table_cells": text_words,
        "table_equivalent_words": DISPLAY_EQUIVALENT_WORDS,
        "estimated_aiaa_equivalent_words": equivalent_words,
        "citation_count": len(citation_order),
        "missing_citation_keys": missing,
        "checks": checks,
        "hard_gate_pass": all(checks.values()),
    }


def main() -> int:
    base.GENERATED.mkdir(parents=True, exist_ok=True)
    manuscript, citation_order, missing = build()
    result = audit(manuscript, citation_order, missing)
    bib = base.parse_bibtex(base.read_text(base.REFERENCES))

    (base.GENERATED / "JAIS_MANUSCRIPT.md").write_text(manuscript, encoding="utf-8")
    (base.GENERATED / "JAIS_EXPORT_AUDIT.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    with (base.GENERATED / "JAIS_REFERENCE_MAP.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["number", "bibtex_key", "entry_type", "doi", "url", "title"])
        for number, key in enumerate(citation_order, start=1):
            e = bib[key]
            writer.writerow([number, key, e.get("ENTRYTYPE", ""), e.get("doi", ""), e.get("url", ""), e.get("title", "")])

    lines = [
        "# JAIS Compact Export Audit",
        "",
        f"- Title words: {result['title_words']} / 12",
        f"- Abstract words: {result['abstract_words']} / 100-200",
        f"- Text words excluding table-cell text: {result['text_words_excluding_table_cells']}",
        f"- AIAA table-equivalent words: {result['table_equivalent_words']}",
        f"- Estimated AIAA equivalent words: {result['estimated_aiaa_equivalent_words']} / 12,000 recommended maximum",
        f"- Numbered references: {result['citation_count']}",
        f"- Missing citation keys: {', '.join(missing) if missing else 'none'}",
        "",
        "## Checks",
        "",
    ]
    for name, passed in result["checks"].items():
        lines.append(f"- [{'x' if passed else ' '}] {name}")
    lines.extend([
        "",
        f"**Compact export gate:** {'PASS' if result['hard_gate_pass'] else 'FAIL'}",
        "",
        "The authoritative numerical Results are generated from frozen manuscript components. The compact profile changes venue-facing exposition only. Exact ScholarOne field lock, final reference archivality/metadata review, package freeze, and separate authorization remain required before submission.",
    ])
    (base.GENERATED / "JAIS_EXPORT_AUDIT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"manuscript={base.GENERATED / 'JAIS_MANUSCRIPT.md'}")
    print(f"audit={base.GENERATED / 'JAIS_EXPORT_AUDIT.md'}")
    print(f"hard_gate_pass={result['hard_gate_pass']}")
    print(f"estimated_equivalent_words={result['estimated_aiaa_equivalent_words']}")
    return 0 if result["hard_gate_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
