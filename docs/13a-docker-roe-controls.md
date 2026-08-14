# Laboratory ROE Addendum — Docker Environment Controls

## Status

This addendum supplies the environment-specific network-isolation and emergency-shutdown controls required by `docs/13-laboratory-rules-of-engagement.md` for the selected Docker-first WP4 architecture.

## Required container label

Every project container must carry:

```text
org.missionaware.project=mission-aware-satellite-cyber-recovery
```

This label enables bounded inspection and shutdown without affecting unrelated containers.

## Preflight checks

Run before launching any experiment services:

```bash
docker info >/dev/null
docker compose version
bash scripts/verify_testbed_runtime.sh
```

Confirm the macOS application firewall state without changing it:

```bash
/usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate
```

## Authorized Docker networks

Create only internal project networks:

```bash
docker network create --internal ma-sim
docker network create --internal ma-control
```

Verify them:

```bash
docker network inspect ma-sim --format '{{.Name}} internal={{.Internal}}'
docker network inspect ma-control --format '{{.Name}} internal={{.Internal}}'
```

Expected values:

```text
ma-sim internal=true
ma-control internal=true
```

## Prohibited Docker configurations

- `--network host`
- Mounting `/var/run/docker.sock` into an experiment container
- Privileged containers unless a separately reviewed technical requirement is recorded
- Public interface bindings such as `0.0.0.0:<port>`
- Unbounded device access
- Reusing unrelated Docker networks
- Pulling images during a scored trial
- `docker system prune`, volume deletion, or other evidence-destructive cleanup during an incident

Optional browser interfaces must bind to loopback only:

```text
127.0.0.1:<host-port>:<container-port>
```

## Pre-run network evidence

Record before each campaign:

```bash
mkdir -p artifacts/runtime

docker network inspect ma-sim ma-control \
  > "artifacts/runtime/docker-networks-$(date -u +%Y%m%dT%H%M%SZ).json"

docker ps --filter label=org.missionaware.project=mission-aware-satellite-cyber-recovery \
  --format '{{json .}}' \
  > "artifacts/runtime/docker-containers-$(date -u +%Y%m%dT%H%M%SZ).jsonl"
```

## Emergency shutdown

### Step 1 — Record active project containers

```bash
mkdir -p artifacts/incidents
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"

docker ps --filter label=org.missionaware.project=mission-aware-satellite-cyber-recovery \
  --no-trunc \
  > "artifacts/incidents/${STAMP}-docker-ps.txt"

docker inspect $(docker ps -q --filter label=org.missionaware.project=mission-aware-satellite-cyber-recovery) \
  > "artifacts/incidents/${STAMP}-docker-inspect.json" 2>/dev/null || true
```

### Step 2 — Pause when brief volatile-state preservation is safe

```bash
docker pause $(docker ps -q --filter label=org.missionaware.project=mission-aware-satellite-cyber-recovery) \
  2>/dev/null || true
```

Skip the pause when continued execution presents risk.

### Step 3 — Stop project containers

```bash
docker unpause $(docker ps -q --filter label=org.missionaware.project=mission-aware-satellite-cyber-recovery) \
  2>/dev/null || true

docker stop --time 10 \
  $(docker ps -q --filter label=org.missionaware.project=mission-aware-satellite-cyber-recovery) \
  2>/dev/null || true
```

### Step 4 — Remove only project networks when containment requires it

```bash
docker network rm ma-sim ma-control 2>/dev/null || true
```

### Step 5 — Preserve evidence

Do not delete containers, volumes, images, raw logs, or run directories until the incident record has been reviewed and checksummed.

## Post-stop verification

```bash
docker ps --filter label=org.missionaware.project=mission-aware-satellite-cyber-recovery

docker network ls --filter name=ma-sim --filter name=ma-control
```

No running project container should remain. Network removal is optional when the incident does not require it.

## Recovery authorization

Testing may resume only after:

1. The incident or stop reason is documented.
2. Raw evidence is preserved.
3. The repository and upstream lock state are verified.
4. Project containers are recreated from the approved image digest.
5. The approved clean baseline is restored.
6. The runtime and schema checks pass again.

## Boundary

These commands affect only Docker resources carrying the project label and the two named internal networks. They do not authorize modification of unrelated host or third-party resources.
