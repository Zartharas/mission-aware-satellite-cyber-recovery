"""AIAA-oriented reference formatter for the JAIS export."""

from __future__ import annotations

import re

import build_jais_export as base


def _authors(entry: dict[str, str]) -> str:
    return base.format_authors(entry.get("author", "")) if entry.get("author") else ""


def _doi_or_url(entry: dict[str, str]) -> str:
    doi = entry.get("doi", "").strip()
    if doi:
        return f"https://doi.org/{doi}"
    return entry.get("url", "").strip()


def _date(entry: dict[str, str]) -> str:
    month = entry.get("month", "").strip()
    year = entry.get("year", "").strip()
    return " ".join(x for x in (month, year) if x)


def _pages(value: str) -> str:
    return value.replace("--", "–")


def format_reference(entry: dict[str, str]) -> str:
    et = entry.get("ENTRYTYPE", "").lower()
    authors = _authors(entry)
    title = base.clean_title(entry.get("title", ""))
    persistent = _doi_or_url(entry)

    if et == "article":
        pieces = [f'{authors}, “{title},”', entry.get("journal", "")]
        if entry.get("volume"):
            pieces.append(f"Vol. {entry['volume']}")
        if entry.get("number"):
            pieces.append(f"No. {entry['number']}")
        elif entry.get("month"):
            pieces.append(entry["month"])
        if entry.get("year"):
            pieces.append(entry["year"])
        pages = entry.get("pages", "")
        if pages:
            if "--" in pages or "-" in pages or "–" in pages:
                pieces.append(f"pp. {_pages(pages)}")
            elif re.fullmatch(r"\d{5,}", pages):
                pieces.append(f"Article {pages}")
            else:
                pieces.append(f"p. {pages}")
        text = ", ".join(p for p in pieces if p).rstrip(",") + "."
        return text + (f" {persistent}" if persistent else "")

    if et == "inproceedings":
        pieces = [f'{authors}, “{title},”', entry.get("booktitle", "")]
        if entry.get("volume"):
            pieces.append(f"Vol. {entry['volume']}")
        if entry.get("number"):
            pieces.append(f"No. {entry['number']}")
        if entry.get("publisher"):
            pieces.append(entry["publisher"])
        if entry.get("address"):
            pieces.append(entry["address"])
        if _date(entry):
            pieces.append(_date(entry))
        pages = entry.get("pages", "")
        if pages:
            pieces.append(f"pp. {_pages(pages)}")
        text = ", ".join(p for p in pieces if p).rstrip(",") + "."
        return text + (f" {persistent}" if persistent else "")

    if et == "techreport":
        pieces = [f'{authors}, “{title},”', entry.get("institution", ""), entry.get("number", "")]
        if entry.get("address"):
            pieces.append(entry["address"])
        if _date(entry):
            pieces.append(_date(entry))
        text = ", ".join(p for p in pieces if p).rstrip(",") + "."
        return text + (f" {persistent}" if persistent else "")

    if et == "dataset":
        pieces = [f'{authors}, “{title},”', entry.get("publisher", "")]
        if entry.get("version"):
            pieces.append(f"Version {entry['version']}")
        if _date(entry):
            pieces.append(_date(entry))
        text = ", ".join(p for p in pieces if p).rstrip(",") + "."
        return text + (f" {persistent}" if persistent else "")

    eprint = entry.get("eprint", "").strip()
    how = entry.get("howpublished", "").strip()
    pieces = [f'{authors}, “{title},”']
    if eprint:
        pieces.append(f"arXiv:{eprint}")
    elif how:
        pieces.append(how)
    if _date(entry):
        pieces.append(_date(entry))
    if entry.get("note"):
        pieces.append(entry["note"])
    text = ", ".join(p for p in pieces if p).rstrip(",") + "."
    return text + (f" {persistent}" if persistent else "")
