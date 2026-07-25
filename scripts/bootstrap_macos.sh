#!/usr/bin/env bash
set -euo pipefail

BASE="/Users/zarthras/Documents/Development Projects/Satellite-Cybersecurity-Research"
PROJECT="mission-aware-satellite-cyber-recovery"
REPO="Zartharas/${PROJECT}"

mkdir -p "$BASE"

CURRENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="$BASE/$PROJECT"

if [[ "$CURRENT_DIR" != "$TARGET" ]]; then
  if [[ -e "$TARGET" ]]; then
    echo "Target already exists: $TARGET"
    echo "Move or merge the downloaded project manually."
    exit 1
  fi
  cp -R "$CURRENT_DIR" "$TARGET"
fi

cd "$TARGET"
chmod +x scripts/*.sh

if [[ ! -d .git ]]; then
  git init -b main
fi

git add .
if ! git diff --cached --quiet; then
  git commit -m "Initialize mission-aware satellite cyber recovery research"
fi

echo
echo "Local research folder is ready:"
echo "$TARGET"

if command -v gh >/dev/null 2>&1; then
  if gh auth status >/dev/null 2>&1; then
    if gh repo view "$REPO" >/dev/null 2>&1; then
      echo "GitHub repository already exists: $REPO"
      if ! git remote get-url origin >/dev/null 2>&1; then
        git remote add origin "https://github.com/$REPO.git"
      fi
      git push -u origin main
    else
      echo "Creating private GitHub repository: $REPO"
      gh repo create "$REPO" --private --source=. --remote=origin --push \
        --description "Mission-aware satellite cyber response and trusted recovery research"
    fi
  else
    echo
    echo "GitHub CLI is installed but not authenticated."
    echo "Run: gh auth login"
    echo "Then rerun this script."
  fi
else
  echo
  echo "GitHub CLI was not found."
  echo "Install it with Homebrew: brew install gh"
  echo "Authenticate: gh auth login"
  echo "Then rerun: scripts/bootstrap_macos.sh"
fi
