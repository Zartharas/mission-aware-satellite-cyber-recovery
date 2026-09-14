from __future__ import annotations

import csv
from dataclasses import dataclass
import hashlib
from io import TextIOWrapper
from pathlib import Path
from typing import Iterator, Mapping
from zipfile import BadZipFile, ZipFile


class InputIdentityError(RuntimeError):
    """Raised when a canonical source fails a frozen identity or shape check."""


@dataclass(frozen=True)
class InputIdentitySpec:
    dataset_id: str
    source_kind: str
    source_path: Path
    canonical_artifact_path: str
    canonical_artifact_sha256: str
    expected_rows: int
    expected_columns: int
    outer_container_sha256: str | None = None

    def __post_init__(self) -> None:
        if self.source_kind not in {"DIRECT_CSV", "ZIP_CSV_MEMBER"}:
            raise ValueError(f"unsupported source kind: {self.source_kind}")
        if not self.dataset_id:
            raise ValueError("dataset_id is required")
        if not self.canonical_artifact_path:
            raise ValueError("canonical_artifact_path is required")
        if len(self.canonical_artifact_sha256) != 64:
            raise ValueError("canonical_artifact_sha256 must be a SHA-256 hex digest")
        if self.expected_rows < 0 or self.expected_columns <= 0:
            raise ValueError("expected shape must be non-negative rows and positive columns")
        if self.source_kind == "ZIP_CSV_MEMBER" and not self.outer_container_sha256:
            raise ValueError("ZIP sources require a frozen outer-container SHA-256")


@dataclass(frozen=True)
class VerifiedCsvSource:
    spec: InputIdentitySpec
    header: tuple[str, ...]
    row_count: int
    column_count: int
    artifact_sha256: str
    outer_container_sha256: str | None


def _sha256_binary_stream(handle) -> str:
    digest = hashlib.sha256()
    for block in iter(lambda: handle.read(1024 * 1024), b""):
        digest.update(block)
    return digest.hexdigest()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
    except OSError as exc:
        raise InputIdentityError(f"cannot read source path {path}: {exc}") from exc
    return digest.hexdigest()


def _validate_header(header: list[str], expected_columns: int) -> tuple[str, ...]:
    if len(header) != expected_columns:
        raise InputIdentityError(
            f"header column count mismatch: observed={len(header)} expected={expected_columns}"
        )
    if any(name == "" for name in header):
        raise InputIdentityError("CSV header contains an empty field name")
    if len(header) != len(set(header)):
        raise InputIdentityError("CSV header contains duplicate field names")
    return tuple(header)


def _inspect_csv_reader(reader: csv.reader, spec: InputIdentitySpec) -> tuple[tuple[str, ...], int]:
    try:
        header_list = next(reader)
    except StopIteration as exc:
        raise InputIdentityError("canonical CSV is empty") from exc
    header = _validate_header(header_list, spec.expected_columns)
    row_count = 0
    for row_count, row in enumerate(reader, start=1):
        if len(row) != spec.expected_columns:
            raise InputIdentityError(
                f"row-width mismatch at data row {row_count}: "
                f"observed={len(row)} expected={spec.expected_columns}"
            )
    if row_count != spec.expected_rows:
        raise InputIdentityError(
            f"row-count mismatch: observed={row_count} expected={spec.expected_rows}"
        )
    return header, row_count


def _unique_zip_member(archive: ZipFile, member_path: str):
    matches = [info for info in archive.infolist() if info.filename == member_path]
    if len(matches) != 1:
        raise InputIdentityError(
            f"ZIP member identity mismatch for {member_path!r}: found {len(matches)} exact matches"
        )
    return matches[0]


def verify_csv_source(spec: InputIdentitySpec) -> VerifiedCsvSource:
    """Verify frozen bytes and CSV shape before any semantic row processing."""
    path = Path(spec.source_path)
    if not path.is_file():
        raise InputIdentityError(f"source path is not a regular file: {path}")

    if spec.source_kind == "DIRECT_CSV":
        artifact_sha = sha256_path(path)
        if artifact_sha != spec.canonical_artifact_sha256:
            raise InputIdentityError(
                f"artifact SHA-256 mismatch for {spec.dataset_id}: "
                f"{artifact_sha} != {spec.canonical_artifact_sha256}"
            )
        try:
            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                header, row_count = _inspect_csv_reader(csv.reader(handle), spec)
        except UnicodeError as exc:
            raise InputIdentityError(f"canonical CSV is not valid UTF-8: {exc}") from exc
        return VerifiedCsvSource(
            spec=spec,
            header=header,
            row_count=row_count,
            column_count=len(header),
            artifact_sha256=artifact_sha,
            outer_container_sha256=None,
        )

    outer_sha = sha256_path(path)
    if outer_sha != spec.outer_container_sha256:
        raise InputIdentityError(
            f"outer-container SHA-256 mismatch for {spec.dataset_id}: "
            f"{outer_sha} != {spec.outer_container_sha256}"
        )
    try:
        with ZipFile(path, "r") as archive:
            member = _unique_zip_member(archive, spec.canonical_artifact_path)
            with archive.open(member, "r") as raw:
                artifact_sha = _sha256_binary_stream(raw)
            if artifact_sha != spec.canonical_artifact_sha256:
                raise InputIdentityError(
                    f"artifact SHA-256 mismatch for {spec.dataset_id}: "
                    f"{artifact_sha} != {spec.canonical_artifact_sha256}"
                )
            with archive.open(member, "r") as raw:
                with TextIOWrapper(raw, encoding="utf-8-sig", newline="") as text:
                    header, row_count = _inspect_csv_reader(csv.reader(text), spec)
    except (BadZipFile, OSError, UnicodeError) as exc:
        if isinstance(exc, InputIdentityError):
            raise
        raise InputIdentityError(f"cannot verify ZIP-backed CSV {path}: {exc}") from exc

    return VerifiedCsvSource(
        spec=spec,
        header=header,
        row_count=row_count,
        column_count=len(header),
        artifact_sha256=artifact_sha,
        outer_container_sha256=outer_sha,
    )


def _iter_csv_reader_rows(reader: csv.reader, verified: VerifiedCsvSource) -> Iterator[Mapping[str, str]]:
    try:
        header_list = next(reader)
    except StopIteration as exc:
        raise InputIdentityError("canonical CSV became empty after verification") from exc
    header = tuple(header_list)
    if header != verified.header:
        raise InputIdentityError("CSV header changed after identity verification")
    count = 0
    for count, row in enumerate(reader, start=1):
        if len(row) != verified.column_count:
            raise InputIdentityError(
                f"row-width changed after verification at data row {count}: "
                f"observed={len(row)} expected={verified.column_count}"
            )
        yield dict(zip(header, row, strict=True))
    if count != verified.row_count:
        raise InputIdentityError(
            f"row count changed after verification: observed={count} expected={verified.row_count}"
        )


def iter_verified_rows(
    spec: InputIdentitySpec,
    verified: VerifiedCsvSource,
) -> Iterator[Mapping[str, str]]:
    """Stream rows only from a source already verified against the same frozen spec."""
    if verified.spec != spec:
        raise InputIdentityError("verified source does not belong to the supplied identity spec")
    path = Path(spec.source_path)

    if spec.source_kind == "DIRECT_CSV":
        try:
            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                yield from _iter_csv_reader_rows(csv.reader(handle), verified)
        except (OSError, UnicodeError) as exc:
            raise InputIdentityError(f"cannot stream verified CSV {path}: {exc}") from exc
        return

    try:
        with ZipFile(path, "r") as archive:
            member = _unique_zip_member(archive, spec.canonical_artifact_path)
            with archive.open(member, "r") as raw:
                with TextIOWrapper(raw, encoding="utf-8-sig", newline="") as text:
                    yield from _iter_csv_reader_rows(csv.reader(text), verified)
    except (BadZipFile, OSError, UnicodeError) as exc:
        raise InputIdentityError(f"cannot stream verified ZIP-backed CSV {path}: {exc}") from exc
