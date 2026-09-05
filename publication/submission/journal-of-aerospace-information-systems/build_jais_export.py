#!/usr/bin/env python3
"""Build a JAIS-target manuscript from the frozen Paper-1 component sources.

This is an editorial/export tool only. It does not rerun experiments, recompute
frozen statistics, or modify Study 1 / Study 2 source evidence.
"""

from __future__ import annotations

import csv
import json
import re
import sys
from collections import OrderedDict
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
MANUSCRIPT = REPO / "publication" / "manuscript"
TABLES = REPO / "publication" / "tables"
REFERENCES = REPO / "references" / "references.bib"
UPLOAD = HERE / "upload-packet"
GENERATED = UPLOAD / "generated"

TITLE = "Satellite Cyber Response and Trusted Recovery Under Contact and Adversarial Evidence Constraints"

COMPONENTS = [
    "01-introduction.md",
    "02-background-and-related-work.md",
    "03-methods.md",
    "03-study2-methods-extension.md",
    "04-results.md",
    "04-study2-results-extension.md",
    "05-discussion.md",
    "06-conclusion.md",
]

# Main-display policy for the first JAIS export. These source tables are frozen
# manuscript-facing summaries; copying them does not alter the underlying science.
MAIN_TABLES = OrderedDict([
    ("table-r1-proposition-summary.csv", "Study 1 frozen population and proposition summary"),
    ("table-r2-p2-contact-effects.csv", "Study 1 modeled contact effects"),
    ("table-r3-p3-p4-evidence-pathways.csv", "Study 1 evidence-dependent recovery and selection pathways"),
    ("table-r4-p5-pareto-status.csv", "Study 1 condition-specific Pareto relations"),
    ("table-r7-study2-prespecified-findings.csv", "Study 2 prespecified findings"),
])

# Conservative AIAA equivalent-space estimate. Standard tables are 200 words;
# the Study-2 findings table is treated as a larger two-column table at 450.
TABLE_EQUIVALENT_WORDS = {
    "table-r1-proposition-summary.csv": 200,
    "table-r2-p2-contact-effects.csv": 200,
    "table-r3-p3-p4-evidence-pathways.csv": 200,
    "table-r4-p5-pareto-status.csv": 200,
    "table-r7-study2-prespecified-findings.csv": 450,
}

# Existing inline tables in the authoritative component text: Study-1 24-cell
# matrix, Study-2 evidence-condition table, and Study-2 secondary multiplicity table.
INLINE_TABLE_EQUIVALENT_WORDS = 3 * 200

VENUE_REPLACEMENTS = {
    "Recent Computers & Security papers also demonstrate venue adjacency through satellite intrusion detection, SatCom risk analysis, space-organization attack-surface measurement, and cyber-physical security testbeds":
        "Recent satellite-security publications provide adjacent evidence through satellite intrusion detection, SatCom risk analysis, space-organization attack-surface measurement, and cyber-physical security testbeds",
    "Recent Computers & Security work establishes particularly close venue adjacency.":
        "Recent satellite-security work provides closely adjacent prior art.",
    "Recent Computers & Security work provides direct venue adjacency but a different center of gravity:":
        "Recent satellite-security work in Computers & Security provides adjacent prior art but a different center of gravity:",
    "Table R5 provides a conservative closest-work comparison. Cells use language such as “not primary focus” rather than asserting that a dimension is completely absent from a cited implementation. This avoids manufacturing novelty from incomplete literature inspection while making the paper's research object visible to reviewers.":
        "The closest-work comparison is kept conservative: prior dimensions are described as not being a primary focus rather than asserted to be absent, avoiding novelty claims based on incomplete literature inspection.",
    "Table R6 provides the full mapping.":
        "The retained endpoints map separately to integrity, availability and mission continuity, safety, recoverability, and evidence assurance.",
    "Figure R1 and Table R2 show the retained contrasts and intervals.":
        "Table 2 reports the retained contrasts and intervals.",
    "Figure R2 and Table R3 summarize these retained outcomes.":
        "Table 3 summarizes these retained outcomes.",
    "Figure R3 displays the deterministic evidence-to-selection-to-consequence pathways, and Table R3 provides the underlying cell-level values.":
        "Table 3 reports the deterministic evidence-to-selection-to-consequence pathways and underlying cell-level values.",
    "Table R4 and Figure R4 summarize the group-level P7 relations.":
        "Table 4 summarizes the group-level P7 relations.",
    "Table S1 records the execution-provenance distribution and sensitivity results.":
        "The complete execution-provenance distribution and sensitivity record is retained in the public research repository.",
}

DISPLAY_LABEL_REPLACEMENTS = {
    "Table R1": "Table 1",
    "Table R2": "Table 2",
    "Table R3": "Table 3",
    "Table R4": "Table 4",
    "Table R7": "Table 5",
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_abstract() -> str:
    text = read_text(HERE / "jais-abstract.md")
    marker = "**Word count:**"
    start = text.index(marker)
    after = text[start:].split("\n\n", 1)[1]
    return after.split("\n\n## AIAA abstract-format check", 1)[0].strip()


def extract_keywords() -> str:
    text = read_text(MANUSCRIPT / "00-title-abstract.md")
    match = re.search(r"## Keywords\s+(.+?)(?:\n\n##|\Z)", text, flags=re.S)
    if not match:
        raise RuntimeError("Could not extract keywords from authoritative title/abstract source")
    return " ".join(match.group(1).split())


def apply_editorial_transform(text: str) -> str:
    for old, new in VENUE_REPLACEMENTS.items():
        text = text.replace(old, new)
    for old, new in DISPLAY_LABEL_REPLACEMENTS.items():
        text = text.replace(old, new)
    # AIAA uses Fig. for figure references. The first export intentionally relies
    # on tables for the Study-1 result displays to reduce equivalent-space cost.
    text = text.replace("Figure R1", "the modeled-contact result display")
    text = text.replace("Figure R2", "the trusted-recovery result display")
    text = text.replace("Figure R3", "the selection-pathway result display")
    text = text.replace("Figure R4", "the Pareto result display")
    return text


def parse_bibtex(text: str) -> dict[str, dict[str, str]]:
    entries: dict[str, dict[str, str]] = {}
    pos = 0
    while True:
        m = re.search(r"@(\w+)\s*\{\s*([^,]+),", text[pos:])
        if not m:
            break
        entry_type, key = m.group(1).lower(), m.group(2).strip()
        start = pos + m.end()
        depth = 1
        i = start
        while i < len(text) and depth:
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
            i += 1
        body = text[start:i-1]
        fields = {"ENTRYTYPE": entry_type, "ID": key}
        # This bibliography uses simple field values; nested braces are uncommon.
        field_pat = re.compile(r"(?ms)^\s*(\w+)\s*=\s*\{(.*?)\}\s*,?\s*$")
        for fm in field_pat.finditer(body):
            value = re.sub(r"\s+", " ", fm.group(2)).strip()
            value = value.replace("\\&", "&").replace("\\url", "")
            value = value.replace("{", "").replace("}", "")
            fields[fm.group(1).lower()] = value
        entries[key] = fields
        pos = i
    return entries


def author_initials(author: str) -> str:
    if author.startswith("{") or author.startswith("The ") or author in {"NASA"}:
        return author.strip("{}")
    if "," in author:
        last, first = [p.strip() for p in author.split(",", 1)]
        initials = " ".join((part[0] + ".") for part in re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ]+", first) if part)
        return f"{last}, {initials}".strip()
    parts = author.split()
    if len(parts) <= 1:
        return author
    return f"{parts[-1]}, " + " ".join(p[0] + "." for p in parts[:-1] if p)


def format_authors(raw: str) -> str:
    raw = raw.replace("{{", "{").replace("}}", "}")
    authors = [a.strip() for a in re.split(r"\s+and\s+", raw) if a.strip()]
    formatted = [author_initials(a.strip("{}")) for a in authors]
    if len(formatted) == 1:
        return formatted[0]
    if len(formatted) == 2:
        return f"{formatted[0]}, and {formatted[1]}"
    return ", ".join(formatted[:-1]) + ", and " + formatted[-1]


def clean_title(value: str) -> str:
    return value.replace("\\'e", "e").replace("\\'E", "E")


def format_reference(entry: dict[str, str]) -> str:
    et = entry.get("ENTRYTYPE", "")
    authors = format_authors(entry.get("author", "")) if entry.get("author") else ""
    title = clean_title(entry.get("title", ""))
    year = entry.get("year", "")
    doi = entry.get("doi", "")
    doi_line = f" https://doi.org/{doi}" if doi else ""

    if et == "article":
        journal = entry.get("journal", "")
        volume = entry.get("volume", "")
        number = entry.get("number", "")
        pages = entry.get("pages", "")
        parts = [f'{authors}, “{title},”', journal]
        if volume:
            parts.append(f"Vol. {volume}")
        if number:
            parts.append(f"No. {number}")
        if year:
            parts.append(year)
        if pages:
            parts.append(f"pp. {pages.replace('--', '-')}" if "-" in pages else f"p. {pages}")
        return ", ".join(p for p in parts if p).rstrip(",") + "." + doi_line

    if et == "inproceedings":
        book = entry.get("booktitle", "")
        volume = entry.get("volume", "")
        number = entry.get("number", "")
        pages = entry.get("pages", "")
        parts = [f'{authors}, “{title},”', book]
        if volume:
            parts.append(f"Vol. {volume}")
        if number:
            parts.append(f"No. {number}")
        if year:
            parts.append(year)
        if pages:
            parts.append(f"pp. {pages.replace('--', '-')}")
        return ", ".join(p for p in parts if p).rstrip(",") + "." + doi_line

    if et == "techreport":
        institution = entry.get("institution", "")
        number = entry.get("number", "")
        parts = [authors + "," if authors else "", f'“{title},”', institution, number, year]
        return " ".join(p for p in parts if p).replace(" ,", ",") + "." + doi_line

    if et == "dataset":
        publisher = entry.get("publisher", "")
        version = entry.get("version", "")
        parts = [authors + "," if authors else "", f'“{title},”', publisher]
        if version:
            parts.append(f"Version {version}")
        if year:
            parts.append(year)
        return " ".join(p for p in parts if p).replace(" ,", ",") + "." + doi_line

    # Web, arXiv, software, and other public electronic sources.
    eprint = entry.get("eprint", "")
    how = entry.get("howpublished", "")
    url = entry.get("url", "")
    note = entry.get("note", "")
    parts = [authors + "," if authors else "", f'“{title},”']
    if eprint:
        parts.append(f"arXiv:{eprint},")
    elif how:
        parts.append(how + ",")
    if year:
        parts.append(year + ".")
    if note:
        parts.append(note + ".")
    if doi:
        parts.append(f"https://doi.org/{doi}")
    elif url:
        parts.append(url)
    return " ".join(p for p in parts if p).replace(" ,", ",")


def replace_citations(text: str, bib: dict[str, dict[str, str]]) -> tuple[str, list[str], list[str]]:
    order: list[str] = []
    missing: list[str] = []

    def repl(match: re.Match[str]) -> str:
        content = match.group(1)
        keys = re.findall(r"@([A-Za-z0-9_:\-.]+)", content)
        if not keys:
            return match.group(0)
        nums = []
        for key in keys:
            if key not in bib:
                if key not in missing:
                    missing.append(key)
                continue
            if key not in order:
                order.append(key)
            nums.append(order.index(key) + 1)
        if not nums:
            return match.group(0)
        return "[" + ", ".join(str(n) for n in nums) + "]"

    # All manuscript citations are Pandoc-style bracket citations.
    converted = re.sub(r"\[([^\]]*@[^\]]+)\]", repl, text)
    return converted, order, missing


def csv_to_markdown(path: Path, number: int, caption: str) -> str:
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    if not rows:
        return ""
    width = max(len(r) for r in rows)
    rows = [r + [""] * (width - len(r)) for r in rows]
    def esc(cell: str) -> str:
        return cell.replace("|", "\\|").replace("\n", " ").strip()
    out = [f"**Table {number}. {caption}.**", ""]
    out.append("| " + " | ".join(esc(x) for x in rows[0]) + " |")
    out.append("| " + " | ".join("---" for _ in rows[0]) + " |")
    for row in rows[1:]:
        out.append("| " + " | ".join(esc(x) for x in row) + " |")
    return "\n".join(out)


def jais_endmatter() -> str:
    return """# 7. Declarations, Data Availability, and Reproducibility

## 7.1 Ethics and responsible-research boundary

The reported studies used no human participants and collected no human-subject data. All identities, commands, mission states, evidence conditions, adversary states, and contact conditions were synthetic or software-emulated on researcher-controlled infrastructure. The research did not access an operational spacecraft or ground station, use operational or stolen credentials, transmit or interfere with radio-frequency systems, intercept non-public communications, or use classified or proprietary mission telemetry. Producer-compromise conditions used frozen research keys and software-generated evidence and do not represent compromise of a real mission organization.

## 7.2 Data and code availability

Study 1 is publicly archived on Zenodo as Version 1.0.0, version DOI 10.5281/zenodo.22181540 and concept DOI 10.5281/zenodo.22181539. Its primary statistical population remains exactly 720 valid observations; nine invalid attempts are retained as provenance outside statistical membership.

Study 2 is separately archived on Zenodo as Version 1.0.0, version DOI 10.5281/zenodo.22289114 and concept DOI 10.5281/zenodo.22289113. Its frozen population remains exactly 3,872 valid observations across 85 cells with zero invalid attempts. The publicly served Study-2 source-evidence archive was independently re-downloaded and its checksum matched the frozen source-evidence identity.

The public research repository is https://github.com/Zartharas/mission-aware-satellite-cyber-recovery. Study-1 reproducibility retains a separately reconstructed statistical implementation because the original executable analysis source was not preserved; the reconstruction begins from frozen derived inputs and regression-validates against preserved authoritative outputs. For Study 2, a separate standard-library auditor recomputed all frozen cell summaries, primary contrasts, secondary contrasts, Holm adjustments and rejection flags, and terminal-state distributions with zero mismatches.

The two study populations remain separate and are not pooled. Neither frozen population is extended for this journal export.

## 7.3 Funding

This research was conducted independently and received no external funding.

## 7.4 Competing interests

The author declares no competing financial or non-financial interests.

## 7.5 Author contribution

Aman Kumar Singh: Conceptualization; Methodology; Software; Validation; Formal analysis; Investigation; Resources; Data curation; Writing - original draft; Writing - review and editing; Visualization; Project administration.

## 7.6 Artificial-intelligence disclosure

During preparation of this journal work, the author used OpenAI ChatGPT to assist with manuscript organization, source checking, editorial refinement, consistency review, reproducibility documentation, repository and audit workflow support, and preparation of journal-submission materials. The author reviewed and edited all resulting content, checked scientific quantities and source claims against the frozen research record and cited sources, and takes full responsibility for the manuscript.

For Study 1, this assistance occurred after the experimental campaign and historical statistical findings were frozen and after the evidence package had been archived. For Study 2, the assistance occurred after the campaign evidence and prospective analysis implementation were frozen. It did not generate or replace experimental observations, alter seeds or exclusions, change the frozen statistical populations, modify the frozen Study-2 analyzer, or provide input to the evaluated response policies. The evaluated Study-1 and Study-2 response mechanisms are deterministic rule-based software mechanisms and do not use generative artificial intelligence or machine learning as the scientific response method.
"""


def word_count(text: str) -> int:
    # Strip common Markdown syntax before counting whitespace-delimited words.
    cleaned = re.sub(r"[`*_#>|]", " ", text)
    cleaned = re.sub(r"https?://\S+", "URL", cleaned)
    return len(re.findall(r"\b\S+\b", cleaned))


def hard_gate_audit(manuscript: str, abstract: str, citation_order: list[str], missing: list[str]) -> dict:
    title_words = len(TITLE.split())
    abstract_words = len(abstract.split())
    body_words = word_count(manuscript)
    table_eq = INLINE_TABLE_EQUIVALENT_WORDS + sum(TABLE_EQUIVALENT_WORDS.values())
    equivalent_words = body_words + table_eq

    checks = OrderedDict()
    checks["title_max_12_words"] = title_words <= 12
    checks["abstract_100_200_words"] = 100 <= abstract_words <= 200
    checks["abstract_single_paragraph"] = "\n" not in abstract.strip()
    checks["abstract_no_citation_marker"] = "[@" not in abstract and not re.search(r"\[\d", abstract)
    checks["no_unconverted_pandoc_citations"] = "[@" not in manuscript
    checks["all_citation_keys_resolved"] = not missing
    checks["study1_population_preserved"] = "720" in manuscript and "24" in manuscript
    checks["study2_population_preserved"] = "3,872" in manuscript and "85" in manuscript
    checks["study2_zero_invalid_preserved"] = "zero invalid" in manuscript.lower() or "0 invalid" in manuscript.lower()
    checks["study_populations_not_pooled"] = "not pooled" in manuscript.lower()
    checks["block_c_structural_boundary_present"] = "structural label-invariance" in manuscript.lower()
    checks["k4_nonordinal_boundary_present"] = "K4" in manuscript and "intermittent/flapping" in manuscript
    checks["a2_k2_coupled_boundary_present"] = "A2/K2" in manuscript and "coupled" in manuscript
    checks["logical_time_boundary_present"] = "logical" in manuscript.lower() and "not measured" in manuscript.lower()
    checks["no_weighted_global_rank"] = "No weighted global" in manuscript or "no weighted global" in manuscript
    checks["no_study8_import"] = "Study 8" not in manuscript and "study8" not in manuscript.lower()
    checks["no_c_and_s_target_residue"] = "primary target remains Computers & Security" not in manuscript
    checks["equivalent_word_guideline"] = equivalent_words <= 12000

    return {
        "title": TITLE,
        "title_words": title_words,
        "abstract_words": abstract_words,
        "text_word_count_including_references_and_tables": body_words,
        "display_equivalent_words": table_eq,
        "estimated_aiaa_equivalent_words": equivalent_words,
        "citation_count": len(citation_order),
        "missing_citation_keys": missing,
        "checks": checks,
        "hard_gate_pass": all(v for k, v in checks.items() if k != "equivalent_word_guideline"),
        "length_gate_pass": checks["equivalent_word_guideline"],
    }


def main() -> int:
    GENERATED.mkdir(parents=True, exist_ok=True)

    abstract = extract_abstract()
    keywords = extract_keywords()
    bib = parse_bibtex(read_text(REFERENCES))

    parts = []
    for name in COMPONENTS:
        parts.append(apply_editorial_transform(read_text(MANUSCRIPT / name)).strip())

    body = "\n\n".join(parts)
    # Replace the target-neutral end matter with concise JAIS end matter.
    body = body + "\n\n" + jais_endmatter().strip()

    body, citation_order, missing = replace_citations(body, bib)

    front = f"""# {TITLE}

**Aman Kumar Singh, MS, DSc**  
Independent Researcher, The Woodlands, Texas, United States  
Corresponding author: asingh65430@ucumberlands.edu  
ORCID: 0009-0008-9752-3743

## Abstract

{abstract}

**Keywords:** {keywords}
"""

    tables_md = ["# Main Tables"]
    for number, (filename, caption) in enumerate(MAIN_TABLES.items(), start=1):
        tables_md.append(csv_to_markdown(TABLES / filename, number, caption))

    refs = ["# References"]
    for number, key in enumerate(citation_order, start=1):
        refs.append(f"[{number}] {format_reference(bib[key])}")

    manuscript = front.strip() + "\n\n" + body.strip() + "\n\n" + "\n\n".join(tables_md) + "\n\n" + "\n\n".join(refs) + "\n"

    audit = hard_gate_audit(manuscript, abstract, citation_order, missing)

    (GENERATED / "JAIS_MANUSCRIPT.md").write_text(manuscript, encoding="utf-8")
    (GENERATED / "JAIS_EXPORT_AUDIT.json").write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")

    with (GENERATED / "JAIS_REFERENCE_MAP.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["number", "bibtex_key", "doi", "title"])
        for number, key in enumerate(citation_order, start=1):
            e = bib[key]
            w.writerow([number, key, e.get("doi", ""), e.get("title", "")])

    lines = [
        "# JAIS Export Audit",
        "",
        f"- Title words: {audit['title_words']} / 12",
        f"- Abstract words: {audit['abstract_words']} / 100-200",
        f"- Manuscript text words (including generated references/tables): {audit['text_word_count_including_references_and_tables']}",
        f"- Conservative display-equivalent words: {audit['display_equivalent_words']}",
        f"- Estimated AIAA equivalent words: {audit['estimated_aiaa_equivalent_words']} / 12,000 recommended maximum",
        f"- Numbered references: {audit['citation_count']}",
        f"- Missing citation keys: {', '.join(missing) if missing else 'none'}",
        "",
        "## Checks",
        "",
    ]
    for name, passed in audit["checks"].items():
        lines.append(f"- [{'x' if passed else ' '}] {name}")
    lines.extend([
        "",
        f"**Hard scientific/export gates:** {'PASS' if audit['hard_gate_pass'] else 'FAIL'}",
        f"**AIAA equivalent-length gate:** {'PASS' if audit['length_gate_pass'] else 'REQUIRES EDITORIAL COMPRESSION'}",
        "",
        "This build is not submission authorization. Exact live ScholarOne field lock and separate author authorization remain required before publisher submission.",
    ])
    (GENERATED / "JAIS_EXPORT_AUDIT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"manuscript={GENERATED / 'JAIS_MANUSCRIPT.md'}")
    print(f"audit={GENERATED / 'JAIS_EXPORT_AUDIT.md'}")
    print(f"hard_gate_pass={audit['hard_gate_pass']}")
    print(f"length_gate_pass={audit['length_gate_pass']}")
    print(f"estimated_equivalent_words={audit['estimated_aiaa_equivalent_words']}")
    return 0 if audit["hard_gate_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
