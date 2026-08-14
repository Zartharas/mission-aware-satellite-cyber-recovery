from __future__ import annotations

import argparse
import hashlib
import json
import socket
from pathlib import Path
from typing import Any

from .nos3_e1_adapter import (
    ALLOWED_HOST,
    ALLOWED_PORT,
    build_sample_noop_packet,
)


def validate_e2_instance(instance: dict[str, Any]) -> None:
    if instance["event_id"] != "E2":
        raise ValueError("adapter accepts E2 only")
    if instance["execution_mode"] != "synthetic_model_only":
        raise ValueError("E2 must remain synthetic")
    truth = instance["ground_truth"]
    if truth["command_syntactically_valid"] is not True:
        raise ValueError("E2 command must be syntactically valid")
    if truth["replay"] is not True:
        raise ValueError("E2 ground truth must identify a replay")
    if truth["command_authorized"] is not False:
        raise ValueError("E2 replay authorization ground truth must be false")


def send_replay_once(
    instance: dict[str, Any],
    *,
    host: str = ALLOWED_HOST,
    port: int = ALLOWED_PORT,
    sock: socket.socket | Any | None = None,
) -> dict[str, Any]:
    validate_e2_instance(instance)
    if host != ALLOWED_HOST or port != ALLOWED_PORT:
        raise ValueError("E2 adapter target is restricted to internal nos-fsw:5012")

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
        "event_id": "E2",
        "role": "replay_event",
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
    result = send_replay_once(instance)
    Path(args.result_json).write_text(
        json.dumps(result, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
