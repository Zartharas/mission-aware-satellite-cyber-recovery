from __future__ import annotations

import json

from study2_security.runtime_authorization import current_runtime_bindings


def main() -> int:
    print(json.dumps(current_runtime_bindings(), indent=2, sort_keys=True))
    print("runtime_execution_performed=false")
    print("campaign_seed_consumed=false")
    print("campaign_observations_generated=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
