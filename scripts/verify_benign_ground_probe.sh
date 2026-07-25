#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"
SCRIPT="$ROOT/scripts/benign_ground_probe.py"

for command in python3 docker; do
  command -v "$command" >/dev/null 2>&1 || {
    echo "[ERROR] Missing command: $command" >&2
    exit 1
  }
done

[[ -f "$SCRIPT" ]] || {
  echo "[ERROR] Missing ground probe: $SCRIPT" >&2
  exit 1
}

docker info >/dev/null 2>&1 || {
  echo "[ERROR] Docker daemon is not reachable." >&2
  exit 1
}

docker image inspect "$IMAGE" >/dev/null 2>&1 || {
  echo "[ERROR] Pinned image is unavailable: $IMAGE" >&2
  exit 1
}

python3 -m py_compile "$SCRIPT"
python3 "$SCRIPT" --self-test

docker run --rm --platform linux/amd64 --network none \
  --mount "type=bind,source=$ROOT,target=/work/project,readonly" \
  --workdir /work/project \
  "$IMAGE" python3 scripts/benign_ground_probe.py --self-test

echo "BENIGN_GROUND_PROBE_VERIFICATION_STATUS=PASS"
