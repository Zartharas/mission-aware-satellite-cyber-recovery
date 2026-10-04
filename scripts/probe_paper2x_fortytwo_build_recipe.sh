#!/usr/bin/env bash
# P2X Phase A: compare two isolated candidate FortyTwo build recipes.
# DO NOT modify original external/fortytwo, historical July locks, or run a simulator.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FT="$ROOT/external/fortytwo"
HIST_LOCK="$ROOT/artifacts/fortytwo-lock.txt"
PIN="eda252bf31f27850e867e698cfdd963e143ead1f"
IMAGE="ivvitc/nos3-64@sha256:06aa945988a7770b759022c2e1f6f2531818c087fe41a4739d3a3a7f2a9dcce2"
OCTOBER_SHA="b4d054bdd8a95dd429201466833fba8403efec4bdef09a9ed7040131dda3006d"
JULY_SHA="9c0062d2a447a6340e7c191850ff952d3f8768dd307e3e7fb141e777961e60c7"
fail() { printf 'P2X_FORTYTWO_RECIPE_PROBE_HOLD=%s\n' "$*" >&2; exit 1; }

test "$(basename "$ROOT")" = "mission-aware-satellite-cyber-recovery" || fail "wrong_research_root"
case "$(git -C "$ROOT" remote get-url origin 2>/dev/null || true)" in
  https://github.com/Zartharas/mission-aware-satellite-cyber-recovery|https://github.com/Zartharas/mission-aware-satellite-cyber-recovery.git|git@github.com:Zartharas/mission-aware-satellite-cyber-recovery|git@github.com:Zartharas/mission-aware-satellite-cyber-recovery.git|ssh://git@github.com/Zartharas/mission-aware-satellite-cyber-recovery|ssh://git@github.com/Zartharas/mission-aware-satellite-cyber-recovery.git) ;;
  *) fail "wrong_research_origin" ;;
esac
test -z "$(git -C "$ROOT" status --porcelain)" || fail "research_worktree_dirty"
for program in git docker shasum tar grep awk; do
  command -v "$program" >/dev/null 2>&1 || fail "missing_command_$program"
done
docker info >/dev/null 2>&1 || fail "docker_unavailable"
test "$(docker image inspect "$IMAGE" --format '{{.Os}}/{{.Architecture}}' 2>/dev/null)" = "linux/amd64" || fail "pinned_image_absent_or_wrong_arch"
test -d "$FT/.git" && test "$(git -C "$FT" rev-parse HEAD)" = "$PIN" || fail "pinned_fortytwo_source_missing"
test -z "$(git -C "$FT" status --porcelain)" || fail "fortytwo_source_dirty"
test "$(awk -F= '$1=="fortytwo_commit"{print $2}' "$HIST_LOCK" | tail -n 1)" = "$PIN" || fail "july_source_pin_changed"
test "$(awk -F= '$1=="fortytwo_binary_sha256"{print $2}' "$HIST_LOCK" | tail -n 1)" = "$JULY_SHA" || fail "july_binary_sha_changed"
test -f "$FT/42" || fail "october_candidate_binary_missing"
test "$(shasum -a 256 "$FT/42" | awk '{print $1}')" = "$OCTOBER_SHA" || fail "october_candidate_binary_changed"
HIST_LOCK_BEFORE="$(shasum -a 256 "$HIST_LOCK" | awk '{print $1}')"
NOMINAL_LOCK="$ROOT/artifacts/nominal-build-lock.txt"
NOMINAL_LOCK_BEFORE="$(shasum -a 256 "$NOMINAL_LOCK" | awk '{print $1}')"

STAMP="$(date -u +%Y%m%dT%H%M%SZ)-$$"
OUT="$ROOT/artifacts/runtime/p2xa-42-recipe-probe-$STAMP"
test ! -e "$OUT" || fail "evidence_directory_collision"
mkdir -p "$OUT"
printf 'phase=P2X_PHASE_A_BUILD_RECIPE_DIAGNOSIS_ONLY\nsource_pin=%s\nimage=%s\njuly_binary_sha256=%s\noctober_binary_sha256=%s\nhistorical_log_available=NO\n' \
  "$PIN" "$IMAGE" "$JULY_SHA" "$OCTOBER_SHA" > "$OUT/recipe-probe-manifest.txt"
printf 'candidate\trecipe\tsha256\tjuly_match\toctober_match\n' > "$OUT/recipe-comparison.tsv"

# git archive includes only versioned source from exact commit: it excludes the October
# Object/*.o and 42 executable, without cleaning or copying the user's live checkout.
# Both isolated source roots are mounted at identical compiler working path /work/fortytwo.
prepare_candidate() {
  name="$1"
  source="$OUT/$name/source"
  mkdir -p "$source"
  git -C "$FT" archive "$PIN" | tar -xf - -C "$source"
  test -s "$source/Makefile" && test -s "$source/Source/42main.c" || fail "archive_incomplete_$name"
  test ! -e "$source/42" || fail "unexpected_binary_in_archive_$name"
  printf '%s\n' "$source"
}
compile_candidate() {
  name="$1"
  recipe="$2"
  source="$(prepare_candidate "$name")"
  log="$OUT/$name/build.log"
  echo "P2X_PROBE_CANDIDATE=$name"
  if [ "$recipe" = "october_flags" ]; then
    docker run --rm --platform linux/amd64 --network none \
      --user "$(id -u):$(id -g)" -e HOME=/tmp \
      --mount "type=bind,source=$source,target=/work/fortytwo" \
      --workdir /work/fortytwo "$IMAGE" bash -lc '
        set -Eeuo pipefail
        gcc --version | head -n 1
        pwd -P
        make GUIFLAG= SHADERFLAG= 42
      ' > "$log" 2>&1
  elif [ "$recipe" = "pinned_default_shader" ]; then
    docker run --rm --platform linux/amd64 --network none \
      --user "$(id -u):$(id -g)" -e HOME=/tmp \
      --mount "type=bind,source=$source,target=/work/fortytwo" \
      --workdir /work/fortytwo "$IMAGE" bash -lc '
        set -Eeuo pipefail
        gcc --version | head -n 1
        pwd -P
        make GUIFLAG= 42
      ' > "$log" 2>&1
  else
    fail "unknown_probe_recipe"
  fi
  test -s "$source/42" || fail "candidate_binary_not_generated_$name"
  sha="$(shasum -a 256 "$source/42" | awk '{print $1}')"
  july=NO
  october=NO
  if [ "$sha" = "$JULY_SHA" ]; then july=YES; fi
  if [ "$sha" = "$OCTOBER_SHA" ]; then october=YES; fi
  printf '%s\t%s\t%s\t%s\t%s\n' "$name" "$recipe" "$sha" "$july" "$october" >> "$OUT/recipe-comparison.tsv"
  printf 'P2X_PROBE_%s_SHA256=%s\n' "$name" "$sha"
  printf '%s\n' "$sha"
}

# First require reproduction of the *observed* October build in an isolated source copy.
# If it cannot be recreated, no inference about SHADERFLAG versus historical binary follows.
compile_candidate control october_flags
control="$(awk -F '\t' '$1=="control"{print $3}' "$OUT/recipe-comparison.tsv")"
test "$control" = "$OCTOBER_SHA" || fail "october_control_not_reproducible_review_environment_first"

# Change only the explicit SHADERFLAG override in the second, independently clean copy.
compile_candidate default_shader pinned_default_shader
probe="$(awk -F '\t' '$1=="default_shader"{print $3}' "$OUT/recipe-comparison.tsv")"

test "$(shasum -a 256 "$FT/42" | awk '{print $1}')" = "$OCTOBER_SHA" || fail "live_october_binary_changed"
test "$(shasum -a 256 "$HIST_LOCK" | awk '{print $1}')" = "$HIST_LOCK_BEFORE" || fail "july_fortytwo_lock_mutated"
test "$(shasum -a 256 "$NOMINAL_LOCK" | awk '{print $1}')" = "$NOMINAL_LOCK_BEFORE" || fail "july_nominal_build_lock_mutated"
test -z "$(git -C "$FT" status --porcelain)" || fail "live_fortytwo_tracked_files_mutated"
test -z "$(git -C "$ROOT" status --porcelain)" || fail "research_tracked_files_mutated"

printf '\nP2X_42_RECIPE_PROBE_CONTROL_REPRODUCED=PASS\n'
if [ "$probe" = "$JULY_SHA" ]; then
  echo "P2X_42_DEFAULT_SHADER_BYTE_MATCH_JULY=YES"
  echo "INTERPRETATION=Historical_byte_match_found_with_one_changed_flag_not_proof_of_original_July_recipe"
else
  echo "P2X_42_DEFAULT_SHADER_BYTE_MATCH_JULY=NO"
  echo "INTERPRETATION=Historical_build_recipe_unresolved_do_not_modify_original_freeze"
fi
echo "P2X_42_RECIPE_PROBE_ONLY=PASS"
echo "P2X_42_CANDIDATE_PROMOTION=NO"
echo "P2X_42_NOS3_BUILD=NO"
echo "P2X_42_RUNTIME=NO"
echo "P2X_42_EVIDENCE=$OUT"
