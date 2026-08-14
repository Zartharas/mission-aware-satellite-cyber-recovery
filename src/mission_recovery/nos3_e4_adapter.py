from __future__ import annotations

import argparse
import hashlib
import json
import socket
import struct
from pathlib import Path
from typing import Any

from .nos3_e1_adapter import ALLOWED_HOST, ALLOWED_PORT

TO_LAB_CMD_MID = 0x18E8
TO_LAB_SEND_HK_MID = 0x18E9
TO_LAB_HK_TLM_MID = 0x08E8
TO_LAB_DATA_TYPES_MID = 0x08E9

TO_LAB_OUTPUT_ENABLE_CC = 2
TO_LAB_SEND_DATA_TYPES_CC = 3


def _command_packet(mid: int, function_code: int, payload: bytes = b"") -> bytes:
    total_size = 8 + len(payload)
    ccsds_length = total_size - 7
    prefix = struct.pack(">HHHB", mid, 0xC000, ccsds_length, function_code)

    value = 0
    for byte in prefix + payload:
        value ^= byte
    checksum = value ^ 0xFF

    packet = prefix + bytes([checksum]) + payload

    verify = 0
    for byte in packet:
        verify ^= byte
    if verify != 0xFF:
        raise RuntimeError("command checksum construction failed")

    return packet


def build_enable_output_packet(destination: str) -> bytes:
    encoded = destination.encode("ascii")
    if len(encoded) > 15:
        raise ValueError("TO_LAB destination must fit in char[16] with terminator")
    payload = encoded + b"\x00" * (16 - len(encoded))
    return _command_packet(TO_LAB_CMD_MID, TO_LAB_OUTPUT_ENABLE_CC, payload)


def build_send_data_types_packet() -> bytes:
    return _command_packet(TO_LAB_CMD_MID, TO_LAB_SEND_DATA_TYPES_CC)


def build_send_housekeeping_packet() -> bytes:
    return _command_packet(TO_LAB_SEND_HK_MID, 0)


def send_once(
    packet: bytes,
    *,
    role: str,
    host: str = ALLOWED_HOST,
    port: int = ALLOWED_PORT,
    sock: socket.socket | Any | None = None,
) -> dict[str, Any]:
    if host != ALLOWED_HOST or port != ALLOWED_PORT:
        raise ValueError("E4 adapter target is restricted to internal nos-fsw:5012")

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
        "event_id": "E4",
        "role": role,
        "target": f"{host}:{port}",
        "datagrams_sent": 1,
        "bytes_sent": sent,
        "packet_hex": packet.hex(),
        "packet_sha256": hashlib.sha256(packet).hexdigest(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command",
        choices=("enable-output", "send-data-types", "send-housekeeping"),
    )
    parser.add_argument("--destination", default="e4-proxy")
    parser.add_argument("--result-json", required=True)
    args = parser.parse_args()

    if args.command == "enable-output":
        packet = build_enable_output_packet(args.destination)
        role = "enable_telemetry_output"
    elif args.command == "send-data-types":
        packet = build_send_data_types_packet()
        role = "generate_high_value_telemetry"
    else:
        packet = build_send_housekeeping_packet()
        role = "generate_retained_housekeeping"

    result = send_once(packet, role=role)
    Path(args.result_json).write_text(
        json.dumps(result, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
