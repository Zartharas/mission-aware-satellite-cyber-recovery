#!/usr/bin/env python3
"""Apply the four authorized stale-table cross-reference corrections to the
untracked TAES Paper-2 short-track supplement source.

The patch is bound to the exact pre-correction R8 supplement Markdown SHA-256
and changes only four prose references from legacy R9 table numbers to the
supplementary table numbers S1-S3. It is idempotent after the first successful
application by binding subsequent runs to its locally written correction audit.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "TAES_10P_R3_SUPPLEMENTARY_MATERIAL.md"
AUDIT = ROOT / "TAES_10P_R3_SUPPLEMENTARY_R9_CROSSREF_FIX_AUDIT.txt"

OLD_SHA256 = "e6313fca178f9de40a6b7c28468be6b20ae1fc7249c2e3c8e30ca5fbf0d7027c"

REPLACEMENTS = (
    (
        "Table II values are logical model time, not spacecraft response time, communication latency, operator latency, or ground-contact duration.",
        "Table S1 values are logical model time, not spacecraft response time, communication latency, operator latency, or ground-contact duration.",
        "STUDY3_TABLE_REFERENCE",
    ),
    (
        "Table III gives the complete frozen map as `first/systematic` counts.",
        "Table S2 gives the complete frozen map as `first/systematic` counts.",
        "STUDY4_TABLE_REFERENCE",
    ),
    (
        "Table IV reports the canonical gate summary.",
        "Table S3 reports the canonical gate summary.",
        "STUDY6_GATE_SUMMARY_REFERENCE",
    ),
    (
        "Again, the denominators in Table IV are finite model populations.",
        "Again, the denominators in Table S3 are finite model populations.",
        "STUDY6_DENOMINATOR_REFERENCE",
    ),
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_audit_sha() -> str | None:
    if not AUDIT.is_file():
        return None
    text = AUDIT.read_text(encoding="utf-8", errors="strict")
    match = re.search(r"^corrected_supplement_sha256=([0-9a-f]{64})$", text, re.MULTILINE)
    return match.group(1) if match else None


def validate_corrected(text: str) -> None:
    for old, new, label in REPLACEMENTS:
        if old in text:
            raise SystemExit(f"ERROR: stale cross-reference survived after correction: {label}")
        if text.count(new) != 1:
            raise SystemExit(
                f"ERROR: corrected cross-reference count for {label} is {text.count(new)}, expected 1"
            )
    if "—" in text:
        raise SystemExit("ERROR: em dash detected in corrected supplement source")
    if "6,408" in text:
        raise SystemExit("ERROR: pooled Paper-2 population detected in corrected supplement source")


def main() -> None:
    if not SOURCE.is_file():
        raise SystemExit(f"ERROR: missing supplement source: {SOURCE}")

    current_sha = sha256(SOURCE)
    audit_sha = read_audit_sha()

    if current_sha == OLD_SHA256:
        text = SOURCE.read_text(encoding="utf-8").replace("\r\n", "\n")
        for old, new, label in REPLACEMENTS:
            old_hits = text.count(old)
            new_hits = text.count(new)
            if old_hits != 1 or new_hits != 0:
                raise SystemExit(
                    f"ERROR: pre-patch invariant failed for {label}: old={old_hits} new={new_hits}"
                )
            text = text.replace(old, new, 1)

        validate_corrected(text)
        SOURCE.write_text(text, encoding="utf-8")
        corrected_sha = sha256(SOURCE)
        if corrected_sha == OLD_SHA256:
            raise SystemExit("ERROR: correction did not change supplement source identity")

        audit_lines = [
            "TAES_SUPPLEMENT_R9_CROSSREF_FIX=PASS_APPLIED",
            f"pre_correction_supplement_sha256={OLD_SHA256}",
            f"corrected_supplement_sha256={corrected_sha}",
            "authorized_replacement_count=4",
            "study3_table_reference=TABLE_II_TO_TABLE_S1",
            "study4_table_reference=TABLE_III_TO_TABLE_S2",
            "study6_gate_summary_reference=TABLE_IV_TO_TABLE_S3",
            "study6_denominator_reference=TABLE_IV_TO_TABLE_S3",
            "table_values_changed=NO",
            "experimental_results_changed=NO",
            "science_files_changed=NONE",
            "study_rerun=NO",
            "main_article_changed=NO",
            "frozen_r9_fallback_changed=NO",
            "publisher_facing=NO",
        ]
        AUDIT.write_text("\n".join(audit_lines) + "\n", encoding="utf-8")
        for line in audit_lines:
            print(line)
        return

    if audit_sha and current_sha == audit_sha:
        text = SOURCE.read_text(encoding="utf-8").replace("\r\n", "\n")
        validate_corrected(text)
        print("TAES_SUPPLEMENT_R9_CROSSREF_FIX=PASS_ALREADY_APPLIED")
        print(f"pre_correction_supplement_sha256={OLD_SHA256}")
        print(f"corrected_supplement_sha256={current_sha}")
        print("authorized_replacement_count=4")
        print("table_values_changed=NO")
        print("experimental_results_changed=NO")
        print("science_files_changed=NONE")
        print("study_rerun=NO")
        return

    raise SystemExit(
        "ERROR: supplement source identity is neither the protected R8 source nor the locally audited corrected source: "
        + current_sha
    )


if __name__ == "__main__":
    main()
