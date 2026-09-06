#!/usr/bin/env python3
"""Apply pre-format compliance corrections for TAES Paper 2.

This helper performs only two controlled manuscript-preparation updates:
1. update TUF reference [11] from stale v1.0.33 metadata to the official
   v1.0.36 release record;
2. bind the controlled IEEE AI-use acknowledgment into deterministic assembly.

It does not rerun or alter Study 3, Study 4, or Study 6 science.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent

MANUSCRIPT = ROOT / "TAES_MANUSCRIPT_FULL_DRAFT.md"
FIG_PDF = ROOT / "TAES_FIGURE1_RESIDUAL_BOUNDARIES.pdf"
FIG_PNG = ROOT / "TAES_FIGURE1_RESIDUAL_BOUNDARIES.png"
CORE = ROOT / "TAES_MANUSCRIPT_SOURCE.md"
LEDGER = ROOT / "TAES_LITERATURE_SOURCE_LEDGER.md"
BIB_HELPER = ROOT / "TAES_APPLY_BIBLIOGRAPHY_FIXES.py"
ASSEMBLER = ROOT / "TAES_ASSEMBLE_MANUSCRIPT.py"
ACK = ROOT / "TAES_ACKNOWLEDGMENT_AI_DISCLOSURE.md"

EXPECTED_MANUSCRIPT = "dde7d9c6ab4efb1c6f567937dd1c28c904baeb713dc960b716eae1b15ef5e709"
EXPECTED_FIG_PDF = "4872707261c8a8b6b747e76b9166b4ad7ae426e43d7bd9ffe272e4c5ea6f4ff8"
EXPECTED_FIG_PNG = "7d22964bdae052b35b4680e1b09f3209f1c99bb1d157a0f995dcd2a6445e6698"

OLD_REF = '[11] The Update Framework. "The Update Framework Specification, v1.0.33." Accessed: Sep. 6, 2026. [Online]. Available: https://theupdateframework.io/spec/'
NEW_REF = '[11] The Update Framework. "The Update Framework Specification, v1.0.36." Aug. 10, 2026. [Online]. Available: https://github.com/theupdateframework/specification/releases/tag/v1.0.36'


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read(path: Path) -> str:
    if not path.is_file():
        raise SystemExit(f"ERROR: missing required file: {path}")
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count == 1:
        return text.replace(old, new, 1)
    if count == 0 and new in text:
        return text
    raise SystemExit(f"ERROR: expected one old marker for {label}; found {count}")


def verify_baseline() -> None:
    bindings = [
        (MANUSCRIPT, EXPECTED_MANUSCRIPT),
        (FIG_PDF, EXPECTED_FIG_PDF),
        (FIG_PNG, EXPECTED_FIG_PNG),
    ]
    for path, expected in bindings:
        actual = sha256(path)
        if actual != expected:
            raise SystemExit(
                f"ERROR: baseline binding mismatch for {path.name}: expected={expected} actual={actual}"
            )


def patch_core() -> None:
    text = read(CORE)
    text = replace_once(text, OLD_REF, NEW_REF, "live manuscript TUF reference")
    write(CORE, text)


def patch_ledger() -> None:
    text = read(LEDGER)
    text = replace_once(
        text,
        'The Update Framework, "The Update Framework Specification, v1.0.33," latest stable specification.',
        'The Update Framework, "The Update Framework Specification, v1.0.36," latest stable specification release.',
        "ledger TUF identity",
    )
    text = replace_once(
        text,
        "Official specification page: https://theupdateframework.io/spec/",
        "Official release record: https://github.com/theupdateframework/specification/releases/tag/v1.0.36",
        "ledger TUF URL",
    )
    text = replace_once(
        text,
        "- the official specification page identifies v1.0.33 as the latest stable specification as of 2026-09-06;",
        "- the official specification repository release history identifies v1.0.36 as the latest release as of 2026-09-06;",
        "ledger TUF live verification",
    )
    write(LEDGER, text)


def patch_bibliography_helper() -> None:
    text = read(BIB_HELPER)
    text = text.replace("v1.0.33", "v1.0.36")
    text = text.replace(
        "https://theupdateframework.io/spec/",
        "https://github.com/theupdateframework/specification/releases/tag/v1.0.36",
    )
    text = text.replace(
        "the official specification page identifies v1.0.36 as the latest stable specification as of 2026-09-06;",
        "the official specification repository release history identifies v1.0.36 as the latest release as of 2026-09-06;",
    )
    text = text.replace("Official specification page:", "Official release record:")
    old_final_ref = '[11] The Update Framework. \\\"The Update Framework Specification, v1.0.36.\\\" Accessed: Sep. 6, 2026. [Online]. Available: https://github.com/theupdateframework/specification/releases/tag/v1.0.36'
    new_final_ref = '[11] The Update Framework. \\\"The Update Framework Specification, v1.0.36.\\\" Aug. 10, 2026. [Online]. Available: https://github.com/theupdateframework/specification/releases/tag/v1.0.36'
    text = replace_once(text, old_final_ref, new_final_ref, "rerunnable helper TUF release date")
    write(BIB_HELPER, text)


def patch_assembler() -> None:
    text = read(ASSEMBLER)

    component_marker = '    "TAES_SECTION_IX_CONCLUSION.md",\n]'
    component_replacement = '    "TAES_SECTION_IX_CONCLUSION.md",\n    "TAES_ACKNOWLEDGMENT_AI_DISCLOSURE.md",\n]'
    text = replace_once(text, component_marker, component_replacement, "acknowledgment component registration")

    later_marker = '    later_sections = [normalize_section(read(name)) for name in SECTION_FILES[1:]]\n\n    assembled_parts = ['
    later_replacement = '''    later_sections = [normalize_section(read(name)) for name in SECTION_FILES[1:]]\n\n    ack_doc = read("TAES_ACKNOWLEDGMENT_AI_DISCLOSURE.md")\n    ack_lines = []\n    for line in ack_doc.splitlines():\n        stripped = line.strip()\n        if stripped == "# Acknowledgment":\n            continue\n        if stripped.startswith("> Control note:"):\n            continue\n        ack_lines.append(line)\n    acknowledgment = "\\n".join(ack_lines).strip()\n    if not acknowledgment:\n        raise SystemExit("ERROR: AI-use acknowledgment body is empty")\n\n    assembled_parts = ['''
    text = replace_once(text, later_marker, later_replacement, "acknowledgment extraction")

    parts_marker = '        *later_sections,\n        references,\n    ]'
    parts_replacement = '        *later_sections,\n        "## Acknowledgment\\n\\n" + acknowledgment,\n        references,\n    ]'
    text = replace_once(text, parts_marker, parts_replacement, "acknowledgment assembly order")

    req_marker = '        "## IX. Conclusion",\n        "## References",'
    req_replacement = '        "## IX. Conclusion",\n        "## Acknowledgment",\n        "## References",'
    text = replace_once(text, req_marker, req_replacement, "acknowledgment required marker")

    print_marker = '    print("retired_table_v_check=PASS")\n'
    print_replacement = '    print("retired_table_v_check=PASS")\n    print("ieee_ai_disclosure_binding=PASS")\n'
    text = replace_once(text, print_marker, print_replacement, "acknowledgment PASS output")

    write(ASSEMBLER, text)


def verify() -> None:
    core = read(CORE)
    ledger = read(LEDGER)
    bib_helper = read(BIB_HELPER)
    assembler = read(ASSEMBLER)
    ack = read(ACK)

    if OLD_REF in core or "v1.0.33" in core:
        raise SystemExit("ERROR: stale TUF v1.0.33 remains in live manuscript source")
    if NEW_REF not in core:
        raise SystemExit("ERROR: corrected TUF v1.0.36 reference missing from live manuscript source")
    if "v1.0.36" not in ledger or "releases/tag/v1.0.36" not in ledger:
        raise SystemExit("ERROR: living literature ledger was not corrected to TUF v1.0.36")
    if "v1.0.33" in bib_helper:
        raise SystemExit("ERROR: rerunnable bibliography helper can still regress TUF to v1.0.33")
    if "TAES_ACKNOWLEDGMENT_AI_DISCLOSURE.md" not in assembler:
        raise SystemExit("ERROR: assembler does not bind AI-use acknowledgment component")
    if "## Acknowledgment" not in assembler:
        raise SystemExit("ERROR: assembler does not require Acknowledgment section")
    required_ack = [
        "OpenAI ChatGPT (GPT-5.6 Sol)",
        "Abstract and Sections I-IX",
        "substantive drafting and editorial level",
        "It was not used to generate or modify the frozen experimental results.",
        "assumes responsibility for the final manuscript",
    ]
    for marker in required_ack:
        if marker not in ack:
            raise SystemExit(f"ERROR: required AI-disclosure marker missing: {marker}")


if __name__ == "__main__":
    verify_baseline()
    patch_core()
    patch_ledger()
    patch_bibliography_helper()
    patch_assembler()
    verify()
    print("TAES_PRE_FORMAT_COMPLIANCE_FIXES=PASS")
    print("tuf_reference=V1.0.36_OFFICIAL_RELEASE_RECORD")
    print("ieee_ai_disclosure=BOUND_AS_CONTROLLED_COMPONENT")
    print("science_files_changed=NONE")
    print("NOTE: Re-run TAES_ASSEMBLE_MANUSCRIPT.py and length audit before committing.")
