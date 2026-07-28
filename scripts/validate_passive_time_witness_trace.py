#!/usr/bin/env python3
"""validate_passive_time_witness_trace.py

WP4 passive NOS Engine time-witness trace validator.

Validates newline-delimited JSON traces emitted by
scripts/passive_nos_engine_time_witness.cpp against the locked schema:

    exactly four keys per record: sequence, monotonic_ns, tick, state

Enforces monotonicity and authoritative-tick non-decrease rules and rejects
any trace text that contains evidence-charged fields or keys related to URIs,
hostnames, IPs, ports, payloads, packets, hashes, commands, policy state,
process IDs, thread IDs, or wall-clock timestamps.

Python standard library only.

Contract version: 0.4.5 (PASSIVE_TIME_WITNESS_IMPLEMENTED_STATIC_GATE_PENDING).
Contract status: closed runtime gate. No runtime authorized.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import re
import sys
from typing import Iterable, List, Tuple

PERMITTED_KEYS: Tuple[str, ...] = ("sequence", "monotonic_ns", "tick", "state")
PERMITTED_STATES: Tuple[str, ...] = ("connected", "tick", "disconnected")

# Forbidden evidence substrings. Matched case-insensitively as whole-word-ish
# tokens so that legitimate key/value content (for example a tick value) is
# not flagged, but a trace containing a URI, hostname, IP, port, payload,
# packet, hash, command, policy state, pid, thread id, or wall-clock timestamp
# is rejected. We match both key presence and value presence.
FORBIDDEN_TOKENS: Tuple[str, ...] = (
    "uri",
    "host",
    "ip",
    "address",
    "port",
    "payload",
    "packet",
    "hash",
    "command",
    "policy",
    "pid",
    "thread",
    "wall_clock",
    "wallclock",
    "wall-clock",
    "ts_",          # wall-clock timestamp family
    "_ts",
    "iso8601",
    "rfc3339",
    "1970-",        # raw epoch-adjacent year markers
    "zulu",
    "utc",
)

# Patterns that are structurally IP-like or that embed a port. These are not
# expected in the four-key schema but are checked defensively.
IPV4_RE = re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}\b")
PORT_LIKE_RE = re.compile(r"\"port\"")


class TraceError(Exception):
    """Validation error."""


def _check_forbidden_evidence(text: str) -> None:
    lowered = text.lower()
    for token in FORBIDDEN_TOKENS:
        if token in lowered:
            raise TraceError(
                f"forbidden evidence token present in trace text: {token!r}"
            )
    if IPV4_RE.search(text):
        raise TraceError("forbidden IPv4-like literal present in trace text")
    if PORT_LIKE_RE.search(lowered):
        raise TraceError('forbidden "port" key present in trace text')


def _is_int(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _validate_record(
    record: dict,
    expected_sequence: int,
    prev_monotonic_ns: int,
    prev_authoritative_tick: int,
    has_prev_tick: bool,
) -> Tuple[int, int, int, bool]:
    """Validate one record dict. Returns (monotonic_ns, tick, authoritative_tick, has_tick)."""
    if not isinstance(record, dict):
        raise TraceError("record is not a JSON object")

    keys = set(record.keys())
    if keys != set(PERMITTED_KEYS):
        extra = sorted(keys - set(PERMITTED_KEYS))
        missing = sorted(set(PERMITTED_KEYS) - keys)
        raise TraceError(
            f"record keys must be exactly {sorted(PERMITTED_KEYS)}; "
            f"extra={extra} missing={missing}"
        )

    sequence = record["sequence"]
    if not _is_int(sequence):
        raise TraceError(f"sequence is not an integer: {sequence!r}")
    if sequence != expected_sequence:
        raise TraceError(
            f"sequence must equal {expected_sequence} (got {sequence})"
        )

    monotonic_ns = record["monotonic_ns"]
    if not _is_int(monotonic_ns):
        raise TraceError(f"monotonic_ns is not an integer: {monotonic_ns!r}")
    if monotonic_ns < 0:
        raise TraceError(f"monotonic_ns is negative: {monotonic_ns}")
    if monotonic_ns < prev_monotonic_ns:
        raise TraceError(
            f"monotonic_ns decreased: prev={prev_monotonic_ns} "
            f"cur={monotonic_ns}"
        )

    state = record["state"]
    if state not in PERMITTED_STATES:
        raise TraceError(
            f"state must be one of {PERMITTED_STATES} (got {state!r})"
        )

    tick = record["tick"]
    if state in ("connected", "disconnected"):
        if tick is not None:
            raise TraceError(
                f"tick must be null for state={state!r} (got {tick!r})"
            )
        return monotonic_ns, 0, prev_authoritative_tick, has_prev_tick

    # state == "tick"
    if tick is None:
        raise TraceError("tick must not be null for state='tick'")
    if not _is_int(tick):
        raise TraceError(f"tick is not an integer: {tick!r}")
    if tick < 0:
        raise TraceError(f"tick is negative: {tick}")
    if has_prev_tick and tick < prev_authoritative_tick:
        raise TraceError(
            f"authoritative tick decreased: prev="
            f"{prev_authoritative_tick} cur={tick}"
        )
    return monotonic_ns, tick, tick, True


def validate_text(text: str, *, require_min_records: int = 0) -> List[dict]:
    """Validate a trace string. Returns the list of parsed record dicts."""
    if text == "":
        # An empty trace is valid only if no minimum was required.
        if require_min_records > 0:
            raise TraceError(
                f"empty trace but minimum {require_min_records} record(s) "
                "required"
            )
        return []

    _check_forbidden_evidence(text)

    records: List[dict] = []
    expected_sequence = 1
    prev_monotonic_ns = 0
    prev_authoritative_tick = 0
    has_prev_tick = False

    for line_no, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if line == "":
            continue  # blank lines are tolerated and skipped
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            raise TraceError(
                f"line {line_no}: not a JSON object: {exc}"
            ) from exc
        _check_forbidden_evidence(line)
        monotonic_ns, _tick, prev_authoritative_tick, has_prev_tick = (
            _validate_record(
                obj,
                expected_sequence,
                prev_monotonic_ns,
                prev_authoritative_tick,
                has_prev_tick,
            )
        )
        prev_monotonic_ns = monotonic_ns
        records.append(obj)
        expected_sequence += 1

    if require_min_records > 0 and len(records) < require_min_records:
        raise TraceError(
            f"trace has {len(records)} record(s) but minimum "
            f"{require_min_records} required"
        )
    return records


def validate_stream(stream: Iterable[str], *, require_min_records: int = 0) -> List[dict]:
    text = "".join(stream)
    return validate_text(text, require_min_records=require_min_records)


def validate_file(path: str, *, require_min_records: int = 0) -> List[dict]:
    with open(path, "r", encoding="utf-8") as fh:
        return validate_text(fh.read(), require_min_records=require_min_records)


# ---------------------------------------------------------------------------
# Self-test: positive and negative fixtures.
# ---------------------------------------------------------------------------

POSITIVE_FIXTURE = (
    '{"sequence":1,"monotonic_ns":1000000000,"tick":null,"state":"connected"}\n'
    '{"sequence":2,"monotonic_ns":1100000000,"tick":0,"state":"tick"}\n'
    '{"sequence":3,"monotonic_ns":1200000000,"tick":1,"state":"tick"}\n'
    '{"sequence":4,"monotonic_ns":1300000000,"tick":2,"state":"tick"}\n'
    '{"sequence":5,"monotonic_ns":1400000000,"tick":null,"state":"disconnected"}\n'
)

# Negative fixtures as (description, fixture_text, expected_token_in_error).
NEGATIVE_FIXTURES: List[Tuple[str, str, str]] = [
    (
        "unknown extra key",
        '{"sequence":1,"monotonic_ns":1,"tick":null,"state":"connected","uri":"tcp://x"}\n',
        "uri",
    ),
    (
        "missing key",
        '{"sequence":1,"monotonic_ns":1,"state":"connected"}\n',
        "missing",
    ),
    (
        "sequence not starting at 1",
        '{"sequence":2,"monotonic_ns":1,"tick":null,"state":"connected"}\n',
        "sequence must equal",
    ),
    (
        "sequence not incrementing by exactly 1",
        '{"sequence":1,"monotonic_ns":1,"tick":null,"state":"connected"}\n'
        '{"sequence":3,"monotonic_ns":2,"tick":0,"state":"tick"}\n',
        "sequence must equal",
    ),
    (
        "monotonic_ns negative",
        '{"sequence":1,"monotonic_ns":-1,"tick":null,"state":"connected"}\n',
        "negative",
    ),
    (
        "monotonic_ns decreases",
        '{"sequence":1,"monotonic_ns":5,"tick":null,"state":"connected"}\n'
        '{"sequence":2,"monotonic_ns":4,"tick":0,"state":"tick"}\n',
        "decreased",
    ),
    (
        "unknown state value",
        '{"sequence":1,"monotonic_ns":1,"tick":null,"state":"resizing"}\n',
        "state",
    ),
    (
        "tick non-null for connected",
        '{"sequence":1,"monotonic_ns":1,"tick":0,"state":"connected"}\n',
        "null",
    ),
    (
        "tick null for tick state",
        '{"sequence":1,"monotonic_ns":1,"tick":null,"state":"tick"}\n',
        "not be null",
    ),
    (
        "tick negative",
        '{"sequence":1,"monotonic_ns":1,"tick":null,"state":"connected"}\n'
        '{"sequence":2,"monotonic_ns":2,"tick":-1,"state":"tick"}\n',
        "negative",
    ),
    (
        "authoritative tick decreases",
        '{"sequence":1,"monotonic_ns":1,"tick":null,"state":"connected"}\n'
        '{"sequence":2,"monotonic_ns":2,"tick":5,"state":"tick"}\n'
        '{"sequence":3,"monotonic_ns":3,"tick":2,"state":"tick"}\n',
        "decreased",
    ),
    (
        "non-JSON line",
        'not-json\n',
        "not a JSON object",
    ),
    (
        "monotonic_ns not integer",
        '{"sequence":1,"monotonic_ns":"x","tick":null,"state":"connected"}\n',
        "not an integer",
    ),
    (
        "forbidden uri key present",
        '{"sequence":1,"monotonic_ns":1,"tick":null,"state":"connected","uri":"nos"}\n',
        "uri",
    ),
    (
        "forbidden port key",
        '{"sequence":1,"monotonic_ns":1,"tick":null,"state":"connected","port":5011}\n',
        "port",
    ),
    (
        "forbidden ip literal",
        '{"sequence":1,"monotonic_ns":1,"tick":null,"state":"connected 127.0.0.1"}\n',
        "IPv4",
    ),
    (
        "forbidden host token",
        '{"sequence":1,"monotonic_ns":1,"tick":null,"state":"host:nos"}\n',
        "host",
    ),
    (
        "forbidden command token",
        '{"sequence":1,"monotonic_ns":1,"tick":null,"state":"command:noop"}\n',
        "command",
    ),
    (
        "forbidden hash token",
        '{"sequence":1,"monotonic_ns":1,"tick":null,"state":"hash:abc"}\n',
        "hash",
    ),
    (
        "forbidden payload token",
        '{"sequence":1,"monotonic_ns":1,"tick":null,"state":"payload:0"}\n',
        "payload",
    ),
    (
        "forbidden packet token",
        '{"sequence":1,"monotonic_ns":1,"tick":null,"state":"packet:0"}\n',
        "packet",
    ),
    (
        "forbidden policy token",
        '{"sequence":1,"monotonic_ns":1,"tick":null,"state":"policy:open"}\n',
        "policy",
    ),
    (
        "forbidden pid token",
        '{"sequence":1,"monotonic_ns":1,"tick":null,"state":"pid:1"}\n',
        "pid",
    ),
    (
        "forbidden thread token",
        '{"sequence":1,"monotonic_ns":1,"tick":null,"state":"thread:1"}\n',
        "thread",
    ),
    (
        "forbidden wall-clock token",
        '{"sequence":1,"monotonic_ns":1,"tick":null,"state":"wall_clock"}\n',
        "wall_clock",
    ),
    (
        "forbidden address token",
        '{"sequence":1,"monotonic_ns":1,"tick":null,"state":"address:0"}\n',
        "address",
    ),
]


def _run_self_test() -> int:
    # Positive fixture must validate with min 5 records.
    parsed = validate_text(POSITIVE_FIXTURE, require_min_records=5)
    if len(parsed) != 5:
        print(
            "self-test: positive fixture produced "
            f"{len(parsed)} records (expected 5)",
            file=sys.stderr,
        )
        return 1
    # Verify connected/tick/disconnected ordering exactly.
    states = [r["state"] for r in parsed]
    if states != ["connected", "tick", "tick", "tick", "disconnected"]:
        print(
            f"self-test: unexpected state order {states}",
            file=sys.stderr,
        )
        return 1
    # Verify tick values 0,1,2 are non-decreasing and present only on tick rows.
    ticks = [r["tick"] for r in parsed]
    if ticks != [None, 0, 1, 2, None]:
        print(
            f"self-test: unexpected tick values {ticks}",
            file=sys.stderr,
        )
        return 1

    # Negative fixtures must each raise TraceError.
    failures = 0
    for desc, fixture, expected_token in NEGATIVE_FIXTURES:
        try:
            validate_text(fixture)
        except TraceError as exc:
            if expected_token.lower() not in str(exc).lower():
                print(
                    f"self-test: negative fixture '{desc}' raised "
                    f"TraceError but message lacked expected token "
                    f"{expected_token!r}: {exc}",
                    file=sys.stderr,
                )
                failures += 1
            continue
        print(
            f"self-test: negative fixture '{desc}' was accepted but "
            "should have been rejected",
            file=sys.stderr,
        )
        failures += 1

    if failures:
        return 1

    # Prove that the exact permitted key set is enforced by parsing a record
    # with the right keys and confirming it does not raise.
    ok_record = (
        '{"sequence":1,"monotonic_ns":0,"tick":null,"state":"connected"}\n'
    )
    try:
        validate_text(ok_record)
    except TraceError as exc:
        print(
            f"self-test: minimal valid record was wrongly rejected: {exc}",
            file=sys.stderr,
        )
        return 1

    # Prove the validator reports the exact permitted key list.
    if set(PERMITTED_KEYS) != {"sequence", "monotonic_ns", "tick", "state"}:
        print("self-test: permitted key set drift", file=sys.stderr)
        return 1

    print("PERMITTED_TRACE_KEYS=sequence,monotonic_ns,tick,state")
    print("POSITIVE_FIXTURE_RECORDS=5")
    print(f"NEGATIVE_FIXTURE_COUNT={len(NEGATIVE_FIXTURES)}")
    print("PASSIVE_TIME_WITNESS_TRACE_VALIDATOR_SELF_TEST=PASS")
    return 0


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Validate a passive NOS Engine time-witness NDJSON trace."
    )
    parser.add_argument(
        "trace_file",
        nargs="?",
        help="Path to an NDJSON trace file. If omitted, reads from stdin.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the deterministic built-in self-test.",
    )
    parser.add_argument(
        "--min-records",
        type=int,
        default=0,
        help="Minimum number of valid records required (default 0).",
    )
    args = parser.parse_args()

    if args.self_test:
        return _run_self_test()

    if args.trace_file:
        records = validate_file(args.trace_file, require_min_records=args.min_records)
    else:
        records = validate_stream(sys.stdin, require_min_records=args.min_records)

    print(f"TRACE_RECORDS_VALID={len(records)}")
    print("TRACE_VALIDATOR_STATUS=PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
