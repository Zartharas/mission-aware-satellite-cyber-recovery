from __future__ import annotations

import argparse
import hashlib
import json
import socket
import struct
import time
from pathlib import Path
from typing import Any

from .nos3_e1_adapter import (
    SAMPLE_NOOP_LENGTH,
    SAMPLE_NOOP_SEQUENCE,
    SAMPLE_NOOP_STREAM_ID,
)

GATEWAY_PORT = 19091
TARGET_HOST = "nos-fsw"
TARGET_PORT = 5012

SUPPORTED_ACTIONS = {
    "OBSERVE_ONLY",
    "ISOLATE_MODELED_SOURCE",
    "RESTRICT_HIGH_RISK_COMMANDS",
}

COMMAND_FUNCTION_CODES = {
    "sample_noop": 0,
    "sample_reset_counters": 1,
}

HIGH_RISK_COMMAND_CLASSES = {"sample_reset_counters"}


def _checksum(prefix: bytes) -> int:
    value = 0
    for byte in prefix:
        value ^= byte
    return value ^ 0xFF


def build_sample_noargs_packet(command_class: str) -> bytes:
    function_code = COMMAND_FUNCTION_CODES[command_class]
    prefix = struct.pack(
        ">HHHB",
        SAMPLE_NOOP_STREAM_ID,
        SAMPLE_NOOP_SEQUENCE,
        SAMPLE_NOOP_LENGTH,
        function_code,
    )
    return prefix + bytes([_checksum(prefix)])


def build_command_envelope(
    source_id: str,
    command_class: str,
) -> dict[str, Any]:
    packet = build_sample_noargs_packet(command_class)
    return {
        "schema": 1,
        "event_id": "E1",
        "probe_variant": "safe_command_class_selectivity",
        "source_id": source_id,
        "command_class": command_class,
        "declared_risk_class": (
            "high_surrogate"
            if command_class in HIGH_RISK_COMMAND_CLASSES
            else "low"
        ),
        "packet_hex": packet.hex(),
        "packet_sha256": hashlib.sha256(packet).hexdigest(),
    }


def build_e1_envelope(source_id: str) -> dict[str, Any]:
    return build_command_envelope(source_id, "sample_noop")


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

    if action == "ISOLATE_MODELED_SOURCE":
        return envelope["source_id"] != isolated_source

    return envelope["command_class"] not in HIGH_RISK_COMMAND_CLASSES


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
                "probe_variant": envelope["probe_variant"],
                "source_id": envelope["source_id"],
                "command_class": envelope["command_class"],
                "declared_risk_class": envelope["declared_risk_class"],
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
                raise RuntimeError(
                    f"short gateway forward: {sent}/{len(packet)}"
                )

        _append(
            decision_jsonl,
            {
                "timestamp_ns": time.time_ns(),
                "action": action,
                "source_id": envelope["source_id"],
                "command_class": envelope["command_class"],
                "declared_risk_class": envelope["declared_risk_class"],
                "packet_sha256": observed_sha,
                "forwarded": forwarded,
                "target": f"{TARGET_HOST}:{TARGET_PORT}",
            },
        )


def send_envelope(
    *,
    source_id: str,
    command_class: str = "sample_noop",
    gateway_host: str = "wp6-gateway",
) -> dict[str, Any]:
    envelope = build_command_envelope(source_id, command_class)
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
        "command_class": command_class,
        "declared_risk_class": envelope["declared_risk_class"],
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
    serve.add_argument(
        "--action",
        required=True,
        choices=sorted(SUPPORTED_ACTIONS),
    )
    serve.add_argument("--truth-jsonl", required=True)
    serve.add_argument("--decision-jsonl", required=True)
    serve.add_argument("--isolated-source", default="modeled_attacker")

    send = sub.add_parser("send")
    send.add_argument("--source-id", required=True)
    send.add_argument(
        "--command-class",
        choices=sorted(COMMAND_FUNCTION_CODES),
        default="sample_noop",
    )
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
        command_class=args.command_class,
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
