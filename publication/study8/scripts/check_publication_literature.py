#!/usr/bin/env python3
"""Fail closed on verified Study-8 publication bibliography/context metadata.

This is a publication-context checker only. It performs no scientific execution or
statistical analysis.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PUB = ROOT / "publication" / "study8"
BIB = PUB / "references" / "references.bib"
VERIFY = PUB / "literature-verification.md"

ERRORS: list[str] = []


def require(condition: bool, message: str) -> None:
    if not condition:
        ERRORS.append(message)
        print(f"[FAIL] {message}", file=sys.stderr)


def main() -> int:
    print("=== STUDY 8 PUBLICATION LITERATURE VERIFICATION ===")
    bib = BIB.read_text(encoding="utf-8")
    verification = VERIFY.read_text(encoding="utf-8")

    required_bib_tokens = (
        'author = {M{\\"a}hn, Jannik and M{\\"u}ller, Matthias and Zielinski, Karin}',
        'author = {Wildfeuer, Christoph and Jauslin, Timeo and Lavoyer, Alain and Starcik, Milenko and Serra, Afonso and Etesi, Laszlo and Tamburello, Valentina and Huttner, Bruno}',
        'title  = {End-to-End Quantum-Safe Security for Satellite Data Links (E2EQSS)}',
        'author = {Robles, Virgile and Bhargavan, Karthikeyan and Kiefer, Franziskus and Gazagnaire, Thomas}',
        'title  = {Secure Satellite Software-Defined Payloads with High-Assurance Post-Quantum Cryptography}',
        'volume  = {44}',
        'number  = {5}',
        'pages   = {524--543}',
        'doi     = {10.1002/sat.70041}',
        'volume  = {246}',
        'pages   = {863--886}',
        'doi     = {10.1016/j.actaastro.2026.04.041}',
        'volume  = {16}',
        'number  = {2}',
        'pages   = {61--70}',
        'doi     = {10.2514/1.I010693}',
    )
    for token in required_bib_tokens:
        require(token in bib, f"verified bibliography metadata missing: {token}")

    forbidden_bib_tokens = (
        'M{\\"a}hn, Sebastian',
        'M{\\"u}ller, Andreas',
        'Zielinski, Oliver',
        'Wildfeuer, Florian',
        'Robles, Sergio',
        'High-Assurance Post-Quantum Cryptography for Satellite Software-Defined Payloads',
        'and others',
    )
    for token in forbidden_bib_tokens:
        require(token not in bib, f"stale/unverified bibliography metadata remains: {token}")

    keys = re.findall(r"(?m)^@\w+\{([^,]+),", bib)
    require(len(keys) == len(set(keys)), "duplicate Study-8 bibliography keys")

    required_verification_tokens = (
        "PUBLICATION_CONTEXT_VERIFIED_NO_SCIENTIFIC_REEXECUTION",
        "post-quantum cryptography for satellites",
        "crypto agility for space systems",
        "IEEE Systems Journal",
        "Acta Astronautica",
        "International Journal of Satellite Communications and Networking",
        "Computers & Security",
        "does **not** claim novelty",
        "not** evidence that CCSDS standardizes ML-KEM or ML-DSA",
    )
    for token in required_verification_tokens:
        require(token in verification, f"literature-verification boundary missing: {token}")

    print(f"errors={len(ERRORS)}")
    if ERRORS:
        print("study8_publication_literature=FAIL", file=sys.stderr)
        return 1
    print("scientific_reexecution=PROHIBITED")
    print("study8_publication_literature=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
