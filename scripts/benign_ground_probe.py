#!/usr/bin/env python3
"""Deterministic internal ground probe for the WP4 benign baseline.

This program has no event-injection capability. It binds the internal telemetry
endpoint, waits for an orchestration trigger, transmits exactly one recorded
TO_ENABLE_OUTPUT setup command, establishes a stable SAMPLE housekeeping
baseline, transmits exactly one frozen SAMPLE_NOOP_CC measured command, and
records separated immutable-ground and policy-visible evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import socket
import struct
import sys
import time
from collections import deque
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, TextIO

TO_COMMAND_MID = 0x1880
TO_ENABLE_OUTPUT_FC = 2
TO_ENABLE_OUTPUT_LENGTH_FIELD = 19
TO_DESTINATION_HOST = "radio-sim"
TO_DESTINATION_PORT = 5011
EXPECTED_TO_ENABLE_OUTPUT_PACKET = bytes.fromhex(
    "1880c0000013021d726164696f2d73696d000000000000009313"
)
EXPECTED_TO_ENABLE_OUTPUT_PACKET_SHA256 = (
    "c9b26e373b21170039deb6ab4d54c49401581eae5d8f3d1eaf304e65f300d3bb"
)

SAMPLE_COMMAND_MID = 0x18FA
SAMPLE_HK_MID = 0x08FA
SAMPLE_NOOP_FC = 0
INITIAL_SEQUENCE_CONTROL = 0xC000
NOOP_PACKET_LENGTH_FIELD = 1
CCSDS_PRIMARY_HEADER_LENGTH = 6
CFE_TLM_SECONDARY_HEADER_LENGTH = 6
SAMPLE_HK_COUNTER_OFFSET = CCSDS_PRIMARY_HEADER_LENGTH + CFE_TLM_SECONDARY_HEADER_LENGTH
EXPECTED_NOOP_PACKET = bytes.fromhex("18fac000000100dc")
EXPECTED_NOOP_PACKET_SHA256 = "722b8fe72fb18ee581c970ea92c100f435fa90ccccaf0a05bf3e8bee0c4d13bd"


class RunInvalid(RuntimeError):
    """Infrastructure, parsing, construction, or evidence failure."""


class BaselineFail(RuntimeError):
    """Healthy infrastructure with a failed benign command assertion."""


@dataclass(frozen=True)
class SampleHousekeeping:
    received_utc: str
    monotonic_ns: int
    source_ip: str
    source_port: int
    packet_length: int
    packet_sha256: str
    cmd_err_count: int
    cmd_count: int
    device_err_count: int

    @property
    def counters(self) -> tuple[int, int, int]:
        return (self.cmd_count, self.cmd_err_count, self.device_err_count)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def cfs_xor_checksum(payload: bytes) -> int:
    checksum = 0xFF
    for byte in payload:
        checksum ^= byte
    return checksum


def build_to_enable_output_packet() -> bytes:
    destination = TO_DESTINATION_HOST.encode("ascii")
    if len(destination) > 16:
        raise RunInvalid("TO destination hostname exceeds the frozen 16-byte field")
    packet = bytearray(
        struct.pack(
            ">HHHBB",
            TO_COMMAND_MID,
            INITIAL_SEQUENCE_CONTROL,
            TO_ENABLE_OUTPUT_LENGTH_FIELD,
            TO_ENABLE_OUTPUT_FC,
            0,
        )
        + destination.ljust(16, b"\x00")
        + struct.pack("<H", TO_DESTINATION_PORT)
    )
    packet[7] = cfs_xor_checksum(packet)
    result = bytes(packet)
    validate_to_enable_output_packet(result)
    return result


def validate_to_enable_output_packet(packet: bytes) -> None:
    if len(packet) != 26:
        raise RunInvalid(f"TO_ENABLE_OUTPUT packet length is {len(packet)}, expected 26")
    mid, sequence, length_field, function_code, _checksum = struct.unpack_from(">HHHBB", packet, 0)
    expected = (
        TO_COMMAND_MID,
        INITIAL_SEQUENCE_CONTROL,
        TO_ENABLE_OUTPUT_LENGTH_FIELD,
        TO_ENABLE_OUTPUT_FC,
    )
    observed = (mid, sequence, length_field, function_code)
    if observed != expected:
        raise RunInvalid(f"TO_ENABLE_OUTPUT field mismatch: observed={observed!r} expected={expected!r}")
    destination = packet[8:24].split(b"\x00", 1)[0].decode("ascii")
    destination_port = struct.unpack_from("<H", packet, 24)[0]
    if destination != TO_DESTINATION_HOST or destination_port != TO_DESTINATION_PORT:
        raise RunInvalid(
            "TO_ENABLE_OUTPUT destination mismatch: "
            f"observed={destination}:{destination_port} "
            f"expected={TO_DESTINATION_HOST}:{TO_DESTINATION_PORT}"
        )
    if cfs_xor_checksum(packet) != 0:
        raise RunInvalid("TO_ENABLE_OUTPUT checksum validation failed")
    if packet != EXPECTED_TO_ENABLE_OUTPUT_PACKET:
        raise RunInvalid(f"TO_ENABLE_OUTPUT vector mismatch: {packet.hex()}")
    if sha256_bytes(packet) != EXPECTED_TO_ENABLE_OUTPUT_PACKET_SHA256:
        raise RunInvalid("TO_ENABLE_OUTPUT SHA-256 mismatch")


def build_sample_noop_packet() -> bytes:
    packet = bytearray(
        struct.pack(
            ">HHHBB",
            SAMPLE_COMMAND_MID,
            INITIAL_SEQUENCE_CONTROL,
            NOOP_PACKET_LENGTH_FIELD,
            SAMPLE_NOOP_FC,
            0,
        )
    )
    packet[-1] = cfs_xor_checksum(packet)
    result = bytes(packet)
    validate_sample_noop_packet(result)
    return result


def validate_sample_noop_packet(packet: bytes) -> None:
    if len(packet) != 8:
        raise RunInvalid(f"SAMPLE_NOOP_CC packet length is {len(packet)}, expected 8")
    mid, sequence, length_field, function_code, _checksum = struct.unpack(">HHHBB", packet)
    expected = (SAMPLE_COMMAND_MID, INITIAL_SEQUENCE_CONTROL, NOOP_PACKET_LENGTH_FIELD, SAMPLE_NOOP_FC)
    observed = (mid, sequence, length_field, function_code)
    if observed != expected:
        raise RunInvalid(f"SAMPLE_NOOP_CC field mismatch: observed={observed!r} expected={expected!r}")
    if cfs_xor_checksum(packet) != 0:
        raise RunInvalid("SAMPLE_NOOP_CC checksum validation failed")
    if packet != EXPECTED_NOOP_PACKET:
        raise RunInvalid(f"SAMPLE_NOOP_CC vector mismatch: {packet.hex()}")
    if sha256_bytes(packet) != EXPECTED_NOOP_PACKET_SHA256:
        raise RunInvalid("SAMPLE_NOOP_CC SHA-256 mismatch")


def parse_sample_housekeeping(payload: bytes, source: tuple[str, int]) -> SampleHousekeeping | None:
    if len(payload) < CCSDS_PRIMARY_HEADER_LENGTH:
        return None
    stream_id, _sequence, length_field = struct.unpack_from(">HHH", payload, 0)
    if stream_id != SAMPLE_HK_MID:
        return None
    expected_length = length_field + 7
    if expected_length != len(payload):
        raise RunInvalid(
            f"SAMPLE_HK_TLM length mismatch: header={expected_length} datagram={len(payload)}"
        )
    minimum_length = SAMPLE_HK_COUNTER_OFFSET + 3
    if len(payload) < minimum_length:
        raise RunInvalid(
            f"SAMPLE_HK_TLM is too short for required counters: {len(payload)} < {minimum_length}"
        )
    cmd_err_count = payload[SAMPLE_HK_COUNTER_OFFSET]
    cmd_count = payload[SAMPLE_HK_COUNTER_OFFSET + 1]
    device_err_count = payload[SAMPLE_HK_COUNTER_OFFSET + 2]
    return SampleHousekeeping(
        received_utc=utc_now(),
        monotonic_ns=time.monotonic_ns(),
        source_ip=source[0],
        source_port=source[1],
        packet_length=len(payload),
        packet_sha256=sha256_bytes(payload),
        cmd_err_count=cmd_err_count,
        cmd_count=cmd_count,
        device_err_count=device_err_count,
    )


def expected_post_count(before: int) -> int:
    return (before + 1) % 256


def append_jsonl(handle: TextIO, record: dict[str, Any]) -> None:
    handle.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
    handle.flush()
    os.fsync(handle.fileno())


def atomic_write_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("wb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    temporary.replace(path)


def atomic_write_json(path: Path, record: dict[str, Any]) -> None:
    payload = (json.dumps(record, indent=2, sort_keys=True) + "\n").encode("utf-8")
    atomic_write_bytes(path, payload)


def write_hash_manifest(directory: Path) -> str:
    manifest = directory / "sha256-manifest.txt"
    entries: list[str] = []
    for path in sorted(directory.rglob("*")):
        if not path.is_file() or path == manifest or path.name.endswith(".tmp"):
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        entries.append(f"{digest}  {path.relative_to(directory).as_posix()}")
    atomic_write_bytes(manifest, ("\n".join(entries) + "\n").encode("utf-8"))
    return hashlib.sha256(manifest.read_bytes()).hexdigest()


def policy_record(hk: SampleHousekeeping) -> dict[str, Any]:
    return {
        "received_utc": hk.received_utc,
        "monotonic_ns": hk.monotonic_ns,
        "packet": "SAMPLE_HK_TLM",
        "cmd_count": hk.cmd_count,
        "cmd_err_count": hk.cmd_err_count,
        "device_err_count": hk.device_err_count,
    }


class GroundProbe:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.ground_dir = Path(args.ground_dir)
        self.policy_dir = Path(args.policy_dir)
        self.start_trigger = (
            Path(args.start_trigger)
            if args.start_trigger
            else self.ground_dir / "start-baseline.trigger"
        )
        self.ground_dir.mkdir(parents=True, exist_ok=True)
        self.policy_dir.mkdir(parents=True, exist_ok=True)
        self.ground_events = (self.ground_dir / "telemetry-events.jsonl").open(
            "a", encoding="utf-8", buffering=1
        )
        self.policy_events = (self.policy_dir / "telemetry.jsonl").open(
            "a", encoding="utf-8", buffering=1
        )
        self.sample_packets_received = 0
        self.setup_command_transmissions = 0
        self.command_transmissions = 0
        self.before: SampleHousekeeping | None = None
        self.after: SampleHousekeeping | None = None
        self.setup_command_sent_utc: str | None = None
        self.setup_command_sent_monotonic_ns: int | None = None
        self.command_sent_utc: str | None = None
        self.command_sent_monotonic_ns: int | None = None
        self.setup_command_packet = build_to_enable_output_packet()
        self.command_packet = build_sample_noop_packet()

    def close(self) -> None:
        for handle in (self.ground_events, self.policy_events):
            if not handle.closed:
                handle.flush()
                os.fsync(handle.fileno())
                handle.close()

    def wait_for_start_trigger(self) -> None:
        deadline = time.monotonic() + self.args.trigger_timeout
        while time.monotonic() < deadline:
            if self.start_trigger.is_file():
                print(
                    f"GROUND_PROBE_TRIGGER_OBSERVED path={self.start_trigger}",
                    flush=True,
                )
                return
            time.sleep(0.2)
        raise RunInvalid(f"timed out waiting for orchestration trigger: {self.start_trigger}")

    def transmit_packet(self, packet: bytes, label: str) -> tuple[str, int]:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as command_socket:
            command_socket.settimeout(5.0)
            try:
                sent = command_socket.sendto(
                    packet, (self.args.command_host, self.args.command_port)
                )
            except OSError as exc:
                raise RunInvalid(f"{label} transmission failed: {exc}") from exc
        if sent != len(packet):
            raise RunInvalid(f"partial {label} transmission: {sent}/{len(packet)}")
        return utc_now(), time.monotonic_ns()

    def send_setup_command(self) -> None:
        validate_to_enable_output_packet(self.setup_command_packet)
        atomic_write_bytes(
            self.ground_dir / "transmitted-setup-command.bin",
            self.setup_command_packet,
        )
        sent_utc, sent_monotonic_ns = self.transmit_packet(
            self.setup_command_packet, "TO_ENABLE_OUTPUT"
        )
        self.setup_command_transmissions += 1
        if self.setup_command_transmissions != 1:
            raise RunInvalid("more than one TO_ENABLE_OUTPUT setup transmission was attempted")
        self.setup_command_sent_utc = sent_utc
        self.setup_command_sent_monotonic_ns = sent_monotonic_ns
        print(
            "GROUND_PROBE_SETUP_COMMAND_SENT "
            f"bytes={len(self.setup_command_packet)} "
            f"sha256={sha256_bytes(self.setup_command_packet)}",
            flush=True,
        )

    def record_telemetry(self, payload: bytes, source: tuple[str, int]) -> SampleHousekeeping | None:
        hk = parse_sample_housekeeping(payload, source)
        if hk is None:
            return None
        self.sample_packets_received += 1
        ground = asdict(hk)
        ground["packet"] = "SAMPLE_HK_TLM"
        ground["ordinal"] = self.sample_packets_received
        append_jsonl(self.ground_events, ground)
        append_jsonl(self.policy_events, policy_record(hk))
        return hk

    def receive_hk(self, telemetry_socket: socket.socket, deadline: float) -> tuple[SampleHousekeeping, bytes]:
        while time.monotonic() < deadline:
            try:
                payload, source = telemetry_socket.recvfrom(65535)
            except socket.timeout:
                continue
            hk = self.record_telemetry(payload, source)
            if hk is not None:
                return hk, payload
        raise RunInvalid("timed out waiting for SAMPLE_HK_TLM")

    def establish_stable_baseline(
        self, telemetry_socket: socket.socket
    ) -> tuple[SampleHousekeeping, list[tuple[SampleHousekeeping, bytes]]]:
        deadline = time.monotonic() + self.args.readiness_timeout
        stable: deque[tuple[SampleHousekeeping, bytes]] = deque(maxlen=self.args.minimum_stable)
        previous_counters: tuple[int, int, int] | None = None
        while time.monotonic() < deadline:
            hk, payload = self.receive_hk(telemetry_socket, deadline)
            if hk.counters == previous_counters:
                stable.append((hk, payload))
            else:
                stable.clear()
                stable.append((hk, payload))
                previous_counters = hk.counters
            if len(stable) >= self.args.minimum_stable:
                baseline = stable[-1][0]
                print(
                    "GROUND_PROBE_PRECOMMAND_STABLE "
                    f"cmd_count={baseline.cmd_count} cmd_err_count={baseline.cmd_err_count} "
                    f"device_err_count={baseline.device_err_count}",
                    flush=True,
                )
                return baseline, list(stable)
        raise RunInvalid("stable pre-command SAMPLE_HK_TLM baseline was not established")

    def send_command(self) -> None:
        validate_sample_noop_packet(self.command_packet)
        atomic_write_bytes(self.ground_dir / "transmitted-command.bin", self.command_packet)
        sent_utc, sent_monotonic_ns = self.transmit_packet(
            self.command_packet, "SAMPLE_NOOP_CC"
        )
        self.command_transmissions += 1
        if self.command_transmissions != 1:
            raise RunInvalid("more than one measured command transmission was attempted")
        self.command_sent_utc = sent_utc
        self.command_sent_monotonic_ns = sent_monotonic_ns
        print(
            "GROUND_PROBE_COMMAND_SENT "
            f"bytes={len(self.command_packet)} sha256={sha256_bytes(self.command_packet)}",
            flush=True,
        )

    def await_acceptance(self, telemetry_socket: socket.socket) -> tuple[SampleHousekeeping, bytes]:
        if self.before is None or self.command_sent_monotonic_ns is None:
            raise RunInvalid("acceptance evaluation started without a baseline or send timestamp")
        deadline = time.monotonic() + self.args.acceptance_timeout
        expected_count = expected_post_count(self.before.cmd_count)
        while time.monotonic() < deadline:
            hk, payload = self.receive_hk(telemetry_socket, deadline)
            if hk.cmd_err_count != self.before.cmd_err_count:
                raise BaselineFail(
                    f"CMD_ERR_COUNT changed {self.before.cmd_err_count}->{hk.cmd_err_count}"
                )
            if hk.device_err_count != self.before.device_err_count:
                raise BaselineFail(
                    f"DEVICE_ERR_COUNT changed {self.before.device_err_count}->{hk.device_err_count}"
                )
            if hk.cmd_count == self.before.cmd_count:
                continue
            if hk.cmd_count != expected_count:
                raise RunInvalid(
                    f"unexpected CMD_COUNT transition {self.before.cmd_count}->{hk.cmd_count}; expected {expected_count}"
                )
            return hk, payload
        raise BaselineFail("SAMPLE_NOOP_CC acceptance transition was not observed within the timeout")

    def finalize(self, classification: str, reason: str | None = None) -> tuple[str, str]:
        self.close()
        result: dict[str, Any] = {
            "run_id": self.args.run_id,
            "classification": classification,
            "reason": reason,
            "event_injection": "disabled",
            "setup_command": {
                "name": "TO_ENABLE_OUTPUT",
                "message_id_hex": "0x1880",
                "function_code": 2,
                "destination_host": TO_DESTINATION_HOST,
                "destination_port": TO_DESTINATION_PORT,
                "packet_hex": self.setup_command_packet.hex(),
                "packet_length": len(self.setup_command_packet),
                "packet_sha256": sha256_bytes(self.setup_command_packet),
                "transmissions": self.setup_command_transmissions,
                "sent_utc": self.setup_command_sent_utc,
                "sent_monotonic_ns": self.setup_command_sent_monotonic_ns,
            },
            "command": {
                "name": "SAMPLE_NOOP_CC",
                "message_id_hex": "0x18FA",
                "function_code": 0,
                "packet_hex": self.command_packet.hex(),
                "packet_length": len(self.command_packet),
                "packet_sha256": sha256_bytes(self.command_packet),
                "transmissions": self.command_transmissions,
                "sent_utc": self.command_sent_utc,
                "sent_monotonic_ns": self.command_sent_monotonic_ns,
            },
            "sample_packets_received": self.sample_packets_received,
            "before": asdict(self.before) if self.before else None,
            "after": asdict(self.after) if self.after else None,
        }
        if self.before and self.after and self.command_sent_monotonic_ns is not None:
            result["command_to_acceptance_latency_ms"] = round(
                (self.after.monotonic_ns - self.command_sent_monotonic_ns) / 1_000_000, 3
            )
        atomic_write_json(self.ground_dir / "probe-result.json", result)
        ground_manifest_sha256 = write_hash_manifest(self.ground_dir)
        policy_manifest_sha256 = write_hash_manifest(self.policy_dir)
        print(
            "GROUND_PROBE_EVIDENCE_HASHED "
            f"ground_manifest_sha256={ground_manifest_sha256} "
            f"policy_manifest_sha256={policy_manifest_sha256}",
            flush=True,
        )
        return ground_manifest_sha256, policy_manifest_sha256

    def run(self) -> int:
        telemetry_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        telemetry_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        telemetry_socket.settimeout(1.0)
        try:
            telemetry_socket.bind((self.args.telemetry_bind, self.args.telemetry_port))
        except OSError as exc:
            self.finalize("RUN_INVALID", f"telemetry bind failed: {exc}")
            print(f"GROUND_PROBE_INVALID reason=telemetry_bind_failed error={exc}", file=sys.stderr, flush=True)
            return 3

        print(
            f"GROUND_PROBE_READY bind={self.args.telemetry_bind} port={self.args.telemetry_port}",
            flush=True,
        )
        try:
            self.wait_for_start_trigger()
            self.send_setup_command()
            self.before, stable_packets = self.establish_stable_baseline(telemetry_socket)
            for index, (_hk, payload) in enumerate(stable_packets, start=1):
                atomic_write_bytes(self.ground_dir / f"pre-command-{index}.bin", payload)
            self.send_command()
            self.after, post_payload = self.await_acceptance(telemetry_socket)
            atomic_write_bytes(self.ground_dir / "post-command.bin", post_payload)
            self.finalize("BENIGN_BASELINE_PASS")
            latency_ms = (self.after.monotonic_ns - self.command_sent_monotonic_ns) / 1_000_000
            print(f"GROUND_PROBE_PASS latency_ms={latency_ms:.3f}", flush=True)
            return 0
        except BaselineFail as exc:
            self.finalize("BENIGN_BASELINE_FAIL", str(exc))
            print(f"GROUND_PROBE_FAIL reason={exc}", file=sys.stderr, flush=True)
            return 2
        except (RunInvalid, OSError, ValueError, struct.error) as exc:
            self.finalize("RUN_INVALID", str(exc))
            print(f"GROUND_PROBE_INVALID reason={exc}", file=sys.stderr, flush=True)
            return 3
        finally:
            telemetry_socket.close()
            self.close()


def self_test() -> None:
    setup_packet = build_to_enable_output_packet()
    assert setup_packet == EXPECTED_TO_ENABLE_OUTPUT_PACKET
    assert setup_packet.hex() == "1880c0000013021d726164696f2d73696d000000000000009313"
    assert sha256_bytes(setup_packet) == EXPECTED_TO_ENABLE_OUTPUT_PACKET_SHA256
    assert cfs_xor_checksum(setup_packet) == 0
    setup_mutated = bytearray(setup_packet)
    setup_mutated[-1] ^= 0x01
    assert cfs_xor_checksum(setup_mutated) != 0

    packet = build_sample_noop_packet()
    assert packet == EXPECTED_NOOP_PACKET
    assert packet.hex() == "18fac000000100dc"
    assert sha256_bytes(packet) == EXPECTED_NOOP_PACKET_SHA256
    assert cfs_xor_checksum(packet) == 0
    mutated = bytearray(packet)
    mutated[-1] ^= 0x01
    assert cfs_xor_checksum(mutated) != 0

    counters = bytes([2, 7, 3])
    total_length = SAMPLE_HK_COUNTER_OFFSET + len(counters)
    synthetic = struct.pack(">HHH", SAMPLE_HK_MID, 0xC000, total_length - 7) + bytes(6) + counters
    parsed = parse_sample_housekeeping(synthetic, ("127.0.0.1", 6011))
    assert parsed is not None
    assert parsed.cmd_count == 7
    assert parsed.cmd_err_count == 2
    assert parsed.device_err_count == 3
    assert expected_post_count(255) == 0
    print("BENIGN_GROUND_PROBE_SELF_TEST=PASS")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--run-id", default=os.environ.get("RUN_ID", "unassigned"))
    parser.add_argument("--ground-dir", default="/evidence/ground")
    parser.add_argument("--policy-dir", default="/evidence/policy-visible")
    parser.add_argument("--start-trigger")
    parser.add_argument("--trigger-timeout", type=int, default=120)
    parser.add_argument("--telemetry-bind", default="0.0.0.0")
    parser.add_argument("--telemetry-port", type=int, default=6011)
    parser.add_argument("--command-host", default="cryptolib")
    parser.add_argument("--command-port", type=int, default=6010)
    parser.add_argument("--readiness-timeout", type=int, default=150)
    parser.add_argument("--acceptance-timeout", type=int, default=30)
    parser.add_argument("--minimum-stable", type=int, default=2)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.minimum_stable < 2:
        raise SystemExit("--minimum-stable must be at least 2")
    if args.trigger_timeout < 30:
        raise SystemExit("--trigger-timeout must be at least 30 seconds")
    if args.readiness_timeout < 30 or args.acceptance_timeout < 1:
        raise SystemExit("invalid timeout")
    return GroundProbe(args).run()


if __name__ == "__main__":
    raise SystemExit(main())
