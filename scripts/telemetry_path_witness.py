#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import signal
import socket
import sys
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class WitnessConfig:
    mode: str
    bind_host: str
    bind_port: int
    forward_host: str | None
    forward_port: int | None
    resolve_timeout: float


def validate_config(config: WitnessConfig) -> None:
    if config.mode not in {"proxy", "sink"}:
        raise ValueError("mode must be proxy or sink")
    if not 1 <= config.bind_port <= 65535:
        raise ValueError("bind port is outside 1-65535")
    if config.resolve_timeout <= 0:
        raise ValueError("resolve timeout must be positive")
    if config.mode == "proxy":
        if not config.forward_host or config.forward_port is None:
            raise ValueError("proxy mode requires a forward host and port")
        if not 1 <= config.forward_port <= 65535:
            raise ValueError("forward port is outside 1-65535")
    elif config.forward_host is not None or config.forward_port is not None:
        raise ValueError("sink mode cannot have a forwarding destination")


def packet_digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


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
        time.sleep(0.25)
    raise RuntimeError(f"unable to resolve {host}:{port}: {last_error}")


def self_test() -> int:
    proxy = WitnessConfig("proxy", "0.0.0.0", 5011, "radio-sim", 5011, 5.0)
    sink = WitnessConfig("sink", "0.0.0.0", 8011, None, None, 5.0)
    validate_config(proxy)
    validate_config(sink)
    assert packet_digest(b"telemetry") == "16091175048ac6014be4712b1640c0e3a3272f4fc944e0bee3248f8861b234be"
    for invalid in (
        WitnessConfig("proxy", "0.0.0.0", 5011, None, None, 5.0),
        WitnessConfig("sink", "0.0.0.0", 8011, "radio-sim", 5011, 5.0),
        WitnessConfig("other", "0.0.0.0", 1, None, None, 5.0),
    ):
        try:
            validate_config(invalid)
        except ValueError:
            pass
        else:
            raise AssertionError(f"invalid configuration accepted: {invalid}")
    print("TELEMETRY_PATH_WITNESS_SELF_TEST=PASS", flush=True)
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Telemetry-only UDP witness for the bounded NOS3 downlink diagnostic.")
    parser.add_argument("--mode", choices=("proxy", "sink"))
    parser.add_argument("--bind-host", default="0.0.0.0")
    parser.add_argument("--bind-port", type=int)
    parser.add_argument("--forward-host")
    parser.add_argument("--forward-port", type=int)
    parser.add_argument("--resolve-timeout", type=float, default=45.0)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return self_test()
    if args.mode is None or args.bind_port is None:
        raise SystemExit("--mode and --bind-port are required")

    config = WitnessConfig(
        mode=args.mode,
        bind_host=args.bind_host,
        bind_port=args.bind_port,
        forward_host=args.forward_host,
        forward_port=args.forward_port,
        resolve_timeout=args.resolve_timeout,
    )
    validate_config(config)

    running = True

    def stop_handler(signum: int, frame: object) -> None:
        nonlocal running
        running = False

    signal.signal(signal.SIGTERM, stop_handler)
    signal.signal(signal.SIGINT, stop_handler)

    destination: tuple[str, int] | None = None
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as receiver:
        receiver.bind((config.bind_host, config.bind_port))
        receiver.settimeout(0.5)
        forward_description = "none"
        if config.mode == "proxy":
            forward_description = f"{config.forward_host}:{config.forward_port}:lazy"
        print(
            f"TELEMETRY_WITNESS_READY mode={config.mode} "
            f"bind={config.bind_host}:{config.bind_port} forward={forward_description}",
            flush=True,
        )

        sequence = 0
        while running:
            try:
                payload, source = receiver.recvfrom(65535)
            except socket.timeout:
                continue
            sequence += 1
            digest = packet_digest(payload)
            print(
                f"TELEMETRY_WITNESS_RECEIVED mode={config.mode} sequence={sequence} "
                f"source={source[0]}:{source[1]} length={len(payload)} sha256={digest}",
                flush=True,
            )

            if config.mode == "proxy":
                if destination is None:
                    assert config.forward_host is not None and config.forward_port is not None
                    destination = resolve_ipv4(config.forward_host, config.forward_port, config.resolve_timeout)
                    print(
                        f"TELEMETRY_WITNESS_DESTINATION_RESOLVED mode=proxy "
                        f"host={config.forward_host} ip={destination[0]} port={destination[1]}",
                        flush=True,
                    )
                sent = receiver.sendto(payload, destination)
                if sent != len(payload):
                    print(
                        f"TELEMETRY_WITNESS_INVALID reason=partial_forward sent={sent} expected={len(payload)}",
                        file=sys.stderr,
                        flush=True,
                    )
                    return 3
                print(
                    f"TELEMETRY_WITNESS_FORWARDED mode=proxy sequence={sequence} "
                    f"destination={destination[0]}:{destination[1]} length={sent} sha256={digest}",
                    flush=True,
                )

    print(f"TELEMETRY_WITNESS_STOPPED mode={config.mode} packets={sequence}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
