#!/usr/bin/env bash
set -euo pipefail

DEST="${1:?usage: bootstrap_monocypher.sh <destination>}"
REV="ab2b16dd619ad5f6979a4fbe69cfa324a6fcc35f"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

git init "$TMP"
git -C "$TMP" remote add origin https://github.com/LoupVaillant/Monocypher.git
git -C "$TMP" fetch --depth=1 origin "$REV"
git -C "$TMP" checkout --detach FETCH_HEAD

test "$(git -C "$TMP" rev-parse HEAD)" = "$REV"
grep -q '^4.0.3$' "$TMP/CHANGELOG.md"
grep -q 'SPDX-License-Identifier: BSD-2-Clause OR CC0-1.0' "$TMP/src/optional/monocypher-ed25519.h"
grep -q 'crypto_ed25519_check' "$TMP/src/optional/monocypher-ed25519.h"

mkdir -p "$DEST/optional"
install -m 0644 "$TMP/src/monocypher.c" "$DEST/monocypher.c"
install -m 0644 "$TMP/src/monocypher.h" "$DEST/monocypher.h"
install -m 0644 "$TMP/src/optional/monocypher-ed25519.c" "$DEST/optional/monocypher-ed25519.c"
install -m 0644 "$TMP/src/optional/monocypher-ed25519.h" "$DEST/optional/monocypher-ed25519.h"

echo "aerc_monocypher_revision=$REV"
echo "aerc_monocypher_version=4.0.3"
echo "aerc_monocypher_license=BSD-2-Clause_OR_CC0-1.0"
