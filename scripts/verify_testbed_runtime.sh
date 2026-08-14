#!/usr/bin/env bash
set -euo pipefail

NETWORK_NAME="ma-testbed-runtime-check"
TEST_IMAGE="alpine:3.20"

cleanup() {
  docker network rm "$NETWORK_NAME" >/dev/null 2>&1 || true
}
trap cleanup EXIT

echo "Research testbed Docker runtime verification"
echo "==============================="

echo
echo_host() {
  printf '%s\n' "$1"
}

echo_host "Host architecture: $(uname -m)"
echo_host "Host kernel: $(uname -s) $(uname -r)"

echo
if ! command -v docker >/dev/null 2>&1; then
  echo "[FAIL] Docker CLI is not installed."
  exit 1
fi

echo "[OK] $(docker --version)"

if ! docker info >/dev/null 2>&1; then
  echo "[FAIL] Docker daemon is not reachable. Start Docker Desktop and rerun."
  exit 1
fi

echo "[OK] Docker daemon reachable"

echo "Docker server architecture: $(docker info --format '{{.Architecture}}')"
echo "Docker server OS type: $(docker info --format '{{.OSType}}')"
echo "Docker server version: $(docker info --format '{{.ServerVersion}}')"

if ! docker compose version >/dev/null 2>&1; then
  echo "[FAIL] Docker Compose plugin is unavailable."
  exit 1
fi

echo "[OK] $(docker compose version)"

echo
container_arch="$(docker run --rm --network none --platform linux/amd64 "$TEST_IMAGE" uname -m)"
if [[ "$container_arch" != "x86_64" ]]; then
  echo "[FAIL] Expected x86_64 container, got: $container_arch"
  exit 1
fi

echo "[OK] linux/amd64 container executed as $container_arch with network disabled"

docker network create --internal "$NETWORK_NAME" >/dev/null
internal_value="$(docker network inspect "$NETWORK_NAME" --format '{{.Internal}}')"
if [[ "$internal_value" != "true" ]]; then
  echo "[FAIL] Docker network was not marked internal."
  exit 1
fi

echo "[OK] internal Docker network created and verified"

if docker run --rm --network "$NETWORK_NAME" --platform linux/amd64 "$TEST_IMAGE" sh -c 'wget -q -T 3 -O- https://example.com >/dev/null 2>&1'; then
  echo "[FAIL] Internal network unexpectedly reached the public internet."
  exit 1
fi

echo "[OK] public internet access blocked from internal network"

echo
cat <<'EOF'
TESTBED_RUNTIME_STATUS=PASS

The runtime is suitable for the Docker-first headless research testbed.
This does not validate NOS3 itself. Next run:

  bash scripts/prepare_nos3_candidate.sh
  python3 -m pip install -r requirements-dev.txt
  python3 scripts/validate_experiment_schema.py
EOF
