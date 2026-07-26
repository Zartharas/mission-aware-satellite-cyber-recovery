#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NOS3="$ROOT/external/nos3"

[[ -d "$NOS3" ]] || {
  echo "[ERROR] Missing pinned NOS3 checkout: $NOS3" >&2
  exit 1
}

for command in git find grep awk sed shasum; do
  command -v "$command" >/dev/null 2>&1 || {
    echo "[ERROR] Missing command: $command" >&2
    exit 1
  }
done

EXPECTED_NOS3="5a3bdee6be9a2c67fdf994ae6db56d5c60395302"
EXPECTED_TO_LAB="6ae88fd1c2bb931d233c0051c88b787447bd5bb6"

actual_nos3="$(git -C "$NOS3" rev-parse HEAD)"
actual_to_lab="$(git -C "$NOS3/fsw/apps/to_lab" rev-parse HEAD)"

printf 'TO_LAB_DOWNLINK_STATIC_AUDIT\n'
printf 'nos3_expected=%s\n' "$EXPECTED_NOS3"
printf 'nos3_actual=%s\n' "$actual_nos3"
printf 'to_lab_expected=%s\n' "$EXPECTED_TO_LAB"
printf 'to_lab_actual=%s\n' "$actual_to_lab"
printf 'nos3_source_clean=%s\n' "$(test -z "$(git -C "$NOS3" status --short)" && echo 1 || echo 0)"
printf 'to_lab_source_clean=%s\n' "$(test -z "$(git -C "$NOS3/fsw/apps/to_lab" status --short)" && echo 1 || echo 0)"

[[ "$actual_nos3" == "$EXPECTED_NOS3" ]] || {
  echo "[ERROR] NOS3 checkout does not match the frozen commit." >&2
  exit 1
}
[[ "$actual_to_lab" == "$EXPECTED_TO_LAB" ]] || {
  echo "[ERROR] TO_LAB checkout does not match the frozen commit." >&2
  exit 1
}

printf '\n[CFG_TLM_PORT_DEFINITIONS]\n'
mapfile_supported=0
if help mapfile >/dev/null 2>&1; then
  mapfile_supported=1
fi

port_files_tmp="$(mktemp)"
trap 'rm -f "$port_files_tmp"' EXIT
find "$NOS3" -type f \
  \( -name '*.h' -o -name '*.c' -o -name '*.cmake' -o -name 'CMakeCache.txt' \) \
  -not -path '*/.git/*' -print0 |
  while IFS= read -r -d '' file; do
    if grep -q 'cfgTLM_PORT' "$file" 2>/dev/null; then
      printf '%s\n' "$file" >> "$port_files_tmp"
    fi
  done

if [[ -s "$port_files_tmp" ]]; then
  while IFS= read -r file; do
    rel="${file#$ROOT/}"
    grep -nH -E 'cfgTLM_PORT|TLM_PORT' "$file" 2>/dev/null |
      sed "s#^$ROOT/##" || true
  done < <(sort -u "$port_files_tmp")
else
  echo "cfg_tlm_port_definition_files=0"
fi

printf '\n[GENERATED_TO_LAB_CONFIG_HEADERS]\n'
find "$NOS3" -type f \
  \( -name 'to_lab_platform_cfg.h' -o -name 'to_lab_internal_cfg.h' -o -name 'to_lab_interface_cfg.h' -o -name '*to_lab*cfg*.h' \) \
  -not -path '*/.git/*' -print |
  sort |
  while IFS= read -r file; do
    rel="${file#$ROOT/}"
    printf 'file=%s sha256=%s\n' "$rel" "$(shasum -a 256 "$file" | awk '{print $1}')"
    grep -nE 'cfgTLM_PORT|TLM_PORT' "$file" || true
  done

printf '\n[TO_LAB_SOURCE_BEHAVIOR]\n'
app="$NOS3/fsw/apps/to_lab/fsw/src/to_lab_app.c"
[[ -f "$app" ]] || {
  echo "[ERROR] Missing TO_LAB source: $app" >&2
  exit 1
}
grep -nE 'getaddrinfo|inet_ntop|OS_SocketAddrFromString|OS_SocketAddrSetPort|OS_SocketSendTo|TO_LAB_TLMOUTSTOP_ERR_EID' "$app" || true

resolver_failure_event_present=0
if grep -nE 'getaddrinfo.*(EVS|SendEvent)|TO.*resolve.*error|hostname.*error' "$app" >/dev/null 2>&1; then
  resolver_failure_event_present=1
fi
socket_addr_status_checked=0
if grep -nE 'status[[:space:]]*=[[:space:]]*OS_SocketAddrFromString' "$app" >/dev/null 2>&1; then
  socket_addr_status_checked=1
fi
printf 'resolver_failure_event_present=%s\n' "$resolver_failure_event_present"
printf 'socket_addr_from_string_status_checked=%s\n' "$socket_addr_status_checked"

printf '\n[SUBSCRIPTION_AND_SCHEDULE]\n'
sub_table="$NOS3/cfg/nos3_defs/tables/to_lab_sub.c"
msg_table="$NOS3/cfg/nos3_defs/tables/sch_def_msgtbl.c"
schedule_table="$NOS3/cfg/nos3_defs/tables/sch_def_schtbl.c"
for file in "$sub_table" "$msg_table" "$schedule_table"; do
  [[ -f "$file" ]] || {
    echo "[ERROR] Missing frozen mission table: $file" >&2
    exit 1
  }
done

grep -n 'SAMPLE_HK_TLM_MID' "$sub_table" || true
grep -n 'SAMPLE_REQ_HK_MID' "$msg_table" || true
grep -nE 'Sample HK Request|[[:space:]]55,[[:space:]]*SCH_GROUP' "$schedule_table" || true

sample_subscription_present="$(grep -q 'SAMPLE_HK_TLM_MID' "$sub_table" && echo 1 || echo 0)"
sample_request_definition_present="$(grep -q 'SAMPLE_REQ_HK_MID' "$msg_table" && echo 1 || echo 0)"
sample_schedule_enabled="$(grep -q 'SCH_ENABLED.*55.*Sample HK Request' "$schedule_table" && echo 1 || echo 0)"
printf 'sample_subscription_present=%s\n' "$sample_subscription_present"
printf 'sample_request_definition_present=%s\n' "$sample_request_definition_present"
printf 'sample_schedule_enabled=%s\n' "$sample_schedule_enabled"

printf '\n[BUILT_TABLE_ARTIFACTS]\n'
find "$NOS3" -type f -name 'to_lab_sub.tbl' -not -path '*/.git/*' -print |
  sort |
  while IFS= read -r file; do
    printf 'file=%s sha256=%s bytes=%s\n' \
      "${file#$ROOT/}" \
      "$(shasum -a 256 "$file" | awk '{print $1}')" \
      "$(wc -c < "$file" | tr -d ' ')"
  done

printf '\n[ASSESSMENT]\n'
if [[ "$sample_subscription_present" == 1 && "$sample_request_definition_present" == 1 && "$sample_schedule_enabled" == 1 ]]; then
  echo "static_sample_telemetry_design=CONFIRMED"
else
  echo "static_sample_telemetry_design=INCOMPLETE"
fi

if [[ "$resolver_failure_event_present" == 0 && "$socket_addr_status_checked" == 0 ]]; then
  echo "hostname_resolution_observability=SILENT_FAILURE_PATH_PRESENT"
else
  echo "hostname_resolution_observability=PARTIALLY_OBSERVED"
fi

echo "runtime_launched=0"
echo "docker_invoked=0"
echo "command_transmission_possible=0"
echo "STATIC_TO_LAB_DOWNLINK_AUDIT_STATUS=COMPLETE"
