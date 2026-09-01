#!/usr/bin/env python3
"""Fail closed on known manuscript-bibliography metadata regressions.

This audit is intentionally offline. It does not claim to replace submission-day
publisher/Crossref verification. It protects canonical records whose metadata was
externally re-verified during the 2026-08-31 academic sanity audit, and catches
BibTeX-level DOI collisions that ordinary citation-key resolution cannot detect.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BIB_PATH = ROOT / "references" / "references.bib"

ERRORS: list[str] = []


def fail(message: str) -> None:
    ERRORS.append(message)
    print(f"[FAIL] {message}", file=sys.stderr)


def entry_chunks(text: str) -> dict[str, str]:
    entries: dict[str, str] = {}
    for chunk in re.split(r"(?m)(?=^\s*@)", text):
        match = re.match(r"\s*@\w+\s*\{\s*([^,\s]+)\s*,", chunk)
        if match:
            entries[match.group(1)] = chunk
    return entries


def main() -> int:
    text = BIB_PATH.read_text(encoding="utf-8")
    entries = entry_chunks(text)

    dois = [
        value.strip().lower()
        for value in re.findall(r"(?im)^\s*doi\s*=\s*\{([^}]+)\}\s*,?\s*$", text)
    ]
    duplicate_dois = sorted({doi for doi in dois if dois.count(doi) > 1})
    if duplicate_dois:
        fail(f"duplicate DOI values in references.bib: {duplicate_dois}")

    forbidden = {
        "10.3390/aerospace6010004": (
            "Unrelated Aerospace DOI previously attached to the NOS3 case-study record"
        ),
        "10.17632/7n2d42pm3n.2": (
            "Superseded CuCD-ID v2 DOI; the manuscript bibliography now cites reviewed v3"
        ),
        "pending target-journal convention": (
            "Temporary bibliographic note must not return to the submission bibliography"
        ),
    }
    lower_text = text.lower()
    for token, reason in forbidden.items():
        if token.lower() in lower_text:
            fail(f"forbidden stale bibliography token {token!r}: {reason}")

    canonical: dict[str, tuple[str, ...]] = {
        "thangavel2024trusted": (
            "author={Thangavel, Kathiravan and Sabatini, Roberto and Gardi, Alessandro and Ranasinghe, Kavindu and Hilton, Samuel and Servidia, Pablo and Spiller, Dario}",
            "journal={Progress in Aerospace Sciences}",
            "volume={144}",
            "pages={100960}",
            "year={2024}",
            "doi={10.1016/j.paerosci.2023.100960}",
        ),
        "geletko2019nos3": (
            "NASA Operational Simulator for Small Satellites (NOS3): The STF-1 CubeSat Case Study",
            "author={Geletko, Dustin M. and Grubb, Matthew D. and Lucas, John P. and Morris, Justin R. and Spolaor, Max and Suder, Mark D. and Yokum, Steven C. and Zemerick, Scott A.}",
            "journal={Journal of Small Satellites}",
            "volume={7}",
            "number={3}",
            "pages={789--800}",
            "year={2018}",
        ),
        "lu2024attackrecovery": (
            "author={Lu, Pengyuan and Zhang, Lin and Liu, Mengyu and Sridhar, Kaustubh and Sokolsky, Oleg and Kong, Fanxin and Lee, Insup}",
            "journal={ACM Computing Surveys}",
            "volume={56}",
            "number={8}",
            "pages={211:1--211:31}",
            "doi={10.1145/3653974}",
        ),
        "wanninger2025fdir": (
            "journal={CEAS Space Journal}",
            "volume={18}",
            "pages={991--1004}",
            "year={2026}",
            "doi={10.1007/s12567-025-00651-6}",
        ),
        "cucdid_2026": (
            "version={3}",
            "publisher={Mendeley Data}",
            "doi={10.17632/7n2d42pm3n.3}",
        ),
        "esa_anomaly_2024": (
            "version={1.0}",
            "publisher={European Space Agency}",
            "doi={10.5281/zenodo.12528696}",
        ),
        "opssat_ad_2025": (
            "author={Ruszczak, Bogdan}",
            "year={2024}",
            "version={v2}",
            "doi={10.5281/zenodo.15108715}",
        ),
    }

    for key, required_tokens in canonical.items():
        entry = entries.get(key)
        if entry is None:
            fail(f"canonical bibliography entry missing: {key}")
            continue
        for token in required_tokens:
            if token not in entry:
                fail(f"{key}: externally verified canonical metadata drift: missing {token!r}")

    if ERRORS:
        print(f"bibliography_metadata_audit=FAIL errors={len(ERRORS)}", file=sys.stderr)
        return 1

    print(
        "bibliography_metadata_audit=PASS "
        f"entries={len(entries)} dois={len(dois)} canonical_records={len(canonical)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
