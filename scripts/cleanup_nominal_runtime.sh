#!/usr/bin/env bash
set -euo pipefail

PROJECT_LABEL="mission-aware-satellite-cyber-recovery"

if ! docker info >/dev/null 2>&1; then
  echo "[ERROR] Docker daemon is not reachable." >&2
  exit 1
fi

container_ids="$(docker ps -aq --filter "label=research.project=$PROJECT_LABEL")"
network_ids="$(docker network ls -q --filter "label=research.project=$PROJECT_LABEL")"

if [[ -z "$container_ids" && -z "$network_ids" ]]; then
  echo "[OK] No project-labeled runtime resources were found."
  exit 0
fi

if [[ -n "$container_ids" ]]; then
  echo "Removing project-labeled containers:"
  docker ps -a \
    --filter "label=research.project=$PROJECT_LABEL" \
    --format '  {{.Names}}  {{.Status}}'
  docker rm -f $container_ids >/dev/null
fi

if [[ -n "$network_ids" ]]; then
  echo "Removing project-labeled networks:"
  docker network ls \
    --filter "label=research.project=$PROJECT_LABEL" \
    --format '  {{.Name}}  {{.Driver}}'
  docker network rm $network_ids >/dev/null
fi

echo "[OK] Project-labeled runtime resources were removed."
