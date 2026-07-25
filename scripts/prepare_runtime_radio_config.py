#!/usr/bin/env python3
"""Prepare the runtime NOS3 radio interface without strict XML parsing.

The pinned NOS3 configuration contains element names such as
``<42-css-scale-factor>`` that are accepted by the NOS3 runtime parser but are
not legal XML names for Python's strict ``xml.etree.ElementTree`` parser.  This
helper therefore treats the upstream configuration as opaque UTF-8 text,
validates the unique generic-radio block and its frozen interface values, and
changes only the FSW CI port from 5010 to 5012 in a copied runtime file.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path


RADIO_MARKER = "<name>generic-radio-sim</name>"
SOURCE_CI_PORT = "5010"
RUNTIME_CI_PORT = "5012"


class PreparationError(RuntimeError):
    """The source configuration does not match the frozen interface contract."""


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def one_connection(block: str, name: str) -> tuple[int, int, str]:
    pattern = re.compile(
        rf"<connection>\s*<name>{re.escape(name)}</name>.*?</connection>",
        re.DOTALL,
    )
    matches = list(pattern.finditer(block))
    if len(matches) != 1:
        raise PreparationError(
            f"expected exactly one {name!r} connection in generic-radio-sim; found {len(matches)}"
        )
    match = matches[0]
    return match.start(), match.end(), match.group(0)


def require_value(block: str, tag: str, expected: str, context: str) -> None:
    pattern = re.compile(
        rf"<{re.escape(tag)}>\s*{re.escape(expected)}\s*</{re.escape(tag)}>"
    )
    count = len(pattern.findall(block))
    if count != 1:
        raise PreparationError(
            f"expected exactly one {context} {tag}={expected}; found {count}"
        )


def prepare_text(source: str) -> tuple[str, int]:
    marker_count = source.count(RADIO_MARKER)
    if marker_count != 1:
        raise PreparationError(
            f"expected exactly one generic-radio-sim marker; found {marker_count}"
        )

    marker_index = source.index(RADIO_MARKER)
    simulator_start = source.rfind("<simulator>", 0, marker_index)
    simulator_end_marker = source.find("</simulator>", marker_index)
    if simulator_start < 0 or simulator_end_marker < 0:
        raise PreparationError("generic-radio-sim simulator boundaries were not found")
    simulator_end = simulator_end_marker + len("</simulator>")
    radio_block = source[simulator_start:simulator_end]

    fsw_start, fsw_end, fsw_block = one_connection(radio_block, "fsw")
    _gsw_start, _gsw_end, gsw_block = one_connection(radio_block, "gsw")

    require_value(fsw_block, "ip", "nos-fsw", "FSW")
    require_value(fsw_block, "ci-port", SOURCE_CI_PORT, "FSW")
    require_value(fsw_block, "to-port", "5011", "FSW")
    require_value(gsw_block, "ip", "cryptolib", "GSW")
    require_value(gsw_block, "cmd-port", "8010", "GSW")
    require_value(gsw_block, "tlm-port", "8011", "GSW")

    ci_pattern = re.compile(r"(<ci-port>\s*)5010(\s*</ci-port>)")
    updated_fsw, replacement_count = ci_pattern.subn(
        rf"\g<1>{RUNTIME_CI_PORT}\g<2>", fsw_block
    )
    if replacement_count != 1:
        raise PreparationError(
            f"expected one bounded CI-port replacement; performed {replacement_count}"
        )

    updated_radio = radio_block[:fsw_start] + updated_fsw + radio_block[fsw_end:]
    updated = source[:simulator_start] + updated_radio + source[simulator_end:]

    if len(updated) != len(source):
        raise PreparationError("runtime edit changed the configuration length")
    differences = [index for index, pair in enumerate(zip(source, updated)) if pair[0] != pair[1]]
    if len(differences) != 1:
        raise PreparationError(
            f"runtime edit changed {len(differences)} characters; expected exactly one"
        )
    difference_index = differences[0]
    if source[difference_index] != "0" or updated[difference_index] != "2":
        raise PreparationError(
            "runtime edit was not the frozen one-character CI-port transition 5010->5012"
        )

    updated_radio_check = updated[simulator_start:simulator_end]
    if "<ci-port>5012</ci-port>" not in updated_radio_check:
        raise PreparationError("runtime radio block does not contain CI port 5012")
    if "<ci-port>5010</ci-port>" in updated_radio_check:
        raise PreparationError("runtime radio block still contains CI port 5010")

    return updated, difference_index


def prepare_file(source_path: Path, output_path: Path) -> None:
    source_bytes = source_path.read_bytes()
    source = source_bytes.decode("utf-8")
    updated, difference_index = prepare_text(source)
    updated_bytes = updated.encode("utf-8")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    temporary.write_bytes(updated_bytes)
    temporary.replace(output_path)

    if source_path.resolve() != output_path.resolve() and source_path.read_bytes() != source_bytes:
        raise PreparationError("source configuration changed during preparation")

    print(f"source_sha256={sha256_bytes(source_bytes)}")
    print(f"runtime_sha256={sha256_bytes(updated_bytes)}")
    print(f"changed_character_offset={difference_index}")
    print("runtime_radio_ci_port=5012")
    print("RUNTIME_RADIO_CONFIG_PREPARATION_STATUS=PASS")


def self_test() -> None:
    synthetic = """<nos3-configuration>
<simulators>
<simulator><name>unrelated</name><hardware-model><data-provider><42-css-scale-factor>1.0</42-css-scale-factor></data-provider></hardware-model></simulator>
<simulator>
  <name>generic-radio-sim</name>
  <hardware-model><connections>
    <connection><name>fsw</name><ip>nos-fsw</ip><ci-port>5010</ci-port><to-port>5011</to-port></connection>
    <connection><name>radio</name><ip>radio-sim</ip><cmd-port>5014</cmd-port></connection>
    <connection><name>gsw</name><ip>cryptolib</ip><cmd-port>8010</cmd-port><tlm-port>8011</tlm-port></connection>
  </connections></hardware-model>
</simulator>
</simulators>
</nos3-configuration>
"""
    updated, offset = prepare_text(synthetic)
    assert updated.count("<42-css-scale-factor>") == 1
    assert updated.count("<ci-port>5012</ci-port>") == 1
    assert updated.count("<ci-port>5010</ci-port>") == 0
    assert len(updated) == len(synthetic)
    differences = [i for i, pair in enumerate(zip(synthetic, updated)) if pair[0] != pair[1]]
    assert differences == [offset]
    assert synthetic[offset] == "0" and updated[offset] == "2"

    try:
        prepare_text(synthetic.replace("<ci-port>5010</ci-port>", "<ci-port>5999</ci-port>"))
    except PreparationError:
        pass
    else:
        raise AssertionError("unexpected source CI port was not rejected")

    print("RUNTIME_RADIO_CONFIG_PREPARATION_SELF_TEST=PASS")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("source", nargs="?")
    parser.add_argument("output", nargs="?")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.self_test:
        self_test()
        return 0
    if not args.source or not args.output:
        raise SystemExit("source and output paths are required unless --self-test is used")
    try:
        prepare_file(Path(args.source), Path(args.output))
    except (OSError, UnicodeError, PreparationError) as exc:
        print(f"RUNTIME_RADIO_CONFIG_PREPARATION_STATUS=FAIL reason={exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
