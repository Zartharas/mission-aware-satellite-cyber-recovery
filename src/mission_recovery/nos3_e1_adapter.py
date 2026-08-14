from __future__ import annotations

import argparse
import hashlib
import json
import socket
import struct
from pathlib import Path
from typing import Any

SAMPLE_NOOP_STREAM_ID = 0x18FA
SAMPLE_NOOP_SEQUENCE = 0xC000
SAMPLE_NOOP_LENGTH = 1
SAMPLE_NOOP_FUNCTION_CODE = 0

ALLOWED_HOST = "nos-fsw"
ALLOWED_PORT = 5012


def _checksum(prefix: bytes) -> int:
    value = 0
    for byte in prefix:
        value ^= byte
    return value ^ 0xFF


def build_sample_noop_packet() -> bytes:
    prefix = struct.pack(
        ">HHHB",
        SAMPLE_NOOP_STREAM_ID,
        SAMPLE_NOOP_SEQUENCE,
        SAMPLE_NOOP_LENGTH,
        SAMPLE_NOOP_FUNCTION_CODE,
    )
    return prefix + bytes([_checksum(prefix)])


def validate_e1_instance(instance: dict[str, Any]) -> None:
    if instance["event_id"] != "E1":
        raise ValueError("adapter accepts E1 only")
    if instance["execution_mode"] != "synthetic_model_only":
        raise ValueError("E1 must remain synthetic")
    truth = instance["ground_truth"]
    if truth["command_syntactically_valid"] is not True:
        raise ValueError("E1 command must be syntactically valid")
    if truth["command_authorized"] is not False:
        raise ValueError("E1 authorization ground truth must be false")


def send_e1_once(
    instance: dict[str, Any],
    *,
    host: str = ALLOWED_HOST,
    port: int = ALLOWED_PORT,
    sock: socket.socket | Any | None = None,
) -> dict[str, Any]:
    validate_e1_instance(instance)
    if host != ALLOWED_HOST or port != ALLOWED_PORT:
        raise ValueError("E1 adapter target is restricted to internal nos-fsw:5012")

    packet = build_sample_noop_packet()
    owns_socket = sock is None
    if sock is None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        sent = sock.sendto(packet, (host, port))
    finally:
        if owns_socket:
            sock.close()

    if sent != len(packet):
        raise RuntimeError(f"short UDP send: {sent}/{len(packet)}")

    return {
        "event_id": "E1",
        "target": f"{host}:{port}",
        "datagrams_sent": 1,
        "bytes_sent": sent,
        "packet_hex": packet.hex(),
        "packet_sha256": hashlib.sha256(packet).hexdigest(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event-json", required=True)
    parser.add_argument("--result-json", required=True)
    args = parser.parse_args()

    instance = json.loads(Path(args.event_json).read_text(encoding="utf-8"))
    result = send_e1_once(instance)
    Path(args.result_json).write_text(
        json.dumps(result, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
