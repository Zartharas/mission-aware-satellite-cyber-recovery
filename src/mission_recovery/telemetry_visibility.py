from __future__ import annotations

import argparse
import json
import socket
import time
from pathlib import Path

HIGH_VALUE_MID = 0x08E9


def packet_mid(payload: bytes) -> int | None:
    if len(payload) < 2:
        return None
    return int.from_bytes(payload[:2], "big")


def should_forward(mode: str, mid: int | None) -> bool:
    return not (mode == "degraded" and mid == HIGH_VALUE_MID)


def _append(path: Path, record: dict) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
        handle.flush()


def run_observer(path: Path, port: int) -> int:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", port))
    while True:
        payload, source = sock.recvfrom(65535)
        _append(
            path,
            {
                "timestamp_ns": time.time_ns(),
                "source": f"{source[0]}:{source[1]}",
                "mid": packet_mid(payload),
                "bytes": len(payload),
                "packet_hex": payload.hex(),
            },
        )


def run_proxy(
    truth_path: Path,
    mode: str,
    listen_port: int,
    policy_host: str,
    policy_port: int,
) -> int:
    if mode not in {"control", "degraded"}:
        raise ValueError("mode must be control or degraded")

    incoming = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    incoming.bind(("0.0.0.0", listen_port))
    forward = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while True:
        payload, source = incoming.recvfrom(65535)
        mid = packet_mid(payload)
        forwarded = should_forward(mode, mid)

        _append(
            truth_path,
            {
                "timestamp_ns": time.time_ns(),
                "mode": mode,
                "mid": mid,
                "bytes": len(payload),
                "packet_hex": payload.hex(),
                "source": f"{source[0]}:{source[1]}",
                "original_destination_port": listen_port,
                "forwarded_to_policy": forwarded,
            },
        )

        if forwarded:
            forward.sendto(payload, (policy_host, policy_port))


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    observer = sub.add_parser("observer")
    observer.add_argument("--jsonl", required=True)
    observer.add_argument("--port", required=True, type=int)

    proxy = sub.add_parser("proxy")
    proxy.add_argument("--truth-jsonl", required=True)
    proxy.add_argument("--mode", choices=("control", "degraded"), required=True)
    proxy.add_argument("--listen-port", required=True, type=int)
    proxy.add_argument("--policy-host", required=True)
    proxy.add_argument("--policy-port", required=True, type=int)

    args = parser.parse_args()

    if args.command == "observer":
        return run_observer(Path(args.jsonl), args.port)

    return run_proxy(
        Path(args.truth_jsonl),
        args.mode,
        args.listen_port,
        args.policy_host,
        args.policy_port,
    )


if __name__ == "__main__":
    raise SystemExit(main())
