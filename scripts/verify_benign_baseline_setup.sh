#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROBE="$ROOT/scripts/benign_ground_probe.py"
RUNNER="$ROOT/scripts/run_benign_baseline.sh"
WRAPPER="$ROOT/scripts/run_benign_baseline_with_setup.sh"
IMAGE="ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"

for file in "$PROBE" "$RUNNER" "$WRAPPER"; do
  [[ -f "$file" ]] || {
    echo "[ERROR] Missing file: $file" >&2
    exit 1
  }
done

python3 -m py_compile "$PROBE"
python3 "$PROBE" --self-test
bash -n "$RUNNER"
bash -n "$WRAPPER"

docker info >/dev/null 2>&1 || {
  echo "[ERROR] Docker daemon is not reachable." >&2
  exit 1
}
docker image inspect "$IMAGE" >/dev/null 2>&1 || {
  echo "[ERROR] Pinned image is unavailable: $IMAGE" >&2
  exit 1
}

docker run --rm --platform linux/amd64 --network none \
  --mount "type=bind,source=$ROOT,target=/work/project,readonly" \
  --workdir /work/project \
  "$IMAGE" python3 scripts/benign_ground_probe.py --self-test

grep -Fq '1880c0000013021d726164696f2d73696d000000000000009313' "$PROBE"
grep -Fq 'c9b26e373b21170039deb6ab4d54c49401581eae5d8f3d1eaf304e65f300d3bb' "$PROBE"
grep -Fq 'entering OPERATIONAL state' "$WRAPPER"
grep -Fq 'Successfully connected to TCP server!' "$WRAPPER"
grep -Fq 'event_injection=disabled' "$WRAPPER"

echo "BENIGN_BASELINE_SETUP_VERIFICATION_STATUS=PASS"
