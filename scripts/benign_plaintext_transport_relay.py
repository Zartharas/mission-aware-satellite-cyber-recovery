#!/usr/bin/env python3
"""Deterministic internal plaintext relay for the WP4 benign baseline.

This relay exists only to validate the nominal CI_LAB/TO_LAB command and
telemetry path before cryptographic semantics are introduced. It has no event
injection capability: the command direction accepts exactly the frozen
SAMPLE_NOOP_CC packet and forwards it at most once. Telemetry datagrams are
forwarded without modification from the radio endpoint to the internal ground
probe.
"""

from __future__ import annotations

import argparse
import hashlib
import selectors
import signal
import socket
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone

EXPECTED_COMMAND = bytes.fromhex("18fac000000100dc")
EXPECTED_COMMAND_SHA256 = "722b8fe72fb18ee581c970ea92c100f435fa90ccccaf0a05bf3e8bee0c4d13bd"


class RelayInvalid(RuntimeError):
    """The relay contract or an internal transport operation failed."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def validate_allowed_command(payload: bytes, command_received: int, command_forwarded: int) -> str:
    digest = sha256_bytes(payload)
    if payload != EXPECTED_COMMAND or digest != EXPECTED_COMMAND_SHA256:
        raise RelayInvalid("received command outside the frozen SAMPLE_NOOP_CC allowlist")
    if command_received != 1 or command_forwarded != 0:
        raise RelayInvalid("more than one command transmission reached the relay")
    return digest


def resolve_ipv4(host: str, port: int, timeout: float) -> tuple[str, int]:
    deadline = time.monotonic() + timeout
    last_error: OSError | None = None
    while time.monotonic() < deadline:
        try:
            results = socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_DGRAM)
            if results:
                return results[0][4][0], port
        except OSError as exc:
            last_error = exc
        time.sleep(0.2)
    raise RelayInvalid(f"could not resolve {host}:{port}: {last_error}")


@dataclass
class RelayCounters:
    command_received: int = 0
    command_forwarded: int = 0
    telemetry_received: int = 0
    telemetry_forwarded: int = 0
    telemetry_bytes: int = 0


class PlaintextRelay:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.running = True
        self.counters = RelayCounters()
        self.command_target: tuple[str, int] | None = None
        self.telemetry_target = resolve_ipv4(args.ground_host, args.ground_telemetry_port, args.resolve_timeout)
        self.command_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.telemetry_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.forward_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        for sock in (self.command_socket, self.telemetry_socket):
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.command_socket.bind((args.bind_host, args.ground_command_port))
        self.telemetry_socket.bind((args.bind_host, args.radio_telemetry_port))
        self.selector = selectors.DefaultSelector()
        self.selector.register(self.command_socket, selectors.EVENT_READ, "command")
        self.selector.register(self.telemetry_socket, selectors.EVENT_READ, "telemetry")

    def stop(self, _signum: int, _frame: object) -> None:
        self.running = False

    def close(self) -> None:
        try:
            self.selector.close()
        finally:
            for sock in (self.command_socket, self.telemetry_socket, self.forward_socket):
                sock.close()

    def handle_command(self) -> None:
        payload, source = self.command_socket.recvfrom(65535)
        self.counters.command_received += 1
        digest = sha256_bytes(payload)
        print(
            "PLAINTEXT_RELAY_COMMAND_RECEIVED "
            f"utc={utc_now()} source={source[0]}:{source[1]} bytes={len(payload)} sha256={digest}",
            flush=True,
        )
        digest = validate_allowed_command(
            payload,
            self.counters.command_received,
            self.counters.command_forwarded,
        )
        if self.command_target is None:
            self.command_target = resolve_ipv4(
                self.args.radio_host,
                self.args.radio_command_port,
                self.args.resolve_timeout,
            )
            print(
                "PLAINTEXT_RELAY_COMMAND_TARGET_RESOLVED "
                f"host={self.args.radio_host} destination={self.command_target[0]}:{self.command_target[1]}",
                flush=True,
            )
        sent = self.forward_socket.sendto(payload, self.command_target)
        if sent != len(payload):
            raise RelayInvalid(f"partial command forward: {sent}/{len(payload)}")
        self.counters.command_forwarded = 1
        print(
            "PLAINTEXT_RELAY_COMMAND_FORWARDED "
            f"utc={utc_now()} destination={self.command_target[0]}:{self.command_target[1]} "
            f"bytes={sent} sha256={digest}",
            flush=True,
        )

    def handle_telemetry(self) -> None:
        payload, source = self.telemetry_socket.recvfrom(65535)
        self.counters.telemetry_received += 1
        self.counters.telemetry_bytes += len(payload)
        sent = self.forward_socket.sendto(payload, self.telemetry_target)
        if sent != len(payload):
            raise RelayInvalid(f"partial telemetry forward: {sent}/{len(payload)}")
        self.counters.telemetry_forwarded += 1
        ordinal = self.counters.telemetry_forwarded
        if ordinal <= 5 or ordinal % 100 == 0:
            stream_id = payload[:2].hex() if len(payload) >= 2 else "short"
            print(
                "PLAINTEXT_RELAY_TELEMETRY_FORWARDED "
                f"utc={utc_now()} ordinal={ordinal} source={source[0]}:{source[1]} "
                f"destination={self.telemetry_target[0]}:{self.telemetry_target[1]} "
                f"bytes={sent} stream_id={stream_id} sha256={sha256_bytes(payload)}",
                flush=True,
            )

    def run(self) -> int:
        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGTERM, self.stop)
        print(
            "PLAINTEXT_RELAY_READY "
            f"command_bind={self.args.bind_host}:{self.args.ground_command_port} "
            f"command_target={self.args.radio_host}:{self.args.radio_command_port}:lazy "
            f"telemetry_bind={self.args.bind_host}:{self.args.radio_telemetry_port} "
            f"telemetry_target={self.telemetry_target[0]}:{self.telemetry_target[1]} "
            f"allowed_command_sha256={EXPECTED_COMMAND_SHA256} maximum_commands=1",
            flush=True,
        )
        try:
            while self.running:
                for key, _mask in self.selector.select(timeout=1.0):
                    if key.data == "command":
                        self.handle_command()
                    else:
                        self.handle_telemetry()
        except (OSError, RelayInvalid) as exc:
            print(f"PLAINTEXT_RELAY_INVALID reason={exc}", file=sys.stderr, flush=True)
            return 3
        finally:
            print(
                "PLAINTEXT_RELAY_STOPPED "
                f"command_received={self.counters.command_received} "
                f"command_forwarded={self.counters.command_forwarded} "
                f"telemetry_received={self.counters.telemetry_received} "
                f"telemetry_forwarded={self.counters.telemetry_forwarded} "
                f"telemetry_bytes={self.counters.telemetry_bytes}",
                flush=True,
            )
            self.close()
        return 0


def expect_invalid(payload: bytes, command_received: int, command_forwarded: int) -> None:
    try:
        validate_allowed_command(payload, command_received, command_forwarded)
    except RelayInvalid:
        return
    raise AssertionError("relay allowlist self-test did not reject invalid command state")


def self_test() -> None:
    assert len(EXPECTED_COMMAND) == 8
    assert EXPECTED_COMMAND.hex() == "18fac000000100dc"
    assert sha256_bytes(EXPECTED_COMMAND) == EXPECTED_COMMAND_SHA256
    assert validate_allowed_command(EXPECTED_COMMAND, 1, 0) == EXPECTED_COMMAND_SHA256
    altered = bytearray(EXPECTED_COMMAND)
    altered[-1] ^= 1
    expect_invalid(bytes(altered), 1, 0)
    expect_invalid(EXPECTED_COMMAND, 2, 0)
    expect_invalid(EXPECTED_COMMAND, 1, 1)
    counters = RelayCounters()
    assert counters.command_received == 0
    assert counters.telemetry_forwarded == 0
    print("BENIGN_PLAINTEXT_TRANSPORT_RELAY_SELF_TEST=PASS")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--bind-host", default="0.0.0.0")
    parser.add_argument("--ground-command-port", type=int, default=6010)
    parser.add_argument("--radio-command-port", type=int, default=8010)
    parser.add_argument("--radio-telemetry-port", type=int, default=8011)
    parser.add_argument("--ground-telemetry-port", type=int, default=6011)
    parser.add_argument("--radio-host", default="radio-sim")
    parser.add_argument("--ground-host", default="ground-probe")
    parser.add_argument("--resolve-timeout", type=float, default=45.0)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.self_test:
        self_test()
        return 0
    ports = (
        args.ground_command_port,
        args.radio_command_port,
        args.radio_telemetry_port,
        args.ground_telemetry_port,
    )
    if any(port < 1 or port > 65535 for port in ports):
        raise SystemExit("invalid UDP port")
    if args.resolve_timeout < 1 or args.resolve_timeout > 120:
        raise SystemExit("--resolve-timeout must be 1-120 seconds")
    try:
        return PlaintextRelay(args).run()
    except (OSError, RelayInvalid) as exc:
        print(f"PLAINTEXT_RELAY_INVALID reason={exc}", file=sys.stderr, flush=True)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
