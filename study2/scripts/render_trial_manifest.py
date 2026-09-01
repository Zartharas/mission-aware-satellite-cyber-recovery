from __future__ import annotations

import argparse
import json
from pathlib import Path

from study2_security.trial_manifest import materialize_trial_manifest, trial_manifest_sha256


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    manifest = materialize_trial_manifest()
    payload = json.dumps(manifest, ensure_ascii=True, allow_nan=False, sort_keys=True, separators=(",", ":")) + "\n"
    if args.output is not None:
        args.output.write_text(payload, encoding="utf-8")
    print(f"position_count={manifest['position_count']}")
    print(f"trial_manifest_sha256={trial_manifest_sha256(manifest)}")
    print("campaign_runtime_executed=false")
    print("campaign_seed_consumed=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
