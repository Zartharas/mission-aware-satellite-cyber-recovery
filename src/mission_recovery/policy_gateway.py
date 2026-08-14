from __future__ import annotations

import argparse
import hashlib
import json
import socket
import time
from pathlib import Path
from typing import Any

from .nos3_e1_adapter import build_sample_noop_packet

GATEWAY_PORT = 19091
TARGET_HOST = "nos-fsw"
TARGET_PORT = 5012
SUPPORTED_ACTIONS = {"OBSERVE_ONLY", "ISOLATE_MODELED_SOURCE"}


def build_e1_envelope(source_id: str) -> dict[str, Any]:
    packet = build_sample_noop_packet()
    return {
        "schema": 1,
        "event_id": "E1",
        "source_id": source_id,
        "command_class": "sample_noop",
        "packet_hex": packet.hex(),
        "packet_sha256": hashlib.sha256(packet).hexdigest(),
    }


def decide_forward(
    action: str,
    envelope: dict[str, Any],
    *,
    isolated_source: str = "modeled_attacker",
) -> bool:
    if action not in SUPPORTED_ACTIONS:
        raise ValueError(f"unsupported gateway action: {action}")
    if action == "OBSERVE_ONLY":
        return True
    return envelope["source_id"] != isolated_source


def _append(path: Path, record: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
        handle.flush()


def run_gateway(
    *,
    action: str,
    truth_jsonl: Path,
    decision_jsonl: Path,
    isolated_source: str,
) -> int:
    if action not in SUPPORTED_ACTIONS:
        raise ValueError(f"unsupported gateway action: {action}")

    incoming = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    incoming.bind(("0.0.0.0", GATEWAY_PORT))
    outgoing = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while True:
        raw, network_source = incoming.recvfrom(65535)
        envelope = json.loads(raw.decode("utf-8"))
        packet = bytes.fromhex(envelope["packet_hex"])
        observed_sha = hashlib.sha256(packet).hexdigest()
        if observed_sha != envelope["packet_sha256"]:
            raise ValueError("envelope packet SHA-256 mismatch")

        _append(
            truth_jsonl,
            {
                "timestamp_ns": time.time_ns(),
                "network_source": f"{network_source[0]}:{network_source[1]}",
                "event_id": envelope["event_id"],
                "source_id": envelope["source_id"],
                "command_class": envelope["command_class"],
                "packet_sha256": observed_sha,
                "packet_hex": packet.hex(),
            },
        )

        forwarded = decide_forward(
            action,
            envelope,
            isolated_source=isolated_source,
        )
        if forwarded:
            sent = outgoing.sendto(packet, (TARGET_HOST, TARGET_PORT))
            if sent != len(packet):
                raise RuntimeError(f"short gateway forward: {sent}/{len(packet)}")

        _append(
            decision_jsonl,
            {
                "timestamp_ns": time.time_ns(),
                "action": action,
                "source_id": envelope["source_id"],
                "command_class": envelope["command_class"],
                "packet_sha256": observed_sha,
                "forwarded": forwarded,
                "target": f"{TARGET_HOST}:{TARGET_PORT}",
            },
        )


def send_envelope(
    *,
    source_id: str,
    gateway_host: str = "wp6-gateway",
) -> dict[str, Any]:
    envelope = build_e1_envelope(source_id)
    encoded = (
        json.dumps(envelope, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sent = sock.sendto(encoded, (gateway_host, GATEWAY_PORT))
    sock.close()
    if sent != len(encoded):
        raise RuntimeError(f"short envelope send: {sent}/{len(encoded)}")

    return {
        "source_id": source_id,
        "gateway": f"{gateway_host}:{GATEWAY_PORT}",
        "datagrams_sent": 1,
        "envelope_bytes_sent": sent,
        "packet_sha256": envelope["packet_sha256"],
        "packet_hex": envelope["packet_hex"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    serve = sub.add_parser("serve")
    serve.add_argument("--action", required=True, choices=sorted(SUPPORTED_ACTIONS))
    serve.add_argument("--truth-jsonl", required=True)
    serve.add_argument("--decision-jsonl", required=True)
    serve.add_argument("--isolated-source", default="modeled_attacker")

    send = sub.add_parser("send")
    send.add_argument("--source-id", required=True)
    send.add_argument("--gateway-host", default="wp6-gateway")
    send.add_argument("--result-json", required=True)

    args = parser.parse_args()

    if args.command == "serve":
        return run_gateway(
            action=args.action,
            truth_jsonl=Path(args.truth_jsonl),
            decision_jsonl=Path(args.decision_jsonl),
            isolated_source=args.isolated_source,
        )

    result = send_envelope(
        source_id=args.source_id,
        gateway_host=args.gateway_host,
    )
    Path(args.result_json).write_text(
        json.dumps(result, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
